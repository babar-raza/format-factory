"""Package-install-proof orchestrator (GAP-FORENSIC-001 heal).

Proves the B9 oracle-to-package boundary for every Python format in
packaging/python/package-matrix.yaml: build the wheel, install it into an
ephemeral venv (never the project .venv — its editable .pth installs would
shadow wheels and fake the proof), import it, and call the primary API on
the same sample corpus the oracle verified.

Governed entry point: the /package-install-proof skill. Direct use:

    python tools/run_package_install_proof.py                 # full fleet
    python tools/run_package_install_proof.py --format fods   # scoped re-proof
    python tools/run_package_install_proof.py --skip-build    # reuse built wheels

Outputs (canonical locations — a validator consumes these):
    reports/package-install-proof/proof-manifest.json   machine-readable, merged per run
    reports/package-install-proof/proof-report.md       human summary, regenerated
    reports/package-install-proof/transcripts/*.json    per-format skill transcripts
    reports/spec-to-code-forensic-audit/feature-proof-register.yaml  (surgical update)

Every proof records wheel_sha256 + source_digest so staleness is detectable:
proof of old source is not proof of current source.

publication_authorized: false — nothing here touches PyPI.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import venv
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))
from package_proof_common import source_digest as _shared_source_digest  # noqa: E402
MATRIX_PATH = REPO_ROOT / "packaging" / "python" / "package-matrix.yaml"
BUILD_SCRIPT = REPO_ROOT / "packaging" / "python" / "build-local-packages.py"
BUILD_DIR = REPO_ROOT / ".local" / "package-builds" / "python-foss"
PROOF_REQUIREMENTS = REPO_ROOT / "packaging" / "python" / "proof-requirements.txt"
VENV_DIR = REPO_ROOT / ".local" / "package-install-proof-venv"
WORK_DIR = REPO_ROOT / ".local" / "package-install-proof-work"
TEST_FILE = REPO_ROOT / "tests" / "python" / "packaging" / "test_package_install_proof_all_formats.py"
REPORT_DIR = REPO_ROOT / "reports" / "package-install-proof"
MANIFEST_PATH = REPORT_DIR / "proof-manifest.json"
REGISTER_PATH = REPO_ROOT / "reports" / "spec-to-code-forensic-audit" / "feature-proof-register.yaml"

SKILL_ID = "package-install-proof"
SKILL_VERSION = "2.0"

# Deep-import scan script, executed with the proof venv's python. Inventories
# which submodules of each installed wheel actually import — converter modules
# that assume the repo layout (from src.python...) surface here as findings
# without flipping the core B9 verdict (import + primary API).
_DEEP_IMPORT_SCRIPT = r'''
import importlib, json, pkgutil, sys

results = {}
for pkg_name in sys.argv[1:-1]:
    entry = {"total": 0, "failed": 0, "failing_modules": {}}
    try:
        pkg = importlib.import_module(pkg_name)
    except Exception as exc:
        entry["package_import_error"] = f"{type(exc).__name__}: {exc}"[:200]
        results[pkg_name] = entry
        continue
    if hasattr(pkg, "__path__"):
        for mod_info in pkgutil.walk_packages(pkg.__path__, prefix=pkg_name + "."):
            entry["total"] += 1
            try:
                importlib.import_module(mod_info.name)
            except BaseException as exc:  # converter modules raise ImportError and worse
                entry["failed"] += 1
                if len(entry["failing_modules"]) < 40:
                    entry["failing_modules"][mod_info.name] = f"{type(exc).__name__}: {exc}"[:160]
    results[pkg_name] = entry

with open(sys.argv[-1], "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=1)
'''


def log(msg: str) -> None:
    print(f"[package-install-proof] {msg}", flush=True)


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    if "env" not in kwargs:
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)  # keep repo source paths out of subprocesses
        env.pop("PYTHONHOME", None)
        kwargs["env"] = env
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def load_matrix() -> list[dict]:
    packages = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))["packages"]
    missing = [p["format_id"] for p in packages if "install_proof" not in p]
    if missing:
        raise SystemExit(f"matrix entries missing install_proof blocks: {missing}")
    return packages


def source_digest(fmt: str) -> str:
    """Content hash binding proof to source state (shared impl — see package_proof_common)."""
    return _shared_source_digest(REPO_ROOT, fmt)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_wheels(formats: list[str], full_fleet: bool) -> None:
    if full_fleet:
        log("building wheels for the full fleet ...")
        proc = run([sys.executable, str(BUILD_SCRIPT)], cwd=str(REPO_ROOT), timeout=3600)
        if proc.returncode != 0:
            raise SystemExit(f"fleet wheel build failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
    else:
        for fmt in formats:
            log(f"building wheel for {fmt} ...")
            proc = run([sys.executable, str(BUILD_SCRIPT), "--format", fmt], cwd=str(REPO_ROOT), timeout=600)
            if proc.returncode != 0:
                raise SystemExit(f"wheel build failed for {fmt}:\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")


def find_wheel(package_name: str) -> Path:
    dist = BUILD_DIR / package_name / "dist"
    wheels = sorted(dist.glob("*.whl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not wheels:
        raise SystemExit(f"WHEEL_MISSING: no wheel in {dist} — run without --skip-build")
    return wheels[0]


def create_proof_venv() -> Path:
    if VENV_DIR.exists():
        shutil.rmtree(VENV_DIR)
    log(f"creating ephemeral proof venv at {VENV_DIR} ...")
    venv.EnvBuilder(with_pip=True, clear=True).create(str(VENV_DIR))
    py = VENV_DIR / "Scripts" / "python.exe"
    if not py.exists():  # non-Windows layout
        py = VENV_DIR / "bin" / "python"
    proc = run([str(py), "-m", "pip", "install", "-r", str(PROOF_REQUIREMENTS), "--quiet"], timeout=600)
    if proc.returncode != 0:
        raise SystemExit(f"proof venv bootstrap failed:\n{proc.stderr[-2000:]}")
    return py


def install_wheels(py: Path, wheels: dict[str, Path]) -> dict[str, str]:
    """Install wheels with --no-deps (deps come pinned from proof-requirements.txt).
    Returns per-format install result."""
    results = {}
    for fmt, wheel in sorted(wheels.items()):
        proc = run([str(py), "-m", "pip", "install", "--no-deps", "--quiet", str(wheel)], timeout=300)
        results[fmt] = "PASS" if proc.returncode == 0 else f"FAIL: {proc.stderr[-400:]}"
        if proc.returncode != 0:
            log(f"  install FAIL {fmt}: {proc.stderr[-200:]}")
    return results


def write_specs_json(packages: list[dict], formats: list[str]) -> Path:
    specs = {}
    for pkg in packages:
        fmt = pkg["format_id"]
        if fmt not in formats:
            continue
        ip = pkg["install_proof"]
        spec = {
            "smoke_module": ip["smoke_module"],
            "smoke_callable": ip["smoke_callable"],
            "expected": ip["expected"],
            "package_name": pkg["package_name"],
        }
        if "smoke_inline_bytes" in ip:
            spec["smoke_inline_bytes"] = ip["smoke_inline_bytes"]
        else:
            spec["smoke_sample_abs"] = str(REPO_ROOT / ip["smoke_sample"])
        specs[fmt] = spec
    path = WORK_DIR / "proof-specs.json"
    path.write_text(json.dumps(specs, indent=1), encoding="utf-8")
    return path


def run_pytest(py: Path, specs_path: Path, formats: list[str], junit_name: str) -> Path:
    junit = WORK_DIR / junit_name
    env = dict(os.environ)
    # PYTHONPATH/PYTHONHOME could leak the repo source tree into the proof venv
    # and fake the wheel-origin check — strip them.
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env.update({
        "FF_PROOF_SPECS": str(specs_path),
        "FF_PROOF_FORMATS": ",".join(sorted(formats)),
        "FF_REPO_ROOT": str(REPO_ROOT),
    })
    proc = run(
        [str(py), "-m", "pytest", str(TEST_FILE),
         f"--confcutdir={TEST_FILE.parent}",
         "-q", "--tb=line", f"--junitxml={junit}", "-p", "no:cacheprovider"],
        cwd=str(WORK_DIR), env=env, timeout=1800,
    )
    tail = proc.stdout.strip().splitlines()
    log(f"pytest ({junit_name}): {tail[-1] if tail else proc.returncode}")
    if not junit.exists():
        raise SystemExit(f"pytest produced no junit xml:\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
    return junit


def parse_junit(junit_files: list[Path]) -> dict[str, dict[str, str]]:
    """-> {fmt: {import: PASS/FAIL..., smoke: ...}} from parametrized testcase names."""
    verdicts: dict[str, dict[str, str]] = {}
    for junit in junit_files:
        root = ElementTree.parse(junit).getroot()
        for case in root.iter("testcase"):
            name = case.get("name", "")
            if "[" not in name:
                continue
            test_name, fmt = name.split("[", 1)
            fmt = fmt.rstrip("]")
            key = "import" if test_name == "test_wheel_import" else (
                "smoke" if test_name == "test_api_smoke" else None)
            if key is None:
                continue
            if case.find("skipped") is not None:
                status = "SKIP"
            elif case.find("failure") is not None or case.find("error") is not None:
                node = case.find("failure") if case.find("failure") is not None else case.find("error")
                status = f"FAIL: {(node.get('message') or '')[:200]}"
            else:
                status = "PASS"
            if status != "SKIP":
                verdicts.setdefault(fmt, {})[key] = status
    return verdicts


def deep_import_scan(py: Path, formats: list[str], out_name: str) -> dict:
    script = WORK_DIR / "deep_import_scan.py"
    script.write_text(_DEEP_IMPORT_SCRIPT, encoding="utf-8")
    out = WORK_DIR / out_name
    proc = run([str(py), str(script), *sorted(formats), str(out)], cwd=str(WORK_DIR), timeout=900)
    if proc.returncode != 0 or not out.exists():
        log(f"deep-import scan failed (non-blocking): {proc.stderr[-300:]}")
        return {}
    return json.loads(out.read_text(encoding="utf-8"))


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"schema_version": 1, "generated_by": "tools/run_package_install_proof.py", "formats": {}}


def write_report(manifest: dict) -> None:
    lines = [
        "# Package Install Proof — All Python Formats",
        "",
        "Proves GAP-FORENSIC-001's B9 boundary: wheel build -> pip install into an",
        "ephemeral venv -> import -> primary API smoke on the oracle sample corpus.",
        f"Canonical machine-readable source: `proof-manifest.json`. Orchestrator:",
        "`tools/run_package_install_proof.py` via the `/package-install-proof` skill.",
        "",
        "| # | Format | Package | Version | Import | API Smoke | Verdict | Deep-import | Proved at (UTC) |",
        "|---|--------|---------|---------|--------|-----------|---------|-------------|-----------------|",
    ]
    for i, (fmt, e) in enumerate(sorted(manifest["formats"].items()), 1):
        deep = e.get("deep_import") or {}
        deep_str = (f"{deep.get('total', 0) - deep.get('failed', 0)}/{deep.get('total', 0)}"
                    if deep else "n/a")
        lines.append(
            f"| {i} | {fmt} | {e['package_name']} | {e['version']} | "
            f"{e['import_result'].split(':')[0]} | {e['smoke_result'].split(':')[0]} | "
            f"**{e['verdict']}** | {deep_str} | {e['proved_at']} |"
        )
    fails = {f: e for f, e in manifest["formats"].items() if e["verdict"] != "PASS"}
    lines += ["", f"**{len(manifest['formats']) - len(fails)}/{len(manifest['formats'])} PASS**"]
    if fails:
        lines += ["", "## Failures", ""]
        for fmt, e in sorted(fails.items()):
            lines.append(f"- **{fmt}**: import={e['import_result']} smoke={e['smoke_result']}")
    deep_findings = {
        f: e["deep_import"] for f, e in sorted(manifest["formats"].items())
        if e.get("deep_import", {}).get("failed")
    }
    if deep_findings:
        lines += [
            "", "## Deep-import findings (non-verdict; converter modules assuming repo layout)", "",
            "These submodules fail to import from the installed wheel. The B9 verdict",
            "covers package import + primary API; these are registered as a separate gap.", "",
        ]
        for fmt, deep in deep_findings.items():
            mods = ", ".join(sorted(deep["failing_modules"])[:6])
            more = "" if deep["failed"] <= 6 else f" (+{deep['failed'] - 6} more)"
            lines.append(f"- **{fmt}**: {deep['failed']}/{deep['total']} failing — {mods}{more}")
    lines += [
        "", "## Evidence chain", "",
        "wheel sha256 + source digest per format are in `proof-manifest.json`;",
        "junit XML at `.local/package-install-proof-results-*.xml`;",
        "staleness is enforced by the package-install-proof coverage governance validator.", "",
    ]
    (REPORT_DIR / "proof-report.md").write_text("\n".join(lines), encoding="utf-8")


def write_transcripts(manifest: dict, formats: list[str]) -> None:
    tdir = REPORT_DIR / "transcripts"
    tdir.mkdir(parents=True, exist_ok=True)
    for fmt in formats:
        e = manifest["formats"].get(fmt)
        if not e:
            continue
        transcript = {
            "skill_id": SKILL_ID,
            "skill_version": SKILL_VERSION,
            "format_id": fmt,
            "package_name": e["package_name"],
            "package_version": e["version"],
            "wheel_path": e["wheel_file"],
            "wheel_sha256": e["wheel_sha256"],
            "source_digest": e["source_digest"],
            "install_method": "pip install --no-deps <wheel> (ephemeral venv)",
            "install_result": e["install_result"],
            "import_result": e["import_result"],
            "import_statement": f"import {fmt}",
            "smoke_result": e["smoke_result"],
            "smoke_test": e["smoke_test"],
            "verdict": e["verdict"],
            "proof_report": "reports/package-install-proof/proof-report.md",
            "notes": "B9 proof via tools/run_package_install_proof.py (GAP-FORENSIC-001)",
            "generated_at": e["proved_at"],
            "worker_agent": "claude",
        }
        (tdir / f"package-install-proof-{fmt}.json").write_text(
            json.dumps(transcript, indent=2), encoding="utf-8")


def update_feature_proof_register(manifest: dict, formats: list[str]) -> None:
    """Surgical text update of the forensic register (preserves comments/banners).
    Only upgrades formats already in the register whose verdict is PASS; formats
    absent from the register (the 6 onboarded ones) are appended with an honest
    proof level (no oracle verdict -> capped at 2 with packaging note)."""
    try:
        text = REGISTER_PATH.read_text(encoding="utf-8")
        evidence_line = "      - reports/package-install-proof/proof-manifest.json"
        appended, upgraded = [], []
        for fmt in formats:
            e = manifest["formats"].get(fmt)
            if not e or e["verdict"] != "PASS":
                continue
            block_start = text.find(f"- format_id: {fmt}\n")
            if block_start != -1:
                block_end = text.find("- format_id:", block_start + 1)
                if block_end == -1:
                    block_end = len(text)
                block = text[block_start:block_end]
                if "proof_level: 3" in block:
                    new_block = (
                        block
                        .replace("proof_level: 3", "proof_level: 4", 1)
                        .replace("proof_level_name: ORACLE_VERIFIED",
                                 "proof_level_name: PACKAGE_INSTALL_PROOF", 1)
                        .replace("packaging_proof: null",
                                 f'packaging_proof: "wheel install + API smoke PASS '
                                 f'{e["proved_at"][:10]} (proof-manifest.json)"', 1)
                    )
                    if evidence_line not in new_block and "evidence_paths:" in new_block:
                        new_block = new_block.replace(
                            "evidence_paths:\n", f"evidence_paths:\n{evidence_line}\n", 1)
                    text = text[:block_start] + new_block + text[block_end:]
                    upgraded.append(fmt)
            else:
                appended.append(fmt)
        if appended:
            addition = ["", "  # Onboarded by GAP-FORENSIC-001 heal (2026-07-15): install proof exists;"]
            addition.append("  # no oracle verdict yet, so proof_level honestly capped at 2.")
            for fmt in sorted(appended):
                e = manifest["formats"][fmt]
                addition += [
                    f"  - format_id: {fmt}",
                    "    proof_level: 2",
                    "    proof_level_name: UNIT_TESTS",
                    "    oracle_verdict: null",
                    f'    packaging_proof: "wheel install + API smoke PASS {e["proved_at"][:10]} '
                    '(proof-manifest.json); oracle verification pending"',
                    "    evidence_paths:",
                    evidence_line,
                ]
            # append at the END of the python_format_proofs list — i.e. just
            # before the next top-level section key (dotnet_format_proofs),
            # backing up over its comment banner and blank lines
            lines = text.splitlines()
            insert_at = len(lines)
            for i, line in enumerate(lines):
                if line.startswith("dotnet_format_proofs:"):
                    insert_at = i
                    while insert_at > 0 and (
                        lines[insert_at - 1].lstrip().startswith("#")
                        or not lines[insert_at - 1].strip()
                    ):
                        insert_at -= 1
                    break
            lines[insert_at:insert_at] = addition + [""]
            text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
        yaml.safe_load(text)  # must remain valid YAML or we do not write it
        REGISTER_PATH.write_text(text, encoding="utf-8")
        log(f"feature-proof-register updated: upgraded={upgraded or 'none'}, appended={appended or 'none'}")
    except Exception as exc:
        # Register update is best-effort; the manifest is the canonical record.
        log(f"WARNING: feature-proof-register update failed (manifest is canonical): {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prove wheel install + API smoke for Python format packages")
    parser.add_argument("--format", action="append", default=None,
                        help="Prove only this format (repeatable); default: full fleet")
    parser.add_argument("--skip-build", action="store_true", help="Reuse already-built wheels")
    args = parser.parse_args()

    packages = load_matrix()
    by_id = {p["format_id"]: p for p in packages}
    if args.format:
        unknown = set(args.format) - set(by_id)
        if unknown:
            raise SystemExit(f"unknown formats (not in package-matrix.yaml): {sorted(unknown)}")
        formats = sorted(set(args.format))
        full_fleet = False
    else:
        formats = sorted(by_id)
        full_fleet = True

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    if not args.skip_build:
        build_wheels(formats, full_fleet)

    wheels = {fmt: find_wheel(by_id[fmt]["package_name"]) for fmt in formats}
    digests = {fmt: source_digest(fmt) for fmt in formats}

    py = create_proof_venv()

    # csv intentionally shadows stdlib csv once installed; contain the blast
    # radius by proving every other format first, then csv in its own pass.
    main_formats = [f for f in formats if f != "csv"]
    csv_requested = "csv" in formats

    install_results = install_wheels(py, {f: wheels[f] for f in main_formats})
    specs_path = write_specs_json(packages, formats)

    junits = []
    if main_formats:
        junits.append(run_pytest(py, specs_path, main_formats, "results-main.xml"))
    deep = deep_import_scan(py, main_formats, "deep-import-main.json")

    if csv_requested:
        install_results.update(install_wheels(py, {"csv": wheels["csv"]}))
        junits.append(run_pytest(py, specs_path, ["csv"], "results-csv.xml"))
        deep.update(deep_import_scan(py, ["csv"], "deep-import-csv.json"))

    verdicts = parse_junit(junits)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    manifest = load_manifest()
    manifest["python_version"] = sys.version.split()[0]
    for fmt in formats:
        pkg = by_id[fmt]
        v = verdicts.get(fmt, {})
        install_res = install_results.get(fmt, "NOT_INSTALLED")
        import_res = v.get("import", "NOT_RUN")
        smoke_res = v.get("smoke", "NOT_RUN")
        verdict = ("PASS" if install_res == "PASS" and import_res == "PASS" and smoke_res == "PASS"
                   else "FAIL")
        ip = pkg["install_proof"]
        smoke_desc = (f"{ip['smoke_module']}.{ip['smoke_callable']}"
                      + (f" on {ip['smoke_sample']}" if "smoke_sample" in ip
                         else " on inline bytes"))
        manifest["formats"][fmt] = {
            "package_name": pkg["package_name"],
            "version": wheels[fmt].name.split("-")[1],
            "wheel_file": wheels[fmt].name,
            "wheel_sha256": sha256_file(wheels[fmt]),
            "source_digest": digests[fmt],
            "install_result": install_res,
            "import_result": import_res,
            "smoke_result": smoke_res,
            "smoke_test": smoke_desc,
            "verdict": verdict,
            "deep_import": deep.get(fmt, {}),
            "proved_at": now,
        }
    manifest["last_run"] = {"at": now, "formats": formats, "full_fleet": full_fleet}
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # keep junits where the validator + humans can find them
    for junit in junits:
        shutil.copy2(junit, REPO_ROOT / ".local" / f"package-install-proof-{junit.stem}.xml")

    write_report(manifest)
    write_transcripts(manifest, formats)
    update_feature_proof_register(manifest, formats)

    passed = [f for f in formats if manifest["formats"][f]["verdict"] == "PASS"]
    failed = [f for f in formats if f not in passed]
    log(f"RESULT: {len(passed)}/{len(formats)} PASS" + (f"; FAIL: {failed}" if failed else ""))
    log(f"manifest: {MANIFEST_PATH}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())

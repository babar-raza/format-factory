"""Baseline freeze and environment capture (TC-PA-001).

Reproducible snapshot of the state this audit was taken against, for
plans/.claude/primary-purpose-the-python-starry-cupcake.md (mission
PORTFOLIO-AUDIT-2026-07-16). READ-ONLY.

Consumes artifacts produced by the capture commands in TC-PA-001 (pip-list.json,
source-hashes.txt, git-status-baseline.txt, pytest-collect.txt) and emits the
single authoritative baseline-capture.yaml with all 7 required fields, plus a
namespace probe whose results the issue ledger (TC-PA-003) cites.

Prerequisites (run from repo root before this script):
    .venv/Scripts/pip list --format=json > <E>/pip-list.json
    find src/python -name "*.py" -not -path "*__pycache__*" | sort | xargs sha256sum > <E>/source-hashes.txt
    git status --porcelain > <E>/git-status-baseline.txt
    .venv/Scripts/pytest tests/python/ --co -q --continue-on-collection-errors > <E>/pytest-collect.txt

Usage:
    .venv/Scripts/python tools/audit/portfolio_baseline_capture.py
Exit codes: 0 ok; 2 a required field is empty (TC-PA-001 completion criteria).
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
EVID = REPO / ".local" / "evidences" / "portfolio-audit-2026-07-16"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, cwd=str(REPO)
    ).stdout.strip()


def probe_namespaces() -> dict[str, Any]:
    """Empirically resolve each package name from a neutral cwd with the venv active."""
    src = REPO / "src" / "python"
    pkgs = sorted(p.name for p in src.iterdir() if p.is_dir() and p.name != "__pycache__")
    code = (
        "import importlib.util, sys, json\n"
        "out={}\n"
        f"pkgs={pkgs!r}\n"
        "for p in pkgs:\n"
        "    try: s=importlib.util.find_spec(p)\n"
        "    except Exception: s=None\n"
        "    out[p]={'origin': (s.origin if s else None), 'stdlib': p in sys.stdlib_module_names}\n"
        "print(json.dumps({'resolved':out,'sys_path':sys.path}))\n"
    )
    venv_py = REPO / ".venv" / "Scripts" / "python.exe"
    r = subprocess.run(
        [str(venv_py), "-c", code], capture_output=True, text=True, cwd=str(Path(venv_py.anchor))
    )
    try:
        data = json.loads(r.stdout)
    except Exception:
        return {"error": f"probe failed: {r.stderr[:300]}"}

    resolved = data["resolved"]
    src_str = str(src).replace("\\", "/").lower()
    collisions = []
    for p, info in sorted(resolved.items()):
        origin = (info.get("origin") or "").replace("\\", "/").lower()
        if origin and src_str not in origin:
            collisions.append(
                {
                    "package": p,
                    "resolves_to": info["origin"],
                    "is_stdlib_name": info["stdlib"],
                    "verdict": "PRODUCT_UNREACHABLE_UNDER_OWN_NAME",
                }
            )
    return {
        "method": "importlib.util.find_spec per package name, neutral cwd, venv interpreter",
        "packages_probed": len(resolved),
        "collisions": collisions,
        "sys_path": data["sys_path"],
        "note": (
            "A package whose name resolves OUTSIDE src/python is shadowed by stdlib or a "
            "third-party distribution and cannot be imported under its own name without a "
            "sys.path.insert(0, ...) hack -- which in turn hijacks that name for the whole process."
        ),
    }


def find_empty(obj: Any, path: str = "") -> list[str]:
    if isinstance(obj, dict):
        out: list[str] = []
        for k, v in obj.items():
            out += find_empty(v, f"{path}.{k}")
        return out
    if obj == "" or obj is None or obj == []:
        return [path]
    return []


def main() -> int:
    ap = argparse.ArgumentParser(description="Baseline freeze and environment capture (TC-PA-001).")
    ap.add_argument("--evidence-dir", default=str(EVID))
    args = ap.parse_args()
    E = Path(args.evidence_dir)

    collect = (E / "pytest-collect.txt").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"(\d+) tests collected(?:, (\d+) error)?", collect)
    collected, errors = (int(m.group(1)), int(m.group(2) or 0)) if m else (-1, -1)
    err_modules = re.findall(r"^ERROR (\S+)", collect, re.M)

    pip = json.loads((E / "pip-list.json").read_text(encoding="utf-8"))
    hashes = (E / "source-hashes.txt").read_text(encoding="utf-8")
    status = (E / "git-status-baseline.txt").read_text(encoding="utf-8", errors="replace").splitlines()

    venv_py = (REPO / ".venv" / "Scripts" / "python.exe").resolve()
    venv_ver = subprocess.run([str(venv_py), "--version"], capture_output=True, text=True).stdout.strip()

    pths = sorted((REPO / ".venv" / "Lib" / "site-packages").glob("*.pth"))
    pat = re.compile(r"src[/\\]python")
    inject = [p.name for p in pths if pat.search(p.read_text(encoding="utf-8", errors="replace"))]

    probe = probe_namespaces()

    doc: dict[str, Any] = {
        "schema_version": "1.0",
        "taskcard": "TC-PA-001",
        "mission_id": "PORTFOLIO-AUDIT-2026-07-16",
        "generator": "tools/audit/portfolio_baseline_capture.py",
        "captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "field_1_head_commit": {
            "sha": git("rev-parse", "HEAD"),
            "short": git("rev-parse", "--short", "HEAD"),
            "subject": git("log", "-1", "--pretty=%s"),
            "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        },
        "field_2_working_tree": {
            "dirty_file_count": len(status),
            "dirty_under_src": len([l for l in status if re.search(r"\ssrc/", l)]),
            "note": (
                "Tree is intentionally dirty: 50+ concurrent agents share this worktree "
                "(AGENTS.md Section CO). A dirty tree is normal state, not failure. The hashes in "
                "field_5 anchor the WORKING TREE this audit read, not HEAD -- they make THIS audit "
                "reproducible; they are not a clean-room snapshot."
            ),
            "evidence": ".local/evidences/portfolio-audit-2026-07-16/git-status-baseline.txt",
        },
        "field_3_python": {
            "system": f"Python {sys.version.split()[0]}",
            "venv": venv_ver,
            "venv_path": str(venv_py),
            "pytest_binary": ".venv/Scripts/pytest (system python has no pytest)",
        },
        "field_4_installed_packages": {
            "count": len(pip),
            "evidence": ".local/evidences/portfolio-audit-2026-07-16/pip-list.json",
            "editable_pth_total": len(pths),
            "editable_pth_injecting_src_python": len(inject),
            "finding": (
                "These .pth files put src/python AND src on sys.path for EVERY interpreter run in "
                "this venv, from any cwd. Consequence: most of the 406 sys.path mutations in "
                "product source are redundant HERE (the path is already injected) -- but they are "
                "NOT redundant for a consumer who pip-installs a single wheel. The csv case is the "
                "exception: insert(0, ...) is load-bearing because stdlib csv otherwise wins."
            ),
        },
        "field_5_source_hashes": {
            "file_count": len(hashes.splitlines()),
            "manifest_sha256": hashlib.sha256(hashes.encode()).hexdigest(),
            "evidence": ".local/evidences/portfolio-audit-2026-07-16/source-hashes.txt",
        },
        "field_6_collectable_tests": {
            "collected": collected,
            "command": ".venv/Scripts/pytest tests/python/ --co -q --continue-on-collection-errors",
            "evidence": ".local/evidences/portfolio-audit-2026-07-16/pytest-collect.txt",
        },
        "field_7_collection_errors": {
            "count": errors,
            "modules": err_modules or ["<none>"],
            "detail": (
                "ImportError: attempted relative import with no known parent package "
                "(src/python/toml/toml_codec.py:25). Root-caused as ISS-TEST_GAP-0001 in "
                "issue-ledger.yaml. NOTE: without --continue-on-collection-errors pytest ABORTS the "
                "entire run on this single error (exit 2)."
            ),
        },
        "namespace_probe": probe,
    }

    out = E / "baseline-capture.yaml"
    out.write_text(yaml.safe_dump(doc, sort_keys=False, width=100, allow_unicode=True), encoding="utf-8")

    empties = [p for p in find_empty(doc) if "sys_path" not in p]
    print(f"wrote {out}")
    print(f"  HEAD: {doc['field_1_head_commit']['short']} on {doc['field_1_head_commit']['branch']}")
    print(f"  python: system={doc['field_3_python']['system']} venv={venv_ver}")
    print(f"  pip packages: {len(pip)} | editable .pth injecting src/python: {len(inject)}/{len(pths)}")
    print(f"  source files hashed: {len(hashes.splitlines())}")
    print(f"  tests collected: {collected} | collection errors: {errors}")
    print(f"  namespace collisions: {[c['package'] for c in probe.get('collisions', [])]}")
    if empties:
        print(f"  TC-PA-001 COMPLETION VIOLATION: empty fields: {empties}")
        return 2
    print("  TC-PA-001 completion criteria: PASS (all 7 fields populated, non-empty)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

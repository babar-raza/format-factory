#!/usr/bin/env python3
"""
check_repo_invariants.py — Physical cross-layer consistency invariant checker.

Validates that registry claims are backed by actual filesystem evidence, that
state files exist, that the latest sprint contract is satisfied, and that no
stale PENDING markers or compiled artifacts appear in the repo.

This is the PHYSICAL invariant layer — it complements the logical checks in
state_linter.py and check_current_state_consistency.py by verifying that
claimed artifacts and files actually exist on disk.

INVARIANTS:
    INV-001  acquisition_pack_yaml_coverage
             For every format with acquisition_pack_created: true in the
             registry, acquisition-packs/<format_id>/pack.yaml must exist.

    INV-002  state_snapshot_files_present
             state/current-state.md and state/current-state.json must exist
             and be non-empty.

    INV-003  latest_sprint_contract_satisfied
             The contract with the highest run_number must have all its
             required_repo_files present in the repository.

    INV-004  no_stale_pending_verdict
             For closed sprint final-verdict files whose VERDICT line contains
             a complete marker (e.g. R40_COMPLETE), no standalone
             "BUNDLE_VALIDATION: PENDING" line may appear.

    INV-005  no_compiled_artifacts_tracked
             git ls-files must not include *.pyc, __pycache__, /bin/, /obj/,
             *.dll, or *.pdb. In no-Git environments, returns passed=True with
             detail NO_GIT_REPO — archive hygiene was not proved.

USAGE:
    python tools/evidence/check_repo_invariants.py [--repo-root PATH]

OUTPUT:
    INVARIANTS: PASS  (all pass)
    INVARIANTS: FAIL  (one or more failed)

EXIT CODE:
    0 on PASS, 1 on FAIL
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml as _yaml
except ImportError:
    _yaml = None

_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    if _yaml:
        return _yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    # minimal key:value fallback (single-depth only)
    data = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(\w+):\s*(.+)$", line)
        if m:
            data[m.group(1)] = m.group(2).strip().strip('"\'')
    return data


def _result(inv_id: str, name: str, passed: bool, details: list) -> dict:
    return {"id": inv_id, "name": name, "passed": passed, "details": details}


# ---------------------------------------------------------------------------
# INV-001: acquisition_pack_yaml_coverage
# ---------------------------------------------------------------------------

def check_inv001_acquisition_pack_coverage(root: Path) -> dict:
    """For every format claiming acquisition_pack_created=true, pack.yaml must exist."""
    inv_id, name = "INV-001", "acquisition_pack_yaml_coverage"
    reg_path = root / "registry" / "format-registry.yaml"
    if not reg_path.exists():
        return _result(inv_id, name, False, ["registry/format-registry.yaml not found"])

    reg = _load_yaml(reg_path)
    formats = reg.get("formats", []) if isinstance(reg, dict) else []
    if not isinstance(formats, list):
        return _result(inv_id, name, False,
                       ["registry formats field is not a list — schema ambiguous"])

    missing = []
    checked = 0
    for fmt in formats:
        if not isinstance(fmt, dict):
            continue
        if not fmt.get("acquisition_pack_created"):
            continue
        fid = fmt.get("format_id", "")
        if not fid:
            missing.append("format with acquisition_pack_created=true has no format_id")
            continue
        pack_yaml = root / "acquisition-packs" / fid / "pack.yaml"
        checked += 1
        if not pack_yaml.exists():
            missing.append(f"MISSING: acquisition-packs/{fid}/pack.yaml")

    if missing:
        return _result(inv_id, name, False, missing)
    return _result(inv_id, name, True,
                   [f"{checked}/{checked} acquisition packs have pack.yaml"])


# ---------------------------------------------------------------------------
# INV-002: state_snapshot_files_present
# ---------------------------------------------------------------------------

def check_inv002_state_files_present(root: Path) -> dict:
    """state/current-state.md and state/current-state.json must exist and be non-empty."""
    inv_id, name = "INV-002", "state_snapshot_files_present"
    issues = []
    for filename in ("current-state.md", "current-state.json"):
        path = root / "state" / filename
        if not path.exists():
            issues.append(f"MISSING: state/{filename}")
        elif path.stat().st_size == 0:
            issues.append(f"EMPTY: state/{filename}")
    if issues:
        return _result(inv_id, name, False, issues)
    return _result(inv_id, name, True, ["state/current-state.md and .json present and non-empty"])


# ---------------------------------------------------------------------------
# INV-003: latest_sprint_contract_satisfied
# ---------------------------------------------------------------------------

def _parse_run_number(rn_str) -> int:
    """Parse run_number 'R47' or 47 to integer. Returns -1 on failure."""
    if isinstance(rn_str, int):
        return rn_str
    if isinstance(rn_str, str):
        cleaned = rn_str.strip().lstrip("Rr")
        return int(cleaned) if cleaned.isdigit() else -1
    return -1


def check_inv003_latest_contract_satisfied(root: Path) -> dict:
    """All required_repo_files in the latest sprint contract must exist."""
    inv_id, name = "INV-003", "latest_sprint_contract_satisfied"
    contracts_dir = root / "tools" / "evidence" / "contracts"
    if not contracts_dir.exists():
        return _result(inv_id, name, False, ["tools/evidence/contracts/ not found"])

    # Collect sprint contracts (those with run_number field)
    sprint_contracts = []
    for cpath in sorted(contracts_dir.glob("*.yaml")):
        try:
            data = _load_yaml(cpath)
        except Exception:
            continue
        rn_raw = data.get("run_number")
        if rn_raw is None:
            continue
        rn = _parse_run_number(rn_raw)
        if rn < 0:
            continue
        sprint_contracts.append((rn, cpath, data))

    if not sprint_contracts:
        return _result(inv_id, name, False, ["No sprint contracts with run_number found"])

    # Find highest run_number; detect duplicates at the same highest number
    max_rn = max(rn for rn, _, _ in sprint_contracts)
    top = [(rn, cp, d) for rn, cp, d in sprint_contracts if rn == max_rn]
    if len(top) > 1:
        names = [cp.name for _, cp, _ in top]
        return _result(inv_id, name, False,
                       [f"AMBIGUOUS: {len(top)} contracts share run_number R{max_rn}: {names}"])

    _, selected_path, selected = top[0]

    # Legacy schema guard
    if "required_artifacts" in selected and "required_repo_files" not in selected:
        return _result(inv_id, name, False,
                       [f"{selected_path.name}: uses legacy required_artifacts, not required_repo_files"])

    required = selected.get("required_repo_files")
    if not required:
        return _result(inv_id, name, True,
                       [f"R{max_rn} contract has no required_repo_files — trivially satisfied",
                        f"Contract: {selected_path.name}"])

    if not isinstance(required, list):
        return _result(inv_id, name, False,
                       [f"{selected_path.name}: required_repo_files is not a list"])

    missing = [f for f in required if not (root / f).exists()]
    if missing:
        details = [f"Contract: R{max_rn} ({selected_path.name})"] + \
                  [f"MISSING: {f}" for f in missing]
        return _result(inv_id, name, False, details)

    return _result(inv_id, name, True,
                   [f"R{max_rn} contract: {len(required)}/{len(required)} required_repo_files present",
                    f"Contract: {selected_path.name}"])


# ---------------------------------------------------------------------------
# INV-004: no_stale_pending_verdict
# ---------------------------------------------------------------------------

def check_inv004_no_stale_pending_verdict(root: Path) -> dict:
    """
    For closed sprint verdicts (containing R<N>_COMPLETE), no standalone
    BUNDLE_VALIDATION: PENDING line may appear.
    Uses anchored multiline regex to avoid false-positives on historical prose.
    """
    inv_id, name = "INV-004", "no_stale_pending_verdict"
    reports_dir = root / "reports"
    if not reports_dir.exists():
        return _result(inv_id, name, True, ["reports/ not found — skipped"])

    # Pattern for a COMPLETE verdict (covers R40_COMPLETE, R39_DRIFT_RECOVERY_..._COMPLETE, etc.)
    complete_re = re.compile(
        r"\*{0,2}VERDICT:\*{0,2}\s*\*{0,2}[A-Z0-9_]*_COMPLETE\b",
        re.IGNORECASE,
    )
    # Anchored standalone PENDING line — does NOT match prose like
    # "BUNDLE_VALIDATION: PENDING forward-documented"
    pending_re = re.compile(r"^BUNDLE_VALIDATION:\s*PENDING\s*$", re.MULTILINE)

    offenders = []
    scanned = 0
    for sprint_dir in sorted(reports_dir.iterdir()):
        if not (sprint_dir.is_dir() and re.match(r"^r\d+$", sprint_dir.name)):
            continue
        vf = sprint_dir / "final-verdict.md"
        if not vf.exists():
            continue
        content = vf.read_text(encoding="utf-8")
        scanned += 1
        has_complete = complete_re.search(content)
        has_stale_pending = pending_re.search(content)
        if has_complete and has_stale_pending:
            offenders.append(
                f"reports/{sprint_dir.name}/final-verdict.md: "
                "claims COMPLETE but has standalone BUNDLE_VALIDATION: PENDING"
            )

    if offenders:
        return _result(inv_id, name, False, offenders)
    return _result(inv_id, name, True,
                   [f"Scanned {scanned} sprint verdict files — no stale PENDING found"])


# ---------------------------------------------------------------------------
# INV-005: no_compiled_artifacts_tracked
# ---------------------------------------------------------------------------

_COMPILED_PATTERNS = [
    r"\.pyc$",
    r"(^|/)__pycache__(/|$)",
    r"(^|/)bin/",
    r"(^|/)obj/",
    r"\.dll$",
    r"\.pdb$",
]


def check_inv005_no_compiled_artifacts_tracked(root: Path) -> dict:
    """git ls-files must not include compiled artifacts."""
    inv_id, name = "INV-005", "no_compiled_artifacts_tracked"
    git_dir = root / ".git"
    if not git_dir.exists():
        return _result(inv_id, name, True,
                       ["NO_GIT_REPO: .git absent — archive hygiene not proved via git ls-files",
                        "Use gitignore direct-read test for no-Git replay hygiene check"])

    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True, text=True, cwd=str(root), timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return _result(inv_id, name, False, [f"git ls-files failed: {exc}"])

    tracked = result.stdout.splitlines()
    offenders = []
    for pattern in _COMPILED_PATTERNS:
        hits = [f for f in tracked if re.search(pattern, f)]
        offenders.extend(hits)

    if offenders:
        sample = offenders[:10]
        details = [f"Tracked compiled artifact: {f}" for f in sample]
        if len(offenders) > 10:
            details.append(f"... and {len(offenders) - 10} more")
        return _result(inv_id, name, False, details)

    return _result(inv_id, name, True,
                   [f"git ls-files: {len(tracked)} tracked files, none are compiled artifacts"])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_all_invariants(root: Path = None) -> list:
    """
    Run all physical invariants against `root` (defaults to repo root).
    Returns list of result dicts: {id, name, passed, details}.
    Safe to import and call without side effects.
    """
    root = Path(root) if root is not None else _ROOT
    return [
        check_inv001_acquisition_pack_coverage(root),
        check_inv002_state_files_present(root),
        check_inv003_latest_contract_satisfied(root),
        check_inv004_no_stale_pending_verdict(root),
        check_inv005_no_compiled_artifacts_tracked(root),
    ]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Physical repository invariant checker",
    )
    parser.add_argument("--repo-root", default=None, help="Override repo root path")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve() if args.repo_root else _ROOT
    results = check_all_invariants(root)

    failed = [r for r in results if not r["passed"]]
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  {r['id']}: {r['name']} ... {status}")
        for detail in r.get("details", []):
            print(f"    - {detail}")

    print()
    if failed:
        print(f"INVARIANTS: FAIL ({len(failed)}/{len(results)} invariants failed)")
        sys.exit(1)
    else:
        print(f"INVARIANTS: PASS ({len(results)}/{len(results)} invariants passed)")


if __name__ == "__main__":
    main()

"""
scope_guard.py — Lane scope boundary enforcement.

Reads registry/lane-scope-registry.yaml and validates file changes against
the permitted/forbidden write rules for the active lane.

Usage:
  python tools/supervisor/scope_guard.py \\
    --lane lane-ci-audit \\
    --changed-files src/net/csv/CsvDocument.cs .github/workflows/ci.yml \\
    --mode block \\
    --registry registry/lane-scope-registry.yaml

Exit codes:
  0 = clean (no violations)
  1 = violation found (block mode) or warn mode always
  2 = configuration error (unknown lane, missing registry, etc.)

Mode:
  block = exit 1 on forbidden file; enforces scope boundary
  warn  = always exit 0; prints violations to stderr for awareness only

JSON output (stdout): machine-readable verdict for pipeline consumption.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo_root = _here.parent.parent
_default_registry = _repo_root / "registry" / "lane-scope-registry.yaml"
_default_lock = _repo_root / ".local" / "supervisor" / "active-plan-lock.json"


# ---------------------------------------------------------------------------
# Glob matching — F-002: fnmatch does NOT handle ** as multi-level wildcard.
# fnmatch.fnmatch("src/net/csv/CsvDocument.cs", "src/**") returns False.
# This helper handles ** correctly for the patterns used in lane-scope-registry.
# ---------------------------------------------------------------------------

def _glob_matches(path: str, pattern: str) -> bool:
    """Match path against a glob pattern supporting ** as multi-level wildcard."""
    path = path.replace("\\", "/")
    pattern = pattern.replace("\\", "/")
    if "**" not in pattern:
        return fnmatch.fnmatch(path, pattern)
    # Split on ** and validate prefix/suffix independently.
    # e.g. "src/**" -> prefix="src", suffix=""
    # e.g. ".github/workflows/**" -> prefix=".github/workflows", suffix=""
    # e.g. "src/**/*.cs" -> prefix="src", suffix=".cs"
    parts = pattern.split("**")
    prefix = parts[0].rstrip("/")
    suffix = parts[-1].lstrip("/")
    if prefix and not (path.startswith(prefix + "/") or path == prefix):
        return False
    if suffix:
        if not (path.endswith("/" + suffix) or path == suffix):
            return False
    return True


def _load_registry(registry_path: Path) -> dict:
    """Load and parse the lane scope registry YAML file."""
    try:
        import yaml  # type: ignore[import]
    except ImportError:
        # Fallback: minimal YAML-ish parser for simple structures won't work here;
        # require PyYAML which is already a project dependency.
        print("ERROR: PyYAML not available. Install with: pip install pyyaml", file=sys.stderr)
        sys.exit(2)
    if not registry_path.exists():
        print(f"ERROR: registry not found: {registry_path}", file=sys.stderr)
        sys.exit(2)
    return yaml.safe_load(registry_path.read_text(encoding="utf-8"))


def _find_lane(registry: dict, lane_id: str) -> dict | None:
    """Find a lane entry by id in the registry."""
    for lane in registry.get("lanes", []):
        if lane.get("id") == lane_id:
            return lane
    return None


def _read_lane_from_lock(lock_path: Path) -> str | None:
    """Read lane_id from the active plan lock file."""
    if not lock_path.exists():
        return None
    try:
        data = json.loads(lock_path.read_text(encoding="utf-8"))
        return data.get("lane_id")
    except Exception:
        return None


def _get_staged_files() -> list[str]:
    """Get list of staged files from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            cwd=str(_repo_root),
        )
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except Exception as exc:
        print(f"ERROR: git diff --cached failed: {exc}", file=sys.stderr)
        sys.exit(2)


def _check_skill_receipt(lane: dict, path: str) -> bool:
    """For requires_skill_transcript lanes, check that a skill receipt exists for the format."""
    if not lane.get("requires_skill_transcript"):
        return True
    # Extract format from path (first directory segment under src/)
    parts = path.replace("\\", "/").split("/")
    if len(parts) >= 2:
        fmt = parts[1]
        receipt_dir = _repo_root / ".local" / "skill-receipts"
        if receipt_dir.exists():
            receipts = list(receipt_dir.glob(f"*{fmt}*"))
            if receipts:
                return True
    return False


def check_files(
    files: list[str],
    lane: dict,
    lane_id: str,
) -> dict:
    """Check each file against the lane's permitted/forbidden write rules.

    Returns a result dict with verdict, violations, permitted, unrecognized.
    """
    permitted_globs = lane.get("permitted_writes", [])
    forbidden_globs = lane.get("forbidden_writes", [])

    violations = []
    permitted = []
    unrecognized = []

    for f in files:
        norm = f.replace("\\", "/")

        # Check forbidden first (forbidden overrides permitted)
        is_forbidden = any(_glob_matches(norm, g) for g in forbidden_globs)
        is_permitted = any(_glob_matches(norm, g) for g in permitted_globs)

        if is_forbidden:
            violations.append({
                "file": f,
                "rule": next(g for g in forbidden_globs if _glob_matches(norm, g)),
                "rule_type": "forbidden_writes",
                "action": "delegate or revert",
            })
        elif is_permitted:
            # For skill-transcript lanes, also check receipt
            if lane.get("requires_skill_transcript") and not _check_skill_receipt(lane, norm):
                violations.append({
                    "file": f,
                    "rule": "requires_skill_transcript",
                    "rule_type": "missing_skill_receipt",
                    "action": "run required skill first and generate receipt",
                })
            else:
                permitted.append(f)
        else:
            unrecognized.append(f)

    verdict = "VIOLATION" if violations else "CLEAN"
    return {
        "lane": lane_id,
        "verdict": verdict,
        "violations": violations,
        "permitted": permitted,
        "unrecognized": unrecognized,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lane scope guard — validates file changes against lane boundaries"
    )
    lane_group = parser.add_mutually_exclusive_group()
    lane_group.add_argument("--lane", type=str, help="Explicit lane ID to validate against")
    lane_group.add_argument("--lane-from-lock", action="store_true",
                            help="Read lane_id from active-plan-lock.json")
    files_group = parser.add_mutually_exclusive_group()
    files_group.add_argument("--changed-files", nargs="+", metavar="FILE",
                             help="Explicit list of changed files to validate")
    files_group.add_argument("--from-git-staged", action="store_true",
                             help="Read changed files from git diff --cached")
    parser.add_argument("--mode", choices=["block", "warn"], default="warn",
                        help="block=exit 1 on violation; warn=always exit 0 (default: warn)")
    parser.add_argument("--registry", type=str, default=str(_default_registry),
                        help="Path to lane-scope-registry.yaml")
    args = parser.parse_args(argv)

    # Resolve lane ID
    lane_id: str | None = None
    if args.lane:
        lane_id = args.lane
    elif args.lane_from_lock:
        lane_id = _read_lane_from_lock(_default_lock)
        if not lane_id or lane_id == "unknown":
            # No lane_id in lock — default to warn mode (safe)
            result = {
                "lane": "unknown",
                "verdict": "UNKNOWN_LANE",
                "violations": [],
                "permitted": [],
                "unrecognized": [],
                "note": "No lane_id in active-plan-lock.json; defaulting to warn mode",
            }
            print(json.dumps(result, indent=2))
            return 0
    else:
        print("ERROR: must specify --lane or --lane-from-lock", file=sys.stderr)
        return 2

    # Resolve files
    if args.changed_files:
        files = args.changed_files
    elif args.from_git_staged:
        files = _get_staged_files()
    else:
        # No files specified — nothing to check
        result = {"lane": lane_id, "verdict": "CLEAN", "violations": [], "permitted": [], "unrecognized": []}
        print(json.dumps(result, indent=2))
        return 0

    if not files:
        result = {"lane": lane_id, "verdict": "CLEAN", "violations": [], "permitted": [], "unrecognized": [],
                  "note": "no files to check"}
        print(json.dumps(result, indent=2))
        return 0

    # Load registry
    registry = _load_registry(Path(args.registry))

    # Find lane
    lane = _find_lane(registry, lane_id)
    if lane is None:
        print(f"ERROR: lane '{lane_id}' not found in registry {args.registry}", file=sys.stderr)
        print(f"Known lanes: {[l.get('id') for l in registry.get('lanes', [])]}", file=sys.stderr)
        return 2

    # Check files
    result = check_files(files, lane, lane_id)
    print(json.dumps(result, indent=2))

    # Emit warnings to stderr
    for v in result["violations"]:
        print(
            f"SCOPE WARNING [{v['rule_type']}]: {v['file']} violates rule '{v['rule']}' "
            f"in lane '{lane_id}' — {v['action']}",
            file=sys.stderr,
        )
    if result["unrecognized"]:
        for f in result["unrecognized"]:
            print(f"SCOPE UNRECOGNIZED: {f} — not in permitted_writes or forbidden_writes for lane '{lane_id}'",
                  file=sys.stderr)

    if result["violations"] and args.mode == "block":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

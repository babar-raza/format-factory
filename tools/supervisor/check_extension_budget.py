"""check_extension_budget.py — CI enforcement: new naming-pattern files require EXTENSION-BUDGET entry.

Guarded patterns (regrowth prevention):
  1. tools/supervisor/autonomous_*.py
  2. tools/supervisor/governance_validators_ext*.py
  3. tools/evidence/run0*_sprint_writer.py

Exit codes:
  0 — all pattern-matching files have EXTENSION-BUDGET entries
  1 — one or more new unbudgeted files found

Usage:
  python tools/supervisor/check_extension_budget.py
"""
from __future__ import annotations

import fnmatch
import sys
from pathlib import Path

GUARDED_PATTERNS = [
    {"pattern": "autonomous_*.py", "scope": "tools/supervisor/"},
    {"pattern": "governance_validators_ext*.py", "scope": "tools/supervisor/"},
    {"pattern": "run0*_sprint_writer.py", "scope": "tools/evidence/"},
]


def main() -> int:
    repo_root = Path(__file__).resolve()
    while repo_root.name not in ("format-factory", "") and repo_root != repo_root.parent:
        repo_root = repo_root.parent

    budget_path = repo_root / "tools" / "supervisor" / "EXTENSION-BUDGET.yaml"
    if not budget_path.exists():
        print(f"ERROR: EXTENSION-BUDGET.yaml not found at {budget_path}", file=sys.stderr)
        return 1

    try:
        import yaml  # type: ignore[import]
    except ImportError:
        print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
        return 1

    data = yaml.safe_load(budget_path.read_text(encoding="utf-8"))
    budgeted: set[str] = set()
    for entry in data.get("entries", []):
        f = entry.get("file", "")
        if f:
            budgeted.add(f.replace("\\", "/"))

    # Find all files matching guarded patterns
    matching: list[str] = []
    for gp in GUARDED_PATTERNS:
        scope_dir = repo_root / gp["scope"]
        if not scope_dir.is_dir():
            continue
        for p in scope_dir.iterdir():
            if p.is_file() and fnmatch.fnmatch(p.name, gp["pattern"]):
                rel = p.relative_to(repo_root).as_posix()
                matching.append(rel)
    matching.sort()

    unbudgeted = [f for f in matching if f not in budgeted]

    print(f"Extension budget check: {len(matching)} pattern-matching files")
    print(f"  Budgeted:   {len(matching) - len(unbudgeted)}")
    print(f"  Unbudgeted: {len(unbudgeted)}")

    if not unbudgeted:
        print("PASS: All naming-pattern files are budgeted.")
        return 0

    print(f"\nVIOLATION: {len(unbudgeted)} new unbudgeted file(s):")
    for f in unbudgeted:
        print(f"  NEW_UNBUDGETED: {f}")
    print(
        "\nTo resolve: add an entry to tools/supervisor/EXTENSION-BUDGET.yaml "
        "with rationale and disposition."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())

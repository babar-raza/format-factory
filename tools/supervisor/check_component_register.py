"""check_component_register.py — CI enforcement: every tools/supervisor/*.py must be registered.

Exit codes:
  0 — all files registered (or invoked with --report-only which always exits 0)
  1 — one or more tools/supervisor/*.py files lack a COMPONENT-REGISTER.yaml entry

Usage:
  python tools/supervisor/check_component_register.py
  python tools/supervisor/check_component_register.py --report-only
"""
from __future__ import annotations

import sys
import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Check COMPONENT-REGISTER.yaml completeness")
    parser.add_argument("--report-only", action="store_true",
                        help="Print gap report but always exit 0 (non-blocking mode)")
    parser.add_argument("--repo-root", type=Path, default=None,
                        help="Explicit repo root path (auto-detected if omitted)")
    args = parser.parse_args()

    # Locate repo root
    if args.repo_root:
        repo_root = args.repo_root.resolve()
    else:
        repo_root = Path(__file__).resolve()
        while repo_root.name not in ("format-factory", "") and repo_root != repo_root.parent:
            repo_root = repo_root.parent

    register_path = repo_root / "tools" / "supervisor" / "COMPONENT-REGISTER.yaml"
    if not register_path.exists():
        print(f"ERROR: COMPONENT-REGISTER.yaml not found at {register_path}", file=sys.stderr)
        return 1 if not args.report_only else 0

    try:
        import yaml  # type: ignore[import]
    except ImportError:
        print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
        return 1 if not args.report_only else 0

    data = yaml.safe_load(register_path.read_text(encoding="utf-8"))
    components = data.get("components", [])

    # Build set of registered file paths (normalised to forward slashes relative to repo root)
    registered: set[str] = set()
    for comp in components:
        f = comp.get("file", "")
        if f:
            registered.add(f.replace("\\", "/"))

    # Glob all .py files under tools/supervisor/ (exclude __pycache__ and _quarantine)
    supervisor_dir = repo_root / "tools" / "supervisor"
    all_py: list[str] = []
    for p in supervisor_dir.rglob("*.py"):
        parts = p.parts
        if "__pycache__" in parts or "_quarantine" in parts:
            continue
        rel = p.relative_to(repo_root).as_posix()
        all_py.append(rel)
    all_py.sort()

    # Find unregistered files
    unregistered = [f for f in all_py if f not in registered]

    print(f"COMPONENT-REGISTER check: {len(all_py)} .py files in tools/supervisor/")
    print(f"  Registered:   {len(all_py) - len(unregistered)}")
    print(f"  Unregistered: {len(unregistered)}")

    if not unregistered:
        print("PASS: All tools/supervisor/*.py files are registered.")
        return 0

    print(f"\nGAP: {len(unregistered)} unregistered file(s):")
    for f in unregistered:
        print(f"  MISSING: {f}")

    if args.report_only:
        print("\n(--report-only: exit 0 despite gaps)")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())

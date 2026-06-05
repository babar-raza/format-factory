"""One-command wrapper: materialize evidence + build review package.

Combines:
1. materialize_declared_evidence.py
2. build_declaration_review_package.py

Exit codes:
  0 — both steps succeeded
  1 — materialization failed
  2 — review package build failed
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent


def run_step(label: str, cmd: list[str]) -> int:
    """Run a subprocess and print status."""
    print(f"[{label}] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    if result.returncode != 0:
        print(f"[{label}] FAILED (exit {result.returncode})")
    else:
        print(f"[{label}] PASSED")
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--declaration", type=Path, required=True)
    parser.add_argument(
        "--python",
        default=str(REPO_ROOT / ".local" / "venv" / "Scripts" / "python"),
    )
    args = parser.parse_args()

    python = args.python
    decl = str(args.declaration)

    materialize_script = str(SCRIPT_DIR / "materialize_declared_evidence.py")
    rc = run_step("materialize", [python, materialize_script, "--declaration", decl])
    if rc != 0:
        return 1

    review_script = str(SCRIPT_DIR / "build_declaration_review_package.py")
    rc = run_step("review-package", [python, review_script, "--declaration", decl])
    if rc != 0:
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())

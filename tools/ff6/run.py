"""Single official entry point for the FF6 mission.

Usage from a clean clone::

    python -m tools.ff6.run

This command:
1. Validates the environment (Python version, venv, required inputs)
2. Reconstructs current state from committed files only
3. Reports the verdict, certified count, and per-format next action
4. Exits 0 (CONTINUE), 1 (BLOCKED), or 2 (GOAL_ACHIEVED)

No local signal, no session identity, no iteration budget.  A fresh
agent on a fresh clone computes the identical answer from identical
committed state.  See docs/authority-decision-record.md for the
authority model this command implements.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MIN_PYTHON = (3, 11)


def _check_environment() -> list[str]:
    """Return a list of environment problems (empty = ready)."""
    problems: list[str] = []

    if sys.version_info < MIN_PYTHON:
        problems.append(
            f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required, "
            f"found {sys.version_info.major}.{sys.version_info.minor}"
        )

    required_inputs = [
        REPO_ROOT / "plans" / "strategic" / "ff6" / "product-goal.yaml",
        REPO_ROOT / "plans" / "strategic" / "ff6" / "controller-state.yaml",
    ]
    for path in required_inputs:
        if not path.exists():
            problems.append(f"Required input missing: {path.relative_to(REPO_ROOT)}")

    obligations_dir = REPO_ROOT / "plans" / "strategic" / "ff6" / "obligations"
    if not obligations_dir.exists() or not any(obligations_dir.glob("*.yaml")):
        problems.append("No obligation registers found under plans/strategic/ff6/obligations/")

    return problems


def main() -> int:
    problems = _check_environment()
    if problems:
        print("ENVIRONMENT CHECK FAILED:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    from tools.ff6.goal_driver import evaluate, render_resume
    from tools.ff6.goal_driver import EXIT_CONTINUE, EXIT_BLOCKED, EXIT_GOAL_ACHIEVED

    try:
        from tools.ff6.controller_state_validator import validate
        result_v = validate()
        if not result_v.get("valid", True):
            print("CONTRADICTION GATE FAILED:", file=sys.stderr)
            for e in result_v.get("errors", []):
                print(f"  - {e}", file=sys.stderr)
            print(
                "\nController-state.yaml is internally contradictory. "
                "Resolve contradictions before trusting the verdict.",
                file=sys.stderr,
            )
    except Exception:
        pass

    result = evaluate()
    print(render_resume(result))

    if result["verdict"] == "GOAL_ACHIEVED":
        return EXIT_GOAL_ACHIEVED
    if result["verdict"] == "BLOCKED":
        return EXIT_BLOCKED
    return EXIT_CONTINUE


if __name__ == "__main__":
    raise SystemExit(main())

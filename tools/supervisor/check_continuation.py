"""
check_continuation.py — Deterministic continuation check for the autonomous loop.

Replaces the 7-condition manual check in CLAUDE.md with a single command.
Reads continuation-signal.json, approval-gates.md, and next-work-items.json.
Returns machine-readable JSON to stdout.

Exit codes:
  0 — CONTINUE (all conditions met)
  1 — STOP (at least one condition failed)

Usage:
  python tools/supervisor/check_continuation.py [--repo-root <path>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_default_repo = _here.parent.parent


def check(repo_root: Path) -> dict:
    """Run all 7 continuation conditions. Returns a verdict dict."""
    repo_root = repo_root.resolve()

    # --- Check 1: continuation-signal.json exists and is valid JSON ---
    signal_path = repo_root / ".local" / "supervisor" / "continuation-signal.json"
    if not signal_path.exists():
        return _stop("NO_SIGNAL", "continuation-signal.json does not exist")
    try:
        signal = json.loads(signal_path.read_text(encoding="utf-8"))
    except Exception as e:
        return _stop("INVALID_SIGNAL", f"continuation-signal.json is not valid JSON: {e}")

    iteration = signal.get("iteration", 0)
    max_iterations = signal.get("max_iterations", 5)

    # --- Check 2: autonomous_continue is truthy ---
    auto_continue = signal.get("autonomous_continue", False)
    if not auto_continue:
        reason = signal.get("stop_reason") or "autonomous_continue is false"
        return _stop("AUTONOMOUS_CONTINUE_FALSE", reason,
                      iteration=iteration, max_iterations=max_iterations)

    # --- Check 3: continuation_state starts with YES ---
    cont_state = signal.get("continuation_state", "")
    if isinstance(cont_state, str) and cont_state.startswith("NO_"):
        return _stop(cont_state, f"continuation_state={cont_state}",
                      iteration=iteration, max_iterations=max_iterations)

    # --- Check 4: hard_stops_detected is empty ---
    hard_stops = signal.get("hard_stops_detected", [])
    if hard_stops:
        return _stop("HARD_STOP", f"hard_stops_detected: {hard_stops}",
                      iteration=iteration, max_iterations=max_iterations)

    # --- Check 5: iteration < max_iterations ---
    if iteration >= max_iterations:
        return _stop("MAX_ITERATIONS",
                      f"iteration {iteration} >= max_iterations {max_iterations}",
                      iteration=iteration, max_iterations=max_iterations)

    # --- Check 6: approval-gates.md contains AUTONOMOUS_CONTINUE: YES ---
    gates_path = repo_root / "reports" / "supervisor" / "approval-gates.md"
    if not gates_path.exists():
        return _stop("APPROVAL_GATE_MISSING", "approval-gates.md does not exist",
                      iteration=iteration, max_iterations=max_iterations)
    gates_text = gates_path.read_text(encoding="utf-8")
    if "AUTONOMOUS_CONTINUE: YES" not in gates_text:
        return _stop("APPROVAL_GATE_NO",
                      "approval-gates.md does not contain AUTONOMOUS_CONTINUE: YES",
                      iteration=iteration, max_iterations=max_iterations)

    # --- Check 7: canonical next-work-items.json exists ---
    work_items_path = repo_root / ".local" / "supervisor" / "next-work-items.json"
    if not work_items_path.exists():
        return _stop("NO_WORK_ITEMS",
                      ".local/supervisor/next-work-items.json does not exist",
                      iteration=iteration, max_iterations=max_iterations)

    # --- All checks passed ---
    rework_items = signal.get("rework_items", [])
    result = {
        "verdict": "CONTINUE",
        "iteration": iteration,
        "max_iterations": max_iterations,
        "continuation_state": cont_state,
        "next_work_items_path": ".local/supervisor/next-work-items.json",
        "next_sprint_path": "reports/supervisor/next-sprint.md",
        "rework_items": rework_items,
        "resume_command": "python tools/supervisor/check_continuation.py",
    }
    if signal.get("evidence_continuation_failed"):
        result["warning"] = (
            f"evidence_continuation bridge failed: "
            f"{signal.get('evidence_continuation_error', 'unknown')}"
        )
    return result


def _stop(reason: str, detail: str, *, iteration: int = 0,
          max_iterations: int = 5) -> dict:
    return {
        "verdict": "STOP",
        "reason": reason,
        "detail": detail,
        "iteration": iteration,
        "max_iterations": max_iterations,
        "resume_command": None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check autonomous continuation conditions")
    parser.add_argument("--repo-root", type=Path, default=_default_repo,
                        help="Repository root (default: auto-detected)")
    args = parser.parse_args(argv)

    result = check(args.repo_root)
    print(json.dumps(result, indent=2))
    return 0 if result["verdict"] == "CONTINUE" else 1


if __name__ == "__main__":
    sys.exit(main())

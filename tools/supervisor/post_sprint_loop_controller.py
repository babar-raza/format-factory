"""
Post-Sprint Loop Controller for the Post-Sprint Autonomy Loop.

Outer orchestration layer that wraps the existing autonomous_cycle.py.
Reads autonomous-cycle outputs, dispatches Stages 1-3, classifies results,
and decides the next stage automatically.

State machine: .supervisor/schemas/loop-decision-state-machine.schema.json

Exit codes:
  0 — all green, accepted
  3 — max loops exceeded with remaining issues
  1 — invalid state or input
  9 — unexpected error

Usage:
  python tools/supervisor/post_sprint_loop_controller.py --repo-root <path> --run-id <id> [--max-loops 3]
  python tools/supervisor/post_sprint_loop_controller.py --help
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# Import sibling modules
sys.path.insert(0, str(SCRIPT_DIR))
from summary_classifier import classify_summary, CLASSIFICATIONS  # noqa: E402
from quality_scorer import score_execution, QUALITY_THRESHOLD, QUALITY_DIMENSIONS  # noqa: E402

# Valid loop states (from loop-decision-state-machine.schema.json)
VALID_STATES = [
    "INITIAL", "AUDIT_RUNNING", "AUDIT_COMPLETE",
    "HARDENING_RUNNING", "HARDENING_COMPLETE",
    "EXECUTION_RUNNING", "EXECUTION_COMPLETE",
    "CLASSIFYING", "REROUTE_TO_HARDEN", "REROUTE_TO_AUDIT",
    "REROUTE_REWORK", "ADVERSARIAL_REVIEW",
    "ACCEPTED_ALL_GREEN", "MAX_LOOPS_EXCEEDED",
    "HARD_STOP", "BLOCKED_EXTERNAL",
]

# Valid state transitions
VALID_TRANSITIONS: dict[str, list[str]] = {
    "INITIAL": ["AUDIT_RUNNING"],
    "AUDIT_RUNNING": ["AUDIT_COMPLETE"],
    "AUDIT_COMPLETE": ["HARDENING_RUNNING"],
    "HARDENING_RUNNING": ["HARDENING_COMPLETE"],
    "HARDENING_COMPLETE": ["EXECUTION_RUNNING"],
    "EXECUTION_RUNNING": ["EXECUTION_COMPLETE"],
    "EXECUTION_COMPLETE": ["CLASSIFYING"],
    "CLASSIFYING": [
        "ACCEPTED_ALL_GREEN", "REROUTE_TO_HARDEN", "REROUTE_TO_AUDIT",
        "REROUTE_REWORK", "BLOCKED_EXTERNAL", "HARD_STOP",
    ],
    "REROUTE_TO_HARDEN": ["HARDENING_RUNNING"],
    "REROUTE_TO_AUDIT": ["AUDIT_RUNNING"],
    "REROUTE_REWORK": ["EXECUTION_RUNNING"],
    "ACCEPTED_ALL_GREEN": ["ADVERSARIAL_REVIEW"],
    "ADVERSARIAL_REVIEW": ["ACCEPTED_ALL_GREEN"],
}

# Invalid final states that must never be the loop's terminal state
INVALID_FINAL_STATES = [
    "NEXT_PROMPT_NEEDED", "HUMAN_REVIEW_NEEDED_BEFORE_AGENT_REVIEW",
    "PROSE_ONLY_ACCEPTED", "SUMMARY_MISSING_ACCEPTED",
    "SCORE_BELOW_4_ACCEPTED", "EVIDENCE_PACKAGE_MISSING_ACCEPTED",
    "PLAN_UPDATED_NOT_EXECUTED", "EXECUTED_NOT_EVALUATED",
    "PROMPT_ASSETS_DISCONNECTED", "TASKCARDS_MISSING_ACCEPTED",
]

DEFAULT_MAX_LOOPS = 3


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _state_file_path(repo_root: Path) -> Path:
    return repo_root / ".local" / "supervisor" / "post-sprint-loop-state.json"


def _read_state(repo_root: Path) -> dict[str, Any] | None:
    path = _state_file_path(repo_root)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _write_state(repo_root: Path, state: dict[str, Any]) -> None:
    path = _state_file_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = _now_iso()
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _validate_transition(from_state: str, to_state: str) -> bool:
    allowed = VALID_TRANSITIONS.get(from_state, [])
    return to_state in allowed


def _record_transition(
    state: dict[str, Any], from_state: str, to_state: str,
    trigger: str, classification: str = "",
) -> None:
    history = state.setdefault("decision_history", [])
    history.append({
        "iteration": state.get("iteration", 0),
        "from_state": from_state,
        "to_state": to_state,
        "trigger": trigger,
        "classification": classification,
        "timestamp": _now_iso(),
    })
    state["current_state"] = to_state


def init_loop(repo_root: Path, run_id: str, max_loops: int = DEFAULT_MAX_LOOPS) -> dict[str, Any]:
    """Initialize a new loop state."""
    state: dict[str, Any] = {
        "current_state": "INITIAL",
        "iteration": 0,
        "max_iterations": max_loops,
        "run_id": run_id,
        "started_at": _now_iso(),
        "updated_at": _now_iso(),
        "decision_history": [],
        "stage1_output_path": "",
        "stage2_output_path": "",
        "stage3_output_path": "",
        "evidence_bundle_path": "",
        "final_verdict": "",
    }
    _write_state(repo_root, state)
    return state


def transition_to(
    repo_root: Path, to_state: str, trigger: str, classification: str = "",
) -> dict[str, Any]:
    """Transition the loop state machine to a new state."""
    state = _read_state(repo_root)
    if state is None:
        raise ValueError("Loop state not initialized. Call init_loop first.")

    from_state = state["current_state"]

    if not _validate_transition(from_state, to_state):
        raise ValueError(
            f"Invalid transition: {from_state} -> {to_state}. "
            f"Allowed: {VALID_TRANSITIONS.get(from_state, [])}"
        )

    _record_transition(state, from_state, to_state, trigger, classification)
    _write_state(repo_root, state)
    return state


def classify_and_decide(repo_root: Path, stage3_output_path: Path) -> dict[str, Any]:
    """
    Classify Stage 3 output and decide the next loop action.

    Returns the classification result and updates loop state.
    """
    state = _read_state(repo_root)
    if state is None:
        raise ValueError("Loop state not initialized.")

    # Record Stage 3 output path
    state["stage3_output_path"] = str(stage3_output_path)

    # Classify
    classification = classify_summary(stage3_output_path)
    cls = classification["classification"]
    recommendation = classification["next_stage_recommendation"]

    # Transition to CLASSIFYING
    if state["current_state"] == "EXECUTION_COMPLETE":
        _record_transition(state, "EXECUTION_COMPLETE", "CLASSIFYING", "start_classification", cls)

    # Apply decision rules
    next_state: str
    if cls == "STRUCTURED_ALL_GREEN":
        next_state = "ACCEPTED_ALL_GREEN"
    elif cls == "MISSING":
        next_state = "REROUTE_TO_AUDIT"
    elif cls == "PROSE_ONLY":
        next_state = "REROUTE_TO_HARDEN"
    elif cls == "STRUCTURED_NOT_GREEN":
        if classification.get("failing_items"):
            next_state = "REROUTE_REWORK"
        else:
            next_state = "REROUTE_TO_HARDEN"
    elif cls == "CONTRADICTORY":
        next_state = "HARD_STOP"
    elif cls == "EVIDENCE_MISSING":
        next_state = "REROUTE_TO_HARDEN"
    elif cls == "SCORES_MISSING":
        next_state = "REROUTE_TO_HARDEN"
    elif cls == "TASKCARDS_INCOMPLETE":
        next_state = "REROUTE_TO_HARDEN"
    elif cls == "BLOCKED_EXTERNAL":
        next_state = "BLOCKED_EXTERNAL"
    else:
        next_state = "HARD_STOP"

    # Check max loops
    state["iteration"] = state.get("iteration", 0) + 1
    if state["iteration"] >= state.get("max_iterations", DEFAULT_MAX_LOOPS):
        if next_state not in ("ACCEPTED_ALL_GREEN", "BLOCKED_EXTERNAL", "HARD_STOP"):
            next_state = "MAX_LOOPS_EXCEEDED"

    _record_transition(state, "CLASSIFYING", next_state, f"decision:{cls}", cls)
    _write_state(repo_root, state)

    return {
        "classification": classification,
        "next_state": next_state,
        "iteration": state["iteration"],
        "max_iterations": state["max_iterations"],
        "loop_state": state,
    }


def get_next_stages(current_state: str) -> list[str]:
    """
    Given the current loop state, return the list of prompt stages to execute next.

    Returns list like ["PROMPT_1", "PROMPT_2", "PROMPT_3"] or ["PROMPT_2", "PROMPT_3"], etc.
    """
    if current_state == "REROUTE_TO_AUDIT":
        return ["PROMPT_1", "PROMPT_2", "PROMPT_3"]
    elif current_state in ("REROUTE_TO_HARDEN",):
        return ["PROMPT_2", "PROMPT_3"]
    elif current_state == "REROUTE_REWORK":
        return ["PROMPT_3"]
    elif current_state == "ACCEPTED_ALL_GREEN":
        return []  # Done
    elif current_state in ("MAX_LOOPS_EXCEEDED", "HARD_STOP", "BLOCKED_EXTERNAL"):
        return []  # Terminal
    elif current_state == "INITIAL":
        return ["PROMPT_1", "PROMPT_2", "PROMPT_3"]
    else:
        return []


def run_loop_dry(
    repo_root: Path, run_id: str, stage3_output_path: Path,
    max_loops: int = DEFAULT_MAX_LOOPS,
) -> dict[str, Any]:
    """
    Dry-run: initialize loop, classify a Stage 3 output, and report the decision.
    Does NOT execute any prompts — only demonstrates the classification and decision logic.
    """
    state = init_loop(repo_root, run_id, max_loops)

    # Simulate progression to EXECUTION_COMPLETE
    _record_transition(state, "INITIAL", "AUDIT_RUNNING", "start_audit")
    _record_transition(state, "AUDIT_RUNNING", "AUDIT_COMPLETE", "audit_finished")
    _record_transition(state, "AUDIT_COMPLETE", "HARDENING_RUNNING", "start_hardening")
    _record_transition(state, "HARDENING_RUNNING", "HARDENING_COMPLETE", "hardening_finished")
    _record_transition(state, "HARDENING_COMPLETE", "EXECUTION_RUNNING", "start_execution")
    _record_transition(state, "EXECUTION_RUNNING", "EXECUTION_COMPLETE", "execution_finished")
    _write_state(repo_root, state)

    # Now classify and decide
    result = classify_and_decide(repo_root, stage3_output_path)
    result["next_stages"] = get_next_stages(result["next_state"])
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Post-Sprint Loop Controller — automates Prompt 1/2/3 stage decisions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Commands:\n"
            "  --init          Initialize a new loop state\n"
            "  --classify      Classify Stage 3 output and decide next action\n"
            "  --dry-run       Full dry-run: init + simulate + classify\n"
            "  --status        Show current loop state\n"
            "  --next-stages   Show what stages to execute next\n"
            "\nExit codes: 0=all-green/ok, 3=max-loops, 1=invalid, 9=error"
        ),
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--run-id", help="Evidence run ID")
    parser.add_argument("--max-loops", type=int, default=DEFAULT_MAX_LOOPS, help="Max outer loop iterations")
    parser.add_argument("--stage3-output", help="Path to Stage 3 output file for classification")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--init", action="store_true", help="Initialize a new loop")
    group.add_argument("--classify", action="store_true", help="Classify Stage 3 output and decide")
    group.add_argument("--dry-run", action="store_true", help="Full dry-run demonstration")
    group.add_argument("--status", action="store_true", help="Show current loop state")
    group.add_argument("--next-stages", action="store_true", help="Show next stages to execute")

    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()

    try:
        if args.init:
            if not args.run_id:
                print("ERROR: --run-id required for --init", file=sys.stderr)
                return 1
            state = init_loop(repo_root, args.run_id, args.max_loops)
            print(json.dumps(state, indent=2))
            return 0

        elif args.classify:
            if not args.stage3_output:
                print("ERROR: --stage3-output required for --classify", file=sys.stderr)
                return 1
            result = classify_and_decide(repo_root, Path(args.stage3_output))
            print(json.dumps(result, indent=2, default=str))
            next_state = result["next_state"]
            if next_state == "ACCEPTED_ALL_GREEN":
                return 0
            elif next_state == "MAX_LOOPS_EXCEEDED":
                return 3
            elif next_state in ("HARD_STOP", "BLOCKED_EXTERNAL"):
                return 1
            return 0

        elif args.dry_run:
            if not args.run_id:
                print("ERROR: --run-id required for --dry-run", file=sys.stderr)
                return 1
            if not args.stage3_output:
                print("ERROR: --stage3-output required for --dry-run", file=sys.stderr)
                return 1
            result = run_loop_dry(repo_root, args.run_id, Path(args.stage3_output), args.max_loops)
            print(json.dumps(result, indent=2, default=str))
            next_state = result["next_state"]
            if next_state == "ACCEPTED_ALL_GREEN":
                return 0
            elif next_state == "MAX_LOOPS_EXCEEDED":
                return 3
            return 0

        elif args.status:
            state = _read_state(repo_root)
            if state is None:
                print("No active loop state found.")
                return 1
            print(json.dumps(state, indent=2))
            return 0

        elif args.next_stages:
            state = _read_state(repo_root)
            if state is None:
                print("No active loop state found.")
                return 1
            stages = get_next_stages(state["current_state"])
            print(json.dumps({"current_state": state["current_state"], "next_stages": stages}, indent=2))
            return 0

    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 9

    return 0


if __name__ == "__main__":
    sys.exit(main())

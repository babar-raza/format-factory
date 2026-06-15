"""No-stop watchdog — prevents premature sprint termination.

This validator checks whether the agent is allowed to stop the current sprint.
It must be consulted before any "Sprint Complete" declaration. If it returns
BLOCK, the agent must continue executing (rework, next action, safe lanes).

Usage:
    python tools/supervisor/validate_no_stop_watchdog.py --evidence-root .local/evidences/<run_id>

Exit codes:
    0 — ALLOW_STOP: No remaining work; agent may stop.
    1 — BLOCK_STOP: Work remains; agent must continue.
    2 — ERROR: Invalid arguments.
"""

from __future__ import annotations

import json
import sys
import argparse
from pathlib import Path


def _find_repo_root(evidence_root: Path) -> Path:
    p = evidence_root.resolve()
    for _ in range(10):
        if (p / ".git").exists() or (p / "CLAUDE.md").exists():
            return p
        parent = p.parent
        if parent == p:
            break
        p = parent
    return evidence_root.resolve().parent.parent.parent


def check_continuation_signal(repo_root: Path) -> dict:
    """Check if continuation signal allows stopping."""
    signal_path = repo_root / ".local" / "supervisor" / "continuation-signal.json"
    if not signal_path.is_file():
        return {"check": "continuation_signal", "blocks_stop": False,
                "reason": "No continuation signal found"}
    try:
        signal = json.loads(signal_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"check": "continuation_signal", "blocks_stop": False,
                "reason": "Malformed signal file"}

    blocks = []
    ac = signal.get("autonomous_continue")
    if ac in (True, "true", "true_with_rework"):
        blocks.append(f"autonomous_continue={ac}")

    cs = signal.get("continuation_state", "")
    if cs.startswith("YES"):
        blocks.append(f"continuation_state={cs}")

    rework = signal.get("rework_items", [])
    if rework:
        blocks.append(f"rework_items={rework}")

    safe = signal.get("safe_lanes_available")
    hard_stops = signal.get("hard_stops_detected", [])
    if safe and not hard_stops:
        blocks.append("safe_lanes_available=true with no hard stops")

    return {
        "check": "continuation_signal",
        "blocks_stop": len(blocks) > 0,
        "blocking_reasons": blocks,
        "reason": "; ".join(blocks) if blocks else "Signal allows stop",
    }


def check_next_action(repo_root: Path) -> dict:
    """Check if executable next action exists."""
    action_path = repo_root / ".local" / "supervisor" / "next-action.json"
    if not action_path.is_file():
        return {"check": "next_action", "blocks_stop": False,
                "reason": "No next-action.json"}
    try:
        action = json.loads(action_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"check": "next_action", "blocks_stop": False,
                "reason": "Malformed next-action.json"}

    action_type = action.get("action_type", "")
    non_blocking = {"QUEUE_HEALTH_CHECK", "RUN_MD_NONEMPTY_CHECK",
                    "RUN_JSON_VALIDATION", "UPDATE_STATE",
                    "GENERATE_EVIDENCE_STUB"}
    is_executable = action_type not in non_blocking
    return {
        "check": "next_action",
        "blocks_stop": is_executable,
        "action_type": action_type,
        "reason": f"Executable next action: {action_type}" if is_executable
                  else f"Non-blocking action: {action_type}",
    }


def check_action_queue(repo_root: Path) -> dict:
    """Check if action queue has pending executable items."""
    queue_path = repo_root / ".local" / "supervisor" / "action-queue.jsonl"
    if not queue_path.is_file():
        return {"check": "action_queue", "blocks_stop": False,
                "reason": "No action queue file"}
    pending = 0
    try:
        for line in queue_path.read_text(encoding="utf-8").strip().splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            status = item.get("status", "")
            if status not in ("done", "failed", "stale", "skipped"):
                pending += 1
    except (json.JSONDecodeError, OSError):
        pass

    return {
        "check": "action_queue",
        "blocks_stop": pending > 0,
        "pending_count": pending,
        "reason": f"{pending} pending queue items" if pending
                  else "All queue items done/failed/stale",
    }


def check_rework_items(repo_root: Path) -> dict:
    """Check if rework items exist in continuation signal."""
    signal_path = repo_root / ".local" / "supervisor" / "continuation-signal.json"
    if not signal_path.is_file():
        return {"check": "rework_items", "blocks_stop": False,
                "reason": "No continuation signal"}
    try:
        signal = json.loads(signal_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"check": "rework_items", "blocks_stop": False,
                "reason": "Malformed signal"}

    rework = signal.get("rework_items", [])
    return {
        "check": "rework_items",
        "blocks_stop": len(rework) > 0,
        "items": rework,
        "reason": f"Rework items: {rework}" if rework else "No rework items",
    }


ALL_CHECKS = [
    check_continuation_signal,
    check_next_action,
    check_action_queue,
    check_rework_items,
]


def run_no_stop_watchdog(evidence_root: Path) -> dict:
    """Run all watchdog checks. Returns verdict and blocking reasons."""
    repo_root = _find_repo_root(evidence_root)
    results = []
    for check_fn in ALL_CHECKS:
        result = check_fn(repo_root)
        results.append(result)

    any_blocks = any(r["blocks_stop"] for r in results)
    blocking = [r for r in results if r["blocks_stop"]]

    # Determine next action recommendation
    next_action = None
    if any_blocks:
        # Priority: rework first, then next action, then queue
        for r in results:
            if r["check"] == "rework_items" and r["blocks_stop"]:
                next_action = f"Execute rework: {r.get('items', [])}"
                break
        if not next_action:
            for r in results:
                if r["check"] == "next_action" and r["blocks_stop"]:
                    next_action = f"Execute next action: {r.get('action_type')}"
                    break
        if not next_action:
            next_action = "Continue with safe lanes"

    return {
        "verdict": "BLOCK_STOP" if any_blocks else "ALLOW_STOP",
        "checks": results,
        "blocking_count": len(blocking),
        "blocking_checks": [r["check"] for r in blocking],
        "next_action": next_action,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="No-stop watchdog validator")
    parser.add_argument("--evidence-root", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    evidence_root = Path(args.evidence_root)
    if not evidence_root.is_dir():
        print(f"ERROR: {evidence_root} not found", file=sys.stderr)
        return 2

    result = run_no_stop_watchdog(evidence_root)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"No-Stop Watchdog: {result['verdict']}")
        for check in result["checks"]:
            status = "BLOCK" if check["blocks_stop"] else "OK"
            print(f"  [{status}] {check['check']}: {check['reason']}")
        if result["next_action"]:
            print(f"  Next action: {result['next_action']}")

    return 0 if result["verdict"] == "ALLOW_STOP" else 1


if __name__ == "__main__":
    sys.exit(main())

"""Select the next best action for a given stream based on current state.

Examines the capability matrix, lane ledger, and selected gaps to determine
what should be done next in each stream.

Returns a ranked list of actions with rationale.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

STREAM_LABELS = ("mainstream", "acceleration", "skills", "supervisor")

ACTION_TYPES = (
    "implement_capability",
    "add_tests",
    "generate_handoff",
    "expand_skill_registry",
    "fix_anti_skip_violation",
    "run_package_proof",
    "update_capability_matrix",
    "generate_stream_prompt",
)


def load_json_safe(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def load_yaml_safe(path: Path) -> dict[str, Any]:
    if path.exists():
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {}


def _score_gap(gap: dict[str, Any]) -> int:
    """Score a gap for next-best-action ranking."""
    score = gap.get("priority_score", 50)
    if gap.get("decision") == "GOVERNED_HANDOFF_REQUIRED":
        score += 15
    if gap.get("decision") == "GOVERNED_SKILL_REQUIRED":
        score += 10
    if gap.get("work_type") == "product_source_change":
        score += 5
    return score


def select_next_actions(
    gaps: list[dict[str, Any]],
    stream: str,
    lane_ledger: dict[str, Any] | None = None,
    max_actions: int = 5,
) -> list[dict[str, Any]]:
    """Select ranked next actions for a stream."""
    stream_gaps = [g for g in gaps if g.get("stream") == stream]
    if not stream_gaps and stream == "mainstream":
        stream_gaps = [g for g in gaps if g.get("stream") not in ("supervisor",)]

    actions: list[dict[str, Any]] = []

    # Check for anti-skip violations first
    completed_lanes = []
    if lane_ledger:
        completed_lanes = [l for l in lane_ledger.get("lanes", []) if l.get("status") == "completed"]
    lanes_without_logs = [l for l in completed_lanes if not l.get("raw_log_path")]
    if lanes_without_logs:
        actions.append({
            "action_type": "fix_anti_skip_violation",
            "priority": 200,
            "target": "missing_raw_logs",
            "details": f"{len(lanes_without_logs)} lanes missing raw_log_path",
            "rationale": "Raw logs are mandatory evidence. Fix before new work.",
        })

    # Score and rank gaps
    scored = sorted(stream_gaps, key=_score_gap, reverse=True)
    for gap in scored[:max_actions]:
        action_type = "implement_capability"
        if gap.get("decision") == "GOVERNED_HANDOFF_REQUIRED":
            action_type = "generate_handoff"
        elif gap.get("work_type") == "test_only_change":
            action_type = "add_tests"

        actions.append({
            "action_type": action_type,
            "priority": _score_gap(gap),
            "target": gap.get("gap_id", ""),
            "capability_path": gap.get("capability_path", ""),
            "format": gap.get("format", ""),
            "decision": gap.get("decision", ""),
            "rationale": f"{gap.get('format')} {gap.get('capability_path')} is {gap.get('current_status')}",
        })

    # Add stream-specific meta-actions
    if stream == "acceleration":
        actions.append({
            "action_type": "expand_skill_registry",
            "priority": 30,
            "target": "skill_registry",
            "rationale": "Check for unregistered tools that should become governed skills.",
        })
    if stream == "mainstream":
        actions.append({
            "action_type": "run_package_proof",
            "priority": 25,
            "target": "package_matrix",
            "rationale": "Verify all packages build and import after capability changes.",
        })

    return sorted(actions, key=lambda a: -a["priority"])[:max_actions]


def select_all_streams(
    gaps: list[dict[str, Any]],
    lane_ledger: dict[str, Any] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Select next actions for all streams."""
    return {stream: select_next_actions(gaps, stream, lane_ledger) for stream in STREAM_LABELS}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gaps", type=Path, required=True, help="selected-product-gaps.json")
    parser.add_argument("--lane-ledger", type=Path, default=None)
    parser.add_argument("--stream", default=None, help="Filter to one stream")
    parser.add_argument("--max-actions", type=int, default=5)
    args = parser.parse_args()

    data = load_json_safe(args.gaps)
    gaps = data.get("selected_gaps", data if isinstance(data, list) else [])
    ledger = load_json_safe(args.lane_ledger) if args.lane_ledger else None

    if args.stream:
        actions = select_next_actions(gaps, args.stream, ledger, args.max_actions)
        print(json.dumps(actions, indent=2))
    else:
        all_actions = select_all_streams(gaps, ledger)
        print(json.dumps(all_actions, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

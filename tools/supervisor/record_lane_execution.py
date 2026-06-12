"""Record lane execution metadata for parallel/broad sprint tracking.

v2 improvements (R100):
- dependency_graph: list of prerequisite lane_ids
- subagent_id: unique subagent identifier
- bottleneck_tags: list of bottleneck categories
- command_log: list of {command, started_at, ended_at} dicts
- handoff_from / handoff_to: lane handoff tracking

v3 improvements (R101):
- stream_id: classification stream (mainstream/acceleration/skills/supervisor)
- raw_log_path: path to raw log file for this lane

Captures per-lane:
- lane_id, start/end timestamps, duration
- concurrency group, owner/subagent id
- files read and changed
- commands executed
- tests run and results
- evidence artifacts produced
- status and blockers

Output: lane-execution-ledger.json (append mode)
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent


LANE_SCHEMA = {
    "type": "object",
    "required": ["lane_id", "sprint_id", "status"],
    "properties": {
        "lane_id": {"type": "string"},
        "sprint_id": {"type": "string"},
        "concurrency_group": {"type": "string"},
        "owner": {"type": "string"},
        "started_at": {"type": "string", "format": "date-time"},
        "ended_at": {"type": ["string", "null"], "format": "date-time"},
        "duration_seconds": {"type": ["number", "null"]},
        "files_read": {"type": "array", "items": {"type": "string"}},
        "files_changed": {"type": "array", "items": {"type": "string"}},
        "commands": {"type": "array", "items": {"type": "string"}},
        "tests_run": {"type": "array", "items": {"type": "string"}},
        "test_count": {"type": "integer"},
        "tests_passed": {"type": "integer"},
        "tests_failed": {"type": "integer"},
        "evidence_artifacts": {"type": "array", "items": {"type": "string"}},
        "status": {
            "type": "string",
            "enum": ["pending", "in_progress", "completed", "blocked", "failed"],
        },
        "blockers": {"type": "array", "items": {"type": "string"}},
        "notes": {"type": "string"},
    },
}


def new_lane(
    lane_id: str,
    sprint_id: str,
    concurrency_group: str = "",
    owner: str = "claude-primary",
    subagent_id: str = "",
    dependency_graph: list[str] | None = None,
    handoff_from: str = "",
    stream_id: str = "mainstream",
    raw_log_path: str = "",
) -> dict[str, Any]:
    """Create a new lane record with start timestamp."""
    return {
        "lane_id": lane_id,
        "sprint_id": sprint_id,
        "concurrency_group": concurrency_group,
        "owner": owner,
        "subagent_id": subagent_id,
        "stream_id": stream_id,
        "raw_log_path": raw_log_path,
        "dependency_graph": dependency_graph or [],
        "handoff_from": handoff_from,
        "handoff_to": "",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "ended_at": None,
        "duration_seconds": None,
        "files_read": [],
        "files_changed": [],
        "commands": [],
        "command_log": [],
        "tests_run": [],
        "test_count": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "evidence_artifacts": [],
        "status": "in_progress",
        "blockers": [],
        "bottleneck_tags": [],
        "notes": "",
    }


def log_command(lane: dict[str, Any], command: str) -> dict[str, Any]:
    """Log a command execution start in the lane's command_log."""
    entry = {
        "command": command,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "ended_at": None,
    }
    lane.setdefault("command_log", []).append(entry)
    if command not in lane.get("commands", []):
        lane.setdefault("commands", []).append(command)
    return entry


def close_command(lane: dict[str, Any], command: str) -> None:
    """Close the most recent matching command_log entry."""
    for entry in reversed(lane.get("command_log", [])):
        if entry["command"] == command and entry.get("ended_at") is None:
            entry["ended_at"] = datetime.now(timezone.utc).isoformat()
            return


def detect_bottlenecks(lane: dict[str, Any]) -> list[str]:
    """Detect bottleneck tags from lane data."""
    tags: list[str] = []
    duration = lane.get("duration_seconds")
    if duration is not None and duration > 300:
        tags.append("slow_lane")
    if lane.get("blockers"):
        tags.append("blocked")
    if lane.get("tests_failed", 0) > 0:
        tags.append("test_failures")
    if not lane.get("files_changed"):
        tags.append("no_output")
    if lane.get("dependency_graph"):
        tags.append("has_dependencies")
    lane["bottleneck_tags"] = tags
    return tags


def close_lane(lane: dict[str, Any], status: str = "completed", handoff_to: str = "") -> dict[str, Any]:
    """Close a lane with end timestamp, computed duration, and bottleneck detection."""
    lane["ended_at"] = datetime.now(timezone.utc).isoformat()
    lane["status"] = status
    if handoff_to:
        lane["handoff_to"] = handoff_to
    if lane.get("started_at"):
        try:
            start = datetime.fromisoformat(lane["started_at"])
            end = datetime.fromisoformat(lane["ended_at"])
            lane["duration_seconds"] = round((end - start).total_seconds(), 2)
        except (ValueError, TypeError):
            pass
    detect_bottlenecks(lane)
    return lane


def load_ledger(path: Path) -> dict[str, Any]:
    """Load or initialize the lane execution ledger."""
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "schema_version": "1.0",
        "lanes": [],
    }


def save_ledger(path: Path, ledger: dict[str, Any]) -> None:
    """Save the lane execution ledger."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")


def append_lane(ledger_path: Path, lane: dict[str, Any]) -> dict[str, Any]:
    """Append a lane to the ledger, updating if lane_id already exists."""
    ledger = load_ledger(ledger_path)
    existing_idx = None
    for i, existing in enumerate(ledger["lanes"]):
        if existing.get("lane_id") == lane["lane_id"]:
            existing_idx = i
            break
    if existing_idx is not None:
        ledger["lanes"][existing_idx] = lane
    else:
        ledger["lanes"].append(lane)
    save_ledger(ledger_path, ledger)
    return ledger


def ledger_summary(ledger: dict[str, Any]) -> dict[str, Any]:
    """Compute summary statistics from the ledger."""
    lanes = ledger.get("lanes", [])
    statuses = {}
    total_duration = 0.0
    total_tests = 0
    total_passed = 0
    total_files = set()
    for lane in lanes:
        status = lane.get("status", "unknown")
        statuses[status] = statuses.get(status, 0) + 1
        if lane.get("duration_seconds"):
            total_duration += lane["duration_seconds"]
        total_tests += lane.get("test_count", 0)
        total_passed += lane.get("tests_passed", 0)
        for f in lane.get("files_changed", []):
            total_files.add(f)
    return {
        "lane_count": len(lanes),
        "status_counts": statuses,
        "total_duration_seconds": round(total_duration, 2),
        "total_tests": total_tests,
        "total_tests_passed": total_passed,
        "total_files_changed": len(total_files),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action")

    start = sub.add_parser("start", help="Start a new lane")
    start.add_argument("--lane-id", required=True)
    start.add_argument("--sprint-id", required=True)
    start.add_argument("--group", default="")
    start.add_argument("--owner", default="claude-primary")
    start.add_argument("--ledger", type=Path, required=True)

    close_cmd = sub.add_parser("close", help="Close a lane")
    close_cmd.add_argument("--lane-id", required=True)
    close_cmd.add_argument("--status", default="completed")
    close_cmd.add_argument("--files-changed", nargs="*", default=[])
    close_cmd.add_argument("--tests-passed", type=int, default=0)
    close_cmd.add_argument("--tests-failed", type=int, default=0)
    close_cmd.add_argument("--evidence", nargs="*", default=[])
    close_cmd.add_argument("--notes", default="")
    close_cmd.add_argument("--ledger", type=Path, required=True)

    summary_cmd = sub.add_parser("summary", help="Print ledger summary")
    summary_cmd.add_argument("--ledger", type=Path, required=True)

    args = parser.parse_args()

    if args.action == "start":
        lane = new_lane(args.lane_id, args.sprint_id, args.group, args.owner)
        append_lane(args.ledger, lane)
        print(f"LANE_STARTED: {args.lane_id}")
        return 0

    elif args.action == "close":
        ledger = load_ledger(args.ledger)
        found = None
        for lane in ledger["lanes"]:
            if lane.get("lane_id") == args.lane_id:
                found = lane
                break
        if not found:
            print(f"ERROR: Lane {args.lane_id} not found in ledger")
            return 1
        found["files_changed"] = args.files_changed
        found["tests_passed"] = args.tests_passed
        found["tests_failed"] = args.tests_failed
        found["test_count"] = args.tests_passed + args.tests_failed
        found["evidence_artifacts"] = args.evidence
        found["notes"] = args.notes
        close_lane(found, args.status)
        save_ledger(args.ledger, ledger)
        print(f"LANE_CLOSED: {args.lane_id} ({args.status})")
        return 0

    elif args.action == "summary":
        ledger = load_ledger(args.ledger)
        s = ledger_summary(ledger)
        print(json.dumps(s, indent=2))
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

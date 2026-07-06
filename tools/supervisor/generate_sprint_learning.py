"""Generate sprint learning reports from lane execution data.

v2 improvements (R100):
- parallelization-suggestions.md — identifies lanes that ran sequentially but could be parallel
- repeated-command-inventory.md — finds repeated commands across lanes
- shallow-evidence-warnings.md — flags work items with low test counts or no files changed

Produces:
- agent-learning-notes.md
- speed-bottlenecks.md
- next-agent-briefing.md
- manual-process-to-skill-candidates.md
- parallelization-suggestions.md (v2)
- repeated-command-inventory.md (v2)
- shallow-evidence-warnings.md (v2)

Inputs: lane-execution-ledger.json, work-item-grades, product-code ledger, selected gaps
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent


def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> Any:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def generate_learning_notes(
    lane_ledger: dict,
    work_item_grades: dict | list,
    sprint_id: str,
) -> str:
    """Generate agent-learning-notes.md content."""
    lines = [
        f"# {sprint_id} Agent Learning Notes",
        "",
        "## What was fast",
    ]

    lanes = lane_ledger.get("lanes", [])
    fast_lanes = sorted(
        [l for l in lanes if l.get("duration_seconds") and l["status"] == "completed"],
        key=lambda x: x["duration_seconds"],
    )
    for lane in fast_lanes[:3]:
        lines.append(f"- {lane['lane_id']}: {lane.get('duration_seconds', '?')}s")

    lines.extend(["", "## What was slow"])
    slow_lanes = sorted(
        [l for l in lanes if l.get("duration_seconds") and l["status"] == "completed"],
        key=lambda x: -x["duration_seconds"],
    )
    for lane in slow_lanes[:3]:
        lines.append(f"- {lane['lane_id']}: {lane.get('duration_seconds', '?')}s")

    lines.extend(["", "## What was blocked"])
    blocked = [l for l in lanes if l["status"] == "blocked"]
    for lane in blocked:
        blockers = ", ".join(lane.get("blockers", ["unknown"]))
        lines.append(f"- {lane['lane_id']}: {blockers}")
    if not blocked:
        lines.append("- (none)")

    lines.extend(["", "## Grade summary"])
    if isinstance(work_item_grades, list):
        grades = work_item_grades
    elif isinstance(work_item_grades, dict):
        grades = work_item_grades.get("work_item_grades", [])
    else:
        grades = []
    grade_counts: dict[str, int] = {}
    for g in grades:
        grade = g.get("supervisor_grade", g.get("grade", "UNKNOWN"))
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    for grade, count in sorted(grade_counts.items()):
        lines.append(f"- {grade}: {count}")

    return "\n".join(lines) + "\n"


def generate_speed_bottlenecks(lane_ledger: dict, sprint_id: str) -> str:
    """Generate speed-bottlenecks.md content."""
    lines = [
        f"# {sprint_id} Speed Bottlenecks",
        "",
    ]

    lanes = lane_ledger.get("lanes", [])
    total_time = sum(l.get("duration_seconds") or 0 for l in lanes)
    lines.append(f"Total lane time: {total_time:.0f}s")
    lines.append("")

    # Blocked lanes
    blocked = [l for l in lanes if l["status"] in ("blocked", "failed")]
    if blocked:
        lines.append("## Blocked / Failed Lanes")
        for lane in blocked:
            lines.append(f"- {lane['lane_id']}: {lane['status']}")
            for b in lane.get("blockers", []):
                lines.append(f"  - {b}")
        lines.append("")

    # Longest lanes
    by_duration = sorted(
        [l for l in lanes if l.get("duration_seconds")],
        key=lambda x: -x["duration_seconds"],
    )
    if by_duration:
        lines.append("## Longest Lanes")
        for lane in by_duration[:5]:
            pct = (lane["duration_seconds"] / total_time * 100) if total_time else 0
            lines.append(f"- {lane['lane_id']}: {lane['duration_seconds']:.0f}s ({pct:.0f}%)")

    return "\n".join(lines) + "\n"


def generate_next_agent_briefing(
    lane_ledger: dict,
    selected_gaps: dict,
    sprint_id: str,
) -> str:
    """Generate next-agent-briefing.md content."""
    lines = [
        f"# Next Agent Briefing (after {sprint_id})",
        "",
        "## Priority actions",
    ]

    # Incomplete lanes become next priorities
    lanes = lane_ledger.get("lanes", [])
    incomplete = [l for l in lanes if l["status"] not in ("completed",)]
    if incomplete:
        lines.append("### Incomplete lanes from this sprint")
        for lane in incomplete:
            lines.append(f"- {lane['lane_id']} ({lane['status']})")
    else:
        lines.append("- All lanes completed")

    lines.extend(["", "## Remaining gaps"])
    gaps = selected_gaps.get("selected_gaps", [])
    mainstream = [g for g in gaps if g.get("stream") == "mainstream"]
    for gap in mainstream[:5]:
        lines.append(f"- {gap.get('gap_id', '?')}: {gap.get('description', '')[:80]}")

    lines.extend(["", "## Recommendations"])
    lines.append("1. Prioritize save/export/dogfood APIs over shallow queries")
    lines.append("2. Capture raw test logs for every test run")
    lines.append("3. Use governed skill invocation with transcript")
    lines.append("4. Update lane execution ledger for every train")

    return "\n".join(lines) + "\n"


def generate_skill_candidates(lane_ledger: dict, sprint_id: str) -> str:
    """Generate manual-process-to-skill-candidates.md content."""
    lines = [
        f"# {sprint_id} Manual Process to Skill Candidates",
        "",
        "## Processes observed that should become skills",
        "",
    ]

    lanes = lane_ledger.get("lanes", [])
    # Look for patterns in notes
    manual_patterns = set()
    for lane in lanes:
        notes = lane.get("notes", "").lower()
        if "manual" in notes:
            manual_patterns.add(lane.get("notes", ""))
        commands = lane.get("commands", [])
        for cmd in commands:
            if "pytest" in cmd.lower() or "dotnet test" in cmd.lower():
                manual_patterns.add("raw test log capture (test output redirect)")
            if "git diff" in cmd.lower():
                manual_patterns.add("source diff capture (git diff to file)")

    if manual_patterns:
        for p in sorted(manual_patterns):
            lines.append(f"- {p}")
    else:
        lines.append("- Lane execution recording (now automated via record_lane_execution.py)")
        lines.append("- Raw test log capture (redirect test output to file)")
        lines.append("- Source diff capture (git diff to file)")
        lines.append("- Sprint report generation (preflight, scoreboard, lane ownership)")

    return "\n".join(lines) + "\n"


def generate_parallelization_suggestions(lane_ledger: dict, sprint_id: str) -> str:
    """Identify lanes in the same group that ran sequentially but could be parallel."""
    lines = [
        f"# {sprint_id} Parallelization Suggestions",
        "",
    ]
    lanes = lane_ledger.get("lanes", [])
    groups: dict[str, list[dict]] = {}
    for lane in lanes:
        group = lane.get("concurrency_group", "")
        if group:
            groups.setdefault(group, []).append(lane)

    suggestions = []
    for group, group_lanes in sorted(groups.items()):
        if len(group_lanes) < 2:
            continue
        independent = [l for l in group_lanes if not l.get("dependency_graph")]
        if len(independent) >= 2:
            ids = [l["lane_id"] for l in independent]
            suggestions.append(f"- Group `{group}`: {', '.join(ids)} have no dependencies — run in parallel")

    if suggestions:
        lines.extend(suggestions)
    else:
        lines.append("- No additional parallelization opportunities found")
    return "\n".join(lines) + "\n"


def generate_repeated_command_inventory(lane_ledger: dict, sprint_id: str) -> str:
    """Find commands repeated across multiple lanes."""
    lines = [
        f"# {sprint_id} Repeated Command Inventory",
        "",
    ]
    lanes = lane_ledger.get("lanes", [])
    cmd_counts: dict[str, int] = {}
    for lane in lanes:
        for cmd in lane.get("commands", []):
            cmd_counts[cmd] = cmd_counts.get(cmd, 0) + 1

    repeated = {cmd: count for cmd, count in cmd_counts.items() if count > 1}
    if repeated:
        for cmd, count in sorted(repeated.items(), key=lambda x: -x[1]):
            lines.append(f"- `{cmd}` — {count} lanes")
    else:
        lines.append("- No repeated commands found")
    return "\n".join(lines) + "\n"


def generate_shallow_evidence_warnings(lane_ledger: dict, sprint_id: str) -> str:
    """Flag lanes with low test counts or no files changed."""
    lines = [
        f"# {sprint_id} Shallow Evidence Warnings",
        "",
    ]
    lanes = lane_ledger.get("lanes", [])
    warnings = []
    for lane in lanes:
        if lane.get("status") != "completed":
            continue
        issues = []
        if lane.get("test_count", 0) == 0:
            issues.append("zero tests")
        if not lane.get("files_changed"):
            issues.append("no files changed")
        if not lane.get("evidence_artifacts"):
            issues.append("no evidence artifacts")
        if issues:
            warnings.append(f"- {lane['lane_id']}: {', '.join(issues)}")

    if warnings:
        lines.extend(warnings)
    else:
        lines.append("- All completed lanes have adequate evidence")
    return "\n".join(lines) + "\n"


def generate_all(
    sprint_id: str,
    lane_ledger_path: Path,
    grades_path: Path,
    gaps_path: Path,
    output_dir: Path,
) -> dict[str, str]:
    """Generate all sprint learning reports."""
    output_dir.mkdir(parents=True, exist_ok=True)

    lane_ledger = load_json(lane_ledger_path)
    grades = load_json(grades_path)
    gaps = load_json(gaps_path)

    outputs = {}

    notes = generate_learning_notes(lane_ledger, grades, sprint_id)
    notes_path = output_dir / "agent-learning-notes.md"
    notes_path.write_text(notes, encoding="utf-8")
    outputs["agent-learning-notes"] = str(notes_path)

    bottlenecks = generate_speed_bottlenecks(lane_ledger, sprint_id)
    bottlenecks_path = output_dir / "speed-bottlenecks.md"
    bottlenecks_path.write_text(bottlenecks, encoding="utf-8")
    outputs["speed-bottlenecks"] = str(bottlenecks_path)

    briefing = generate_next_agent_briefing(lane_ledger, gaps, sprint_id)
    briefing_path = output_dir / "next-agent-briefing.md"
    briefing_path.write_text(briefing, encoding="utf-8")
    outputs["next-agent-briefing"] = str(briefing_path)

    candidates = generate_skill_candidates(lane_ledger, sprint_id)
    candidates_path = output_dir / "manual-process-to-skill-candidates.md"
    candidates_path.write_text(candidates, encoding="utf-8")
    outputs["manual-process-to-skill-candidates"] = str(candidates_path)

    parallel = generate_parallelization_suggestions(lane_ledger, sprint_id)
    parallel_path = output_dir / "parallelization-suggestions.md"
    parallel_path.write_text(parallel, encoding="utf-8")
    outputs["parallelization-suggestions"] = str(parallel_path)

    repeated = generate_repeated_command_inventory(lane_ledger, sprint_id)
    repeated_path = output_dir / "repeated-command-inventory.md"
    repeated_path.write_text(repeated, encoding="utf-8")
    outputs["repeated-command-inventory"] = str(repeated_path)

    shallow = generate_shallow_evidence_warnings(lane_ledger, sprint_id)
    shallow_path = output_dir / "shallow-evidence-warnings.md"
    shallow_path.write_text(shallow, encoding="utf-8")
    outputs["shallow-evidence-warnings"] = str(shallow_path)

    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sprint-id", required=True)
    parser.add_argument(
        "--lane-ledger",
        type=Path,
        default=REPO_ROOT / ".local" / "supervisor" / "lane-execution-ledger.json",
    )
    parser.add_argument(
        "--grades",
        type=Path,
        default=REPO_ROOT / "reports" / "supervisor" / "work-item-grades.json",
    )
    parser.add_argument(
        "--gaps",
        type=Path,
        default=REPO_ROOT / ".local" / "supervisor" / "selected-product-gaps.json",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    outputs = generate_all(
        args.sprint_id,
        args.lane_ledger,
        args.grades,
        args.gaps,
        args.output_dir,
    )
    for name, path in outputs.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

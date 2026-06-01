"""
sync_local_memory.py — Format Factory Local Supervisor Control Plane
Appends latest sprint facts to .supervisor/project-memory.md.

Rules:
  - Append only — never overwrites prior entries
  - Idempotent for same sprint_id + bundle_path
  - Marks entries stale when sprint_id is > 3 sprints behind (by R-number)
  - MUST NOT write to AGENTS.md, GOVERNANCE.md, plans/master-plan.md, registry/**

Exit codes:
  0 — success (appended or skipped as idempotent)
  9 — unexpected error

Usage:
  python tools/supervisor/sync_local_memory.py --review reports/supervisor/evidence-review.json
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


FORBIDDEN_WRITE_TARGETS = [
    "AGENTS.md",
    "GOVERNANCE.md",
    "plans/master-plan.md",
    "registry/format-registry.yaml",
]
STALE_THRESHOLD = 3  # entries older than this many R-numbers are marked stale


def load_json(path: Path) -> dict:
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def extract_r_number(sprint_id: str) -> int | None:
    """Extract R-number from sprint ID like FORMAT-FACTORY-R77-..."""
    m = re.search(r"R(\d+)", sprint_id, re.IGNORECASE)
    return int(m.group(1)) if m else None


def is_already_synced(memory_text: str, sprint_id: str, bundle_path: str) -> bool:
    """Check if this sprint_id + bundle combination already exists in memory."""
    if sprint_id not in memory_text:
        return False
    # Check if the bundle path also matches
    if bundle_path and bundle_path in memory_text:
        return True
    # If sprint_id is present but bundle path differs, we still skip (idempotent by sprint_id)
    return sprint_id in memory_text


def mark_stale_entries(memory_text: str, current_r: int | None) -> str:
    """Mark entries older than STALE_THRESHOLD R-numbers as stale."""
    if current_r is None:
        return memory_text

    def replace_stale(match):
        sprint_id = match.group(1)
        r_num = extract_r_number(sprint_id)
        if r_num and current_r - r_num > STALE_THRESHOLD:
            # Mark the header line as stale
            line = match.group(0)
            if "[STALE]" not in line:
                return line.rstrip() + " [STALE]\n"
        return match.group(0)

    # Find and mark stale entry headers
    pattern = r"^## Entry: ([^\n]+)\n"
    return re.sub(pattern, replace_stale, memory_text, flags=re.MULTILINE)


def format_entry(review: dict, additional_facts: dict | None = None) -> str:
    """Format a new memory entry."""
    sprint_id = review.get("sprint_id", "unknown")
    verdict = review.get("verdict", "unknown")
    facts = review.get("facts", {})
    timestamp = datetime.now().isoformat()
    extra = additional_facts or {}

    lines = [
        f"",
        f"## Entry: {sprint_id}",
        f"- timestamp: {timestamp}",
        f"- verdict: {verdict}",
        f"- test_count: {facts.get('test_count', 0)}",
        f"- fail_count: {facts.get('fail_count', 0)}",
        f"- git_head: {facts.get('git_head', 'unknown')}",
        f"- bundle_path: {review.get('bundle_path', 'unknown')}",
        f"- pending_marker_count: {facts.get('pending_marker_count', 0)}",
        f"- bundle_entry_count: {facts.get('bundle_entry_count', 0)}",
        f"- bundle_validation_pass: {facts.get('bundle_validation_pass', 'unknown')}",
    ]

    validator_error_summary = facts.get("validator_error_summary", "")
    if validator_error_summary:
        lines.append(f"- validator_error_summary: {validator_error_summary[:200]}")

    gate_states = facts.get("gate_states", {})
    if gate_states:
        lines.append(f"- gate_states_summary: {json.dumps(gate_states)}")

    for k, v in extra.items():
        lines.append(f"- {k}: {v}")

    return "\n".join(lines) + "\n"


def sync(
    review: dict,
    memory_path: Path,
    additional_facts: dict | None = None,
) -> dict:
    """Sync latest sprint facts to project-memory.md."""
    sprint_id = review.get("sprint_id", "unknown")
    bundle_path = review.get("bundle_path", "")

    # Read existing memory
    if memory_path.exists():
        memory_text = memory_path.read_text(encoding="utf-8")
    else:
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        memory_text = "# Supervisor Project Memory\n# Append-only. Do not manually overwrite.\n\n"

    # Idempotence check
    if is_already_synced(memory_text, sprint_id, bundle_path):
        return {
            "action": "skipped_idempotent",
            "sprint_id": sprint_id,
            "reason": "Sprint ID already present in memory",
        }

    # Mark stale entries
    current_r = extract_r_number(sprint_id)
    updated_text = mark_stale_entries(memory_text, current_r)

    # Append new entry
    new_entry = format_entry(review, additional_facts)
    final_text = updated_text.rstrip() + "\n" + new_entry

    memory_path.write_text(final_text, encoding="utf-8")

    return {
        "action": "appended",
        "sprint_id": sprint_id,
        "entry_length": len(new_entry),
    }


def write_sync_report(result: dict, output_dir: Path) -> None:
    """Write memory sync report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Memory Sync Report",
        f"Timestamp: {datetime.now().isoformat()}",
        f"Action: {result['action']}",
        f"Sprint ID: {result['sprint_id']}",
    ]
    if result.get("reason"):
        lines.append(f"Reason: {result['reason']}")
    if result.get("entry_length"):
        lines.append(f"Entry length: {result['entry_length']} chars")
    (output_dir / "memory-sync-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def compute_test_delta(review: dict, memory_path: Path) -> dict:
    """Compute test count delta from the previous entry in memory."""
    additional = {}
    current_count = review.get("facts", {}).get("test_count", 0)
    if not current_count or not memory_path.exists():
        return additional

    memory_text = memory_path.read_text(encoding="utf-8")
    # Find the most recent test_count entry
    prev_counts = re.findall(r"- test_count:\s*(\d+)", memory_text)
    if prev_counts:
        prev_count = int(prev_counts[-1])
        delta = current_count - prev_count
        additional["test_delta"] = f"{delta:+d}" if delta != 0 else "0"
        additional["test_delta_from"] = str(prev_count)
    return additional


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync sprint facts to .supervisor/project-memory.md"
    )
    parser.add_argument(
        "--review",
        type=Path,
        default=Path("reports/supervisor/evidence-review.json"),
        help="Path to evidence-review.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/supervisor"),
        help="Directory for sync report",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    memory_path = repo_root / ".supervisor" / "project-memory.md"

    # Safety check: never write to forbidden targets
    for forbidden in FORBIDDEN_WRITE_TARGETS:
        target = repo_root / forbidden
        if memory_path.resolve() == target.resolve():
            print(f"ERROR: memory_path points to forbidden target: {forbidden}", file=sys.stderr)
            return 9

    review = load_json(args.review)
    if not review:
        print("WARNING: No evidence review data found. Using empty review.", file=sys.stderr)
        review = {"sprint_id": "unknown", "verdict": "unknown", "facts": {}}

    # Compute test delta from previous entry if possible
    additional_facts = compute_test_delta(review, memory_path)
    result = sync(review, memory_path, additional_facts)
    write_sync_report(result, args.output_dir)

    print(f"MEMORY_SYNC: {result['action'].upper()}")
    print(f"  Sprint: {result['sprint_id']}")
    if result.get("reason"):
        print(f"  Reason: {result['reason']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

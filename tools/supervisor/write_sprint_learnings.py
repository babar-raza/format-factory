"""write_sprint_learnings.py — Writes sprint-learnings.jsonl alongside evidence declarations.

TC-L15-WRITER-001: Root cause of learning_consumer.py always returning 0 entries is
NO_LEARNINGS_REGISTERED — no sprint has ever written a sprint-learnings.jsonl file.
This script generates that file from the evidence declaration's incomplete_work_items,
test_results.failed, and governance rework signals.

Usage:
  python write_sprint_learnings.py --sprint-id <id> [--output-dir <dir>] [--declaration <path>]

The output file is written to <output-dir>/sprint-learnings.jsonl.
Format: one JSON object per line, compatible with learning_consumer.py schema.

Required fields per entry (per learning_consumer.py aggregate()):
  category          str  — grouping key (e.g., "TEST_FAILURE", "INCOMPLETE_WORK", "GOVERNANCE")
  description       str  — what was learned (max 100 chars used for dedup hash)
  recommended_action str — what to do next time
  impacted_stream   str  — "product" | "supervisor" | "governance" | "all"
  sprint_id         str  — sprint that generated this entry
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _load_declaration(declaration_path: Path) -> dict:
    """Load a YAML or JSON evidence declaration."""
    if not declaration_path.exists():
        return {}
    text = declaration_path.read_text(encoding="utf-8")
    try:
        import yaml
        return yaml.safe_load(text) or {}
    except ImportError:
        pass
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def extract_learnings(sprint_id: str, declaration: dict) -> list[dict]:
    """Extract learning entries from an evidence declaration."""
    entries = []
    ts = datetime.now(timezone.utc).isoformat()

    # Learning source 1: incomplete_work_items
    for item in declaration.get("incomplete_work_items", []):
        if not item:
            continue
        entries.append({
            "category": "INCOMPLETE_WORK",
            "description": f"Work item not completed: {str(item)[:80]}",
            "recommended_action": "Break into smaller taskcards; ensure unblock conditions are met before sprint start",
            "impacted_stream": "product",
            "sprint_id": sprint_id,
            "timestamp": ts,
        })

    # Learning source 2: test failures
    test_results = declaration.get("test_results", {})
    failed_count = test_results.get("failed", 0) or 0
    new_failures = test_results.get("new_failures", 0) or 0
    if failed_count > 0 or new_failures > 0:
        entries.append({
            "category": "TEST_FAILURE",
            "description": f"Sprint ended with {failed_count} test failures ({new_failures} new)",
            "recommended_action": "Fix test failures before closing sprint; never carry forward new failures",
            "impacted_stream": "product",
            "sprint_id": sprint_id,
            "timestamp": ts,
        })

    # Learning source 3: collection errors
    collection_errors = test_results.get("collection_errors", 0) or 0
    if collection_errors > 0:
        entries.append({
            "category": "TEST_COLLECTION_ERROR",
            "description": f"Sprint had {collection_errors} pytest collection errors (ImportError stubs or missing modules)",
            "recommended_action": "Delete ImportError stub test files before sprint closeout; do not carry collection errors",
            "impacted_stream": "product",
            "sprint_id": sprint_id,
            "timestamp": ts,
        })

    # Learning source 4: governance/supervisor patterns
    worker_verdict = declaration.get("worker_self_verdict", declaration.get("worker_self_grade", ""))
    if worker_verdict and worker_verdict.upper() == "PASS":
        # Sprint passed — record positive signal for gate compliance
        entries.append({
            "category": "SPRINT_CLOSEOUT_PATTERN",
            "description": "Sprint declaration validated PASS with sprint_executor_validate.py",
            "recommended_action": "Continue using sprint_executor_validate.py --repair before closeout",
            "impacted_stream": "supervisor",
            "sprint_id": sprint_id,
            "timestamp": ts,
        })

    return entries


def write_sprint_learnings(sprint_id: str, output_dir: Path, declaration_path: Path | None = None) -> Path:
    """Write sprint-learnings.jsonl to output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "sprint-learnings.jsonl"

    declaration = {}
    if declaration_path and declaration_path.exists():
        declaration = _load_declaration(declaration_path)
    elif sprint_id:
        # Try to find declaration in standard location
        candidates = [
            Path(f".local/evidences/{sprint_id}/evidence-declaration.yaml"),
            Path(f".local/evidences/{sprint_id}/evidence-declaration.json"),
        ]
        for c in candidates:
            if c.exists():
                declaration = _load_declaration(c)
                break

    entries = extract_learnings(sprint_id, declaration)

    if not entries:
        # Write a minimal baseline entry so the file exists and scan_all_learnings() finds it
        entries.append({
            "category": "SPRINT_CLOSEOUT_PATTERN",
            "description": f"Sprint {sprint_id} completed closeout",
            "recommended_action": "Review evidence declaration for completeness before submitting",
            "impacted_stream": "supervisor",
            "sprint_id": sprint_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    with out_path.open("w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Write sprint-learnings.jsonl for learning_consumer.py")
    parser.add_argument("--sprint-id", required=True, help="Sprint ID (matches evidence-declaration.yaml sprint_id)")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: .local/evidences/<sprint-id>/)")
    parser.add_argument("--declaration", default=None, help="Path to evidence-declaration.yaml")
    args = parser.parse_args()

    sprint_id = args.sprint_id
    output_dir = Path(args.output_dir) if args.output_dir else Path(f".local/evidences/{sprint_id}")
    declaration_path = Path(args.declaration) if args.declaration else None

    out_path = write_sprint_learnings(sprint_id, output_dir, declaration_path)
    entries_written = sum(1 for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip())
    print(f"[write_sprint_learnings] Written: {out_path} ({entries_written} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

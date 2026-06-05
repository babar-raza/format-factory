"""
lane_execution_ledger.py — Generate and validate lane execution ledgers.

A lane execution ledger records what was executed during a sprint, with
lane IDs, commands, exit codes, durations, and log paths.

Schema:
  sprint_id: str
  run_id: str
  generated_at: str (ISO timestamp)
  lanes:
    - lane_id: str
      title: str
      status: completed | partial | failed | skipped
      command: str | null
      exit_code: int | null
      duration_seconds: float | null
      log_path: str | null
      artifacts: list[str]
      notes: str
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


def create_ledger(
    sprint_id: str,
    run_id: str,
    lanes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create a new lane execution ledger."""
    return {
        "sprint_id": sprint_id,
        "run_id": run_id,
        "generated_at": datetime.now().isoformat(),
        "lanes": lanes or [],
    }


def add_lane(
    ledger: dict[str, Any],
    lane_id: str,
    title: str,
    status: str = "completed",
    command: str | None = None,
    exit_code: int | None = None,
    duration_seconds: float | None = None,
    log_path: str | None = None,
    artifacts: list[str] | None = None,
    notes: str = "",
) -> dict[str, Any]:
    """Add a lane entry to the ledger."""
    entry = {
        "lane_id": lane_id,
        "title": title,
        "status": status,
        "command": command,
        "exit_code": exit_code,
        "duration_seconds": duration_seconds,
        "log_path": log_path,
        "artifacts": artifacts or [],
        "notes": notes,
    }
    ledger["lanes"].append(entry)
    return entry


def validate_ledger(ledger: dict[str, Any]) -> dict[str, Any]:
    """Validate a lane execution ledger against the schema.

    R108: Also reports warnings for lanes with null execution metadata.
    """
    errors = []
    warnings = []

    if not ledger.get("sprint_id"):
        errors.append("Missing sprint_id")
    if not ledger.get("run_id"):
        errors.append("Missing run_id")
    if not ledger.get("generated_at"):
        errors.append("Missing generated_at")

    lanes = ledger.get("lanes", [])
    if not lanes:
        errors.append("No lanes in ledger")

    valid_statuses = {"completed", "partial", "failed", "skipped"}
    null_execution_count = 0
    for i, lane in enumerate(lanes):
        lid = lane.get("lane_id", f"lane-{i}")
        if not lane.get("lane_id"):
            errors.append(f"Lane {i}: missing lane_id")
        if not lane.get("title"):
            errors.append(f"Lane {i}: missing title")
        if lane.get("status") not in valid_statuses:
            errors.append(f"Lane {i}: invalid status '{lane.get('status')}' (must be one of {valid_statuses})")
        # R108: Warn about null execution metadata
        if lane.get("command") is None and lane.get("exit_code") is None:
            null_execution_count += 1
            warnings.append(f"{lid}: null command and exit_code (no execution proof)")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "lane_count": len(lanes),
        "completed_count": sum(1 for l in lanes if l.get("status") == "completed"),
        "failed_count": sum(1 for l in lanes if l.get("status") == "failed"),
        "null_execution_count": null_execution_count,
    }


def write_ledger(ledger: dict[str, Any], path: Path) -> None:
    """Write ledger to YAML file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.dump(ledger, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def load_ledger(path: Path) -> dict[str, Any]:
    """Load ledger from YAML file."""
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def generate_from_declaration(
    declaration: dict[str, Any],
    evidence_root: Path,
) -> dict[str, Any]:
    """Generate a lane execution ledger from a declaration.

    Maps declared work items to lane entries. This provides a baseline
    ledger when no explicit lane tracking was done during execution.
    """
    sprint_id = declaration.get("sprint_id", "unknown")
    run_id = declaration.get("run_id", "unknown")

    ledger = create_ledger(sprint_id, run_id)

    for item in declaration.get("planned_work_items", []):
        item_id = item.get("item_id", "unknown")
        title = item.get("title", item_id)
        status = item.get("status", "not_started")

        lane_status = "completed" if status == "completed" else "partial"

        artifacts = []
        for p in item.get("evidence_paths", []):
            artifacts.append(p)
        for t in item.get("test_references", []):
            artifacts.append(t)

        # R108: Populate descriptive command for non-subprocess lanes
        command = f"[manual] {title}"
        exit_code = 0 if lane_status == "completed" else None

        add_lane(
            ledger,
            lane_id=item_id,
            title=title,
            status=lane_status,
            command=command,
            exit_code=exit_code,
            artifacts=artifacts,
            notes=item.get("acceptance_criteria", ""),
        )

    # Add test execution lane if test results exist
    test_results = declaration.get("test_results", {})
    if test_results:
        raw_logs_dir = evidence_root / "raw-logs"
        log_path = None
        capture_meta = None
        if raw_logs_dir.exists():
            combined = raw_logs_dir / "raw-test-log.txt"
            if combined.exists():
                log_path = str(combined)
            # R108: Cross-reference capture-meta.json for real exit_code
            meta_path = raw_logs_dir / "capture-meta.json"
            if meta_path.exists():
                try:
                    capture_meta = json.loads(meta_path.read_text(encoding="utf-8"))
                except Exception:
                    pass

        # Prefer capture-meta exit_code (real pytest result) over declaration-derived
        if capture_meta and "exit_code" in capture_meta:
            real_exit_code = capture_meta["exit_code"]
            duration = capture_meta.get("duration_seconds")
            command = " ".join(capture_meta.get("command", []))
        else:
            real_exit_code = 0 if test_results.get("failed", 0) == 0 else 1
            duration = None
            command = None

        add_lane(
            ledger,
            lane_id="TEST-EXECUTION",
            title="Test suite execution",
            status="completed" if real_exit_code == 0 else "failed",
            command=command,
            exit_code=real_exit_code,
            duration_seconds=duration,
            log_path=log_path,
            notes=f"Passed: {test_results.get('passed', 0)}, Failed: {test_results.get('failed', 0)}, Skipped: {test_results.get('skipped', 0)}",
        )

    return ledger

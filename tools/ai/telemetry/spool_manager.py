"""Spool manager — manages local telemetry spool lifecycle.

Phase 1: local spool only. No external Agent Metrics posting.
Spool replay design placeholder for Phase 2+.
"""

from __future__ import annotations

import json
from pathlib import Path


DEFAULT_SPOOL_PATH = Path(".local/ai/spool")


def get_spool_path() -> Path:
    """Return the canonical spool path."""
    return DEFAULT_SPOOL_PATH


def spool_exists() -> bool:
    """Check if spool file exists."""
    return (DEFAULT_SPOOL_PATH / "ai-telemetry.jsonl").exists()


def spool_record_count() -> int:
    """Count records in the spool."""
    spool_file = DEFAULT_SPOOL_PATH / "ai-telemetry.jsonl"
    if not spool_file.exists():
        return 0
    count = 0
    with open(spool_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                count += 1
    return count


def rotate_spool() -> Path | None:
    """Rotate the spool file by renaming with timestamp.

    Returns the path to the rotated file, or None if no spool exists.
    """
    from datetime import datetime, timezone
    spool_file = DEFAULT_SPOOL_PATH / "ai-telemetry.jsonl"
    if not spool_file.exists():
        return None
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rotated = DEFAULT_SPOOL_PATH / f"ai-telemetry-{ts}.jsonl"
    spool_file.rename(rotated)
    return rotated


# --- Agent Metrics field mapping (Phase 2 local validation) ---

AGENT_METRICS_MAPPING = {
    "timestamp": "timestamp",
    "sprint_id": "job_type",
    "run_id": "run_id",
    "status": "status",
    "operation": "product",
    "input_tokens": "token_usage.input",
    "output_tokens": "token_usage.output",
    "total_tokens": "token_usage.total",
    "api_calls_count": "api_calls_count",
}

AI_LOCAL_ONLY_FIELDS = [
    "model", "role", "provider", "prompt_hash",
    "input_artifact_hashes", "output_artifact_hashes",
    "model_fingerprint", "fallback_used",
    "evidence_path", "endpoint_identity",
    "error_class_redacted",
]


def validate_spool_record(record: dict) -> list[str]:
    """Validate a single spool record for replay readiness."""
    errors: list[str] = []
    if not record.get("timestamp"):
        errors.append("missing_timestamp")
    if not record.get("taskcard_id") and not record.get("gate_id"):
        if not record.get("sprint_id"):
            errors.append("missing_run_context")
    for key, val in record.items():
        if isinstance(val, str) and ("sk-" in val or "Bearer " in val):
            errors.append(f"secret_leak_in_{key}")
    return errors


def validate_spool_for_replay(spool_path: Path) -> dict:
    """Validate all records in a spool for Agent Metrics replay readiness."""
    from tools.ai.telemetry.call_logger import read_spool as _read
    records = _read(spool_path)
    valid = 0
    invalid = 0
    all_errors: list[dict] = []
    for i, rec in enumerate(records):
        errs = validate_spool_record(rec)
        if errs:
            invalid += 1
            all_errors.append({"index": i, "errors": errs})
        else:
            valid += 1
    return {
        "total": len(records),
        "valid": valid,
        "invalid": invalid,
        "errors": all_errors,
        "posted_externally": False,
        "blocked_by_policy": True,
    }


# Phase 2+ placeholder: replay_spool() would POST records to Agent Metrics.
# Not implemented — posted_to_agent_metrics remains False.
# External posting blocked_by_policy until repo gate explicitly authorizes.

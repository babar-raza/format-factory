"""Telemetry drain — posts spool records to Agent Metrics (dry-run by default).

Agent Metrics is the canonical telemetry sink.
Local spool is replay/evidence/offline buffer.
Posting requires explicit env var and policy gate approval.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.ai.telemetry.call_logger import read_spool
from tools.ai.telemetry.spool_manager import (
    validate_spool_record,
)


AGENT_METRICS_ENV_VARS = [
    "AGENT_METRICS_ENDPOINT",
    "AGENT_METRICS_API_KEY",
]

REQUIRED_AGENT_METRICS_FIELDS = [
    "timestamp",
    "agent_name",
    "product",
    "platform",
    "website",
    "website_section",
    "job_type",
    "run_id",
    "sprint_id",
    "taskcard_id",
    "model",
    "endpoint_identity",
    "token_usage",
    "api_calls_count",
    "run_duration_ms",
    "status",
    "posted_to_agent_metrics",
]


def is_agent_metrics_configured() -> bool:
    """Check if Agent Metrics endpoint is configured."""
    return all(
        os.environ.get(var, "").strip()
        for var in AGENT_METRICS_ENV_VARS
    )


def map_spool_to_agent_metrics(
    record: dict[str, Any],
    agent_name: str = "format-factory-ai",
    product: str = "format-factory",
    platform: str = "windows",
    website: str = "professionalize.com",
    website_section: str = "ai-platform",
) -> dict[str, Any]:
    """Map a local spool record to Agent Metrics payload format."""
    payload: dict[str, Any] = {
        "timestamp": record.get("timestamp", datetime.now(timezone.utc).isoformat()),
        "agent_name": agent_name,
        "product": product,
        "platform": platform,
        "website": website,
        "website_section": website_section,
        "job_type": record.get("sprint_id", "unknown"),
        "run_id": record.get("run_id", ""),
        "sprint_id": record.get("sprint_id", ""),
        "taskcard_id": record.get("taskcard_id", ""),
        "model": record.get("model", ""),
        "endpoint_identity": record.get("endpoint_identity", ""),
        "token_usage": {
            "input": record.get("input_tokens", 0),
            "output": record.get("output_tokens", 0),
            "total": record.get("total_tokens", 0),
        },
        "api_calls_count": record.get("api_calls_count", 1),
        "run_duration_ms": record.get("run_duration_ms", 0),
        "status": record.get("status", "unknown"),
        "posted_to_agent_metrics": False,
    }
    return payload


def validate_drain_payload(payload: dict[str, Any]) -> list[str]:
    """Validate a drain payload before posting."""
    errors: list[str] = []
    for field_name in REQUIRED_AGENT_METRICS_FIELDS:
        if field_name not in payload:
            errors.append(f"missing field: {field_name}")

    # Secret check
    payload_str = json.dumps(payload, default=str)
    if "sk-" in payload_str or "Bearer " in payload_str:
        errors.append("secret_detected_in_payload")

    return errors


def drain_spool(
    spool_path: Path,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Drain spool records to Agent Metrics.

    Default: dry_run=True. Records are validated but not posted.
    Returns summary of drain operation.
    """
    records = read_spool(spool_path)
    if not records:
        return {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "posted": 0,
            "dry_run": dry_run,
            "errors": [],
            "blocked_reason": "empty_spool",
        }

    valid_payloads: list[dict[str, Any]] = []
    invalid_records: list[dict[str, Any]] = []

    for i, rec in enumerate(records):
        spool_errors = validate_spool_record(rec)
        if spool_errors:
            invalid_records.append({"index": i, "errors": spool_errors})
            continue

        payload = map_spool_to_agent_metrics(rec)
        payload_errors = validate_drain_payload(payload)
        if payload_errors:
            invalid_records.append({"index": i, "errors": payload_errors})
            continue

        valid_payloads.append(payload)

    posted = 0
    blocked_reason = ""

    if not dry_run:
        if not is_agent_metrics_configured():
            blocked_reason = "blocked_missing_env"
        else:
            blocked_reason = "blocked_by_policy"

    return {
        "total": len(records),
        "valid": len(valid_payloads),
        "invalid": len(invalid_records),
        "posted": posted,
        "dry_run": dry_run,
        "errors": invalid_records,
        "blocked_reason": blocked_reason,
    }

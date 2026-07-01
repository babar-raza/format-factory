"""
tools/llm/run_record.py — LLM Run Record Writer
TC-0005 (Phase 1, 2026-06-18)

Writes JSONL run records to .local/llm-logs/ for every LLM-assisted execution.
See docs/ai/llm-endpoint-strategy.md and AGENTS.md Section B8.

Safety invariants:
- Secrets are NEVER written to run records (use secret_redacted=True)
- authority_state is always "ai_advisory"
- Run records are append-only; never modified after writing
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_LOCAL_DIR = Path(__file__).parents[2] / ".local" / "llm-logs"


def _ensure_log_dir(task_id: str) -> Path:
    """Create .local/llm-logs/<task-id>/ if needed and return it."""
    log_dir = _LOCAL_DIR / task_id
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def write_run_record(
    task_id: str,
    task_type: str,
    endpoint_id: str,
    model_id: str,
    prompt_hash: str,
    response_hash: str,
    format_id: str | None = None,
    status: str = "success",
    error: str | None = None,
    duration_seconds: float | None = None,
    metadata: dict[str, Any] | None = None,
) -> Path:
    """
    Write a single LLM run record as a JSONL line.

    Returns the path to the run record file.
    Secrets must NEVER be passed; prompt_hash and response_hash are SHA-256 digests only.
    """
    log_dir = _ensure_log_dir(task_id)
    record_file = log_dir / "run-record.jsonl"

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_id": task_id,
        "task_type": task_type,
        "format_id": format_id,
        "endpoint_id": endpoint_id,
        "model_id": model_id,
        "prompt_hash": prompt_hash,
        "response_hash": response_hash,
        "status": status,
        "error": error,
        "duration_seconds": duration_seconds,
        "authority_state": "ai_advisory",
        "metadata": metadata or {},
    }

    with record_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    return record_file


def hash_text(text: str) -> str:
    """Return SHA-256 hex digest of text. Use instead of storing full prompt/response."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_unavailable_record(task_id: str, task_type: str, reason: str) -> Path:
    """Write an ENDPOINT_UNAVAILABLE record when no LLM is reachable."""
    return write_run_record(
        task_id=task_id,
        task_type=task_type,
        endpoint_id="UNAVAILABLE",
        model_id="UNAVAILABLE",
        prompt_hash="",
        response_hash="",
        status="ENDPOINT_UNAVAILABLE",
        error=f"ENDPOINT_UNAVAILABLE: {reason}",
    )


def list_run_records(task_id: str) -> list[dict[str, Any]]:
    """Return all run records for a task_id as a list of dicts."""
    log_dir = _LOCAL_DIR / task_id
    record_file = log_dir / "run-record.jsonl"
    if not record_file.exists():
        return []
    records = []
    with record_file.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records

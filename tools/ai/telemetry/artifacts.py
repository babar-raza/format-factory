"""Durable redacted telemetry artifacts — persist pipeline telemetry to disk.

Writes telemetry from live pipeline runs to reports/<run>/live-telemetry/
with all secrets redacted. Only hashes, counts, and status values are stored.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.ai.validators.secret_redaction import redact_text


def write_telemetry_artifact(
    telemetry: dict[str, Any],
    output_dir: Path,
    artifact_name: str = "pipeline-telemetry.json",
) -> Path:
    """Write a redacted telemetry artifact to disk.

    All string values are passed through secret redaction.
    Returns the path to the written artifact.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    redacted = _deep_redact(telemetry)
    redacted["_artifact_metadata"] = {
        "written_at": datetime.now(timezone.utc).isoformat(),
        "redaction_applied": True,
    }
    path = output_dir / artifact_name
    path.write_text(json.dumps(redacted, indent=2, default=str), encoding="utf-8")
    return path


def _deep_redact(obj: Any) -> Any:
    """Recursively redact secrets from a data structure."""
    if isinstance(obj, str):
        return redact_text(obj)
    if isinstance(obj, dict):
        return {k: _deep_redact(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_deep_redact(v) for v in obj]
    return obj

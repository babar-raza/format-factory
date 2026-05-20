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


# Keys whose values are stripped entirely (contain raw prompt/response content)
_CONTENT_STRIP_KEYS = frozenset({
    "prompt", "response", "raw_output", "raw_response", "messages",
    "content", "full_text", "source_text",
})


def write_telemetry_artifact(
    telemetry: dict[str, Any],
    output_dir: Path,
    artifact_name: str = "pipeline-telemetry.json",
    minimize: bool = True,
) -> Path:
    """Write a redacted telemetry artifact to disk.

    All string values are passed through secret redaction.
    When minimize=True, raw prompt/response content keys are stripped
    to keep artifacts small and avoid leaking source material.
    Returns the path to the written artifact.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    data = _strip_content_keys(telemetry) if minimize else telemetry
    redacted = _deep_redact(data)
    redacted["_artifact_metadata"] = {
        "written_at": datetime.now(timezone.utc).isoformat(),
        "redaction_applied": True,
        "content_minimized": minimize,
    }
    path = output_dir / artifact_name
    path.write_text(json.dumps(redacted, indent=2, default=str), encoding="utf-8")
    return path


def _strip_content_keys(obj: Any) -> Any:
    """Remove keys that contain raw prompt/response content."""
    if isinstance(obj, dict):
        return {
            k: ("[stripped]" if k in _CONTENT_STRIP_KEYS else _strip_content_keys(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_strip_content_keys(v) for v in obj]
    return obj


def _deep_redact(obj: Any) -> Any:
    """Recursively redact secrets from a data structure."""
    if isinstance(obj, str):
        return redact_text(obj)
    if isinstance(obj, dict):
        return {k: _deep_redact(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_deep_redact(v) for v in obj]
    return obj

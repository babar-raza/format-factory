"""AI Gateway — single approved call path to LLM endpoints.

All AI calls must go through this gateway. Direct endpoint calls are forbidden.
Secrets are never logged. Every call produces a telemetry record.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

import litellm

from tools.ai.control_plane.config import AIConfig, get_api_key
from tools.ai.schemas.models import AIUsageRecord, CallStatus


# Suppress litellm's verbose logging
litellm.suppress_debug_info = True


def gateway_chat(
    config: AIConfig,
    model: str,
    messages: list[dict[str, str]],
    role: str = "",
    operation: str = "",
    sprint_id: str = "",
    taskcard_id: str = "",
    gate_id: str = "",
) -> tuple[dict[str, Any], AIUsageRecord]:
    """Execute a chat completion through the AI gateway.

    Returns (response_dict, telemetry_record).
    The response_dict contains 'content' and 'usage' keys.
    The telemetry_record is ready for spool writing.
    """
    prompt_hash = hashlib.sha256(
        str(messages).encode()
    ).hexdigest()[:16]

    record = AIUsageRecord(
        provider=config.provider_name,
        endpoint_identity=config.endpoint_identity,
        model=model,
        role=role,
        operation=operation,
        sprint_id=sprint_id,
        taskcard_id=taskcard_id,
        gate_id=gate_id,
        prompt_hash=prompt_hash,
    )

    if not config.is_configured:
        record.status = CallStatus.blocked_missing_env
        record.error_class_redacted = "missing_endpoint_or_key"
        return {"content": "", "usage": {}}, record

    api_key = get_api_key()
    if not api_key:
        record.status = CallStatus.blocked_missing_env
        record.error_class_redacted = "missing_api_key"
        return {"content": "", "usage": {}}, record

    try:
        response = litellm.completion(
            model=f"openai/{model}",
            messages=messages,
            api_key=api_key,
            api_base=config.endpoint,
        )
        content = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        if usage:
            record.input_tokens = getattr(usage, "prompt_tokens", 0) or 0
            record.output_tokens = getattr(usage, "completion_tokens", 0) or 0
            record.total_tokens = getattr(usage, "total_tokens", 0) or 0

        record.status = CallStatus.success
        return {"content": content, "usage": record.model_dump(include={"input_tokens", "output_tokens", "total_tokens"})}, record

    except Exception as exc:
        record.status = CallStatus.error
        record.error_class_redacted = type(exc).__name__
        return {"content": "", "usage": {}}, record

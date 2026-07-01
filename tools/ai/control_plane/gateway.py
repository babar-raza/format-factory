"""AI Gateway — single approved call path to LLM endpoints.

All AI calls must go through this gateway. Direct endpoint calls are forbidden.
Secrets are never logged. Every call produces a telemetry record.
"""

from __future__ import annotations

import hashlib
import os
from typing import Any

import tools.ai.control_plane.config as _ai_config
from tools.ai.control_plane.config import AIConfig
from tools.ai.schemas.models import AIUsageRecord, CallStatus

# Default per-call timeout in seconds. Override via GRADER_LLM_TIMEOUT env var.
# Prevents indefinite hang on SSL read / TCP stall (RC-1 in LLM-GRADER-TIMEOUT-001).
_DEFAULT_LLM_TIMEOUT = 30.0


def _get_litellm():
    """Lazily import litellm only when needed for live calls.

    Raises ImportError with a clear message if litellm is not installed.
    """
    try:
        import litellm
    except ImportError:
        raise ImportError(
            "litellm is required for live AI gateway calls. "
            "Install it with: pip install litellm. "
            "Non-live AI tests and fixture pipelines do not require litellm."
        )
    litellm.suppress_debug_info = True
    return litellm


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

    api_key = _ai_config.get_api_key()
    if not api_key:
        record.status = CallStatus.blocked_missing_env
        record.error_class_redacted = "missing_api_key"
        return {"content": "", "usage": {}}, record

    _timeout = float(os.environ.get("GRADER_LLM_TIMEOUT", str(_DEFAULT_LLM_TIMEOUT)))
    try:
        litellm = _get_litellm()
        response = litellm.completion(
            model=f"openai/{model}",
            messages=messages,
            api_key=api_key,
            api_base=config.endpoint,
            temperature=0,
            timeout=_timeout,  # bounded per RC-1: LLM-GRADER-TIMEOUT-001
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
        # Classify to canonical error class for structured telemetry
        try:
            from tools.supervisor.grader_reliability import classify_exception
            error_cls = classify_exception(exc).value
        except Exception:
            error_cls = type(exc).__name__
        record.status = CallStatus.error
        record.error_class_redacted = error_cls
        return {"content": "", "usage": {}}, record

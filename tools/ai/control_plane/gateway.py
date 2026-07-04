"""AI Gateway — single approved call path to LLM endpoints.

All AI calls must go through this gateway. Direct endpoint calls are forbidden.
Secrets are never logged. Every call produces a telemetry record.
"""

from __future__ import annotations

import concurrent.futures as _futures
import hashlib
import os
import socket
from typing import Any

import tools.ai.control_plane.config as _ai_config
from tools.ai.control_plane.config import AIConfig
from tools.ai.schemas.models import AIUsageRecord, CallStatus

# Default per-call timeout in seconds. Override via GRADER_LLM_TIMEOUT env var.
# Prevents indefinite hang on SSL read / TCP stall (RC-1 in LLM-GRADER-TIMEOUT-001).
# Reduced from 30s → 15s so a hanging SSL read fails fast; retries handle transient drops.
_DEFAULT_LLM_TIMEOUT = 15.0

# Grace period added on top of litellm's own timeout for the thread enforcer (§ below).
_THREAD_DEADLINE_OVERHEAD = 2.0

# Belt-and-suspenders: set a process-wide socket default timeout so that any SSL socket
# created by httpcore/httpx inherits a finite recv() deadline at the OS level.
# This ensures the orphaned worker thread (see _call_litellm_bounded) self-terminates
# rather than leaking indefinitely.  Set once at module import — not per-call — to
# avoid races in multi-threaded environments.
# Does NOT affect sockets that explicitly call sock.settimeout() themselves.
socket.setdefaulttimeout(_DEFAULT_LLM_TIMEOUT + _THREAD_DEADLINE_OVERHEAD)


def _call_litellm_bounded(litellm, model: str, messages, api_key: str,
                          api_base: str, timeout: float):
    """Call litellm.completion with a hard wall-clock deadline.

    Problem: litellm passes timeout= to httpx, which in turn passes it to httpcore.
    httpcore's SyncSSLStream.read() calls ssl.SSLObject.read() which is a blocking
    C-level syscall.  On Windows (and sometimes Linux), this syscall ignores Python's
    select-based timeout and can hang indefinitely when the TLS peer stalls mid-stream.

    Fix: run the litellm call in a worker thread and enforce the deadline from the
    caller via concurrent.futures.Future.result(timeout=...).  The caller is unblocked
    within (timeout + _THREAD_DEADLINE_OVERHEAD) seconds regardless of SSL state.
    The orphaned worker thread will self-terminate once the OS-level socket timeout
    fires (set via socket.setdefaulttimeout above) or when the process exits.

    Raises:
        TimeoutError: when the wall-clock deadline is exceeded.
        Any exception raised by litellm.completion is re-raised unchanged.
    """
    def _inner():
        return litellm.completion(
            model=f"openai/{model}",
            messages=messages,
            api_key=api_key,
            api_base=api_base,
            temperature=0,
            timeout=timeout,
        )

    executor = _futures.ThreadPoolExecutor(max_workers=1)
    future = executor.submit(_inner)
    # shutdown(wait=False) releases the executor immediately; we hold the future ref.
    # If the thread is stuck in recv(), it won't be interrupted here — that's intentional:
    # the OS socket timeout will fire and clean it up asynchronously.
    executor.shutdown(wait=False)
    hard_limit = timeout + _THREAD_DEADLINE_OVERHEAD
    try:
        return future.result(timeout=hard_limit)
    except _futures.TimeoutError:
        raise TimeoutError(
            f"LLM gateway: call exceeded {hard_limit:.0f}s wall-clock limit "
            f"(litellm timeout={timeout:.0f}s + {_THREAD_DEADLINE_OVERHEAD:.0f}s grace). "
            "SSL read hang suspected — worker thread orphaned, will self-terminate."
        )


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
        response = _call_litellm_bounded(
            litellm, model, messages, api_key, config.endpoint, _timeout
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

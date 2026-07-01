"""
grader_reliability.py — Shared LLM grader reliability layer.

Provides:
  - GraderErrorClass: canonical 16-class error taxonomy
  - classify_exception(): maps any exception to a GraderErrorClass
  - is_retryable(): policy for which classes allow retry
  - get_retry_after(): parse provider Retry-After headers
  - RetryPolicy: configurable timeout/retry/backoff contract
  - call_with_retry(): executes fn with exponential backoff + jitter + deadline
  - GradingEvent / GradingObserver: structured observability (no secrets)

All grader call sites must go through call_with_retry() — do not add
ad-hoc retry loops or bare except Exception catches in individual callers.
"""
from __future__ import annotations

import json
import os
import random
import ssl
import socket
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable


# ---------------------------------------------------------------------------
# 1. Error taxonomy
# ---------------------------------------------------------------------------

class GraderErrorClass(str, Enum):
    DNS_FAILURE = "DNS_FAILURE"
    CONNECT_TIMEOUT = "CONNECT_TIMEOUT"
    TLS_FAILURE = "TLS_FAILURE"
    WRITE_TIMEOUT = "WRITE_TIMEOUT"
    READ_TIMEOUT = "READ_TIMEOUT"
    POOL_TIMEOUT = "POOL_TIMEOUT"
    CONNECTION_RESET = "CONNECTION_RESET"
    RATE_LIMITED = "RATE_LIMITED"
    PROVIDER_5XX = "PROVIDER_5XX"
    AUTHENTICATION_FAILURE = "AUTHENTICATION_FAILURE"
    INVALID_REQUEST = "INVALID_REQUEST"
    CONTEXT_LIMIT = "CONTEXT_LIMIT"
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
    CANCELLED = "CANCELLED"
    LOCAL_STATE_FAILURE = "LOCAL_STATE_FAILURE"
    UNKNOWN_PROVIDER_FAILURE = "UNKNOWN_PROVIDER_FAILURE"


_RETRYABLE: frozenset[GraderErrorClass] = frozenset({
    GraderErrorClass.READ_TIMEOUT,
    GraderErrorClass.CONNECT_TIMEOUT,
    GraderErrorClass.WRITE_TIMEOUT,
    GraderErrorClass.PROVIDER_5XX,
    GraderErrorClass.CONNECTION_RESET,
    GraderErrorClass.POOL_TIMEOUT,
    GraderErrorClass.UNKNOWN_PROVIDER_FAILURE,
    GraderErrorClass.DNS_FAILURE,
    GraderErrorClass.RATE_LIMITED,   # retry with Retry-After backoff
})

_NON_RETRYABLE: frozenset[GraderErrorClass] = frozenset({
    GraderErrorClass.AUTHENTICATION_FAILURE,
    GraderErrorClass.INVALID_REQUEST,
    GraderErrorClass.CONTEXT_LIMIT,
    GraderErrorClass.TLS_FAILURE,
    GraderErrorClass.CANCELLED,
    GraderErrorClass.LOCAL_STATE_FAILURE,
    GraderErrorClass.MALFORMED_RESPONSE,
})


def is_retryable(cls: GraderErrorClass) -> bool:
    """Return True if this error class is eligible for retry."""
    return cls in _RETRYABLE


# ---------------------------------------------------------------------------
# 2. Exception classifier
# ---------------------------------------------------------------------------

def classify_exception(exc: BaseException) -> GraderErrorClass:
    """Map any exception to the canonical GraderErrorClass.

    Inspects exception type hierarchy and message; never evaluates secrets.
    Falls back to UNKNOWN_PROVIDER_FAILURE for unmapped types.
    """
    exc_type = type(exc).__name__
    exc_msg = str(exc).lower()

    # --- Cancellation ---
    if isinstance(exc, (KeyboardInterrupt, SystemExit)):
        return GraderErrorClass.CANCELLED
    if "cancel" in exc_msg:
        return GraderErrorClass.CANCELLED

    # --- SSL / TLS ---
    if isinstance(exc, ssl.SSLError):
        return GraderErrorClass.TLS_FAILURE
    if "ssl" in exc_msg and ("cert" in exc_msg or "handshake" in exc_msg or "verify" in exc_msg):
        return GraderErrorClass.TLS_FAILURE

    # --- httpx errors (openai SDK uses httpx internally) ---
    # We inspect by class name to avoid hard dependency on httpx at import time.
    if exc_type in ("ReadTimeout", "PoolTimeout"):
        if exc_type == "PoolTimeout":
            return GraderErrorClass.POOL_TIMEOUT
        return GraderErrorClass.READ_TIMEOUT
    if exc_type == "ConnectTimeout":
        return GraderErrorClass.CONNECT_TIMEOUT
    if exc_type == "WriteTimeout":
        return GraderErrorClass.WRITE_TIMEOUT
    if exc_type in ("RemoteProtocolError", "RemoteDisconnected"):
        return GraderErrorClass.CONNECTION_RESET
    if exc_type == "ConnectError":
        if "name or service not known" in exc_msg or "nodename" in exc_msg or "dns" in exc_msg:
            return GraderErrorClass.DNS_FAILURE
        return GraderErrorClass.CONNECT_TIMEOUT

    # --- openai SDK typed errors ---
    if exc_type == "AuthenticationError":
        return GraderErrorClass.AUTHENTICATION_FAILURE
    if exc_type == "RateLimitError":
        return GraderErrorClass.RATE_LIMITED
    if exc_type in ("BadRequestError", "UnprocessableEntityError"):
        if "context" in exc_msg and ("limit" in exc_msg or "length" in exc_msg or "token" in exc_msg):
            return GraderErrorClass.CONTEXT_LIMIT
        return GraderErrorClass.INVALID_REQUEST
    if exc_type == "APIStatusError":
        # Extract status code from message or attributes
        status = getattr(exc, "status_code", None)
        if status is None:
            # Try parsing from message "Error code: 429"
            for tok in exc_msg.split():
                if tok.isdigit():
                    status = int(tok)
                    break
        if status == 429:
            return GraderErrorClass.RATE_LIMITED
        if status == 401 or status == 403:
            return GraderErrorClass.AUTHENTICATION_FAILURE
        if status is not None and 400 <= status < 500:
            return GraderErrorClass.INVALID_REQUEST
        if status is not None and 500 <= status < 600:
            return GraderErrorClass.PROVIDER_5XX
        return GraderErrorClass.UNKNOWN_PROVIDER_FAILURE
    if exc_type == "APIConnectionError":
        if "timeout" in exc_msg:
            return GraderErrorClass.READ_TIMEOUT
        return GraderErrorClass.CONNECT_TIMEOUT

    # --- urllib / socket errors ---
    if exc_type == "URLError":
        reason = str(getattr(exc, "reason", exc_msg)).lower()
        if "timed out" in reason or "timeout" in reason:
            return GraderErrorClass.READ_TIMEOUT
        if "name or service not known" in reason or "nodename" in reason:
            return GraderErrorClass.DNS_FAILURE
        if "connection refused" in reason or "connection reset" in reason:
            return GraderErrorClass.CONNECTION_RESET
        if "ssl" in reason:
            return GraderErrorClass.TLS_FAILURE
        return GraderErrorClass.CONNECT_TIMEOUT
    if exc_type in ("timeout", "TimeoutError") or isinstance(exc, (socket.timeout, TimeoutError)):
        return GraderErrorClass.READ_TIMEOUT
    if exc_type in ("ConnectionResetError", "BrokenPipeError"):
        return GraderErrorClass.CONNECTION_RESET
    if exc_type == "ConnectionRefusedError":
        return GraderErrorClass.CONNECT_TIMEOUT
    if exc_type == "gaierror":  # socket.gaierror (DNS)
        return GraderErrorClass.DNS_FAILURE

    # --- HTTP status codes embedded in generic exceptions ---
    if "429" in exc_msg or "rate limit" in exc_msg or "too many requests" in exc_msg:
        return GraderErrorClass.RATE_LIMITED
    if "401" in exc_msg or "403" in exc_msg or "unauthorized" in exc_msg or "forbidden" in exc_msg:
        return GraderErrorClass.AUTHENTICATION_FAILURE
    if "500" in exc_msg or "502" in exc_msg or "503" in exc_msg or "504" in exc_msg:
        return GraderErrorClass.PROVIDER_5XX
    if "context" in exc_msg and "length" in exc_msg:
        return GraderErrorClass.CONTEXT_LIMIT
    if "json" in exc_msg or "parse" in exc_msg or "decode" in exc_msg:
        return GraderErrorClass.MALFORMED_RESPONSE
    if "timeout" in exc_msg or "timed out" in exc_msg:
        return GraderErrorClass.READ_TIMEOUT

    # --- litellm wrapped exceptions ---
    if "litellm" in exc_type.lower() or "litellm" in exc_msg:
        if "timeout" in exc_msg:
            return GraderErrorClass.READ_TIMEOUT
        if "rate" in exc_msg or "429" in exc_msg:
            return GraderErrorClass.RATE_LIMITED
        if "auth" in exc_msg or "401" in exc_msg:
            return GraderErrorClass.AUTHENTICATION_FAILURE
        return GraderErrorClass.UNKNOWN_PROVIDER_FAILURE

    return GraderErrorClass.UNKNOWN_PROVIDER_FAILURE


def get_retry_after(exc: BaseException) -> float | None:
    """Extract Retry-After delay (seconds) from a 429 exception, if present.

    Returns None if no Retry-After header is found or parseable.
    """
    # openai RateLimitError may carry response headers
    for attr in ("response", "headers"):
        obj = getattr(exc, attr, None)
        if obj is None:
            continue
        # headers dict-like
        headers = getattr(obj, "headers", obj) if attr == "response" else obj
        if hasattr(headers, "get"):
            val = headers.get("retry-after") or headers.get("Retry-After")
            if val is not None:
                try:
                    return float(val)
                except (ValueError, TypeError):
                    pass
    # Try parsing from exception message "retry after N seconds"
    msg = str(exc).lower()
    for marker in ("retry after ", "retry-after: ", "retry_after="):
        idx = msg.find(marker)
        if idx >= 0:
            tail = msg[idx + len(marker):].split()[0].rstrip("s,.")
            try:
                return float(tail)
            except (ValueError, TypeError):
                pass
    return None


# ---------------------------------------------------------------------------
# 3. Retry policy
# ---------------------------------------------------------------------------

@dataclass
class RetryPolicy:
    """Configurable timeout and retry contract for a single grader call."""
    max_attempts: int = 3
    base_backoff: float = 2.0       # seconds; delay = base^attempt + jitter
    jitter: bool = True             # adds random(0, base^attempt) to sleep
    overall_deadline: float = 95.0  # wall-clock cap across all attempts
    connect_timeout: float = 10.0   # per-attempt connect timeout (passed to client)
    read_timeout: float = 30.0      # per-attempt read timeout (passed to client)

    def backoff_for(self, attempt: int, retry_after: float | None = None) -> float:
        """Compute sleep duration before the next attempt.

        attempt is 0-indexed (0 = after 1st failure).
        Respects provider's Retry-After if provided.
        """
        if retry_after is not None:
            return min(retry_after, self.overall_deadline)
        delay = self.base_backoff ** (attempt + 1)
        if self.jitter:
            delay += random.uniform(0, self.base_backoff ** attempt)
        return delay


# ---------------------------------------------------------------------------
# 4. Observability
# ---------------------------------------------------------------------------

@dataclass
class GradingEvent:
    request_id: str
    item_id: str
    attempt: int
    phase: str              # "attempt" | "success" | "retry" | "exhausted" | "permanent_fail"
    error_class: str | None
    duration_ms: int
    retrying: bool
    final_status: str | None   # None until terminal; "SUCCEEDED" | "FAILED_TRANSIENT_EXHAUSTED" | "FAILED_PERMANENT"
    provider: str = ""
    model: str = ""


_DEFAULT_LOG_DIR = Path(__file__).resolve().parent.parent.parent / ".local" / "llm-call-logs"


class GradingObserver:
    """Writes structured GradingEvent JSON lines. Never logs secrets."""

    def __init__(self, log_dir: Path | None = None) -> None:
        self._log_dir = log_dir or _DEFAULT_LOG_DIR
        self._log_path = self._log_dir / "grader-events.jsonl"
        self._enabled = True

    def record(self, event: GradingEvent) -> None:
        """Append a single GradingEvent as a JSON line. Non-fatal on error."""
        if not self._enabled:
            return
        try:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": event.request_id,
                "item_id": event.item_id,
                "attempt": event.attempt,
                "phase": event.phase,
                "error_class": event.error_class,
                "duration_ms": event.duration_ms,
                "retrying": event.retrying,
                "final_status": event.final_status,
                "provider": event.provider,
                "model": event.model,
            }
            with self._log_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record) + "\n")
        except Exception:
            pass  # observability must never block grading


# Module-level default observer (used when callers don't provide one)
_default_observer: GradingObserver | None = None


def _get_default_observer() -> GradingObserver:
    global _default_observer
    if _default_observer is None:
        _default_observer = GradingObserver()
    return _default_observer


# ---------------------------------------------------------------------------
# 5. call_with_retry()
# ---------------------------------------------------------------------------

class GraderRetryExhausted(Exception):
    """Raised when all retry attempts are exhausted (transient errors only)."""
    def __init__(self, error_class: GraderErrorClass, last_exc: BaseException) -> None:
        self.error_class = error_class
        self.last_exc = last_exc
        super().__init__(f"Grader retries exhausted after {error_class}")


class GraderPermanentFailure(Exception):
    """Raised immediately for non-retryable error classes."""
    def __init__(self, error_class: GraderErrorClass, exc: BaseException) -> None:
        self.error_class = error_class
        self.exc = exc
        super().__init__(f"Grader permanent failure: {error_class}")


def call_with_retry(
    fn: Callable[[], Any],
    policy: RetryPolicy | None = None,
    observer: GradingObserver | None = None,
    item_id: str = "",
    request_id: str | None = None,
    provider: str = "",
    model: str = "",
) -> Any:
    """Execute fn() with exponential backoff + jitter, deadline awareness, and observability.

    Args:
        fn: Zero-argument callable that performs the LLM call. Must raise on failure.
        policy: RetryPolicy (uses defaults if None).
        observer: GradingObserver for structured logging (uses default if None).
        item_id: Grading item identifier for logging.
        request_id: Stable ID for this grading request (generated if None).
        provider: Provider name for logging only.
        model: Model name for logging only.

    Returns:
        Whatever fn() returns on success.

    Raises:
        GraderPermanentFailure: on non-retryable error (auth, bad request, etc.)
        GraderRetryExhausted: when all retry attempts exhausted for transient errors.

    Callers should catch both and fall back to intermediate verification or deferred grading.
    """
    if policy is None:
        policy = RetryPolicy()
    if observer is None:
        observer = _get_default_observer()
    if request_id is None:
        request_id = str(uuid.uuid4())[:16]

    deadline = time.monotonic() + policy.overall_deadline
    last_exc: BaseException = RuntimeError("no attempt made")
    last_cls = GraderErrorClass.UNKNOWN_PROVIDER_FAILURE

    for attempt in range(policy.max_attempts):
        t0 = time.monotonic()
        try:
            result = fn()
            duration_ms = int((time.monotonic() - t0) * 1000)
            observer.record(GradingEvent(
                request_id=request_id,
                item_id=item_id,
                attempt=attempt,
                phase="success",
                error_class=None,
                duration_ms=duration_ms,
                retrying=False,
                final_status="SUCCEEDED",
                provider=provider,
                model=model,
            ))
            return result

        except (KeyboardInterrupt, SystemExit) as exc:
            duration_ms = int((time.monotonic() - t0) * 1000)
            observer.record(GradingEvent(
                request_id=request_id, item_id=item_id, attempt=attempt,
                phase="permanent_fail", error_class=GraderErrorClass.CANCELLED,
                duration_ms=duration_ms, retrying=False,
                final_status="FAILED_PERMANENT", provider=provider, model=model,
            ))
            raise GraderPermanentFailure(GraderErrorClass.CANCELLED, exc) from exc

        except Exception as exc:
            duration_ms = int((time.monotonic() - t0) * 1000)
            cls = classify_exception(exc)
            last_exc = exc
            last_cls = cls

            if not is_retryable(cls):
                observer.record(GradingEvent(
                    request_id=request_id, item_id=item_id, attempt=attempt,
                    phase="permanent_fail", error_class=cls.value,
                    duration_ms=duration_ms, retrying=False,
                    final_status="FAILED_PERMANENT", provider=provider, model=model,
                ))
                raise GraderPermanentFailure(cls, exc) from exc

            is_last = (attempt == policy.max_attempts - 1)
            remaining = deadline - time.monotonic()

            if is_last or remaining <= 0:
                observer.record(GradingEvent(
                    request_id=request_id, item_id=item_id, attempt=attempt,
                    phase="exhausted", error_class=cls.value,
                    duration_ms=duration_ms, retrying=False,
                    final_status="FAILED_TRANSIENT_EXHAUSTED", provider=provider, model=model,
                ))
                raise GraderRetryExhausted(cls, exc) from exc

            # Compute sleep, capped to remaining deadline
            retry_after = get_retry_after(exc)
            sleep_s = min(policy.backoff_for(attempt, retry_after), remaining)

            observer.record(GradingEvent(
                request_id=request_id, item_id=item_id, attempt=attempt,
                phase="retry", error_class=cls.value,
                duration_ms=duration_ms, retrying=True,
                final_status=None, provider=provider, model=model,
            ))
            time.sleep(sleep_s)

    # Should not reach here — loop always raises on last attempt
    raise GraderRetryExhausted(last_cls, last_exc)

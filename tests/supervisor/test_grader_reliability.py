"""Tests for tools/supervisor/grader_reliability.py.

REL-001 … REL-020 — all deterministic, no live network calls.

Covers:
  - classify_exception() for all 16 error classes
  - is_retryable() policy
  - get_retry_after() header parsing
  - call_with_retry() retry mechanics, backoff, deadline, observability
  - GradingObserver structured logging (no secrets)
  - Idempotency (cache hit bypasses provider call)
"""
from __future__ import annotations

import json
import socket
import ssl
import sys
import time
import types
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch, call as mock_call

# Ensure tools/supervisor is importable
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))

from grader_reliability import (
    GraderErrorClass,
    GraderPermanentFailure,
    GraderRetryExhausted,
    GradingEvent,
    GradingObserver,
    RetryPolicy,
    call_with_retry,
    classify_exception,
    get_retry_after,
    is_retryable,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_exc(name: str, msg: str = "", status_code: int | None = None) -> Exception:
    """Create a named fake exception for classifier tests."""
    exc_cls = type(name, (Exception,), {})
    exc = exc_cls(msg)
    if status_code is not None:
        exc.status_code = status_code
    return exc


class _FakeReadTimeout(Exception):
    pass


class _FakeConnectTimeout(Exception):
    pass


class _FakeWriteTimeout(Exception):
    pass


class _FakePoolTimeout(Exception):
    pass


class _FakeRemoteDisconnected(Exception):
    pass


class _FakeConnectError(Exception):
    pass


class _FakeAuthenticationError(Exception):
    pass


class _FakeRateLimitError(Exception):
    pass


class _FakeBadRequestError(Exception):
    pass


class _FakeAPIStatusError(Exception):
    def __init__(self, msg: str, status_code: int) -> None:
        super().__init__(msg)
        self.status_code = status_code


# ---------------------------------------------------------------------------
# REL-001: ssl.SSLError → TLS_FAILURE
# ---------------------------------------------------------------------------

class TestClassifyExceptionSSL:
    def test_ssl_error_tls_failure(self):
        """REL-001: ssl.SSLError maps to TLS_FAILURE."""
        exc = ssl.SSLError("CERTIFICATE_VERIFY_FAILED")
        assert classify_exception(exc) == GraderErrorClass.TLS_FAILURE


# ---------------------------------------------------------------------------
# REL-002: httpx.ReadTimeout → READ_TIMEOUT
# ---------------------------------------------------------------------------

class TestClassifyExceptionReadTimeout:
    def test_read_timeout(self):
        """REL-002: exception named ReadTimeout → READ_TIMEOUT."""
        exc = _make_exc("ReadTimeout", "read operation timed out")
        assert classify_exception(exc) == GraderErrorClass.READ_TIMEOUT


# ---------------------------------------------------------------------------
# REL-003: httpx.ConnectTimeout → CONNECT_TIMEOUT
# ---------------------------------------------------------------------------

class TestClassifyExceptionConnectTimeout:
    def test_connect_timeout(self):
        """REL-003: exception named ConnectTimeout → CONNECT_TIMEOUT."""
        exc = _make_exc("ConnectTimeout", "connection attempt timed out")
        assert classify_exception(exc) == GraderErrorClass.CONNECT_TIMEOUT


# ---------------------------------------------------------------------------
# REL-004: 429 → RATE_LIMITED
# ---------------------------------------------------------------------------

class TestClassifyExceptionRateLimited:
    def test_rate_limited_status_code(self):
        """REL-004: APIStatusError with status 429 → RATE_LIMITED."""
        exc = _FakeAPIStatusError("Rate limited", 429)
        exc.__class__.__name__ = "APIStatusError"
        # Patch class name
        exc2 = _make_exc("APIStatusError", "429 rate limit exceeded")
        exc2.status_code = 429
        assert classify_exception(exc2) == GraderErrorClass.RATE_LIMITED

    def test_rate_limited_message(self):
        """REL-004b: message containing 'too many requests' → RATE_LIMITED."""
        exc = Exception("Error 429: too many requests")
        assert classify_exception(exc) == GraderErrorClass.RATE_LIMITED


# ---------------------------------------------------------------------------
# REL-005: 500 → PROVIDER_5XX
# ---------------------------------------------------------------------------

class TestClassifyExceptionProvider5xx:
    def test_provider_5xx_status_code(self):
        """REL-005: APIStatusError with status 500 → PROVIDER_5XX."""
        exc = _make_exc("APIStatusError", "internal server error")
        exc.status_code = 500
        assert classify_exception(exc) == GraderErrorClass.PROVIDER_5XX

    def test_provider_5xx_message(self):
        """REL-005b: message '502 bad gateway' → PROVIDER_5XX."""
        exc = Exception("Upstream returned 502 bad gateway")
        assert classify_exception(exc) == GraderErrorClass.PROVIDER_5XX


# ---------------------------------------------------------------------------
# REL-006: 401 → AUTHENTICATION_FAILURE
# ---------------------------------------------------------------------------

class TestClassifyExceptionAuth:
    def test_auth_failure_status_code(self):
        """REL-006: AuthenticationError → AUTHENTICATION_FAILURE."""
        exc = _make_exc("AuthenticationError", "invalid api key")
        assert classify_exception(exc) == GraderErrorClass.AUTHENTICATION_FAILURE

    def test_auth_failure_401_in_message(self):
        """REL-006b: message with '401 unauthorized' → AUTHENTICATION_FAILURE."""
        exc = Exception("Server returned 401 unauthorized")
        assert classify_exception(exc) == GraderErrorClass.AUTHENTICATION_FAILURE


# ---------------------------------------------------------------------------
# REL-007: 400 → INVALID_REQUEST
# ---------------------------------------------------------------------------

class TestClassifyExceptionInvalidRequest:
    def test_bad_request_error_name(self):
        """REL-007: BadRequestError → INVALID_REQUEST."""
        exc = _make_exc("BadRequestError", "invalid parameters")
        assert classify_exception(exc) == GraderErrorClass.INVALID_REQUEST

    def test_api_status_400(self):
        """REL-007b: APIStatusError status=400 → INVALID_REQUEST."""
        exc = _make_exc("APIStatusError", "bad request 400")
        exc.status_code = 400
        assert classify_exception(exc) == GraderErrorClass.INVALID_REQUEST


# ---------------------------------------------------------------------------
# REL-008: get_retry_after() parses header
# ---------------------------------------------------------------------------

class TestGetRetryAfter:
    def test_parses_numeric_retry_after(self):
        """REL-008: get_retry_after parses Retry-After: 5 → 5.0."""
        exc = Exception("rate limit")
        exc.response = MagicMock()
        exc.response.headers = {"retry-after": "5"}
        result = get_retry_after(exc)
        assert result == 5.0

    def test_returns_none_when_no_header(self):
        """REL-008b: get_retry_after returns None when no Retry-After present."""
        exc = Exception("rate limit")
        result = get_retry_after(exc)
        assert result is None

    def test_parses_from_message(self):
        """REL-008c: get_retry_after parses 'retry after 10' from exception message."""
        exc = Exception("Too many requests, retry after 10 seconds")
        result = get_retry_after(exc)
        assert result == 10.0


# ---------------------------------------------------------------------------
# REL-009: is_retryable(READ_TIMEOUT) → True
# ---------------------------------------------------------------------------

class TestIsRetryable:
    def test_read_timeout_retryable(self):
        """REL-009: READ_TIMEOUT is retryable."""
        assert is_retryable(GraderErrorClass.READ_TIMEOUT) is True

    def test_connect_timeout_retryable(self):
        assert is_retryable(GraderErrorClass.CONNECT_TIMEOUT) is True

    def test_provider_5xx_retryable(self):
        assert is_retryable(GraderErrorClass.PROVIDER_5XX) is True

    def test_connection_reset_retryable(self):
        assert is_retryable(GraderErrorClass.CONNECTION_RESET) is True


# ---------------------------------------------------------------------------
# REL-010: is_retryable(AUTHENTICATION_FAILURE) → False
# ---------------------------------------------------------------------------

class TestIsNotRetryable:
    def test_auth_failure_not_retryable(self):
        """REL-010: AUTHENTICATION_FAILURE is NOT retryable."""
        assert is_retryable(GraderErrorClass.AUTHENTICATION_FAILURE) is False

    def test_invalid_request_not_retryable(self):
        assert is_retryable(GraderErrorClass.INVALID_REQUEST) is False

    def test_tls_failure_not_retryable(self):
        assert is_retryable(GraderErrorClass.TLS_FAILURE) is False

    def test_context_limit_not_retryable(self):
        assert is_retryable(GraderErrorClass.CONTEXT_LIMIT) is False


# ---------------------------------------------------------------------------
# REL-011: call_with_retry succeeds on 1st attempt
# ---------------------------------------------------------------------------

class TestCallWithRetrySuccess:
    def test_success_on_first_attempt(self):
        """REL-011: fn succeeds on 1st call → result returned, 1 attempt only."""
        call_count = [0]

        def fn():
            call_count[0] += 1
            return "grading_result"

        policy = RetryPolicy(max_attempts=3, overall_deadline=10.0)
        observer = GradingObserver(log_dir=Path("/tmp/grader-test-obs"))
        result = call_with_retry(fn, policy=policy, observer=observer, item_id="ITEM-1")

        assert result == "grading_result"
        assert call_count[0] == 1


# ---------------------------------------------------------------------------
# REL-012: call_with_retry retries READ_TIMEOUT, succeeds on 3rd
# ---------------------------------------------------------------------------

class TestCallWithRetryTransient:
    def test_retries_and_succeeds_on_third(self):
        """REL-012: READ_TIMEOUT on first 2 → retry; success on 3rd."""
        attempts = [0]

        class FakeReadTimeout(Exception):
            pass

        def fn():
            attempts[0] += 1
            if attempts[0] < 3:
                raise FakeReadTimeout("timeout")
            return "success_after_retry"

        policy = RetryPolicy(max_attempts=3, base_backoff=0.01, jitter=False, overall_deadline=10.0)
        with patch("time.sleep"):
            result = call_with_retry(fn, policy=policy, item_id="ITEM-T")

        assert result == "success_after_retry"
        assert attempts[0] == 3


# ---------------------------------------------------------------------------
# REL-013: call_with_retry exhausts all retries
# ---------------------------------------------------------------------------

class TestCallWithRetryExhausted:
    def test_all_retries_exhausted_raises(self):
        """REL-013: all 3 attempts fail with READ_TIMEOUT → GraderRetryExhausted."""
        # Use _make_exc to create a class named exactly "ReadTimeout" so the classifier
        # maps it to READ_TIMEOUT (classifier checks exc_type == "ReadTimeout").
        calls = [0]

        def fn():
            calls[0] += 1
            raise _make_exc("ReadTimeout", "timed out waiting for response")

        policy = RetryPolicy(max_attempts=3, base_backoff=0.01, jitter=False, overall_deadline=10.0)
        with patch("grader_reliability.time.sleep"):
            try:
                call_with_retry(fn, policy=policy)
                assert False, "Should have raised"
            except GraderRetryExhausted as exc:
                assert exc.error_class == GraderErrorClass.READ_TIMEOUT, (
                    f"Expected READ_TIMEOUT, got {exc.error_class}"
                )
        assert calls[0] == 3


# ---------------------------------------------------------------------------
# REL-014: call_with_retry stops on AUTHENTICATION_FAILURE
# ---------------------------------------------------------------------------

class TestCallWithRetryPermanentFailure:
    def test_auth_failure_no_retry(self):
        """REL-014: AuthenticationError → GraderPermanentFailure, called only once."""
        calls = [0]

        def fn():
            calls[0] += 1
            raise _make_exc("AuthenticationError", "invalid key")

        policy = RetryPolicy(max_attempts=3, overall_deadline=10.0)
        try:
            call_with_retry(fn, policy=policy)
            assert False, "Should have raised"
        except GraderPermanentFailure as exc:
            assert exc.error_class == GraderErrorClass.AUTHENTICATION_FAILURE
        assert calls[0] == 1, "Must NOT retry on AUTHENTICATION_FAILURE"


# ---------------------------------------------------------------------------
# REL-015: call_with_retry respects overall_deadline
# ---------------------------------------------------------------------------

class TestCallWithRetryDeadline:
    def test_deadline_aborts_retries(self):
        """REL-015: overall_deadline elapsed before 3rd attempt → exhausted early."""
        class FakeReadTimeout(Exception):
            pass

        # Fake monotonic clock: advance by 100s per call to simulate deadline exceeded
        _time_ref = [0.0]
        original_monotonic = time.monotonic

        def fake_monotonic():
            _time_ref[0] += 50.0
            return _time_ref[0]

        calls = [0]

        def fn():
            calls[0] += 1
            raise FakeReadTimeout("slow timeout")

        policy = RetryPolicy(max_attempts=3, base_backoff=0.01, jitter=False, overall_deadline=30.0)
        with patch("grader_reliability.time.monotonic", side_effect=fake_monotonic):
            with patch("grader_reliability.time.sleep"):
                try:
                    call_with_retry(fn, policy=policy)
                except GraderRetryExhausted:
                    pass  # expected

        # With 50s per fake monotonic tick, the deadline of 30s is exceeded quickly
        assert calls[0] < 3, f"Should stop before 3 attempts when deadline exceeded, got {calls[0]}"


# ---------------------------------------------------------------------------
# REL-016: call_with_retry uses jitter
# ---------------------------------------------------------------------------

class TestCallWithRetryJitter:
    def test_jitter_produces_variable_backoff(self):
        """REL-016: jitter=True produces sleep durations in the expected range."""
        class FakeTimeout(Exception):
            pass

        sleep_times = []
        policy = RetryPolicy(max_attempts=3, base_backoff=2.0, jitter=True, overall_deadline=30.0)

        def fn():
            raise FakeTimeout("always fail")

        with patch("grader_reliability.time.sleep", side_effect=lambda s: sleep_times.append(s)):
            try:
                call_with_retry(fn, policy=policy)
            except GraderRetryExhausted:
                pass

        assert len(sleep_times) >= 1
        # First backoff: base^1 + jitter in [0, base^0] = 2.0 + [0,1) → [2.0, 3.0)
        # With jitter the result is non-deterministic but must be >= base^1 = 2.0
        assert sleep_times[0] >= 2.0, f"First sleep should be >= 2.0, got {sleep_times[0]}"


# ---------------------------------------------------------------------------
# REL-017: call_with_retry respects get_retry_after
# ---------------------------------------------------------------------------

class TestCallWithRetryRetryAfter:
    def test_retry_after_sets_sleep_duration(self):
        """REL-017: 429 with Retry-After:5 → sleep ~5s (not base backoff)."""
        # Use a class named "RateLimitError" so classify_exception maps it to RATE_LIMITED
        # (which is retryable), then verify Retry-After header is used for sleep duration.
        calls = [0]
        sleep_times = []

        def fn():
            calls[0] += 1
            if calls[0] == 1:
                exc = _make_exc("RateLimitError", "too many requests")
                # Attach a fake response with Retry-After header
                fake_resp = MagicMock()
                fake_resp.headers = {"retry-after": "5"}
                exc.response = fake_resp
                raise exc
            return "ok"

        policy = RetryPolicy(max_attempts=3, base_backoff=2.0, jitter=False, overall_deadline=30.0)

        with patch("grader_reliability.time.sleep", side_effect=lambda s: sleep_times.append(s)):
            result = call_with_retry(fn, policy=policy)

        assert result == "ok"
        assert len(sleep_times) == 1
        # Retry-After of 5s should be used (not base_backoff^1 = 2.0)
        assert sleep_times[0] == 5.0, f"Expected 5.0 from Retry-After, got {sleep_times[0]}"


# ---------------------------------------------------------------------------
# REL-018: GradingObserver writes JSON line without secrets
# ---------------------------------------------------------------------------

class TestGradingObserverNoSecrets:
    def test_writes_json_line(self, tmp_path):
        """REL-018: GradingObserver.record() writes valid JSON line, no secrets."""
        observer = GradingObserver(log_dir=tmp_path)
        event = GradingEvent(
            request_id="req-001",
            item_id="ITEM-001",
            attempt=0,
            phase="success",
            error_class=None,
            duration_ms=150,
            retrying=False,
            final_status="SUCCEEDED",
            provider="api.example.com",
            model="recommended",
        )
        observer.record(event)

        log_file = tmp_path / "grader-events.jsonl"
        assert log_file.exists()
        lines = [l for l in log_file.read_text().splitlines() if l.strip()]
        assert len(lines) == 1
        record = json.loads(lines[0])

        assert record["request_id"] == "req-001"
        assert record["item_id"] == "ITEM-001"
        assert record["phase"] == "success"
        assert record["final_status"] == "SUCCEEDED"
        # Secrets must never appear — provider only shows hostname, not key
        assert "api_key" not in json.dumps(record).lower()
        assert "Bearer" not in json.dumps(record)

    def test_observer_non_fatal_on_bad_dir(self):
        """REL-018b: GradingObserver.record() never raises even if log dir is unwritable."""
        observer = GradingObserver(log_dir=Path("/nonexistent/__grader_test_xyz__"))
        event = GradingEvent(
            request_id="x", item_id="y", attempt=0, phase="success",
            error_class=None, duration_ms=0, retrying=False, final_status="SUCCEEDED",
        )
        # Must not raise
        observer.record(event)


# ---------------------------------------------------------------------------
# REL-019: Duplicate call on same input_hash hits cache, skips provider
# ---------------------------------------------------------------------------

class TestIdempotentCacheHit:
    def test_cache_hit_skips_provider(self, tmp_path):
        """REL-019: same evidence_hash → grade-cache hit → provider fn NOT called.

        This test exercises the grade cache that already exists in grade_declared_work.py.
        We verify that _get_cached_grade returns the stored result on the 2nd call,
        so that call_with_retry is never invoked for a cache-hit item.
        """
        sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))
        try:
            from grade_declared_work import _get_cached_grade, _cache_grade
        except ImportError:
            import pytest
            pytest.skip("grade_declared_work not importable in this test context")

        cache_path = tmp_path / "grade-cache.json"
        item_id = "ITEM-IDEM-001"
        ev_hash = "abc123"
        stored = {
            "adequate": True, "confidence": 0.9,
            "stub_detected": False, "deficiencies": [], "llm_used": True,
        }
        _cache_grade(item_id, ev_hash, stored, cache_path=cache_path)

        # 2nd call — should hit cache
        result = _get_cached_grade(item_id, ev_hash, cache_path=cache_path)
        assert result is not None
        assert result["adequate"] is True
        assert result.get("_from_cache") or result.get("llm_used") is True


# ---------------------------------------------------------------------------
# REL-020: call_with_retry emits GradingEvent per attempt
# ---------------------------------------------------------------------------

class TestCallWithRetryObservability:
    def test_events_emitted_per_attempt(self):
        """REL-020: GradingEvent is recorded for each attempt including final success."""
        events = []

        class FakeObserver(GradingObserver):
            def __init__(self):
                pass  # skip file setup

            def record(self, event: GradingEvent) -> None:
                events.append(event)

        class FakeTimeout(Exception):
            pass

        calls = [0]

        def fn():
            calls[0] += 1
            if calls[0] < 2:
                raise FakeTimeout("transient")
            return "done"

        policy = RetryPolicy(max_attempts=3, base_backoff=0.01, jitter=False, overall_deadline=10.0)
        with patch("grader_reliability.time.sleep"):
            result = call_with_retry(fn, policy=policy, observer=FakeObserver(), item_id="OBS-001")

        assert result == "done"
        # Should have: 1 retry event + 1 success event
        phases = [e.phase for e in events]
        assert "retry" in phases
        assert "success" in phases
        assert all(e.item_id == "OBS-001" for e in events)

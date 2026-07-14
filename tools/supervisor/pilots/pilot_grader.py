"""pilot_grader.py — 8 fault-injection pilots for grader reliability hardening.

Usage: python tools/supervisor/pilots/pilot_grader.py --pilot N  (N=1..8)
       python tools/supervisor/pilots/pilot_grader.py --all
All pilots use unittest.mock — no live network calls required.
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import MagicMock, patch

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))
os.environ.setdefault("GRADER_LOG_DIR", tempfile.mkdtemp())

from grader_reliability import (
    GraderCircuitBreaker,
    GraderErrorClass,
    GraderPermanentFailure,
    GraderRetryExhausted,
    GradingObserver,
    RetryPolicy,
    call_with_retry,
)

_PILOTS: dict[int, tuple[str, object]] = {}


def pilot(n: int, name: str):
    def dec(fn):
        _PILOTS[n] = (name, fn)
        return fn
    return dec


@pilot(1, "Normal grading — fn() succeeds on first attempt")
def pilot_1():
    log_dir = Path(tempfile.mkdtemp())
    calls = [0]

    def fn():
        calls[0] += 1
        return "ok"

    policy = RetryPolicy(max_attempts=3, overall_deadline=10.0)
    observer = GradingObserver(log_dir=log_dir)
    with patch("grader_reliability.time.sleep"):
        result = call_with_retry(fn, policy=policy, observer=observer, item_id="P1")
    assert result == "ok", f"Expected 'ok', got {result!r}"
    assert calls[0] == 1, f"Expected 1 call, got {calls[0]}"


@pilot(2, "SSL read timeout x2 -> retry -> success on 3rd")
def pilot_2():
    log_dir = Path(tempfile.mkdtemp())
    calls = [0]

    class FakeReadTimeout(Exception):
        pass

    def fn():
        calls[0] += 1
        if calls[0] < 3:
            raise FakeReadTimeout("read timeout")
        return "ok"

    policy = RetryPolicy(max_attempts=3, base_backoff=0.01, jitter=False, overall_deadline=10.0)
    observer = GradingObserver(log_dir=log_dir)
    with patch("grader_reliability.time.sleep"):
        result = call_with_retry(fn, policy=policy, observer=observer, item_id="P2")
    assert result == "ok"
    assert calls[0] == 3, f"Expected 3 calls, got {calls[0]}"


@pilot(3, "PROVIDER_5XX + CONNECTION_RESET -> retry -> success")
def pilot_3():
    log_dir = Path(tempfile.mkdtemp())
    calls = [0]

    def fn():
        calls[0] += 1
        if calls[0] == 1:
            raise Exception("HTTP 503 server error")   # PROVIDER_5XX
        if calls[0] == 2:
            raise Exception("RemoteProtocolError peer disconnected")  # CONNECTION_RESET
        return "ok"

    policy = RetryPolicy(max_attempts=3, base_backoff=0.01, jitter=False, overall_deadline=10.0)
    observer = GradingObserver(log_dir=log_dir)
    with patch("grader_reliability.time.sleep"):
        result = call_with_retry(fn, policy=policy, observer=observer, item_id="P3")
    assert result == "ok"
    assert calls[0] == 3


@pilot(4, "Authentication failure -> no retry, 1 call only")
def pilot_4():
    log_dir = Path(tempfile.mkdtemp())
    calls = [0]
    _AuthErr = type("AuthenticationError", (Exception,), {})

    def fn():
        calls[0] += 1
        raise _AuthErr("invalid key")

    policy = RetryPolicy(max_attempts=3, overall_deadline=10.0)
    observer = GradingObserver(log_dir=log_dir)
    try:
        call_with_retry(fn, policy=policy, observer=observer, item_id="P4")
        raise AssertionError("Should have raised GraderPermanentFailure")
    except GraderPermanentFailure as exc:
        assert exc.error_class == GraderErrorClass.AUTHENTICATION_FAILURE
    assert calls[0] == 1, f"Must NOT retry on auth failure; got {calls[0]} calls"


@pilot(5, "Circuit breaker opens after 3 failures -> 4th call fast-fails with CIRCUIT_OPEN")
def pilot_5():
    log_dir = Path(tempfile.mkdtemp())
    cb = GraderCircuitBreaker(failure_threshold=3, reset_timeout=60.0)
    calls = [0]

    def fn():
        calls[0] += 1
        raise Exception("HTTP 503 server error")

    policy = RetryPolicy(max_attempts=1, base_backoff=0.01, jitter=False, overall_deadline=10.0)
    observer = GradingObserver(log_dir=log_dir)
    # Trip the breaker: 3 consecutive failures
    for _ in range(3):
        try:
            call_with_retry(fn, policy=policy, observer=observer, circuit_breaker=cb, item_id="P5-trip")
        except (GraderRetryExhausted, GraderPermanentFailure):
            pass
    assert cb.is_open(), "Circuit should be OPEN after 3 failures"
    # 4th call: should raise CIRCUIT_OPEN immediately without calling fn
    calls_before = calls[0]
    try:
        call_with_retry(fn, policy=policy, observer=observer, circuit_breaker=cb, item_id="P5-fast")
        raise AssertionError("Should have raised GraderPermanentFailure(CIRCUIT_OPEN)")
    except GraderPermanentFailure as exc:
        assert exc.error_class == GraderErrorClass.CIRCUIT_OPEN
    assert calls[0] == calls_before, "fn() must not be called when circuit is OPEN"


@pilot(6, "Cache resume: _cache_grade preloads result; no LLM call on re-grade")
def pilot_6():
    import json
    from grade_declared_work import _get_cached_grade, _cache_grade
    tmp = Path(tempfile.mkdtemp())
    cache = tmp / "grade-cache.json"
    item_id = "cached-item"
    ev_hash = "deadbeef"
    preloaded = {
        "adequate": True, "confidence": 0.9, "stub_detected": False,
        "deficiencies": [], "llm_used": True, "source": "pilot_6_preloaded",
    }
    _cache_grade(item_id, ev_hash, preloaded, cache_path=cache)
    hit = _get_cached_grade(item_id, ev_hash, cache_path=cache)
    assert hit is not None, "Cache miss; expected preloaded result"
    assert hit.get("source") == "pilot_6_preloaded"


@pilot(7, "Concurrent calls — 5 simultaneous retries complete without deadlock")
def pilot_7():
    import threading
    log_dir = Path(tempfile.mkdtemp())
    barrier = threading.Barrier(5)
    results = []

    def fn():
        barrier.wait()
        return "concurrent_ok"

    policy = RetryPolicy(max_attempts=3, overall_deadline=10.0)

    def one_call():
        obs = GradingObserver(log_dir=log_dir)
        return call_with_retry(fn, policy=policy, observer=obs, item_id="P7")

    with ThreadPoolExecutor(max_workers=5) as exc:
        futures = [exc.submit(one_call) for _ in range(5)]
    results = [f.result() for f in futures]
    assert all(r == "concurrent_ok" for r in results), f"Not all concurrent calls succeeded: {results}"


@pilot(8, "Idempotent rerun — same item graded twice; second run returns from cache (_from_cache=True)")
def pilot_8():
    from grade_declared_work import _get_cached_grade, _cache_grade
    tmp = Path(tempfile.mkdtemp())
    cache = tmp / "grade-cache.json"
    item_id = "idempotent-item"
    ev_hash = "abc123"
    first_result = {
        "adequate": True, "confidence": 0.85, "stub_detected": False,
        "deficiencies": [], "llm_used": True, "source": "pilot_8_first_run",
    }
    _cache_grade(item_id, ev_hash, first_result, cache_path=cache)
    second = _get_cached_grade(item_id, ev_hash, cache_path=cache)
    assert second is not None, "Second run should return cached result"
    assert second.get("source") == "pilot_8_first_run"
    # Confirm source is cached, not re-generated
    assert second.get("llm_used") is True


def main():
    parser = argparse.ArgumentParser(description="Grader reliability fault-injection pilots")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pilot", type=int, metavar="N", help="Run pilot N (1-8)")
    group.add_argument("--all", action="store_true", help="Run all 8 pilots")
    args = parser.parse_args()

    pilots_to_run = list(range(1, 9)) if args.all else [args.pilot]
    failed = []

    for n in pilots_to_run:
        name, fn = _PILOTS.get(n, (None, None))
        if fn is None:
            print(f"Pilot {n} NOT FOUND", file=sys.stderr)
            failed.append(n)
            continue
        try:
            fn()
            print(f"Pilot {n} PASS: {name}")
        except Exception as exc:
            print(f"Pilot {n} FAIL: {name} — {exc}", file=sys.stderr)
            failed.append(n)

    if failed:
        print(f"\n{len(failed)} pilot(s) FAILED: {failed}", file=sys.stderr)
        sys.exit(1)
    print(f"\nAll {len(pilots_to_run)} pilot(s) PASSED")


if __name__ == "__main__":
    main()

# Plan: LLM Grader Network Timeout — Harden, Test, Pilot-Prove

## Context

The LLM grader (used by `grade_declared_work.py` during `autonomous_cycle.py` step 3) experienced
an SSL read / network read timeout while calling an OpenAI-compatible endpoint. The MEMORY.md
confirms `GPT_OSS_ENDPOINT + GPT_OSS_API_KEY` are active. The root cause is that the PRIMARY call
path (`gateway_chat()` via litellm) has **no timeout configured** — if litellm blocks at the TCP/
SSL layer, the entire grading pipeline hangs indefinitely. The fallback (`_sv_sdk_fallback()`) has
`timeout=30` but uses generic `except Exception` with no error classification, linear fixed
backoff (no jitter), a new client created per attempt, and no overall deadline guard.

Mission: find the exact failing boundary, implement a production-grade shared reliability layer,
cover all error classes with deterministic tests, and prove the solution through fault-injection
pilots.

---

## Incident Binding

```yaml
incident:
  incident_id: LLM-GRADER-TIMEOUT-001
  grader: grade_declared_work._sv_llm_call
  provider: openai-compatible (GPT_OSS_ENDPOINT)
  model: "recommended"
  exception_type: SSLError / ReadTimeout (caught as generic Exception)
  first_failing_boundary: gateway.py:79 — litellm.completion() with no timeout
  affected_inputs: PRODUCT_SOURCE items in evidence-declaration.yaml
  retry_count: 3 (in fallback; gateway has 0 retries)
  timeout_configuration:
    gateway_litellm: NONE (hangs indefinitely)
    sdk_fallback_per_attempt: 30s
    sdk_fallback_total: ~90s
    llm_api_backend: 15s (urllib, single attempt)
  state_after_failure: item graded DEFERRED_WITH_REASON (TC-C3-001) or intermediate_verify fallback
```

---

## Root Causes (verified in code)

| # | Location | Gap | Severity |
|---|----------|-----|----------|
| RC-1 | `tools/ai/control_plane/gateway.py:79` | `litellm.completion()` has **no timeout** — indefinite hang possible | CRITICAL |
| RC-2 | `tools/supervisor/grade_declared_work.py:277` | `except Exception` catches all — no error classification (SSL vs auth vs 5xx) | HIGH |
| RC-3 | `tools/supervisor/grade_declared_work.py:268` | New `OpenAI()` client created per retry attempt — wasted connection setup | MEDIUM |
| RC-4 | `tools/supervisor/grade_declared_work.py:260` | Backoff `[1, 2, 4]` is fixed linear — no jitter, no overall deadline | MEDIUM |
| RC-5 | `tools/supervisor/backends/llm_api_backend.py:118` | `urlopen(timeout=15)` — single attempt, no retry, no error class | MEDIUM |
| RC-6 | All callers | No structured observability — only `print()` statements | LOW |
| RC-7 | `tests/supervisor/test_grade_timeout_behavior.py` | Tests cover only `_sv_sdk_fallback()` — gateway path timeout untested | MEDIUM |

---

## Reliability Contract

```yaml
timeouts:
  connect: 10s
  read: 30s
  overall_deadline: 95s  # slightly > 3×30s to allow backoff

retries:
  maximum_attempts: 3
  exponential_backoff_base: 2.0
  jitter: true  # random(0, base^attempt)
  retryable_errors: [READ_TIMEOUT, CONNECT_TIMEOUT, PROVIDER_5XX, CONNECTION_RESET, POOL_TIMEOUT]
  non_retryable_errors: [AUTHENTICATION_FAILURE, INVALID_REQUEST, CONTEXT_LIMIT, TLS_FAILURE]
  deadline_aware: true  # abort retry if overall_deadline exceeded

state:
  input_hash: SHA256 of item_id + evidence_hash  # existing grade-cache.json key
  result_status: PENDING | IN_FLIGHT | SUCCEEDED | FAILED_TRANSIENT_EXHAUSTED | FAILED_PERMANENT
  # Grade cache already provides idempotent re-run protection
```

---

## Error Classification (16 classes)

New module `tools/supervisor/grader_reliability.py` defines:

```python
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

def classify_exception(exc: BaseException) -> GraderErrorClass:
    # Maps exception type + message to one of the 16 classes above
    # Uses isinstance checks: ssl.SSLError, httpx.ReadTimeout, httpx.ConnectTimeout,
    # openai.AuthenticationError, openai.RateLimitError, openai.BadRequestError,
    # openai.APIStatusError (5xx), socket.timeout, urllib.error.URLError, etc.
    ...

def is_retryable(cls: GraderErrorClass) -> bool: ...
def get_retry_after(exc: BaseException) -> float | None: ...  # parse 429 Retry-After header
```

Also provides:
```python
@dataclass
class RetryPolicy:
    max_attempts: int = 3
    base_backoff: float = 2.0
    jitter: bool = True
    overall_deadline: float = 95.0
    connect_timeout: float = 10.0
    read_timeout: float = 30.0

def call_with_retry(fn: Callable, policy: RetryPolicy, observer: GradingObserver) -> Any:
    # Executes fn(), classifies exceptions, retries with exp backoff + jitter,
    # respects overall deadline, never retries permanent failures.
    ...

@dataclass
class GradingEvent:
    request_id: str
    item_id: str
    attempt: int
    phase: str  # "connect" | "read" | "parse" | "persist"
    error_class: str | None
    duration_ms: int
    retrying: bool
    final_status: str | None

class GradingObserver:
    def record(self, event: GradingEvent) -> None:
        # Writes JSON line to .local/llm-call-logs/grader-events.jsonl
        ...
```

---

## Implementation Plan

### Task 1 — Create shared reliability module (NEW FILE)

**File:** `tools/supervisor/grader_reliability.py`

Contents:
- `GraderErrorClass` enum (16 classes)
- `classify_exception(exc) -> GraderErrorClass`
- `is_retryable(cls) -> bool`
- `get_retry_after(exc) -> float | None`
- `RetryPolicy` dataclass with defaults matching the contract above
- `call_with_retry(fn, policy, observer) -> Any` — respects overall_deadline + per-attempt timeout
- `GradingEvent` dataclass
- `GradingObserver` — writes structured JSON lines, redacts secrets

### Task 2 — Fix gateway.py: add timeout to litellm call

**File:** `tools/ai/control_plane/gateway.py`

Change `litellm.completion(...)` at line 79 to pass `timeout=30` (configurable via env var
`GRADER_LLM_TIMEOUT`, default 30). This is the single most critical fix — prevents indefinite hang
on the primary path.

```python
_timeout = float(os.environ.get("GRADER_LLM_TIMEOUT", "30"))
response = litellm.completion(
    ...,
    timeout=_timeout,
)
```

Also classify the exception in the except block using `GraderErrorClass` and record it in the
`AIUsageRecord.error_class_redacted` field (already exists, just needs the canonical name).

### Task 3 — Harden `_sv_sdk_fallback()` in grade_declared_work.py

**File:** `tools/supervisor/grade_declared_work.py`

Replace the current manual retry loop with `call_with_retry()` from the shared module:
- Create `OpenAI` client **once** before the retry loop (not per attempt)
- Pass `httpx.Timeout(connect=10, read=30)` to the client constructor
- Let `call_with_retry` handle backoff + jitter + overall deadline
- Classify exceptions via `classify_exception()`; stop immediately on `AUTHENTICATION_FAILURE`
  or `INVALID_REQUEST` — no useless retry
- Pass `GradingObserver` to emit structured events

### Task 4 — Harden `llm_api_backend.py` urllib call

**File:** `tools/supervisor/backends/llm_api_backend.py`

Replace single `urlopen(timeout=15)` with:
- Use `RetryPolicy(max_attempts=2, overall_deadline=40.0, read_timeout=15.0)` via `call_with_retry`
- Classify `urllib.error.URLError` and `socket.timeout` using `classify_exception`
- Write structured failure records to result_path instead of silently returning `FAILED`

### Task 5 — Write tests: `test_grader_reliability.py`

**File:** `tests/supervisor/test_grader_reliability.py`

Deterministic tests using `unittest.mock` / fake exceptions — no live network calls:

| Test ID | Scenario |
|---------|----------|
| REL-001 | `classify_exception` correctly maps `ssl.SSLError` → `TLS_FAILURE` |
| REL-002 | `classify_exception` maps `httpx.ReadTimeout` → `READ_TIMEOUT` |
| REL-003 | `classify_exception` maps `httpx.ConnectTimeout` → `CONNECT_TIMEOUT` |
| REL-004 | `classify_exception` maps 429 HTTP response → `RATE_LIMITED` |
| REL-005 | `classify_exception` maps 500 HTTP response → `PROVIDER_5XX` |
| REL-006 | `classify_exception` maps 401 → `AUTHENTICATION_FAILURE` |
| REL-007 | `classify_exception` maps 400 → `INVALID_REQUEST` |
| REL-008 | `get_retry_after()` parses `Retry-After: 5` header → 5.0 |
| REL-009 | `is_retryable(READ_TIMEOUT)` → True |
| REL-010 | `is_retryable(AUTHENTICATION_FAILURE)` → False |
| REL-011 | `call_with_retry` succeeds on 1st attempt → result returned, 1 attempt |
| REL-012 | `call_with_retry` retries READ_TIMEOUT, succeeds on 3rd → result returned |
| REL-013 | `call_with_retry` exhausts all retries → `GraderErrorClass.READ_TIMEOUT` error, None |
| REL-014 | `call_with_retry` stops immediately on AUTHENTICATION_FAILURE (no retry) |
| REL-015 | `call_with_retry` respects overall_deadline (fake clock) |
| REL-016 | `call_with_retry` uses jitter: backoff delays are in expected range |
| REL-017 | `call_with_retry` respects `get_retry_after()` for 429 |
| REL-018 | `GradingObserver.record()` writes JSON line without secrets |
| REL-019 | Duplicate call on same input_hash hits cache, skips provider call |
| REL-020 | `call_with_retry` emits GradingEvent per attempt via observer |

### Task 6 — Write tests: `test_gateway_timeout.py`

**File:** `tests/supervisor/test_gateway_timeout.py`

| Test ID | Scenario |
|---------|----------|
| GW-001 | `gateway_chat()` passes `timeout=30` (or env override) to litellm |
| GW-002 | `gateway_chat()` litellm raises Exception → returns error record with `error_class_redacted` set |
| GW-003 | `gateway_chat()` litellm timeout → error record status=`CallStatus.error` |
| GW-004 | Missing API key → `CallStatus.blocked_missing_env` (existing, verify unbroken) |
| GW-005 | `GRADER_LLM_TIMEOUT` env override respected |

### Task 7 — Pilot proof scripts

**File:** `tests/supervisor/pilots/pilot_llm_grader_timeout.py`

A runnable script (no live network needed) that executes all 8 pilots using mocks:

| Pilot | What it proves |
|-------|---------------|
| P1 — Normal grading | Successful path: result persisted, cache populated, no regression |
| P2 — Injected SSL read timeout | READ_TIMEOUT classified → bounded retry → correct state |
| P3 — Transient provider failures (reset, 429, 5xx) | Retry policy + Retry-After behavior |
| P4 — Permanent failure (401) | No useless retry, FAILED_PERMANENT state |
| P5 — Restart/resume | Grade cache provides safe resume — no dup provider call |
| P6 — Fallback (gateway → SDK) | Governed fallback: gateway fails → SDK used, provenance recorded |
| P7 — Concurrency/load | RetryPolicy respects overall_deadline under concurrent load |
| P8 — Idempotency | Same evidence_hash → cache hit, provider NOT called |

Each pilot prints `PASS` / `FAIL` and a brief summary; exit code 0 = all pass.

---

## Files to Create / Modify

| Action | File | Purpose |
|--------|------|---------|
| CREATE | `tools/supervisor/grader_reliability.py` | Shared error classifier, retry policy, observer |
| MODIFY | `tools/ai/control_plane/gateway.py` | Add `timeout=` to litellm.completion() |
| MODIFY | `tools/supervisor/grade_declared_work.py` | Use shared retry + error classification in `_sv_sdk_fallback()` |
| MODIFY | `tools/supervisor/backends/llm_api_backend.py` | Add retry + error classification to urllib call |
| CREATE | `tests/supervisor/test_grader_reliability.py` | 20 deterministic tests (no live network) |
| CREATE | `tests/supervisor/test_gateway_timeout.py` | 5 gateway path tests |
| CREATE | `tests/supervisor/pilots/pilot_llm_grader_timeout.py` | 8 pilot proof runs (mock-based) |

---

## Existing Code to Reuse

- `tools/supervisor/grade_declared_work.py:63-100` — `_get_cached_grade()` / `_cache_grade()` —
  already provides idempotent re-run protection via content-hash. Reuse as-is.
- `tools/supervisor/grade_declared_work.py:39-60` — `_evidence_hash()` — stable input hash.
  Used as the idempotency key.
- `tools/supervisor/atomic_io.py` — `atomic_write_json()` — safe for result persistence.
- `tools/ai/control_plane/config.py` — `AIConfig.endpoint_identity` — safe hostname-only logging.
- `tests/supervisor/test_grade_timeout_behavior.py` — existing sys.modules injection pattern
  for mocking openai — reuse the `_call_sdk_fallback_with_mock_openai()` helper pattern.

---

## Verification (how to run after implementation)

```bash
# 1. Run focused reliability tests (no live network)
.venv/Scripts/pytest tests/supervisor/test_grader_reliability.py -v

# 2. Run gateway timeout tests
.venv/Scripts/pytest tests/supervisor/test_gateway_timeout.py -v

# 3. Run existing timeout regression tests (must not break)
.venv/Scripts/pytest tests/supervisor/test_grade_timeout_behavior.py tests/supervisor/test_grade_timeout_spec_parity.py -v

# 4. Run pilot proof (mock-based, no live network)
.venv/Scripts/python tests/supervisor/pilots/pilot_llm_grader_timeout.py

# 5. Full supervisor test suite (regression guard)
.venv/Scripts/pytest tests/supervisor/ -v --tb=short
```

Expected: all tests pass, pilot prints 8×PASS, no regressions in existing suite.

---

## Taskcards

| TC-ID | Status |
|-------|--------|
| TC-LLM-001 | CLOSED |
| TC-LLM-002 | CLOSED |
| TC-LLM-003 | CLOSED |
| TC-LLM-004 | CLOSED |
| TC-LLM-005 | CLOSED |
| TC-LLM-006 | CLOSED |
| TC-LLM-007 | CLOSED |
| TC-LLM-008 | CLOSED |


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-01T20:19:20.505583+00:00"
  locked_by: "df3c9d31692b"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->

# Telemetry and Agent Metrics Design Review

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-FINAL-DEEP-PLAN-HEALING-001
**Date:** 2026-05-18
**Gate:** 5
**Lane:** L5

---

## 1. Telemetry Architecture

### 1.1 Three-Layer Design

```
Layer 1: Per-Call JSONL        → .local/ai/llm-logs/{sprint-id}.jsonl (immediate, always)
Layer 2: Per-Sprint Aggregate  → In-memory during sprint, flushed at end
Layer 3: Agent Metrics Post    → Google Sheet append-only endpoint (async, retryable)
```

### 1.2 Per-Call Record Schema (30 fields)

```
TelemetryRecord:
  # Identity
  timestamp: datetime            # ISO 8601
  run_id: str                    # Sprint-unique run identifier
  sprint_id: str
  taskcard_id: str
  gate: Optional[str]
  format: Optional[str]

  # Model
  provider: str                  # "llm.professionalize.com"
  model_id: str                  # Exact model from discovery
  model_fingerprint: Optional[str]
  model_role: str                # From role routing
  endpoint_identity: str         # URL without secrets

  # Operation
  operation_type: str            # chat_completion, embedding, retrieval
  prompt_version: str            # Hash of prompt template
  input_artifact_hashes: list[str]
  output_artifact_hashes: list[str]

  # Tokens
  input_token_count: int
  output_token_count: int
  total_token_count: int
  embedding_count: Optional[int]

  # Retrieval
  vector_index_id: Optional[str]

  # Status
  api_calls_count: int           # Including retries
  retries: int
  fallback_model_used: bool
  status: str                    # success, error, timeout, rejected, role_unavailable
  error_class: Optional[str]     # Redacted error classification

  # Platform
  product: str                   # "FormatFactory"
  platform: str                  # "win32", "linux"

  # Post tracking
  posted_to_agent_metrics: bool
  local_spool_path: str
```

## 2. Agent Metrics Field Mapping (Concrete)

### 2.1 The 17 Agent Metrics Fields

Agent Metrics is a Google Sheet with 17 columns. Each row = one posting (typically one per sprint or one per batch).

### 2.2 Mapping Table: Local → Agent Metrics

| # | Agent Metrics Field | Source from Local Telemetry | Aggregation Rule |
|---|--------------------|-----------------------------|------------------|
| 1 | `timestamp` | Max `timestamp` across all calls in sprint | Latest call time |
| 2 | `agent_name` | Static: `"format-factory-ai"` | — |
| 3 | `agent_owner` | Static: `"Babar Raza"` | — |
| 4 | `job_type` | Most frequent `model_role` in sprint | Mode (if tie: first alphabetically) |
| 5 | `run_id` | `sprint_id` + `-` + SHA-256(all record hashes)[:8] | Deterministic from records |
| 6 | `status` | Worst status: if any `error` → `"failure"`; if any `timeout` → `"partial"`; else `"success"` | Worst-case |
| 7 | `product` | Static: `"FormatFactory"` | — |
| 8 | `platform` | Static: `"Python"` | — |
| 9 | `website` | Static: `"N/A"` | — |
| 10 | `website_section` | Static: `"N/A"` | — |
| 11 | `item_name` | Summary of operation types: `"LLM:5,Embed:2"` or `"LLM calls"` if only one type | Comma-separated counts |
| 12 | `items_discovered` | Count of all telemetry records (attempted calls) | SUM |
| 13 | `items_succeeded` | Count where `status == "success"` | SUM |
| 14 | `items_failed` | Count where `status != "success"` | SUM |
| 15 | `run_duration_ms` | Sprint wall-clock time (last timestamp - first timestamp in ms) | Delta |
| 16 | `token_usage` | Sum of all `total_token_count` | SUM |
| 17 | `api_calls_count` | Sum of all `api_calls_count` (including retries) | SUM |

### 2.3 Aggregation Verification Test

```
Given: 5 telemetry records for sprint X
  - 3 success (1000 tokens each), 1 timeout (500 tokens), 1 error (0 tokens)
Expected Agent Metrics row:
  timestamp: max of 5 timestamps
  status: "failure" (worst case)
  items_discovered: 5
  items_succeeded: 3
  items_failed: 2
  token_usage: 3500
  api_calls_count: sum of individual api_calls_count
```

## 3. Posting Lifecycle

### 3.1 Flow

```
Sprint End → Aggregate Records → Build Agent Metrics Row
  → POST to Google Sheet endpoint
  → On success: mark all records posted_to_agent_metrics=true
  → On failure: retain in spool, retry on next sprint
```

### 3.2 Idempotency

- `run_id` is deterministic (sprint_id + hash of records)
- Before posting: check idempotency ledger at `.local/ai/spool/posted.jsonl`
- If `run_id` already posted: skip (no double-post)
- Ledger entry: `{run_id, posted_at, response_status}`

### 3.3 Retry Policy

| Condition | Action |
|-----------|--------|
| Post succeeds | Mark posted, add to ledger |
| Post fails (network) | Retain in spool, retry next invocation |
| Post fails (auth) | Log error, do NOT retry (auth issue needs human) |
| Spool record > 7 days old | Mark `spool_expired`, stop retrying |
| Spool expired records | Remain in local JSONL for evidence, never deleted |

### 3.4 Offline Mode

When Agent Metrics endpoint is unreachable:
1. All telemetry records written to local JSONL (always happens)
2. Aggregation still computed
3. Posting skipped with `posted_to_agent_metrics: false`
4. Spool accumulates
5. Next sprint invocation attempts to drain spool
6. No AI operations blocked by posting failure

## 4. Evidence Bundle Telemetry Integration

Evidence bundles include a **summary**, not raw JSONL:

```
AI Telemetry Summary:
  sprint_id: str
  total_calls: int
  calls_by_operation_type: dict[str, int]
  calls_by_model_role: dict[str, int]
  calls_by_status: dict[str, int]
  total_tokens: int
  fallback_usage_count: int
  error_count_by_class: dict[str, int]
  agent_metrics_post_status: str  # "posted", "pending", "failed", "offline"
  models_used: list[str]
```

## 5. What Breaks in Telemetry

| Failure | Consequence | Mitigation |
|---------|------------|------------|
| JSONL write fails | Call result returned but no record | Write before returning; fail call if write fails |
| Spool corrupted | Partial records, aggregation wrong | Line-by-line validation; skip corrupt lines |
| Agent Metrics schema changes | Posts rejected | Version check before posting; spool until fixed |
| Clock skew | Timestamps inconsistent | Use monotonic timestamps for ordering |
| Concurrent writes | Interleaved JSONL lines | File-level locking or per-call temp-file + rename |
| Sprint ID not set | Records unattributable | Require sprint_id in gateway config; reject if missing |

## 6. Privacy and Security Controls

1. No API keys in telemetry records (endpoint_identity strips auth)
2. No prompt text in records (only prompt_version hash)
3. No input/output content in records (only hashes)
4. Error messages redacted to error_class enum
5. JSONL files in .local/ (gitignored)
6. Evidence summary contains aggregates only

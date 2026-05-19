# AI Phase 2: Telemetry and Agent Metrics Mapping Report
# Sprint: R26 Lane C
# Date: 2026-05-19

## Agent Metrics Mapping

Agent Metrics is the canonical telemetry sink. Local JSONL spool is offline buffer, replay ledger, evidence artifact, and debug trace.

### Field Mapping (AIUsageRecord → Agent Metrics)

| AIUsageRecord Field | Agent Metrics Field | Status |
|--------------------|--------------------|--------|
| timestamp | timestamp | mapped |
| sprint_id | job_type | mapped |
| run_id | run_id | mapped |
| status | status | mapped |
| operation | product | mapped |
| input_tokens | token_usage.input | mapped |
| output_tokens | token_usage.output | mapped |
| total_tokens | token_usage.total | mapped |
| api_calls_count | api_calls_count | mapped |

### AI-Specific Local-Only Fields (preserved in spool, NOT posted)

| Field | Purpose |
|-------|---------|
| model | Model ID used |
| role | Role that selected the model |
| provider | Provider name |
| prompt_hash | SHA-256 hash of prompt content |
| input_artifact_hashes | Hashes of input artifacts |
| output_artifact_hashes | Hashes of output artifacts |
| model_fingerprint | Model discovery fingerprint |
| fallback_used | Whether fallback routing was used |
| evidence_path | Path to related evidence bundle |
| endpoint_identity | Hostname of endpoint (no secrets) |
| error_class_redacted | Exception class name (no stack trace) |

## Spool Replay Validation

Added `validate_spool_record()` and `validate_spool_for_replay()` to `spool_manager.py`.

### Validation Rules
1. Every record must have `timestamp`
2. Every record must have `taskcard_id`, `gate_id`, or `sprint_id` (run context)
3. No secrets (sk-*, Bearer tokens) in any field value
4. `posted_to_agent_metrics` must be False (Phase 2 — no external posting)

### External Posting Status
- **posted_externally: false**
- **blocked_by_policy: true**
- Agent Metrics endpoint/token not configured and no repo gate authorizes test posting

## New Tests (Lane C): 12 tests

| Test Class | Tests | Status |
|-----------|-------|--------|
| TestAgentMetricsMapping | 4 | PASS |
| TestSpoolRecordValidation | 7 | PASS |
| TestSpoolReplayValidation | 3 | PASS (includes posted_to_agent_metrics=false check) |

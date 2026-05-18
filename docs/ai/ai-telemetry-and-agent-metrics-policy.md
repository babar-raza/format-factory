# AI Telemetry and Agent Metrics Policy

**Version:** 1.0
**Date:** 2026-05-18
**Status:** PLAN — Implementation not yet authorized
**Authority:** docs/ai/ai-platform-operating-model.md

---

## 1. Purpose

Define the telemetry architecture for all AI/LLM/Embedding usage in Format Factory. Agent Metrics is the canonical telemetry/analytics sink. Local JSONL is allowed only as offline spool, replay ledger, evidence artifact, or pre-post buffer — not as the final telemetry product.

## 2. Canonical Telemetry Sink: Agent Metrics

Agent Metrics is the production telemetry and analytics product for AI usage. The local AI layer must align its telemetry fields and patterns to Agent Metrics API fields and existing collector/poster patterns.

### 2.1 Why Agent Metrics (Not Custom JSONL-Only)

- Centralized analytics across all AI operations
- Consistent field schema aligned to industry patterns
- Aggregation, dashboards, and alerting capabilities
- Cross-project comparability
- Token usage and cost tracking
- Avoiding reinventing a metrics product

### 2.2 Local JSONL Role

Local JSONL files in `.local/ai/llm-logs/` serve as:
- **Offline spool** — buffer when Agent Metrics is unreachable
- **Replay ledger** — complete record for deterministic rerun analysis
- **Evidence artifact** — included in evidence bundles
- **Pre-post buffer** — staging area before Agent Metrics post
- **Debug trace** — detailed per-call diagnostics

Local JSONL is NOT the final telemetry product. It is the local substrate that feeds Agent Metrics.

## 3. Telemetry Record Schema

Every AI call (LLM, embedding, retrieval) must record the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | ISO 8601 | Yes | Call timestamp |
| `run_id` | string | Yes | Unique run identifier |
| `sprint_id` | string | Yes | Current sprint identifier |
| `taskcard_id` | string | Yes | Linked taskcard |
| `gate` | string | If applicable | Relevant gate (e.g., gate_4, gate_11) |
| `format` | string | If applicable | Target format (e.g., fods, fodt) |
| `product` | string | If applicable | Product track (python-foss, net-commercial) |
| `platform` | string | Yes | Operating platform (win32, linux, etc.) |
| `provider` | string | Yes | Endpoint provider (llm.professionalize.com, local, etc.) |
| `model_id` | string | Yes | Exact model identifier |
| `model_fingerprint` | string | If available | Model version/hash |
| `model_role` | string | Yes | Role from routing (agentic_low_risk, structured_extraction, etc.) |
| `endpoint_identity` | string | Yes | Endpoint URL without secrets |
| `operation_type` | string | Yes | chat_completion, embedding, retrieval, etc. |
| `input_token_count` | integer | Yes | Input tokens consumed |
| `output_token_count` | integer | Yes | Output tokens generated |
| `total_token_count` | integer | Yes | Total tokens |
| `embedding_count` | integer | If applicable | Number of embeddings generated |
| `vector_index_id` | string | If applicable | Vector index used for retrieval |
| `prompt_version` | string | Yes | Hash of prompt template |
| `input_artifact_hashes` | list[string] | Yes | SHA-256 of input artifacts |
| `output_artifact_hashes` | list[string] | Yes | SHA-256 of output artifacts |
| `api_calls_count` | integer | Yes | Number of API calls (including retries) |
| `retries` | integer | Yes | Number of retry attempts |
| `fallback_model_used` | boolean | Yes | Whether fallback model was used |
| `status` | string | Yes | success, error, timeout, rejected, etc. |
| `error_class` | string | If error | Redacted error classification |
| `evidence_bundle_path` | string | If applicable | Path to evidence bundle |
| `posted_to_agent_metrics` | boolean | Yes | Whether successfully posted |
| `local_spool_path` | string | Yes | Path to local JSONL record |

## 4. Agent Metrics Integration

### 4.1 Post Flow

```
AI Call → Local JSONL (immediate) → Agent Metrics Post (async)
                                  → Update posted_to_agent_metrics flag
                                  → On failure: retain in spool for retry
```

### 4.2 Field Mapping

The local telemetry schema maps to Agent Metrics API fields. Mapping rules:
- Direct 1:1 mapping where field names match
- Composite fields (e.g., `format` + `gate` → Agent Metrics dimension)
- Redacted fields (error details stripped to error_class)
- Excluded fields (local_spool_path not posted)

### 4.3 Retry Policy

- On Agent Metrics post failure: retain record in spool
- Retry on next pipeline invocation
- Maximum retry age: 7 days
- After 7 days: mark as `spool_expired` and stop retrying
- Spool expired records remain in local JSONL for evidence

### 4.4 Offline Mode

When Agent Metrics is unreachable:
- All telemetry records written to local JSONL
- `posted_to_agent_metrics: false` for all records
- Spool accumulates until connectivity restored
- Next pipeline invocation attempts to drain spool

## 5. Telemetry for Evidence Bundles

Evidence bundles include:
- Telemetry summary (counts by operation_type, model_role, status)
- Total token usage for the sprint
- Model selection frequency
- Fallback usage count
- Error count by error_class
- Agent Metrics post success rate

Raw JSONL is NOT included in evidence bundles (too verbose). Summary statistics only.

## 6. Privacy and Security

- No secrets (API keys, tokens) in telemetry records
- `endpoint_identity` contains URL without authentication parameters
- `error_class` is a classification, not raw error messages
- Input/output content is NOT recorded — only hashes
- Prompt text is NOT in telemetry — only prompt_version hash

## 7. Cross-References

| Document | Relationship |
|----------|-------------|
| `docs/ai/ai-platform-operating-model.md` | Parent platform model |
| `AGENTS.md` Section H5, Section L | Existing run record requirements |
| `docs/ai-usage-operating-model.md` | AI usage ledger format (existing) |
| `docs/ai/ai-risk-register.md` | RISK-AI-016, RISK-AI-017, RISK-AI-023 |

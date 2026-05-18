# Model Routing and Discovery Policy

**Version:** 1.0
**Date:** 2026-05-18
**Status:** PLAN — Implementation not yet authorized
**Authority:** docs/ai/ai-platform-operating-model.md

---

## 1. Purpose

Define how Format Factory discovers, evaluates, selects, and routes to AI models at llm.professionalize.com. Model selection must be role-based, not hardcoded, because the endpoint can add, remove, rename, or replace models without notice.

## 2. Environment Configuration

All endpoint configuration comes from system environment:
- `GPT_OSS_API_KEY` — API authentication
- `GPT_OSS_ENDPOINT` — Base URL

No model names, endpoint URLs, or credentials may be hardcoded in any tool or config file committed to the repository. The file `tools/llm/endpoints.yaml` may reference environment variable names but must not contain actual values.

## 3. Model Discovery

### 3.1 Discovery Process

On each pipeline invocation that requires AI:
1. Read `GPT_OSS_ENDPOINT` from environment
2. Call the model listing endpoint (e.g., `/v1/models`)
3. For each discovered model, capture:
   - model_id
   - model_name
   - context_window (if reported)
   - capabilities (chat, completion, embedding)
   - max_tokens (if reported)
   - pricing_tier (if reported)
4. Store discovered models in `.local/ai/model-registry/models-{timestamp}.json`
5. Compare against previous discovery to detect changes

### 3.2 Capability Probing

After discovery, probe each model for:
- Chat completion support (structured output)
- Embedding generation support (with dimension count)
- Function/tool calling support
- JSON mode support
- Token limit accuracy

Probing uses minimal, non-sensitive test inputs. Results cached until next discovery refresh.

### 3.3 Fail-Closed Behavior

If a required role capability is unavailable (no model meets minimum requirements for the role):
1. Log `ROLE_UNAVAILABLE: {role_name}` to telemetry
2. Do NOT fall back to an unqualified model
3. Stop the task and report the gap
4. Record the failure in the evidence bundle

## 4. Role-Based Model Routing

### 4.1 Defined Roles

| Role | Purpose | Minimum Capability | Preferred Model Family |
|------|---------|-------------------|----------------------|
| `agentic_low_risk` | Classification, sorting, simple extraction | Chat + structured output | Qwen2 |
| `agentic_high_risk` | Repo mutations, evidence generation | NOT routed through llm.professionalize.com | Claude/Codex |
| `structured_extraction` | Spec fact extraction, requirement drafting | Chat + JSON mode + 8K+ context | GPT-OSS |
| `security_analysis` | Parser security review, fuzzing strategy | Chat + 16K+ context | GPT-OSS |
| `test_generation` | Test idea generation from requirements | Chat + structured output | GPT-OSS |
| `evidence_review` | Sprint evidence gap analysis | Chat + 16K+ context | GPT-OSS |
| `embedding_retrieval` | Spec/evidence vector encoding | Embedding + stable dimensions | Embedding model (auto-detected) |
| `retrieval_reranker` | Re-ranking retrieved chunks | Chat + structured output | Deferred (Phase 6+) |

### 4.2 Selection Algorithm

```
1. Enumerate available models from latest discovery
2. Filter by role's minimum capability requirements
3. Prefer the role's preferred model family
4. If preferred family unavailable, check fallback order
5. If no model qualifies, fail closed
6. Log selected model, fingerprint, and role in telemetry
```

### 4.3 Fallback Policy

Fallback order per role is defined in the control plane configuration. Fallback rules:
- Fallback model must still meet minimum capability for the role
- Fallback selection is logged with `fallback_model_used: true`
- Quality degradation risk from fallback must be documented
- A fallback that silently changes output quality triggers a warning in evidence

## 5. Model Fingerprinting

Every AI call must capture:
- `model_id` — exact model identifier returned by API
- `model_fingerprint` — hash or version string if available
- `discovery_timestamp` — when the model was last discovered
- `endpoint_identity` — endpoint URL (without secrets)

These fields are included in telemetry records and evidence artifacts.

## 6. Qwen2 Routing Constraints

Qwen2 may be selected for `agentic_low_risk` roles only after:
1. Model discovery confirms Qwen2 availability
2. Capability probe confirms structured output support
3. Governance check confirms the task is classified as low-risk
4. Task contract explicitly allows Qwen2

Qwen2 MUST NOT be routed to:
- `agentic_high_risk` — use Claude/Codex
- `security_analysis` — requires higher reasoning capability
- Any task that involves direct repo mutations without IV

See `docs/ai/agentic-qwen2-control-policy.md` for full Qwen2 controls.

## 7. GPT-OSS Routing

GPT-OSS should be the default recommendation for:
- `structured_extraction`
- `security_analysis`
- `test_generation`
- `evidence_review`

Selection conditional on endpoint capability confirmation. If GPT-OSS is unavailable, the task must fail closed rather than silently route to a less capable model.

## 8. Embedding Model Routing

Embedding model is auto-detected during discovery:
1. Filter discovered models for embedding capability
2. Verify dimension stability (compare against previous index dimensions)
3. If dimension changes, all existing indexes must be flagged for rebuild
4. Bind to embedding roles after stability check
5. Record embedding model fingerprint in every vector index manifest

## 9. Cross-References

| Document | Relationship |
|----------|-------------|
| `docs/ai/ai-platform-operating-model.md` | Parent platform model |
| `docs/ai/agentic-qwen2-control-policy.md` | Qwen2-specific controls |
| `docs/ai/gpt-oss-synthesis-control-policy.md` | GPT-OSS-specific controls |
| `docs/ai/ai-telemetry-and-agent-metrics-policy.md` | Telemetry fields |

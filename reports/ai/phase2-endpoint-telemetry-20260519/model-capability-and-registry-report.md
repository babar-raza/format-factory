# AI Phase 2: Model Capability and Registry Report
# Sprint: R26 Lane B
# Date: 2026-05-19

## Changes Made

### ModelCapability Schema Enhancement
Added 5 new fields to `tools/ai/schemas/models.py:ModelCapability`:

| Field | Type | Purpose |
|-------|------|---------|
| `supports_json_or_structured_output` | bool | Discoverable structured output capability |
| `model_family_guess` | str | Inferred from model_id (no hardcoded names) |
| `role_candidates` | list[AIRole] | Suggested roles based on family |
| `last_probe_status` | str | Last capability probe result |
| `endpoint_identity_hash` | str | SHA-256 truncated hash of endpoint hostname |

### Model Family Inference
Added `guess_model_family(model_id)` to `model_discovery.py`:
- Pattern-based matching on model_id substrings (gpt, qwen, embed, llama, mistral)
- Returns "unknown" for unrecognized patterns
- No hardcoded model names — inference is based on family keywords only

### Role Candidate Inference
Added `infer_role_candidates(model_id)` to `model_discovery.py`:
- gpt family → structured_extraction, evidence_review, summarization
- qwen family → agentic_low_risk
- embedding family → embedding_retrieval
- unknown → summarization (safe default)

### Discovery Enhancement
`discover_models()` now populates:
- `model_family_guess` from `guess_model_family()`
- `role_candidates` from `infer_role_candidates()`
- `endpoint_identity_hash` from SHA-256 of hostname

## Endpoint Probe Status

- GPT_OSS_ENDPOINT: not configured in this environment
- Status: **blocked_missing_env**
- No live probe executed — fixture-mode tests only

## New Tests (Lane B): 20 tests

| Test Class | Tests | Status |
|-----------|-------|--------|
| TestModelFamilyGuess | 7 | PASS |
| TestRoleCandidates | 3 | PASS |
| TestModelCapabilityFields | 2 | PASS |
| TestDiscoverModelsPhase2 | 1 | PASS |
| TestModelDisappearanceAndReplacement | 4 | PASS |
| TestFallbackLogging (existing expanded) | 3 | PASS (in existing test_model_router.py) |

## Forbidden Actions Verified
- No hardcoded model names
- No embeddings created
- No vector DB
- No synthesis workflows
- No agentic execution
- No env values printed or committed

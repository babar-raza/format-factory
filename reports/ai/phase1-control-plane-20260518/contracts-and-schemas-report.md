# Contracts and Schemas Report

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-PHASE1-CONTROL-PLANE-FOUNDATION-001
**Date:** 2026-05-18
**Gate:** GATE 3

## Pydantic v2 Schemas (11 models)

| Model | Purpose |
|-------|---------|
| AIProviderConfig | Endpoint configuration (env var names, never values) |
| ModelCapability | Discovered model capabilities |
| ModelFingerprint | Model identity hash at discovery time |
| ModelSelectionRequest | Router input (role + optional preference) |
| ModelSelectionDecision | Router output (selected model, fallback, fail-closed) |
| AITaskContract | Task constraints (retries, timeout, requirements) |
| PromptTemplateRecord | Prompt registry with hash/version |
| AIUsageRecord | 24-field telemetry record |
| ArtifactAuthorityState | 12-state authority lifecycle |
| ValidationResult | Schema/content validation outcome |
| RuntimeGuardResult | Import guard scan outcome |

## YAML Contracts (5 files)

| File | Content |
|------|---------|
| roles.yaml | 7 roles (structured_extraction, security_analysis, test_generation, evidence_review, summarization, embedding_retrieval, agentic_low_risk) |
| task-types.yaml | 6 task types with role assignments |
| artifact-authority-states.yaml | 12 states, transition rules, terminal states |
| forbidden-runtime-imports.yaml | Protected paths, forbidden imports/env/URLs |
| telemetry-schema.yaml | 24-field record spec, spool format, never-log list |

## Prompt Registry

- 2 probe templates registered (capability_probe_v1, model_identity_probe_v1)
- Hash/version tracking via PromptTemplateRecord
- No production prompts (Phase 1 only)

## Tests

27/27 PASS (test_schemas_contracts.py)

## GATE 3: PASS

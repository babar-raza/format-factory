# Validators and Runtime Guard Report

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-PHASE1-CONTROL-PLANE-FOUNDATION-001
**Date:** 2026-05-18
**Gate:** GATE 6

## Implementation

### Schema Validator
- **File:** tools/ai/validators/schema_validator.py
- Wraps Pydantic v2 validation with standardized ValidationResult output

### Authority Lifecycle Validator
- **File:** tools/ai/validators/authority_lifecycle.py
- Enforces 12-state machine transitions
- `can_transition()` for single-step checks
- `validate_transition_chain()` for multi-step validation
- No skip from ai_draft to authoritative_after_gate

### Runtime AI-Import Guard
- **File:** tools/ai/validators/runtime_guard.py
- Scans: src/python/, src/net/
- Forbidden imports: tools.ai, litellm, lancedb, llama_index, langchain, openai, anthropic, qdrant, chromadb, ollama
- Forbidden env refs: GPT_OSS_API_KEY, GPT_OSS_ENDPOINT, PROFESSIONALIZE_API_KEY, PROFESSIONALIZE_BASE_URL
- Forbidden URL refs: llm.professionalize.com
- **Real repo scan result:** PASS (0 violations)

### Secret Redaction
- **File:** tools/ai/validators/secret_redaction.py
- Redacts sk-* keys, Bearer tokens, URL key/token params
- Cross-checks against known env var values

## Tests

- test_runtime_guard.py: 6/6 PASS
- test_authority_lifecycle.py: 7/7 PASS
- test_secret_redaction.py: 6/6 PASS

## GATE 6: PASS

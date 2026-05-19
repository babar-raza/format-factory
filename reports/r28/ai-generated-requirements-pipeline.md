# R28 Lane E: AI-Generated Requirements Pipeline
# Date: 2026-05-19

## Module Created

### tools/ai/requirements/generator.py

- **GeneratedRequirement** dataclass with full provenance:
  - req_id, text, format_id, source_chunk_hash, source_path, source_section
  - authority_state (always starts as ai_draft)
  - priority (EXISTING_SOURCE > TEST_EVIDENCE > VERIFIED_FACT > SPEC > PRODUCT_DECISION > AI_PROPOSAL)
  - verifier_status (pending_review, accepted, rejected)
  - generation_hash for audit

- **REQUIREMENT_SCHEMA** — validates required fields, valid priorities, valid states

- **validate_requirement()** — schema validation with provenance check

- **review_requirement()** — verifier accept/reject pipeline

- **generate_requirements_from_synthesis()** — extracts requirements from synthesis output

- **write_requirements_packet()** — writes JSON packet with authority_state = ai_draft

## Provenance Chain

Every requirement links to:
1. Source chunk hash (from normalized spec)
2. Source file path
3. Source section
4. Generation hash (deterministic from req_id + text + chunk_hash)
5. Generation timestamp

## Verifier Lane

- Requirements start as `pending_review`
- Verifier can `accept` (→ verifier_reviewed) or `reject` (stays ai_draft)
- No auto-acceptance
- Priority levels enforced by schema

## Test Results

- **New tests:** 13 (test_r28_requirements_pipeline.py)
- **All 13/13 PASS**

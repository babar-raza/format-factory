# Lane C: GPT-OSS Synthesis Controls

## Implementation
Created `tools/ai/synthesis/runner.py` with:
1. `SynthesisResult` — tracks authority state (always ai_draft), citations, contradictions, schema validation
2. `validate_task_contract()` — validates AITaskContract before synthesis
3. `validate_structured_output()` — schema validation against required fields
4. `verify_citations()` — citation source/text verification against local snippets
5. `check_contradictions()` — deterministic fallback against verified-facts.yaml
6. `run_synthesis()` — full validation pipeline on raw LLM output (does NOT call LLM)

All outputs start as `ai_draft`. Authority state is never auto-escalated.

## Fixture/Offline Tests (11)
- test_valid_contract, test_missing_task_id
- test_valid_output, test_missing_field, test_no_schema, test_non_dict_output
- test_valid_citations, test_missing_source, test_empty_citations, test_citation_text_not_in_source
- test_missing_verified_facts, test_no_contradictions
- test_valid_extraction, test_malformed_json_rejected, test_authority_never_escalated, test_missing_citation_error

## Live Endpoint: BLOCKED_MISSING_ENV (GPT_OSS_ENDPOINT not set)

## Lane C Status: CLOSED_VERIFIED (fixture mode)

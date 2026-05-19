# R29 Lane G: AI Requirements into Format Pipeline
# Date: 2026-05-19

## Status
FODS and FODT have existing generated-requirements directories with schema-validated artifacts.
The R29 Lane D tests (TestAuthorityEscalationGuard, TestMultiFormatContamination, TestRequirementsValidationEdgeCases) verify the generation pipeline's safety properties.

## Key Verifications
1. Generated requirements always start as `ai_draft` — no authority escalation
2. Priority hierarchy enforced: EXISTING_SOURCE > TEST_EVIDENCE > VERIFIED_FACT > SPEC > PRODUCT_DECISION > AI_PROPOSAL
3. Invalid priorities are rejected by `validate_requirement()`
4. Reviewer can accept (-> verifier_reviewed) or reject (stays ai_draft)
5. No auto-escalation to authoritative_after_gate
6. Format ID contamination prevented — all requirements in a packet share one format_id

## Existing Requirements State
- `generated-requirements/fods/` — schema-validated, verifier-reviewed, PENDING IV acceptance
- `generated-requirements/fodt/` — schema-validated, verifier-reviewed, PENDING IV acceptance
- ODS/ODT/QOI — no generated requirements yet (not yet needed for Gate 5-7 work)

## New Tests Covering This Lane
From test_r29_synthesis_hardening.py:
- TestAuthorityEscalationGuard (5 tests)
- TestMultiFormatContamination (2 tests)
- TestRequirementsValidationEdgeCases (5 tests)

## CLOSED_VERIFIED

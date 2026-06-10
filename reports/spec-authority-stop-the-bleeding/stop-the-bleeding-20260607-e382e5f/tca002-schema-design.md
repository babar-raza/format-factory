# TCA-002: spec_fact_refs BLOCKING Enforcement — Evidence
# Sprint: SPEC-AUTHORITY-LAYER-STOP-THE-BLEEDING-001
# Run: stop-the-bleeding-20260607-e382e5f
# Date: 2026-06-07

## Artifacts Produced

1. schemas/evidence/spec-fact-refs.schema.json — formal JSON schema for spec_fact_refs field
   - Defines spec_fact_refs array of FACT-<FORMAT>-<NUMBER> patterns
   - Defines 5 exception_classification values
   - Defines enforcement_rule with BLOCKING mode
   - Includes 4 examples (2 PASS, 2 FAIL)

2. docs/automation/supervisor-worker-contract.md — updated with spec_fact_refs section
   - Section: "Spec Fact References (spec_fact_refs) — BLOCKING Enforcement"
   - Lists 5 blocking item types: PRODUCT_SOURCE, TEST, REQUIREMENT, READINESS, RELEASE_GATE
   - Documents 5 exception classifications
   - Documents validated_by rules

## Validation
- Schema JSON valid: PASS (python -m json.tool exits 0)
- Contract updated: PASS (grep spec_fact_refs returns multiple hits)

## Negative Test
A PRODUCT_SOURCE declaration with empty spec_fact_refs and no exception_classification is
now INVALID per the contract. The supervisor-worker-contract.md explicitly states this is a
hard gate, not a warning.

## Status: CLOSED_VERIFIED

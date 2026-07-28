---
version: "1.0"
last-updated: "2026-07-23"
phase-available: "all"
gate-required: null
skill_type: "ATOMIC_SKILL"
idempotency: "Equivalent contract inputs compile to byte-identical projections and digests."
risk_level: HIGH
created-by: SKILL-GAP-FF6-PRODUCT-CONTRACT-RUNTIME
product_track: format_contract
generated_by: codex
visibility: generated
---

# /product-contract-runtime-repair

Repair the strict `ProductContract` runtime and its regression controls. This
skill owns content-address closure, stable obligation identity, fact-reference
edges, mandatory-obligation failure semantics, and deterministic compilation.

## Required Inputs

- `defect_id`
- `failing_regression`
- `expected_invalidation_input`

## Execution

1. Reproduce the defect with a minimal strict-contract input.
2. Add a regression test that fails for the root cause.
3. Apply the smallest runtime correction without weakening legacy validation.
4. Prove three same-input compilations have identical projections and digests.
5. Mutate each newly covered input and prove the digest changes.
6. Run the production-program and format-contract focused suites.

## Mandatory Validations

- `complete_contract_digest_closure`
- `obligation_fact_edges_preserved`
- `equivalent_rerun_determinism`
- `changed_contract_input_invalidates_digest`

## Allowed Paths

- `tools/format_contract/product_contract.py`
- `tests/production_program/test_production_program.py`
- `reports/skills-rff6/skill-transcripts/product-contract-runtime-repair-*.json`

## Forbidden Paths

- `src/**`
- gate or release approval records
- legacy validator weakening
- manual promotion state

## Stop Conditions

- If a proposed change makes missing authority or fact references advisory,
  stop and retain the fail-closed behavior.
- If equivalent inputs produce different digests, block promotion and isolate
  the nondeterministic field.

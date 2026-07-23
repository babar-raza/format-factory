---
version: "1.0"
last-updated: "2026-07-23"
phase-available: "all"
gate-required: null
skill_type: "ATOMIC_SKILL"
idempotency: "Equivalent target mappings produce byte-identical controller projections."
risk_level: HIGH
created-by: SKILL-GAP-FF6-PRODUCTION-PROGRAM-IDENTITY
product_track: machinery_repair
generated_by: codex
visibility: generated
---

# /production-program-controller-repair

Repair the crash-resumable production controller's target identity model.
Product state, Python package paths, and canonical repository format-contract
IDs are separate authorities and must be represented explicitly.

## Required Inputs

- `defect_id`
- `product_id`
- `contract_format_id`
- `source_package_id`

## Execution

1. Reproduce the incorrect contract lookup with an identity whose product ID
   differs from its canonical format registry ID.
2. Introduce an immutable target descriptor with explicit product, contract,
   and source-package identities.
3. Preserve the product ID as the persistent state and gap ownership key.
4. Resolve contract files through the canonical contract ID and source/test
   paths through the package ID.
5. Include both product and contract identities in snapshot and compilation
   evidence.
6. Prove identity targets retain prior behavior and that equivalent bootstraps
   remain deterministic.

## Mandatory Validations

- `canonical_contract_registry_mapping`
- `stable_product_state_identity`
- `stable_gap_ownership_identity`
- `identity_target_regression`
- `deterministic_bootstrap`

## Allowed Paths

- `tools/supervisor/production_program.py`
- `tests/production_program/test_production_program.py`
- `reports/skills-*/skill-transcripts/production-program-controller-repair-*.json`

## Forbidden Paths

- `src/**`
- contract or authority content
- persistent state key renames
- manual gap resolution or promotion edits
- human-only gate and release records

## Stop Conditions

- If an existing product state key would be renamed, add an explicit migration
  before proceeding.
- If a mapping can resolve a contract outside the canonical format-contract
  directory, fail closed.
- If an identity target's behavior changes, retain the existing behavior and
  repair the descriptor model.

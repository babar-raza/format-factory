---
version: "1.0"
last-updated: "2026-07-16"
phase-available: "all"
gate-required: null
skill_type: PIPELINE_TOOL
idempotency: "idempotent"
loc_budget: "0 lines own logic - thin routing over registered skills only"
test_path: "tests/format_contract/"
risk_level: LOW
created-by: TC-FCL-080
product_track: format_contract
---

# /prove-format-contract

End-to-end proof for one format: readiness -> compile (--verify-idempotency) -> validate -> score -> (reference formats) compare vs oracle -> reconcile -> gaps -> /review-format-contract adversarial verdict -> second-run idempotency evidence. Prints every skill invoked, all evidence paths, and the final verdict; non-zero on any blocking failure.

## Skill chain (routing only - this command implements NO workflow of its own)

check-contract-sal-readiness, compile-format-contract, validate-format-contract, reconcile-contract-capabilities, compile-contract-gaps, review-format-contract

## Mandatory Validations

- **skill_chain_printed**: every invoked skill and its verdict printed
- **no_alternate_workflow**: any behavior beyond routing the chain above is a bypass (forbidden)

## Required Inputs

| Field | Description |
|---|---|
| `format_id` | Lowercase format id (backfill runs portfolio-wide without it) |

## Allowed Paths

- Whatever the routed skills allow - nothing additional

## Forbidden Paths

- Everything beyond the routed skills' allowed paths

## Stop Conditions

- First blocking failure in the chain: stop, print failing skill + evidence path, exit non-zero

## Output Format

Skill chain trace, authoritative input paths, output paths, validation results, evidence paths.

## Idempotency Contract

Inherited from the routed skills (all idempotent).

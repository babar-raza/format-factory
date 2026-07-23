---
version: "1.0"
last-updated: "2026-07-24"
phase-available: "all"
gate-required: null
skill_type: "ATOMIC_SKILL"
idempotency: "Equivalent family semantics, mapping, and readiness policy validate to identical canonical output."
risk_level: "MEDIUM"
created-by: "SKILL-GAP-FF6-FAMILY-PACK-AUTHORING"
product_track: "format_contract"
generated_by: codex
visibility: generated
---

# /create-format-family-pack

Create one genuinely new format-family policy pack. This skill owns family
semantics and readiness policy; it does not compile contracts or mutate
product source.

## Required inputs

- `family_id`
- `representative_formats`
- `semantic_scope`
- `excluded_concepts`
- `required_fact_categories`
- `policy_pack_path`

## Execution

1. Confirm no existing family pack accurately represents the format.
2. Define a positive semantic scope and nearby excluded concepts.
3. Author format-agnostic domains only for behavior shared by every
   representative format.
4. Add readiness categories, normalized weights, and evidence-scaled minimums.
5. Route each representative format to the family.
6. Run `family_pack_validator.py --verify-idempotency`.
7. Run focused format-contract tests, readiness, deterministic compilation,
   strict ProductContract validation, and a false-obligation scan.
8. Record the old/new obligation inventory and invalidation impact.

## Mandatory validations

- `family_pack_schema_valid`
- `baseline_ids_unique`
- `readiness_weights_normalized`
- `mapping_resolves`
- `excluded_concepts_do_not_leak`
- `semantic_applicability_review_recorded`
- `validator_idempotent`

## Allowed paths

- `shared/format-contracts/policy/family-packs/<family_id>.yaml`
- `shared/format-contracts/policy/format-family-map.yaml`
- `shared/format-contracts/policy/fact-category-requirements.yaml`
- `reports/skills-*/skill-transcripts/create-format-family-pack-*.json`

## Forbidden paths

- `src/**`
- `shared/sal-facts/**`
- generated contract bodies except through `/compile-format-contract`
- threshold reduction intended only to force a readiness pass
- human approval or release records

## Stop conditions

- Do not create a family when an existing pack can be narrowed safely without
  weakening its current formats.
- If readiness is blocked, preserve the threshold and route to authority/SAL
  acquisition.
- If a generated contract still contains an excluded concept, repair the
  family policy before compiling product work.

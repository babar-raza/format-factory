---
version: "1.0"
last-updated: "2026-07-23"
phase-available: "all"
gate-required: null
skill_type: "ATOMIC_SKILL"
idempotency: "An existing identical format-to-family mapping is a no-op."
risk_level: MEDIUM
created-by: SKILL-GAP-FF6-FORMAT-CONTRACT-ONBOARD
product_track: format_contract
generated_by: codex
visibility: generated
---

# /format-contract-onboard

Onboard a canonical format-registry identity into the format-contract family
map. This skill creates no product source and grants no implementation or
release approval.

## Required inputs

- `format_id`
- `family`
- `authority_source_ids`
- `sal_store_path`

## Execution

1. Prove the format ID exists in `registry/format-registry.yaml`.
2. Prove the named family pack exists and matches its declared family.
3. Prove every authority source is `ACQUIRED` with a SHA-256 content hash.
4. Prove the canonical SAL store exists, is non-empty, and all new facts bind
   acquired authority digests.
5. Add exactly one deterministic format-to-family mapping.
6. Run readiness, deterministic compilation, strict ProductContract, and
   idempotency checks.

## Mandatory validations

- `registry_entry_exists`
- `family_pack_exists`
- `authority_sources_acquired`
- `sal_store_nonempty`
- `deterministic_contract_compilation`

## Allowed paths

- `shared/format-contracts/policy/format-family-map.yaml`
- `reports/skills-*/skill-transcripts/format-contract-onboard-*.json`

## Forbidden paths

- `src/**`
- gate or release approval records
- family threshold reduction
- fabricated or URL-only authority status

## Stop conditions

- Stop the affected format if the registry identity, family pack, acquired
  source, or canonical fact store is absent.
- Stop if compilation is blocked or nondeterministic.

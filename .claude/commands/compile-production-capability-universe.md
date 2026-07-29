---
version: "1.0"
last-updated: "2026-07-29"
phase-available: "all"
gate-required: null
skill_type: PIPELINE_TOOL
idempotency: "Identical canonical inputs produce byte-identical inventories and manifest."
risk_level: HIGH
created-by: TC-FF6-CAPABILITY-COMPILER-001
product_track: format_contract
generated_by: codex
visibility: generated
---

# /compile-production-capability-universe

Compile the production capability and normative-obligation universe for one or
more formats from canonical format contracts, SAL facts, the locked release
policy, and explicit enrichment records.

## Required inputs

- `format_ids`: non-empty format IDs known to the policy.
- `policy_path`: repository-relative locked release policy.
- `enrichment_dir`: repository-relative per-format enrichment root.
- `output_dir`: repository-relative output root.

## Execution

```powershell
python -m tools.format_contract.capability_universe compile `
  --repo-root . `
  --policy plans/strategic/ff6/capability-policy.yaml `
  --enrichment-dir plans/strategic/ff6/capability-enrichments `
  --output-dir plans/strategic/ff6 `
  --format ipynb --format ora --format nrrd `
  --format xliff --format safetensors --format ubl
```

Use `--check` to compare an in-memory compilation with existing outputs without
writing. Use `--verify-idempotency` to compile three times in isolated temporary
directories and byte-compare every output.

## Invariants

- Compile obligations only through `tools.format_contract.product_contract`.
- Preserve canonical `SAL-<FORMAT>-OBL-*` IDs and provenance.
- Require one enrichment record per contract capability and reject extras.
- Use only `STABLE_REQUIRED`, `OPTIONAL_ADAPTER_REQUIRED`,
  `PREVIEW_ISOLATED`, or `EXCLUDED_WITH_AUTHORITY`.
- Reject duplicate, missing, foreign, dangling, or multiply owned references.
- Reject an excluded capability without authority basis and user disposition.
- Reject empty future implementation references; use the literal `PLANNED`.
- Include contract, SAL, policy, enrichment, compiler, and schema digests in the
  manifest.
- Exclude timestamps, absolute paths, random IDs, and filesystem ordering.
- Check mode writes no bytes.
- Never mutate product source, tests, packages, gates, or release state.

## Allowed paths

- `tools/format_contract/capability_universe.py`
- `tools/format_contract/capability_universe_command.py`
- `tools/format_contract/capability_universe_runtime.py`
- `tools/format_contract/capability_universe_validation.py`
- `tests/production_program/test_capability_universe.py`
- `schemas/ff6/capability-universe.schema.json`
- `plans/strategic/ff6/capability-policy.yaml`
- `plans/strategic/ff6/capability-enrichments/*.yaml`
- `plans/strategic/ff6/capabilities/*.yaml`
- `plans/strategic/ff6/obligations/*.yaml`
- `plans/strategic/ff6/capability-taxonomy.yaml`
- `plans/strategic/ff6/capability-coverage.yaml`
- `plans/strategic/ff6/capability-manifest.json`
- governed taskcards, controller events, gaps, and execution transcripts

## Forbidden paths

- `src/**`
- product test roots
- package/release metadata
- authority bytes or contract bodies
- gate or promotion records

## Mandatory validation

1. Focused compiler tests and negative controls pass.
2. Existing product-contract and production-program suites pass.
3. Three isolated compilations are byte-identical.
4. Each input category changes the aggregate manifest digest when mutated.
5. Check mode passes on committed outputs and writes nothing.
6. Skill/command/route registries and generated capability surfaces reconcile.
7. Execution transcript validates.

## Stop conditions

- Fail closed on missing or contradictory authority, contract, SAL, policy, or
  enrichment input.
- Do not omit an obligation to make counts reconcile.
- Do not replace a canonical ID with a hand-written alias.
- Do not promote a product based on successful compilation.

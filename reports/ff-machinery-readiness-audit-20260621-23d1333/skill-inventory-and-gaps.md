# Skill Inventory and Gaps
# Sprint ID: ff-machinery-readiness-audit-20260621-23d1333

## Skill Registry Overview

File: `.supervisor/skill-registry.yaml`
Version: 2.0, generated 2026-06-12

Status: `active_fail_closed` — skills require explicit execution handoff, no ad-hoc edits.

Global controls enforce:
- `source_edits_require_explicit_handoff: true`
- `exact_path_scope_required: true`
- `product_code_ledger_required_before_source_edit: true`
- `skill_invocation_transcript_required: true`

## Skill Inventory

### Product Skills (Core — R90 Original)

| Skill | Command | QName Required | Track | Status |
|-------|---------|---------------|-------|--------|
| add-dotnet-api | /add-dotnet-api | YES | commercial_dotnet | active |
| add-python-api | /add-python-api | YES | foss_python | active |
| add-python-object-model-feature | /add-python-object-model-feature | YES | foss_python | active |
| add-dotnet-object-model-feature | /add-dotnet-object-model-feature | YES | commercial_dotnet | active |
| add-same-format-writer-feature | /add-same-format-writer-feature | YES | foss_python | active |
| add-roundtrip-test | /add-roundtrip-test | NO | foss_python | active |
| add-dogfood-export | /add-dogfood-export | NO | dogfood | active |
| add-installed-package-example | /add-installed-package-example | NO | packaging | active |

### Spec/QName Skills

| Skill | Command | Status | Gap |
|-------|---------|--------|-----|
| spec-literal-qname-to-code-mapping | /spec-literal-qname-to-code-mapping | active | References `qname_ontology_generator.py` which was NOT FOUND in tools/supervisor/ |
| spec-parity-source-regeneration-and-migration | /spec-parity-source-regeneration-and-migration | active | Requires `blueprint_path` (spec-shaped blueprint) to exist first |
| python-reduced-spec-parity-model | /python-reduced-spec-parity-model | active | Reduced scope variant |
| spec-parity-verification | /spec-parity-verification | active | Verification skill — good |
| spec-shaped-product-architecture-blueprint | /spec-shaped-product-architecture-blueprint | active | Blueprint generation skill |

### Analytics Skill

| Skill | Command | Status | Note |
|-------|---------|--------|------|
| add-analytics-function | /add-analytics-function | active | SUSPENDED per keen-dancing-hopper plan. Do NOT use for ZST/XCF/FODG |

### Supervisor/Governance Skills

| Skill | Command | Status |
|-------|---------|--------|
| autonomous-loop | /autonomous-loop | active |
| build-context-pack | /build-context-pack | active |
| check-gate | /check-gate | active |
| check-release-boundary | /check-release-boundary | active |
| post-sprint-audit | /post-sprint-audit | active |
| plan-hardening | /plan-hardening | active |
| validate-product-code-ledger | /validate-product-code-ledger | active |
| validate-skill-transcript | /validate-skill-transcript | active |

## Skill Gaps

### Gap 1: qname_ontology_generator.py Missing (CRITICAL)

Skill `spec-literal-qname-to-code-mapping` invokes:
```
python tools/supervisor/qname_ontology_generator.py --format <FORMAT_ID> ...
```

This tool was NOT FOUND in `tools/supervisor/`. Without it, the QName mapping skill
cannot execute. This is a blocker for all QName compliance work.

**Required fix:** Implement `tools/supervisor/qname_ontology_generator.py` that:
1. Reads spec source from `.local/spec-cache/<format>/`
2. Extracts XML element/attribute names
3. Generates `qname-to-code-map-<format>.json`
4. Generates `namespace-tree-<format>.json`
5. Validates coverage against known spec sections

### Gap 2: No Spec-Shaped Blueprint for Any Format (BLOCKER)

Skill `spec-parity-source-regeneration-and-migration` requires `blueprint_path` pointing to
a spec-shaped architecture blueprint YAML. No such blueprint exists for any format.

Skill `spec-shaped-product-architecture-blueprint` exists to generate blueprints but has
never been run to produce one for any active format.

**Required fix:** Run `/spec-shaped-product-architecture-blueprint` for FODS first, produce
a verified blueprint, then use it as input to the migration skill.

### Gap 3: No QName Validator in Governance

governance_validators.py has 38 validators but none enforce QName class naming conventions
in product source. Skills declare `spec_qname_required: true` but this is not machine-checked
at sprint closeout.

**Required fix:** Add `validate_qname_compliance` validator to governance_validators.py
that checks product source files for canonical namespace patterns.

### Gap 4: Analytics Skill Suspended, No Replacement Path

`add-analytics-function` skill is SUSPENDED for ZST/XCF/FODG. The rotation was producing
spec-unsupported functions that triggered GOV_BLOCK. But there is no alternative skill for
adding SPEC-BACKED analytics functions.

**Required fix:** Create `add-spec-backed-analytics-function` skill that requires:
- `gap_ledger_ref` pointing to a GAP-* entry
- `spec_fact_ref` pointing to a FACT-* entry
- Routes to `{format}_analytics.py` file only

### Gap 5: No Skill Transcript Validation in CI

`validate-skill-transcript` skill exists but is not called automatically during sprint closeout.
Skill invocation transcripts are produced but not systematically validated.

## Repeatability Assessment

Skills are repeatable at the invocation level (same inputs → same outputs via handoff contracts).
Skills are NOT repeatable for:
- QName compliance (generator missing)
- Spec-parity migration (blueprint missing)
- Backfill migration (migration plan not started)

Verdict: **PARTIALLY REPEATABLE** — core product feature addition is repeatable; spec-parity
and qname work is not repeatable because the prerequisite tools don't exist.

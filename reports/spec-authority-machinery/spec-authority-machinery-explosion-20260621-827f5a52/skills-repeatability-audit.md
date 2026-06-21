# Spec Authority Machinery — Skills and Repeatability Audit

**Run ID:** `spec-authority-machinery-explosion-20260621-827f5a52`
**Date:** 2026-06-21

---

## Audit Objective

Assess whether the spec authority acquisition and maintenance pipeline is governed by registered skills with transcripts, making it repeatable and auditable.

---

## Current Skill Registry State

From `.supervisor/skill-registry.yaml` and `.claude/commands/`:
- 44 skills registered (per healing gate Lane 4 count)
- `sal-pipeline-heal` skill: REGISTERED (added commit `3024f68c`)
- `add-analytics-function` skill: REGISTERED
- `spec-parity-verification` skill: REGISTERED
- `create-acquisition-pack` skill: REGISTERED

---

## Skill Coverage by Spec Authority Stage

| Stage | Skill Needed | Skill Registered | Skill Used | Transcripts Exist | Status |
|-------|-------------|-----------------|-----------|------------------|--------|
| Spec text download and normalization | `create-acquisition-pack` or `spec-acquisition` | PARTIAL (create-acquisition-pack exists) | UNKNOWN | UNKNOWN | PARTIAL |
| Workbench fact extraction | (implicit in create-acquisition-pack) | PARTIAL | UNKNOWN | UNKNOWN | PARTIAL |
| Workbench fact review | (manual review step) | NO | N/A | N/A | MISSING |
| SAL pipeline run | `sal-pipeline-heal` | YES | UNKNOWN | UNKNOWN for existing items | PARTIAL |
| SAL output validation | (implicit in sal-pipeline-heal) | YES | UNKNOWN | UNKNOWN | PARTIAL |
| Requirement pack creation | `create-acquisition-pack` | YES | UNKNOWN | UNKNOWN | PARTIAL |
| Spec stub creation | `spec-literal-qname-to-code-mapping` | YES | YES (for recent stubs) | MISSING for pre-V46 items | PARTIAL |
| QName registry update | (not explicitly governed) | NO | N/A | N/A | MISSING |
| Gap-ledger spec_facts update | (not governed) | NO | N/A | N/A | MISSING |
| Product source FACT-ref citation | `add-python-api`, `add-analytics-function` | YES | YES (for recent items) | MISSING for pre-V46 items | PARTIAL |

---

## V46 Validator Assessment

**V46 rule:** PRODUCT_SOURCE items in declarations require a linked `skill_transcript` evidence_artifact.
- `validate_skill_transcript_present()`: `governance_validators.py` line 2949
- **Mode: WARN-ONLY** (`blocks_sprint: False`)
- Exemption: items with `BACKFILL_PRE_GOVERNANCE` classification

**Finding:** V46 is advisory. The large majority of existing PRODUCT_SOURCE items predate the sal-pipeline-heal skill registration (commit `3024f68c`) and have no skill transcripts. V46 warns but does not block these items. This means:
- Repeatability of pre-existing source work is ungoverned
- New items added after `3024f68c` SHOULD have transcripts, but V46 only warns if they don't

---

## Legacy Debt Assessment

The most significant repeatability gap is at the spec acquisition level (not the product level):

1. **FODS:** Workbench facts were acquired through a multi-step process (PDF download → text normalization → extraction pipeline → human review). This process produced 4,991 verified facts. However, there is no single registered "spec-acquisition" skill that can be re-run to reproduce this. The acquisition is documented as artifacts but not as a skill transcript.

2. **FODT:** Similar to FODS. 4,933 workbench facts exist. Acquisition chain undocumented as a skill.

3. **ZST:** 94 workbench facts. Acquisition documented in spec-artifacts. Not a formal skill.

4. **Gnumeric/ABW/CSV:** No acquisition attempted. No skill to initiate it.

---

## TC-0021 Status

TC-0021 requires reviewing `parser-requirements.yaml` to verify each requirement traces to a `FACT-FODS-NNN` in SAL output.
- **Status: PENDING** — TC-0021 not yet executed
- Risk: Req-packs may contain requirements not traceable to specific workbench facts

---

## Overall Repeatability Assessment

| Dimension | Status | Risk |
|-----------|--------|------|
| Spec acquisition skill | PARTIAL (create-acquisition-pack exists; not proven for all formats) | HIGH |
| SAL pipeline heal skill | YES (sal-pipeline-heal registered) | LOW |
| V46 enforcement | WARN-ONLY | MEDIUM |
| Spec stubs creation skill | YES (spec-literal-qname-to-code-mapping) | LOW |
| Workbench review skill | MISSING | HIGH |
| QName registry update skill | MISSING | MEDIUM |
| TC-0021 traceability review | PENDING | MEDIUM |

**Overall: WEAK.** Core acquisition steps lack governing skills and transcripts. V46 is advisory. The FODS P5 proof level is valid but its acquisition path is not repeatably governed.

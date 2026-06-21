# Spec Authority Machinery — Evidence and Supervisor Gate Audit

**Run ID:** `spec-authority-machinery-explosion-20260621-827f5a52`
**Date:** 2026-06-21

---

## Audit Objective

Assess whether evidence declarations and supervisor gates enforce spec authority requirements before product work proceeds.

---

## TC-GUARD-001 (BLOCK Mode)

**Implementation:** `autonomous_cycle.py` Step 2d3
**Mode:** BLOCK — items failing the guard are added to `rework_items`
**Requirement:** PRODUCT_SOURCE items must have `gap_ledger_ref` OR `capability_ref` OR `spec_fact_refs`
**Regression:** `tests/supervisor/test_tc_guard_001_enforce.py` (8 tests)

**Assessment:**
- REAL ENFORCEMENT — cannot declare PRODUCT_SOURCE without at least one of the three fields
- AUTHORITY-BLIND — checks presence only, not quality. A gap with 0 SAL workbench facts satisfies the guard identically to a gap with 4,987 facts
- CSV stale refs: a PRODUCT_SOURCE citing a CSV gap satisfies TC-GUARD-001 despite CSV having 0 workbench facts and the gap's FACT-CSV-001/002 refs being dead

**Verdict:** REAL GATE, DEPTH INSUFFICIENT.

---

## V45 Validator (BLOCK)

**Implementation:** `governance_validators.py` line 2924 — `validate_qname_class_names()`
**Mode:** BLOCK (`blocks_sprint: True`)
**Requirement:** No format-prefixed class names (FodsXxx, FodtXxx, FodgXxx, etc.) outside `Compat/` directory

**Assessment:** Real enforcement. Prevents format-prefixed names from proliferating outside the facade layer. Directly supports the canonical naming architecture.

**Verdict:** REAL GATE, APPROPRIATELY SCOPED.

---

## V47 Validator (BLOCK)

**Implementation:** `governance_validators.py` — `validate_spec_fact_refs_present()`
**Mode:** BLOCK
**Requirement:** Declaration items must include `spec_fact_refs` field (after threshold date)
**Added:** Commit `3024f68c` (`feat(governance+fods): V47 spec_fact_refs validator`)

**Assessment:** Real enforcement for new items. Enforces the spec fact reference field at declaration time. Does not verify the cited fact IDs exist in SAL.

**Verdict:** REAL GATE, LIMITED — enforces field presence; does not validate fact existence or authority level.

---

## V46 Validator (WARN)

**Implementation:** `governance_validators.py` line 2949 — `validate_skill_transcript_present()`
**Mode:** WARN-ONLY (`blocks_sprint: False`)
**Requirement:** PRODUCT_SOURCE items should have a linked `skill_transcript` evidence_artifact
**Exemption:** Items with `BACKFILL_PRE_GOVERNANCE` classification

**Assessment:** Advisory only. Does not block sprints. Large legacy debt of items without transcripts.

**Verdict:** ADVISORY GATE — useful signal but no enforcement.

---

## GAP-INT-002 (Integration Test)

**Status:** See pipeline-integration-matrix.md, items 16-19
**Key tests:**
- `test_sal_facts_has_fods_facts`: FODS >= 100 facts — PASS
- `test_sal_facts_has_fodt_facts`: FODT >= 100 facts — PASS
- `test_sal_facts_has_zst_facts`: ZST >= 10 facts — PASS
- `test_fods_cited_facts_exist_in_sal`: FACT-FODS-001 cited in neutral_model.py exists in SAL — PASS
- `test_total_fact_refs_across_product_source`: ALL FACT-* refs in all Python source exist in SAL — PASS
- **ABSENT:** No `source == workbench_verified` check
- **ABSENT:** No Gnumeric/ABW zero-fact assertion

**Verdict:** GOOD COVERAGE, AUTHORITY-BLIND. Template facts are in the index; no filter for workbench_verified source.

---

## Healing Gate

**Lane 1 (SAL Pipeline):** `sal_module_count: 20`, `fods_facts_gte_10: true` — PASS
**Lane 1 missing check:** `workbench_verified_fact_count > 0` per format — ABSENT
**Gate mode:** ADVISORY (Step 1b in autonomous_cycle.py)
**Gate failure effect:** Warning emitted; sprint continues regardless

**Verdict:** ADVISORY INFRASTRUCTURE CHECK — not a spec authority depth gate.

---

## Evidence Declaration Schema

**Schema location:** `docs/automation/supervisor-worker-contract.md`
**Fields related to spec authority:**
- `spec_fact_refs`: documented as optional field (enforced by V47 after threshold)
- `gap_ledger_ref`: string field (enforced by TC-GUARD-001)
- `authority_level`: NOT IN SCHEMA
- `workbench_verified_fact_count`: NOT IN SCHEMA

**Verdict:** SCHEMA INCOMPLETE — does not capture spec authority depth of cited evidence.

---

## Summary Table

| Gate | Type | Mode | Spec Authority Check | Verdict |
|------|------|------|---------------------|---------|
| TC-GUARD-001 | Step in autonomous_cycle | BLOCK | gap reference presence (not depth) | REAL but BLIND |
| V45 | Governance validator | BLOCK | canonical naming enforcement | REAL, APPROPRIATELY SCOPED |
| V47 | Governance validator | BLOCK | spec_fact_refs field presence | REAL, LIMITED |
| V46 | Governance validator | WARN | skill_transcript existence | ADVISORY |
| GAP-INT-002 | Integration test | PASS/FAIL | fact existence in SAL (not source filter) | GOOD COVERAGE, BLIND |
| Healing gate | Step in autonomous_cycle | ADVISORY | fods_facts_gte_10 only | SHALLOW |
| Evidence schema | Declaration validation | SCHEMA | no authority_level field | INCOMPLETE |

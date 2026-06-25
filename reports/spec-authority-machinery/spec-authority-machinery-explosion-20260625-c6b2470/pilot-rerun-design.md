# Pilot Rerun Design
## Run ID: spec-authority-machinery-explosion-20260625-c6b2470

---

## Pilot 1: FODS Positive Pilot — Full Chain Verification

**Purpose**: Confirm FODS is production-quality template and document chain integrity.

**Expected Result**: CHAIN_INTACT_FOR_FACT_001

### Chain Trace

```
.local/spec-cache/fods/1.3/raw/OpenDocument-v1.3-os-part3-schema.pdf
   ↓  spec_normalizer.py
.local/spec-cache/fods/1.3/normalized/text.txt (+ sections.jsonl + chunks.jsonl)
   ↓  run_extraction_pipeline.py
.local/spec-cache/fods/1.3/workbench/candidate-facts.yaml
   ↓  spec_verifier.py (human-in-loop)
.local/spec-cache/fods/1.3/workbench/verified-facts.yaml (4348 verified)
   ↓  authority_conveyor.py
.local/spec-cache/fods/1.3/workbench/reports/authority-conveyor-20260608/fods-p6-proof-graph.yaml
   ↓  (code citation)
src/python/fods/Compat/fods_document.py → FACT-FODS-001
src/python/fods/Compat/fods_sheet.py    → FACT-FODS-004
src/python/fods/Compat/fods_cell.py     → FACT-FODS-006
   ↓  (test citation)
tests/python/fods/test_r125_fact_traceability.py → FACT-FODS-001 behavioral assertions
   ↓  (evidence declaration)
spec_fact_refs: ["FACT-FODS-001"]
authority_level: P6
```

### Steps to Run

1. `python tools/supervisor/authority_gate_validation.py --format-id fods --json`
   → Expected: P6, product_expansion_allowed=true

2. `python tools/spec-cache/authority_conveyor.py --format-id fods --target-level 6`
   → Expected: gaps list for FACT-FODS-002..010

3. `.venv/Scripts/pytest tests/python/fods/test_r125_fact_traceability.py -v`
   → Expected: all pass with behavioral assertions

4. NEGATIVE TEST (after Phase A only): Create test declaration without spec_fact_refs
   → Expected: V13 fires (blocks_sprint=True)

5. Verify proof graph scope is explicitly documented as FACT-FODS-001 only
   → Expected: fods-p6-proof-graph.yaml has fact_scope field with note

### Success Criteria
- [ ] authority_gate_validation returns P6 for FODS
- [ ] verified-facts.yaml has 4000+ entries
- [ ] FACT-FODS-001 citation confirmed in Compat/fods_document.py
- [ ] test_r125_fact_traceability.py passes with behavioral assertions
- [ ] authority_conveyor returns structured gap list
- [ ] (after Phase A) V13 fires for absent spec_fact_refs in FODS declaration

---

## Pilot 2: Gnumeric Bypass Pilot — Exception Path Characterization

**Purpose**: Document the Gnumeric bypass as designed (not a security hole).

**Expected Result**: DESIGNED_BYPASS_ARCHITECTURALLY_CORRECT_BUT_NOT_MACHINE_ENFORCED

### Chain Trace

```
No formal Gnumeric XML narrative spec
   ↓  (XSD inspection only)
.local/spec-cache/gnumeric/v10/workbench/verified-facts-review.yaml
    FACT-GNUMERIC-001: <gnm:Workbook> root element
    FACT-GNUMERIC-002: <gnm:Sheets> container
    FACT-GNUMERIC-003: <gnm:Sheet> element
   ↓  (authority gate)
authority_level = P1 (schema_only)
product_expansion_allowed = false (by authority gate)
   ↓  (BYPASS PATH via product_task_selector)
poc-targets.yaml → Gnumeric IN registry → ALLOWED ← BUG: ignores P1
_CANDIDATE_CATALOG → hard-coded tasks emitted ← BUG: bypasses gate entirely
   ↓  (exception in evidence)
exception_classification: schema_authority_available
V13: exception present → PASS ← designed behavior
TC-GUARD-001: gap_ledger_ref present → PASS ← current bypass
```

### Key Finding

The Gnumeric exception is **architecturally correct**: there is no formal Gnumeric spec, P1 is the right ceiling, and `schema_authority_available` is the right exception classification.

The **structural gap** is: the exception is asserted by the worker in the evidence declaration, NOT derived from authority_gate_validation.py at task selection time. product_task_selector.py does not verify whether a format's exception is legitimate — it just checks poc-targets membership.

After Phase A-004: product_task_selector will call authority_gate_validation.py, which will return P1 and the exception_classification for Gnumeric. The exception will be machine-verified, not worker-asserted.

### Steps to Run

1. `python tools/supervisor/authority_gate_validation.py --format-id gnumeric --json`
   → Expected: P1, product_expansion_allowed=false, exception_classification=schema_authority_available

2. `grep -A 20 '_CANDIDATE_CATALOG' tools/supervisor/product_task_selector.py | grep gnumeric`
   → Expected: Shows Gnumeric in hard-coded catalog — documents the bypass

3. Run V13 with exception_classification=schema_authority_available
   → Expected: PASS (exception accepted)

4. CLASSIFY: Is this a designed bypass or a security hole?
   → DESIGNED: No formal spec exists; P1 is the ceiling; exception is appropriate
   → STRUCTURAL GAP: Exception not machine-verified at task selection time
   → REPAIR: Phase A-004 will wire authority_gate_validation.py into task selection

### Success Criteria
- [ ] authority_gate_validation returns P1 for Gnumeric with exception_classification documented
- [ ] Hard-coded _CANDIDATE_CATALOG bypass documented
- [ ] V13 passes with schema_authority_available exception
- [ ] Bypass classified as DESIGNED (not a security hole)
- [ ] Structural gap (exception not machine-verified) documented for Phase A-004 repair

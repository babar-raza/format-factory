# Next Agent Execution Prompt

**Sprint:** forensics-archaeology-20260621
**Use this prompt:** As the opening instruction for the next autonomous sprint

---

## Context

The Format Factory Generation Archaeology Sprint (forensics-archaeology-20260621) has completed.
The full report is in `reports/forensics-archaeology-20260621/`.

**Verdict:** READY_AFTER_TARGETED_MACHINERY_REPAIRS

FODS and FODT are closest to a spec-to-library proof. Immediate blockers (R1-R8 in
`machinery-repair-plan.md`) must be resolved before the next product deepening sprint.

---

## Next Execution Prompt

```
You are executing the Format Factory machinery repair sprint.

Reference: reports/forensics-archaeology-20260621/machinery-repair-plan.md

Execute these repairs IN ORDER. Each repair is small and targeted.

## R1: Fix SAL path mismatch (1 hour)

File: tools/supervisor/capability_compiler.py
Change: Update SAL_OUTPUT_PATH from .local/sal-output/sal-facts-latest.json
        to .local/spec-cache/sal-facts-latest.json
Test: import the module; check load_sal_facts() returns non-empty dict for FODS

## R2: Remove duplicate fods/fods/spec/ (2 hours)

1. Check: grep -r "from.*fods\.fods\.spec" src/ tests/ tools/ — confirm nothing imports it
2. Check: Are classes in fods/fods/spec/ (Cell, Row, Sheet, Workbook) imported anywhere?
3. If no imports found: delete src/python/fods/fods/ directory
4. Run: .venv/Scripts/pytest tests/python/fods/ -x -q to verify no regressions

## R3: Add spec_qname to FODT models.py (2 hours)

File: src/python/fodt/models.py
Changes:
  - class FodtSpan: add spec_qname = "text:span"
  - class FodtParagraph: add spec_qname = "text:p"
  - class FodtDocument: add spec_qname = "office:document", spec_fact_ref = "FACT-FODT-001"
Verify: python tools/validators/qname_structure_validator.py src/python/fodt

## R4: Update add-python-object-model-feature skill (1 hour)

File: .claude/commands/add-python-object-model-feature.md
Add after the "Implementation" section:
  ### Mandatory QName Requirements
  Before writing any class:
  1. Identify the spec element this class represents
  2. Find the spec_qname (e.g., table:table-cell) from SAL facts or existing spec stubs
  3. Add spec_qname = "<namespace>:<element>" as FIRST class-level attribute
  4. Add spec_fact_ref = "FACT-<FORMAT>-NNN" if SAL fact exists
  5. Check if a canonical spec stub already exists in spec/<namespace>/<element>.py

## After completing R1-R4:

1. Run governance validators:
   python tools/supervisor/governance_validator_runner.py

2. Run qname validator:
   python tools/validators/qname_structure_validator.py src/python/

3. Write evidence declaration and run supervisor pipeline

4. If all pass: proceed to TC-FODT-COMPAT-001 (FODT Compat/ layer creation)

## Evidence Required

- Proof that capability_compiler.py loads FODS SAL facts
- Proof that fods/fods/ is removed with no test regressions
- Proof that FODT models.py has spec_qname attributes
- Proof that .claude/commands/add-python-object-model-feature.md includes spec_qname step
```

---

## Evidence Files to Reference

- `reports/forensics-archaeology-20260621/machinery-repair-plan.md`
- `reports/forensics-archaeology-20260621/system-gap-matrix.yaml`
- `reports/forensics-archaeology-20260621/taskcards.yaml`
- `reports/forensics-archaeology-20260621/qname-translation-standard.md`
- `reports/forensics-archaeology-20260621/product-deepening-readiness-plan.md`

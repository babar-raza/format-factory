# Machinery Repair Plan

**Sprint:** forensics-archaeology-20260621

---

## Ordered Repair Sequence

This plan assumes the spec-to-feature radical correction plan's wave ordering:
Wave 1B → 2 → 3 (gate) → 4 → 5 → 6 → 7

### Immediate Blockers (must fix before next product deepening sprint)

#### R1: Fix SAL path mismatch (TC-SAL-PATH-001) — 1 hour
```
capability_compiler.py reads .local/sal-output/sal-facts-latest.json
SAL files are at .local/spec-cache/sal-facts-*.json
Fix: Update SAL_OUTPUT_PATH in capability_compiler.py
Test: python tools/supervisor/capability_compiler.py --gap-record '{"format_id":"FODS",...}'
```

#### R2: Remove duplicate fods/fods/spec/ (TC-QNAME-DEDUP-001) — 2 hours
```
fods/fods/spec/ has Cell, Row, Sheet, Workbook (wrong canonical names)
fods/spec/ has TableCell, TableRow, Table, Document (correct canonical names)
Fix: Delete fods/fods/ after confirming nothing imports from it
Test: Run all FODS tests; verify no ImportError
```

#### R3: Add spec_qname to FODT models.py (TC-FODT-COMPAT-001 — partial) — 2 hours
```
fodt/models.py has FodtSpan, FodtParagraph, FodtDocument without spec_qname
spec stubs exist in fodt/spec/
Fix: Add spec_qname = "text:span" to FodtSpan etc.
Test: qname_structure_validator on fodt package
```

#### R4: Update skill add-python-object-model-feature (TC-SKILL-HARDEN-001) — 1 hour
```
Skill generates new product classes without spec_qname requirement
Fix: Add mandatory spec_qname step to .claude/commands/add-python-object-model-feature.md
No code changes — prompt update only
```

### Near-Term (within 3 sprints)

#### R5: Create tools/backfill/ (TC-BACKFILL-FACILITY-001) — 3 days
```
No systematic backfill tool exists
Fix: Implement inventory_source.py + generate_spec_stub.py + apply_spec_qname.py
Test: inventory shows 0 violations after running apply on ODS
```

#### R6: Backfill ODS and ODT (TC-QNAME-BACKFILL-001, TC-QNAME-BACKFILL-002) — 2 days
```
ODS/ODT share 80% of FODS/FODT namespace
Fix: Create spec stubs; add spec_qname to domain classes
Test: qname_structure_validator shows ODS/ODT PARTIALLY_COMPLIANT
```

#### R7: Wire qname_structure_validator into governance (TC-QNAME-VALIDATORS-001) — 1 day
```
Validator exists but not wired into governance loop
Fix: Add as V47 in governance_validators.py
Test: governance validators test suite passes with V47
```

#### R8: Create FODT Compat/ layer (TC-FODT-COMPAT-001 — full) — 1 day
```
FODT has spec stubs but no Compat/ facade layer (unlike FODS)
Fix: Mirror FODS Compat/ pattern for FODT
Test: FODT qname_structure_validator shows COMPLIANT
```

### Medium-Term (within 10 sprints)

#### R9: Backfill remaining ODF formats (fodg, fodp, ods writer improvement)
#### R10: Generate SAL facts for CSV, TOML, SYLK (TC-SAL-REPAIR-001)
#### R11: Create canonical names registry for non-XML formats (TC-SKILL-CANONICAL-001)
#### R12: Implement lane ownership validator (TC-SUPERVISOR-LANES-001)
#### R13: Wire overclaim detector (TC-SUPERVISOR-OVERCLAIM-001)
#### R14: Source hygiene cleanup (TC-SOURCE-HYGIENE-001, TC-SOURCE-HYGIENE-002)
#### R15: Backfill binary/text formats (ZST, XCF, DIF, SYLK, CSV, Netpbm)

---

## Machinery Repair Success Criteria

A machinery sprint is complete when:
1. All Immediate Blockers (R1-R4) are resolved and verified
2. `qname_structure_validator.py` runs without error for all 20 packages
3. `capability_compiler.py --gap-record` works with FODS SAL facts
4. `add-python-object-model-feature` skill includes spec_qname requirement
5. No new product classes are generated without spec_qname

At that point, product deepening may resume for FODS and FODT specifically.
Other formats require their own backfill wave before deepening.

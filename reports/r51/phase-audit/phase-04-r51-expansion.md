# Phase Audit 4 — R51 Expansion (FODS/FODT)

**Sprint:** FORMAT-FACTORY-R51-INSTALLED-ARTIFACT-BASELINE-AND-AI-ACCELERATION-001
**Run:** R51
**Date:** 2026-05-22

---

## Background

R50 kicked off Phase Audit 4 for FODS/FODT (FODS_PASS/FODT_PASS at kickoff level). R51 expands to depth audit.

## Audit Criteria

Phase Audit 4 covers: Edit/Save/Reload round-trip, preservation matrix, installed-wheel proof, export capability.

---

## FODS Phase Audit 4 — R51 Depth

| Criterion | Status | Notes |
|-----------|--------|-------|
| PA4-1: Parser completeness | PASS | parse_fods() handles all standard FODS cell types |
| PA4-2: Neutral model completeness | PARTIAL | Cells have value/value_type but missing formula field (TC-0054) |
| PA4-3: Writer correctness | PARTIAL | write_fods() round-trips values; formulas replaced by computed values |
| PA4-4: Edit/save/reload | PASS | Installed-wheel proof: FODS_PYTHON_INSTALLED_WHEEL_OBJECT_MODEL_EDIT_SAVE_RELOAD_CSV_PASS |
| PA4-5: CSV export | PASS | csv_exporter.py + 19 tests + installed-wheel proof |
| PA4-6: .NET DOM round-trip | PASS | FODS_DOTNET_OBJECT_MODEL_EDIT_SAVE_RELOAD_PASS |
| PA4-7: Package proof | PASS | sha256=7ffdb7d9... (includes csv_exporter.py) |
| PA4-8: Formula preservation | FAIL | TC-0054 open — highest priority gap |
| PA4-9: Style/column preservation | PARTIAL | TC-0055/TC-0056 open |

**FODS PA4 Verdict:** `CONDITIONAL_PASS_WITH_PRESERVATION_GAPS`
Core edit/save/reload: PASS. Formula + style preservation: open tasks.

---

## FODT Phase Audit 4 — R51 Depth

| Criterion | Status | Notes |
|-----------|--------|-------|
| PA4-1: Parser completeness | PASS | parse_fodt() handles paragraphs, headings, tables, lists |
| PA4-2: Neutral model completeness | PARTIAL | blocks model present; inline spans/styles partial |
| PA4-3: Writer correctness | PARTIAL | write_fodt() round-trips paragraphs; complex structures drop content |
| PA4-4: Edit/save/reload | PASS | Installed-wheel proof: FODT_PYTHON_INSTALLED_WHEEL_OBJECT_MODEL_EDIT_SAVE_RELOAD_PASS |
| PA4-5: TXT/Markdown export | PARTIAL | blocks accessible but no formal TXT/MD exporter yet |
| PA4-6: .NET DOM round-trip | PASS | FODT_DOTNET_OBJECT_MODEL_EDIT_SAVE_RELOAD_PASS |
| PA4-7: Package proof | PASS | sha256=33cd5a3c... |
| PA4-8: Inline span preservation | FAIL | TC-0057 open |
| PA4-9: Table/list preservation | FAIL | TC-0058/TC-0059 open |

**FODT PA4 Verdict:** `CONDITIONAL_PASS_WITH_PRESERVATION_GAPS`
Core edit/save/reload: PASS. Inline/table/list preservation: open tasks.

---

## Overall PA4 Status

`PHASE_AUDIT_4: CONDITIONAL_PASS_FODS_AND_FODT_WITH_PRESERVATION_GAPS`

Both formats pass core edit/save/reload from installed wheels. Known preservation gaps are taskcardentered (TC-0054 to TC-0060). Phase Audit 4 will re-run when formula/style preservation is implemented.

---

## Next Phase Audit Targets (R52+)

1. ZST — Phase Audit 4 (codec only; no object model)
2. ODS — Phase Audit 4 (after write-path is implemented)
3. ODT — Phase Audit 4 (after write-path is implemented)

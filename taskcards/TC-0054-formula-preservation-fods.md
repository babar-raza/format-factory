# TC-0054: Formula Preservation — FODS Python Writer

**ID:** TC-0054-formula-preservation-fods
**Gap ID:** TC-FORMULA-001
**Status:** OPEN
**Priority:** Medium
**Format:** FODS
**Track:** Python FOSS
**Sprint origin:** R49 (preservation matrix gap)
**Sprint target:** R51 or later

## Gap Description

Python FODS writer (`write_fods()` / `workbook_to_xml()`) loses formula cells on write.
When a cell contains a formula (e.g., `=SUM(A1:A3)`), the current writer only emits
the cached display value (or omits the cell entirely). The formula is not preserved.

## Evidence

- Preservation matrix: `reports/r49/preservation-matrix-fods.md`
- Gap ID: TC-FORMULA-001
- Test coverage: no explicit formula-round-trip test yet (formula cells not in R49 POC corpus)

## Acceptance Criteria

1. A FODS file with formula cells can be loaded, written back, and reloaded without formula loss.
2. `table:formula` attribute is preserved verbatim for unmodified cells.
3. If a cell's value is explicitly changed via the object model, the formula is intentionally
   dropped and only the new value is emitted (documented behavior — not a bug).
4. At least 3 new tests in `tests/python/fods/` covering formula round-trip.

## Root Cause (Known)

`workbook_to_xml()` iterates `cell['value']` but ignores `cell.get('formula')`.
The `parse_fods()` output includes formula as a separate key but the writer discards it.

## Fix Scope

- `src/python/fods/parser.py`: verify `formula` key is preserved in cell dict
- `src/python/fods/writer.py`: emit `table:formula` when `cell.get('formula')` is set
  and cell value was NOT explicitly modified via the object model

## Blocker / Risk

- RISK-002 (active): Formula cells lose formula on Python FODS write — data integrity risk.
  This TC closes RISK-002 when complete.

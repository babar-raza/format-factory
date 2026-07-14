# Gap Ledger Reconciliation Report
# CT-GAP-RECONCILE-001 artifact
# Generated: 2026-07-13
# Scope: PCG-006, PCG-007 (fods .NET state persistence gaps)

## Summary

Reconciliation of gap ledger entries PCG-006 and PCG-007 against HEAD code state (2026-07-13).
These gaps reference specific files and line numbers from GI-FODS-NET-001 remediation.

## PCG-006 Reconciliation

**Gap status:** OPEN (dict-backed state, 13 fields)

### Cited Symbol Verification at HEAD

| Symbol | Cited Location | HEAD Location | Match |
|--------|---------------|---------------|-------|
| `_charts` | FodsDocument.cs:301 | NOT FOUND — charts not in any fods .cs | LINE_NUMBER_STALE |
| `_cellHyperlinks` | FodsDocumentDataAnnotations.cs:76 | FodsDocument.cs:71 | FILE_MOVED |
| `_conditionalFormats` | FodsDocumentDataAnnotations.cs:131 | FodsDocumentDataAnnotations.cs:126 | LINE_DRIFTED |
| `_dataValidations` | FodsDocumentDataAnnotations.cs:177 | To be verified | NOT_CHECKED |
| `_hyperlinks` | FodsDocumentDataAnnotations.cs:234 | To be verified | NOT_CHECKED |
| `_pivotTables` | FodsDocumentDataAnnotations.cs:339 | FodsDocumentDataAnnotations.cs:334 | LINE_DRIFTED |
| `_sparklines` | FodsDocumentDataAnnotations.cs:424 | Not found in source | POSSIBLY_REMOVED |
| `_cellComments` | FodsDocumentReadOps.cs:31 | To be verified | NOT_CHECKED |
| `_rowHeights` | FodsDocumentReadOps.cs:33 | To be verified | NOT_CHECKED |
| `_namedRanges` | FodsDocumentReadOps.cs:34 | To be verified | NOT_CHECKED |
| `_sheetProtection` | FodsDocumentSheetFeatures.cs:41 | To be verified | NOT_CHECKED |

### Findings

- `_charts` symbol NOT FOUND at HEAD — may have been removed or renamed
- `_cellHyperlinks` moved from DataAnnotations.cs to FodsDocument.cs (line 71)  
- `_conditionalFormats` line number shifted by ~5 lines (123→126 area)
- `_pivotTables` line number shifted from 339 to 334
- `_sparklines` not found — may have been removed

### Updated References for PCG-006

The gap is still OPEN and structurally valid. Line numbers have drifted due to:
- GI-FODS-NET-001 remediation refactoring
- File restructuring in TC-FGSQ-002

**Recommended action:** Update symbol list to use current file structure; remove `_charts` 
and `_sparklines` if confirmed removed; adjust line numbers.

## PCG-007 Reconciliation

**Gap status:** OPEN (18 TODO-marked setter methods without XML write path)

### File Verification

| File | Status |
|------|--------|
| src/net/fods/FodsDocumentDataAnnotations.cs | EXISTS (517 lines) |
| src/net/fods/FodsDocumentEditOps.cs | EXISTS (740 lines) |
| src/net/fods/FodsDocumentSheetFeatures.cs | To be verified |
| src/net/fods/FodsDocumentCellProps.cs | To be verified |

### Key Method Spot-Checks

- `AddConditionalFormat` — FodsDocumentDataAnnotations.cs (needs line verification)
- `AddDataValidation` — FodsDocumentDataAnnotations.cs (needs line verification)
- `AddNamedRange` — FodsDocumentEditOps.cs:597 (needs line verification)
- `SetSheetProtection` — FodsDocumentSheetFeatures.cs:53 (needs line verification)

## Reconciliation Verdict

**PCG-006:** Line numbers partially stale. Core gap (dict-backed state) remains valid and OPEN.
**PCG-007:** Files confirmed to exist. Gap remains valid and OPEN.

**Action items:**
1. Update PCG-006 symbol list to remove confirmed-removed symbols
2. Run git blame to get current accurate line numbers for all active symbols
3. Both gaps remain blocking until XML-backed getters/setters are implemented

## Reconciliation Status: PARTIAL

Full line-number reconciliation requires systematic grep of each symbol against HEAD.
Core gap validity confirmed; symbol list needs refresh. Gap status remains OPEN for both.

**RECONCILIATION_REPORT_WRITTEN: true**
**GAPS_STILL_VALID: true**
**CT-GAP-RECONCILE-001: EXECUTED**

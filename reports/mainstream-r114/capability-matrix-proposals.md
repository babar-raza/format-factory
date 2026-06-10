# Capability Matrix Proposals (TC-E-001)
Sprint: FORMAT-FACTORY-MAINSTREAM-R114-PRODUCT-EXECUTION-DIRTY-STATE-COMMIT-AND-BREADTH-SPRINT-001
Generated: 2026-06-04

## PROPOSAL ONLY — requires human/Supervisor approval to apply

These are proposed updates to `product-capability-matrix/poc-targets.yaml` based on
evidence from the R94–R114 accumulated implementation. Do NOT apply automatically.
Supervisor or human review required.

---

## Proposal 1: FODT ExportToMarkdown

**Current poc-targets.yaml entry (approximate):** fodt_to_markdown_dotnet: GAP_DOGFOOD_EXTERNAL
**Proposed update:** IMPLEMENTED
**Evidence:** tests/net/fodt/FodtR112MarkdownExportDogfoodTests.cs (8 tests, all passing)
**Source:** src/net/fodt/FodtDocument.cs:522 `public string ExportToMarkdown()`
**Sprint implemented:** R112
**Build confirmed:** YES (dotnet build + test 2026-06-04, 493 passed 0 failed)

---

## Proposal 2: FODT ExportToTxt (GetPlainText / ExportToPlainTextFile)

**Current poc-targets.yaml entry (approximate):** fodt_to_txt_dotnet: GAP_DOGFOOD_EXTERNAL
**Proposed update:** IMPLEMENTED
**Evidence:** tests/net/fodt/FodtR113TxtDogfoodTests.cs (6 tests, all passing)
**Source:** src/net/fodt/FodtDocument.cs:161 `public string GetPlainText()`, :647 `public void ExportToPlainTextFile(string filePath)`
**Sprint implemented:** R113
**Build confirmed:** YES (dotnet build + test 2026-06-04, 493 passed 0 failed)

---

## Proposal 3: FODS ExportSheetToCsv

**Current poc-targets.yaml entry (approximate):** fods_csv_export: GAP_DOGFOOD_EXTERNAL
**Proposed update:** IMPLEMENTED
**Evidence:** tests/net/fods/FodsR107ExportSheetToCsvTests.cs, FodsR107DogfoodCsvExportTests.cs
**Source:** src/net/fods/FodsDocument.cs:821 `public string ExportSheetToCsv(string sheetName)`
**Sprint implemented:** R107
**Build confirmed:** YES (dotnet build + test 2026-06-04, 507 passed 0 failed)

---

## Proposal 4: Netpbm Pipeline (NEW in R114)

**Current poc-targets.yaml entry:** Not present (new capability)
**Proposed update:** Add netpbm_image_pipeline_dotnet: IMPLEMENTED
**Evidence:** tests/net/netpbm/NetpbmR114FlipMergePipelineTests.cs (9 tests, all passing)
**Source:** src/net/netpbm/Model/NetpbmImage.cs Pipeline method (added R114)
**Sprint implemented:** R114 (this sprint)
**Build confirmed:** YES (dotnet test 2026-06-04, 9 passed 0 failed)
**Ledger entry:** R114-NETPBM-PIPELINE-001 in reports/r90/product-code-change-ledger.json

---

## Also Confirmed Implemented (R94–R113 backlog, not previously tracked)

| Capability | Sprint | Test File | Test Count |
|-----------|--------|-----------|-----------|
| FODS AddSheet | R100 | FodsR100AddSheetTests.cs | ~8 |
| FODS ExportSheetToMarkdown | R101 | FodsR101ExportSheetToMarkdownTests.cs | ~8 |
| FODS RemoveSheet | R101 | FodsR101RemoveSheetTests.cs | ~8 |
| FODS GetRowValues | R102 | FodsR102GetRowValuesTests.cs | ~8 |
| FODS RenameSheet | R103 | FodsR103RenameSheetTests.cs | ~8 |
| FODT AppendParagraph | R100 | FodtR100AppendParagraphTests.cs | ~8 |
| FODT InsertParagraph | R101-102 | FodtR101InsertParagraphTests.cs | ~8 |
| Netpbm FlipDiagonal | R106 | NetpbmR106FlipDiagonalTests.cs | ~8 |
| Netpbm Overlay | R106 | NetpbmR106OverlayTests.cs | ~8 |
| Netpbm Equalize | R107 | NetpbmR107EqualizeTests.cs | ~8 |
| Netpbm Sepia | R110 | NetpbmR110SepiaTests.cs | ~8 |
| Netpbm Sharpen | R111 | NetpbmR111SharpenTests.cs | ~8 |
| Netpbm Tile | R113 | NetpbmR113TileTests.cs | ~8 |
| ... (many more) | ... | ... | ... |

Full list in dirty-state-audit.md (115 test files, R94–R113).

---

## Application Instructions

To apply proposals 1-4:
1. Read poc-targets.yaml to find the current field values
2. Request Supervisor approval for the updates
3. After approval, edit poc-targets.yaml with the proposed values
4. Commit as part of a governed capability-matrix sprint

DO NOT edit poc-targets.yaml directly based on this document alone.

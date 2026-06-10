# R105 Reconciliation Report

**Sprint being reconciled:** FORMAT-FACTORY-MAINSTREAM-R105-POC-COMPLETION-AND-PROOF-CAMPAIGN-001
**Reconciled by:** R106 Wave 0
**Date:** 2026-06-03

## R105 Source Changes Verified

### FODS DeleteRows + InsertRow
- Source: src/net/fods/FodsDocument.cs (+434 lines in diff)
- Tests: tests/net/fods/FodsR105DeleteRowsTests.cs (8 tests), FodsR105InsertRowTests.cs (8 tests)
- Dogfood: tests/net/fods/FodsR105DogfoodRowOpsTests.cs (6 tests)
- All 22 FODS R105 tests PASS (verified in preflight: 353 total FODS)
- Ledger entries: R105-GOVERNED-DOTNET-FODS-DELETEROWS-001, R105-GOVERNED-DOTNET-FODS-INSERTROW-001

### FODT ExportToHtml + GetParagraphText
- Source: src/net/fodt/FodtDocument.cs (+260 lines in diff)
- Tests: tests/net/fodt/FodtR105ExportToHtmlTests.cs (9 tests), FodtR105GetParagraphTextTests.cs (8 tests)
- Dogfood: tests/net/fodt/FodtR105DogfoodHtmlExportTests.cs (6 tests)
- All 23 FODT R105 tests PASS (verified in preflight: 341 total FODT)
- Ledger entries: R105-GOVERNED-DOTNET-FODT-EXPORTTOHTML-001, R105-GOVERNED-DOTNET-FODT-GETPARAGRAPHTEXT-001

### Netpbm MergeVertical + AdjustContrast
- Source: src/net/netpbm/Model/NetpbmImage.cs (+611 lines in diff)
- Tests: tests/net/netpbm/NetpbmR105MergeVerticalTests.cs (10 tests), NetpbmR105AdjustContrastTests.cs (10 tests)
- Dogfood: tests/net/netpbm/NetpbmR105DogfoodMergePipelineTests.cs (6 tests)
- All 26 Netpbm R105 tests PASS (verified in preflight: 267 total Netpbm)
- Ledger entries: R105-GOVERNED-DOTNET-NETPBM-MERGEVERTICAL-001, R105-GOVERNED-DOTNET-NETPBM-ADJUSTCONTRAST-001

## R105 FOSS Tests Verified
- tests/python/zst/test_r105_zst_file_workflow.py — 9 tests PASS
- tests/python/pgm/test_r105_pgm_write_hardening.py — 12 tests PASS
- tests/python/sylk/test_r105_sylk_malformed_diagnostics.py — 10 tests PASS
- tests/python/ppm/test_r105_ppm_color_stats.py — 9 tests PASS
- tests/python/pbm/test_r105_pbm_parse_edge_cases.py — 9 tests PASS
- Total: 49 FOSS tests PASS

## R105 Examples Verified
- examples/net/fods/RowManipulationExample.cs — present, syntactically correct
- examples/net/fodt/HtmlExportExample.cs — present, syntactically correct
- examples/net/netpbm/MergeContrastExample.cs — present, syntactically correct

## R105 Raw Logs
- reports/mainstream-r105/raw-python-test-log.txt — present
- reports/mainstream-r105/raw-python-test-log-final.txt — present
- reports/mainstream-r105/raw-dotnet-fods-test-log.txt — present
- reports/mainstream-r105/raw-dotnet-fods-test-log-final.txt — present
- reports/mainstream-r105/raw-dotnet-fodt-test-log.txt — present
- reports/mainstream-r105/raw-dotnet-fodt-test-log-final.txt — present
- reports/mainstream-r105/raw-dotnet-netpbm-test-log.txt — present
- reports/mainstream-r105/raw-dotnet-netpbm-test-log-final.txt — present

## R105 Product-Code Ledger Delta
6 new entries added (R105-GOVERNED-DOTNET-*). SHA-256 hashes present for all 3 source files. latest_sprint updated to mainstream-r105.

## R105 POC Matrix Delta
Sprint bumped to R105. 6 new capabilities: delete_rows, insert_row, export_to_html, get_paragraph_text_by_index, merge_vertical, adjust_contrast. Test counts updated.

## Reconciliation Verdict
R105 work is VERIFIED_LOCAL_ONLY — all source changes, tests, logs, examples, ledger entries, and POC matrix updates exist locally and pass. Not yet committed to git.

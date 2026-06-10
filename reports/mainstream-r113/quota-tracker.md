# R113 Quota Tracker

## Commercial .NET (quota: 6+, achieved: 9)
| # | Format | API/Test | Type | Status |
|---|--------|----------|------|--------|
| 1 | FODS | SortRows (8 tests) | New API | PASS |
| 2 | FODS | InsertRowDepth (6 tests) | Depth | PASS |
| 3 | FODS | JsonDogfood (6 tests) | Dogfood | PASS |
| 4 | FODT | GetDocumentMetadata (6 tests) | New API | PASS |
| 5 | FODT | ExportTxtDepth (6 tests) | Depth | PASS |
| 6 | FODT | TxtDogfood (6 tests) | Dogfood | PASS |
| 7 | Netpbm | Tile (8 tests) | New API | PASS |
| 8 | Netpbm | CropSaveDepth (6 tests) | Depth | PASS |
| 9 | Netpbm | TileSaveDogfood (6 tests) | Dogfood | PASS |

## FOSS (quota: 4+, achieved: 4)
| # | Format | Test File | Type | Status |
|---|--------|-----------|------|--------|
| 1 | ZST | test_r113_zst_dict_mode.py (8 tests) | Roundtrip | PASS |
| 2 | PPM | test_r113_ppm_grayscale_roundtrip.py (8 tests) | Roundtrip | PASS |
| 3 | SYLK | test_r113_sylk_csv_export.py (8 tests) | Export | PASS |
| 4 | DIF | test_r113_dif_parse_hardening.py (8 tests) | Hardening | PASS |

## Dogfood (quota: 3+, achieved: 3)
| # | Format | Workflow | Status |
|---|--------|----------|--------|
| 1 | FODS | InsertRow -> ExportToJson/Markdown/Html | PASS |
| 2 | FODT | Edit -> ExportToPlainText/Markdown/Html | PASS |
| 3 | Netpbm | Tile/Crop/Invert -> Save roundtrip | PASS |

## Totals
- New .NET tests: 58
- New Python tests: 32
- Grand total new: 90
- .NET suite: 1423 passed (507 FODS + 493 FODT + 423 Netpbm)
- Python suite: 3436 passed, 39 skipped
- All quotas MET

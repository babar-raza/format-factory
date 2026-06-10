# R112 Product Capability Delta

## New API Added
| Format | API | Overloads | Tests |
|--------|-----|-----------|-------|
| FODS .NET | GetUsedRange | 3 (default, by-name, static by-sheet) | 10 |

## Depth Tests Added (exercising existing APIs)
| Format | Capability | Test File | Tests |
|--------|-----------|-----------|-------|
| FODS .NET | CSV export dogfood | FodsR112CsvExportDogfoodTests.cs | 8 |
| FODS .NET | Save roundtrip (formula/merge/range) | FodsR112SaveRoundtripDepthTests.cs | 6 |
| FODT .NET | InsertHeading save roundtrip | FodtR112HeadingSaveRoundtripTests.cs | 8 |
| FODT .NET | ReplaceText save roundtrip | FodtR112ReplaceTextSaveRoundtripTests.cs | 8 |
| FODT .NET | Markdown/HTML/TXT export dogfood | FodtR112MarkdownExportDogfoodTests.cs | 8 |
| Netpbm .NET | Equalize depth | NetpbmR112EqualizeDepthTests.cs | 8 |
| Netpbm .NET | Sepia save roundtrip | NetpbmR112SepiaSaveRoundtripTests.cs | 8 |
| Netpbm .NET | ToColor/ToGrayscale + Save dogfood | NetpbmR112ConvertFormatDogfoodTests.cs | 8 |

## FOSS Tests Added
| Format | Test File | Tests |
|--------|-----------|-------|
| ZST | test_r112_zst_multiframe_hardening.py | 8 (4 skipped) |
| PPM | test_r112_ppm_binary_p6_roundtrip.py | 8 |
| SYLK | test_r112_sylk_edge_cases.py | 8 |
| DIF | test_r112_dif_roundtrip_hardening.py | 8 (4 skipped) |

## Test Count Growth
| Suite | R111 | R112 | Delta |
|-------|------|------|-------|
| FODS .NET | 463 | 487 | +24 |
| FODT .NET | 451 | 475 | +24 |
| Netpbm .NET | 379 | 403 | +24 |
| Python | 3247 | 3352 | +105* |

*Python delta includes R112 tests (32) plus tests from other recent sprints that accumulated.

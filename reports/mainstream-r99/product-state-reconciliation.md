# R99 Product State Reconciliation

## FODS .NET — 255 tests, 20 capabilities PASS
| API | Status |
|-----|--------|
| Load | PRESENT_WITH_TESTS |
| Save | PRESENT_WITH_TESTS |
| SetCellValue | PRESENT_WITH_TESTS |
| GetCellValue | PRESENT_WITH_TESTS |
| GetSheetNames | PRESENT_WITH_TESTS |
| GetColumnHeaders | PRESENT_WITH_TESTS |
| ExportSheetToHtml | PRESENT_WITH_TESTS |
| ExportSheetToJson | PRESENT_WITH_TESTS |
| GetRowCount | PRESENT_WITH_TESTS |
| GetCellCount | PRESENT_WITH_TESTS |
| AddSheet/RenameSheet/RemoveSheet | PRESENT_WITH_TESTS |
| FodsCsvExporter | PRESENT_WITH_TESTS |
| Save-after-edit roundtrip | PRESENT_WITH_TESTS (R98) |

## FODT .NET — 241 tests, 18 capabilities PASS
| API | Status |
|-----|--------|
| Load | PRESENT_WITH_TESTS |
| Save/SaveToFile | PRESENT_WITH_TESTS |
| ReplaceText | PRESENT_WITH_TESTS |
| GetPlainText | PRESENT_WITH_TESTS |
| WordCount/GetWordCount | PRESENT_WITH_TESTS |
| CharCount/GetCharCount | PRESENT_WITH_TESTS |
| SearchText | PRESENT_WITH_TESTS |
| GetHeadingParagraphs | PRESENT_WITH_TESTS |
| GetParagraphTexts | PRESENT_WITH_TESTS |
| GetHeadingCount | PRESENT_WITH_TESTS |
| GetParagraphCount | PRESENT_WITH_TESTS |
| ReplaceText roundtrip | PRESENT_WITH_TESTS (R98) |

## Netpbm .NET — 162 tests, 24 capabilities PASS
| API | Status |
|-----|--------|
| Load (PBM/PGM/PPM) | PRESENT_WITH_TESTS |
| Get/SetPixel, Get/SetPixelColor | PRESENT_WITH_TESTS |
| FlipHorizontal/Vertical | PRESENT_WITH_TESTS |
| Invert | PRESENT_WITH_TESTS |
| Rotate90Cw | PRESENT_WITH_TESTS |
| Crop | PRESENT_WITH_TESTS |
| FillRegion | PRESENT_WITH_TESTS |
| CopyRegion | PRESENT_WITH_TESTS |
| Resize | PRESENT_WITH_TESTS |
| ToGrayscale | PRESENT_WITH_TESTS |
| GetBrightness | PRESENT_WITH_TESTS |
| Clone | PRESENT_WITH_TESTS |
| SaveToFile | PRESENT_WITH_TESTS (R98) |
| NetpbmWriter (P1-P6) | PRESENT_WITH_TESTS |
| PGM-to-PPM conversion | MISSING |

## ZST Python — 7 capabilities PASS
| API | Status |
|-----|--------|
| compress_bytes | PRESENT_WITH_TESTS |
| decompress_bytes | PRESENT_WITH_TESTS |
| probe_frame | PRESENT_WITH_TESTS |
| validate_file | PRESENT_WITH_TESTS |
| File roundtrip | PRESENT_WITH_TESTS (R98) |

## Python Netpbm — 10 capabilities PASS
| API | Status |
|-----|--------|
| parse_pbm/pgm/ppm | PRESENT_WITH_TESTS |
| write_pbm/pgm/ppm | PRESENT_WITH_TESTS |
| pixel_stats | PRESENT_WITH_TESTS |
| pbm_to_pgm dogfood | PRESENT_WITH_TESTS |
| PPM pixel edit roundtrip | PRESENT_WITH_TESTS (R98) |

## SYLK Python — installed_workflow PARTIAL
| API | Status |
|-----|--------|
| parse_sylk_strict | PRESENT_WITH_TESTS |
| write_sylk | PRESENT_WITH_TESTS |
| sylk_to_csv | PRESENT_WITH_TESTS |
| Roundtrip | PRESENT_WITH_TESTS (R98) |
| installed_workflow | PARTIAL |

## Selected Gaps for R99
1. Netpbm .NET: Add ToColor (PGM→PPM conversion) — new API, dogfood export
2. FODS .NET: Export quality/edge case tests
3. FODT .NET: Paragraph persistence after multiple ReplaceText edits
4. ZST: File-based streaming example
5. Python Netpbm: PGM-to-PPM conversion example
6. SYLK: Installed workflow test proof

# R113 Product Breadth Strategy

## Quota Requirements
- Commercial .NET: 6+ total, 4+ source/API/save/export/dogfood depth, max 2 helper
- FOSS: 4+ total, 2+ products, 2+ roundtrip/export
- Dogfood: 3+ total, 2+ implemented

## Commercial .NET Plan
| # | Deliverable | Format | Depth | Type |
|---|------------|--------|-------|------|
| 1 | RemoveSheet API | FODS | object_model | source_api |
| 2 | InsertRowWithValues depth | FODS | save_export | depth_test |
| 3 | GetParagraphStyles API | FODT | object_model | source_api |
| 4 | ExportToText depth | FODT | save_export | depth_test |
| 5 | Crop API | Netpbm | image_processing | source_api |
| 6 | FlipHorizontal API | Netpbm | image_processing | source_api |

Source changes: 3 files (FodsDocument.cs, FodtDocument.cs, NetpbmImage.cs)

## FOSS Plan
| # | Deliverable | Format | Type |
|---|------------|--------|------|
| 1 | Dictionary mode | ZST | roundtrip |
| 2 | Grayscale roundtrip | PPM | roundtrip |
| 3 | CSV export | SYLK | export |
| 4 | Parse hardening | DIF | hardening |

## Dogfood Plan
| # | Deliverable | Format | Type |
|---|------------|--------|------|
| 1 | JSON export dogfood | FODS | dogfood |
| 2 | TXT export dogfood | FODT | dogfood |
| 3 | Crop+Save dogfood | Netpbm | dogfood |

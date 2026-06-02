# R89 POC Product Work Plan

Sprint: FORMAT-FACTORY-R89-AUTHORITATIVE-TEST-BASELINE-DECLARATION-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

## .NET Commercial POC Targets
| Format | R88 Tests | R89 New APIs | R89 Tests |
|--------|-----------|-------------|-----------|
| FODS | 185 | SheetCount, GetSheetByName, GetCellValue, ExportSheetToCsvString | 191 (+6) |
| FODT | 167 | CharCount, SearchText, ReplaceText | 176 (+9) |
| Netpbm | 71 | GetChannelStats, Rotate90Cw, Crop | 94 (+23) |

## FOSS Targets
- ZST: dependency classification, no code changes
- Python Netpbm: verified at Gate 10
- SYLK/DIF: CSV shadow fix enables full-suite pass

## Dogfood
- All existing exports verified (PBM->PGM, FODS->CSV, FODT->TXT)
- .NET Netpbm dogfood via NetpbmImage model transforms

# Commercial Gap Closure Plan

**Created:** 2026-06-16
**Taskcard:** TC-NEW-04
**Status:** TRACKING
**Total gaps:** 34 (FODS=10, FODT=9, Netpbm=15)

## Overview

All 34 commercial gaps require .NET implementation evidence. Python FOSS tests do NOT close commercial gaps. Each gap needs:
1. .NET implementation in the appropriate project
2. .NET test coverage proving the capability works
3. Gate 11 C1-C20 criteria alignment

## FODS Commercial Gaps (10)

| Gap ID | Capability | Priority | Closure Method | .NET Project |
|--------|-----------|----------|---------------|-------------|
| GAP-FODS-COMM-LOAD-001 | Load | P0 | Implement `FodsDocument.Load(stream)` | FormatFactory.Fods |
| GAP-FODS-COMM-SAVE_SAME_FO-001 | Save Same Format | P0 | Implement `FodsDocument.Save(stream)` | FormatFactory.Fods |
| GAP-FODS-COMM-RELOAD_AND_V-001 | Reload And Verify | P1 | Load→Save→Load roundtrip test | FormatFactory.Fods.Tests |
| GAP-FODS-COMM-INSPECT_OBJE-001 | Inspect Object Model | P2 | Expose Sheet/Row/Cell object model | FormatFactory.Fods |
| GAP-FODS-COMM-EDIT_CELLS-001 | Edit Cells | P2 | `Cell.Value` setter + type coercion | FormatFactory.Fods |
| GAP-FODS-COMM-EXPORT_CSV_M-001 | Export CSV Multi Sheet | P2 | `FodsDocument.ExportCsv(sheetIndex)` | FormatFactory.Fods |
| GAP-FODS-COMM-EXPORT_CSV_I-001 | Export CSV In Memory | P2 | `FodsDocument.ExportCsvToString()` | FormatFactory.Fods |
| GAP-FODS-COMM-ENUMERATE_SH-001 | Enumerate Sheets | P2 | `FodsDocument.Sheets` property | FormatFactory.Fods |
| GAP-FODS-COMM-SAVE_AFTER_E-001 | Save After Edit Roundtrip | P2 | Edit→Save→Reload verify | FormatFactory.Fods.Tests |
| GAP-FODS-COMM-EXPORT_QUALI-001 | Export Quality Edge Cases | P2 | Empty sheets, merged cells, formulas | FormatFactory.Fods.Tests |

**Closure order:** P0 (Load, Save) → P1 (Roundtrip) → P2 (remaining 7)
**Dependencies:** Load must exist before all others. Save must exist before roundtrip.

## FODT Commercial Gaps (9)

| Gap ID | Capability | Priority | Closure Method | .NET Project |
|--------|-----------|----------|---------------|-------------|
| GAP-FODT-COMM-LOAD-001 | Load | P0 | Implement `FodtDocument.Load(stream)` | FormatFactory.Fodt |
| GAP-FODT-COMM-SAVE_SAME_FO-001 | Save Same Format | P0 | Implement `FodtDocument.Save(stream)` | FormatFactory.Fodt |
| GAP-FODT-COMM-RELOAD_AND_V-001 | Reload And Verify | P1 | Load→Save→Load roundtrip test | FormatFactory.Fodt.Tests |
| GAP-FODT-COMM-INSPECT_OBJE-001 | Inspect Object Model | P2 | Expose Paragraph/Heading/List model | FormatFactory.Fodt |
| GAP-FODT-COMM-EDIT_PARAGRA-001 | Edit Paragraphs | P2 | `Paragraph.Text` setter | FormatFactory.Fodt |
| GAP-FODT-COMM-EDIT_HEADING-001 | Edit Headings | P2 | `Heading.Text` and `Level` setters | FormatFactory.Fodt |
| GAP-FODT-COMM-ENUMERATE_HE-001 | Enumerate Headings | P2 | `FodtDocument.Headings` property | FormatFactory.Fodt |
| GAP-FODT-COMM-GET_PARAGRAP-001 | Get Paragraph Text By Index | P2 | `FodtDocument.GetParagraph(index)` | FormatFactory.Fodt |
| GAP-FODT-COMM-GET_TEXT_BET-001 | Get Text Between Paragraphs | P2 | Range extraction API | FormatFactory.Fodt |

**Closure order:** P0 (Load, Save) → P1 (Roundtrip) → P2 (remaining 6)

## Netpbm Commercial Gaps (15)

| Gap ID | Capability | Priority | Closure Method | .NET Project |
|--------|-----------|----------|---------------|-------------|
| GAP-Netpbm-COMM-SAVE_SAME_FO-001 | Save Same Format | P0 | Implement `NetpbmImage.Save(stream)` | FormatFactory.Netpbm |
| GAP-Netpbm-COMM-LOAD_PBM-001 | Load PBM | P2 | `PbmImage.Load(stream)` | FormatFactory.Netpbm |
| GAP-Netpbm-COMM-LOAD_PGM-001 | Load PGM | P2 | `PgmImage.Load(stream)` | FormatFactory.Netpbm |
| GAP-Netpbm-COMM-LOAD_PPM-001 | Load PPM | P2 | `PpmImage.Load(stream)` | FormatFactory.Netpbm |
| GAP-Netpbm-COMM-INSPECT_IMAG-001 | Inspect Image Model | P2 | Width, Height, MaxVal, pixel array | FormatFactory.Netpbm |
| GAP-Netpbm-COMM-EDIT_PIXELS-001 | Edit Pixels | P2 | `Image[x,y]` setter | FormatFactory.Netpbm |
| GAP-Netpbm-COMM-EXPORT_PBM_T-001 | Export PBM to PGM | P2 | Format conversion | FormatFactory.Netpbm |
| GAP-Netpbm-COMM-EXPORT_PGM_T-001 | Export PGM to PPM | P2 | Format conversion | FormatFactory.Netpbm |
| GAP-Netpbm-COMM-EXPORT_PPM_T-001 | Export PPM to PGM | P2 | Format conversion | FormatFactory.Netpbm |
| GAP-Netpbm-COMM-FLIP_HORIZON-001 | Flip Horizontal | P2 | Pixel transform | FormatFactory.Netpbm |
| GAP-Netpbm-COMM-FLIP_VERTICA-001 | Flip Vertical | P2 | Pixel transform | FormatFactory.Netpbm |
| GAP-Netpbm-COMM-INVERT-001 | Invert | P2 | Pixel transform | FormatFactory.Netpbm |
| GAP-Netpbm-COMM-ROTATE_90CW-001 | Rotate 90CW | P2 | Pixel transform | FormatFactory.Netpbm |
| GAP-Netpbm-COMM-GET_CHANNEL_-001 | Get Channel Stats | P2 | Statistical analysis | FormatFactory.Netpbm |
| GAP-Netpbm-COMM-BINARY_WRITE-001 | Binary Write P4/P5/P6 | P2 | Binary format writers | FormatFactory.Netpbm |

**Closure order:** P0 (Save) → P2 Load group (PBM, PGM, PPM) → P2 remaining

## Execution Strategy

### Wave 1: Foundation (P0 — 5 gaps)
- FODS Load + Save (2)
- FODT Load + Save (2)
- Netpbm Save (1)

### Wave 2: Verification (P1 — 2 gaps)
- FODS Roundtrip (1)
- FODT Roundtrip (1)

### Wave 3: Feature Depth (P2 — 27 gaps)
- FODS object model + edit + export (7)
- FODT object model + edit + enumerate (6)
- Netpbm loads + transforms + stats (14)

### Blockers
- **TRUE_EXTERNAL_GATE:** .NET implementation requires access to commercial .NET projects
- **TRUE_EXTERNAL_GATE:** Gate 11 C1-C20 verification requires Babar Raza approval
- **Agent-owned:** Python FOSS equivalents already exist for all 34 capabilities; can serve as reference implementations

### Metrics
- Gap closure rate target: 5 gaps/sprint for Wave 1-2, 10 gaps/sprint for Wave 3
- Each closed gap requires: implementation + test + gap-ledger status update

# R107 Product Capability Delta

## New .NET APIs (6 total — 4 depth/export, 2 processing)

### FODS (2 APIs)
1. **ExportSheetToCsv(sheetName)** — RFC 4180 CSV export with proper quoting. 3 overloads. *Depth/export.*
2. **InsertRowWithValues(sheetName, rowIndex, values)** — Programmatic row insertion with typed cells. *Object-model depth.*

### FODT (2 APIs)
3. **GetHeadingTexts()** — Extract heading-only text from document. *Object-model depth.*
4. **ExportToPlainTextFile(filePath)** — Export document to plain text file. *Export/save.*

### Netpbm (2 APIs)
5. **Equalize()** — Histogram equalization for PGM images. *Processing depth.*
6. **ConvertFormat(targetFormat)** — ASCII<->binary format conversion within same family. *Format conversion.*

## Depth Classification
- Save/export/dogfood/object-model depth: 4 (ExportSheetToCsv, InsertRowWithValues, ExportToPlainTextFile, GetHeadingTexts)
- Processing/transform: 2 (Equalize, ConvertFormat)
- Shallow helpers: 0
- **PASS quota: 4+ depth required, 6 delivered (4 depth + 2 processing)**

## FOSS Deliverables (5 total — 3+ workflow-advanced)
1. ZST dependency isolation proof (10 tests)
2. PBM binary roundtrip proof (10 tests)
3. PPM+PGM conversion workflow (10 tests) — *workflow advanced*
4. SYLK CSV export hardening (9 tests) — *export workflow*
5. DIF roundtrip proof (9 tests) — *roundtrip workflow*

## Dogfood/Export (4 total — all implemented + test-proven)
1. FODS CSV export pipeline (6 tests)
2. FODT plain text export pipeline (6 tests)
3. Netpbm equalize+overlay+convert pipeline (6 tests)
4. SYLK CSV dogfood pipeline (6 tests)

## Examples/Docs (4 total)
1. `examples/dotnet/fods/export_sheet_to_csv.csx`
2. `examples/dotnet/fodt/export_to_plain_text.csx`
3. `examples/dotnet/netpbm/equalize_and_convert.csx`
4. `examples/python/sylk/sylk_csv_pipeline.py`

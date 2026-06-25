# Product Source Inventory

**Sprint:** FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
**Date:** 2026-06-25
**Method:** Direct source code inspection (read every key source file)

---

## .NET Products

### FODS — FormatFactory.Fods
**Source Root:** `src/net/fods/`
**Maturity Classification:** `LOAD_EDIT_SAVE_POC` → approaching `COMMERCIAL_CANDIDATE`

**Public Entry Points:**
- `FodsDocument` (sealed partial class) — primary document facade
  - `static FodsDocument Load(string filePath, long maxFileSizeBytes = 50MB)` — path-based load
  - `static FodsDocument CreateNew()` — blank document factory
  - `void Save(string filePath)` — write to disk
  - Properties: `Sheets` (IReadOnlyList), `SheetCount`, `MimeType`, `OdfVersion`
  - Sheet ops: `GetSheetByName()`, `GetSheetByIndex()`, `GetSheetNames()`, `AddSheet()`, `RemoveSheet()`, `RenameSheet()`, `CopySheet()`
  - Row ops: `InsertRow()`, `InsertRowWithValues()`, `DeleteRows()`, `ClearSheet()`
  - Cell ops: `GetCellValue()` (2 overloads), `SetCellValue()` (static + instance), `GetColumnHeaders()` (3 overloads)
  - Advanced: `MergeCells()`, `SetCellFormula()`, `SortRows()`, `SetCellStyle()`
  - Query (in Accessor): `GetRowCount()`, `GetColumnCount()`, `FindCellsByValue()`, `GetUsedRange()`, `GetRowValues()`, `GetColumnValues()`, `GetNumericColumnValues()`, `FilterRows()`, `GetColumnAggregates()`, `GetCellDataType()`, `ExportSheetToHtml()`, `ExportSheetToJson()`, `ExportSheetToCsv()`, `ExportSheetToMarkdown()`, `ExportSheetToXml()`, `ExportSheetToTsv()`, `HasSheet()`, `GetSheetStats()`
- `FodsSheet` — sheet wrapper (exposes XElement, Rows, Name, RowCount, etc.)
- `FodsRow` — row wrapper (exposes Cells)
- `FodsCell` — cell wrapper (Value, IsCovered, SetText(), Element)
- Exporters: `FodsCsvExporter`, `FodsHtmlExporter`, `FodsJsonExporter`, `FodsOdsExporter`, `FodsPdfExporter`, `FodsPngExporter`
- `FodsDocumentException` — custom exception

**API Quality Notes:**
- `GetColumnHeaders()` has 3 overloads: instance (first sheet), named sheet, static(FodsSheet) — **STATIC OVERLOAD** is inconsistent with the instance-method pattern
- No `Load(Stream)` overload — only file path
- All exceptions are `FodsDocumentException` (wraps XmlException correctly)
- Security: DTD prohibited, XmlResolver null, 50MB size guard

**Tests:** 73 test files (FodsR86 through FodsR118 + base tests)
**Examples:** 5 Python examples (edit_save_fods.py, edit_and_export.py, read_and_inspect.py, etc.)
**Samples:** `samples/by-format/fods/` (4 files: formula-basic, minimal-spreadsheet, multi-sheet-basic, typed-values-basic)
**Docs/README:** None (csproj references README.md but it does NOT exist)
**Packaging:** `.csproj` with PackageId, Version=0.1.0-tier0; depends on FormatFactory.Csv + FormatFactory.Html

---

### FODT — FormatFactory.Fodt
**Source Root:** `src/net/fodt/`
**Maturity Classification:** `LOAD_EDIT_SAVE_POC` → approaching `COMMERCIAL_CANDIDATE`

**Public Entry Points:**
- `FodtDocument` (sealed partial class) — primary document facade
  - `static FodtDocument Load(string filePath)` — path-based load (DTD-prohibited, security guard)
  - `static FodtDocument CreateEmpty()` — blank document factory
  - `void Save(string filePath)` — write to disk
  - Text ops: `GetParagraphTexts()`, `GetHeadingTexts()`, `AppendParagraph()`, `InsertParagraph()`, `RemoveParagraph()`, `RemoveAllParagraphs()`, `SetParagraphText()`, `GetPlainTextRange()`, `GetTextBetween()`
  - Heading ops: `GetHeadingParagraphs()`, `InsertHeading()`, `RemoveHeading()`
  - Analysis: `GetWordCount()`, `GetCharCount()`, `GetHeadingCount()`, `GetParagraphCount()`, `GetDocumentStats()`, `GetDocumentOutline()`, `GetDocumentMetadata()`, `GetParagraphStyleName()`, `SetParagraphStyle()`, `WordFrequency()`
  - Search: `ReplaceText()`
  - Export: `ExportToHtml()`, `ExportToHtml(filePath)`, `ExportToPlainText()`, `ExportToPlainText(filePath)`, `ExportToMarkdown()`, `ExportToMarkdown(filePath)`, `ExportOutlineJson()`, `ExportToPdf()` (stub?), `ExportToPng()` (stub?)
- `FodtBody` — body model wrapper
- `FodtParagraph` — paragraph wrapper (Text, StyleName, IsHeading, Level)
- Spec stubs: `Spec/Office/Body.cs`, `Spec/Table/Table.cs`, `Spec/Table/TableCell.cs`, `Spec/Table/TableRow.cs`, `Spec/Text/Heading.cs`, `Spec/Text/List.cs`, `Spec/Text/ListItem.cs`, `Spec/Text/Paragraph.cs`, `Spec/Text/Span.cs`
- `FodtDocumentException` — custom exception

**API Quality Notes:**
- No `Load(Stream)` overload
- `ExportToPdf()` and `ExportToPng()` may be stubs — needs inspection of FodtPdfExporter.cs
- Table spec stubs (Spec/Table/*) exist but table editing not visible in public API — **TABLE EDITING UNVERIFIED**
- Paragraph model is flat (FodtParagraph with Text/StyleName) — no rich text spans visible at API level

**Tests:** ~65 test files (FodtR86 through FodtR116)
**Examples:** 5 Python examples
**Samples:** `samples/by-format/fodt/` (4 files)
**Docs/README:** None

---

### NetPBM — FormatFactory.Netpbm
**Source Root:** `src/net/netpbm/`
**Maturity Classification:** `LOAD_EDIT_SAVE_POC`

**Public Entry Points:**
- `NetpbmDocument` — document-level wrapper
  - `static NetpbmDocument Load(string path)` — load from file (P1/P2/P3/P4/P5/P6)
  - `static NetpbmDocument LoadStream(Stream stream)` — stream-based load (**STREAM SUPPORT EXISTS**)
  - `static NetpbmDocument FromImage(NetpbmImage image)` — from model
  - `void Save(string path)` — write to file
  - Properties: `Width`, `Height`, `Format`, `PixelCount`, `MaxValue`, `IsColor`, `IsGrayscale`, `IsBitmap`, `AspectRatio`, `IsSquare`, `SourcePath`
  - Pixel: `GetPixel(row, col)`, `GetPixelColor(row, col)`
  - Serialize: `ToAsciiString()`, `ToBinaryBytes()`
- `NetpbmImage` (sealed partial class, 4 files) — full editable pixel model
  - Pixel ops: `GetPixel()`, `GetPixelColor()`, `SetPixel()`, `SetPixelColor()`, `FillRegion()`, `CopyRegion()`, `CreateCanvas()`, `Overlay()`, `DrawRectangle()`, `DrawLine()`
  - Transforms: `FlipHorizontal()`, `FlipVertical()`, `FlipDiagonal()`, `Rotate90()`, `Rotate180()`, `Rotate270()`, `Resize()`, `Crop()`, `MergeHorizontal()`, `MergeVertical()`, `Tile()`
  - Filters: `ToGrayscale()`, `ToColor()`, `AdjustBrightness()`, `AdjustContrast()`, `GetBrightness()`, `Threshold()`, `ExtractChannel()`, `BlurBox()`, `Sharpen()`, `Equalize()`, `ApplyGamma()`, `Posterize()`, `ApplySepia()`, `Solarize()`, `MedianFilter()`, `ConvertFormat()`
  - Analysis: `GetHistogram()`, `Clone()`
- `NetpbmExporter` — within-family conversion ONLY (PBM→PGM, PBM→PPM) — NOT external format
- `NetpbmParser` — parses P1/P2/P3/P4/P5/P6
- `NetpbmWriter` — writes ASCII and binary
- `NetpbmFormat` (enum) — PBM_P1, PBM_P4, PGM_P2, PGM_P5, PPM_P3, PPM_P6
- `NetpbmException` — custom exception

**API Quality Notes:**
- `NetpbmDocument.LoadStream()` exists — GOOD (unlike FODS/FODT)
- Extremely rich image processing API (30+ transform/filter methods)
- `NetpbmExporter` is WITHIN-FORMAT only (PBM→PGM, PBM→PPM) — not an external format exporter
- No export to HTML/PNG/JPEG — this library converts between Netpbm variants only
- `Image` property on `NetpbmDocument` exposes the full `NetpbmImage` model — powerful but leaks internal

**Tests:** ~65 test files (NetpbmR87 through NetpbmR118)
**Samples:** No samples found for PBM/PGM/PPM in samples/by-format/

---

### NDJSON — FormatFactory.Ndjson
**Source Root:** `src/net/ndjson/`
**Maturity Classification:** `PARSER_WITH_MODEL`

**Public Entry Points:**
- `NdjsonDocument` — document model
  - `static NdjsonDocument Load(string content)` — from string content (AMBIGUOUS: is this path or content?)
  - `static NdjsonDocument Load(Stream stream)` — from stream (**STREAM SUPPORT**)
  - `static NdjsonDocument LoadFile(string path)` — from file path
  - `void SaveToFile(string path)` — write to file
  - `string ToNdjson()` — serialize to string
  - Properties: `Records` (List<JsonElement>), `Count`
  - Query: `GetAllKeys()`, `GetFieldValues(key)`, `IsUniformSchema()`, `Filter(predicate)`
  - **NO AddRecord() method** — cannot add records to document
- `NdjsonReader` — internal reader
- `NdjsonWriter` — internal writer
- `NdjsonCsvExporter` — export to CSV
- `NdjsonException` — custom exception

**API Quality Notes:**
- `Load(string content)` vs `LoadFile(string path)` — **NAMING AMBIGUITY** (Load takes content, LoadFile takes path)
- `Records` is `List<JsonElement>` — raw JsonElement, not typed domain objects
- No `AddRecord()` or mutation API — records list is public (mutable by ref) but no provided methods
- `Filter()` returns a new document — immutable-friendly but inconsistent with FODS pattern
- Stream support: YES (unlike FODS/FODT)

**Tests:** 6 test files
**Samples:** `samples/by-format/ndjson/` (1 minimal file)

---

### CSV — FormatFactory.Csv
**Source Root:** `src/net/csv/`
**Maturity Classification:** `THIN_PARSER` (target writer role)

**Public Entry Points:**
- `CsvDocument` — simple model
  - `static CsvDocument Load(string content, bool hasHeaders = true)` — from string content
  - `static CsvDocument LoadFile(string path, bool hasHeaders = true)` — from file path
  - `string ToCsv()` — serialize to string
  - `void SaveToFile(string path)` — write to file
  - Properties: `Headers` (string[]?), `Rows` (List<string[]>), `HasHeaders`, `RowCount`, `ColumnCount`
  - Query: `IsEmpty`, `GetCellValue(row, col)`, `Filter(predicate)`, `HasColumn(name)` — (behavioral methods added R117)
- `CsvReader` — parses CSV
- `CsvWriter` — writes CSV

**API Quality Notes:**
- Target writer role: other products export TO this via `FodsCsvExporter`, `NdjsonCsvExporter`, etc.
- `Filter()` added as behavioral method — GOOD
- `Rows` is `List<string[]>` — no typed values (all strings)
- No per-cell data type detection
- No formula support
- Simple model appropriate for its target-writer role

**Tests:** 4 test files

---

### TSV — FormatFactory.Tsv
**Source Root:** `src/net/tsv/`
**Maturity Classification:** `THIN_PARSER` (target writer role)

Similar to CSV. `TsvDocument` with Headers, Rows, behavioral query methods.
`TsvCsvExporter` — TSV→CSV export.
`TsvException` — custom exception.

**Tests:** 6 test files

---

### ZST — FormatFactory.Zst
**Source Root:** `src/net/zst/`
**Maturity Classification:** `THIN_PARSER` (CRITICAL GAP: no writer)

**Public Entry Points:**
- `ZstDocument` — pure read-only DTO (ALL properties are `init`, no methods)
  - Properties: `FilePath`, `FileSizeBytes`, `MagicValid`, `FrameCount`, `FrameHeaderDescriptor`, `IsMinimalFrame`, `SizeExceeds100K`, `IsHighlyCompressed`, `OverheadBytes`, `BytesPerFrame`, `ContentTypeHint`, `IsEmptyContent`
  - Computed: `HasMultipleFrames`, `FileSizeKB`, `IsValid`, `SizeLabel`
  - **NO Load() method** — document is created by ZstParser
  - **NO Save() method** — no write capability
  - **NO compress/decompress API**
- `ZstParser` — reads ZST file headers, returns `ZstDocument`
- `ZstException` — custom exception

**CRITICAL API GAP:** `ZstDocument` cannot be loaded by the user (no `ZstDocument.Load()`), cannot be saved, and provides no compress/decompress operations. Users must call `ZstParser.Parse(path)` to get the document, and there is NO way to write a ZST file from .NET.

**Tests:** 2 test files (ZstParserTests, ZstR117DocumentPropertiesTests)

---

### HTML / Markdown / TXT — Target Writers
**Source Root:** `src/net/html/`, `src/net/markdown/`, `src/net/txt/`
**Maturity Classification:** `EMPTY_OR_SKELETON` (single writer class each, no parser/model)

- `HtmlWriter` — write HTML tables from row data
- `MarkdownWriter` — write Markdown tables from row data
- `TxtWriter` — write plain text from row data

These are NOT standalone products. They are dogfood target writer libraries used by FODS, FODT, etc.
No parser, no domain model, no document class, no examples.

---

## Python Products

### FODS Python — format-factory-fods
**Source Root:** `src/python/fods/`
**Maturity Classification:** `LOAD_EDIT_SAVE_POC` → approaching `FOSS_RELEASE_CANDIDATE`

**Core Source Files:**
- `parser.py` — `parse_fods(path)` → neutral model dict, `parse_fods_strict(path)` → raises on error
- `writer.py` — `write_fods(workbook, path)` — serializes neutral model back to FODS XML
- `neutral_model.py` — low-level dict manipulation functions (`workbook_set_cell_value`, `workbook_warnings_for_unsupported_edit`, `workbook_sheet_summary`, etc.)
- `models.py` — class-based wrappers: `FodsDocument`, `FodsSheet`, `FodsCell` over neutral model dict
- `csv_exporter.py` — `fods_to_csv(path_or_workbook, output_path)` — export to CSV
- `fods_to_tsv.py` — export to TSV
- `spreadsheet_document.py`, `spreadsheet_model_document.py` — additional doc classes
- `constants.py`, `exceptions.py`

**DUAL API PROBLEM:** Users can use EITHER:
1. Function-based API: `parse_fods()` → dict, `workbook_set_cell_value()` → dict
2. Class-based API: `FodsDocument.from_file()` → `FodsDocument` instance

No documentation tells users which to use. Both are exported from `__init__.py`.

**pyproject.toml:** Missing: authors, [project.urls], keywords, classifiers, readme
**Examples:** 5 files including installed-path example
**Tests:** Many (fods test directory)
**Samples:** 4 sample files

---

### FODT Python — format-factory-fodt
**Source Root:** `src/python/fodt/`
**Maturity Classification:** `LOAD_EDIT_SAVE_POC` → approaching `FOSS_RELEASE_CANDIDATE`

**Core Source Files:**
- `parser.py` — `parse_fodt(path)` → neutral model
- `writer.py` — `write_fodt(model, path)`
- `exporters.py` — `fodt_to_txt(path_or_model, dest)`, `fodt_to_markdown(path_or_model, dest)`, `fodt_to_html(path_or_model, dest)`
- `fodt_document_edit.py` — edit operations (neutral_model-based)
- `fodt_document_query.py` — query operations
- `neutral_model.py`, `models.py`, `text_document.py`, `fodt_neutral_ops.py`

**Exporters:** `fodt_to_txt`, `fodt_to_markdown`, `fodt_to_html` — CONFIRMED from source
**Note:** PDF/PNG exporters not visible in Python FODT

---

### ODS Python — format-factory-ods
**Core Source:** `ods_parser.py` (ZIP-based), `ods_writer.py`, `ods_csv_exporter.py`, `ods_stats.py`
**Maturity:** `LOAD_EDIT_SAVE_PARTIAL`
**Key API:** `load_ods(path)`, `write_ods(model, path)`, `set_cell_value(src, dest, sheet, row, col, val)`

---

### ODT Python — format-factory-odt
**Core Source:** `odt_parser.py`, `odt_writer.py`, `text_document.py`
**Maturity:** `LOAD_EDIT_SAVE_PARTIAL`
**Key API:** `load_odt(path)`, `write_odt(paragraphs, dest)`, `odt_from_text(text, dest)`, `odt_from_model(model, dest)`

---

### PBM/PGM/PPM Python — format-factory-pbm/pgm/ppm
**Maturity:** `LOAD_EDIT_SAVE_PARTIAL`
**PBM Key API:** `parse_pbm(path)`, `parse_pbm_strict(path)` (raises PbmError), `probe_pbm(path)`, `PbmImage` dataclass
- Supports P1 (ASCII) and P4 (binary) — CONFIRMED from source
- Error hierarchy: `PbmError`, `PbmInvalidMagicError`, `PbmInvalidHeaderError`, `PbmSizeError`, `PbmDecodeError`
- Cross-format: `pbm_to_pgm(pbm_path, pgm_path)`, `pbm_to_ppm(pbm_path, ppm_path)`
- **No write_pbm() for general use** — conversions to other formats only, no save-in-place

---

### QOI Python — format-factory-qoi
**Maturity:** `LOAD_EDIT_PARTIAL`
**Key API:** `qoi_parser.py` (parse), `qoi_encoder.py` (encode)
**Note:** QOI is a modern image format — encoder exists which is good

---

### XCF Python — format-factory-xcf
**Maturity:** `PARSER_WITH_MODEL`
**Key API:** `xcf_parser.py` (XcfImage class with layer_names), `xcf_image_metrics.py`
**Note:** Real layer names now implemented (2026-06-25 per MEMORY.md)

---

### ZST Python — format-factory-zst
**Maturity:** `PARSER_WITH_MODEL` → `LOAD_EDIT_PARTIAL`
**Key API:** `compress_string(text, level=3)`, `decompress_to_string(data)`, `ZstDocument` class
**Note:** Python ZST has BOTH compress AND decompress — contrast with .NET ZST (parser only)

---

### SYLK Python — format-factory-sylk
**Maturity:** `PARSER_WITH_MODEL`
**Key API:** `sylk_parser.py`, `SylkDocument` (flat model: rows count, cells list)
**SYLK API Oddity:** `set_cell_value(src, dest, row, col, value)` takes BOTH source and destination paths — file-based mutation, not model-based mutation

---

### DIF Python — format-factory-dif
**Maturity:** `PARSER_WITH_MODEL`
**Key API:** `dif_parser.py`, `DifDocument`, `DifCell`, `write_dif(doc, path)`

---

### GNUMERIC Python — format-factory-gnumeric
**Maturity:** `LOAD_EDIT_SAVE_PARTIAL`
**Key API:** `gnumeric_codec.py` (`load() → dict`), `models.py` (`GnumericDocument`), `write_gnumeric(model, path)`
**Note:** Gnumeric files are gzipped XML — implementation handles gzip transparently

---

### NDJSON Python — format-factory-ndjson
**Maturity:** `LOAD_EDIT_SAVE_PARTIAL`
**Key API:** `ndjson_codec.py` (`load_ndjson(path) → list`), `models.py` (`NdjsonDocument`), `write_ndjson(records, path)`, `ndjson_analytics.py` (37+ analytics functions)
**Note:** Analytics file (923 LOC) is separate from domain model — good separation

---

### TOML Python — format-factory-toml
**Maturity:** `LOAD_EDIT_SAVE_PARTIAL`
**Key API:** `toml_codec.py`, `models.py` (`TomlDocument`), `config_document.py`, `write_toml(data, path)`
**Note:** Uses Python stdlib `tomllib` (3.11+) for read, custom writer for write

---

### CSV Python — format-factory-csv
**Maturity:** `LOAD_EDIT_SAVE_PARTIAL`
**Key API:** `csv_parser.py` (`parse_csv_strict(path)`), `csv_writer.py` (`write_csv_to_file(rows, path, headers=...)`), `models.py` (`CsvDocument`)
**Import Conflict:** `csv` package name conflicts with Python stdlib `csv` — requires `sys.path.insert()`

---

### TSV Python — format-factory-tsv
**Maturity:** `LOAD_EDIT_PARTIAL`
**Key API:** `tsv_parser.py`, `models.py` (`TsvDocument`), `write_tsv(rows, dest, headers=headers)`
**Note:** `write_tsv` takes rows as `list[list[str]]` NOT list-of-dicts

---

### ABW Python — format-factory-abw
**Maturity:** `LOAD_EDIT_SAVE_PARTIAL`
**Key API:** `abw_codec.py` (`load() → dict`), `models.py` (`AbwDocument`), `append_paragraph(model, text)`, `write_abw(model, dest)`

---

### FODG Python — format-factory-fodg
**Maturity:** `LOAD_EDIT_PARTIAL`
**Key API:** `fodg_codec.py` (`load(path) → dict`), `write_fodg(model, path)`, `drawing_document.py`
**Note:** Dict-based model only — no typed domain objects for shape/page

---

### FODP Python — format-factory-fodp
**Maturity:** `LOAD_ONLY_POC`
**Key API:** `fodp_codec.py` (`load(path) → dict`, `get_page_count(path)`, `fodp_slide_count(path)`)
**CRITICAL GAP:** NO `write_fodp()` function — completely read-only
**Documentation:** No user-facing disclosure of this limitation

---

## Summary Table

| Product | Language | Maturity Class | Load | Edit | Save | Export | Tests | Examples | Docs |
|---------|----------|----------------|------|------|------|--------|-------|----------|------|
| FODS | .NET | LOAD_EDIT_SAVE_POC | ✓ | ✓ Rich | ✓ | 7 formats | 73 | 0 | ✗ |
| FODT | .NET | LOAD_EDIT_SAVE_POC | ✓ | ✓ Rich | ✓ | 5 (PDF/PNG?) | ~65 | 0 | ✗ |
| NetPBM | .NET | LOAD_EDIT_SAVE_POC | ✓+Stream | ✓ Rich | ✓ | Within-family | ~65 | 0 | ✗ |
| NDJSON | .NET | PARSER_WITH_MODEL | ✓+Stream | Partial | ✓ | CSV | 6 | 0 | ✗ |
| CSV | .NET | THIN_PARSER | ✓ | Partial | ✓ | — | 4 | 0 | ✗ |
| TSV | .NET | THIN_PARSER | ✓ | Partial | ✓ | CSV | 6 | 0 | ✗ |
| ZST | .NET | THIN_PARSER | ✗* | ✗ | ✗ | — | 2 | 0 | ✗ |
| HTML | .NET | WRITER_ONLY | — | — | ✓ | — | 1 | 0 | ✗ |
| Markdown | .NET | WRITER_ONLY | — | — | ✓ | — | 1 | 0 | ✗ |
| TXT | .NET | WRITER_ONLY | — | — | ✓ | — | 1 | 0 | ✗ |
| FODS | Python | LOAD_EDIT_SAVE_POC | ✓ | ✓ | ✓ | CSV/TSV | Many | 5 | ✗ |
| FODT | Python | LOAD_EDIT_SAVE_POC | ✓ | ✓ | ✓ | TXT/MD/HTML | Many | 5 | ✗ |
| ODS | Python | LOAD_EDIT_SAVE_PARTIAL | ✓ | Partial | ✓ | CSV | Many | 1 | ✗ |
| ODT | Python | LOAD_EDIT_SAVE_PARTIAL | ✓ | Partial | ✓ | — | Many | 1 | ✗ |
| PBM | Python | LOAD_EDIT_PARTIAL | ✓ | ✗ | ✗** | PGM/PPM | Some | 2 | ✓*** |
| PGM | Python | LOAD_EDIT_PARTIAL | ✓ | ✗ | ✗ | PPM | Some | 2 | ✓*** |
| PPM | Python | LOAD_EDIT_PARTIAL | ✓ | ✗ | ✗ | PGM | Some | 3 | ✓*** |
| QOI | Python | LOAD_EDIT_PARTIAL | ✓ | ✗ | ✓*** | — | Some | 0 | ✗ |
| XCF | Python | PARSER_WITH_MODEL | ✓ | ✗ | ✗ | — | Some | 0 | ✗ |
| ZST | Python | PARSER_WITH_MODEL | ✓ | ✓ | ✗**** | — | Some | 4 | ✗ |
| SYLK | Python | PARSER_WITH_MODEL | ✓ | File-based | File-based | CSV | Many | 4 | ✗ |
| DIF | Python | PARSER_WITH_MODEL | ✓ | Partial | ✓ | — | Some | 1 | ✗ |
| GNUMERIC | Python | LOAD_EDIT_SAVE_PARTIAL | ✓ | Dict | ✓ | CSV/JSON | Some | 5 | ✗ |
| NDJSON | Python | LOAD_EDIT_SAVE_PARTIAL | ✓ | List | ✓ | — | Some | 2 | ✗ |
| TOML | Python | LOAD_EDIT_SAVE_PARTIAL | ✓ | Dict | ✓ | — | Some | 3 | ✗ |
| CSV | Python | LOAD_EDIT_SAVE_PARTIAL | ✓ | List | ✓ | — | Some | 2 | ✗ |
| TSV | Python | LOAD_EDIT_PARTIAL | ✓ | List | ✓ | — | Some | 2 | ✗ |
| ABW | Python | LOAD_EDIT_SAVE_PARTIAL | ✓ | Partial | ✓ | TXT | Some | 4 | ✗ |
| FODG | Python | LOAD_EDIT_PARTIAL | ✓ | Dict | ✓ | TXT/JSON | Some | 2 | ✗ |
| FODP | Python | LOAD_ONLY_POC | ✓ | ✗ | ✗ | — | Some | 2 | ✗ |

Notes:
- `*` ZST .NET: `ZstDocument` is returned by `ZstParser.Parse()`, not `ZstDocument.Load()`
- `**` PBM/PGM/PPM: Cross-format conversions exist but no write-back to same format
- `***` QOI: encoder exists, docs/api/pbm.md/pgm.md/ppm.md exist (new, untracked)
- `****` ZST Python: write bytes directly, no `write_zst()` function

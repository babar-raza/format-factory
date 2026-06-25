# Product Source Map

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25
Method: Direct source inspection + git status analysis

---

## .NET Products (`src/net/`)

### FODS — `src/net/fods/`
| File | Role | LOC (est) | Key Contents |
|------|------|-----------|-------------|
| `FodsDocument.cs` | Primary facade (partial 1/3) | ~732 | Load, Save, CreateNew, Sheet CRUD, Cell ops, Sort, Merge |
| `FodsDocumentAccessor.cs` | Query methods (partial 2/3) | ~300 | GetRowCount, FilterRows, ExportSheetToHtml, GetColumnAggregates |
| `FodsDocumentExporter.cs` | Export methods (partial 3/3) | ~200 | Export orchestration |
| `FodsParser.cs` | XML parsing | ~200 | DTD-prohibited XML load, namespace constants |
| `FodsWriter.cs` | XML serialization | ~150 | Save/serialize logic |
| `FodsCsvExporter.cs` | CSV target export | ~80 | Sheet → CSV |
| `FodsHtmlExporter.cs` | HTML target export | ~80 | Sheet → HTML |
| `FodsJsonExporter.cs` | JSON target export | ~80 | Sheet → JSON |
| `FodsOdsExporter.cs` | ODS target export | ~80 | Sheet → ODS |
| `FodsPdfExporter.cs` | PDF target export | ~80 | Sheet → PDF |
| `FodsPngExporter.cs` | PNG target export | ~80 | Sheet → PNG |
| `Model/FodsCell.cs` | Domain model | ~60 | Cell properties |
| `Model/FodsRow.cs` | Domain model | ~50 | Row properties |
| `Model/FodsSheet.cs` | Domain model | ~60 | Sheet properties |
| `Exceptions/FodsDocumentException.cs` | Exception type | ~30 | Wraps XmlException |
| `Spec/Office/Document.cs` | Architecture stub | ~10 | spec_qname marker |
| `Spec/Table/Table.cs` | Architecture stub | ~10 | spec_qname marker |
| `Spec/Table/TableCell.cs` | Architecture stub | ~10 | spec_qname marker |
| `Spec/Table/TableRow.cs` | Architecture stub | ~10 | spec_qname marker |

**Tests:** `tests/net/fods/` (~73 files)
**Namespace:** `FormatFactory.Fods`
**Notes:** Partial class split across 3 files. Gate 11 contradiction in csproj. No README.md at source root.

---

### FODT — `src/net/fodt/`
| File | Role | LOC (est) |
|------|------|-----------|
| `FodtDocument.cs` | Primary facade (partial 1/2) | ~600 |
| `FodtDocumentAccessor.cs` | Query methods (partial 2/2) | ~250 |
| `FodtParser.cs` | XML parsing | ~150 |
| `FodtWriter.cs` | XML serialization | ~150 |
| `FodtHtmlExporter.cs` | HTML export | ~80 |
| `FodtMarkdownExporter.cs` | Markdown export | ~80 |
| `FodtTxtExporter.cs` | Text export | ~80 |
| `FodtPdfExporter.cs` | PDF export (likely stub) | ~40 |
| `FodtPngExporter.cs` | PNG export (likely stub) | ~40 |
| `Model/FodtBody.cs` | Domain model | ~60 |
| `Model/FodtParagraph.cs` | Domain model | ~60 |
| `Exceptions/FodtDocumentException.cs` | Exception type | ~30 |
| `Spec/Office/Body.cs` | Architecture stub | ~10 |
| `Spec/Table/Table.cs` | Architecture stub | ~10 |
| `Spec/Table/TableCell.cs` | Architecture stub | ~10 |
| `Spec/Table/TableRow.cs` | Architecture stub | ~10 |
| `Spec/Text/Heading.cs` | Architecture stub | ~10 |
| `Spec/Text/List.cs` | Architecture stub | ~10 |
| `Spec/Text/ListItem.cs` | Architecture stub | ~10 |
| `Spec/Text/Paragraph.cs` | Architecture stub | ~10 |
| `Spec/Text/Span.cs` | Architecture stub | ~10 |

**Tests:** `tests/net/fodt/` (~65 files)
**Namespace:** `FormatFactory.Fodt`
**Notes:** Spec/Table/* and Spec/Text/* are architecture stubs. Whether table operations are wired in public API is unconfirmed (PQ-012).

---

### NetPBM — `src/net/netpbm/`
| File | Role | LOC (est) |
|------|------|-----------|
| `NetpbmDocument.cs` | Public facade | ~350 |
| `NetpbmParser.cs` | Binary/ASCII parser | ~300 |
| `NetpbmWriter.cs` | Binary/ASCII writer | ~250 |
| `NetpbmExporter.cs` | Within-family converter | ~150 |
| `Model/NetpbmImage.cs` | Image model (partial 1/4) | ~400 |
| `Model/NetpbmFormat.cs` | Format enum | ~40 |
| `Model/NetpbmImageAnalyzer.cs` | Analytics (partial 2/4) | ~200 |
| `Model/NetpbmImageFilters.cs` | Filters (partial 3/4) | ~200 |
| `Model/NetpbmImageTransforms.cs` | Transforms (partial 4/4) | ~200 |
| `Spec/NetpbmImage.cs` | Architecture stub | ~10 |
| `Exceptions/NetpbmException.cs` | Exception type | ~30 |

**Tests:** `tests/net/netpbm/` (~65 files)
**Namespace:** `FormatFactory.Netpbm`
**Notes:** Has `LoadStream(Stream)` — only .NET product with stream load. NetpbmExporter is within-family (PBM→PGM, PBM→PPM), NOT an external format exporter (resolves PQ-013 as "within-family only").

---

### NDJSON — `src/net/ndjson/`
| File | Role | LOC (est) |
|------|------|-----------|
| `NdjsonDocument.cs` | Domain model + facade | ~146 |
| `NdjsonReader.cs` | Parse/load | ~100 |
| `NdjsonWriter.cs` | Serialize/save | ~80 |
| `NdjsonCsvExporter.cs` | CSV export | ~80 |
| `NdjsonException.cs` | Exception type | ~20 |
| `Spec/NdjsonRecord.cs` | Architecture stub | ~10 |

**Tests:** `tests/net/ndjson/` (~6 files)
**Namespace:** `FormatFactory.Ndjson`
**Notes:** Holds `List<JsonElement>` — raw, not typed domain objects. `Load(string content)` naming is ambiguous (PQ-011). Has `Load(Stream)` (stream support confirmed).

---

### CSV — `src/net/csv/`
| File | Role | LOC (est) |
|------|------|-----------|
| `CsvDocument.cs` | Domain model + facade | ~120 |
| `CsvReader.cs` | Parse | ~100 |
| `CsvWriter.cs` | Serialize | ~80 |
| `Spec/CsvRecord.cs` | Architecture stub | ~10 |

**Tests:** `tests/net/csv/` (~4 files)
**Namespace:** `FormatFactory.Csv`
**Notes:** Simple model: `Headers (string[]?)`, `Rows (List<string[]>)`. Target writer role for other exporters.

---

### TSV — `src/net/tsv/`
| File | Role | LOC (est) |
|------|------|-----------|
| `TsvDocument.cs` | Domain model + facade | ~100 |
| `TsvReader.cs` | Parse | ~80 |
| `TsvWriter.cs` | Serialize | ~60 |
| `TsvCsvExporter.cs` | CSV export | ~60 |
| `TsvException.cs` | Exception type | ~20 |
| `Spec/TsvRecord.cs` | Architecture stub | ~10 |

**Tests:** `tests/net/tsv/` (~6 files)
**Namespace:** `FormatFactory.Tsv`

---

### ZST — `src/net/zst/`
| File | Role | LOC (est) |
|------|------|-----------|
| `ZstDocument.cs` | Pure DTO (read-only) | ~87 |
| `ZstParser.cs` | Parse (entry point) | ~120 |
| `Exceptions/ZstException.cs` | Exception type | ~20 |

**Tests:** `tests/net/zst/` (~2 files)
**Namespace:** `FormatFactory.Zst`
**Notes:** `ZstDocument` is a pure DTO — ALL properties are `init`-only. No `Load()`, no `Save()`, no compress/decompress. `ZstParser.Parse(filePath)` or `ZstParser.Parse(byte[])` is the only entry point. CRITICAL GAP: no write/compress capability (PQ-007).

---

### HTML, Markdown, TXT — Writer Helpers
Each has exactly 1 source file:
- `src/net/html/HtmlWriter.cs` — renders HTML from internal model
- `src/net/markdown/MarkdownWriter.cs` — renders Markdown
- `src/net/txt/TxtWriter.cs` — renders plain text

These are internal utility writers used by FODS/FODT exporters, not standalone products (PQ-015).

---

## Python Products (`src/python/`)

### FODS — `src/python/fods/`
| File | Role |
|------|------|
| `__init__.py` | Package entry point (wildcard imports) |
| `parser.py` | XML parse → neutral model dict |
| `writer.py` | Dict → FODS XML |
| `models.py` | FodsDocument / FodsSheet / FodsCell wrappers |
| `neutral_model.py` | Dict-based neutral model functions |
| `spreadsheet_document.py` | Spreadsheet facade |
| `spreadsheet_model_document.py` | Model document facade |
| `csv_exporter.py` | Export to CSV |
| `fods_to_tsv.py` | Export to TSV |
| `constants.py` | XML namespace constants |
| `exceptions.py` | Custom exception types |
| `Compat/` | Architecture-only facades (FodsDocument, FodsSheet, FodsCell as stubs) |
| `Spec/` | Architecture-only spec markers |

**Tests:** `tests/python/fods/` (many files)
**Notes:** Dual API (PQ-002). Wildcard imports (PQ-001). Both dict-function API and class-based API exported simultaneously from `__init__.py`.

---

### FODT — `src/python/fodt/`
| File | Role |
|------|------|
| `parser.py` | XML parse → neutral model |
| `writer.py` | Model → FODT XML |
| `models.py` | FodtDocument wrapper |
| `exporters.py` | fodt_to_txt, fodt_to_markdown, fodt_to_html |
| `fodt_document_edit.py` | Edit operations (~729 LOC) |
| `fodt_document_query.py` | Query operations |
| `fodt_neutral_ops.py` | Neutral model ops (~796 LOC) |
| `neutral_model.py` | Neutral model (was 1916 LOC, healed to 279 LOC) |
| `text_document.py` | Text document facade (~992 LOC) |
| `Compat/` | Architecture stubs (fodt_list, fodt_table, etc.) |
| `Spec/` | Architecture spec markers |

**Notes:** Healed from GOV_BLOCK. Analytics distributed to multiple files.

---

### ODS — `src/python/ods/`
`ods_parser.py`, `ods_writer.py`, `ods_csv_exporter.py`, `ods_stats.py`, `models.py`
Load+write+export confirmed. ZIP-based (OpenDocument).

---

### ODT — `src/python/odt/`
`odt_parser.py`, `odt_writer.py`
Load+write confirmed. ZIP-based ODT. `odt_from_text()`, `write_odt()` available.

---

### ABW — `src/python/abw/`
`abw_codec.py`, `models.py`, `spec/document/` (architecture stubs)
`load()` → dict. `append_paragraph(model, text)`. `write_abw(model, dest)`. AbwDocument class.

---

### CSV — `src/python/csv/`
`csv_parser.py`, `csv_writer.py`, `models.py`
`parse_csv_strict()`, `write_csv_to_file()`, `get_column_names()`, `get_cell_value()`. CsvDocument class.
**Note:** Package name conflicts with stdlib `csv` — requires `sys.path.insert` workaround.

---

### TSV — `src/python/tsv/`
`tsv_parser.py`, `models.py`
`parse_tsv_strict()` → dict. `write_tsv(rows, dest, headers=)`. TsvDocument class.
**Note:** `write_tsv` takes `list[list[str]]` not list-of-dicts.

---

### DIF — `src/python/dif/`
`dif_parser.py`
DifDocument, DifCell. `load_dif()`, `write_dif()`. Flat model (single row list).

---

### GNUMERIC — `src/python/gnumeric/`
`gnumeric_codec.py`, `models.py`, `spec/workbook/` (architecture stubs)
`load()` → dict with `cell_grid: {(row,col): value}`. `write_gnumeric()`. GnumericDocument class.
`export_to_csv(path)` (takes path), `export_to_json(model)` (takes dict).

---

### NDJSON — `src/python/ndjson/`
`ndjson_codec.py`, `models.py`, `json_stream.py`, `ndjson_record_stats.py`, `ndjson_analytics.py` (923 LOC)
`load_ndjson()`, `write_ndjson()`. NdjsonDocument class. 37+ analytics functions.
**Note:** `ndjson_analytics.py` is large — analytics masquerade risk.

---

### TOML — `src/python/toml/`
`toml_codec.py`, `models.py`, `config_document.py`, `exceptions.py`
`load_toml()`, `write_toml()`. TomlDocument class. TomlError, TomlInputError.

---

### SYLK — `src/python/sylk/`
`sylk_parser.py`
SylkDocument (flat model: `.rows` count, `.cells` list of SylkCell). `set_cell_value(src, dest, row, col, val)` is FILE-BASED.
`sylk_to_csv(file_path)` takes file path, not model.

---

### PBM — `src/python/pbm/`
`pbm_parser.py`
PbmImage dataclass. P1 (ASCII) + P4 (binary). `parse_pbm()`, `parse_pbm_strict()`, `probe_pbm()`.
Exception hierarchy: PbmError → PbmInvalidMagicError, PbmInvalidHeaderError, PbmSizeError, PbmDecodeError.

---

### PGM — `src/python/pgm/`
`pgm_parser.py`
PgmImage. P2 (ASCII) + P5 (binary). Grayscale.

---

### PPM — `src/python/ppm/`
`ppm_parser.py`
PpmImage. P3 (ASCII) + P6 (binary). Full color (R, G, B channels).

---

### QOI — `src/python/qoi/`
`qoi_parser.py`, `qoi_encoder.py`
Modern lossless image format. `parse_qoi()`, `encode_qoi()`. Minimal typed model.

---

### XCF — `src/python/xcf/`
`xcf_parser.py`, `xcf_image_metrics.py`
XcfImage class (spec_qname="xcf:image"). `xcf_layer_name_list()` returns real layer names (fixed 2026-06-25).
Read-only (GIMP format). No write/export capability.

---

### ZST — `src/python/zst/`
`zst_codec.py`, `models.py`
`compress_string(text, level=3)` → bytes. `decompress_to_string(data: bytes)`.
ZstDocument.from_file(path): spec_qname="zst:frame". Unlike .NET ZST, Python ZST has compress/decompress.

---

### FODG — `src/python/fodg/`
`fodg_codec.py`
Dict-only model. `load(path)` → dict. `write_fodg(model, dest)`.
`export_to_txt(path)`, `export_to_json(model)` (mixed path/dict API).

---

### FODP — `src/python/fodp/`
`fodp_codec.py`
Dict-only model. `load(path)` → dict. No write capability.
`get_page_count(path)` takes path (not model). `fodp_slide_count(path)` also file-based.
**CRITICAL:** Read-only but no user-facing documentation of this limitation (PQ-009).

---

## Architecture Stub Locations

Python packages with `Spec/` or `Compat/` subdirectories containing `# GENERATED — architecture_only` markers:
- `src/python/fods/Spec/` — architecture stubs
- `src/python/fods/Compat/` — FodsDocument/FodsSheet/FodsCell (empty shells inheriting from stubs)
- `src/python/fodt/Spec/` — architecture stubs
- `src/python/fodt/Compat/` — architecture stubs
- `src/python/abw/spec/document/` — ABW document architecture stubs
- `src/python/gnumeric/spec/workbook/` — Gnumeric architecture stubs

.NET packages with `Spec/` architecture stubs:
- `src/net/fods/Spec/` (4 files)
- `src/net/fodt/Spec/` (8 files)
- `src/net/ndjson/Spec/` (1 file)
- `src/net/csv/Spec/` (1 file)
- `src/net/tsv/Spec/` (1 file)
- `src/net/netpbm/Spec/` (1 file)

These are intentional spec-parity markers, NOT behavioral implementations. V48 governance validator blocks RELEASE_GATE claims citing these.

---

## Shared Base Class Usage

`src/python/_shared/` contains `_base_codec.py` and `_base_parser.py`.
These base classes exist but most format packages do NOT inherit from them in practice.
This is a dead abstraction (PQ-016).

---

## Test Suite Organization

Tests follow sprint-naming convention (e.g., `FodsR87ProductDeepening.cs`, `FodsR100AddSheetTests.cs`).
This makes feature-coverage navigation difficult (PQ-017).

Tests are located at:
- `tests/net/{format}/` — per format under .NET
- `tests/python/{format}_format/` or `tests/python/{format}/` — per format under Python
- `tests/supervisor/` — supervisor and governance tests

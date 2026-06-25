# Source Review Checklist
# Format Factory — Expert Manual System Review
# Phase 2 output — Generated: 2026-06-25

## How To Use

Mark each item: [x] = confirmed, [ ] = not verified, [!] = gap found

---

## .NET Products

### FODS (FormatFactory.Fods)

**Parser checks:**
- [x] FodsParser.cs reads flat XML correctly
- [x] DTD injection disabled (XmlReaderSettings.DtdProcessing = Prohibit)
- [x] 50MB file size guard exists
- [x] Returns structured FodsDocument with sheets

**Model checks:**
- [x] FodsDocument exposes Sheets
- [x] FodsSheet exposes Rows
- [x] FodsRow exposes Cells
- [x] FodsCell exposes Value, ValueType, DisplayValue
- [x] Cells have coordinate access (Row, Col)

**Writer checks:**
- [x] Internal FodsWriter produces valid flat ODS XML

**Exporter checks:**
- [x] FodsCsvExporter — uses FormatFactory.Csv (dogfood)
- [x] FodsHtmlExporter — uses FormatFactory.Html (dogfood)
- [x] FodsJsonExporter — pure .NET
- [!] FodsOdsExporter — marked "PROTOTYPE STATUS" in source; PASS in poc-targets (DISCREPANCY)
- [x] FodsPdfExporter — pure .NET; Latin-1 only (known gap)
- [x] FodsPngExporter — pure .NET

**Test checks:**
- [x] 71 test files
- [?] Edge case test coverage for malformed input (needs deeper review)
- [?] ODS exporter roundtrip test — does it verify ZIP is valid ODS?

**Commercial checks:**
- [x] GenerateDocumentationFile=true (fixed in prior sprint)
- [!] PDF Latin-1 limitation blocks any non-Western Unicode content

---

### FODT (FormatFactory.Fodt)

**Parser checks:**
- [x] FodtParser.cs reads flat ODF text document
- [x] Security hardening (DTD disabled)

**Model checks:**
- [x] FodtDocument exposes Body
- [x] FodtBody exposes Paragraphs (top-level only)
- [!] FodtBody.Paragraphs EXPLICITLY skips tables/lists — documented limitation
- [!] Spec/Table/TableCell.cs, TableRow.cs exist but NOT exposed in public model

**Writer checks:**
- [x] Internal FodtWriter produces valid flat ODT XML

**Exporter checks:**
- [x] FodtHtmlExporter
- [x] FodtMarkdownExporter (uses FormatFactory.Markdown dogfood)
- [x] FodtPdfExporter (Latin-1 only)
- [x] FodtPngExporter
- [x] FodtTxtExporter (uses FormatFactory.Txt dogfood)

**Test checks:**
- [x] 64 test files
- [?] Table content test coverage — verify no test checks table cells in body

---

### NetPBM (FormatFactory.Netpbm)

**Parser checks:**
- [x] Reads P1/P2/P3 (ASCII) and P4/P5/P6 (binary) formats
- [x] Security: file size guards

**Model checks:**
- [x] NetpbmImage — core image model
- [x] NetpbmImageTransforms — FlipH, FlipV, Rotate90CW, Invert
- [x] NetpbmImageFilters — threshold, normalize
- [x] NetpbmImageAnalyzer — GetStats, GetChannelStats

**Writer checks:**
- [x] NetpbmWriter — writes PBM/PGM/PPM

**Exporter checks:**
- [!] NO exporter to any other format — no PNG/JPEG/BMP output
- [!] No dogfood path to any other FormatFactory library

**Test checks:**
- [x] 56 test files (high density)

---

### CSV (FormatFactory.Csv)

**Parser checks:**
- [x] CsvReader.cs — reads delimiter-separated lines

**Model checks:**
- [x] CsvDocument — exposes Headers, Rows
- [!] NO AddRow() method
- [!] NO SetCell() method
- [!] NO RemoveRow() method

**Writer checks:**
- [x] CsvWriter.cs — basic write

**Test checks:**
- [!] Only 6 test files — minimal coverage
- [!] No malformed input tests visible

---

### TSV (FormatFactory.Tsv)

- [x] TsvReader, TsvWriter, TsvDocument
- [x] CsvExporter (dogfood)
- [!] Only 6 test files
- [!] No edit API

---

### NDJSON (FormatFactory.Ndjson)

- [x] NdjsonReader, NdjsonWriter, NdjsonDocument
- [x] CsvExporter (dogfood)
- [!] Only 6 test files
- [!] No edit API

---

### ZST (FormatFactory.Zst) — CRITICAL GAP

- [x] ZstParser reads magic bytes (0x28 0xB5 0x2F 0xFD)
- [x] ZstParser counts frames (heuristic)
- [!] **NO decompression — explicitly documented "probe-only"**
- [!] ZstDocument cannot access compressed payload
- [!] Only 2 test files — covers probe only
- [!] A "compression format product" with no decompression is an inspection tool, not a library

---

### HTML / Markdown / TXT (Target Writers)

- [x] Target writers only — no parse capability
- [!] Listed as format products in system — inflates format count
- [x] Each: ~70–118 LOC, 1 test file
- [!] Not independently useful products

---

## Python Packages

### FODS Python

- [x] fods_parser.py + models.py
- [x] 12 Compat facades (FodsCell, FodsSheet, FodsDocument, etc.)
- [x] spec/ classes present
- [x] write_fods() → produces flat ODS XML
- [x] Export functions to CSV, HTML, JSON
- [x] 93 test files
- Score: APPROACHING_PY5

### FODT Python

- [x] fodt_parser.py + models.py + 10 Compat facades
- [x] exporters.py with fodt_to_txt(), fodt_to_markdown(), fodt_to_html()
- [x] write_fodt()
- [x] 131 test files
- Score: APPROACHING_PY5

### FODP Python

- [x] fodp_codec.py — read + export
- [x] export_to_txt(), export_to_csv(), export_to_json()
- [!] NO write_fodp() — cannot create or modify presentations
- Score: PY2 (model present, export-only)

### ODS Python

- [x] ods_parser.py
- [x] ods_writer.py with write_ods() (confirmed in source)
- [x] Pure stdlib ZIP + ElementTree
- Score: PY3

### ODT Python

- [x] odt_parser.py + odt_writer.py (added 2026-06-24)
- [x] write_odt(), odt_from_text(), odt_from_model()
- Score: PY3

### XCF Python

- [x] xcf_parser.py (1,272 LOC)
- [x] layer_names now returns REAL names (fixed 2026-06-25)
- [!] No write capability (acceptable for GIMP format)
- Score: PY2

### ZST Python

- [x] zst_codec.py (1,549 LOC — analytics-heavy)
- [x] compress_string(), decompress_to_string() — core works
- [!] LOC cap violation — analytics bloat
- Score: PY3 (functional core, analytics heavy)

### GNUMERIC Python

- [x] gnumeric_codec.py (760 LOC)
- [x] load() returns dict model; GnumericDocument wraps it
- [x] write_gnumeric(), export_to_csv(), export_to_json()
- [!] Two-layer dict+object pattern may confuse users
- Score: PY3

### SYLK Python

- [x] sylk_parser.py (741 LOC)
- [x] set_cell_value() is FILE-BASED (takes src+dest paths)
- [!] File-based mutation API is unusual
- Score: PY3

### PBM/PGM/PPM Python

- [x] write_pbm(), write_pgm(), write_ppm() confirmed in source (corrects initial assessment)
- [x] PBM → PGM/PPM cross-format conversion
- Score: PY3 (full read+write+convert)

### ABW / DIF / FODG / TOML / NDJSON / TSV / CSV Python

- [x] All have read + write capability
- [x] Domain models present (from 2026-06-24 sprint)
- Score: PY3

### QOI Python

- [x] qoi_encoder.py exists (can create QOI files)
- Score: PY3

### FODG Python

- [x] fodg_codec.py (large)
- [x] write_fodg(), export_to_txt(), export_to_json()
- Score: PY3

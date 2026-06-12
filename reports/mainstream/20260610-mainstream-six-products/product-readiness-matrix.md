# Product Readiness Matrix — Mainstream Mega-Train
# Date: 2026-06-10
# Python tests: 3001 passed, 20 skipped
# .NET tests: 1666 passed, 0 failed

## Summary

| Product | Python Ready | .NET Ready | Python Tests | .NET Tests | Package Py | Package .NET |
|---------|-------------|-----------|-------------|-----------|-----------|-------------|
| FODS | VALIDATED | VALIDATED | 211 | 547 | YES | YES |
| FODT | VALIDATED | VALIDATED | 248 | 520 | YES | YES |
| CSV | VALIDATED | VALIDATED | 38 | 36 | YES | YES |
| Netpbm | VALIDATED | VALIDATED | 144 | 465 | YES | YES |
| NDJSON | VALIDATED | VALIDATED | 233 | 29 | YES | YES |
| TSV | VALIDATED | VALIDATED | 373 | 38 | YES | YES |

**6/6 Python product tracks: VALIDATED**
**6/6 .NET product tracks: VALIDATED**

## Detailed Python Readiness

### FODS Python
- [x] Load/read: streaming XML parser with defusedxml
- [x] Inspect/query: neutral model (Workbook/Sheet/Row/Cell/Formula/Warning)
- [x] Edit: multiple edit functions (set_cell_value, add_sheet, etc.)
- [ ] Write/save: NOT implemented (Python read-only)
- [ ] Roundtrip: NOT implemented
- [x] Export: export_to_csv via ODS CSV exporter pattern
- [x] Error handling: tested (211 tests)
- [x] Security: defusedxml, 100MB guard, DTD prohibited
- [x] Package: format-factory-fods-python 0.1.0.dev0 installed
- [x] API: public API with __all__ exports

### FODT Python
- [x] Load/read: streaming XML parser with depth-tracking
- [x] Inspect/query: neutral model (Document/Block/List/Table)
- [x] Edit: multiple edit functions
- [ ] Write/save: NOT implemented (Python read-only)
- [ ] Roundtrip: NOT implemented
- [x] Export: export functions present
- [x] Error handling: tested (248 tests)
- [x] Security: defusedxml, 100MB guard
- [x] Package: format-factory-fodt-python 0.1.0.dev0 installed
- [x] API: public API with __all__ exports

### CSV Python
- [x] Load/read: RFC 4180 inline parser with delimiter sniff
- [x] Inspect/query: probe_csv, column/row counts
- [x] Edit: parse_and_rewrite with transform
- [x] Write/save: write_csv, write_csv_to_file (NEW THIS SPRINT)
- [x] Roundtrip: parse_and_rewrite roundtrip verified
- [x] Export: N/A (CSV is already an interchange format)
- [x] Error handling: tested (38 tests)
- [x] Security: 64MB guard, 1M row limit
- [x] Package: format-factory-csv 0.1.0.dev0 installed (NEW THIS SPRINT)
- [x] API: public API with __all__ exports

### Netpbm Python (PBM/PGM/PPM)
- [x] Load/read: P1/P2/P3/P4/P5/P6 full decode (ASCII + binary)
- [x] Inspect/query: dataclass models (PbmImage/PgmImage/PpmImage)
- [ ] Edit: NOT implemented
- [ ] Write/save: NOT implemented
- [ ] Roundtrip: NOT implemented
- [ ] Export: NOT implemented
- [x] Error handling: tested (144 combined tests)
- [x] Security: 64MB guard, dimension limits, pixel validation
- [x] Package: format-factory-pbm/pgm/ppm installed
- [x] API: public parsers

### NDJSON Python
- [x] Load/read: line-by-line JSON parser
- [x] Inspect/query: count, filter, group, aggregate
- [x] Edit: sort, deduplicate, merge, pick, pluck
- [x] Write/save: write_ndjson, to_jsonl_str
- [x] Roundtrip: roundtrip verified
- [x] Export: export_to_csv
- [x] Error handling: tested (233 tests)
- [x] Security: size guard
- [x] Package: format-factory-ndjson 0.1.0.dev0 installed
- [x] API: public API with __all__ exports

### TSV Python
- [x] Load/read: tab-split parser with BOM strip
- [x] Inspect/query: headers, column values, row counts
- [x] Edit: add/rename/drop column, filter, sort, merge, deduplicate
- [x] Write/save: write_tsv, write_tsv_strict, append_row
- [x] Roundtrip: roundtrip function verified
- [x] Export: to_csv export
- [x] Error handling: tested (373 tests)
- [x] Security: 64MB guard, 1M row limit
- [x] Package: format-factory-tsv 0.1.0.dev0 installed
- [x] API: public API with __all__ exports

## Detailed .NET Readiness

### FODS .NET
- [x] Build: 0 errors
- [x] Load/read: FodsParser (streaming XML)
- [x] Inspect/query: FodsDocument model (Sheet/Row/Cell)
- [x] Edit: in-model editing
- [x] Write/save: FodsWriter
- [x] Roundtrip: load-edit-save-reload verified
- [x] Export: CSV, HTML, JSON exporters
- [x] Tests: 547 pass
- [x] Package: FormatFactory.Fods.0.1.0-tier0.nupkg
- Commercial tier: classified (tier 0, NOT approved)

### FODT .NET
- [x] Build: 0 errors
- [x] Load/read: FodtParser
- [x] Inspect/query: FodtDocument model (Body/Paragraph)
- [x] Edit: in-model editing
- [x] Write/save: FodtWriter
- [x] Roundtrip: load-edit-save-reload verified
- [x] Export: HTML, TXT, Markdown exporters
- [x] Tests: 520 pass
- [x] Package: FormatFactory.Fodt.0.1.0-tier0.nupkg
- Commercial tier: classified (tier 0, NOT approved)

### CSV .NET
- [x] Build: 0 errors
- [x] Load/read: CsvReader (RFC 4180, BOM strip) — NEW THIS SPRINT
- [x] Inspect/query: CsvDocument model (headers, columns) — NEW THIS SPRINT
- [x] Edit: N/A for CSV
- [x] Write/save: CsvWriter (RFC 4180)
- [x] Roundtrip: read-write roundtrip verified — NEW THIS SPRINT
- [x] Export: N/A (CSV is interchange)
- [x] Tests: 36 pass (was 15, +21 this sprint)
- [x] Package: FormatFactory.Csv.0.1.0-mwp.nupkg
- Commercial tier: not classified

### Netpbm .NET
- [x] Build: 0 errors
- [x] Load/read: NetpbmParser (all Netpbm formats)
- [x] Inspect/query: NetpbmImage model
- [x] Edit: pixel manipulation
- [x] Write/save: NetpbmWriter
- [x] Roundtrip: verified
- [x] Export: NetpbmExporter
- [x] Tests: 465 pass
- [x] Package: FormatFactory.Netpbm.0.1.0-r85-poc.nupkg
- Commercial tier: not classified

### NDJSON .NET — NEW THIS SPRINT
- [x] Build: 0 errors
- [x] Load/read: NdjsonReader (string/stream/file, 64MB guard)
- [x] Inspect/query: NdjsonDocument model (Records, Count)
- [x] Edit: N/A
- [x] Write/save: NdjsonWriter (serialize + file output)
- [x] Roundtrip: load-write-reload verified
- [x] Export: NdjsonCsvExporter (to CSV)
- [x] Tests: 29 pass
- [x] Package: FormatFactory.Ndjson.0.1.0-mwp.nupkg
- Commercial tier: not classified

### TSV .NET — NEW THIS SPRINT
- [x] Build: 0 errors
- [x] Load/read: TsvReader (string/stream/file, BOM strip, 64MB guard)
- [x] Inspect/query: TsvDocument model (Headers, Rows, ColumnCount)
- [x] Edit: N/A
- [x] Write/save: TsvWriter (field validation, UTF-8)
- [x] Roundtrip: load-write-reload verified
- [x] Export: TsvCsvExporter (to CSV)
- [x] Tests: 38 pass
- [x] Package: FormatFactory.Tsv.0.1.0-mwp.nupkg
- Commercial tier: not classified

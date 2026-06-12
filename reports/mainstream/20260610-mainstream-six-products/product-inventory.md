# Product Inventory — Mainstream Mega-Train
# Date: 2026-06-10

## Python Product Inventory (selected 6)

### FODS
- Source: src/python/fods/ (parser.py, neutral_model.py, constants.py, exceptions.py, __init__.py)
- LOC: 793
- Tests: 211 (tests/python/fods/)
- Capabilities: read, inspect, neutral model (Workbook/Sheet/Row/Cell/Formula/Warning)
- Missing: write, export
- Package: format_factory_fods_python (egg-info exists)

### FODT
- Source: src/python/fodt/ (parser.py, neutral_model.py, list_traversal.py, constants.py, exceptions.py, __init__.py)
- LOC: 857
- Tests: 248 (tests/python/fodt/)
- Capabilities: read, inspect, neutral model (Document/Block/List/Table)
- Missing: write, export
- Package: format_factory_fodt_python (egg-info exists)

### CSV
- Source: src/python/csv/ (csv_parser.py)
- LOC: 213
- Tests: 19 (tests/python/csv/)
- Capabilities: read (RFC 4180 parser, BOM strip, delimiter sniff)
- Missing: write, export, neutral model, packaging

### Netpbm (PBM/PGM/PPM)
- PBM source: src/python/pbm/ (pbm_parser.py) — 290 LOC, 48 tests
- PGM source: src/python/pgm/ (pgm_parser.py) — 319 LOC, 47 tests
- PPM source: src/python/ppm/ (ppm_parser.py) — 322 LOC, 49 tests
- Capabilities: full read (ASCII + binary variants)
- Missing: write, export
- Packages: egg-info exists for each

### NDJSON
- Source: src/python/ndjson/ (ndjson_codec.py)
- LOC: 815
- Tests: 233 (tests/python/ndjson/)
- Capabilities: read, write, export (CSV), roundtrip, filter, sort, group, aggregate
- Missing: formal packaging
- Package: format_factory_ndjson (egg-info exists)

### TSV
- Source: src/python/tsv/ (tsv_parser.py)
- LOC: 198
- Tests: 19 (tests/python/tsv/)
- Capabilities: read (tab-split, BOM strip, header heuristic)
- Missing: write (write_tsv_strict exists per memory), export, neutral model

## .NET Product Inventory (selected 6)

### FODS
- Source: src/net/fods/ (FodsParser.cs, FodsWriter.cs, FodsDocument.cs, FodsCsvExporter.cs, FodsHtmlExporter.cs, FodsJsonExporter.cs, Model/*)
- Tests: 547 (tests/net/fods/)
- Capabilities: read, write, roundtrip, export (CSV/HTML/JSON), neutral model
- Package: FormatFactory.Fods.csproj (net10.0)

### FODT
- Source: src/net/fodt/ (FodtParser.cs, FodtWriter.cs, FodtDocument.cs, FodtHtmlExporter.cs, FodtTxtExporter.cs, FodtMarkdownExporter.cs, Model/*)
- Tests: 520 (tests/net/fodt/)
- Capabilities: read, write, roundtrip, export (HTML/TXT/Markdown), neutral model
- Package: FormatFactory.Fodt.csproj (net10.0)

### CSV
- Source: src/net/csv/ (CsvWriter.cs)
- Tests: 15 (tests/net/csv/)
- Capabilities: write only
- Missing: read/parse, inspect, roundtrip, export
- Package: FormatFactory.Csv.csproj (net10.0)

### Netpbm
- Source: src/net/netpbm/ (NetpbmParser.cs, NetpbmWriter.cs, NetpbmExporter.cs, NetpbmException.cs, Model/NetpbmImage.cs)
- Tests: 465 (tests/net/netpbm/)
- Capabilities: read, write, export, neutral model
- Package: FormatFactory.Netpbm.csproj (net10.0)

### NDJSON (.NET)
- Source: DOES NOT EXIST
- Must create: src/net/ndjson/
- Blocker: .NET project needs creation

### TSV (.NET)
- Source: DOES NOT EXIST
- Must create: src/net/tsv/
- Blocker: .NET project needs creation

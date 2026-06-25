# Source Inventory Report

**Sprint/Run ID:** ff-archaeology-20260625

---

## Python Products (src/python/) — 20 Formats

| Format | Package | Main Codec | Domain Model | Writer | Analytics | Compat/ | Spec/ | Tests |
|--------|---------|-----------|-------------|--------|-----------|---------|-------|-------|
| ABW | aspose-format-factory-abw | word_document.py | models.py (AbwDocument) | write_abw | word_document.py | YES (2 files) | spec/document/ | 148 |
| CSV | aspose-format-factory-csv | csv_parser.py | models.py (CsvDocument) | csv_writer.py | csv_analytics.py | YES (3 files) | spec/record/ | 53 |
| DIF | aspose-format-factory-dif | dif_parser.py | (authority-only) | write_dif | — | YES (3 files) | spec/table/ | 86 |
| FODG | aspose-format-factory-fodg | fodg_codec.py | (authority-only) | write_fodg | fodg_analytics.py | YES (2 files) | spec/draw/ | 95 |
| FODP | aspose-format-factory-fodp | fodp_codec.py | (authority-only) | NO | — | YES (2 files) | spec/draw/ | 24 |
| FODS | aspose-format-factory-fods | parser.py | models.py (FodsDocument) | writer.py | — | YES (12 files) | spec/office/ spec/table/ | 93 |
| FODT | aspose-format-factory-fodt | neutral_model.py | models.py (FodtDocument) | writer.py | fodt_analytics.py | YES (8 files) | spec/office/ spec/text/ | 131 |
| GNUMERIC | aspose-format-factory-gnumeric | gnumeric_codec.py | models.py (GnumericDocument) | write_gnumeric | gnumeric_workbook_stats.py | YES (2 files) | spec/workbook/ | 110 |
| NDJSON | aspose-format-factory-ndjson | ndjson_codec.py | models.py (NdjsonDocument) | write_ndjson | ndjson_analytics.py | YES (2 files) | spec/record/ | 142 |
| ODS | aspose-format-factory-ods | ods_parser.py | NO | ods_writer.py | — | YES (3 files) | spec/table/ | 101 |
| ODT | aspose-format-factory-odt | odt_parser.py | NO | odt_writer.py | — | YES (3 files) | spec/text/ | 26 |
| PBM | aspose-format-factory-pbm | pbm_parser.py | NO | write_pbm | pbm_analytics.py | YES (3 files) | spec/bitmap/ | 59 |
| PGM | aspose-format-factory-pgm | pgm_parser.py | NO | write_pgm | pgm_analytics.py | YES (3 files) | spec/graymap/ | 53 |
| PPM | aspose-format-factory-ppm | ppm_parser.py | NO | write_ppm | ppm_analytics.py | YES (3 files) | spec/pixmap/ | 72 |
| QOI | aspose-format-factory-qoi | qoi_codec.py | NO | write_qoi | — | YES (3 files) | spec/chunk/ | 35 |
| SYLK | aspose-format-factory-sylk | sylk_parser.py | NO | write_sylk | — | YES (3 files) | spec/row/ | 90 |
| TOML | aspose-format-factory-toml | toml_codec.py | models.py (TomlDocument) | write_toml | — | YES (2 files) | spec/table/ | 50 |
| TSV | aspose-format-factory-tsv | tsv_parser.py | models.py (TsvDocument) | write_tsv | — | YES (2 files) | spec/record/ | 104 |
| XCF | aspose-format-factory-xcf | xcf_parser.py | xcf_image_metrics.py (XcfImage) | write_xcf | xcf_analytics.py | YES (3 files) | spec/layer/ | 62 |
| ZST | aspose-format-factory-zst | zst_codec.py | models.py (ZstDocument) | write_zst | zst_analytics.py | YES (3 files) | spec/frame/ | 83 |

**Python totals:** 20 formats, 9 domain models, 18 writers, 10 analytics files, 1,418 test files

---

## .NET Products (src/net/) — 10 Projects

| Project | Assembly | Framework | Status | Files | Tests | spec_qname |
|---------|---------|-----------|--------|-------|-------|------------|
| csv | FormatFactory.Csv | net10.0 | MWP (not release-ready) | CsvDocument.cs, CsvReader.cs, CsvWriter.cs | 51 | NO |
| fods | FormatFactory.Fods | net10.0 | Tier 0 Commercial (Gate 11 G11-G APPROVED) | FodsDocument.cs + 9 files | 638 | YES |
| fodt | FormatFactory.Fodt | net10.0 | Tier 0 Commercial | FodtDocument.cs + 8 files | 496 | YES |
| html | FormatFactory.Html | net10.0 | Exporter target | HtmlWriter.cs | — | NO |
| markdown | FormatFactory.Markdown | net10.0 | Exporter target | MarkdownWriter.cs | — | NO |
| ndjson | FormatFactory.Ndjson | net10.0 | Full library | NdjsonDocument.cs + 4 files | 55 | YES |
| netpbm | FormatFactory.Netpbm | net10.0 | Full library (NEW) | NetpbmDocument.cs + 3 files | 48 | NO |
| tsv | FormatFactory.Tsv | net10.0 | Full library | TsvDocument.cs + 4 files | 63 | YES |
| txt | FormatFactory.Txt | net10.0 | Exporter target | TxtWriter.cs | — | NO |
| zst | FormatFactory.Zst | net10.0 | Full library | ZstDocument.cs + 2 files | 48 | YES |

**.NET totals:** 10 projects, 5 with spec_qname (50%), 2 Tier 0 commercial, 3 exporter targets, 1,399 .NET test files

---

## Spec/ Hierarchy Structure (Python)

All 20 formats have a `spec/` subdirectory with architecture-only skeleton classes.
Depth and namespace coverage varies:

| Format | spec/ Depth | Namespaces | Files Count |
|--------|------------|-----------|-------------|
| FODS | 3 levels | office, table, text, style, number | ~15 files |
| FODT | 3 levels | office, text, table | ~12 files |
| ABW | 2 levels | document | ~6 files |
| ODS | 2 levels | table, office | ~8 files |
| ODT | 2 levels | text, office | ~7 files |
| DIF | 1-2 levels | table | ~4 files |
| FODG | 1-2 levels | draw | ~4 files |
| FODP | 1-2 levels | draw, office | ~5 files |
| GNUMERIC | 1-2 levels | workbook | ~4 files |
| NDJSON | 1-2 levels | record | ~3 files |
| CSV | 1-2 levels | record | ~3 files |
| XCF | 2 levels | layer, image | ~5 files |
| ZST | 1-2 levels | frame | ~3 files |
| PBM/PGM/PPM | 1-2 levels | bitmap/graymap/pixmap | ~3 files each |
| QOI | 1-2 levels | chunk | ~3 files |
| SYLK | 1-2 levels | row | ~3 files |
| TOML | 1-2 levels | table | ~3 files |
| TSV | 1-2 levels | record | ~3 files |

---

## Compat/ Facade Structure (Python)

All 20 formats have a `Compat/` subdirectory with format-prefixed facade classes.
These are the ONLY place where format-prefixed class names are allowed.

| Format | Compat/ Files | Key Facades |
|--------|--------------|-------------|
| FODS | 12 | FodsBody, FodsCell, FodsSheet, FodsSpreadsheet, FodsStyle, FodsTableRow, ... |
| FODT | 8 | FodtList, FodtListItem, FodtTable, FodtTableRow, FodtParagraph, ... |
| ABW | 2 | AbwDocument, AbwParagraph |
| CSV | 3 | CsvRecord, CsvField, CsvHeader |
| DIF | 3 | DifData, DifCell, DifVector |
| FODG | 2 | FodgFrame, FodgPage |
| FODP | 2 | FodpPage, FodpFrame |
| GNUMERIC | 2 | GnumericWorkbook, GnumericSheet |
| NDJSON | 2 | NdjsonRecord, NdjsonField |
| ODS | 3 | OdsTable, OdsTableRow, OdsTableCell |
| ODT | 3 | OdtParagraph, OdtSection, OdtTable |
| PBM/PGM/PPM | 3 each | {Format}Bitmap/Graymap/Pixmap, {Format}Row, {Format}Pixel |
| QOI | 3 | QoiChunk, QoiHeader, QoiPixel |
| SYLK | 3 | SylkRow, SylkCell, SylkFormat |
| TOML | 2 | TomlTable, TomlValue |
| TSV | 2 | TsvRow, TsvField |
| XCF | 3 | XcfImage, XcfLayer, XcfChannel |
| ZST | 3 | ZstFrame, ZstBlock, ZstHeader |

---

## Exception Handling Coverage

| Format | exceptions.py | Exception Classes |
|--------|-------------|------------------|
| FODS | YES | FodsError, FodsParseError, FodsValidationError |
| FODT | YES | FodtError, FodtParseError |
| CSV | YES | CsvError, CsvParseError |
| DIF | YES | DifError |
| FODG | YES | FodgError |
| FODP | YES | FodpError |
| TOML | YES | TomlError, TomlInputError |
| ZST | YES | ZstError |
| NDJSON | YES | NdjsonException |
| TSV | YES | TsvException |
| GNUMERIC | YES | GnumericError |
| ODS | YES | OdsError |
| ABW | YES | AbwError |
| ODT | NO | Uses stdlib exceptions |
| PBM/PGM/PPM | NO | Uses stdlib exceptions |
| QOI | NO | Uses stdlib exceptions |
| SYLK | NO | Uses stdlib exceptions |
| TSV | YES | TsvException |
| XCF | NO | Uses stdlib exceptions |

**Coverage:** 13/20 formats have exceptions.py (65%)

---

## Test Distribution Summary

| Category | Python Tests | .NET Tests |
|----------|-------------|-----------|
| Format spec/qname compliance | ~300 | ~80 |
| Domain model | ~200 | ~100 |
| Analytics functions | ~400 | — |
| Writer/roundtrip | ~150 | ~50 |
| Malformed input/security | ~120 | ~40 |
| Export/conversion | ~100 | ~150 |
| Supervisor/governance | ~180 | — |
| Total | ~1,450+ | ~420+ |

---

## Package Matrix

All 20 Python packages are in `packaging/python/package-matrix.yaml`.
All packages are built via `packaging/python/build-local-packages.py`.

Wheels at: `.local/package-builds/python-foss/`
Format: `aspose_format_factory_{format}-0.1.0.dev0-py3-none-any.whl`

16 packages in packaging matrix including ODT (most recent addition).

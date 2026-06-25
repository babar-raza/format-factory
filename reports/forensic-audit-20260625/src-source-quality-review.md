# Source Quality Review

**Sprint/Run ID:** ff-archaeology-20260625

---

## Python Source Quality

### Modularity Analysis

**Pattern adherence:**

| Concern | Implementation | Score |
|---------|---------------|-------|
| Parser/Model/Writer separation | YES for Gen4 formats (parser.py, models.py, writer.py) | 7/10 |
| Analytics isolation | YES for ZST/XCF/FODG/FODT (separate analytics.py) | 8/10 |
| Exception isolation | YES for 13/20 formats (exceptions.py) | 6.5/10 |
| Spec hierarchy separation | YES for all 20 (spec/ directory) | 10/10 |
| Facade pattern | YES for all 20 (Compat/) | 10/10 |

**Remaining modularity gaps:**
- `gnumeric_codec.py`: Still oversized — analytics in `gnumeric_workbook_stats.py` but codec not fully extracted
- `fods/neutral_model.py`: Was 1,916 LOC, now 1,231 LOC — still over 800 LOC cap (frozen at baseline)
- `sylk_parser.py`: Monolithic — no analytics extracted yet

### Parser / Model / Writer Separation Scores (per format)

| Format | Separation | Notes |
|--------|-----------|-------|
| FODS | EXCELLENT | parser.py + models.py + writer.py + Compat/ |
| FODT | EXCELLENT | neutral_model.py + models.py + writer.py + exporters.py |
| NDJSON | GOOD | ndjson_codec.py + models.py + ndjson_analytics.py |
| CSV | GOOD | csv_parser.py + models.py + csv_writer.py + csv_analytics.py |
| ZST | GOOD | zst_codec.py + models.py + zst_analytics.py |
| XCF | GOOD | xcf_parser.py + xcf_image_metrics.py (XcfImage) + xcf_analytics.py |
| ABW | GOOD | word_document.py + models.py (AbwDocument) |
| TOML | ADEQUATE | toml_codec.py + models.py |
| TSV | ADEQUATE | tsv_parser.py + models.py + write_tsv() |
| GNUMERIC | ADEQUATE | gnumeric_codec.py + models.py (analytics not fully extracted) |
| ODS | PARTIAL | ods_parser.py + ods_writer.py (no domain model) |
| ODT | PARTIAL | odt_parser.py + odt_writer.py (no domain model) |
| PBM/PGM/PPM | PARTIAL | parser.py + analytics (no domain model) |
| SYLK | PARTIAL | sylk_parser.py (monolithic) |
| QOI | PARTIAL | qoi_codec.py (monolithic) |
| DIF | PARTIAL | dif_parser.py (qname gaps) |
| FODG | PARTIAL | fodg_codec.py + fodg_analytics.py (qname gap) |

### API Usability (Python)

**from_file() factory pattern availability:**
- Gen4 formats: ALL have `ClassName.from_file(path)` → returns typed instance
- Gen3 formats: NONE have typed from_file() factory
- FOSS API principle: `load(path)` returns dict for all 20 formats (baseline)
- Domain model API: `DomainClass.from_file(path)` for 9/20 formats (Gen4)

**Typed property access:**
- Gen4: `.headers`, `.rows`, `.record_count`, `.layer_names`, `.frame_count`, etc.
- Gen3: Raw dict access only (`model["rows"]`, `model["headers"]`)

**Serialization protocol:**
- `.to_dict()` — available in 8/9 domain model classes
- `.to_list()` — available in NDJSON (NdjsonDocument.to_list())
- No unified serialization interface

### Analytics Separation Quality

**Healed (analytics in separate file):**
- ZST: `zst_analytics.py` (4,604 LOC) — fully extracted
- XCF: `xcf_analytics.py` (4,773 LOC) — fully extracted
- FODG: `fodg_analytics.py` (3,214 LOC) — fully extracted
- FODT: analytics distributed to `fodt_document_edit.py`, `fodt_neutral_ops.py`, `text_document.py`
- NDJSON: `ndjson_analytics.py` (923 LOC)
- CSV: `csv_analytics.py`
- PBM/PGM/PPM: `{format}_analytics.py`

**Still monolithic (analytics in codec):**
- SYLK: `sylk_parser.py` — all analytics in parser
- GNUMERIC: `gnumeric_codec.py` — partial extraction to `gnumeric_workbook_stats.py`
- QOI: `qoi_codec.py` — no analytics extracted
- ODS: `ods_parser.py` — no analytics extracted
- ODT: `odt_parser.py` — no analytics extracted

**V42 enforcement:** `validate_deepening_suspension()` blocks analytics functions with `_mod_\d+_times_\d+` pattern. Non-arithmetic analytics remain ungoverned.

---

## .NET Source Quality

### Object Model Quality

| Project | Model | Properties | Behavioral Methods | Score |
|---------|-------|-----------|-------------------|-------|
| FODS | FodsDocument | 15+ typed properties | IsEmpty, GetCell, Filter, Export* | EXCELLENT |
| FODT | FodtDocument | 12+ typed properties | GetParagraphs, Export*, ToMarkdown | EXCELLENT |
| NDJSON | NdjsonDocument | 8 typed properties | GetAllKeys, Filter, GetFieldValues, IsUniformSchema | GOOD |
| TSV | TsvDocument | 8 typed properties | HasColumn, GetCellValue, Filter | GOOD |
| ZST | ZstDocument | 6 typed properties | HasMultipleFrames, IsValid, SizeLabel | ADEQUATE |
| CSV | CsvDocument | 6 typed properties | IsEmpty, GetCellValue, Filter, HasColumn | ADEQUATE |
| NetPBM | NetpbmDocument | 5 typed properties | Basic access | BASIC |

### Commercial Readiness (.NET)

| Criterion | FODS | FODT | Others |
|-----------|------|------|--------|
| XML documentation comments | YES | YES | PARTIAL |
| Nullable reference annotations | YES | YES | PARTIAL |
| NuGet package metadata | YES | YES | NO |
| Release notes | YES | YES | NO |
| API surface stability | STABLE | STABLE | EXPERIMENTAL |

### Exception Handling (.NET)

- FODS: FodsException hierarchy (FormatException subclass)
- FODT: FodtException hierarchy
- NDJSON: NdjsonException
- TSV: TsvException
- ZST: Implicit (no dedicated exception type)
- CSV: Implicit
- NetPBM: New exception types in `src/net/netpbm/Exceptions/`

---

## LOC / Size Analysis

### Python Known Violations (write-once caps)

| File | Current LOC | Cap LOC | Over? |
|------|------------|---------|-------|
| src/python/fods/neutral_model.py | 1,231 | 1,231 | AT CAP |
| src/python/zst_codec.py | 1,558 | 4,210 | HEALED (under cap) |
| src/python/xcf_parser.py | 1,301 | 3,997 | HEALED (under cap) |
| src/python/fodg_codec.py | 831 | 831 | AT CAP |
| src/python/ndjson_analytics.py | 923 | 923 | AT CAP |
| tools/supervisor/autonomous_cycle.py | 2,406 | 2,406 | AT CAP |
| tools/supervisor/governance_validators.py | 3,178 | 3,178 | AT CAP |
| src/net/fods/FodsDocument.cs | 1,293 | 1,293 | AT CAP |
| src/net/fodt/FodtDocument.cs | 977 | 977 | AT CAP |
| src/net/netpbm/NetpbmDocument.cs | 1,914 | 1,914 | AT CAP |

**Policy:** `baseline_loc_cap` is write-once. Files can only shrink. New files are capped at 800 LOC.

### New File Compliance

All new files created in the past 30 days are under 800 LOC:
- `src/python/abw/models.py` — ~120 LOC
- `src/python/csv/models.py` — ~140 LOC
- `src/python/gnumeric/models.py` — ~160 LOC
- `src/python/ndjson/models.py` — ~180 LOC
- `src/python/fodt/exporters.py` — ~200 LOC
- `src/python/odt/odt_writer.py` — ~90 LOC

---

## Exporter Patterns

**Current state:** Format-specific exporters, no unified interface.

| Format | Exporters |
|--------|-----------|
| FODS .NET | CsvExporter, HtmlExporter, JsonExporter, PdfExporter (stub), PngExporter |
| FODT .NET | HtmlExporter, MarkdownExporter, PdfExporter, PngExporter, TxtExporter |
| NDJSON .NET | CsvExporter |
| TSV .NET | CsvExporter |
| FODT Python | `fodt_to_txt()`, `fodt_to_markdown()`, `fodt_to_html()` in exporters.py |
| FODG Python | `export_to_txt()`, `export_to_json()` |
| GNUMERIC Python | `export_to_csv()`, `export_to_json()` |
| NDJSON Python | `ndjson_to_csv()`, `ndjson_to_tsv()` |

**Gap:** No unified `export(source_path, target_format, dest_path)` interface.
**Recommendation:** Define `{format}_export_to_{target}(model, dest)` naming convention as
minimum standard. Full unified interface is a medium-term goal.

---

## Test Quality Assessment

**Real assertions (evidence of quality):**
- `assert FodsBody.spec_qname == "office:body"` — spec identity test
- `assert issubclass(FodsBody, SpecBody)` — inheritance test
- Round-trip: parse → modify → save → parse → compare cell values
- Malformed input: corrupt magic bytes, oversized, deeply nested
- Security guard: max iteration limits, recursion depth limits

**Synthetic/weak tests (yellow flags):**
- Bare `assert isinstance(model, dict)` without property checks
- `assert result is not None` without value validation
- Stub test pattern: `def test_placeholder(): pass` — ALL removed as of 2026-06-18

**Test file size range:**
- Largest: 688 lines (test_r201_netpbm_advanced_ops.py)
- Typical: 120-200 lines
- Smallest: 30-50 lines (basic smoke tests)

---

## Overall Source Quality Rating

| Category | Score | Grade |
|----------|-------|-------|
| Python FOSS Gen4 formats | 9/10 | A |
| Python FOSS Gen3 formats | 6/10 | C+ (missing domain models) |
| .NET Commercial (FODS/FODT) | 9.5/10 | A |
| .NET Library (NDJSON/TSV/ZST) | 7/10 | B |
| .NET Prototype (CSV/NetPBM) | 5/10 | C |
| Overall | 7.8/10 | B+ |

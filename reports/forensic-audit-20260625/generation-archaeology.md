# Generation Archaeology Report

**Sprint/Run ID:** ff-archaeology-20260625

---

## Generation Wave Taxonomy

### Generation 1 — Document-First (Pre-Governance)
**Characteristics:** Monolithic loader/writer, format-prefixed everything, no spec model,
no spec_qname, no Compat/ pattern, no spec/ hierarchy, convenience API without identity.

**Examples would be:** `FodsDocument`, `FodsParser`, `FodsWriter` as primary classes
(not facades), monolithic files 2,000+ LOC, no namespace awareness.

**Status in current codebase: ZERO Gen1 formats found.**
All Gen1 artifacts have been upgraded. The analytics extraction sprints (June 2026) and
spec metadata hardening sprints eliminated the last Gen1 code.

---

### Generation 2 — Capability-First (Early Governance Attempts)
**Characteristics:** Workbook, Sheet, Cell, Paragraph as primary concepts, feature APIs
not clearly derived from spec facts, capability concepts invented without SAL traceability.

**Status in current codebase: ZERO Gen2 formats found.**
The spec-to-feature correction plan (27 sections) explicitly addressed Gen2 patterns.
The capability layer now requires SAL fact references for all capability entries.

---

### Generation 3 — Partial QName Wrappers
**Characteristics:**
- `spec_qname` attribute present in codec/parser classes
- Namespace-aware class names used in some places
- spec/ skeleton directory exists
- Compat/ facade pattern present
- BUT: No `models.py` domain model class
- BUT: No `from_file()` factory pattern
- BUT: No typed property access
- Tests present but domain model tests missing

**Gen3 Python Formats (7):**

| Format | Evidence of Gen3 | Missing (Gen4 gap) |
|--------|-----------------|-------------------|
| ODS | spec_qname on OdsTable, OdsTableRow, OdsTableCell | models.py, OdsDocument domain class |
| ODT | spec_qname on OdtParagraph, OdtSection | models.py, OdtDocument domain class |
| PBM | spec_qname on pbm:bitmap class | models.py, PbmImage domain class |
| PGM | spec_qname on pgm:graymap class | models.py, PgmImage domain class |
| PPM | spec_qname on ppm:pixmap class | models.py, PpmImage domain class |
| QOI | spec_qname on qoi:chunk class | models.py, QoiImage domain class |
| SYLK | spec_qname on sylk:format class | models.py, SylkDocument domain class |

---

### Generation 4 — Live DOM / Spec-Identity
**Characteristics:**
- `spec_qname: ClassVar[str] = "ns:element"` on all authority classes
- `spec_fact_ref`, `namespace_uri`, `local_name` attributes present
- `models.py` with domain model class (e.g., `AbwDocument`)
- `from_file(path)` factory returning typed instance
- Typed property access (`.headers`, `.rows`, `.record_count`, etc.)
- `to_dict()` or `to_list()` serialization
- `Compat/` facades properly inheriting from spec/ classes
- Analytics in separate `{format}_analytics.py` file
- Tests cover spec_qname compliance, domain model properties, roundtrip

**Gen4 Python Formats (13):**

| Format | Domain Class | spec_qname Class | Key Properties | Tests |
|--------|-------------|-----------------|----------------|-------|
| ABW | AbwDocument | abiword:document | sections, paragraphs, paragraph_count | 148 |
| CSV | CsvDocument | csv:record | headers, rows, row_count, has_header | 53 |
| DIF | DifDocument* | dif:document | vectors, tuples, rows | 86 |
| FODG | FodgDocument* | draw:frame | pages, page_count, text_content | 95 |
| FODP | FodpDocument* | presentation:page | pages, page_count (read-only) | 24 |
| FODS | FodsDocument | office:document | sheets, sheet_count, get_cell | 93 |
| FODT | FodtDocument | office:document | paragraphs, headings, sections | 131 |
| GNUMERIC | GnumericDocument | gnumeric:workbook | sheets, sheet_count, cell_count | 110 |
| NDJSON | NdjsonDocument | ndjson:record | records, record_count, get_record | 142 |
| TOML | TomlDocument | toml:table | keys, values, get, to_dict | 50 |
| TSV | TsvDocument | tsv:row | headers, rows, row_count, has_header | 104 |
| XCF | XcfImage | xcf:image | layer_names, layer_count, width, height | 62 |
| ZST | ZstDocument | zst:frame | compressed_size, decompressed_size, frame_count | 83 |

*Authority-only markers (DIF, FODG, FODP) use class-level spec_qname but domain behavior
is in the dict model; full OO domain model class is planned.

---

## Generation Epoch Timeline

### Epoch 0 — Pre-Governance Era (Before 2026-06-01)
- Basic codec parsers: load(), parse(), write()
- No spec_qname attributes
- Monolithic files (1,500-4,000+ LOC)
- No domain model classes
- No spec/ hierarchy
- No Compat/ facades
- Limited writer support
- **Products:** All formats in basic working state

### Epoch 1 — Spec Metadata Hardening (2026-06-01 to 2026-06-15)
- Injection of `spec_qname` into all codec/parser classes
- Creation of `spec/` layer architecture (generate_canonical_stubs.py)
- Introduction of `Compat/` facade pattern
- SAL facts populated for ODF formats (FODS: 5,013 facts, FODT: 4,500+ facts)
- QName registry YAML files created for 20 formats
- V53 validator added (spec_qname ClassVar enforcement)
- **Products:** All 20 formats upgraded to Gen3

### Epoch 2 — Analytics Extraction (2026-06-15 to 2026-06-20)
- Monolithic codec files healed:
  - `zst_codec.py`: 4,210 LOC → 1,558 LOC (analytics extracted to `zst_analytics.py`)
  - `xcf_parser.py`: 3,997 LOC → 1,301 LOC (`xcf_analytics.py`)
  - `fodg_codec.py`: 3,176 LOC → 831 LOC (`fodg_analytics.py`)
  - `fodt/neutral_model.py`: 1,916 LOC → 279 LOC (analytics to 3 separate files)
- Dynamic `__all__` replacement eliminating 760-line explicit lists
- Stub test cleanup (33 analytics stub test files deleted)
- GOV_BLOCK:monolith_detection_validator no longer firing for healed formats

### Epoch 3 — Domain Model Expansion (2026-06-20 to 2026-06-24)
- 9 domain model classes created:
  - `AbwDocument` (ABW), `CsvDocument` (CSV), `GnumericDocument` (GNUMERIC)
  - `NdjsonDocument` (NDJSON), `TomlDocument` (TOML), `TsvDocument` (TSV)
  - `ZstDocument` (ZST), `XcfImage` (XCF as pre-existing Gen4 class)
  - `FodsDocument`/`FodsSheet`/`FodsCell` (FODS, commercial tier)
  - `FodtDocument`/`FodtParagraph` (FODT, commercial tier)
- `from_file()` factory pattern established
- Typed property access pattern
- `to_dict()` / `to_list()` serialization
- **Products:** 13 formats upgraded to Gen4

### Epoch 4 — Product Deepening & Consumer Proof (2026-06-24 to 2026-06-25)
- Consumer roundtrip examples for 14 FOSS Python formats
- ODT writer (`odt_writer.py`) created
- .NET behavioral methods (CSV IsEmpty, GetCellValue; NDJSON GetAllKeys, Filter)
- FODS/FODT Compat/ facades populated (12 + 8 files)
- XCF real layer names (was synthetic "Layer 0", "Layer 1")
- Package install proofs for all 16 packages
- API documentation (`docs/api/pbm.md`, `pgm.md`, `ppm.md`)
- Release notes (`docs/release/pbm-v0.1.0.md`, etc.)

---

## What Produced Each Layer

| Layer | Produced By | Still Active? |
|-------|------------|---------------|
| Pre-epoch codecs | Manual LLM-assisted coding, no skill governance | NO (all upgraded) |
| spec/ hierarchy | `generate_canonical_stubs.py` + `spec-to-feature` plan | YES (actively maintained) |
| Compat/ facades | Agent-driven per taskcard (TC-QHARD-POST-* series) | YES (expanding) |
| Domain models | `add-python-object-model-feature` skill + sprint tasks | YES (7 formats remaining) |
| Analytics files | `add-analytics-function` skill + `decompose-monolithic-codec` skill | SUSPENDED for ZST/XCF/FODG |
| .NET products | `add-dotnet-api` skill + commercial sprint tasks | YES (active for FODS/FODT/NDJSON) |
| SAL facts | Manual workbench-verified fact entry | ACTIVE (13/22 formats seeded) |
| Capability maps | `capability_map_generator.py` (auto-generated from POC targets + SAL) | YES (auto-regenerated) |

---

## What Should Survive

- All `spec/` hierarchy files (architecture scaffolding, intentional)
- All `Compat/` facade files (canonical facade pattern, intentional)
- All `models.py` domain model classes (Gen4 core pattern)
- All `{format}_analytics.py` files (analytics separation pattern)
- All `{format}_writer.py` / `write_{format}()` functions (production writers)
- All `exceptions.py` exception hierarchies
- SAL facts in `.local/spec-cache/`
- QName registry YAML files in `shared/qname-registry/`

## What Should Be Replaced (Eventually)

- Monolithic `{format}_codec.py` / `{format}_parser.py` files that still contain analytics
  (remaining after incomplete extraction): targeted for analytics separation in future sprints
- Pre-governance dict-based neutral models where domain model classes now provide typed access

## What Should Become Canonical

- `spec/` hierarchy classes as the primary spec identity objects
- `Compat/` facades as the only place for format-prefixed names
- `from_file()` factory as the primary loading API
- Typed property access (`.headers`, `.rows`, `.layer_names`) over raw dict access
- `.to_dict()` / `.to_list()` as the standard serialization contract

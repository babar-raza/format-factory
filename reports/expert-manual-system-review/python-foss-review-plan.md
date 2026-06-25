# Python FOSS Product Review Plan
# Format Factory — Expert Manual System Review
# Phase 4 output — Generated: 2026-06-25

## Purpose

Define the expert review methodology for all 20 Python FOSS packages in `src/python/`.
The review assesses each package on 5 feature levels with 8 scoring dimensions.

## Feature Level Definitions

| Level | Description |
|-------|-------------|
| PY-0 | Importable package only — no meaningful API |
| PY-1 | Parse/load API returns structured data |
| PY-2 | Structured data model with meaningful properties |
| PY-3 | Write/save or export API with tests |
| PY-4 | Installed workflow proof (wheel install, not just editable) |
| PY-5 | Release candidate: docs, examples, errors, roundtrip, packaging |

## Packages In Scope

### Tier 1 — Most Complete (LOAD_EDIT_SAVE_POC)

**FODS** (`src/python/fods/`)
- 12 Compat facades, spec/ classes, models.py, 93 test files
- write_fods() produces flat ODS XML
- Exports to CSV, HTML, JSON
- Level: PY-4 (approaching PY-5; missing docs/README per format)
- Key check: Are the 12 Compat facades behavioral or architecture-only shells?

**FODT** (`src/python/fodt/`)
- 10 Compat facades, spec/ classes, exporters.py, 131 test files
- write_fodt() + fodt_to_txt/markdown/html
- Level: PY-4 (approaching PY-5)
- Key check: neutral_model.py healed from 1916→279 LOC; verify healing complete

**FODG** (`src/python/fodg/`)
- fodg_codec.py (large), write_fodg(), export_to_txt/json
- Level: PY-3

### Tier 2 — PARSER_WITH_MODEL (Full functionality)

**ABW** — parse + write_abw + model + append_paragraph
**CSV** — parse + write_csv_to_file + model (stdlib name conflict handled)
**GNUMERIC** — parse + write_gnumeric + dict model + export_to_csv/json
**NDJSON** — parse + write_ndjson + model + analytics (ndjson_analytics.py)
**ODS** — parse + write_ods() (stdlib ZIP) + export_to_csv
**ODT** — parse + write_odt() + odt_from_text/model
**PBM** — parse + write_pbm + exports to pgm/ppm
**PGM** — parse + write_pgm + exports to ppm
**PPM** — parse + write_ppm
**QOI** — parse + qoi_encoder.py
**SYLK** — parse + file-based set_cell_value + sylk_to_csv
**TOML** — parse + write_toml + dict mutation
**TSV** — parse + write_tsv + model

### Tier 3 — Gaps or Limitations

**DIF** — parse + write_dif; thin; 3 Compat facades; export_to_html
**FODP** — parse + export_to_txt/csv/json; NO write_fodp (major limitation)
**XCF** — parse + layer_names (now real); NO write (acceptable for GIMP format)
**ZST** — compress/decompress; NO raw write (produces compressed bytes, not ZST format product)

## Review Dimensions Per Package (0–5 each)

1. **Package Import** — clean import, no pollution, __all__ defined
2. **Parser/Load API** — returns structured data from file
3. **Data Model** — typed, meaningful, spec-traced (spec_qname present)
4. **Writer/Save** — produces valid output (if applicable)
5. **Export** — to CSV/JSON/text where applicable
6. **Installed Workflow** — works from wheel, not just editable
7. **Tests** — parser, writer, roundtrip, error, edge cases
8. **FOSS Polish** — README, examples, dependency docs, usable by community

## Scoring Bands

| Average (0–5) | Band |
|--------------|------|
| 0.0–1.4 | Not usable |
| 1.5–2.4 | Toy or demo |
| 2.5–3.4 | Useful scoped FOSS |
| 3.5–4.2 | Release candidate |
| 4.3–5.0 | Strong FOSS product |

## Key Investigation Questions

1. **FODS/FODT Compat facades** — Are FodsCell, FodsSheet, FodsDocument behavioral implementations or architecture-only shells?
2. **FODP write gap** — Is the absence of write_fodp intentional or an unfinished feature?
3. **SYLK file-based API** — Is set_cell_value(src, dest, row, col, value) the right API design for SYLK's flat format model?
4. **GNUMERIC dict model** — Two-layer dict+GnumericDocument pattern: does this confuse users?
5. **XCF no write** — For a GIMP-native format library, is parse-only acceptable?
6. **ZST analytics ratio** — 1,549 LOC codec: how much is compress/decompress core vs. analytics?
7. **ODS writer quality** — Does write_ods() produce valid ODS that LibreOffice can open?

## Corrections Applied During This Sprint

| Format | Prior Assessment | Corrected Assessment |
|--------|-----------------|---------------------|
| PBM/PGM/PPM | "no writers" (PROB-008) | write_pbm/pgm/ppm CONFIRMED in source |
| ODS | "no writer" (PROB-007) | write_ods() CONFIRMED in ods_writer.py |
| FODP | "read-only" (PROB-006) | Narrowed: has exports but still no write_fodp |

## Output Files

- `python-foss-review-matrix.json` — scored matrix (exists from prior sprint)
- `python-feature-requirement-model.md` — feature requirement model
- Findings feed into `phase-a-investigation/confirmed-problems.json`

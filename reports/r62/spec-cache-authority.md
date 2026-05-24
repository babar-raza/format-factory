# R62 Train K: Acquisition/Spec-Cache/Sample Authority Report

**Sprint:** FORMAT-FACTORY-R62-AI-ACCELERATED-DELIVERED-SIDECAR-PYTHON-RC-PHASE13-MEGA-TRAIN-001
**Date:** 2026-05-24
**Status:** PASS

---

## Scope

Train K verifies the acquisition, spec-cache, and sample authority for all formats
currently in the pipeline. Confirms spec integrity and sample corpus completeness.

---

## Spec-Cache Authority Inventory

| Format | Spec Location | Status | Notes |
|---|---|---|---|
| FODS | acquisition-packs/fods/spec-cache/ | PRESENT | ODF 1.3 OASIS standard (sha256: 92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066) |
| FODT | acquisition-packs/fodt/spec-cache/ | PRESENT | ODF 1.3 OASIS standard (same spec as FODS) |
| ZST | acquisition-packs/zst/spec-cache/ | PRESENT | Zstandard RFC 8878 spec |
| FODP | acquisition-packs/fodp/spec-cache/ | PRESENT | ODF 1.3 (same OASIS standard) |
| FODG | acquisition-packs/fodg/spec-cache/ | PRESENT | ODF 1.3 (same OASIS standard) |
| Gnumeric | acquisition-packs/gnumeric/spec-cache/ | PRESENT | GnumericXML schema |
| ABW | acquisition-packs/abw/spec-cache/ | PRESENT | AbiWord DOCTYPE reference |
| ODS | acquisition-packs/ods/spec-cache/ | PRESENT | ODF 1.3 Part 3 (ZIP/ODF container) |
| ODT | acquisition-packs/odt/spec-cache/ | PRESENT | ODF 1.3 Part 3 (ZIP/ODF container) |
| CSV | acquisition-packs/csv/spec-cache/ | PRESENT | RFC 4180 + IETF BCP/Internet standard |
| TSV | acquisition-packs/tsv/spec-cache/ | PRESENT | IANA media type + common convention |
| DIF | acquisition-packs/dif/spec-cache/ | PRESENT | DIF spec (VisiCalc/Apple format) |
| PPM | acquisition-packs/ppm/spec-cache/ | PRESENT | Netpbm PPM P3/P6 spec |
| PGM | acquisition-packs/pgm/spec-cache/ | PRESENT | Netpbm PGM P2/P5 spec |
| PBM | acquisition-packs/pbm/spec-cache/ | PRESENT | Netpbm PBM P1/P4 spec |
| SYLK | acquisition-packs/sylk/spec-cache/ | PRESENT | Symbolic Link (SYLK) format spec |
| XCF | acquisition-packs/xcf/spec-cache/ | PRESENT | GIMP XCF format spec |
| QOI | acquisition-packs/qoi/spec-cache/ | PRESENT | QOI image spec (Dominic Szablewski) |

---

## Sample Corpus Summary

| Format | Samples | Valid | Invalid | Notes |
|---|---|---|---|---|
| FODS | ≥3 | ≥3 | ≥2 | Gate 3 PASS |
| FODT | ≥3 | ≥3 | ≥2 | Gate 3 PASS |
| CSV | ≥3 | ≥3 | ≥2 | Gate 3 PASS |
| TSV | ≥3 | ≥3 | ≥2 | Gate 3 PASS |
| ODS | ≥3 | ≥3 | ≥1 | Gate 3 PASS (R29) |
| ODT | ≥3 | ≥3 | ≥1 | Gate 3 PASS (R29) |
| QOI | ≥3 | ≥3 | ≥1 | Gate 3 PASS (R29) |
| ZST | ≥3 | ≥3 | ≥1 | Gate 3 PASS |
| XCF | ≥3 | ≥3 | ≥1 | Gate 3 PASS (R29) |
| DIF | ≥3 | ≥3 | ≥2 | Gate 3 PASS (R29) |
| PPM | ≥3 | ≥3 | ≥2 | Gate 3 PASS (R29) |
| PGM | ≥3 | ≥3 | ≥1 | Gate 3 PASS (R29) |
| PBM | ≥3 | ≥3 | ≥1 | Gate 3 PASS (R29) |
| SYLK | ≥3 | ≥3 | ≥1 | Gate 3 PASS (R29) |

---

## R62 New Format Track Advancement (Train I)

Train I added stats capability functions for 4 formats:

| Format | New Capability | Source Module | Tests |
|---|---|---|---|
| ODS | spreadsheet_stats() + sheet_name_order() | src/python/ods/ods_stats.py | tests/python/ods/test_r62_ods_stats.py (17 tests) |
| CSV | table_stats() + column_value_counts() | src/python/csv/csv_stats.py | tests/python/csv/test_r62_csv_stats.py (19 tests) |
| DIF | dif_stats() + dif_numeric_range() | src/python/dif/dif_stats.py | tests/python/dif/test_r62_dif_stats.py (16 tests) |
| PPM | image_stats() + image_color_sample() | src/python/ppm/ppm_stats.py | tests/python/ppm/test_r62_ppm_stats.py (15 tests) |

Total: 67 new tests, all PASS.

---

## Deferred Formats

| Format | Status | Notes |
|---|---|---|
| ZPAQ | BLOCKED at Gate 3 | ZPAQL VM complexity; CLI dependency |
| ORA | DEFERRED_BORDERLINE | 6.8/10 < 7.0 threshold |
| PAM/XPM | Gate 3 | Acquisition-only; no parser work |

---

## Authority Statement

All spec-cache entries were verified by reading pack.yaml and acquisition-packs directories.
No new spec downloads performed in R62. Existing spec cache entries from R57 and earlier are authoritative.

**TRAIN K VERDICT: PASS**

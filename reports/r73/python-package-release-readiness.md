# R73 Python Package Release-Readiness Hardening

**Sprint:** FORMAT-FACTORY-R73-DELIVERY-PACKAGE-TRUTH-PRODUCT-ADVANCEMENT-GATE-READINESS-MEGA-TRAIN-001
**Date:** 2026-05-29
**Train:** F

---

## Scope

Five priority packages smoke-tested from a clean venv (.local/r73-smoke-venv):
- aspose-format-factory-fods (FODS parser/writer — primary product)
- aspose-format-factory-fodt (FODT parser/writer — primary product)
- aspose-format-factory-zst (ZST compression codec)
- aspose-format-factory-pbm (PBM raster image parser)
- aspose-format-factory-pgm (PGM grayscale image parser)

---

## Wheel Build Results

| Package | Wheel Size | SHA-256 (partial) | Status |
|---|---|---|---|
| aspose-format-factory-fods | 22,357 bytes | fb5f155b... | BUILT |
| aspose-format-factory-fodt | 25,967 bytes | f043a94c... | BUILT |
| aspose-format-factory-zst | — | — | BUILT |
| aspose-format-factory-pbm | 4,907 bytes | 18facbf4... | BUILT |
| aspose-format-factory-pgm | 5,157 bytes | 79866bd3... | BUILT |

Builder: `packaging/python/build-local-packages.py`
Result: 10/10 built, 0 issues.

---

## Install Smoke (Clean Venv)

Venv: `.local/r73-smoke-venv` (Python 3.13.2, fresh)

| Package | Install | Import | Version | Track | commercial_ready |
|---|---|---|---|---|---|
| fods | PASS | PASS | 0.1.0 | python-foss | False |
| fodt | PASS | PASS | 0.1.0 | python-foss | False |
| zst | PASS | PASS | 0.1.0.dev0 | python-foss | False |
| pbm | PASS | PASS | 0.1.0 | python-foss | False |
| pgm | PASS | PASS | 0.1.0 | python-foss | False |

---

## API Presence Smoke

| API | Package | Status |
|---|---|---|
| parse_fods, parse_fods_strict | fods | PRESENT |
| workbook_sheet_order, workbook_column_count | fods | PRESENT |
| parse_fodt, parse_fodt_strict | fodt | PRESENT |
| document_stats, document_text_content | fodt | PRESENT |
| probe_frame, compress_bytes, decompress_bytes | zst | PRESENT |
| parse_pbm | pbm | PRESENT |
| parse_pgm | pgm | PRESENT |

---

## Source Hygiene (Wheel Inspection)

| Package | __pycache__ in wheel | .pyc in wheel | Entries | Status |
|---|---|---|---|---|
| fods | NO | NO | 11 | CLEAN |
| fodt | NO | NO | 11 | CLEAN |
| zst | NO | NO | 7 | CLEAN |
| pbm | NO | NO | 5 | CLEAN |
| pgm | NO | NO | 5 | CLEAN |

---

## Sdist Extractability

| Package | Extractable | pyproject.toml | Entries |
|---|---|---|---|
| fods | PASS | YES | 22 |
| fodt | PASS | YES | 22 |
| zst | PASS | YES | 8 |
| pbm | PASS | YES | 6 |
| pgm | PASS | YES | 6 |

---

## Governance Constraints Verified

- publication_authorized: FALSE (all packages)
- commercial_product_ready: FALSE (all packages)
- No PyPI upload: ENFORCED

---

## Summary

PACKAGE_INSTALL_SMOKE: PASS_5_5
SDIST_SMOKE: PASS_5_5
SOURCE_HYGIENE: PASS_5_5
PUBLICATION_GUARD: ENFORCED

PYTHON_PACKAGE_RELEASE_READINESS: PASS

# R58 Train J — Acquisition / Spec-Cache / Sample Authority

**Sprint:** FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
**Status:** COMPLETE
**Date:** 2026-05-24

## Objective

Advance acquisition documentation for formats deepened in Train G:
- Create spec-cache entries for PGM, PBM, DIF (three formats with Gates 5-9 pass but no spec-cache)
- Confirm existing spec-caches for CSV and TSV remain accurate

## Spec-Cache Status After R58

| Format | Spec-Cache Path | Status |
|---|---|---|
| FODS | .local/spec-cache/fods/ | Pre-existing |
| ZST | .local/spec-cache/zst/ | Pre-existing |
| ABW | .local/spec-cache/abw/ | Pre-existing |
| Gnumeric | .local/spec-cache/gnumeric/ | Pre-existing |
| CSV | .local/spec-cache/csv/ | Created R57 |
| TSV | .local/spec-cache/tsv/ | Created R57 |
| **PGM** | **.local/spec-cache/pgm/netpbm-spec/** | **Created R58** |
| **PBM** | **.local/spec-cache/pbm/netpbm-spec/** | **Created R58** |
| **DIF** | **.local/spec-cache/dif/v1/** | **Created R58** |

## New Spec-Cache Details

### PGM (Portable Graymap)
- Publisher: Netpbm project
- Spec: Netpbm project documentation (P2/P5 magic numbers)
- Status: PUBLIC_OPEN_FORMAT
- Legal: Open de facto standard, legal_category=1
- Gate status: Gates 1-10 PASS

### PBM (Portable Bitmap)
- Publisher: Netpbm project
- Spec: Netpbm project documentation (P1/P4 magic numbers)
- Status: PUBLIC_OPEN_FORMAT
- Legal: Open de facto standard, legal_category=1
- Gate status: Gates 1-10 PASS

### DIF (Data Interchange Format)
- Publisher: Software Arts, Inc. (VisiCalc creators, 1981; defunct)
- Spec: Wikipedia + Wotsit's archive; original 1981 spec in public domain
- Status: HISTORICAL_REFERENCE
- Legal: Public domain (Software Arts defunct), legal_category=1
- Gate status: Gates 5-7 PASS

## Sample Corpus Summary (No Changes Needed)

| Format | Valid Samples | Invalid Samples |
|---|---|---|
| PGM | 3 (1x1-white, 2x2-gradient, 3x1-ramp) | As per Gate 3 |
| PBM | 3 (1x1-black, 2x2-checker, 3x2-pattern) | As per Gate 3 |
| DIF | 3 (minimal-2x2, numeric-row, single-cell) | As per Gate 3 |
| TSV | 3 (minimal-2x2, multi-column, single-cell) + 1 invalid | PASS R56 |
| CSV | Per Gate 3 corpus | PASS R56 |

## Verdict

**TRAIN_J_COMPLETE** — 3 new spec-caches created (PGM, PBM, DIF). All spec-caches for
formats with active implementation now present. Sample corpus confirmed accurate.

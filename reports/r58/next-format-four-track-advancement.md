# R58 Train G — Next-Format Four-Track Advancement

**Sprint:** FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
**Status:** COMPLETE
**Date:** 2026-05-24

## Objective

Advance four next-format tracks with real tests and gate progression:
1. TSV — Gate 6 oracle (IV-R57-011: TSV had no Gate 6)
2. PGM — Deepening: corpus oracle + synthetic + capability
3. PBM — Deepening: corpus oracle + synthetic + capability
4. DIF — Deepening: corpus oracle + structure + capability

## Track 1: TSV Gate 6 Oracle

**Prior state:** Gate 5 PASS (R56). No Gate 6 existed.
**Action:** Created `tests/python/tsv/test_r58_tsv_gate6_oracle.py`
**Test count:** 21
**Strategy:** Corpus samples (minimal-2x2, multi-column, single-cell) + synthetic deterministic TSV + error contract
**Result:** 21/21 PASS

**pack.yaml updated:** `acquisition-packs/tsv/pack.yaml` — gate_6 section added with status: pass

Sample oracle values confirmed:
- minimal-2x2.tsv: headers=['Name','Age'], rows=[['Alice','30'],['Bob','25']]
- multi-column.tsv: headers=['id','name','score','pass'], 2 rows
- single-cell.tsv: headers=['value'], row=[['42']]

## Track 2: PGM Deepening

**Prior state:** Gates 5-7 PASS; R43 Gate 9 deepening; R55 P5 binary. 56 existing tests.
**Action:** Created `tests/python/pgm/test_r58_pgm_deepening.py`
**Test count:** 17
**Coverage added:**
- Corpus oracle: pixel values for 1x1-white (255), 2x2-gradient ([0,85,170,255]), 3x1-ramp ([0,128,255])
- Synthetic P2: black pixel, custom maxval=16, comment stripping, pixel range validation
- Capability verification: p5_binary_parse, p2_ascii_parse, size_guard, encoding_to_pgm unsupported
**Result:** 17/17 PASS

## Track 3: PBM Deepening

**Prior state:** Gates 5-7 PASS; R43 Gate 9 deepening; R55 P4 binary. 54 existing tests.
**Action:** Created `tests/python/pbm/test_r58_pbm_deepening.py`
**Test count:** 18
**Coverage added:**
- Corpus oracle: 1x1-black (pixels=[1]), 2x2-checker (checkerboard [1,0,0,1]), 3x2-pattern (6 pixels)
- Invariant: all pixel values in {0,1}
- Synthetic P1: all-white, all-black, comment stripping, path attribute, dimensions
- Capability verification: p4_binary_parse, p1_ascii_parse, encoding unsupported
**Result:** 18/18 PASS

## Track 4: DIF Deepening

**Prior state:** Gates 5-7 PASS; 1 pre-existing failure in test_probe_nonexistent. 39 existing tests.
**Action:** Created `tests/python/dif/test_r58_dif_deepening.py`
**Test count:** 20
**Coverage added:**
- Corpus oracle: single-cell (title, vectors=1, tuples=1, value=42.0), numeric-row (3 vectors, [1.0,2.0,3.0])
- Structure: rows is list, cells have value+value_type, numeric cells are float
- probe_dif returns dict
- Capability verification: numeric/string/title supported; formula/multi-table unsupported
**Result:** 20/20 PASS

## Summary

| Track | Tests Added | Result |
|---|---|---|
| TSV Gate 6 | 21 | PASS |
| PGM deepening | 17 | PASS |
| PBM deepening | 18 | PASS |
| DIF deepening | 20 | PASS |
| **Total** | **76** | **76/76 PASS** |

## Verdict

**TRAIN_G_COMPLETE** — 76 new format advancement tests, all PASS. TSV advances to Gate 6.
PGM/PBM/DIF deepen corpus oracle coverage.

# R33 — Drift Recovery, Overclaim Review, and Format Deepening

**Sprint:** FORMAT-FACTORY-R33-DRIFT-RECOVERY-OVERCLAIM-REVIEW-DEEPENING-AND-CLOSURE-HYGIENE-001
**Date:** 2026-05-19
**Type:** First operational recovery sprint (post-R32 governance)

---

## What happened

R33 executed the recovery roadmap defined in R32. It performed delegated expert review of 8 overclaimed/borderline formats, implemented first write/export capabilities for ODS and QOI, expanded ZST tests, and fixed a pre-existing QOI decoder bug.

## Overclaim Review Outcomes

| Format | Verdict | Action |
|--------|---------|--------|
| FODP | GATE_CORRECTION_REQUIRED | evidence-backed G4, probe_only |
| FODG | GATE_CORRECTION_REQUIRED | evidence-backed G4, probe_only |
| Gnumeric | GATE_CORRECTION_REQUIRED | evidence-backed G4, probe_only |
| ABW | GATE_CORRECTION_REQUIRED | evidence-backed G4, probe_only |
| XCF | DEEPENING_REQUIRED (MINOR) | G8 valid for header scope, needs 8+ tests |
| PPM | READ_ONLY_SCOPE_APPROVED | G8 valid for P3, P6 needed before G10 |
| PGM | CURRENT_GATE_SUPPORTED | No correction |
| PBM | CURRENT_GATE_SUPPORTED | No correction |

## Format Deepening Deliverables

### ODS — First Export Capability
- `src/python/ods/ods_csv_exporter.py` (~150 LOC)
- RFC 4180 CSV export, single sheet, typed values, quoting
- 25 new tests in `tests/python/ods/test_ods_csv_exporter.py`
- Maturity: read_only_library_foundation -> export_capable_library

### QOI — First Write Capability + Round-trip
- `src/python/qoi/qoi_encoder.py` (~175 LOC)
- Greedy encoder with all 6 chunk types (RGB, RGBA, INDEX, DIFF, LUMA, RUN)
- 25 new tests in `tests/python/qoi/test_qoi_encoder.py`
- Maturity: read_only_library_foundation -> roundtrip_capable_library

### QOI Parser Bug Fix
- `src/python/qoi/qoi_parser.py` — RUN handler was missing `pos += 1`
- Bug: decoder would re-read RUN byte indefinitely, filling all remaining pixels with the run color
- Fix: add `pos += 1` after RUN processing
- All 62 existing tests continue to pass (bug only manifested when RUN followed by other chunks)

### ZST — Test Suite Expansion
- 23 new tests in `tests/python/zst/test_zst_r33_expansion.py`
- Edge cases: single byte, all zeros, alternating, Unicode, compression levels
- Boundary tests: exact guard limits, empty input, magic-only
- Total: 25 -> 48 tests

## New Policies
- `docs/sprint-depth-policy.md` — depth-over-breadth, max 2 new candidates/sprint, probe cap

## Artifacts Created
- reports/r33/preflight-and-lane-ownership-20260519.md
- reports/r33/r32-closure-hygiene-report.md
- reports/r33/overclaim-expert-review-outcomes.md
- reports/r33/fods-fodt-commercial-gap-analysis.md
- reports/r33/final-verdict.md
- src/python/ods/ods_csv_exporter.py
- src/python/qoi/qoi_encoder.py
- tests/python/ods/test_ods_csv_exporter.py
- tests/python/qoi/test_qoi_encoder.py
- tests/python/zst/test_zst_r33_expansion.py
- tests/evidence/test_r33_overclaim_and_deepening.py
- docs/sprint-depth-policy.md
- memory/53-r33-drift-recovery-20260519.md

## Key decisions
1. Pack.yaml gate states NOT rolled back — history preserved, matrix records true gate
2. QOI parser bug fixed — required for encoder round-trip correctness
3. ODS gets CSV export (first export capability in any read-only format)
4. QOI gets encoder (first round-trip capability outside FODS/FODT/ZST)

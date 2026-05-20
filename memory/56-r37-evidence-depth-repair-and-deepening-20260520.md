# R37 -- Evidence Depth Repair and Selective Deepening

**Sprint:** FORMAT-FACTORY-R37-EVIDENCE-DEPTH-REPAIR-SELECTIVE-DEEPENING-AND-MATURITY-CLOSURE-001
**Date:** 2026-05-20
**Baseline:** R36 commit d51d4a4

## What R37 Fixed

R36 had an evidence-depth caveat: 19 of 32 metadata files contained only `placeholder: true`. R37 closes this gap:

- **validate_evidence_bundle.py:** Added `placeholder: true` to PENDING_MARKER_PATTERNS
- **test_r37_evidence_depth_guards.py:** 10 guard tests preventing future placeholder metadata
- **R36 classification:** R36_EVIDENCE_DEPTH_SUPERSEDED_BY_R37

## Probe-Format Recovery Decisions

| Format | Decision | Priority |
|--------|----------|----------|
| FODP | Quarantine (Option B) | None |
| FODG | Quarantine (Option B) | None |
| Gnumeric | Quarantine + Deepening Candidate | After ODS/ODT |
| ABW | Quarantine (Option B) | None |

## Deepening

| Format | Before | After | New Tests |
|--------|--------|-------|-----------|
| ODS | 101 | 107 | 6 (RFC 4180 compliance) |
| QOI | 102 | 108 | 6 (encoder boundary conditions) |
| ZST | 57 | 62 | 5 (codec depth) |

## Evidence

- Python: 892/4skip (2 pre-existing)
- Evidence: 582/1skip (1 pre-existing)
- .NET FODS: 157/157, FODT: 145/145
- R37 new tests: 27 (evidence=10, ODS=6, QOI=6, ZST=5)

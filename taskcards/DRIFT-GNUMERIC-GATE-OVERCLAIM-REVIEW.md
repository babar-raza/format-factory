# DRIFT-GNUMERIC-GATE-OVERCLAIM-REVIEW

**Type:** Drift correction
**Created:** R32 (2026-05-19)
**Format:** Gnumeric
**Priority:** High

---

## Current Claimed State
- **Claimed gate:** G10 (verified, local release candidate)
- **Source:** src/python/gnumeric/gnumeric_codec.py (170 LOC)
- **Tests:** tests/python/gnumeric/ (1 file, 16 test methods)

## Evidence Concern
- Parser is a **shallow cell counter** (170 LOC — smallest spreadsheet parser)
- Returns plain dict, no neutral model
- gzip+XML: extracts sheet names, cell_count, cell values without type detection
- **No write, no export, no round-trip, no cell type inference**
- 16 tests prove cell counting works

## Likely Maturity Class
**probe_only**

## Evidence-Backed Gate
**G4**

## Required Review
Human review of product scope.

## Allowed Outcomes
1. Deepen: neutral model, typed cells, formula handling, export
2. Quarantine: probe_only, capped at G4
3. Read-only probe scope with explicit approval

## Remediation Options
- Add neutral_model.py with Workbook/Sheet/Row/Cell entities
- Implement cell type detection (gnm:Value types)
- Add formula parsing
- Add 30+ tests
- Implement at least 1 export (CSV, JSON)

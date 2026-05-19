# DRIFT-ABW-GATE-OVERCLAIM-REVIEW

**Type:** Drift correction
**Created:** R32 (2026-05-19)
**Format:** ABW (AbiWord)
**Priority:** High

---

## Current Claimed State
- **Claimed gate:** G10 (verified, local release candidate)
- **Source:** src/python/abw/abw_codec.py (141 LOC — smallest parser in project)
- **Tests:** tests/python/abw/ (1 file, 17 test methods)

## Evidence Concern
- Parser is a **shallow text extractor** (141 LOC)
- Returns plain dict, no neutral model
- Extracts section count and paragraph text strings via itertext()
- DOCTYPE stripping is a good security measure, but does not add library depth
- **No write, no export, no round-trip**
- 17 tests prove paragraph extraction works

## Likely Maturity Class
**probe_only**

## Evidence-Backed Gate
**G4**

## Required Review
Human review of product scope.

## Allowed Outcomes
1. Deepen: neutral model (Document/Section/Paragraph/Span), inline formatting, export
2. Quarantine: probe_only, capped at G4
3. Read-only probe scope with explicit approval

## Remediation Options
- Add neutral_model.py with Document/Section/Paragraph/Span entities
- Implement inline formatting extraction (bold, italic, links)
- Add 30+ tests
- Implement export (plain text, markdown)

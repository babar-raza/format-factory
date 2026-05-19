# DRIFT-PGM-PBM-ASCII-SCOPE-REVIEW

**Type:** Drift correction (scope review)
**Created:** R32 (2026-05-19)
**Formats:** PGM (Portable Graymap), PBM (Portable Bitmap)
**Priority:** Low

---

## Current Claimed State
- **PGM:** G7, src/python/pgm/pgm_parser.py (224 LOC), 40 tests
- **PBM:** G7, src/python/pbm/pbm_parser.py (215 LOC), 40 tests

## Evidence Concern
- PGM handles P2 (ASCII) only; P5 (binary) deferred
- PBM handles P1 (ASCII) only; P4 (binary) deferred
- G7 is reasonable for ASCII variant testing
- Binary variants needed for practical library use

## Likely Maturity Class
**read_only_prototype** for both

## Evidence-Backed Gate
**G7** — no overclaim at current gate, but binary support needed before G10

## Required Review
Low priority. Gate claims are honest for current scope.

## Allowed Outcomes
1. Add binary support (P5 for PGM, P4 for PBM) before advancing past G7
2. Accept ASCII-only scope with explicit limitation
3. No gate correction needed at G7

## Remediation
- PGM: implement P5 binary reader
- PBM: implement P4 binary reader
- Add binary test fixtures and corpus samples
- Consider combining PGM/PBM/PPM into unified Netpbm library

---

## R33 Expert Review Outcome (2026-05-19)

**Verdict:** CURRENT_GATE_SUPPORTED
**Reviewed by:** R33 delegated expert review
**Evidence-backed gate confirmed:** G7 for both PGM and PBM
**Maturity class confirmed:** read_only_prototype for both
**Action taken:** No correction needed. Gate claims are honest for ASCII scope. Binary support (P5/P4) must be added before advancing past G7.
**Next step:** Add P5 (PGM) and P4 (PBM) binary readers before advancing to G8+.

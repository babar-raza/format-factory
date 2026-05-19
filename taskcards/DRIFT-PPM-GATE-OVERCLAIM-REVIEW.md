# DRIFT-PPM-GATE-OVERCLAIM-REVIEW

**Type:** Drift correction
**Created:** R32 (2026-05-19)
**Format:** PPM (Portable Pixmap)
**Priority:** Low

---

## Current Claimed State
- **Claimed gate:** G8 (security review passed)
- **Source:** src/python/ppm/ppm_parser.py (228 LOC)
- **Tests:** tests/python/ppm/ (4 files, 40 test methods)

## Evidence Concern
- Parser handles **P3 (ASCII) variant only**
- P6 (binary) is explicitly deferred — P6 is the dominant real-world variant
- G8 security review is valid for P3 parsing
- A PPM library that cannot read P6 has limited practical value

## Likely Maturity Class
**read_only_prototype** — P3 decode is complete but P6 gap limits usefulness

## Evidence-Backed Gate
**G7** — parser handles malformed input well for what it parses

## Required Review
- Low priority: gate claim is borderline, not severely overclaimed
- P6 support should be added before claiming library maturity

## Allowed Outcomes
1. Add P6 binary support (medium effort)
2. Accept P3-only scope with explicit limitation noted
3. No gate correction needed (G8 is valid for P3 security)

## Remediation
- Implement P6 binary reader (struct-based pixel parsing)
- Add P6 test fixtures
- Add P6 corpus samples

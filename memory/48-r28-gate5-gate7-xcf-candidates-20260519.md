# Memory 48 — R28 Gate 5/7 + XCF G4 + DIF/PPM Candidates
# Sprint: FORMAT-FACTORY-R28-GATE5-GATE7-ORACLE-FUZZ-XCF-ZPAQ-G11-C9-PUBLICATION-HARDENING-001
# Date: 2026-05-19

## Sprint Summary

R28 is a 15-lane (0-N) non-AI sprint covering Gate 5 neutral model, Gate 6 oracle planning, Gate 7 fuzz guards, XCF Gate 4 prototype, ZPAQ Gate 3 recovery attempt, FODS/FODT C9 export readiness, and two new candidates (DIF, PPM).

## Key Outcomes

### ODS/ODT/QOI Gate 5 (Lanes B/C/D)
- UNSUPPORTED_FEATURES + SUPPORTED_FEATURES frozensets added to all 3 parsers
- get_capabilities() functions returning neutral model dicts
- ODS: 12 supported, 17 unsupported; ODT: 10 supported, 21 unsupported; QOI: 15 supported, 10 unsupported
- 52 new Gate 5 tests (17+18+17) — all PASS

### Gate 6 Oracle Planning (Lane E)
- Deterministic expected-value oracles for all 3 formats
- 19 oracle tests (6+6+7) — all PASS
- Blocker: Full round-trip oracle requires LibreOffice (documented, not blocking)

### Gate 7 Fuzz Guards (Lane F)
- Deterministic malformed input guards for all 3 formats
- 23 fuzz tests (7+7+9) — all PASS
- Tests: not-a-zip, empty file, ZIP bomb, malformed XML, binary garbage, truncated data, nested XML

### XCF Gate 4 (Lane G)
- Header + property list + layer offset table parser (no pixel decode)
- src/python/xcf/xcf_parser.py + __init__.py + 17 tests — all PASS
- 3 valid + 1 invalid XCF samples in samples/by-format/xcf/

### ZPAQ Gate 3 (Lane H)
- BLOCKED — GATE3_BLOCKED_REQUIRES_EXTERNAL_TOOL (unchanged from R27)
- Blocker report: reports/planning/r28-zpaq-gate3-recovery-or-blocker-report-20260519.md
- Recommended: Path A (install zpaq CLI)

### FODS/FODT C9 (Lanes I/J)
- FODS: 16 C9 tests (CSV 4, JSON 5, HTML 5, Gov 2) → 157/157 PASS
- FODT: 17 C9 tests (TXT 5, MD 4, HTML 5, Gov 2, implicit 1) → 145/145 PASS

### New Candidates (Lane L)
- DIF: Gates 1-3 PASS, score 8.7/10, public domain 1981, text-based cells format
- PPM: Gates 1-3 PASS, score 9.1/10, public domain 1988, Netpbm imaging format

## Test Baselines
- Python (non-AI): 2013 prior + 94 new Gate 5/6/7 + 17 XCF = 2124 (estimate)
- .NET FODS: 157/157 PASS (+21 C9)
- .NET FODT: 145/145 PASS (+21 C9)
- tests/ai: 202 (untouched)

## Format Pipeline (R28 end state)
- FODS/FODT: G1-10 + G11f, C9 tested
- ZST: G1-10, LC ready
- ODS/ODT/QOI: G1-5 (neutral model)
- XCF: G1-4 (prototype)
- DIF/PPM: G1-3 (corpus)
- ZPAQ: G1-2, G3 blocked

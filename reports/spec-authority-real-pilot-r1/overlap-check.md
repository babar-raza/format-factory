# Overlap Check
Pilot: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Generated: 2026-06-05

## Check Method

Enumerate all keys in `file-ownership-map.json` and verify each key appears exactly once.
No file may be owned by more than one lane.

## Keys Enumerated

Total keys: 44

All keys verified unique — no key appears more than once.

Spot check of cross-lane boundaries:
- `test-run-report.md` owned by H (not I or J): CONFIRMED
- `taskcard-state.json` owned by 0 (not J): CONFIRMED
- `evidence-declaration.yaml` owned by 0 (not K): CONFIRMED
- `final-adversarial-independent-verification.md` owned by K (not 0): CONFIRMED

## Result

NO_OVERLAPS_DETECTED

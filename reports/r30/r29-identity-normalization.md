# R30 Lane A: R29 Evidence Identity Normalization
# Date: 2026-05-19

## Problem
Two distinct R29 sprints share the `reports/r29/` directory:

1. **R29 Main-Track** (FORMAT-FACTORY-R29-MAIN-TRACK-MEGA-TRAIN-GATE6-GATE8-XCF-DIF-PPM-G11-PUBLICATION-CANDIDATES-001)
   - Commit: 7cb1586 (primary), d26395b, 16a0a19
   - Scope: Format gate advancement (ODS/ODT/QOI Gate 6/7, XCF Gate 5-7, DIF/PPM parsers, PGM/PBM/SYLK candidates)
   - Metadata: reports/r29-mega-train-sprint-metadata-20260519/
   - Evidence bundle: .local/bundles/r29-mega-train.zip

2. **R29 State-Consistency** (FORMAT-FACTORY-R29-MEGA-TRAIN-STATE-CONSISTENCY-AI-FORMAT-COMMERCIAL-PUBLICATION-EVIDENCE-001)
   - Commit: cdad103 (primary), 0952309
   - Scope: R28 sprint-state repair, evidence validator hardening, AI test coverage
   - Metadata: reports/r29-state-consistency-sprint-metadata-20260519/
   - Evidence bundle: .local/evidence-bundles/r29-mega-train-state-consistency-ai-format-commercial-publication-evidence-20260519.zip

## How They Coexist
- Both use `reports/r29/` for lane reports, but each has a **separate metadata directory** with distinct sprint_id
- `reports/r29/sprint-state.yaml` was overwritten by the state-consistency sprint (now references state-consistency sprint_id)
- `reports/r29/final-verdict-mega-train-20260519.md` references the main-track sprint_id
- The evidence consistency tests use `sprint_id` matching to avoid cross-sprint false positives

## Reconciliation
| Artifact | Main-Track | State-Consistency |
|----------|------------|-------------------|
| sprint-state.yaml | overwritten | current (cdad103) |
| final-verdict | references main-track | no separate verdict file |
| metadata dir | r29-mega-train-sprint-metadata-20260519/ | r29-state-consistency-sprint-metadata-20260519/ |
| evidence bundle | r29-mega-train.zip | r29-mega-train-state-consistency-...zip |
| lane reports | preflight-and-lane-ownership, r28-metadata-refresh | preflight-current-state, all lane reports A-O |

## Future Prevention
- The `test_r29_sprint_state_consistency.py` tests match by `sprint_id` to avoid cross-sprint interference
- Evidence contracts use unique contract_id matching sprint_id
- Metadata directories use sprint-specific names, not just `rNN/`

## Status: CLOSED_VERIFIED
No history rewrite needed. Forward documentation sufficient.

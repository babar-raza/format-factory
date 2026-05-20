# R35 Clean Recovery Baseline and Gate Corrections

**Sprint:** FORMAT-FACTORY-R35-CLEAN-RECOVERY-BASELINE-GATE-CORRECTIONS-DEEPENING-AND-PUBLICATION-READINESS-001
**Date:** 2026-05-20
**Commit:** TBD (pending)

## Key Facts

1. R35 is the first sprint to start with a fully clean working tree after R33/R34 recovery.
2. R34 scope separation verified: reports/r33/ = drift recovery only; AI artifacts in reports/ai/.
3. R33 product work revalidated: 96/96 tests pass (ODS exporter, QOI encoder, ZST expansion).

## Gate Corrections Applied

| Format | Previous Claimed | Evidence-Backed | Maturity | Pack.yaml |
|--------|-----------------|-----------------|----------|-----------|
| FODP | G10 | G4 | probe_only | gate_correction added |
| FODG | G10 | G4 | probe_only | gate_correction added |
| Gnumeric | G10 | G4 | probe_only | gate_correction added |
| ABW | G10 | G4 | probe_only | gate_correction added |

## Scope Finalizations Applied

| Format | Scope | Binary Status | Pack.yaml |
|--------|-------|---------------|-----------|
| XCF | header_and_metadata_only | pixel decode not implemented | scope_finalization added |
| PPM | read_only_ascii_p3 | P6 not implemented | scope_finalization added |
| PGM | read_only_ascii_p2 | P5 not implemented | scope_finalization added |
| PBM | read_only_ascii_p1 | P4 not implemented | scope_finalization added |

## Deepening Results

| Format | R35 New Tests | Total | Target Met |
|--------|---------------|-------|------------|
| ODS | 8 hardening | 94 | YES |
| QOI | 8 hardening | 95 | YES |
| ZST | 4 stabilization | 52 | YES (50+) |

## Evidence Guard Tests Added

13 new tests in test_r35_evidence_guard_hardening.py covering:
- Contract consistency (emergency_blocker, require_clean_git, sprint_id)
- Report namespace collision detection
- Gate correction field completeness (previous_claimed_gate required)
- Probe-only release candidacy guard
- Scope finalization completeness

## Third Bundle

r33-ai-runner-executable-pipeline-real-synthesis-truth-reconciliation-20260519.zip — classified as AI-parallel-out-of-scope.

## R34 Closure Outcome

R34_CLOSURE_SUPERSEDED_BY_R35_CLEAN_BASELINE — all dirty AI parallel state resolved before R35 start.

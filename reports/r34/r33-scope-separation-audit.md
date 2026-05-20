# R33 Scope Separation Audit

**Sprint:** FORMAT-FACTORY-R34-R33-SCOPE-SEPARATION-CLOSURE-REPAIR-AND-RECOVERY-CONTINUATION-001
**Date:** 2026-05-20

## Problem Statement

Commit b99006c ("fix(governance): execute drift recovery overclaim review and focused deepening")
mixed artifacts from two concurrent R33 sprints into the same report directory (reports/r33/):

1. **R33 Drift Recovery** (FORMAT-FACTORY-R33-DRIFT-RECOVERY-OVERCLAIM-REVIEW-DEEPENING-AND-CLOSURE-HYGIENE-001)
2. **R33 AI Runner Pipeline** (FORMAT-FACTORY-R33-AI-RUNNER-EXECUTABLE-PIPELINE-REAL-SYNTHESIS-AND-TRUTH-RECONCILIATION-MEGA-TRAIN-001)

Additionally, reports/r33/sprint-state.yaml contained the AI sprint ID, not the drift recovery sprint ID.

## Classification of reports/r33/ Files (Pre-Repair)

| File | Classification | Evidence |
|------|---------------|----------|
| final-verdict.md | drift_recovery_r33 | Sprint ID is drift recovery, content describes overclaim review/deepening |
| fods-fodt-commercial-gap-analysis.md | drift_recovery_r33 | Describes FODS/FODT commercial gap, no AI content |
| overclaim-expert-review-outcomes.md | drift_recovery_r33 | 8-format overclaim review, no AI content |
| r32-closure-hygiene-report.md | drift_recovery_r33 | R32 closure review, no AI content |
| preflight-and-lane-ownership-20260519.md | drift_recovery_r33 | Lists drift recovery lanes (A-L), no AI lanes |
| sprint-state.yaml | **ai_runner_r33** (CONTAMINATED) | Contains AI sprint ID, AI lanes (B-O), tools/ai file references |
| preflight-current-state.md | ai_runner_r33 | Describes AI runner baseline, --live-pipeline, AI test counts |
| r32-truth-reconciliation.md | ai_runner_r33 | Describes AI pipeline truth reconciliation, synthesis modes |
| lane-ownership-and-overlap-matrix.md | ai_runner_r33 | Lists AI lanes modifying tools/ai/*, tests/ai/* |
| live-telemetry/live-pipeline-output.json | ai_runner_r33 | AI pipeline telemetry output |
| live-telemetry/redacted-live-telemetry.json | ai_runner_r33 | AI redacted telemetry |
| pipeline-fixture-run/ai-pipeline-runner-output.json | ai_runner_r33 | AI pipeline fixture output |

## Repair Actions

1. **Moved** 5 committed AI artifacts from reports/r33/ to reports/ai/r33-runner-pipeline-truth-20260519/ via git mv
2. **Moved** 1 untracked AI telemetry file (redacted-live-telemetry.json) manually
3. **Moved** 1 untracked AI verdict (final-verdict-ai-runner-pipeline.md) manually
4. **Repaired** sprint-state.yaml to contain drift recovery sprint ID and lanes
5. **Added** scope-contamination note to final-verdict.md
6. **Fixed** evidence contract require_clean_git from false to true

## Post-Repair State

reports/r33/ now contains ONLY drift recovery artifacts:
- final-verdict.md (with scope-contamination note)
- fods-fodt-commercial-gap-analysis.md
- overclaim-expert-review-outcomes.md
- r32-closure-hygiene-report.md
- preflight-and-lane-ownership-20260519.md
- sprint-state.yaml (repaired, drift recovery ID and lanes)

reports/ai/r33-runner-pipeline-truth-20260519/ contains the separated AI artifacts:
- preflight-current-state.md
- r32-truth-reconciliation.md
- lane-ownership-and-overlap-matrix.md
- final-verdict-ai-runner-pipeline.md
- live-telemetry/live-pipeline-output.json
- live-telemetry/redacted-live-telemetry.json
- pipeline-fixture-run/ai-pipeline-runner-output.json

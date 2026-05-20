# R33 AI Artifact Separation Report

**Sprint:** R34
**Date:** 2026-05-20

## Action Taken: MOVED

AI report artifacts were moved from reports/r33/ to reports/ai/r33-runner-pipeline-truth-20260519/.

## Files Moved

### Via git mv (committed, tracked)
1. reports/r33/preflight-current-state.md -> reports/ai/r33-runner-pipeline-truth-20260519/preflight-current-state.md
2. reports/r33/r32-truth-reconciliation.md -> reports/ai/r33-runner-pipeline-truth-20260519/r32-truth-reconciliation.md
3. reports/r33/lane-ownership-and-overlap-matrix.md -> reports/ai/r33-runner-pipeline-truth-20260519/lane-ownership-and-overlap-matrix.md
4. reports/r33/live-telemetry/live-pipeline-output.json -> reports/ai/r33-runner-pipeline-truth-20260519/live-telemetry/live-pipeline-output.json
5. reports/r33/pipeline-fixture-run/ai-pipeline-runner-output.json -> reports/ai/r33-runner-pipeline-truth-20260519/pipeline-fixture-run/ai-pipeline-runner-output.json

### Manual move (untracked files)
6. reports/r33/live-telemetry/redacted-live-telemetry.json -> reports/ai/r33-runner-pipeline-truth-20260519/live-telemetry/redacted-live-telemetry.json
7. reports/r33/final-verdict-ai-runner-pipeline.md -> reports/ai/r33-runner-pipeline-truth-20260519/final-verdict-ai-runner-pipeline.md

## Invariants Held
- No tools/ai/** modified
- No tests/ai/** modified
- No AI execution performed
- No evidence deleted (only relocated)
- Drift recovery evidence contract references not broken (contract did not reference AI files)

## Remaining Dirty AI Files (NOT staged by R34)
- docs/ai/ai-system-verification-matrix.md (modified)
- tests/ai/test_r28_e2e_pilot.py (modified)
- tools/ai/pipeline/e2e_pilot.py (modified)
- tools/ai/run_ai_checks.py (modified)
- memory/53-r33-ai-runner-executable-pipeline-20260519.md (untracked)
- reports/governance/r33-adversarial-review.md (untracked)
- reports/verification/r33-independent-verification.md (untracked)
- tests/ai/test_r33_runner_pipeline_truth.py (untracked)
- tools/ai/schemas/commit_metadata.py (untracked)
- tools/ai/telemetry/artifacts.py (untracked)
- tools/evidence/contracts/r33-ai-runner-executable-pipeline-real-synthesis-truth-reconciliation.yaml (untracked)

These belong to the incomplete AI runner pipeline sprint and must be handled by a future AI-scoped sprint.

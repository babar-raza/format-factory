# R33 Lane Ownership and Overlap Matrix

## Lane Structure
| Lane | Name | Files Modified | Files Created | Tests |
|------|------|---------------|---------------|-------|
| 0 | Coordinator | - | reports/r33/*.md, sprint-state.yaml | - |
| A | R32 Truth Reconciliation | - | reports/r33/r32-truth-reconciliation.md | 5 |
| B | Live Pipeline Runner | tools/ai/run_ai_checks.py | - | 4 |
| C | --all Mode | tools/ai/run_ai_checks.py | - | 2 |
| D | Synthesis Wiring | tools/ai/pipeline/e2e_pilot.py | - | 4 |
| E | Diverse Retrieval Corpus | tools/ai/pipeline/e2e_pilot.py | - | 6 |
| F | Contradiction Policy | tools/ai/pipeline/e2e_pilot.py | - | 6 |
| G | Evidence Validator | tools/ai/run_ai_checks.py | - | 4 |
| H | Commit Metadata | - | tools/ai/schemas/commit_metadata.py | 6 |
| I | Telemetry Artifacts | - | tools/ai/telemetry/artifacts.py | 5 |
| J | Gate Dry-Run Hooks | - | - | 2 |
| K | Verification Matrix | docs/ai/ai-system-verification-matrix.md | - | 2 |
| L | Sync | memory/, docs/ | - | - |
| M | Tests + Validation | tests/ai/test_r28_e2e_pilot.py | tests/ai/test_r33_runner_pipeline_truth.py | 5 |
| N | IV + Adversarial | - | reports/verification/, reports/governance/ | - |
| O | Evidence Bundle | - | reports/r33/final-verdict.md | - |

## Overlap Resolution
- Lanes B/C/G all modify run_ai_checks.py: changes are additive (new function + new flag + replacement of stub)
- Lanes D/E/F all modify e2e_pilot.py: changes are in separate sections (PilotConfig, fixture data, synthesis/contradiction)
- Lane M modifies test_r28_e2e_pilot.py: adapts to new stage_3_synthesis return type

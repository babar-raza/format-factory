# R64 Lane Ownership

**Sprint:** FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
**Date:** 2026-05-25

---

## Closure-Critical Trains

| Train | Owner | Allowed Paths | Forbidden Paths | Shared Files | Stop Condition |
|---|---|---|---|---|---|
| 0 | Coordinator | reports/r64/*.md, .local/r64-metadata/ | src/ | final-verdict.md, scoreboard | All trains reported |
| A | IV Lead | reports/r64/r63-*.md, reports/r64/r63-*.json | src/, tools/ | None | 13 defects verified |
| B | Sidecar Lead | tests/evidence/test_r64_*, .local/r64-metadata/*sidecar* | src/ | final-verdict.md | Sidecar delivered + 3 negative proofs |
| C | Packaging Lead | tools/packaging/find_bundle_artifacts.py, tests/packaging/test_r64_* | src/ | None | Artifact discovery run-aware + extracted replay pass |
| D | API Lead | tests/packaging/test_python_installed_wheels.py | tools/ | None | 11+11 APIs proven from venv |
| E | Artifact Lead | .local/r64-metadata/package-artifacts/, packaging/ | src/ | package-artifact-manifest.yaml | 10+10+2 rebuilt |
| F | .NET Lead | reports/r64/dotnet-*, .local/r64-metadata/dotnet-* | src/python/ | None | NuGet replay proven or SDK-unavailable |
| G | AI Lead | reports/r64/ai-* | src/ | None | All reviewers run, AI_NOT_LIVE declared |
| J | Audit Lead | reports/r64/phase-audit-* | src/ | None | PA14 repaired + PA15 verdict |
| M | Bundle Lead | .local/r64-*, reports/r64/final-verdict.md | None | All shared | BUNDLE_VALIDATION: PASS + SIDECAR_PROOF_VALIDATION: PASS |

## Product Trains

| Train | Owner | Allowed Paths | Forbidden Paths | Shared Files | Stop Condition |
|---|---|---|---|---|---|
| H | FODS/FODT Lead | src/python/fods/, src/python/fodt/, tests/python/fods/, tests/python/fodt/ | tools/ | release-manifests | 2+2 capabilities + tests |
| I | Format Lead | src/python/{ods,csv,dif,ppm}/, tests/python/{ods,csv,dif,ppm}/ | tools/ | None | 4 tracks advanced |

## Work-Ahead Trains

| Train | Owner | Allowed Paths | Stop Condition |
|---|---|---|---|
| K | Authority Lead | reports/r64/acquisition-* | Authority verified |
| L | Docs Lead | reports/r64/docs-*, memory/ | Memory synced |
| W1-W7 | Work-Ahead Lead | reports/r64/workahead-* | Reports completed |

---

LANE_OWNERSHIP_STATUS: COMPLETE

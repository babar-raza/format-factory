# Regression Test Plan
# Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R1-001
# Lane: L

## Purpose

Ensure the RCA layer implementation remains correct across reruns and future changes.
All tests are deterministic and require no external state.

## Test File

`tests/requirement_capability_authority/test_real_pilot_r1.py` — 25 tests

## Categories Covered

| # | Category | Test(s) | Proof |
|---|----------|---------|-------|
| 1 | Missing requirement blocks claim | TestMissingRequirementBlocksClaim | GraphValidator invariant 1 |
| 2 | Missing implementation blocks coverage | TestMissingImplementationBlocksClaim | CapabilityCoverageEvaluator |
| 3 | Missing tests blocks coverage | TestMissingTestsBlocksCoverage | CoverageEvaluator IMPLEMENTATION_ONLY level |
| 4 | Missing dogfood blocks dogfood claim | TestMissingDogfoodBlocksDogfoodClaim | dogfood_required=True without artifact |
| 5 | Export without target writer blocks | TestExportWithoutTargetWriterBlocks | FODS/FODT blocked exports |
| 6 | ai_draft rejected as proof | TestAiDraftRejectedAsProof | GraphValidator invariant 6 |
| 7 | EvidencePackage path-only does not prove claim | TestEvidencePackagePathOnlyDoesNotProveClaim | No evidenced_by edge |
| 8 | accepted_with_limitations requires UnsupportedFeature | TestAcceptedWithLimitationsRequiresUnsupportedFeature | GraphValidator invariant 4 |
| 9 | Stale requirement invalidates coverage | TestStaleRequirementInvalidatesCoverage | StalenessInvalidationEngine |
| 10 | Same inputs → same graph hash | TestGraphHashDeterminism | GraphStore hash determinism |
| 11 | Different inputs → different hash | TestGraphHashDeterminism | GraphStore hash correctness |
| 12 | Gap queue generated for blocked claims | TestGapQueueGenerated | MainstreamGapQueueGenerator |
| 13 | Gap queue deterministic | TestGapQueueGenerated | Two-run hash comparison |
| 14 | SVP generated with claims_checked | TestSupervisorVerdictPacketGenerated | SupervisorVerdictPacketGenerator |
| 15 | SVP has source_graph_hash field | TestSupervisorVerdictPacketGenerated | SVP field presence |
| 16 | All 6 golden replay fixtures pass | TestGoldenReplayFixtures | GoldenReplaySuite |
| 17 | Determinism across all fixtures | TestGoldenReplayFixtures | 3-run hash comparison per fixture |
| 18–23 | Architecture-blocked FODS/FODT exports cleared | TestArchitectureBlockedExportsClearedByPilot | Pilot proof graph + coverage records |

## Execution Command

```bash
PYTHON=".local/venv/Scripts/python"
[ -f "$PYTHON" ] || PYTHON="python"
$PYTHON -m pytest tests/requirement_capability_authority/test_real_pilot_r1.py -v
```

## Pass Criteria

- All 25 tests pass with exit code 0
- No PENDING markers
- No test depends on external services or live imports
- Log saved to: reports/requirement-capability-real-pilot-r1/raw-logs/rca-tests.log

## Existing Suite Non-regression

Run after any changes to tools/requirements_authority/:
```bash
$PYTHON -m pytest tests/supervisor/test_r100_graph_store.py tests/supervisor/test_r100_validators.py \
  tests/supervisor/test_r100_coverage_evaluator.py tests/supervisor/test_r100_overclaim_and_staleness.py -q
```
Expected: 48 passed (all existing RCA core tests).

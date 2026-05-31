# R79 Risk Register

**sprint_id:** FORMAT-FACTORY-R79-PACKAGE-SOURCE-SYNC-FIRST-REAL-FODS-PRODUCT-RC-ZST-DEPENDENCY-REPLAY-MEGA-TRAIN-001
**date:** 2026-05-30

## Active Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| RR-R79-001 | FODT structural gap fix breaks existing FODT tests | HIGH | HIGH | Run full suite after fix; test roundtrip before and after |
| RR-R79-002 | Package rebuild generates new wheel with different SHA, invalidating any pre-built test references | MEDIUM | MEDIUM | Rebuild wheels in Train B, capture new SHA, update evidence |
| RR-R79-003 | sdist exclude for dist*/ not honored by hatchling, old artifacts still included | MEDIUM | MEDIUM | Verify exclude pattern works; use `exclude = ["dist*/"]` syntax |
| RR-R79-004 | ZST offline install still fails even after classification — classification is not a fix | LOW | LOW | Classification is the correct response; no engineering fix needed |
| RR-R79-005 | .NET test project creation breaks existing dotnet build | MEDIUM | HIGH | Test inside new csproj only; don't touch existing src/net/fods/ main project |
| RR-R79-006 | Installed-wheel smoke test imports `fods` but installed namespace differs | MEDIUM | HIGH | Confirm `import fods` works after wheel install; record exact module name |
| RR-R79-007 | FODT paragraph management fix changes behavior relied on by existing tests | HIGH | HIGH | Audit all existing FODT paragraph tests; update fixtures if needed |
| RR-R79-008 | Version "0.1.0" → "0.1.0.dev0" change in constants.py could break version-dependent tests | LOW | LOW | Search tests for hardcoded "0.1.0" version string assertions |
| RR-R79-009 | Bundle build encounters PENDING markers in new R79 reports | MEDIUM | HIGH | Review all reports for PENDING before bundle build |
| RR-R79-010 | Supervisor review package missing required components | LOW | HIGH | Checklist-verify all 12 required components before sealing |

## Closed Risks (carried from R78 as resolved)

| ID | Risk | Resolution |
|---|---|---|
| RR-R78-001 | Circular SHA dependency in inner ZIP | RESOLVED — delegation labels used (R75 model) |
| RR-R78-002 | Sidecar gitignored | RESOLVED — SHA recorded in final-verdict.md |

## Risk Thresholds

- Any HIGH/HIGH risk that materializes → sprint verdict drops to PARTIAL
- Any MEDIUM/HIGH risk that materializes → addressed in same sprint before sealing

# R76 Defect Ledger

**sprint_id:** FORMAT-FACTORY-R77-TRUE-CLEAN-REVIEW-PACKAGE-PACKAGE-ARTIFACTS-STATE-CLOSURE-PRODUCT-DEEPENING-MEGA-TRAIN-001
**date:** 2026-05-30
**source:** Supervisor classification of R76 + local artifact verification

## Defect Summary

| ID | Description | Severity | R77 Action |
|---|---|---|---|
| D76-01 | state/current-state.md says R76_IN_PROGRESS | RC_BLOCKING | REPAIRED in Train B |
| D76-02 | state/current-state.json verdict=R76_IN_PROGRESS | RC_BLOCKING | REPAIRED in Train B |
| D76-03 | plans/master-plan.md says R76 IN_PROGRESS | RC_BLOCKING | REPAIRED in Train B |
| D76-04 | bundle-metadata says pass1 but packaged file is pass2 | RC_BLOCKING | REPAIRED in Train C |
| D76-05 | 0 physical .whl/.tar.gz/.nupkg in review package | RC_BLOCKING | REPAIRED in Train F |
| D76-06 | Negative proof files lack raw command evidence | MAJOR | REPAIRED in Train D |
| D76-07 | Missing bundle-metadata/package-install-smoke-summary.txt | MAJOR | REPAIRED in Train G |
| D76-08 | Missing bundle-metadata/dotnet-raw-log-summary.txt | MAJOR | REPAIRED in Train K |
| D76-09 | Missing bundle-metadata/gate8-readiness-summary.txt | MAJOR | REPAIRED in Train P |
| D76-10 | Missing bundle-metadata/gate11-readiness-summary.txt | MAJOR | REPAIRED in Train R |
| D76-11 | Missing bundle-metadata/next-format-summary.txt | MODERATE | REPAIRED in Train V |
| D76-12 | Missing bundle-metadata/master-plan-sync-summary.txt | MODERATE | REPAIRED in Train V |
| D76-13 | Missing bundle-metadata/final-artifact-authority-summary.txt | MODERATE | REPAIRED in Train C |
| D76-14 | Missing reports/r76/final-adversarial-independent-verification.md | MODERATE | Closed: R77 adds r77/ IV |
| D76-15 | Missing reports/r76/final-review-package-replay.md | MODERATE | REPAIRED in Train G |
| D76-16 | Missing reports/r76/dotnet-commercial-product-depth.md | MODERATE | REPAIRED in Train K |
| D76-17 | Missing reports/r76/state-registry-memory-master-plan-sync.md | MODERATE | REPAIRED in Train V |
| D76-18 | Validator passed despite IN_PROGRESS state | MAJOR | REPAIRED in Train E |
| D76-19 | package-artifact-manifest.yaml lacks physical paths + full SHA | MAJOR | REPAIRED in Train F |

## Defect Classification

All 19 defects are CONFIRMED_CARRIED_TO_R77 and actioned in corresponding trains.

Zero defects classified as EXPLAINED_NOT_DEFECT.

# R20 Preflight — R19 Baseline and Lane Ownership
Sprint: FORMAT-FACTORY-R20-PRODUCTIZATION-TRAIN-ZST-FODP-FODG-GNUMERIC-ABW-SOURCE-AND-GATE11-ARCHITECTURE-SWARM-001
Date: 2026-05-16

## Git Baseline

- HEAD: 2dcd7f8 feat(acquisition): complete R19 high-throughput acquisition train
- Branch: main
- Working tree: clean (known unrelated untracked: .claude/commands/export-plan-context.md, format-factory.zip)
- R19 bundle: .local/r19-bundle.zip EXISTS

## R19 Gate State Verification (from live registry)

| Format | G1 | G2 | G3 | G4 | G5 | G6 | G7 | impl_authorized | cpr |
|--------|----|----|----|----|----|----|----|-----------------|-----|
| ZST | passed | passed | passed | passed | waived | passed | passed | False | False |
| FODP | passed | passed_fast_path | passed | not_started | not_started | not_started | not_started | not_set | False |
| FODG | passed | passed_fast_path | passed | not_started | not_started | not_started | not_started | not_set | False |
| Gnumeric | passed | passed | passed | not_started | not_started | not_started | not_started | not_set | False |
| ABW | passed | passed_with_notes | passed | not_started | not_started | not_started | not_started | not_set | False |
| ORA | deferred_borderline | - | - | - | - | - | - | not_set | False |

## Test Baseline Verified

- R19 authorized test result: 1181 passed, 8 skipped, 0 failed
- Post-R19 verification (background task bxfcnjmb6): 1181 passed, 8 skipped — CONFIRMED

## Known R19 Evidence Hygiene Note (per R20 prompt)

- r19-sprint-gate-status.md had Gate 19 as "IN PROGRESS" in the final bundle
- This must be corrected by Guard 1 (IN_PROGRESS detection in validate_evidence_bundle.py)
- R20 Gate 1 will implement this guard

## Lane Ownership (R20)

| Lane | Format | R20 Objective | Stop Condition |
|------|--------|--------------|----------------|
| ZST | compression | Python FOSS source (G8+) | impl gate fails |
| FODP | presentation | G4-7 + Python source | any gate fails |
| FODG | drawing | G4-7 + Python source | any gate fails |
| Gnumeric | cells | G4-7 + Python source | any gate fails |
| ABW | document | G4-7 + Python source | DTD risk unacceptable |
| ORA | image | closed (deferred) | N/A |
| dnumber | cells | closed (rejected) | N/A |
| FODS | cells | G11 architecture plan | no execution |
| FODT | document | G11 architecture plan | no execution |

## Hard Invariants Confirmed

- commercial_product_ready: false (all formats)
- FODS/FODT Gate 11: NOT APPROVED
- src/net: no changes authorized
- No push, no PR

PREFLIGHT: PASS
R19_BASELINE: VERIFIED

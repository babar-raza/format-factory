# Risk Register
Pilot: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Generated: 2026-06-05

## Risks Identified and Mitigated

| ID | Risk | Severity | Status | Mitigation |
|----|------|----------|--------|------------|
| R-001 | SAL implementation not present | HIGH | MITIGATED | All 12 subsystems confirmed PRESENT at pilot start |
| R-002 | Tests fail due to wrong assertions | MEDIUM | MITIGATED | 2 test assertion defects fixed; 45/45 pass |
| R-003 | Production source modification | HIGH | MITIGATED | All changes within allowed scope; changed-files-classification.md confirms no src/ changes |
| R-004 | DIF requirements overclaimed as ACCEPTED_SPEC | HIGH | MITIGATED | DIF classified EMPIRICAL_ONLY throughout pipeline; anti-bypass verified |
| R-005 | Context pack non-determinism | HIGH | MITIGATED | Determinism proven for ZST/Netpbm/DIF; run1==run2 SHA-256 confirmed |
| R-006 | poc-targets.yaml mutation | HIGH | MITIGATED | No mutation; file unchanged |

## Residual Risks (for R2)

| ID | Risk | Severity | Note |
|----|------|----------|------|
| R-007 | Real RFC fetch rate-limited or content changes | MEDIUM | Deferred to R2; add fetch guard |
| R-008 | ODF license not confirmable | LOW | FODS stays ACCEPTED_WITH_CAVEAT until confirmed |
| R-009 | Staleness auto-trigger missing | MEDIUM | D-STALE-001 documented; add in R2 |

## Verdict

`RISK_REGISTER_COMPLETE — NO_UNMITIGATED_R1_RISKS`

# Risk Register
# Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R1-001

| Risk ID | Risk | Severity | Status | Mitigation |
|---------|------|----------|--------|-----------|
| R01 | FODT has no Spec Authority R2 context pack | MEDIUM | MITIGATED | Fixture-backed input; clearly caveated |
| R02 | Architecture-blocked exports (FODS/FODT) falsely PASS | HIGH | MITIGATED | UnsupportedFeature nodes + blocked claim status; 0 false passes |
| R03 | Stale proof supporting accepted_for_poc | HIGH | MITIGATED | Staleness engine correctly blocks zst:old-compress |
| R04 | Overclaim on netpbm:save direction | MEDIUM | REMEDIATED | Pattern 2 detected + remediated: direction write_only → read_write |
| R05 | DIF empirical claims overclaim official spec | MEDIUM | MITIGATED | EMPIRICAL_ONLY spec; accepted_with_limitations + UnsupportedFeature |
| R06 | poc-targets.yaml mutation | CRITICAL | PREVENTED | SyncProposal only; prohibition note enforced |
| R07 | Spec Authority R2 live dependency | MEDIUM | MITIGATED | All inputs frozen as snapshots with SHA-256 |
| R08 | Product source edits | CRITICAL | PREVENTED | Hard prohibitions; no src/ files modified |
| R09 | False positive overclaim errors blocking pilot | LOW | RESOLVED | 0 overclaim errors after netpbm:save remediation |
| R10 | COVERAGE_BLOCKED due to synthetic stale | LOW | ACCEPTED | Expected behavior; stale proof correctly blocked |

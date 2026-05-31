# R85 Risk Register

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## Risk Matrix

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R-01 | .NET Netpbm first slice fails to compile | LOW | HIGH | Use simple P3/P6 binary reader; .NET has BinaryReader built-in |
| R-02 | Supervisor run-on-latest picks supervisor review ZIP (38 entries) instead of inner bundle | MEDIUM | MEDIUM | Pass --bundle explicitly to inner ZIP |
| R-03 | Product direction update to policies.yaml triggers validator rejection | LOW | LOW | Additive-only policy changes |
| R-04 | PBM→PGM cross-format dogfood requires matching pixel model | MEDIUM | MEDIUM | Both are grayscale-compatible; PBM is 1-bit PGM subset — conversion is trivial |
| R-05 | Evidence bundle build fails ARTIFACT_POLICY_SELF_CONTAINED check | MEDIUM | HIGH | Copy fresh package artifacts from .local/r85-packages/ before bundle build |
| R-06 | Full Python test suite csv-shadow 19 failures persist | HIGH (expected) | LOW | Document as known/pre-existing; all pass in isolation |
| R-07 | Supervisor next-sprint.md does not include product-factory lanes | MEDIUM | HIGH | Fix prompt template + add test before accepting |
| R-08 | INV-014 R84 SHA format regex mismatch persists | LOW | LOW | Known stale-state issue; R85 final-verdict uses correct format |
| R-09 | No dogfood export from .NET (C# FODS→CSV uses FF CSV library?) | MEDIUM | MEDIUM | C# CSV exporter writes directly, not via FF Python library; document as GAP |
| R-10 | SYLK/DIF save-same-format not implemented | HIGH | LOW | Scope as read-export-only; document explicitly |

## Active Blockers (inherited from R84)
- B-01: Gate 11 G11-G NOT_STARTED — requires Babar Raza written approval
- B-02: Gate 8 for ODS/ODT/QOI/XCF/DIF/PPM — awaiting human approval
- B-03: No push authority — local only

## R85 does not attempt to unblock B-01 or B-02. These require external approval.

# R61 Risk Register

**Sprint:** FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
**Date:** 2026-05-24

| ID | Risk | Severity | Mitigation |
|----|------|----------|------------|
| R61-RISK-001 | Extracted-bundle replay discovers more broken paths beyond package tests | high | Train C comprehensively scans all test files for .local/ paths before declaring done |
| R61-RISK-002 | .nupkg inclusion in bundle increases ZIP size significantly | medium | Budget ~5MB; builder auto-includes; verify entry_count and size_bytes in proof |
| R61-RISK-003 | artifact_source_commit policy requires validator changes; may break existing contracts | high | Implement as additive validator check; existing contracts pass if field absent |
| R61-RISK-004 | SHA mismatch again in Pass 2 (chicken-and-egg with proof file) | critical | Use 3-pass protocol: interim Pass 2 → update final-verdict → true final Pass 2 → sidecar |
| R61-RISK-005 | DIF/PPM probe_nonexistent path test pre-existing failures remain | low | Pre-existing; document as known issue; do not block closure |
| R61-RISK-006 | CSV Gate 8 may uncover spec gaps not addressed in Gate 7 | medium | Gate 8 scope: adversarial/injection; scoped to what Gate 7 did not cover |
| R61-RISK-007 | Phase Audit 12 RC reproducibility check may find new gaps | medium | Phase Audit 12 scoped to extracted-bundle replay proof — Train M provides proof |
| R61-RISK-008 | Memory/docs out of date after R61 completion | low | Train L explicitly covers memory sync |
| R61-RISK-009 | Final bundle PENDING check fails due to proof file writing order | critical | Write all proof files BEFORE final bundle build; validate --check-no-pending |
| R61-RISK-010 | Validator does not support new artifact_source_commit field | medium | Train D implements validator support before Train M bundle build |

## Pre-Existing Known Issues (Not R61 Blockers)

- DIF probe_nonexistent Windows path: 2 pre-existing test failures (DIF/PPM)
- Gate 11 G11-G: awaiting Babar Raza approval — NOT a sprint blocker
- ODS/ODT/QOI Gate 8: awaiting human security review — NOT a sprint blocker

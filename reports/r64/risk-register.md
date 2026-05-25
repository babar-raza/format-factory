# R64 Risk Register

**Sprint:** FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
**Date:** 2026-05-25

---

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| RISK-001 | Sidecar not delivered again | CRITICAL | Train B generates sidecar + 3 negative proofs; Train M validates before final verdict |
| RISK-002 | Final proof has placeholder language | HIGH | Train B adds test_r64_final_proof_no_placeholders.py; validator scans for forbidden tokens |
| RISK-003 | Artifact discovery returns wrong run | HIGH | Train C makes find_artifact_dir run-aware; test_r64_artifact_discovery_run_awareness.py |
| RISK-004 | SHA mismatch between verdict and ZIP | HIGH | Two-pass build: commit after Pass 1 SHA, rebuild Pass 2, sidecar authoritative |
| RISK-005 | Packaging replay tests skip from extracted bundle | MEDIUM | Train C separates source-build from extracted-bundle mode |
| RISK-006 | AI reviewers fixture-only but overclaimed | MEDIUM | AI_NOT_LIVE labeling mandatory; Train G verdict declares mode |
| RISK-007 | .NET SDK unavailable | MEDIUM | Train F reports SDK status honestly; no consumer proof if unavailable |
| RISK-008 | Phase Audit 15 blocked by sidecar | MEDIUM | Train J depends on Train B completion |
| RISK-009 | Context window exhaustion on mega-train | MEDIUM | Parallel subagent delegation; incremental commits |
| RISK-010 | Gate 11 G11-G requires human approval | LOW | Accept as external blocker; do not overclaim |

---

RISK_REGISTER_STATUS: COMPLETE

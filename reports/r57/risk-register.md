# R57 Risk Register

**Sprint:** FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
**Date:** 2026-05-23

---

| Risk ID | Description | Likelihood | Impact | Mitigation |
|---------|-------------|------------|--------|------------|
| R57-RISK-001 | Fix to test_r56_package_rc.py creates new path coupling | Medium | Medium | Use discovery function + skip when artifact dir absent |
| R57-RISK-002 | Full SHA recompute modifies local manifest (gitignored) | Low | Low | SHA computed from actual bytes; manifest stays in .local/ |
| R57-RISK-003 | Validator PENDING_MARKER_PATTERNS regex too broad | Low | Medium | Test against known-good bundles before adding pattern |
| R57-RISK-004 | FODS manifest wording change introduces factual ambiguity | Medium | Medium | Keep supported/unsupported split semantically distinct |
| R57-RISK-005 | Format advancement (Train F) picks formats with latent test failures | Medium | High | Run tests immediately after each gate work; stop on FAIL |
| R57-RISK-006 | Phase Audit 8 uncovers undocumented gaps causing Train K delay | Low | Medium | Document gaps as conditional items; do not block Train K |
| R57-RISK-007 | Bundle build includes .local/ artifact files making it oversized | Low | Low | Builder gitignores .local/ by default; verify size after build |
| R57-RISK-008 | Sidecar adversarial tests false-fail on timing/path edge cases | Low | Low | Use tmp_path fixtures and normalized comparison |

---

**STATUS: RISK_REGISTER_COMPLETE**

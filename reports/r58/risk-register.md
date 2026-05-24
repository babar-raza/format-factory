# R58 Risk Register

**Sprint:** FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
**Date:** 2026-05-24

---

## Active Risks

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| RISK-R58-001 | Rebuilt wheel build fails (pip/build tooling) | Low | High | Use packaging/python/build-local-packages.py as established path |
| RISK-R58-002 | TSV Gate 6 oracle tests fail due to TSV parser edge cases | Medium | Medium | Scope to deterministic tests only, document failures as known |
| RISK-R58-003 | .NET SDK upgrade breaks test suite | Low | High | Pin to .NET 10.0.204; run bounded test, include raw logs |
| RISK-R58-004 | Sidecar protocol change breaks R56/R57 backward compat validation | Medium | Low | Add backward-compat `bundle_sha256` fallback in validator |
| RISK-R58-005 | find_bundle_artifacts parent-dir check breaks local dev workflow | Low | Low | Check parent only when local .local/ path not found |
| RISK-R58-006 | State snapshot script fails or produces stale data | Low | High | Run explicitly before bundle, include output in metadata |
| RISK-R58-007 | pycache exclusion from bundle removes too many files | Low | Low | Exclude only `__pycache__/` and `*.pyc`; not all compiled |
| RISK-R58-008 | Phase Audit 9 cannot reach PASS due to missing examples | High | Low | Use PHASE9_PARTIAL_PASS_DOCS_OR_EXAMPLES_MISSING as allowed verdict |
| RISK-R58-009 | Gate 11 accidentally approved due to .NET NuGet local proof | Low | Critical | Explicitly state G11 NOT approved in all reports |
| RISK-R58-010 | Memory file exceeds 200 lines causing truncation | High | Medium | Move details to topic files, keep MEMORY.md as index |

---

## Closed Risks (inherited from R57)

- RISK-R57-001: 32-char MD5 wheel SHA — CLOSED (R57 Train D)
- RISK-R57-002: PENDING markers in bundle — CLOSED (R57 Train B)
- RISK-R57-003: FODT hyperlink code missing — CLOSED (R56 Train C)

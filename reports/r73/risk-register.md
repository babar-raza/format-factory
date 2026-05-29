# R73 Risk Register

**Sprint:** FORMAT-FACTORY-R73-DELIVERY-PACKAGE-TRUTH-PRODUCT-ADVANCEMENT-GATE-READINESS-MEGA-TRAIN-001
**Date:** 2026-05-29

---

## Active Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| RISK-R73-001 | FODS/FODT source changes break existing 211+259 tests | Medium | High | Run full suite after each change; revert if >0 new failures |
| RISK-R73-002 | .NET test runner fails in CI-less env | Low | Medium | Report DOTNET_SDK_AVAILABLE; capture raw logs |
| RISK-R73-003 | Bundle build creates circular SHA reference (delivery manifest inside outer ZIP cannot contain outer ZIP's own SHA) | Known | Low | Document as design constraint; outer SHA recorded in final-verdict.md + standalone .sha256.txt |
| RISK-R73-004 | Next-format source changes introduce import errors or test collection failures | Medium | Medium | Run targeted format tests before suite-wide |
| RISK-R73-005 | Package artifact SHA drift (artifacts rebuilt with new SHAs vs manifest) | Low | High | Do NOT rebuild packages unless required; verify SHAs against existing manifest |
| RISK-R73-006 | Validator --check-no-pending false positive from new metadata files | Low | Medium | Review new metadata for PENDING tokens before bundle build |
| RISK-R73-007 | R73 contract file missing required fields causing bundle validation failure | Low | High | Validate contract before bundle build |
| RISK-R73-008 | Outer delivery package build fails if inner ZIP not yet built | Known | Medium | Enforce two-pass build order in Train M |

---

## Resolved Risks (from R72)

| ID | Risk | Resolution |
|---|---|---|
| RISK-R72-001 | Validator scope bug causes all historical verdicts to be checked | FIXED: current_run=None check added |
| RISK-R72-002 | POST_BUNDLE_AUTHORITATIVE: PENDING not caught before bundle build | FIXED: pre-build state detection in tests |
| RISK-R72-003 | Delivery package inspector confused by inner ZIP vs outer package | ADDRESSED: supervisor-readme.md added in R73 |

---

## Hardcoded Governance Constraints

These are NOT risks — they are hard constraints that must hold:

- Gate 11 approved: MUST stay false
- commercial_product_ready: MUST stay false
- No git push
- No PyPI upload
- No NuGet upload
- No Gate 8 approval
- No Gate 11 approval
- No destructive cleanup
- No deleting evidence to make validation pass

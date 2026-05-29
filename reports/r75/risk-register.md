# R75 Risk Register

**sprint_id:** FORMAT-FACTORY-R75-FINAL-ARTIFACT-AUTHORITY-REPAIR-RC-SEAL-PRODUCT-ADVANCEMENT-MEGA-TRAIN-001
**date:** 2026-05-29

## Active Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R75-RR-001 | Validator hardening creates false positives in historical bundles | LOW | MEDIUM | New patterns use specific exact tokens; historical bundles don't use these tokens |
| R75-RR-002 | Pass-number drift check breaks if proof file format changes | LOW | LOW | Check skips if no `Bundle:` line — backwards compatible |
| R75-RR-003 | Delivery builder authority JSON path logic fails for non-standard names | LOW | LOW | Fallback path logic present |
| R75-RR-004 | Gate 11 G11-G still not approved | CERTAIN | LOW | Deferred to human approval; not a sprint blocker |
| R75-RR-005 | Ordering-sensitive test failures in full suite run | MEDIUM | LOW | Known issue; all pass in isolation; authoritative result is isolation run |

## Closed Risks

- R74-RR-001: Multi-pass SHA loop (infinite iteration) — CLOSED by stopping at BUNDLE_VALIDATION: PASS + SIDECAR_PROOF_VALIDATION: PASS
- R74-RR-002: TO_BE_FILLED patterns not caught — CLOSED by R75 Train C
- R74-RR-003: No standalone SHA file — CLOSED by R75 Train D

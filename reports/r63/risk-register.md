# R63 Risk Register

**Sprint:** FORMAT-FACTORY-R63-AI-ASSISTED-RC-CLOSURE-AND-WORKAHEAD-MULTI-SPRINT-MEGA-TRAIN-001
**Date:** 2026-05-24

---

## Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| RR-001 | API repair breaks existing tests | Medium | High | Run full suite after each __init__.py change |
| RR-002 | Wheel rebuild produces wrong SHA | Low | High | Validate manifest hashes before bundling |
| RR-003 | INV-007 fix reintroduces placeholder | Medium | Medium | Verify state_snapshot.py after final-verdict edit |
| RR-004 | R63 sidecar tests fail on extracted bundle | Medium | High | Write tests against R63 paths, not R61/R62 |
| RR-005 | Packaging test skips masking failures | High | High | Explicitly fail missing artifact checks |
| RR-006 | Work-ahead lane mutates authority files | Low | High | Lane ownership enforcement; coordinator gate |
| RR-007 | State-transition test failures at bundle time | High | Medium | Pre-commit state_snapshot.py run |
| RR-008 | .NET SDK unavailable for local consumer proof | Medium | Low | Document unavailability; do not claim proof |
| RR-009 | Phase Audit 14 overclaims handoff readiness | Medium | High | Restrict verdict to allowed values only |
| RR-010 | Deferred format advancement overclaims gate | Low | High | Gate changes require deterministic evidence + human |

---

## Accepted Limitations

- AI reviewers run in fixture mode (AI_NOT_LIVE) — no live endpoint configured
- Gate 8 remains human-approval-only (ODS/ODT/QOI/XCF/DIF/PPM)
- Gate 11 remains human-approval-only (FODS/FODT)
- Publication gates remain blocked (no PyPI/NuGet upload)

RISK_REGISTER: DOCUMENTED

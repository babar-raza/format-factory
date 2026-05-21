# R46 Risk Register

**Sprint:** FORMAT-FACTORY-R46-ARTIFACT-CONTAINED-TWO-PRODUCT-RC-001
**Date:** 2026-05-21

---

## Active Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| RK-001 | R46 bundle build sequence repeats R45 PENDING defect | Medium | High | Fix validator FIRST (MT1 1B), build bundle AFTER all reports complete |
| RK-002 | Package artifacts (.whl/.nupkg) too large for bundle | Low | Medium | Artifacts are ~50KB each — acceptable for bundle |
| RK-003 | .NET consumer dotnet restore fails without nuget feed | Low | High | nuget.config must be committed; test replay from bundled artifacts |
| RK-004 | pytest.ini timeout warning causes test count inflation | Low | Medium | filterwarnings fix in MT4 4A |
| RK-005 | FODT spec not cached — Phase Audit 1 incomplete | Medium | Low | Document gap; accept partial audit for R46 |
| RK-006 | FODS Python write capability breaks existing tests | Low | Medium | Add write tests without modifying existing read tests |
| RK-007 | Meta count < 30 floor fails bundle validation | Low | High | Create ≥30 metadata files before bundle build |

---

## Carried Risks from R45

| ID | Risk | R45 Status | R46 Action |
|----|------|------------|------------|
| RK-R45-001 | G11-G NOT_STARTED | Active — human approval required | No change (human gate) |
| RK-R45-002 | Gate 8 awaiting human approval (6 formats) | Active — packets ready | No change (human gate) |
| RK-R45-003 | PACKAGE_NOT_PUSHED | Active — local only | No change (push not authorized) |

---

## Closed Risks from R45

| ID | Risk | Resolution |
|----|------|------------|
| RK-R44-001 | cp1252 encoding in state files | Fixed in R45 MT1 1B |
| RK-R44-002 | require_clean_git: false in contract | Fixed in R45 MT1 1C |
| RK-R44-003 | Validator too weak | Fixed in R45 MT3 3C |

# R56 Risk Register

**Sprint:** FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Date:** 2026-05-23

## Active Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R56-RISK-001 | Hyperlink (`text:a`) implementation creates parser regression in FODT test suite | Medium | High | Run full FODT suite after C; gate on zero regressions |
| R56-RISK-002 | Nested list implementation alters document ordering logic | Medium | Medium | Keep `content` dispatch unchanged; add nested case only |
| R56-RISK-003 | Package wheel build fails (pip/build toolchain issue) | Low | High | Fall back to D-BLOCKED verdict; do not fabricate build claims |
| R56-RISK-004 | .NET SDK unavailable or test counts differ from R55 | Low | Medium | Use bounded runner; report DOTNET_SDK_UNAVAILABLE if absent |
| R56-RISK-005 | CSV/TSV Gate 5 neutral model reveals parsing gaps | Medium | Low | Scope narrowly; advance only what passes tests |
| R56-RISK-006 | Final bundle sidecar mismatch if bundle rebuilt post-verdict | Medium | High | Write sidecar AFTER final build; never pre-generate |
| R56-RISK-007 | Disk space issues during bundle build (R55 lesson: runaway cascading zips) | Low | High | Verify output path is NOT inside metadata dir; check disk before build |
| R56-RISK-008 | Phase Audit 7 consumer proof blocked by no published artifact | Medium | Medium | Use PHASE7_PARTIAL_PASS verdict; document blocker explicitly |

## Inherited Defects Being Repaired

| Defect | From | R56 Action |
|--------|------|-----------|
| IV-R55-001 | R55 scoreboard PENDING | Train A + Train J: repair scoreboard, document in IV report |
| IV-R55-002 | Package artifact claim vs. policy contradiction | Train D: build wheels, update manifest |
| IV-R55-003 | Sidecar mismatch in final bundle | Train K: write matching top-level sidecar for R56 final bundle |
| IV-R55-006 | fods.yaml/fodt.yaml missing from release-manifests | Train G: create both files |
| IV-R55-007 | TC-0057 hyperlink overclaim | Train C: implement hyperlinks or reopen TC |
| IV-R55-008 | TC-0059 nested list overclaim | Train C: implement nested lists or reopen TC |
| IV-R55-009 | Nested ZIPs in R55 bundle | Train K: no nested ZIPs in R56 bundle |
| IV-R55-010 | memory/60 TC contradiction | Train J: correct memory file |

## Deferred Items (Not R56 Scope)

- Gate 11 G11-G commercial approval (human: Babar Raza)
- Gate 8 approval for ODS/ODT/QOI/XCF/DIF/PPM
- Live AI endpoint (no GPT_OSS_ENDPOINT in this environment)
- Agent Metrics live post
- PyPI/NuGet publication

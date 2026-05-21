# R44 Independent Verification

**Sprint:** FORMAT-FACTORY-R45-TWO-PRODUCT-LOCAL-RC-REPLAYABLE-001
**Subject:** R44 (FORMAT-FACTORY-R44-TWO-PRODUCT-LOCAL-RC-BASELINE-001)
**IV Agent:** R45 session (independent of R44 session)

---

## R44 Claimed Verdict

`R44_TWO_PRODUCT_LOCAL_RC_BASELINE_READY`

---

## IV Classification

**R44_PROGRESS_ACCEPTED_RC_OVERCLAIMED**

R44 made genuine material progress. However, the claimed verdict
`TWO_PRODUCT_LOCAL_RC_BASELINE_READY` is overclaimed: a "replayable local RC
baseline" requires that the artifacts themselves exist in the bundle and that
a consumer can verify them — not just that logs and hashes are present.

---

## Verified Claims (ACCEPTED)

| Claim | Evidence | Status |
|-------|----------|--------|
| R43 IV — all 10 R42 blockers verified closed | reports/r44/r43-independent-verification.md | ACCEPTED |
| pycache defect in replay_extracted_bundle.py fixed | tools/evidence/replay_extracted_bundle.py + 12 tests pass | ACCEPTED |
| pytest-timeout 2.3.1 IS installed in user site-packages | test_r44_timeout_portability.py 4/4 PASS | ACCEPTED |
| FODT blocks=0 regression closed | test_r44_semantic_smoke.py asserts len(blocks) >= 1 | ACCEPTED |
| FODS semantic smoke 7 tests | test_r44_semantic_smoke.py — format_id, sheets, formulas, types | ACCEPTED |
| .NET NuGet readme fix — 0 warnings | PackageReadmeFile added to both .csproj files | ACCEPTED |
| FODS .NET 157/157 PASS | reports/r44/package-proof/dotnet/ | ACCEPTED |
| FODT .NET 145/145 PASS | reports/r44/package-proof/dotnet/ | ACCEPTED |
| PGM/PBM/SYLK Gate 9 recorded | registry/format-registry.yaml + pack.yaml | ACCEPTED |
| State snapshot verdict regex fix (R43) | tests/state/ 20/20 PASS | ACCEPTED |

---

## Overclaimed Items (PARTIAL / NOT_COMPLETED)

| Claim | Gap | Status |
|-------|-----|--------|
| "Two-product local RC baseline" | No .whl/.nupkg artifacts in evidence bundle | PARTIAL |
| Package proof | Logs and hashes only — no artifact replay proof | PARTIAL |
| pytest-timeout portability | Passes only in user environment, fails in clean extracted env | PARTIAL |
| .NET consumer project proof (Lane 3B/3C) | Not completed — packages built but no consumer restore+run | NOT_COMPLETED |
| require_clean_git: false in contract | An RC baseline must commit before building | WEAK |
| G11-G approval packet | Incorrectly asks for commercial_product_ready: true (Tier 0 only) | NEEDS_REWRITE |

---

## UTF-8 Defect (Introduced in R44)

`state/current-state.md` contains byte `0x97` (cp1252 em dash) at offset 80.
Root cause: `tools/state/state_snapshot.py` uses `open()` without `encoding="utf-8"`.
The em dash in line 169 (`— {verdict}`) becomes `0x97` on Windows cp1252.

This defect means R44 state files are not portable to Linux/macOS systems.
Fixed in R45 MT1 Lane 1B.

---

## R44 Gap Inventory for R45

| Gap | R45 Lane | Priority |
|-----|----------|---------|
| UTF-8 state snapshot encoding | MT1 1B | HIGH |
| Contract require_clean_git: false | MT1 1C | HIGH |
| pytest-timeout portability (env-specific) | MT2 2A | HIGH |
| auto_proof timeout in extracted replay | MT2 2B | HIGH |
| Package artifacts not in bundle | MT3 3A/3B | HIGH |
| Validator too weak for LOCAL_RC verdicts | MT3 3C | HIGH |
| .NET consumer project not completed | MT4 4A/4B | MEDIUM |
| G11-G packet too broad | MT4 4C | MEDIUM |

---

## R44 IV Verdict Summary

R44 is accepted as `R44_PROGRESS_ACCEPTED_RC_OVERCLAIMED`. The pycache, FODT smoke,
NuGet readme, and PGM/PBM/SYLK Gate 9 work are all genuine and solid. The "local RC
baseline" claim requires the artifact replay chain that R45 must now complete.

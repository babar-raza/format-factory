# R59 R58 Defect Ledger

**Sprint:** FORMAT-FACTORY-R59-CLEAN-RC-CLOSURE-PACKAGING-NORMALIZATION-PHASE10-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Date:** 2026-05-24
**Source:** R59 Train A IV

---

| ID | Title | Severity | Train | Status |
|----|-------|----------|-------|--------|
| IV-R58-003 | Train M IN_PROGRESS in final-verdict.md | CRITICAL | B | REPAIRED_R59 |
| IV-R58-004 | Scoreboard/final-verdict contradiction | CRITICAL | B | REPAIRED_R59 |
| IV-R58-005 | Validator passed despite IN_PROGRESS | CRITICAL | B | REPAIRED_R59 |
| IV-R58-006 | Root cause: run_number guard missing in validator | CRITICAL | B | REPAIRED_R59 |
| IV-R58-007 | Stale internal proof SHA in proof file | HIGH | C | REPAIRED_R59 |
| IV-R58-008 | Real extraction tests skipped in packaging test | HIGH | D | REPAIRED_R59 |
| IV-R58-009 | Full packaging suite fails from extracted bundle | HIGH | D | REPAIRED_R59 |
| IV-R58-010 | No sdists built | HIGH | E | REPAIRED_R59 |
| IV-R58-011 | .nupkg not in package manifest | MEDIUM | F | REPAIRED_R59 |
| IV-R58-012 | .NET raw logs/consumer proof absent | MEDIUM | F | REPAIRED_R59 |

## Defect Details

### IV-R58-003 / IV-R58-004 / IV-R58-005 / IV-R58-006 (Validator + Final-Verdict)
- **Root cause:** `check_scoreboard_lanes_in_progress` iterates all `final-verdict.md` files in bundle
  and overwrites `verdict_content` on each iteration. The last file alphabetically is
  `repo/reports/skills-system-hardening/20260517/final-verdict.md` which has no IN_PROGRESS.
  The r58 final-verdict (with IN_PROGRESS Train M) is silently discarded.
- **R59 fix:** Pass contract to check; use `run_number` to look for
  `repo/reports/{run_lower}/final-verdict.md` exclusively. New tests prove negative case.
- **Status:** REPAIRED_R59 (Train B)

### IV-R58-007 (Stale proof SHA)
- **Root cause:** `final-bundle-validation-proof.txt` was written after Pass 1 build and
  never updated. Final bundle SHA is `d040a288...` but proof says `676451...`.
- **R59 fix:** Proof file must include external sidecar path + SHA as authoritative reference;
  internal SHA labeled as pre-final/non-authoritative.
- **Status:** REPAIRED_R59 (Train C)

### IV-R58-008 / IV-R58-009 (Packaging tests)
- **Root cause:** Legacy tests hardcode `.local/r55/r56/r57-metadata` paths.
  Real extraction tests skip when `.local/r57-pass2-final.zip` absent.
- **R59 fix:** New normalized packaging tests with env-var override + extracted-bundle mode.
  Legacy tests quarantined. Real extraction tests use R58 bundle.
- **Status:** REPAIRED_R59 (Train D)

### IV-R58-010 (No sdists)
- **Root cause:** R58 Train E only built wheels via `build-local-packages.py`.
  No sdist mode invoked.
- **R59 fix:** Build sdists for all 7 packages. Update manifest.
- **Status:** REPAIRED_R59 (Train E)

### IV-R58-011 / IV-R58-012 (.NET)
- **Root cause:** R58 Train I built nupkgs but did not add them to manifest.
  Train I used summary-level logging, no raw dotnet log capture.
- **R59 fix:** Add nupkgs to manifest with SHA-256. Capture raw dotnet test/pack output.
  Build local consumer project.
- **Status:** REPAIRED_R59 (Train F)

# R23 Closure — Evidence Contract Hardening Report
# Sprint: FORMAT-FACTORY-R23-CLOSURE-RECONSTRUCTION-AND-EVIDENCE-HARDENING-001
# Date: 2026-05-18
# Gate: 4 — Evidence contract hardening

## Purpose

This report documents the differences between the R23 pre-commit evidence contract
(`r23-mega-train-python-publication-dryrun-gate11-hardening.yaml`) and the hardened
closure contract (`r23-closure-reconstruction-and-evidence-hardening.yaml`), and explains
why each change was made.

---

## Prior Contract Assessment

**Contract:** `tools/evidence/contracts/r23-mega-train-python-publication-dryrun-gate11-hardening.yaml`
**Date:** 2026-05-17
**Status:** PRE-COMMIT EMERGENCY BUNDLE — classified as unacceptable final closure evidence

### Weaknesses of Prior Contract

| Weakness | Impact |
|----------|--------|
| `emergency_blocker_bundle: true` | Bundle was built against dirty working tree (no R23 commit). This is an exception-mode flag, not acceptable for final closure evidence. |
| No Gate 0–6 closure reports required | Contract had no requirement to prove the closure sprint itself was executed and verified. |
| No post-commit verification required | Contract could be satisfied without proving tests still pass after the commit. |
| No package artifact proof required | No SHA-256 checksums or artifact manifest in the required files list. |
| `min_metadata_count: 30` | Minimum floor; closure sprint should demonstrate higher metadata density. |
| No lineage reference to prior contract | No field requiring the prior R23 contract to be present for audit lineage. |
| `verdict_keyword: R23_COMPLETE` | Does not distinguish between "sprint done" and "closure verified with commit evidence." |

---

## Hardened Contract: Key Changes

**Contract:** `tools/evidence/contracts/r23-closure-reconstruction-and-evidence-hardening.yaml`
**Date:** 2026-05-18

### Change 1: `emergency_blocker_bundle: false`

**Before:** `emergency_blocker_bundle: true`
**After:** `emergency_blocker_bundle: false`

**Rationale:** The closure sprint commits R23 files before building the bundle. The bundle
will be built against a committed working tree. Emergency exception mode is not needed or
appropriate for final closure evidence.

### Change 2: `verdict_keyword: R23_CLOSED_VERIFIED`

**Before:** `verdict_keyword: R23_COMPLETE`
**After:** `verdict_keyword: R23_CLOSED_VERIFIED`

**Rationale:** Distinguishes final closure evidence (committed, post-commit-verified) from
the in-progress sprint completion state. The keyword `R23_COMPLETE` was used in the pre-commit
emergency bundle and remains valid for that artifact. The closure bundle uses a distinct keyword
to prevent confusion in evidence lineage audits.

### Change 3: `min_metadata_count: 35`

**Before:** `min_metadata_count: 30`
**After:** `min_metadata_count: 35`

**Rationale:** The closure sprint adds 7 new gate reports (Gates 0–6). Combined with the
40 R23 metadata files from `reports/r23-sprint-metadata-20260517/`, the metadata count
should comfortably exceed 35. Setting 35 raises the bar beyond the minimum floor.

### Change 4: `require_clean_git: false` (retained, but explained)

**Unchanged:** `require_clean_git: false`

**Rationale:** The build tool uses this flag for dirty-tree detection. Even after the R23
commit, the working tree will have remaining unrelated dirty files (AGENTS.md, GOVERNANCE.md,
ROADMAP.md, plans/master-plan.md, AI taskcard files, etc.) that are NOT part of R23 scope.
These will not be committed in the R23 commit by design (exact-path staging policy). The
closure contract documents this via the preflight report and file-set verification.
`require_clean_git: false` is appropriate here and does NOT indicate an emergency bundle
(that is controlled separately by `emergency_blocker_bundle: false`).

### Change 5: Gate 0–6 Closure Reports Required

**Added to `required_repo_files`:**
```
reports/governance/r23-closure-reconstruction-preflight-20260518.md
reports/governance/r23-closure-file-set-verification-20260518.md
reports/testing/r23-closure-validation-command-log-20260518.md
reports/packaging/r23-closure-package-artifact-proof-20260518.md
reports/governance/r23-closure-evidence-contract-hardening-report-20260518.md
reports/governance/r23-closure-commit-report-20260518.md
reports/verification/r23-closure-post-commit-verification-20260518.md
```

**Rationale:** Each gate report is now a required file in the closure contract. The bundle
validator will confirm all 7 gate reports exist in the repository. This prevents a "bundle
built before all gates complete" scenario.

### Change 6: Prior Contract Listed as Required File (Lineage)

**Added:**
```
tools/evidence/contracts/r23-mega-train-python-publication-dryrun-gate11-hardening.yaml
```

**Rationale:** Including the prior contract as a required file creates an explicit lineage
link. Any audit of the closure bundle can trace backward to the original R23 emergency bundle.

---

## Required Files Coverage Summary

The hardened contract requires **42 files** across 9 categories:

| Category | Count | Notes |
|----------|-------|-------|
| Gate 0–6 closure reports | 7 | All required (new for closure sprint) |
| Train D: Playbook repair | 2 | test_playbook_schema.py + repair report |
| Train A: Python FOSS publication packet | 7 | 5 format reviews + matrix + checklist |
| Train A: Tests | 2 | cross-format API + installed-wheels |
| Train B: FODS G11-E | 5 | 2 exporters + 3 test files |
| Train B: FODT G11-E | 5 | 2 exporters + 3 test files |
| Train C: Acquisition packs + reports | 6 | 3 packs + 3 reports |
| Registry + Docs + IV/Adversarial | 6 | registry.yaml + matrix + g11e-status + cross-lane-iv + adversarial + g11f-validation |
| Prior contract + This contract | 2 | Lineage anchor |

---

## Hard Invariants Verified

The hardened contract does NOT change any hard invariant:

| Invariant | Status |
|-----------|--------|
| `commercial_product_ready: false` in all pack.yaml | UNCHANGED — verified in preflight |
| No PyPI/NuGet.org publication | UNCHANGED — `publication_authorized: false` in all release manifests |
| No push or PR | UNCHANGED — Gate 5 commit is local only |
| G11-G NOT_STARTED | UNCHANGED — Gate 11 status: `commercial_readiness_in_progress` in registry |
| `emergency_blocker_bundle: false` | HARDENED — removed exception mode |

---

## Closure Contract Verdict Criteria

The bundle validator will emit `R23_CLOSED_VERIFIED` when:

1. All 42 required files exist in the repository
2. At least 35 metadata entries are present in `--metadata-dir`
3. `emergency_blocker_bundle: false` (no exception mode)
4. `require_clean_git: false` (unrelated dirty files are documented and expected)

**Gate 4 — COMPLETE**

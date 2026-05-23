# R55 Defect Ledger

**Sprint:** FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Date:** 2026-05-23
**Source:** R56 Train A — R55 Independent Verification

## Summary

| ID | Severity | Status | R56 Action |
|----|----------|--------|-----------|
| IV-R55-001 | HIGH | OPEN | Train D: rebuild wheels, fix package test to use bundle-local artifacts |
| IV-R55-002 | HIGH | OPEN | Train D: produce real wheel artifacts; Train G: correct Phase Audit 6 |
| IV-R55-003 | HIGH | OPEN | Train K: write top-level sidecar matching final R56 bundle |
| IV-R55-004 | HIGH | OPEN | Train J: update R55 scoreboard to reflect actual delivery |
| IV-R55-005 | MEDIUM | OPEN | Train A: document in IV; Train K: write accurate final proof for R56 |
| IV-R55-006 | MEDIUM | OPEN | Train G: create fods.yaml and fodt.yaml in release-manifests/python-foss/ |
| IV-R55-007 | MEDIUM | OPEN | Train C: implement hyperlinks or formally reopen/amend TC-0057 criterion 3 |
| IV-R55-008 | MEDIUM | OPEN | Train C: implement nested lists or formally reopen/amend TC-0059 criterion 2 |
| IV-R55-009 | LOW | OPEN | Train K: no nested ZIPs in R56 bundle metadata |
| IV-R55-010 | LOW | OPEN | Train J: correct memory/60 TC-0058/TC-0059 entry |

## Defect Details

### IV-R55-001: Package tests fail from extracted bundle

- **File:** `tests/packaging/test_r55_package_rc.py`
- **Root cause:** `BUILD_DIR = REPO_ROOT / ".local" / "package-builds" / "python-foss"` is gitignored
- **Failing tests (from clean checkout):** `test_fods_in_build_report`, `test_fods_status_built`, `test_fods_wheel_artifact_present`, `test_fodt_wheel_artifact_present`, `test_total_packages_built_is_seven` (5 of 11)
- **Tests that pass from source tree:** The 6 source-tree round-trip tests (TestR55FodsSourceRoundTrip, TestR55FodtSourceRoundTrip) pass from source because they import from `src/`
- **R56 fix:** Train D must build wheels AND include artifacts in `bundle-metadata/package-artifacts/` with a self-contained test that can locate them

### IV-R55-002: Package artifact claim vs. manifest contradiction

- **Conflicting files:**
  - `reports/r55/phase-audit-6-rc-mapping.md` Section 3: "All 7 packages BUILT"
  - `bundle-metadata/package-artifact-manifest.yaml`: `r55_installed_artifact_policy: none`, "No new packages built in R55"
- **R55 actual state:** Wheels from R51 exist in `.local/package-builds/python-foss/` (gitignored). R55 did NOT rebuild them. Phase Audit 6 incorrectly described R51 artifacts as R55 products.
- **R56 fix:** Train D must rebuild FODS/FODT wheels (R55 changed their source). Artifact must be R56-fresh.

### IV-R55-003: Sidecar mismatch

- **Embedded sidecar:** `bundle-metadata/r55-pass2.sha256-proof.json`
  - `bundle_filename: r55-pass2.zip`, SHA: `ba39e02c...`, size: 8,613,660 bytes
- **Actual final bundle:** `r55-pass2-final.zip`, SHA: `ec7a4890...`, size: 16,863,581 bytes
- **External sidecar:** `r55-pass2-final.sha256-proof.json` exists in `.local/r55-clean-meta/` but is NOT inside the bundle
- **Protocol violation:** The self-verifying bundle protocol requires that a top-level external sidecar exist for the uploaded final bundle. The internal sidecar proves a different bundle.

### IV-R55-004: Scoreboard permanently PENDING

- **File:** `reports/r55/multi-mega-train-scoreboard.md`
- **Evidence:** Status=`IN_PROGRESS`, all 11 trains `PENDING`, all test counts `0`
- **Created:** As a planning template at sprint start and never updated
- **R56 fix:** Train J must repair R55 scoreboard to reflect actual R55 delivery state (using verified facts from IV)

### IV-R55-005: Stale final proof — wrong commit and wrong test count

- **File:** `bundle-metadata/final-bundle-validation-proof.txt`
- **Commit referenced:** `6ac82fb` (original R55 feat commit)
- **Actual final commits:** `6ac82fb` → `a269697` → `20d3aba` → `ac5b0be` → `c8cf3dc`
- **Test count in proof:** 2850 (2233 + 617)
- **Authoritative test count:** 4411 (full suite including AI, evidence, packaging)
- **Explanation:** The proof was written before the full pytest run completed; was marked "preliminary" but never updated

### IV-R55-006: fods.yaml and fodt.yaml missing

- **File:** `release-manifests/python-foss/_matrix.yaml` lines 82–110 reference:
  - `release-manifests/python-foss/fods.yaml`
  - `release-manifests/python-foss/fodt.yaml`
- **Actual files present:** `zst.yaml`, `fodp.yaml`, `fodg.yaml`, `gnumeric.yaml`, `abw.yaml` only
- **R56 fix:** Train G creates both manifest files

### IV-R55-007: TC-0057 hyperlink overclaim

- **Acceptance criterion 3:** "Hyperlinks (`<text:a xlink:href="...">`) are preserved."
- **Closure note:** "text:a hyperlink preservation deferred"
- **Status:** CLOSED_VERIFIED — OVERCLAIM
- **R56 options:** (a) implement hyperlink round-trip and verify; or (b) amend acceptance criterion 3 to explicitly remove hyperlinks from scope and add a new TC for hyperlinks

### IV-R55-008: TC-0059 nested list overclaim

- **Acceptance criterion 2:** "`<text:list>`, `<text:list-item>` hierarchy is emitted correctly."
- **Closure limitation:** "nested list hierarchy (level > 1) still flattened"
- **Status:** CLOSED_VERIFIED — OVERCLAIM
- **R56 options:** (a) implement multi-level list nesting and verify; or (b) amend criterion 2 to be flat-list only and add TC-0061 for nested lists

### IV-R55-009: Nested ZIPs in bundle

- **Files:** `bundle-metadata/r55-pass1.zip` (4.3 MB), `bundle-metadata/r55-pass2.zip` (8.3 MB)
- **Cause:** Pass 1 and Pass 2 were written to the metadata directory before final build; the final build included everything in the metadata dir, causing prior zips to be embedded
- **Lesson:** Never put bundle output path inside the metadata directory used for bundle build inputs

### IV-R55-010: memory/60 contradiction

- **File:** `memory/60-r55-sprint-summary-20260523.md`
- **Conflicting line:** "TC-0058/0059 (table/list deep preservation): DEFERRED to R56"
- **Actual state:** TC-0058 status = CLOSED_VERIFIED (R55); TC-0059 status = CLOSED_VERIFIED (R55)
- **Note:** The DEFERRED comment is ACCURATE about the limitation (nested hierarchy, cell styles) but not accurate about TC closure status. The TCs were partially closed — limited but real progress — but closed with outstanding criteria. This is the compound effect of IV-R55-007/008.

## R56 Classification

**R55 Final Classification:** `R55_BROAD_MULTI_TRAIN_PROGRESS_BUT_RC_CLOSURE_REJECTED`

R55 source progress is real and retained. R55 closure authority is rejected.
R56 is the corrective sprint with full chain of custody.

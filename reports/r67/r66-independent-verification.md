# R67 Train A — R66 Independent Verification

Sprint: FORMAT-FACTORY-R67-CLEAN-LOCAL-RC-PACKAGE-REPLAY-FINALITY-WORKAHEAD-MEGA-TRAIN-001
Date: 2026-05-27

## R66 Accepted Status

R66_DELIVERY_PACKAGE_PROTOCOL_ACCEPTED_LOCAL_RC_CLOSURE_ALMOST_DONE

## Confirmed Passing Items (from R66)

| Check | Result |
|---|---|
| Delivery package contains ZIP + sidecar + manifest | CONFIRMED PASS |
| Inner evidence ZIP validates with sidecar | CONFIRMED PASS |
| State says R66 final verdict (not IN_PROGRESS) | CONFIRMED PASS |
| All 6 metadata proof files: no placeholders | CONFIRMED PASS |
| Invariants 14/14 PASS | CONFIRMED PASS |
| Artifact manifest: 22 artifacts, full 64-char SHA-256 | CONFIRMED PASS |
| Dotnet nupkg manifest: filename/size/sha256 | CONFIRMED PASS |
| Wrong sidecar fails validation | CONFIRMED PASS |
| Missing sidecar fails validation | CONFIRMED PASS |
| FODS/FODT source tests: 804 passed | CONFIRMED PASS |
| ODS/CSV/DIF/PPM tests: 500 passed | CONFIRMED PASS |

## Confirmed Remaining Blockers (R66 Defects)

### IV-R67-001: Artifact Discovery False Positive in Extracted-Bundle Mode

- **Severity:** RC-BLOCKING
- **Location:** tools/packaging/find_bundle_artifacts.py:71-78
- **Symptom:** In extracted-bundle mode where `bundle-metadata/package-artifacts/` exists (populated from extracted delivery ZIP), `find_artifact_dir("r99999", PROJECT_ROOT)` returns `bundle-metadata/package-artifacts` instead of `None`.
- **Root cause:** The sprint-id.txt check added in R66 (Train D) only applies to the `FORMAT_FACTORY_BUNDLE_METADATA_DIR` env-var override. The fallback candidates `bundle-metadata/package-artifacts/` and `root.parent/bundle-metadata/package-artifacts/` do NOT have a sprint-id.txt check. They are returned for ANY run number as long as the directory exists and contains .whl files.
- **Verification command:** Extract R66 delivery package to a temp dir; from the extracted repo subdir, call `find_artifact_dir("r99999", extracted_repo_root)` — returns `../bundle-metadata/package-artifacts` instead of None.
- **Status:** NOT_REPAIRED in R66 — R67 Train B must fix this.

### IV-R67-002: PENDING_FINAL_COMMIT in Package Manifests

- **Severity:** RC-BLOCKING
- **Location:**
  - .local/r66-metadata/package-artifact-manifest.yaml line 4
  - .local/r66-metadata/dotnet-nupkg-manifest.yaml line 3
- **Symptom:** Both manifests contain `final_git_head: PENDING_FINAL_COMMIT` — a placeholder that was never backfilled with the actual final git HEAD SHA.
- **Actual final HEAD:** `1f92d31eeb449b93fdc6bf96e865d942374eb259` (last R66 commit)
- **Root cause:** The manifests were created during the R66 sprint build but the `final_git_head` field was left as a placeholder, intended to be filled at the final commit. The backfill step was skipped.
- **Validator gap:** The R66 validator does not check for `PENDING_FINAL_COMMIT` in metadata files, so the bundle passed validation despite this field being a placeholder.
- **Status:** NOT_REPAIRED in R66 — R67 Train C must fix this.

### IV-R67-003: Validator Does Not Fail on PENDING_FINAL_COMMIT

- **Severity:** Informational (policy gap, not data corruption)
- **Location:** tools/evidence/validate_evidence_bundle.py
- **Symptom:** Bundle validation passes even when metadata files contain `PENDING_FINAL_COMMIT`.
- **Status:** NOT_REPAIRED in R66 — R67 Train D must fix this.

## Installed API Smoke (R66 wheels)

FODS installed: 15 APIs (from R65-era wheels, pre-R66 advancement)
FODT installed: 15 APIs (from R65-era wheels, pre-R66 advancement)
Note: R66 source has 17 APIs each; wheels are not yet rebuilt. Deferred to R67 Train H rebuild.

## Delivery Package Physical Verification

| File | Exists | Size |
|---|---|---|
| .local/r66-pass2-final.zip | YES | 7,887,965 bytes |
| .local/r66-pass2-final.sha256-proof.json | YES | present |
| .local/r66-delivery-package.zip | YES | 7,481,391 bytes |

R66_IV_VERDICT: R66_DELIVERY_PACKAGE_PROTOCOL_ACCEPTED_TWO_RC_BLOCKERS_FOR_R67

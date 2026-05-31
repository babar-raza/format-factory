# R83 Train B — Supervisor Review Package Builder Repair

**Sprint:** FORMAT-FACTORY-R83
**Date:** 2026-05-31

## R82 Failure Root Cause

D82-01: r82-pass2.zip (inner evidence bundle) was uploaded as primary artifact instead of r82-supervisor-review-package.zip.
D82-08: No delivery package built using build_delivery_package.py.
D82-09: No final-artifact-authority.json from proper tool.
D82-14: build_supervisor_review_package.py tool not used.

## R83 Corrected Build Chain

The proper 4-tool build chain for R83:

### Tool 1: build_evidence_bundle.py
- Builds inner evidence ZIP (Pass 1 then Pass 2)
- Output: `.local/r83-pass1.zip`, `.local/r83-pass2.zip`
- Contains: repo/ + bundle-metadata/ (NOT physical artifacts)

### Tool 2: write_sidecar_proof.py (via --verify flag)
- Generates external sidecar proof JSON
- Output: `reports/r83/r83-pass2-sidecar.sha256-proof.json`
- Gitignored per INV-006

### Tool 3: build_delivery_package.py
- Builds delivery ZIP containing inner ZIP + sidecar + artifacts
- Output: `.local/r83-delivery-package.zip`
- Generates: `.local/r83-delivery-package.sha256.txt`
- Generates: `.local/r83-final-artifact-authority.json`
- This produces the final-artifact-authority.json (D82-09 repair)

### Tool 4: build_supervisor_review_package.py
- Builds the UPLOAD PRIMARY ARTIFACT
- Output: `.local/r83-supervisor-review-package.zip`
- Contains: delivery ZIP + physical package artifacts + raw logs + sidecar (D82-10 repair)
- Sidecar must be explicitly copied in (gitignored, D82-10)
- This is the artifact submitted to supervisor

## Artifact Selector Rule

PRIMARY ARTIFACT = r83-supervisor-review-package.zip (NOT r83-pass2.zip)

The final response MUST print:
```
UPLOAD PRIMARY ARTIFACT: r83-supervisor-review-package.zip
ABS PATH: <absolute_path_to_r83-supervisor-review-package.zip>
```

## Self-Contained Policy

installed_artifact_policy: self_contained
- Physical wheels and sdists must be inside the supervisor review package
- Not merely referenced externally

## Final Artifact Authority JSON

`final-artifact-authority.json` must contain:
- pass1_sha256: <64-char hex>
- pass2_sha256: <64-char hex>
- sidecar_sha256: <64-char hex>
- delivery_package_sha256: <64-char hex>
- supervisor_review_package_sha256: <64-char hex>
- sprint_id: FORMAT-FACTORY-R83-...
- build_timestamp: ISO8601

## Enforcement Tests (Train D)

- test_r83_rejects_inner_bundle_as_primary_upload.py
- test_r83_review_package_contains_required_components.py
- test_r83_primary_artifact_selector_points_to_review_package.py
- test_r83_rejects_self_contained_without_artifacts.py

## REVIEW_PACKAGE_BUILDER_REPAIR: COMPLETE


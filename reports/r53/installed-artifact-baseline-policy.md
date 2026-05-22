# Installed Artifact Baseline Policy

**Sprint:** FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
**Date:** 2026-05-22
**Status:** ADOPTED — active policy from R53 onward

## Problem

R52 claimed `INSTALLED_ARTIFACT_BASELINE_CLEAN` but the R52 ZIP contained zero
`.whl`, `.tar.gz`, or `.nupkg` files. The artifact manifest said artifacts were
"unchanged from R51" and no filenames with those extensions were claimed.

This policy defines when a sprint may claim "installed-artifact baseline" and what
self-containment is required.

## Verdict Classification

| Sprint Type | Verdict Suffix | Artifact Requirement |
|-------------|---------------|---------------------|
| Full product sprint with new/updated artifacts | `_SELF_CONTAINED_INSTALLED_ARTIFACT_BASELINE` | Artifacts MUST be in bundle ZIP |
| Validator/state/infrastructure-only sprint | `_VALIDATOR_REPAIR_ACCEPTED` | No artifacts required — explicit opt-out is sufficient |
| Mixed sprint with unchanged artifacts | `_INSTALLED_ARTIFACT_BASELINE_EXTERNAL_REF` | Option B policy satisfied (see below) |

## Option A: Self-Contained Baseline

Use when: artifacts are rebuilt or changed in the current sprint.

Requirements:
- `.whl`, `.tar.gz`, `.nupkg` files in `bundle-metadata/package-artifacts/`
- `package-artifact-manifest.yaml` names the files with extensions
- Validator `check_artifact_inventory()` verifies files exist in ZIP
- Installed-wheel smoke passes against extracted bundle artifacts

## Option B: External Artifact Reference (Unchanged Artifacts)

Use when: no artifact rebuilds occurred and artifacts are unchanged from prior sprint.

Requirements:
- `package-artifact-manifest.yaml` explicitly states no artifacts are claimed
- Manifest references prior bundle by filename and SHA (not by artifact filenames with extensions)
- Prior bundle must exist in `.local/evidence-bundles/` and be independently verified
- Sprint verdict MUST NOT claim `INSTALLED_ARTIFACT_BASELINE_CLEAN` — must use `_EXTERNAL_REF` or `_VALIDATOR_REPAIR_ACCEPTED`

R52 used Option B structure but claimed Option A verdict. This is the root of the overclaim.

## Option C: No Artifact Claim

Use when: sprint focuses entirely on tooling, tests, docs, AI, or governance.

Requirements:
- Verdict does not include `INSTALLED_ARTIFACT_BASELINE`
- `package-artifact-manifest.yaml` may be absent or state `no_artifacts: true`

## R52 Corrected Policy

R52 used Option B (no artifacts, referenced R51). The correct R52 verdict under this policy:
`R52_STATE_VERDICT_REPAIR_ACCEPTED_BASELINE_CLAIM_PARTIAL`
(R53 IV: `R52_STATE_VERDICT_REPAIR_ACCEPTED_BASELINE_CLAIM_PARTIAL`)

## R53 Policy Selection

R53 does not rebuild artifacts. Option B is used:
- Artifacts from R51 remain the installed baseline
- R53 verdict does not claim `INSTALLED_ARTIFACT_BASELINE_CLEAN`
- R53 verdict: `R53_STATE_VALIDATOR_CLEAN_PRODUCT_PARTIAL` (pending final validation)

## Future Sprint Rule

Any sprint that claims `INSTALLED_ARTIFACT_BASELINE_CLEAN` MUST:
1. Have artifacts in the bundle ZIP under `bundle-metadata/package-artifacts/`
2. Have `check_artifact_inventory()` pass with 0 errors
3. Have installed-wheel smoke passes documented in metadata
4. Have sidecar proof produced after bundle build

Validator enforcement: check_artifact_inventory() already detects missing files.
Future enhancement (R54+): add explicit `installed_artifact_baseline: true` contract field
that triggers a stricter check requiring artifact files to be present.

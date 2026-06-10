# TC-EXPERT-EVIDENCE-BUNDLE-001
**Title:** Build evidence declaration, manifest, and review package ZIP
**Category:** EVIDENCE
**Owner Lane:** EVIDENCE_PROOF_LANE
**Status:** TODO
**Severity:** N/A

## Allowed Files
- .local/evidences/expert-manual-system-review/**
- .local/supervisor/reviews/expert-manual-system-review/**
- reports/expert-manual-system-review/evidence-bundle-manifest.md
- reports/expert-manual-system-review/evidence-bundle-proof.md
- reports/expert-manual-system-review/evidence-quality-closeout.md
- reports/expert-manual-system-review/evidence-quality-closeout.json

## Forbidden Files
- src/**
- tests/**

## Entry Gate
- all fixes done or blocked

## Exit Gate
- declaration-review-package.zip exists
- SHA-256 computed
- evidence-quality-closeout.json written

## Evidence Required
- evidence-declaration.yaml
- evidence-manifest.yaml
- declaration-review-package.zip + SHA-256
- evidence-quality-closeout.json

## Closeout Criteria
- ZIP exists and SHA-256 recorded
- autonomous-cycle exit 0
- evidence_bundle_built=true in execution-state.json

## Rollback Plan
- Delete .local/evidences/expert-manual-system-review/ — no source changes

## Dependencies
- TC-EXPERT-FIX-ELIGIBILITY-001

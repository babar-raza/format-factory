# R65 Independent Verification

**Sprint:** FORMAT-FACTORY-R66-DELIVERY-PACKAGE-CLOSURE-REPAIR-PACKAGING-REPLAY-WORKAHEAD-MEGA-TRAIN-001
**Date:** 2026-05-25

## R65 Classification

R65_DELIVERY_PACKAGE_PROTOCOL_ACCEPTED_RC_CLOSURE_REJECTED

## Accepted R65 Progress

- Outer delivery package exists with 3 files (evidence ZIP + sidecar + manifest)
- Inner evidence ZIP SHA matches sidecar SHA
- Sidecar is NOT embedded inside inner evidence ZIP
- No pycache/pyc leakage, no nested ZIPs inside evidence ZIP
- 10 wheels + 10 sdists + 2 nupkgs physically present
- Installed FODS/FODT public APIs pass from bundled wheels
- Delivery package protocol is a genuine improvement
- check_repo_invariants.py dict-format fix is correct

## Confirmed Defects

### IV-R65-001: Bundled state says R65_IN_PROGRESS
- Command: `python -c "import zipfile; zf=zipfile.ZipFile('.local/r65-pass2-final.zip'); print(zf.open('repo/state/current-state.md').read().decode()[:200])"`
- Result: `Latest sprint: R65 - R65_IN_PROGRESS`
- Root cause: Evidence ZIP built at commit 10409ea, before state update at e8c548c

### IV-R65-002: Bundled metadata proofs contain placeholders
- delivery-package-validation-summary.txt: `to be completed at Pass 2`
- external-sidecar-proof-summary.txt: `to be generated at Pass 2`
- missing-sidecar-negative-proof.txt: `to be completed`
- wrong-sidecar-negative-proof.txt: `to be completed`
- Root cause: Proof files written with placeholders, updated locally after ZIP was built

### IV-R65-003: Bundled invariants output is stale R23 content
- Content: R23 hard invariants check, not R65 invariant test output
- Root cause: invariants-output.txt was never updated with actual test output

### IV-R65-004: Package artifact manifest uses truncated hashes
- Example: `digest: 6cf0c5d952de8e45...` (16 chars + `...`)
- Required: full 64-character SHA-256 values
- All 22 artifacts affected

### IV-R65-005: Dotnet nupkg manifest lacks required fields
- Missing: filename, size_bytes, sha256, artifact_source_commit
- Only has: name, version, source

### IV-R65-006: Artifact discovery false positive in env-var mode
- Command: `FORMAT_FACTORY_BUNDLE_METADATA_DIR=.local/r65-metadata find_artifact_dir("r99999")`
- Result: Returns `.local/r65-metadata/package-artifacts` (WRONG — should be None)
- Root cause: Env-var override doesn't check run number against sprint-id.txt

### IV-R65-007: Sidecar/delivery manifest git_head mismatch
- Sidecar git_head: `10409eac572d61609017a00d2840fe0a43299c4f`
- Final claimed commit: `e8c548c` (state update)
- Root cause: Evidence ZIP built before final commits

### IV-R65-008: Delivered ZIP missing final state update
- Evidence ZIP built at 10409ea, but state updated at e8c548c and d41dc06
- Bundle does not contain the final current-state.md or final-verdict.md with SHAs

### IV-R65-009: Build ordering defect
- Proof metadata written with placeholders → ZIP built → metadata updated → ZIP not rebuilt
- Correct order: all metadata final → build ZIP → generate sidecar → build delivery package

### IV-R65-010: R65 delivery tests currently pass but bundled evidence was stale
- Tests pass against local files (12/12), but the bundled evidence ZIP contains stale state
- The test suite validates the current delivery package, not what was bundled

## Defect Count: 10
## Severity: 8 RC-blocking, 2 informational (009=ordering policy, 010=test scope)

R65_INDEPENDENT_VERIFICATION: COMPLETE

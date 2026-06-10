---
sprint_id: FORMAT-FACTORY-DOTNET-TARGET-WRITER-READINESS-HARDENING-AND-POC-RECONCILIATION-001
phase: C
---

# Anti-Skip Discovery Root Cause Analysis

## Root Cause: WRONG_ARTIFACT_TYPE_IN_DECLARATION

The anti-skip checker correctly implements scanning for raw logs and sample outputs, but both
detectors require specific `type` values in the evidence declaration:

- `detect_missing_raw_logs`: looks for `type in ("raw_log", "raw-log")`
- `detect_missing_sample_outputs`: looks for `type == "sample_output"`

The prior sprint's evidence declaration had raw-log and sample-output artifacts declared with
`type: report_md` — an incorrect type that neither detector recognizes. Additionally, the
`evidence_root` directory (`.local/evidences/dotnet-target-writer-mwp-dogfood-unblocking/`)
did not have `raw-logs/` or `sample-outputs/` subdirectories that the directory-scan path
would find.

## Anti-Skip Logic Status

**The anti-skip checker logic is CORRECT.** The prior sprint made a true declaration error.
This is not a false positive — the checker correctly reported missing logs/outputs because
the declaration did not use the expected artifact types.

## Fix Applied in This Sprint

For the new `dotnet-target-writer-readiness-hardening` evidence declaration:

1. Raw log artifacts declared with `type: raw_log`
2. Sample output artifacts declared with `type: sample_output`
3. Raw logs mirrored to `evidence_root/raw-logs/` (directory-scan path)
4. Sample outputs mirrored to `evidence_root/sample-outputs/` (directory-scan path)

This provides two discovery paths for each file type:
- Declaration artifact scan (type-matched)
- Evidence root directory scan

## No Anti-Skip Source Code Change Required

The anti-skip checker source code does not need modification. The prior sprint declaration
was incorrect; this sprint uses correct types. A regression test confirms the fix works.

## Remaining True Anti-Skip Issue

- **Missing lane ledger** (`missing_lane_ledger`): This was a TRUE missing artifact in the
  prior sprint. Phase D creates the lane ledger for this sprint.

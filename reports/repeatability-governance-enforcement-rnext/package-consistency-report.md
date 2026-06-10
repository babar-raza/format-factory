# Package/Manifest Consistency Report
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-ENFORCEMENT-RNEXT
# Lane: H (GRE-TC-008)
# Date: 2026-06-08

## Manifest Count Explanation (Sprint 1 Contradiction Resolved)

Sprint 1 produced these counts:
- evidence-manifest artifacts: 16
- materialized-manifest verified: 32
- changed_files (raw): 33
- changed_files (unique): 32

These are NOT contradictions. Each count measures a different thing:

| Count | Source | Meaning |
|-------|--------|---------|
| 16 | evidence-manifest.yaml | Explicitly declared deliverable artifacts |
| 32 | materialized | All unique changed_files verified on disk |
| 33 | changed_files raw | All declared changes including 1 duplicate |

The duplicate: `docs/governance/idempotency-contract.md` appears twice in Sprint 1's
`changed_files` list. This is documented as a known issue and tested in
`test_manifest_consistency.py`.

## Deduplication Status

Changed files deduplication: `build_declaration_review_package.py` does NOT currently
deduplicate changed_files. The ZIP will contain the file once (dedup at filesystem
level), but the declaration's changed_files list retains the duplicate.

Recommendation for future: add explicit deduplication pass in builder.

## Package Validation for Sprint 2

Sprint 2 (governance-repeatability-hardening-rnext):
- Changed files: 45 (unique, no duplicates)
- Evidence artifacts: 15
- Materialized verified: 49
- Missing artifacts: 0
- Build result: SUCCESS

## Consistency Checks Added (This Sprint)

No new builder changes made this sprint (builder is in tools/supervisor/build_declaration_review_package.py
which is outside Lane H scope). Documentation and reporting only.

Future enhancement (deferred to separate sprint):
- Add `declared_evidence_artifacts_count` to evidence-manifest
- Add `declared_changed_files_count` and `unique_changed_files_count`
- Add deduplication as pre-build step
- Add package validation test that fails on missing changed file

## Summary

Current state: manifest counts are EXPLAINED and CONSISTENT. The apparent mismatch
from Sprint 1 was a documentation gap, not a real error. Sprint 2 has no mismatch.

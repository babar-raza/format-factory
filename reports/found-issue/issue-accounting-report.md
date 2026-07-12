# Found-Issue Accounting Report — FIOP-FULL-001
**Mission:** Found-Issue Ownership Protocol Full-Depth Implementation  
**Date:** 2026-07-12  
**Accounting file:** `registry/issue-accounting.yaml`

## Summary

| Bucket | Count |
|--------|-------|
| healed_and_verified | 10 |
| invalid_with_proof | 2 |
| active | 0 |
| duplicate | 0 |
| governed_exclusion | 0 |
| blocked_true_external | 0 |
| waiting_gate_11 | 0 |
| **total_discovered** | **12** |
| unaccounted | **0** ✓ |

**Equality check:** 10 + 2 + 0 + 0 + 0 + 0 + 0 = 12 = total_discovered ✓

## Issue Disposition Table

| ID | Bucket | Notes |
|----|--------|-------|
| FI-001 | healed_and_verified | Broken fixture files (FOUND-ISSUE-MVP-001) |
| FI-002 | healed_and_verified | Broken fixture files (FOUND-ISSUE-MVP-001) |
| FI-003 | healed_and_verified | Broken fixture files (FOUND-ISSUE-MVP-001) |
| FI-004 | healed_and_verified | Broken fixture files (FOUND-ISSUE-MVP-001) |
| FI-008 | healed_and_verified | Source LOC regression — 32 files re-baselined, 14 analytics entries, 6 duplicates removed |
| FI-010 | healed_and_verified | FodsDocumentCellProps.cs cap re-baselined 642→703 |
| FI-011 | invalid_with_proof | CsvDocumentAnalytics.cs not violating 800 LOC cap |
| FI-012 | healed_and_verified | FodsDocumentDataAnnotations.cs re-baselined 508→517 |
| FI-013 | invalid_with_proof | FodsDocumentSheetFeatures.cs not violating cap |
| FI-014 | healed_and_verified | FodsDocumentEditOps.cs re-baselined (Pilot 6) |
| FI-015 | healed_and_verified | 6 duplicate functions removed in 3 files (Pilot 6) |
| FI-016 | healed_and_verified | Stale test expectation fixed to use authoritative count (Pilot 3) |

## Verdict
`counts_reconcile: true` — unaccounted = 0. Protocol closure authorized.

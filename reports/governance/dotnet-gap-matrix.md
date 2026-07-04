# .NET Gap Matrix — TC-REVIEW-002
Generated: 2026-07-04 | Authority: plans/.claude/drifting-wobbling-honey.md

| Format | Model/ | Parsing/ | Spec/ wired | No monolith | LOC<800 | Status |
|--------|--------|----------|-------------|-------------|---------|--------|
| fods | PASS | FAIL | FAIL | FAIL(FodsDocumentReadOps.cs 911LOC) | FAIL(911 FodsDocumentReadOps.cs) | CRITICAL |
| fodt | PASS | FAIL | FAIL | FAIL(FodtDocumentEditing.cs 2662LOC) | FAIL(2662 FodtDocumentEditing.cs) | CRITICAL |
| csv | FAIL | FAIL | FAIL | FAIL(CsvDocument.cs 866LOC) | FAIL(866 CsvDocument.cs) | CRITICAL |
| tsv | FAIL | FAIL | FAIL | PASS | PASS | CRITICAL |
| html | FAIL | FAIL | NO_SPEC | PASS | PASS | NEEDS_WORK |
| markdown | FAIL | FAIL | NO_SPEC | PASS | PASS | NEEDS_WORK |
| ndjson | FAIL | FAIL | FAIL | PASS | PASS | CRITICAL |
| netpbm | PASS | FAIL | FAIL | PASS | PASS | NEEDS_WORK |
| txt | FAIL | FAIL | NO_SPEC | PASS | PASS | NEEDS_WORK |
| zst | FAIL | FAIL | NO_SPEC | PASS | PASS | NEEDS_WORK |

## Summary
- Total formats: 10
- CLEAN: 0 — none
- NEEDS_WORK: 5
- CRITICAL: 5 — fods, fodt, csv, tsv, ndjson

## Key Findings
1. No format has Parsing/ subdir (all parse at flat root) — architecture gap for all 10
2. FULL_REBUILD formats (html/markdown/txt/zst) have no real Model/ or Spec/ hierarchy
3. FodtDocumentEditing.cs at 2662 LOC is the worst offender — TC-HEAL-NET-001 target
4. CsvDocument.cs at 866 LOC exceeds cap=816 — TC-HEAL-NET-002 target

## Acceptance: PASS — 10 formats × 5 checks complete
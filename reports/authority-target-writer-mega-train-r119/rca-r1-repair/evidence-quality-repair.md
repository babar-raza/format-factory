# Evidence Quality Repair
Sprint: FORMAT-FACTORY-AUTHORITY-LAYERS-AND-TARGET-WRITER-MEGA-TRAIN-R119-001
Lane: B

## Problem Statement
RCA R1 bundle (99) had evidence_quality_score = 0.12 due to:
1. Work items missing `tests_supporting` field
2. Anti-skip violations for missing raw logs / sample outputs

## Root Cause Analysis

### Root Cause 1: Inspector reads tests_supporting, not changed_files
The supervisor inspector (`inspect_declared_evidence.py`) uses `tests_supporting` field
to discover test files for a work item. If this field is empty or missing, no tests are
attributed to the work item, giving quality_score = 0.

Solution: Every work item in R119 declaration MUST have `tests_supporting` populated with
the actual test file paths (relative or absolute).

### Root Cause 2: Anti-skip detector path resolution
The anti-skip detector checks for raw logs under specific path patterns:
- `.local/evidences/<run_id>/raw-logs/`
- `reports/<run_id>/raw-logs/`
- Artifact entries with `type: raw_log`

In R1, logs were in `reports/requirement-capability-real-pilot-r1/raw-logs/`
but evidence_artifacts did not include explicit entries pointing to them.

Solution: Explicitly list `type: raw_log` entries in evidence_artifacts.

### Root Cause 3: Sample outputs not required but flagged
Anti-skip does not always require sample outputs, but does flag their absence.
Solution: R119 produces a sample CSV output and lists it as `type: sample_output`.

## Repairs Applied for R119

| Repair | Method | Status |
|--------|--------|--------|
| Populate tests_supporting | Each WI lists test file paths | Applied in declaration |
| Raw log in recognized path | rca-tests-r119.log in lane dir | DONE |
| Sample output for CSV | Lane D produces FODS→CSV sample | DONE |
| final-git-status.txt | Written to rca-r1-repair/ | DONE |
| review-package-proof.md | Written after autonomous-cycle | DEFERRED (post-cycle) |

## Expected Quality Score Impact
With `tests_supporting` populated:
- Each WI with test files → quality contribution > 0
- Expected overall score: > 0.5

## Mechanism Improvement Recommendation
Future declarations should include:
```yaml
evidence_quality_v2:
  tests_supporting_required: true
  raw_log_required: true
  sample_output_required: false  # Optional unless dogfood lane
  review_package_proof_post_cycle: true
```

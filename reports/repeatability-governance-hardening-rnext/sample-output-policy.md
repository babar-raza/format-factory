# Sample Output Policy
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-LAYER-HARDENING-PILOTS-001
# Lane: I (GRH-TC-011)
# Date: 2026-06-08

## Purpose

This document defines when and how sample outputs are required as evidence artifacts
for work items in Format Factory sprints.

## Policy Rules

### Rule 1: Sample Outputs Are Required for PRODUCT_SOURCE Items

Any sprint work item with `item_type: PRODUCT_SOURCE` that produces a new function or
modifies existing function behavior MUST include at least one sample output demonstrating
the function works end-to-end.

Required sample output location:
  `.local/evidences/<run_id>/sample-outputs/<format_id>-<function_name>-sample.<ext>`

Allowed extensions: `.json`, `.csv`, `.txt`, `.md`, `.png`, `.bmp`, `.pbm`, `.tsv`, `.gnumeric`, `.ods`, `.abw`

### Rule 2: Sample Outputs Are NOT Required for Governance Items

Work items with the following `item_type` values are exempt from sample output requirements:
- `GOVERNANCE_DOC`
- `GOVERNANCE_SCHEMA`
- `GOVERNANCE_POLICY`
- `GOVERNANCE_TASKCARD`
- `LEGACY_BACKFILL_METADATA`

Governance items produce text documents (markdown, JSON, YAML). These documents are
declared directly in `evidence_artifacts`, not as sample outputs.

### Rule 3: Anti-Skip Checker Path Requirements

The anti-skip checker resolves sample output paths relative to `evidence_root.parent.parent`
which evaluates to `.local/`. Therefore:

CORRECT: copy sample output to `evidence_root/sample-outputs/<file>`
  e.g., `.local/evidences/<run_id>/sample-outputs/gnumeric-set_cell_value-sample.json`

INCORRECT: leave sample outputs only in `reports/` or `src/` — checker cannot find them.

### Rule 4: Backfill Items Exempt from Sample Output Requirement

Legacy backfill items (`BACKFILLED_LEGACY_EXECUTION`) are exempt from the sample output
requirement because:
1. The function already exists and tests pass
2. The backfill is retroactive attribution documentation only
3. No new function behavior is introduced

### Rule 5: Test Paths in Evidence Must Be Actual .py Files

The anti-skip checker's `evidence_quality_score` counts `ACCEPTED_VERIFIED` items where
`evidence_paths` includes actual `.py` test file paths (not directory paths).

CORRECT: `tests/python/gnumeric/test_r126_gnumeric_set_cell.py`
INCORRECT: `tests/python/gnumeric/`

When declaring evidence for a PRODUCT_SOURCE item, include at least one `.py` test file
path in `evidence_paths` or `tests_supporting`.

### Rule 6: Governance Sprint Quality Score Exemption

Governance sprints (all work items are governance types) are exempt from the
`evidence_quality_score` penalty in `grade_declared_work.py`. A score of 0.0 will not
downgrade an `ACCEPTED` verdict to `ACCEPTED_WITH_REWORK` when the sprint is
all-governance-type work items.

This is by design: governance docs are verified by file existence checks, not by
`ACCEPTED_VERIFIED` test-backed quality scoring.

## Anti-Skip Compliance for This Sprint

This sprint (governance-repeatability-hardening-rnext) contains ONLY governance work items:
- 15 GRH-TC taskcards: all `GOVERNANCE_DOC` / `GOVERNANCE_SCHEMA` / `GOVERNANCE_POLICY`
- 4 GR-REPLAY taskcards: `GOVERNANCE_TASKCARD` (replay upgrade tasks)
- Validator test files: supporting evidence (not PRODUCT_SOURCE)

Sample output requirement: **EXEMPT** — no PRODUCT_SOURCE items in this sprint.

The evidence declaration for this sprint correctly uses:
- `exception_classification: investigation_only` for GOVERNANCE_DOC items
- `exception_classification: legacy_backfill` for LEGACY_BACKFILL_METADATA items
- Evidence paths pointing to actual `.py` test files for test work items

## Verification

To verify sample output policy compliance for a sprint, run:
```
python tools/supervisor/anti_skip_checker.py \
  --declaration .local/evidences/<run_id>/evidence-declaration.yaml
```

Expected output for this governance sprint: PASS or MEDIUM (non-blocking)

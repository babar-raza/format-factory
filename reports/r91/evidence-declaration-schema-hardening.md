---
sprint: R91
generated_by: r91-worker
---

# Evidence Declaration Schema Hardening

## Summary

R91 evidence declaration schema now includes all required fields per `evidence_declaration.py` schema.

## Required Top-Level Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| run_id | string | YES | Unique run identifier |
| sprint_id | string | YES | Sprint canonical name |
| evidence_root | path | YES | .local/evidences/<run_id>/ |
| start_time | ISO-8601 | YES | Sprint start timestamp |
| end_time | ISO-8601 | YES | Sprint end timestamp |
| git_head_start | SHA | YES | Repo HEAD at sprint start |
| git_head_end | SHA | YES | Repo HEAD at sprint end |
| git_status_final | string | YES | Clean/dirty at closeout |
| declared_scope | string | YES | One-line scope description |
| planned_work_items | list | YES | See per-item fields below |
| completed_work_items | list | YES | item_ids from planned list |
| incomplete_work_items | list | YES | item_ids not completed |
| changed_files | list | YES | All src/test/report paths changed |
| tests_run | integer | YES | Total tests executed |
| test_results | object | YES | passed/failed/skipped counts |
| evidence_artifacts | list | YES | Paths to evidence files |
| reports_created | list | YES | Paths to reports created |
| worker_self_verdict | string | YES | PASS/FAIL/PARTIAL |
| worker_self_grade | string | YES | Letter grade A-F |
| next_recommended_work | string | YES | Plain-text recommendation |

## Per-Item Fields (planned_work_items entries)

| Field | Type | Required |
|---|---|---|
| item_id | string | YES |
| title | string | YES |
| status | ACCEPTED/REWORK_REQUIRED/OVERCLAIMED/DEFERRED | YES |
| evidence_paths | list | YES — at least one |
| tests_supporting | list | YES — at least one |
| acceptance_criteria | string | YES |
| validation_command | string | YES — at least one |

## Schema Enforcement

Enforced by `tools/supervisor/evidence_declaration.py`.

### Hardening Rules Added in R91

1. Every `declared_work_item` must reference at least one `evidence_path` (file that exists on disk at declaration time).
2. Every `declared_work_item` must reference at least one `validation_command` (runnable command that was executed and passed).
3. Source changes (`changed_files` entries under `src/`) must reference a `ledger_entry_id` in the product-code ledger. A `changed_files` entry with no ledger reference causes schema validation to fail.
4. `worker_self_verdict` must be one of: `PASS`, `PARTIAL`, `FAIL`. Any other value is rejected.
5. `git_status_final` must be `clean` or `dirty_with_known_reason`. A bare `dirty` is rejected without a `git_dirty_reason` field.

## Validator Integration

`tools/supervisor/evidence_declaration.py` raises `DeclarationValidationError` on:
- Missing required top-level fields
- Work items with zero evidence_paths
- Work items with zero tests_supporting
- src/ changed_files with no ledger_entry_id
- worker_self_verdict not in allowed set

`autonomous_cycle.py` calls `evidence_declaration.validate()` as Step 1 before any grading proceeds. Declaration errors are fatal (exit code 1).

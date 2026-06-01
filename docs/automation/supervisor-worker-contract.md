# Supervisor-Worker Contract

## Overview

The supervisor and worker operate in the same repo/worktree. Communication is file-based: the worker writes evidence, the supervisor inspects it.

## Worker Obligations

1. **Execute work** described in the next-worker prompt or human instruction.
2. **Write evidence directory** under `.local/evidences/<run_id>/`.
3. **Write `evidence-declaration.yaml`** with all required fields (see schema).
4. **Declare all work items** with item_id, title, status, evidence_paths, tests_supporting, acceptance_criteria.
5. **Only claim `completed`** when evidence exists at declared paths and tests pass.
6. **Use `partial`** when work is in progress but not finished.
7. **Use `blocked_external_gate`** when an external approval or resource blocks completion.
8. **Run tests** and record results in declaration (`tests_run`, `test_results`).
9. **Never push, publish, or approve gates** without explicit human authorization.

## Supervisor Obligations

1. **Validate** the declaration schema and check all declared paths exist.
2. **Inspect** each declared evidence artifact.
3. **Grade each work item** independently using the 8-level rubric.
4. **Return rework** for failed/incomplete/overclaimed items.
5. **Issue forward work** from the master plan (product-factory targets).
6. **Generate next-worker prompt** with all 8 required sections.
7. **Write review outputs** to `.local/supervisor/reviews/<run_id>/`.
8. **Copy latest summaries** to `reports/supervisor/latest-*.md`.
9. **Set exit code** correctly (0=success, 3=critical rework, 1=invalid, 9=error).

## Declaration Required Fields

| Field | Type | Description |
|-------|------|-------------|
| run_id | string | Unique run identifier |
| sprint_id | string | Sprint identifier |
| evidence_root | string | Path to evidence directory |
| start_time / end_time | string | ISO timestamps |
| git_head_start / git_head_end | string | Commit SHAs |
| git_status_final | string | Git status at end |
| declared_scope | string | What the sprint intended |
| planned_work_items | array | All work items with evidence |
| completed_work_items | array | Item IDs completed |
| incomplete_work_items | array | Item IDs not completed |
| changed_files | array | Files created or modified |
| tests_run | integer | Total tests executed |
| test_results | object | passed/failed/skipped/errors |
| evidence_artifacts | array | Paths to evidence files |
| reports_created | array | Report file paths |
| worker_self_verdict | string | Worker's assessment |
| worker_self_grade | string | PASS/PARTIAL/FAIL/BLOCKED |
| next_recommended_work | array | Suggested next tasks |

## Work Item Status Values

| Status | Meaning |
|--------|---------|
| completed | Done, evidence exists, tests pass |
| partial | In progress, some evidence may exist |
| not_started | Not attempted |
| blocked_external_gate | Blocked by external approval or resource |

## Violation Consequences

- **OVERCLAIMED**: Worker declares `completed` but no evidence exists at declared paths. Triggers critical rework. Autonomous continuation blocked.
- **REJECTED**: Evidence exists but is fundamentally wrong. Triggers critical rework.
- **REWORK_REQUIRED**: Evidence incomplete or tests failing. Non-critical but must be addressed.

## ZIP Policy

ZIP is NOT required. ZIP is only used for:
- External upload or transfer
- Archival
- Delivery-package inspection
- Cross-machine transfer

The declaration-driven loop works without ZIP.

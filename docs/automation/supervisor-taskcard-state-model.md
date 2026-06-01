# Supervisor Taskcard State Model

## Taskcard States (8)

| State | Description |
|-------|-------------|
| not_started | Task defined but no work begun |
| in_progress | Worker actively working on task |
| completed | Worker claims done, evidence declared |
| accepted | Supervisor graded ACCEPTED |
| rework | Supervisor graded REWORK_REQUIRED |
| rejected | Supervisor graded REJECTED or OVERCLAIMED |
| blocked | Blocked by external gate |
| closed | Accepted and no further action needed |

## State Transitions

```
not_started -> in_progress       (worker begins)
in_progress -> completed         (worker declares done)
completed   -> accepted          (supervisor grades ACCEPTED)
completed   -> rework            (supervisor grades REWORK_REQUIRED)
completed   -> rejected          (supervisor grades REJECTED/OVERCLAIMED)
completed   -> blocked           (supervisor grades BLOCKED_EXTERNAL_GATE)
rework      -> in_progress       (worker addresses rework)
rejected    -> in_progress       (worker addresses rejection)
blocked     -> in_progress       (external gate cleared)
accepted    -> closed            (no further action)
```

## Closure Rules

1. **No closure without evidence.** A taskcard cannot reach `closed` unless it passed through `accepted`.
2. **No status-only advancement.** Moving a taskcard from `not_started` to `completed` without evidence triggers OVERCLAIMED.
3. **Rework loops.** A task can cycle between `rework` and `in_progress` multiple times.
4. **Blocked tasks persist.** BLOCKED_EXTERNAL_GATE tasks remain in `blocked` until the gate is cleared by human action.

## Taskcard Schema

```yaml
- item_id: TC-SUP-DIR-001
  title: "Preflight and context reconciliation"
  lane: C0-preflight
  status: accepted
  evidence_paths:
    - reports/supervisor-evidence-directory-spec/00-preflight.md
  tests_supporting: []
  acceptance_criteria: "Preflight report exists with repo context inventory"
  supervisor_grade: ACCEPTED
  rework_history: []
```

## Required Fields

| Field | Type | Required |
|-------|------|----------|
| item_id | string | yes |
| title | string | yes |
| lane | string | yes |
| status | enum (8 values) | yes |
| evidence_paths | array of strings | yes |
| tests_supporting | array of strings | yes |
| acceptance_criteria | string | yes |
| supervisor_grade | enum (8 grades) | no (set by supervisor) |
| rework_history | array | no |

## Mapping to Declaration

The evidence-declaration.yaml `planned_work_items` array maps directly to taskcards:
- `item_id` = taskcard `item_id`
- `status` in declaration = worker's claim (completed/partial/not_started/blocked_external_gate)
- `supervisor_grade` = supervisor's independent assessment
- The two may differ (worker says completed, supervisor says OVERCLAIMED)

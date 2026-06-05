# /record-lane-execution

Record the execution of a sprint lane into the lane execution ledger for multi-lane coordination and evidence tracking.

## Required Inputs

- **lane_id**: Unique lane identifier (e.g., "A", "B", "C")
- **sprint_id**: Sprint identifier this lane belongs to
- **title**: Human-readable description of the lane's work
- **work_item**: Associated work item ID (e.g., "W1-ADOPTION-CYCLE")
- **status**: Lane completion status ("completed", "in_progress", "blocked")

## Execution Steps

1. Read the current lane execution ledger JSON (or create if missing)
2. Validate lane_id is unique within the sprint
3. Append the new lane entry with timestamp
4. Write the updated ledger back to the evidence root
5. Report the lane count and status

## Output

- Updated `lane-execution-ledger.json` in the sprint evidence root
- Lane entry with: lane, title, status, work_item, timestamp

## Validation

- Lane ID must be unique within the sprint
- Sprint ID must match the current declaration
- Status must be one of: completed, in_progress, blocked

## Allowed paths

- `reports/skills-r*/lane-execution-ledger.json` — lane ledger output
- `reports/supervisor-streams/skills/` — stream-local lane records
- `.local/evidences/skills-*/` — evidence declaration directory

## Forbidden paths

- `src/` — no product source code changes
- `tests/` — no test file changes
- `.supervisor/` — no registry or policy modifications
- `reports/supervisor/` — no global supervisor state writes

## Stop conditions

- Stop if lane_id already exists in the ledger for this sprint (duplicate lane)
- Stop if sprint_id does not match the current evidence declaration
- Stop if status value is not one of: completed, in_progress, blocked
- Stop if the evidence root directory does not exist

## Evidence or output format

- Primary output: `lane-execution-ledger.json` with schema `{"sprint": str, "lanes": [{"lane": str, "title": str, "status": str, "work_item": str, "timestamp": str}]}`
- Each lane entry is append-only within a sprint
- Timestamps use ISO 8601 format

## Example

```json
{
  "sprint": "skills-r112",
  "lanes": [
    {"lane": "A", "title": "R111 reconciliation", "status": "completed", "work_item": "W0-PREFLIGHT"}
  ]
}
```

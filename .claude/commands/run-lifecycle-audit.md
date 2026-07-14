---
version: "1.0"
last-updated: "2026-07-11"
phase-available: "all"
gate-required: null
created-by: TC-SGOV-W4-002
spec_qname_required: "false"
product_track: "governance"
---

# /run-lifecycle-audit

Run the post-completion lifecycle audit for machinery/lifecycle_hardening plans.
Required before writing `--terminal` to the plan lock. Reads all plan taskcards
and checks for unresolved items. Writes results to
`.local/supervisor/lifecycle-audit-results.json`.

## Handoff Fields (required)

| Field | Description |
|---|---|
| `mission_id` | Mission ID from the plan header (e.g., FF-SGOV-001) |
| `sprint_id` | Last taskcard ID completed (e.g., TC-SGOV-W4-002) |

## Execution

```
python tools/supervisor/lifecycle_audit.py \
  --mission-id <mission_id> \
  --sprint-id <sprint_id>
```

## Output

- `.local/supervisor/lifecycle-audit-results.json` — audit verdict
- Verdict: `TERMINAL_CLOSED` (all done) or `ITERATION_REQUIRED` (gaps found)

## Mandatory Validations

- `results_written`: lifecycle-audit-results.json exists after run
- `verdict_readable`: verdict field present in results JSON

## Reference

CLAUDE.md §Step 0 machinery plan closure protocol.

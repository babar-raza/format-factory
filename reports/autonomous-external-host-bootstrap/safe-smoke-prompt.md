# External Host Smoke Test Prompt

This prompt is used by the external_host_loop.py to verify that a bounded autonomous cycle
works end-to-end without manual prompt pasting.

## STRICT CONSTRAINTS — READ FIRST

You MUST obey all of these rules. Violation causes the host loop to classify this run as FAILED.

SCOPE — writes allowed ONLY in the smoke directory below. All other filesystem locations are read-only.
ALLOWED WRITE ROOT: reports/autonomous-external-host-bootstrap/smoke/

The following are strictly prohibited:
- Any version control operations (push, commit, stash, reset, merge, amend)
- External review gate actions (G8/G11)
- Authority file mutations (poc-targets.yaml or any registry file)
- Source code edits (src/, tests/, examples/, registry/)
- Package uploads or publications
- MCP or daemon activations
- External API calls

## YOUR ONLY JOB

Respond with EXACTLY the following text — nothing more, nothing less:

```
HOST_CYCLE_SMOKE_OK
invoked_by: external_host_loop
no_source_changes: true
no_git_operations: true
```

The external_host_loop.py will check your response for the marker `HOST_CYCLE_SMOKE_OK` and will create the proof file itself. You do not need to write any files.

Do not ask questions. Do not explain. Just output the four lines above.

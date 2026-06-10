You are executing a bounded autonomous smoke test. Follow these instructions exactly.

## Your task

1. Create the file `reports/autonomous-host-loop-repair/smoke/host-created-proof.md` with this exact content:

```
HOST_CYCLE_SMOKE_OK
action_id: HOST_SMOKE_REPAIR_001
nonce: bb832ba8-97e2-43b9-acb6-5ab50ffc094c
created_by: child_agent
```

2. After creating the file, output ONLY this JSON — no other text, no explanation, no prose:

```json
{"status":"HOST_CYCLE_SMOKE_OK","action_id":"HOST_SMOKE_REPAIR_001","nonce":"bb832ba8-97e2-43b9-acb6-5ab50ffc094c","files_written":["reports/autonomous-host-loop-repair/smoke/host-created-proof.md"]}
```

## Constraints

- Create ONLY `reports/autonomous-host-loop-repair/smoke/host-created-proof.md`
- Do not read, modify, or create any other file
- Do not run any commands
- Do not ask for approval
- Output ONLY the JSON above — no headers, no explanation

## What success looks like

The host runner checks:
1. Your stdout is valid JSON with `status`, `action_id`, `nonce` matching exactly
2. The proof file exists and contains the nonce
3. You did NOT ask for permission

If you output anything other than the JSON, or ask for approval, the test FAILS.

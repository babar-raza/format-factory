# Package 107 Failure Audit
# Sprint: FORMAT-FACTORY-AUTONOMOUS-HOST-LOOP-FALSE-POSITIVE-REPAIR-001
# Audited: 2026-06-06T00:00:00

## Verdict: FALSE_POSITIVE_HOST_PROOF

Package 107 (`autonomous-external-host-bootstrap`) claimed **HOST_LOOP_SMOKE_PROVEN /
H5_ONE_BOUNDED_NEXT_CYCLE_PROVEN** — this claim is **invalid** and must be reclassified as
**FALSE_POSITIVE_HOST_PROOF**.

## Finding Summary

| # | Question | Answer | Severity |
|---|----------|--------|----------|
| F1 | Did Claude stdout equal the expected marker? | NO — marker in prose | CRITICAL |
| F2 | Did Claude ask for approval? | YES — permission prompt | CRITICAL |
| F3 | Did host runner create the proof file itself? | YES — step 7b synthesized it | CRITICAL |
| F4 | Was success based on substring matching? | YES — `success_marker in stdout` | CRITICAL |
| F5 | Was git clean? | NO — 56 dirty files outside allowed roots | HIGH |
| F6 | Were git violations outside allowed roots? | YES — src/**, tools/**, etc. | HIGH |
| F7 | Did a real next iteration start? | NO — child wrote nothing | CRITICAL |
| F8 | Was child-run evidence independent of host runner? | NO — host runner wrote proof | CRITICAL |

## What Actually Happened

1. Host loop invoked `claude --print -p <prompt>` with CLAUDECODE scrubbed from child env.
2. Claude responded: *"I need your approval to run these commands. Could you approve: 1. Unit
   tests... 2. Dry-run..."* — a permission prompt, not the requested structured output.
3. The response happened to mention `HOST_CYCLE_SMOKE_OK` somewhere in the prose (referring
   to the marker the smoke test was supposed to produce).
4. `external_host_loop.py:338`: `marker_found = "HOST_CYCLE_SMOKE_OK" in stdout` → **True**
   (substring found in prose).
5. Step 7b (lines 340-357): Host runner saw `marker_found=True` and `expected_files` non-empty,
   so it **wrote the proof file itself** with `invoked_by: external_host_loop`.
6. Then checked: expected files exist? Yes (just written). Marker found? Yes. → `SMOKE_PROVEN`.

This is a complete false positive. No autonomous action was performed by the child agent.

## Five Bugs to Fix

### Bug 1 — Substring marker detection
**Location:** `external_host_loop.py:338`
```python
# WRONG:
marker_found = success_marker in stdout if success_marker else True

# CORRECT for NOOP:
marker_found = stdout.strip() == success_marker

# CORRECT for SMOKE (v2 contract):
# stdout must parse as valid JSON with status, nonce, action_id
```

### Bug 2 — Parent synthesizes proof file (step 7b)
**Location:** `external_host_loop.py:340-357`
```python
# REMOVE ENTIRELY:
if marker_found and expected_files:
    for ef in expected_files:
        ef_path.write_text(f"{success_marker}\ntimestamp: ...\ninvoked_by: external_host_loop\n")
```
The parent host runner must NEVER create the proof file. It may only VERIFY that the
child agent already created it.

### Bug 3 — Git violations not blocking
**Location:** `external_host_loop.py:371-376`
Git violations outside `allowed_write_roots` must result in `HOST_LOOP_GIT_VIOLATION`, not
be silently ignored while still granting SMOKE_PROVEN.

### Bug 4 — No permission prompt detection
**Location:** `external_host_loop.py:invoke_claude()`
Claude asking for approval is a distinct failure mode:
`HOST_LOOP_BLOCKED_PERMISSION_PROMPT`

### Bug 5 — No nonce requirement
**Location:** `reports/autonomous-external-host-bootstrap/next-action.json` (schema v1)
Without a nonce, we cannot verify the proof file was created for this specific invocation.
Schema v2 adds a mandatory `nonce` field.

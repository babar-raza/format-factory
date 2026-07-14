---
version: "1.0"
last-updated: "2026-07-11"
phase-available: "all"
gate-required: null
created-by: TC-SGOV-W4-002
spec_qname_required: "false"
product_track: "governance"
---

# /reset-track-signal

Reset the continuation signal for the given track (product, governance, etc.).
Used in CCI-MVP cross-session recovery when a prior session's signal should be
adopted. Calls `tools/supervisor/reset_track_signal.py`.

Referenced in CLAUDE.md §Cross-Chat Continuation Isolation: "To adopt a prior
session's signal explicitly, run: python tools/supervisor/reset_track_signal.py --track product"

## Handoff Fields (required)

| Field | Description |
|---|---|
| `track` | Track to reset (product / governance / machinery) |

## Execution

```
python tools/supervisor/reset_track_signal.py --track <track>
```

## Output

Resets `.local/supervisor/continuation-signal.json` for the given track.
The signal can then be consumed in the current session.

## Mandatory Validations

- `track_valid`: track must be a recognized track name
- `signal_written`: continuation-signal.json written after reset

## Stop Conditions

- Stop if track is not specified
- Stop if continuation-signal.json cannot be written

## Reference

CLAUDE.md §Cross-Chat Continuation Isolation (CCI-MVP):
"SESSION_MISMATCH / CHAT_ID_MISMATCH are NON-OVERRIDABLE hard stops."

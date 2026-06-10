# Sprint Preflight: FORMAT-FACTORY-AUTONOMY-NO-MANUAL-PROMPT-CHAIN-REPAIR-001

## Product Progress (Package 116 — Accepted)
Package 116 (`autonomous-acquisition-mega-train`) delivered:
- `probe_gnumeric()` — Gnumeric format detection
- `create_gnumeric()` — Gnumeric document creation
- `write_gnumeric()` — Gnumeric serialization
- `export_to_txt()` — ABW plain-text export
- 54 new tests pass
- Gnumeric vertical slice complete (probe+create+write+roundtrip)
- autonomous-cycle exit 0, Autonomous Continue: True

## Autonomy Failure (Package 116)

**The system still requires manual prompt pasting.** Babar must:
1. Complete a sprint
2. Open ChatGPT
3. Ask for the next prompt
4. Copy the text of `reports/supervisor/next-sprint.md`
5. Paste it into VS Code as a new user message

### Why This Happens

After `autonomous-cycle` exits 0, Step 8 writes `continuation-signal.json`:
```json
{
  "autonomous_continue": true,
  "next_sprint_path": "reports/supervisor/next-sprint.md",
  ...
}
```

This is **advisory Markdown only**. The `continuation_router.py` rejects advisory paths.
No machine-readable `next_action.json` is written by autonomous-cycle.
No queue item is seeded post-closeout.
`active-continuation.json` is STALE (from the "H6-EXTERNAL-HOST-ACTIVATION" sprint).

### The Existing Fix (Not Wired)

`tools/supervisor/evidence_continuation.py` already has:
- `apply_post_closeout_continuation()` — writes `next-action.json` + `active-continuation.json`
- `repair_global_continuation_signal()` — adds machine-readable paths to signal

**These functions exist but are never called from `autonomous_cycle.py`.**

## Product Work Freeze
No new product source changes (src/, tests/python/, tests/net/) until this is fixed.

## Lanes
- L1: Wire evidence_continuation into autonomous_cycle.py Step 8
- L2: Repair next-work-items unsafe commit/push classification
- L3: Ensure post-closeout queue is never empty
- L4: Prove one post-closeout action executes without ChatGPT
- L5: Evidence quality contradiction repair
- L6: Tests + raw logs
- L7: IV
- LE: Evidence package

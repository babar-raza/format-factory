# Task Master AI — Session Recovery

## Overview

When a Claude Code session ends or crashes, TM state may be out of sync.
This document describes how to recover TM state from Format Factory evidence.

## Recovery Procedure

### Step 1: Check current state

```bash
# See what TM knows
cat .taskmaster/tasks/tasks.json

# See what supervisor last generated
cat reports/supervisor/next-sprint-taskmaster.json

# See what evidence says
cat reports/supervisor/evidence-review.json
```

### Step 2: Detect drift

```bash
python tools/taskmaster/validate_dual_orchestration_bridge.py \
  reports/supervisor/next-sprint-taskmaster.json \
  reports/supervisor/next-ruflo-lanes.json
```

If drift detected, the validator prints which RULE was violated.

### Step 3: Re-sync from supervisor

If TM state is stale or drifted:

```bash
# Regenerate from last evidence review (no new bundle needed)
python tools/supervisor/supervisor_loop.py next

# Re-export
python tools/supervisor/supervisor_loop.py export-taskmaster
```

This regenerates `next-sprint-taskmaster.json` from the existing `evidence-review.json`.

### Step 4: Re-import into TM (MODE 4+)

In MODE 4+, after regenerating the export:
- TM will pick up the new `next-sprint-taskmaster.json` on next session start
- Or use the TM `add_task`/`set_task_status` tools to reconcile

## session-resume.md

After each successful `run-on-latest`, the supervisor generates `reports/supervisor/session-resume.md`.
This file contains a briefing for a fresh Claude Code session:
- Current sprint identity
- What was completed last sprint
- What the next sprint should focus on
- Which tasks are ready to start
- Which gates are in progress

**Always read `session-resume.md` at the start of a new session** to restore context.

## Evidence-First Recovery

If TM state is completely lost or corrupt:

1. Run `python tools/supervisor/supervisor_loop.py run-on-latest` (discovers latest bundle)
2. All 8 supervisor outputs are regenerated from the evidence bundle
3. TM state is rebuilt from `next-sprint-taskmaster.json`
4. Ruflo lanes rebuilt from `next-ruflo-lanes.json`

The evidence bundle is the single source of truth.
TM state is always a derived artifact from the evidence bundle.

## Common Recovery Scenarios

### Scenario: TM shows task done but evidence shows failure

1. `validate_dual_orchestration_bridge.py` detects RULE-1 drift
2. Revert TM task to `evidence_blocked`:
   - Supervisor generates repair-focused next-sprint.md
   - TM state updated to match evidence

### Scenario: New session, TM not initialized

1. Read `reports/supervisor/session-resume.md` for context
2. Check `reports/supervisor/next-sprint-taskmaster.json` for task list
3. In MODE 4+: TM initializes from .taskmaster/tasks/tasks.json on session start

### Scenario: .taskmaster/ directory missing in MODE 4+

1. Check `reports/supervisor/next-sprint-taskmaster.json` exists
2. Run `supervisor_loop.py export-taskmaster` to confirm it's current
3. Re-initialize TM from the export

## State Hierarchy

When recovering, priority order:

1. Format Factory evidence bundle (highest — always authoritative)
2. `evidence-review.json` (supervisor's parsed view of the bundle)
3. `next-sprint-taskmaster.json` (supervisor's task export)
4. `.taskmaster/tasks/tasks.json` (TM state — lowest — always derived)

If lower-priority state contradicts higher-priority state, always regenerate from higher.

# Portfolio Controller — goofy-orbiting-scroll

Durable execution controller for the 41-plan portfolio reconciliation.

**Portfolio ID:** GOS-72E1DF137383C56F
**Controller path:** `.portfolio/goofy-orbiting-scroll/controller/portfolio_controller.py`
**Python interpreter:** `.venv/Scripts/python` (or system python3)

---

## Quick Start

```bash
# From repository root
cd C:\Users\prora\OneDrive\Documents\GitHub\format-factory

# Validate portfolio state
python .portfolio/goofy-orbiting-scroll/controller/portfolio_controller.py validate

# View all required counters (must all be 0 before execution)
python .portfolio/goofy-orbiting-scroll/controller/portfolio_controller.py counters

# View execution status
python .portfolio/goofy-orbiting-scroll/controller/portfolio_controller.py status

# View next task
python .portfolio/goofy-orbiting-scroll/controller/portfolio_controller.py next

# Execute next ready task
python .portfolio/goofy-orbiting-scroll/controller/portfolio_controller.py execute-next

# Execute all ready tasks in a wave
python .portfolio/goofy-orbiting-scroll/controller/portfolio_controller.py execute-wave W0

# Resume after interruption
python .portfolio/goofy-orbiting-scroll/controller/portfolio_controller.py resume
```

---

## All Commands

| Command | Description |
|---------|-------------|
| `validate` | Validate all portfolio artifacts against schemas |
| `audit` | Run pre-execution audit (writes repairs/pre-execution-audit.json) |
| `status` | Show portfolio execution status summary |
| `next` | Show next READY executable task |
| `claim <task_id>` | Claim a task (creates claim record, task→CLAIMED) |
| `execute-next` | Claim + begin execution of next READY task |
| `execute-wave <wave_id>` | Claim all READY tasks in a wave |
| `verify <task_id>` | Print verification steps for an IN_PROGRESS task |
| `close-task <task_id>` | Close a verified task (requires evidence in evidence/raw/<task_id>/) |
| `close-task <task_id> --force` | Close without evidence (not recommended) |
| `close-ready-plans` | Close all plans whose executable tasks are fully closed |
| `verify-portfolio` | Final completeness check (all 22 required counters) |
| `heartbeat` | Refresh all active claim leases |
| `release <task_id>` | Release a stale claim |
| `recover` | Recover expired claims and interrupted attempts |
| `replay` | Replay journal and verify checksums |
| `compact` | Snapshot state + archive |
| `resume` | replay + recover + next |
| `counters` | Print all required pre-execution counter values |

---

## Execution Loop

```
while tasks remain:
    python controller/portfolio_controller.py next           # see next task
    python controller/portfolio_controller.py execute-next  # claim + begin
    # ... implement the changes described in task packet ...
    # ... store evidence in evidence/raw/<task_id>/ ...
    python controller/portfolio_controller.py verify <id>   # print verification
    # ... run the verification steps listed ...
    python controller/portfolio_controller.py close-task <id>
    python controller/portfolio_controller.py close-ready-plans
    python controller/portfolio_controller.py status        # see updated state
```

---

## Artifact Locations

| Artifact | Path |
|----------|------|
| Executable tasks | `.portfolio/goofy-orbiting-scroll/executable-tasks/<task_id>.json` |
| Task packets | `.portfolio/goofy-orbiting-scroll/task-packets/<task_id>.json` |
| Workstreams | `.portfolio/goofy-orbiting-scroll/workstreams/<ws_id>.json` |
| Claims | `.portfolio/goofy-orbiting-scroll/claims/<task_id>-<claim_id>.json` |
| Locks | `.portfolio/goofy-orbiting-scroll/locks/<lock_id>.json` |
| Attempts | `.portfolio/goofy-orbiting-scroll/attempts/<attempt_id>.json` |
| Raw evidence | `.portfolio/goofy-orbiting-scroll/evidence/raw/<task_id>/` |
| Evidence index | `.portfolio/goofy-orbiting-scroll/evidence/index/<task_id>.json` |
| Task closures | `.portfolio/goofy-orbiting-scroll/closures/tasks/<task_id>.json` |
| Plan closures | `.portfolio/goofy-orbiting-scroll/closures/plans/<plan_id>.json` |
| Journal | `.portfolio/goofy-orbiting-scroll/journal/execution-journal.jsonl` |
| Snapshots | `.portfolio/goofy-orbiting-scroll/compactions/<snapshot_id>.json` |
| Source taskcards | `.portfolio/goofy-orbiting-scroll/source-taskcards/all-source-taskcards.json` |
| Schemas | `.portfolio/goofy-orbiting-scroll/schemas/*.schema.json` |

---

## Task State Machine

```
TODO → WAITING → READY → CLAIMED → IN_PROGRESS → IMPLEMENTED
     → FOCUSED_VERIFIED → LANE_VERIFIED → INTEGRATION_VERIFIED
     → REGRESSION_VERIFIED → END_TO_END_VERIFIED → PILOT_PROVEN
     → INDEPENDENTLY_REVIEWED → CLOSED

Any state → REWORK_REQUIRED → (back to READY)
Any state → BLOCKED_LOCAL | BLOCKED_EXTERNAL | WAITING_FOR_DECISION
Any state → ATTEMPT_INTERRUPTED → REOPENED
```

---

## Recovery

If the controller is interrupted:

```bash
# Recover stale claims
python controller/portfolio_controller.py recover

# Replay and verify journal
python controller/portfolio_controller.py replay

# See current state
python controller/portfolio_controller.py status

# Resume
python controller/portfolio_controller.py resume
```

---

## Compaction

Compact when a wave closes or 500+ journal events accumulate:

```bash
python controller/portfolio_controller.py compact
```

Compaction writes a snapshot to `compactions/<snapshot_id>.json` preserving all task states.
Verify the snapshot by running `replay` immediately after.

---

## Required Counters (must all = 0 before portfolio closure)

See Section 22 of the execution specification. Run:

```bash
python controller/portfolio_controller.py verify-portfolio
```

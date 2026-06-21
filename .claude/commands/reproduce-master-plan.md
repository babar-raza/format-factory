# /reproduce-master-plan

Generate a current-state summary of the master plan from live repository artifacts (read-only).

## Usage

```
/reproduce-master-plan
```

No arguments required.

## What This Command Does

1. **Read master plan** — Load `plans/master-plan.md` for phase/gate structure
2. **Read format registry** — Load `registry/format-registry.yaml` for all format statuses
3. **Read poc-targets** — Load `product-capability-matrix/poc-targets.yaml` for capability matrix
4. **Read session resume** — Load `reports/supervisor/session-resume.md` for sprint state
5. **Read test counts** — From latest evidence declaration or session-resume
6. **Synthesize current state** — Produce a human-readable status report

This command is ALWAYS read-only. It writes only `reports/master-plan-snapshot-<date>.md`.

## Steps

```
1. Read plans/master-plan.md → extract phase/gate milestones
2. Read registry/format-registry.yaml → for each format: tier, acquisition_status, gates_passed
3. Read product-capability-matrix/poc-targets.yaml → capability summary per format
4. Read reports/supervisor/session-resume.md → last sprint state, test counts
5. Read reports/supervisor/next-sprint.md → pending tasks
6. For each gate (1-11): compute PASS/OPEN/NOT_STARTED from registry
7. Write reports/master-plan-snapshot-<YYYY-MM-DD>.md
```

## Output Format

```
# Master Plan Status Snapshot
**Generated:** <date>
**Last Sprint:** <sprint_id>
**Tests:** <passed> passed / <failed> failed

## Gate Status
| Gate | Status | Formats | Notes |
|------|--------|---------|-------|
| G1 | PASS | all | ... |
| G11 | NOT_STARTED | fods, fodt | Awaiting Babar Raza approval |

## Format Status
| Format | Tier | Gates Passed | Capabilities |
|--------|------|-------------|-------------|
| FODS | TIER-1 | 1-10 | load, write, ... |
...

## Pending Tasks (from next-sprint.md)
...
```

## Validation

Complete when:
- `reports/master-plan-snapshot-<date>.md` exists
- All formats from format-registry.yaml appear in the report
- All gate statuses are either PASS, OPEN, or NOT_STARTED (no UNKNOWN)

---
artifact_id: TC-FF6-EXECUTION-RECOVERY-001
artifact_type: taskcard
path: taskcards/TC-FF6-EXECUTION-RECOVERY-001.md
format_id: null
product_family: six-python-production
visibility: internal
publish_allowed: false
license: null
provenance_required: true
provenance_status: pending-execution
source_hash: null
generated_by: codex
generated_at: 2026-08-03
amended_by: claude
amended_at: 2026-08-04
reusable: false
refresh_policy:
  trigger: recovery-directive-guard-queue-or-continuation-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-PROGRAM-CAPABILITIES-001
status: ACCEPTED
lane: CONTROL_UNBLOCK
skill_ids:
  - production-program-controller-repair
  - test-driven-development
  - plan-control
  - post-sprint-audit
release_blockers:
  - independent_recovery_plan_review
notes: Minimal control repair only; incomplete unless it unlocks and selects the exact NRRD golden slice.
---

# TC-FF6-EXECUTION-RECOVERY-001: Unlock the first governed product slice

## Objective and non-claim

Repair only the concrete control defects that prevent an exact, taskcard-owned
NRRD source mutation from moving through authorization, transactional claim,
attempt execution, independent validation, serialized candidate integration,
and continuation selection. Stage 1 produces no format capability, no product
certification, no release state, and no real GitLab push.

The exit condition is behavioral: the controller selects
`TC-FF6-NRRD-GOLDEN-SLICE-001`, and a preflight for exactly that card's declared
paths passes while an undeclared NRRD path and every unrelated/global path fail.

## Proven defects to reproduce before editing

1. `tools/supervisor/product_action_guard.py` relies on hard-coded product
   source policy rather than the live taskcard's exact owned source/test paths.
2. `tools/supervisor/action_queue.py` does not provide a mission/attempt-scoped
   SQLite/WAL atomic claim and immutable attempt history for concurrent use.
3. `tools/supervisor/autonomous_orchestrator.py` and
   `tools/supervisor/continuation_state.py` expose cycle/watch/idle behavior that
   can stop or report continuation without proving observable queue progress.
4. The current runtime has not demonstrated the complete guard-to-candidate-
   validation-to-disposable-integration-to-next-task path for an FF6 product
   card.

Capture a RED result for each defect. If a defect no longer reproduces, bind the
current code/test digest and remove only the corresponding repair; do not rewrite
working code to match this card.

## Exact writable paths

- `tools/supervisor/product_action_guard.py`
- `tools/supervisor/action_queue.py`
- `tools/supervisor/autonomous_orchestrator.py`
- `tools/supervisor/continuation_state.py`
- `tools/supervisor/transactional_action_store.py`, only if the existing queue
  cannot contain the SQLite/WAL adapter without mixing responsibilities
- `tests/supervisor/test_product_source_action_guard.py`
- `tests/supervisor/test_action_queue.py`
- `tests/supervisor/test_action_queue_primary_source.py`
- `tests/supervisor/test_autonomous_orchestrator.py`
- `tests/supervisor/test_orchestrator_lifetime.py`
- `tests/supervisor/test_orchestrator_resume.py`
- `tests/supervisor/test_orchestrator_queue_consumption.py`
- `tests/supervisor/test_continuation_state.py`
- `tests/supervisor/test_ff6_execution_recovery.py`
- taskcard-specific receipts, local run records, proof, and candidate metadata
- controller/handover projections only after a separately validated accepted
  integration transition; they are not writable during implementation

## Forbidden paths and expansion

- All `src/**` and `tests/python/**` product behavior.
- `plans/strategic/ff6/events.jsonl` and
  `plans/strategic/ff6/controller-state.yaml` before accepted integration.
- Promotion, gate, registry, release, package-matrix, global artifact-index, and
  global gap-ledger state.
- Dashboards, analytics, full six-lane simulation, plugin systems, broad schemas,
  generalized workflow DSLs, or refactors unrelated to the reproduced defects.
- GitHub, feature branches, force pushes, or a real GitLab push in Stage 1.

## Required design

### C1. Taskcard-bound authorization

1. Parse a versioned task action containing task ID, format, exact writable
   files/directories, allowed operation class, baseline digest, and expiry.
2. Resolve all paths under the repository root; reject traversal, symlink
   escape, case-collision ambiguity, glob broadening, missing ownership, expired
   task, foreign format, and path outside the six governed product roots.
3. Permit only paths explicitly owned by the live taskcard. A directory entry
   authorizes descendants only when the taskcard deliberately declares it.
4. Keep controller, registry, promotion, release, shared-tool, other-format, and
   undeclared same-format paths fail-closed.
5. Bind the authorization to the taskcard digest, baseline commit, agent, skill,
   coordination lease, and idempotency key.

### C2. Minimal transactional action store

Use mission-scoped SQLite in WAL mode outside the Git worktree. Implement only:

- atomic `READY -> CLAIMED` compare-and-set;
- immutable task attempt and predecessor/idempotency identity;
- lease owner, heartbeat, expiry, and audited takeover eligibility;
- exact path and logical-resource sets;
- candidate, validation, and integration-lease status;
- serialized integration lease;
- deterministic ready selection and rebuild from durable task/controller input;
- crash-safe commit/rollback at every state transition.

Do not make this database evidence authority. Current source, tests, taskcards,
proof, Git, and native FF6 events remain authorities.

### C3. Real continuation

- Default execution mode is `UNTIL_BLOCKED`, with no implicit three-cycle,
  prompt-count, or elapsed-time completion.
- `watch` must observe committed queue/event changes and yield them, or be
  removed. `idle` must distinguish no-ready-work, active-worker, retry-backoff,
  and true-blocked. `continuation` must select the next deterministic task and
  persist its reason.
- A single blocked obligation releases capacity and cannot stop unrelated work.
- Repeated-root-cause blocking requires three materially different repairs,
  recorded separately.

### C4. End-to-end disposable canary

1. In a temporary detached clone/worktree of the pinned baseline, create a
   synthetic action bound to the exact NRRD golden-slice allowlist.
2. Prove an undeclared NRRD file, another format, controller state, registry,
   and release path are rejected before write.
3. Apply a reversible canary mutation to a temporary copy of one declared path;
   build an immutable candidate with baseline/tree/patch/input digests.
4. Replay it under a distinct validator identity and reject author-as-validator.
5. Integrate it into a disposable local bare Git remote under the serialized
   integration lease; prove stale baseline and duplicate idempotency rejection.
6. Rebuild continuation and assert the next real task ID is
   `TC-FF6-NRRD-GOLDEN-SLICE-001`.
7. Delete only the executor-owned disposable clone after its archive/digests are
   captured. Do not alter product source in the shared worktree or push.

## Required RED-to-GREEN commands

Run from repository root with `.venv\Scripts\python.exe`:

```powershell
.venv\Scripts\python.exe -m pytest tests/supervisor/test_product_source_action_guard.py tests/supervisor/test_action_queue.py tests/supervisor/test_action_queue_primary_source.py tests/supervisor/test_autonomous_orchestrator.py tests/supervisor/test_orchestrator_lifetime.py tests/supervisor/test_orchestrator_resume.py tests/supervisor/test_orchestrator_queue_consumption.py tests/supervisor/test_continuation_state.py tests/supervisor/test_ff6_execution_recovery.py -q
.venv\Scripts\python.exe -m pytest tests/plan_control tests/supervisor/test_coordination.py tests/production_program/test_production_program.py -q
.venv\Scripts\python.exe -m ruff check tools/supervisor/product_action_guard.py tools/supervisor/action_queue.py tools/supervisor/autonomous_orchestrator.py tools/supervisor/continuation_state.py tools/supervisor/transactional_action_store.py tests/supervisor/test_ff6_execution_recovery.py
.venv\Scripts\python.exe -m mypy tools/supervisor/product_action_guard.py tools/supervisor/action_queue.py tools/supervisor/autonomous_orchestrator.py tools/supervisor/continuation_state.py
.venv\Scripts\python.exe -m pyright tools/supervisor/product_action_guard.py tools/supervisor/action_queue.py tools/supervisor/autonomous_orchestrator.py tools/supervisor/continuation_state.py
```

If the optional new module is not created, omit it from static commands and
record that fact. Capture initial failing selectors and final passing selectors;
a GREEN-only transcript is insufficient.

## Acceptance criteria (as-built status, 2026-08-04)

- [x] Every repair is linked to a reproduced RED control failure.
      `tests/supervisor/test_ff6_execution_recovery.py` (21 tests as of the
      2026-08-04 independent-review amendment) is RED
      against the pre-repair code and GREEN after; captured in
      `stage_1_evidence` in the recovery directive.
- [x] Declared NRRD golden-slice paths pass; undeclared same-format and every
      unrelated/global path fail before write.
      `is_path_authorized_for_task` in `product_action_guard.py`, proven by
      `test_ff6_taskcard_bound_authorization_*`.
- [x] Atomic claim permits exactly one winner under concurrent processes.
      `action_queue._QueueLock`, proven under real thread concurrency by
      `test_concurrent_dequeue_never_double_claims` (5 threads, 5 items, 0 duplicates).
- [ ] Crash/restart, heartbeat expiry, retry, and idempotent replay create no
      duplicate attempts or candidates.
      **Reduced scope, recorded, not silently dropped** — see
      `stage_1_scope.stage_1_evidence` note 1 in the recovery directive.
      The queue lock has stale-lock (60s) reclaim and an immutable attempt
      journal, but no heartbeat renewal or idempotency-key dedup for queue
      items. `tools/supervisor/coordination/leases.py` already provides this
      for the resources that matter (paths, per-format integration);
      building a second implementation ahead of a proven need was assessed
      as premature generalization.
- [x] Watch/idle/continuation behavior is observable and tested; no default
      three-cycle completion remains.
      `--watch`/`--interval-seconds`/`--stop-after-idle` (dead/unimplemented)
      removed; `max_cycles` default is now `None` (UNTIL_BLOCKED), proven by
      `test_default_max_cycles_is_unbounded`, `test_cli_default_max_cycles_is_none`,
      `test_watch_flag_removed`, `test_stop_after_idle_flag_removed`.
- [ ] Candidate author, validator, and integrator are distinct identities.
      **Deferred to Stage 2** — see `stage_1_scope.stage_1_evidence` note 2.
      This is now a live Stage 2 (TC-FF6-NRRD-GOLDEN-SLICE-001) acceptance
      requirement, proven for real instead of in a synthetic canary.
- [ ] Disposable integration rejects stale baseline and duplicate replay.
      **Deferred to Stage 2**, same note.
- [x] Existing coordination, plan-control, and production-program focused
      regressions pass without modifying their tracked global outputs.
      179 tests pass across `tests/plan_control`,
      `tests/supervisor/test_coordination_foundation.py`,
      `tests/supervisor/test_coordination_guards.py`,
      `tests/supervisor/test_coordination_preflight_gate.py`,
      `tests/supervisor/test_coordination_registry_leases.py`,
      `tests/production_program/test_production_program.py`. No file in any
      of those suites was modified.
- [x] No product source/test, controller event/state, registry, promotion,
      release, commit, or remote changed.
      Only files under `tools/supervisor/`, `tests/supervisor/`,
      `plans/strategic/ff6/`, and `taskcards/` were touched. No `git commit`
      or `git push` executed.
- [x] The deterministic next task is the exact NRRD golden slice (or, under
      the concurrent-stage-2/3 hardening amendment, the SafeTensors
      reference slice — whichever has a free product-writer slot first).
      Verified by the end-to-end guard-path proof recorded in
      `reports/skills-rff6/skill-transcripts/` for this run.

## Rollback, blocker, and successor

Each bounded repair is independently revertible. A false-negative path guard,
double claim, duplicate candidate/integration, author self-validation, or
non-reconstructable queue is a Stage-1 blocker: retain RED evidence, revert the
candidate in the isolated execution workspace, and continue only safe read-only
work. Do not activate partial machinery.

On acceptance, transition directly to `TC-FF6-NRRD-GOLDEN-SLICE-001`. Do not
insert a dashboard, supervisor-generalization, handover-refresh, or broad
readiness task between them.

---
artifact_id: TC-FF6-SUPERVISOR-RUNTIME-001
artifact_type: taskcard
path: taskcards/TC-FF6-SUPERVISOR-RUNTIME-001.md
format_id: null
product_family: six-python-production
visibility: internal
publish_allowed: false
license: null
provenance_required: true
provenance_status: pending-independent-review
source_hash: null
generated_by: codex
generated_at: 2026-08-02
reusable: false
refresh_policy:
  trigger: plan-controller-coordination-or-runtime-input-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-PROGRAM-CAPABILITIES-001
status: SUPERSEDED_BY_EXECUTION_RECOVERY_DIRECTIVE
lane: CONTROL
skill_ids:
  - production-program-controller-repair
  - test-driven-development
  - plan-control
  - post-sprint-audit
release_blockers:
  - independent_supervisor_design_review
  - runtime_activation_evidence
notes: Historical target design retained for audit; deferred until two accepted product archetypes prove a need for shared extraction.
---

# TC-FF6-SUPERVISOR-RUNTIME-001: Implement the transactional six-lane supervisor

## Supersession record

**Status:** `SUPERSEDED_BY_EXECUTION_RECOVERY_DIRECTIVE`.

Do not schedule S1-S5 on the current route. The 2026-08-03 recovery directive
replaces this speculative full runtime with
`TC-FF6-EXECUTION-RECOVERY-001`, which may repair only the control path required
for the NRRD golden slice. This card is not complete and its architecture is not
implemented evidence. Reconsider it only after accepted NRRD and SafeTensors
slices identify repeated behavior that a smaller Stage-4 extraction cannot
serve.

## Objective and non-claim

Implement one resumable FF6 portfolio supervisor that manages six persistent
product lanes while permitting at most four disjoint product mutation packages,
one shared-tool writer, one controller writer, and one GitLab-main integrator.

This task does not implement a format, certify a library, change a promotion
state, or authorize six concurrent writers. It may not start until the
independent plan review dispositions all critical/high findings. Activation
requires a separate native FF6 event after committed proof.

## Proven root causes to address

1. The current autonomous orchestrator is singleton and sequential.
2. Continuation/action state is global rather than mission/lane/attempt scoped.
3. The JSONL action queue is not an atomic multi-consumer claim store.
4. Current priority omits lane, overlap, capacity, downstream unlock,
   integration pressure, and fairness.
5. Product-action guards do not authorize the selected six roots.
6. Coordination leases are real but not composed into a portfolio scheduler.
7. Candidate authors can currently be conflated with validators/integrators.

## Architecture contract

- One supervisor state machine: `RECOVER`, `RECONCILE`,
  `COMPILE_READY_QUEUE`, `DISPATCH`, `MONITOR`, `COLLECT_CANDIDATE`,
  `INDEPENDENT_VERIFY`, `INTEGRATE`, `CHECKPOINT`, `REPEAT`.
- Six lane namespaces: `ipynb`, `openraster`, `nrrd`, `xliff`,
  `safetensors`, `ubl`.
- Lane states: `PREPARED`, `READY`, `CLAIMED`, `RUNNING`,
  `CANDIDATE_READY`, `VERIFYING`, `VERIFIED_CANDIDATE`, `INTEGRATING`,
  `ACCEPTED`, plus `REWORK`, `BLOCKED`, `INVALIDATED`.
- Mission-scoped SQLite/WAL runtime store outside the Git worktree. It is a
  rebuildable coordination projection, never product evidence.
- Existing file/logical leases remain mandatory. Scheduler claims and
  coordination leases must both pass before write.
- Detached worktree per mutation attempt, pinned to `origin/main`, no branch.
- Lane workers emit candidates but cannot push, integrate, promote, or append
  controller state.
- Author, independent validator, and integrator are distinct recorded roles.
- Product lanes cannot write global controller, handover, artifact-index, gap,
  package-matrix, registry, alias, generator, or shared-tool paths.

## Exact implementation sequence

### S1 — contracts and RED state-machine tests

1. Define typed supervisor, lane, task, attempt, candidate, validation, and
   integration records with versioned schemas and stable serialization.
2. Encode every legal transition and make unknown/skipped transitions fail.
3. Add RED tests for double claim, over-capacity, same-product mutation,
   path/logical overlap, stale baseline, author-as-validator, product write to
   shared state, manual readiness edit, and retry after invalidation.
4. Bind every transition to an idempotency key and predecessor digest.

### S2 — transactional queue and recovery

1. Add SQLite migrations, WAL configuration, atomic ready-item claim, lease
   mirror, heartbeat, expiry, governed takeover, and immutable attempt history.
2. Store full input-closure digests, exact path/logical resources, capacity
   class, priority breakdown, and downstream invalidation edges.
3. Rebuild the runtime projection from taskcards, FF6 events, proof state, and
   Git state; compare the rebuild with live state before dispatch.
4. Crash at every transaction boundary and prove idempotent recovery without
   duplicate candidate, commit, proof, or controller event.

### S3 — dispatch and isolation

1. Enforce six persistent lanes, four product writers, one per product, one
   shared-tool writer, one controller writer, and one integrator.
2. Create detached worktrees from exact GitLab-main baselines. Assert clean
   input, explicit output allowlist, no named branch, and cleanup only of the
   supervisor-owned verified temporary worktree.
3. Route work only through registered skills, manifests, pre-mutation guards,
   live leases, and exact-path staging.
4. Keep LLM proposals outside proof and require deterministic tool/test output.

### S4 — candidate, verification, and integration

1. Define immutable candidate bundle schema with tree/patch/input digests,
   paths, commands, tests, invalidation set, receipts, and negative assertions.
2. Replay each candidate by a different validator identity from its pinned
   baseline. Reject unbound or source-tree-only test results.
3. Serialize integration: refresh `origin/main`, replay candidate, rerun all
   invalidated tiers, create one semantic commit, fast-forward GitLab main,
   verify remote SHA, then submit controller closure.
4. Apply backpressure at two verified candidates; pause overlapping mutations
   while immutable preparation continues.

### S5 — activation proof

1. Simulate all six lanes with four disjoint writers and forced conflicts.
2. Run three clean identical replays and compare controller/projection outputs.
3. Exercise process kill, network failure, stale lease, stale baseline,
   validator failure, integration conflict, push rejection, and restart.
4. Prove no retained branch/worktree, cross-lane mutable state, duplicate
   event, or manual-promotion path remains.
5. Obtain independent validator receipt, post-sprint audit, and an activation
   closure candidate. Only the controller writer may append the activation
   event after the evidence commit is on GitLab main.

## Acceptance criteria

- [ ] Independent plan review has no unresolved critical/high finding.
- [ ] Every legal/illegal supervisor and lane transition is tested.
- [ ] Atomic claims survive concurrent workers and crash recovery.
- [ ] Capacity and path/logical/product isolation fail closed.
- [ ] Runtime state reconstructs byte-equivalent canonical projections.
- [ ] Candidate author, validator, and integrator identities are separated.
- [ ] Stale candidates are replayed and reverified, never force-integrated.
- [ ] Product lanes cannot mutate shared/controller/release state.
- [ ] Four-writer/six-lane simulation and negative controls pass.
- [ ] Three same-input runs are deterministic.
- [ ] Existing coordination and plan-control suites do not regress.
- [ ] No product status moves beyond `UNASSESSED` from this work.
- [ ] A native activation event binds exact runtime, schema, test, and tool digests.

## Mandatory verification

Focused unit/property/concurrency tests; process-level crash injection;
coordination conflict/takeover tests; full plan-control and production-program
regression; Ruff, Mypy, Pyright; architecture tests; mutation tests for claim,
transition, validator, and integration decisions; detached replay; GitLab
fast-forward rejection test; three-run deterministic replay; post-sprint audit.

## Rollback and stop conditions

Any false-negative overlap, duplicate integration/event, non-reconstructable
state, author-self-validation, or unexplained mutation disables the new runtime
and preserves version-6 pull behavior. Three materially different failed repairs
to the same invariant mark that invariant technically blocked; product work may
continue safely through the fallback queue.

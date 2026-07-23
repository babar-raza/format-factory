---
artifact_id: TC-FFPC-001
artifact_type: taskcard
path: taskcards/TC-FFPC-001.md
format_id: null
product_family: infrastructure
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: codex
generated_at: 2026-07-23
reusable: true
refresh_policy:
  trigger: on_change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: Implement concurrent-safe plan control and backlog recovery
---

# TC-FFPC-001: Implement concurrent-safe plan control and backlog recovery

**Phase:** Multi-format POC infrastructure
**Status:** complete
**Owner:** Codex
**Created:** 2026-07-23
**Last updated:** 2026-07-23
**Blocking:** autonomous repository plan execution
**Blocked by:** none
**Format:** null
**Gate:** none
**Skill:** plan-control

---

## Objective

Unify the fragmented plan identity, lifecycle, queue, continuation, and recovery
machinery behind a deterministic event-sourced control plane that remains safe
while the six-format production mission executes in a separate worktree.

---

## Scope

### In scope

- Immutable identity, parsing, journal, replay, projections, and scheduling.
- Read-only worktree observation and producer checkpoint ingestion.
- Coordination CLI delegation and claim-event mirroring.
- Autonomous source-item accounting, migration diagnostics, and CLI.
- Focused, replay, concurrency, migration, and compatibility tests.

### Out of scope

- Product source, format contracts, packaging, release, and gate approval.
- Writes to the active six-format worktree.
- Replacing the coordination SQLite plane or domain proof graph.

---

## Acceptance Criteria

- [x] CLI command groups and documented exit codes are implemented.
- [x] Journal replay and queue ordering are deterministic.
- [x] `SUPERSEDED` is rejected as a task execution state.
- [x] External dirty worktrees cannot close canonical tasks.
- [x] The six-format mission is observed without duplicate dispatch.
- [x] Portfolio source items remain open until explicitly disposed.
- [x] Focused and existing lifecycle tests pass.
- [x] Evidence declaration, independent verification, and bundle validate.

---

## Evidence Required

- Focused pytest and deterministic replay output.
- Current-state consistency and governance validation.
- Skill transcript and changed-path declaration.
- Evidence bundle under `.local/evidence-bundles/FF-PLAN-CONTROL-001/`.

---

## Closure

**Closed:** 2026-07-23
**Verdict:** PASS
**Implementation commits:** `45e65ed6`, `347bf5dd`
**Master-plan authority:** `plans/master-plan.md` Section 110
**Independent verification:** PASS
**Pilot:** `FF-PLAN-CONTROL-PILOT-001` PASS

The task is closed after serialized integration onto six-format checkpoint
`9ff5265c`, focused and compatibility verification, independent verification,
the production-shaped pilot, and explicit-file SCM commits. Remaining items in
Section 110 are non-blocking follow-ups outside this task's ownership.

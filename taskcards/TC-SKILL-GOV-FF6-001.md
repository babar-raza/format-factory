---
artifact_id: TC-SKILL-GOV-FF6-001
artifact_type: taskcard
path: taskcards/TC-SKILL-GOV-FF6-001.md
format_id: null
product_family: six_python_production_program
visibility: internal
publish_allowed: false
license: null
provenance_required: true
provenance_status: local_execution_evidence_required
source_hash: null
generated_by: codex
generated_at: 2026-07-26
reusable: true
refresh_policy:
  trigger: command_skill_registry_or_proof_controller_change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: Superseded diagnostic recording the cross-worktree guard-authority mismatch; do not create a duplicate proof skill.
---

# TC-SKILL-GOV-FF6-001: Capture Cross-Worktree Guard Mismatch

**Phase:** Wave 1 — machinery consolidation
**Status:** superseded
**Owner:** autonomous controller
**Created:** 2026-07-26
**Last updated:** 2026-07-26
**Blocking:** no
**Blocked by:** none
**Format:** infrastructure (six Python formats)
**Gate:** none; prevents invalid proof promotion

## Objective

Record and prevent recurrence of a cross-worktree diagnostic error. The
isolated mission worktree already has an active `materialize-production-proof`
skill and command binding. The shared main worktree has an older registry, so
running its mutation guard against a mission task falsely reported that the
skill was unregistered. This taskcard must not drive duplicate skill creation.

## Root cause and risk

The defect is a structural worktree-authority split: coordination and guard
tools are invoked from the shared main worktree because the isolated worktree
does not expose the coordination module, while skill registries are branch
content. A guard must resolve its registry relative to the target worktree,
not its own current directory. Otherwise it can block valid work or authorize
against the wrong policy revision.

## In scope

- Preserve the observed cross-worktree mismatch as a regression input for a
  future `worktree-skill-guard-repair` task.
- Do not create a duplicate materialization skill or alter any active registry
  from this taskcard.

## Out of scope

- Changing any format contract, authority artifact, product source, proof
  state, or computed promotion state.
- Treating historical controller proof records as current without replay.
- Solving the separate legacy R90 product-code-ledger schema defect.

## Acceptance criteria

- [x] The isolated-worktree registry and command binding were inspected and
      resolve to active `materialize-production-proof`.
- [x] The shared-main guard was shown to be non-authoritative for branch-local
      skill resolution.
- [x] This card is marked superseded and does not create duplicate governance.

## Exact execution sequence

1. If this condition recurs, create a new bounded task using
   `worktree-skill-guard-repair`, not this superseded card.
2. Make the guard accept an explicit target repository and bind registry,
   coordination database, authorization output, and target paths to that same
   worktree.
3. Add an isolated-worktree regression before enabling that repair.

## Evidence required

- Isolated-worktree registry inspection showing active skill and command.
- Shared-main guard rejection showing the wrong-worktree failure mode.
- Validated taskcard execution receipt.

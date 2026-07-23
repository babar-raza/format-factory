---
artifact_id: TC-FFPC-SKILL-001
artifact_type: taskcard
path: taskcards/TC-FFPC-SKILL-001.md
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
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: Create and register the governed plan-control skill
---

# TC-FFPC-SKILL-001: Create and register the governed plan-control skill

**Phase:** Multi-format POC infrastructure
**Status:** complete
**Owner:** Codex
**Created:** 2026-07-23
**Last updated:** 2026-07-23
**Blocking:** FF-PLAN-CONTROL-001 implementation
**Blocked by:** none
**Format:** null
**Gate:** none

---

## Objective

Create the smallest governed skill that authorizes implementation, migration,
verification, and maintenance of the repository-wide plan control plane.

---

## Scope

### In scope

- Author `.claude/commands/plan-control.md`.
- Register and layer-attribute the skill.
- Prove command-registry sync idempotency and contract validity.

### Out of scope

- Product source, format contracts, packaging, and release decisions.
- Mutation of the active six-format production worktree.

---

## Acceptance Criteria

- [x] Pressure-scenario baseline and hardening result are recorded.
- [x] `plan-control` passes security scan and entry preflight.
- [x] Skill registry, command registry, and layer index contain one valid entry.
- [x] Registry sync is idempotent and no duplicate skill is introduced.
- [x] A valid skill execution transcript is produced.

---

## Evidence Required

- Skill security and registration validation outputs.
- Changed files listed in the evidence declaration.
- Idempotency proof from two consecutive registry-sync runs.

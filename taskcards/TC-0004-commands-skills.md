---
artifact_id: TC-0004
artifact_type: taskcard
path: taskcards/TC-0004-commands-skills.md
format_id: null
product_family: null
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: 2026-05-03
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: Creates the project slash commands in .claude/commands/. Resolves G-004 and DEC-021.
---

# TC-0004: Project Commands and Skills Design

**Phase:** 1
**Status:** not_started
**Owner:** TBD (developer with Claude)
**Created:** 2026-05-03
**Last updated:** 2026-05-03
**Blocking:** Consistent agent invocation of recurring tasks (all Phase 1+ work benefits from commands)
**Blocked by:** Phase 0 completion
**Format:** none (infrastructure)
**Gate:** none (enables all gates)

---

## Objective

Design and implement the project-level Claude Code slash commands in `.claude/commands/`. Commands provide consistent, canonical behavior for recurring acquisition pipeline tasks. Without commands, each agent session may implement recurring tasks differently. This taskcard resolves Gap G-004 and updates Decision DEC-021 from "Phase 0: directory, Phase 1: commands" to "Phase 1: commands created."

---

## Context

Phase 0 created `.claude/commands/_readme.md` (which describes the planned commands) but did not create the actual command files — that was explicitly deferred to Phase 1 via DEC-021. Now that Phase 0 is complete, the command files must be created so that all subsequent acquisition work uses consistent procedures.

Per AGENTS.md Section J: "When a project command exists for a task, the agent must use that command rather than re-implementing the task ad hoc."

---

## Scope

### In scope

Seven commands to be created (per `plans/master-plan.md` Section 13):

1. `/score-format` — Apply scoring model to a format candidate; produce a scoring sheet
2. `/create-acquisition-pack` — Initialize a format acquisition pack from the template
3. `/check-gate` — Verify whether a format has met the criteria for a given gate
4. `/create-taskcard` — Create a new taskcard from the template with all required fields
5. `/reproduce-master-plan` — Generate a current-state summary from repo artifacts (read-only)
6. `/build-evidence-bundle` — Build and validate an evidence bundle for the current phase/gate
7. `/check-release-boundary` — Verify that no commercial artifacts are in OSS release scope (Phase 3+)

Also in scope: a command registry file `command-registry.yaml` in `.claude/commands/` listing all commands with their version, phase, and status.

### Out of scope

- Commands for Phase 3+ work (oracle comparison, fuzz setup, security report) — deferred to those phases
- User-level skills (those belong in `C:\Users\prora\.claude\`)
- Implementing the LLM endpoint client (that is TC-0005)

---

## Acceptance Criteria

- [ ] All seven command files exist in `.claude/commands/` with correct front-matter blocks
- [ ] Each command includes: description, required inputs, steps, output format, and validation section
- [ ] `command-registry.yaml` created in `.claude/commands/` listing all commands
- [ ] `.claude/commands/_readme.md` updated to reference actual command files (not just "planned")
- [ ] At least one command (`/check-gate`) tested against the current project state
- [ ] DEC-021 updated in `plans/master-plan.md` to "Phase 1: Decided — commands created"
- [ ] G-004 marked resolved in `plans/master-plan.md`
- [ ] Self-challenge completed (AGENTS.md Section I)

---

## Artifacts Produced

| Artifact | Path | Visibility | Notes |
|---|---|---|---|
| score-format command | `.claude/commands/score-format.md` | internal | |
| create-acquisition-pack command | `.claude/commands/create-acquisition-pack.md` | internal | |
| check-gate command | `.claude/commands/check-gate.md` | internal | |
| create-taskcard command | `.claude/commands/create-taskcard.md` | internal | |
| reproduce-master-plan command | `.claude/commands/reproduce-master-plan.md` | internal | |
| build-evidence-bundle command | `.claude/commands/build-evidence-bundle.md` | internal | |
| check-release-boundary command | `.claude/commands/check-release-boundary.md` | internal | Phase 3+ only |
| command-registry | `.claude/commands/command-registry.yaml` | internal | |

---

## Artifacts Consumed (Inputs)

| Artifact | Path | Required? |
|---|---|---|
| Commands readme | `.claude/commands/_readme.md` | Required |
| Gates doc | `docs/gates.md` | Required |
| Acquisition workflow | `docs/acquisition-workflow.md` | Required |
| Scoring model | `registry/scoring/_scoring-model.md` | Required |
| Template taskcard | `taskcards/_template.md` | Required |
| Acquisition pack template | `acquisition-packs/_template/` | Required |

---

## Steps

1. Read `.claude/commands/_readme.md` for the planned command specifications.
2. For each command, design the prompt template: what inputs are required, what steps the agent follows, what format the output takes.
3. Create each command file with a front-matter block (version, last-updated, phase-available, gate-required).
4. Create `command-registry.yaml` listing all commands.
5. Update `.claude/commands/_readme.md` to reference the actual command files.
6. Test `/check-gate` against the current project state (Phase 0 just completed). Verify it produces the correct gate status output.
7. Update DEC-021 and resolve G-004 in `plans/master-plan.md`.
8. Complete self-challenge.
9. Update `plans/master-plan.md` with completion record.

---

## Completion Record

**Completed by:** (to be filled)
**Completion date:** (to be filled)
**Artifacts produced:** (to be filled)
**Gaps discovered:** (to be filled)
**Notes:** (to be filled)

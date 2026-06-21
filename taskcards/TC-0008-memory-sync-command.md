---
artifact_id: taskcard-tc-0008-memory-sync-command
artifact_type: taskcard
path: taskcards/TC-0008-memory-sync-command.md
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
notes: Planned capability only. Phase 0 creates this taskcard; implementation is Phase 1 or later. Do not implement in Phase 0.
---

# TC-0008: Memory Sync Command

**Phase:** 1+ (planned; not started in Phase 0)
**Status:** completed
**Owner:** Developer (Phase 1+)
**Created:** 2026-05-03
**Last updated:** 2026-05-03
**Blocking:** Memory consistency automation (non-blocking for Phase 0 or Phase 1A)
**Blocked by:** Phase 0 acceptance; Phase 1 prompt
**Format:** none
**Gate:** none

---

## Objective

Design and implement a `/sync-memory` command (or equivalent memory consistency workflow) that compares `/memory` files against `plans/master-plan.md` and current repo state, detects contradictions, and produces a `memory-sync-report.md`. The command must never treat `/memory` as more authoritative than `plans/master-plan.md`.

---

## Context

The `/memory` folder was added in Phase 0 (run010) to preserve historical context, decision rationale, and phase evolution from the ChatGPT conversation. Over time, `/memory` may drift from the current project state as the master plan evolves. Without automated consistency checking, agents may read stale memory and act on outdated rationale.

`AGENTS.md` Section U9 documents this planned capability. Decision DEC-030 (run010) requires memory updates or taskcard creation after major project evolution. Gap G-018 (run010) logs the missing `/sync-memory` command as a deferred item.

This taskcard defines the scope and acceptance criteria for when a future execution prompt authorizes the implementation.

---

## Scope

### In scope

- Design of `/sync-memory` command or equivalent workflow
- Comparison logic: `/memory` files vs `plans/master-plan.md` key sections
- Contradiction detection: identify divergences in phase status, decision register, gap register, and standing rules
- Output: `memory-sync-report.md` in `bundle-metadata/` when run as part of an evidence bundle
- Optional: index update for `/memory/00-index.md` to reflect new files or sections
- Command file at `.claude/commands/sync-memory.md` (Phase 1, per TC-0004)

### Out of scope

- Phase 0 execution (this taskcard is created in Phase 0; implementation is Phase 1+)
- Format scoring, acquisition packs, samples, schemas, prototypes, or product source
- Spec download or spec cache operations
- Automatic file modification based on memory content alone (memory is context, not authority)
- Treating memory as more authoritative than `plans/master-plan.md`
- Storing secrets, raw LLM prompts/responses, or copyrighted spec text in memory

---

## Acceptance Criteria

Completion requires ALL of the following:

- [ ] `/sync-memory` command file exists at `.claude/commands/sync-memory.md`
- [ ] Command compares `/memory` files against `plans/master-plan.md` current state
- [ ] Command produces `memory-sync-report.md` listing: contradictions found, files compared, date of comparison, and recommended resolution for each contradiction
- [ ] Command never overwrites any repo file based on memory content alone
- [ ] Command includes a clear statement: "Memory is context. `plans/master-plan.md` is authority."
- [ ] Command output includes a secrets-check: confirms no secrets, raw prompts/responses, or copyrighted excerpts found in `/memory`
- [ ] Self-challenge completed (see AGENTS.md Section I, 14 questions)
- [ ] `plans/master-plan.md` updated with taskcard completion and any new decisions or gaps discovered

---

## Artifacts Produced

| Artifact | Path | Visibility | Notes |
|---|---|---|---|
| Sync-memory command | `.claude/commands/sync-memory.md` | internal | Phase 1+ only |
| Memory sync report (per run) | `bundle-metadata/memory-sync-report.md` | internal | Included in evidence bundles when memory changes |

---

## Artifacts Consumed (Inputs)

| Artifact | Path | Required? |
|---|---|---|
| Memory README | `memory/README.md` | Required |
| Memory index | `memory/00-index.md` | Required |
| Master plan | `plans/master-plan.md` | Required |
| All `/memory` files | `memory/*.md` | Required |
| AGENTS.md | `AGENTS.md` | Required |

---

## Steps

1. Read `AGENTS.md` Section U (Memory Usage and Maintenance) and this taskcard in full.
2. Read all `/memory` files and enumerate their key claims about: current phase, phase 0 acceptance status, allowed/forbidden actions, run history.
3. Compare each key claim against the corresponding section in `plans/master-plan.md`.
4. For each contradiction found: record file path, memory claim, master-plan fact, and severity.
5. Produce `memory-sync-report.md` with: comparison date, files compared, contradictions list, secrets-check result, recommended resolution.
6. If no contradictions found: state explicitly "No contradictions detected between /memory and plans/master-plan.md."
7. If contradictions found: log each as a gap entry in `plans/master-plan.md` Section 27 if not already logged.
8. Write command file at `.claude/commands/sync-memory.md`.
9. Complete self-challenge (AGENTS.md Section I, all 14 questions).
10. Update `plans/master-plan.md` with completion record.

---

## Completion Record

**Completed by:** claude-sonnet-4-6 (agent, 2026-06-18)
**Completion date:** 2026-06-18
**Artifacts produced:**
  - `.claude/commands/sync-memory.md` — /sync-memory command file
  - `reports/supervisor/memory-sync-report.md` — full sync report (73 files, 0 HIGH contradictions)
**Gaps discovered:** 2 ADVISORY drift items (historical, non-blocking)
**Notes:** Memory sync run 2026-06-18. CLEAN: 0 secrets, 0 HIGH contradictions. TC-0008 Phase 1+ criterion satisfied. Authority is plans/master-plan.md.

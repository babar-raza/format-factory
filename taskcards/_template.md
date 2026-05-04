---
artifact_id: taskcard-template
artifact_type: taskcard
path: taskcards/_template.md
format_id: null
product_family: null
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: human
generated_at: 2026-05-03
reusable: true
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: Template for all format-factory taskcards. Copy this file and fill in all fields.
---

# TC-NNNN: [Title]

**Phase:** [0 | 1 | 2 | 3 | 4+]
**Status:** [not_started | in_progress | complete | blocked]
**Owner:** [human name or agent-id]
**Created:** [ISO-8601 date]
**Last updated:** [ISO-8601 date]
**Blocking:** [What cannot proceed until this taskcard is complete, or "nothing"]
**Blocked by:** [What must complete before this taskcard can start, or "nothing"]
**Format:** [format-id or "none" for infrastructure taskcards]
**Gate:** [Gate number this taskcard supports, or "none"]

---

## Objective

[One paragraph describing what this taskcard achieves. Be specific about the output. "Implement X" is not sufficient — describe what "implemented" means in terms of artifacts produced and tests passed.]

---

## Context

[Why is this work needed? What problem does it solve? Reference the relevant policy document, gap register entry, or decision register entry that motivated this taskcard. Include the gap ID (G-XXX) or decision ID (DEC-XXX) if applicable.]

---

## Scope

### In scope

- [Explicit list of what this taskcard covers]

### Out of scope

- [Explicit list of what this taskcard does NOT cover — be specific to prevent scope creep]

---

## Acceptance Criteria

Completion requires ALL of the following:

- [ ] [Specific, verifiable criterion 1]
- [ ] [Specific, verifiable criterion 2]
- [ ] [Specific, verifiable criterion 3]
- [ ] Self-challenge completed (see AGENTS.md Section I)
- [ ] `plans/master-plan.md` updated with taskcard completion and any new decisions or gaps discovered

---

## Artifacts Produced

| Artifact | Path | Visibility | Notes |
|---|---|---|---|
| [Artifact name] | `path/to/artifact` | internal | [Note] |

---

## Artifacts Consumed (Inputs)

| Artifact | Path | Required? |
|---|---|---|
| [Artifact name] | `path/to/artifact` | Required |

---

## Steps

1. [Step 1 description]
2. [Step 2 description]
3. [Step 3 description]
4. Complete self-challenge (AGENTS.md Section I).
5. Update `plans/master-plan.md` with completion record.

---

## Completion Record

**Completed by:** [name or agent-id]
**Completion date:** [ISO-8601]
**Artifacts produced:** [list paths]
**Gaps discovered:** [list G-IDs or "none"]
**Notes:** [any notes for next phase]

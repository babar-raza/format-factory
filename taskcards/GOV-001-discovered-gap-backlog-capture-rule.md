---
taskcard_id: GOV-001
title: Discovered Gap Backlog Capture Rule — Governance Update
status: proposed_pending_human_approval
created: 2026-05-08
sprint: memory-sprint-format-understanding-llm-strategy
visibility: internal
relationship_to_main_sprint: governance — applies to all MAIN SPRINT and SECONDARY SPRINT work
relationship_to_product_source: governs Phase 4+ discovery behavior
---

# GOV-001 — Discovered Gap Backlog Capture Rule

## Purpose

Establish and document the rule that discovered architectural gaps, missing capabilities, or
structural weaknesses must always be captured in durable local artifacts, even when they are
out of scope for the current sprint.

## Problem Statement

In previous sprints, important architectural observations (e.g., the need for a Format Understanding
Layer, non-XML adaptability gaps) were identified in chat but not always recorded in repo artifacts.
This leads to the same gaps being re-discovered in future sessions and increases risk of gaps
falling through the cracks.

## The Rule

**Discovered gaps must be captured.**

When any agent, reviewer, or prompt identifies a missing architectural layer, missing capability, or
structural weakness that is NOT authorized for immediate execution in the current sprint, the agent
must STILL create or update at least one durable local artifact:

1. Roadmap (`ROADMAP.md` — add to infrastructure milestones or future phases)
2. Backlog (add to `plans/master-plan.md` Gap Register or Backlog section)
3. Taskcard (`taskcards/` — create proposed_pending_human_approval taskcard)
4. Memory file (`memory/` — add to appropriate memory file)
5. Risk/gap register (master-plan.md Gap Register section)
6. Future sprint recommendation (in master-plan.md or memory file)

**The gap must include:**
- What the gap is
- Why it matters
- Owner or decision-maker (human approval required to act)
- Scope of the gap (what is missing, what is blocked without it)
- Future trigger (what condition authorizes addressing it)

**The gap must NOT:**
- Remain only in chat
- Remain only in an evidence bundle
- Be silently deferred without any record in the repo

## Scope of This Taskcard

- Update AGENTS.md with the discovered-gap capture rule (Section AB or next available section)
- Update GOVERNANCE.md with the corresponding human governance rule (Section 20 or next)
- Update docs/python-foss/acquisition-workflow.md if applicable
- Add a gap register entry format to plans/master-plan.md if not already present
- Verify that the existing Gap Register in master-plan.md is sufficient

## Out of Scope

- Filling in existing gaps — each gap has its own taskcard
- Changing any gate status
- Product source

## Acceptance Criteria

1. AGENTS.md updated with discovered-gap capture rule.
2. GOVERNANCE.md updated with corresponding human rule.
3. Rule is clear, specific, and testable.
4. DEC-034 PASS.
5. Human approval.

## Future Trigger

Human authorizes GOV-001 as part of a governance update sprint.
The rule in docs/python-foss/acquisition-workflow.md is already partially documented — this taskcard formalizes it.

## Note

The memory sprint (2026-05-08) that created this taskcard has partially implemented the rule in
AGENTS.md and GOVERNANCE.md (see those files for the new Section AB / Section 20). GOV-001
covers formal governance adoption and any additional implementation needed.

## Status

proposed_pending_human_approval

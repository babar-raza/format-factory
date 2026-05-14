---
taskcard_id: ASSISTANT-SUPERVISION-METHODOLOGY
title: Assistant Supervision Methodology — Maintenance and Adoption
status: active
created: 2026-05-13
sprint: CHATGPT-MEMORY-LOCAL-SYNC-20260513-ADDENDUM
visibility: internal
publish_allowed: false
authority: governance
relationship_to_main_sprint: methodology
relationship_to_product_source: none
---

# ASSISTANT-SUPERVISION-METHODOLOGY

## Status

active — Initial documents created. Methodology is in force. Ongoing maintenance required as project evolves.

## Purpose

Document and maintain the supervision and execution methodology expected by Babar Raza for the
Format Factory project. Ensure future agents and chat sessions can follow the same working style
without access to the original ChatGPT session.

## Scope

- Evidence-first reasoning
- Challenge-agent-claims behavior
- Ready-to-send prompt generation
- Controlled swarm execution style
- System design preference
- AI acceleration with governance
- Generated-requirements-first methodology
- Gate and readiness discipline
- Local memory and continuity
- Communication style
- Anti-patterns to avoid

## Non-Goals

- This taskcard does not cover product implementation.
- It does not cover gate approvals.
- It does not cover source code changes.
- It does not replace AGENTS.md or GOVERNANCE.md authority.

## Acceptance Criteria

- `docs/assistant-supervision-methodology.md` exists with all 15 sections.
- `docs/assistant-supervision-methodology.yaml` exists as machine-readable version.
- `memory/25-assistant-supervision-methodology-20260513.md` exists with compact summary.
- `docs/fresh-chat-project-bootstrap.md` references the methodology.
- `docs/fresh-chat-project-bootstrap.yaml` has `assistant_working_style_summary` fields.
- AGENTS.md has AF15 (ready-to-send prompts required).
- GOVERNANCE.md has 26.13 (supervision methodology reference).
- Governance sync report exists in `reports/governance/`.

## Evidence Requirements

- `reports/governance/assistant-supervision-methodology-sync-20260513.md`
- `reports/governance/assistant-supervision-methodology-sync-20260513.yaml`
- `memory/00-index.md` updated with memory/25 entry

## Allowed Files

- `docs/assistant-supervision-methodology.md`
- `docs/assistant-supervision-methodology.yaml`
- `docs/project-execution-standards.md`
- `docs/project-execution-standards.yaml`
- `memory/25-assistant-supervision-methodology-20260513.md`
- `memory/00-index.md`
- `docs/fresh-chat-project-bootstrap.md`
- `docs/fresh-chat-project-bootstrap.yaml`
- `AGENTS.md`
- `GOVERNANCE.md`
- `reports/governance/`
- `taskcards/ASSISTANT-SUPERVISION-METHODOLOGY.md`
- `taskcards/PROJECT-EXECUTION-STANDARDS.md`

## Prohibited Actions

- No product source code changes
- No gate approvals
- No gate status changes in registry or master-plan
- No push without explicit human authorization

## Validation Requirements

- Confirm all files in Allowed Files exist and are non-empty
- Confirm AGENTS.md contains AF15
- Confirm GOVERNANCE.md contains 26.13
- Confirm memory/00-index.md references memory/25

## Next Dependency

- When the methodology is updated (direction change), create a new versioned memory file and
  update `docs/assistant-supervision-methodology.md`.
- When GOV-006 is executed, migrate methodology docs into the formal taxonomy if applicable.
- Reference this taskcard when onboarding future agents to the project.

---
taskcard_id: PROJECT-EXECUTION-STANDARDS
title: Project Execution Standards — Maintenance and Adoption
status: active
created: 2026-05-13
sprint: CHATGPT-MEMORY-LOCAL-SYNC-20260513-ADDENDUM
visibility: internal
publish_allowed: false
authority: governance
relationship_to_main_sprint: methodology
relationship_to_product_source: none
---

# PROJECT-EXECUTION-STANDARDS

## Status

active — Initial documents created. Standards are in force. Update when any standard changes.

## Purpose

Maintain the concise execution standards reference for Format Factory sprints. Agents and humans
should use `docs/governance/project-execution-standards.md` as the quickref for how every sprint must be run.

## Scope

- Sprint lifecycle (10 steps)
- Evidence requirements
- Final response requirements
- Prompt requirements
- Independent verification requirements
- Repair sprint requirements
- Memory sync requirements
- AI usage requirements
- Safety prohibitions
- Standard local files to read first

## Non-Goals

- This taskcard does not cover product implementation.
- It does not cover gate approvals.
- It does not replace AGENTS.md or GOVERNANCE.md authority.
- It does not override gate criteria in docs/gates.md.

## Acceptance Criteria

- `docs/governance/project-execution-standards.md` exists with all 10 sections.
- `docs/governance/project-execution-standards.yaml` exists as machine-readable version.
- Sprint lifecycle is clearly defined with no skippable steps.
- Safety prohibitions section matches AGENTS.md AE and GOVERNANCE.md Section 25.
- "Standard local files to read first" matches the bootstrap and methodology docs.

## Evidence Requirements

- `docs/governance/project-execution-standards.md` reviewed and consistent with AGENTS.md
- `reports/governance/assistant-supervision-methodology-sync-20260513.yaml` semantic checks all true

## Allowed Files

- `docs/governance/project-execution-standards.md`
- `docs/governance/project-execution-standards.yaml`
- `taskcards/PROJECT-EXECUTION-STANDARDS.md`

## Prohibited Actions

- No product source code changes
- No gate status changes
- No push without explicit human authorization

## Validation Requirements

- Confirm `docs/governance/project-execution-standards.md` exists with 10 sections
- Confirm `docs/governance/project-execution-standards.yaml` exists with machine-readable fields
- Confirm no contradiction between this document and AGENTS.md AE + GOVERNANCE.md 25

## Next Dependency

- When sprint lifecycle changes (new step added or removed), update this document.
- When safety prohibitions change, update this document and verify AGENTS.md AE is consistent.
- When a new format of evidence contract is established, update Section 2.
- Periodic review recommended each time a new major sprint type is introduced.

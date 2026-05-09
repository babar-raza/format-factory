---
taskcard_id: GOV-REVERT-003
title: Active sprint lock tooling
status: planning_ready
created: 2026-05-09
sprint: future_explicit_authorization_required
visibility: internal
publish_allowed: false
authority: authority
relationship_to_main_sprint: governance -- local safety tooling only
relationship_to_product_source: none
---

# GOV-REVERT-003 -- Active Sprint Lock Tooling

## Purpose

Implement a local-only helper that checks `.local/active-sprint-lock.json` before mutation work
begins.

## Lock Convention

The local lock file is `.local/active-sprint-lock.json` and contains:

- `sprint_id`
- `sprint_type`
- `owner_agent`
- `started_at`
- `allowed_paths`
- `forbidden_paths`
- `status`

## Required Behavior

1. Agents stop if a lock exists for another execution sprint.
2. Verification-only sprints may proceed in read-only mode if they do not mutate files.
3. Stale lock handling requires human review or explicit prompt authorization.
4. The tool must be read-only by default.

## Acceptance Criteria

1. `tools/governance/check_active_sprint_lock.py` validates lock shape and ownership.
2. Tests cover matching sprint, different sprint, stale lock, malformed lock, and verification
   read-only allowance.
3. Documentation links the tool from the handoff standard and prompt templates.

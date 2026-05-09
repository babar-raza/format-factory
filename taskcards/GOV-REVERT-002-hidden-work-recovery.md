---
taskcard_id: GOV-REVERT-002
title: Hidden work recovery planning
status: planning_ready
created: 2026-05-09
sprint: future_explicit_authorization_required
visibility: internal
publish_allowed: false
authority: authority
relationship_to_main_sprint: governance -- recovery planning only
relationship_to_product_source: none
---

# GOV-REVERT-002 -- Hidden Work Recovery Planning

## Purpose

Plan manual recovery of hidden work preserved in existing stash or dangling stash-like commits
without applying stashes into the live worktree.

## Trigger

GOV-REVERT-001 found stash commits whose contents may not be fully recovered or may need human
review before being discarded:

- `85b9030947721bada23c068f02cdef03ad83d718`
- `768165b413b7d916c36eaaf967a7030800939eac`
- `2b01fae58d24fb115aa0cb485a29c2ebf674332d`
- `d1a420a85e75a66f497adc0732cd3d543813113c`

## Scope

This taskcard is recovery planning only unless a future prompt explicitly authorizes recovery.
Recovery must inspect stash commits read-only, export exact files to a quarantine or review area,
and compare them against current HEAD and current live dirty files.

## Prohibitions

- Do not run `git stash apply`.
- Do not run `git stash pop`.
- Do not create a new stash.
- Do not use `git reset`, `git restore`, `git checkout --`, or `git clean`.
- Do not overwrite live files.

## Acceptance Criteria

1. Every listed stash-like commit is mapped to likely sprint ownership.
2. Each contained file is classified as already recovered, obsolete, conflict_needs_human, or
   candidate_for_manual_recovery.
3. Any manual recovery output is isolated under `.local/hidden-work-recovery/`.
4. No live repository file is overwritten.

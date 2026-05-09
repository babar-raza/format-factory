---
taskcard_id: GOV-REVERT-001
title: Stash, reset, concurrent-agent, and bundle-metadata safety
status: execution_in_progress
created: 2026-05-09
sprint: GOV-REVERT-001
visibility: internal
publish_allowed: false
authority: authority
relationship_to_main_sprint: governance -- safety controls only
relationship_to_product_source: none
---

# GOV-REVERT-001 -- Stash, Reset, Concurrent-Agent, and Bundle-Metadata Safety

## Purpose

Prevent recurrence of agent changes being hidden, reverted, overwritten, or mixed with unrelated
sprint metadata.

## Accepted Root Cause

The accepted REVERT-ROOTCAUSE-001 investigation classified the issue as `MULTIPLE_CAUSES` with
high confidence. The primary cause was agent cleanup using `git stash` and clean-tree tactics to
hide other sprint work. Secondary causes included concurrent sprint streams in one worktree,
root `bundle-metadata/` contamination, reset reflog entries, dangling stash commits, and evidence
metadata identity gaps.

## Required Controls

1. Agents must not use `git stash` to hide unrelated work.
2. Agents must not use `git reset`, `git restore`, `git checkout --`, or `git clean` to make the
   tree appear clean.
3. If unrelated dirty work exists, agents must classify it and stop or produce a blocker bundle.
4. Evidence tooling clean-tree pressure is not a reason to hide changes.
5. Every sprint must use exact-path staging only.
6. Broad staging is forbidden.
7. Broad rollback is forbidden.
8. Concurrent sprint streams must not share a single worktree unless explicitly authorized and
   dirty-state classification is complete.
9. One worktree should have one active execution sprint at a time.
10. Verification sprints may inspect but must not clean up other sprint work.

## Deliverables

- Governance policy updates in `AGENTS.md`, `GOVERNANCE.md`, handoff standards, methodology, and
  prompt templates.
- Read-only local git safety checker at `tools/governance/check_git_safety.py`.
- Unit tests for git safety and evidence metadata identity validation.
- Evidence builder hardening to reject root `bundle-metadata/` by default.
- Evidence validator hardening to fail mixed metadata identity.
- Local-only concurrent sprint lock standard.
- Exact-path quarantine of stale root `bundle-metadata/`, if safe.

## Acceptance Criteria

1. Git safety checker reports branch, HEAD, dirty files, untracked files, stash warnings, reset
   reflog warnings, root metadata contamination, broad staging command logs, and metadata identity
   conflicts.
2. Evidence builder rejects implicit root `bundle-metadata/` unless a legacy flag is explicitly
   supplied.
3. Evidence validator fails mixed primary sprint or contract identity in identity-critical metadata.
4. Governance docs and prompt templates require `git-safety-policy-check.md`.
5. Future execution final responses include `NO_STASH_RESET_RESTORE_CLEAN_USED: YES`.
6. Validation passes or any failure is documented as a blocker within this sprint's evidence.

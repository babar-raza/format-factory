# R42 Lane 1B: Local Commit / Dirty Tree Governance Rule

**Sprint:** R42
**Date:** 2026-05-21

## Governance Finding

AGENTS.md P1-P3:
- P1: Agent must never run `git commit` unless the human explicitly says so in the current session.
- P2: "Phase complete" does not mean "commit."
- P3: Approval from a previous session does NOT carry over.

This is unambiguous. Commits require explicit human instruction in the current session.

## Codified Rule

**Rule C-LOCAL-001: Sprint-Authorized Commits**

An agent may run `git commit` in a session if and only if:
1. The current-session human prompt explicitly says to commit OR authorizes the agent to act on behalf of a named project lead, AND
2. All staged files have been verified (no secrets, no .local/ contents, no .env), AND
3. Commits are exact-path only (no `git add .` or `git add -A`), AND
4. Remote push and publication remain forbidden without separate explicit approval.

**Rule C-LOCAL-002: Clean-Tree Requirement**

A sprint MUST NOT claim final verdict (`*_COMPLETE`, `*_POC_READY`, `*_HIGH_THROUGHPUT_*`) while `git status --short` shows uncommitted changes, UNLESS the final verdict is explicitly:
- `*_DIRTY_TREE_BLOCKED` with exact reason, OR
- `*_PROGRESS_ACCEPTED_CLOSEOUT_SUPERSEDED`

**Rule C-LOCAL-003: Emergency Bundle Restriction**

`emergency_blocker_bundle: true` is for genuine emergency blockers (e.g., CI outage, dependency unavailable).
A normal sprint with uncommitted changes must NOT use emergency_blocker_bundle to get around the dirty-tree check.
If the tree is dirty because work is uncommitted, the agent must:
1. Commit the work (if authorized in current session), OR
2. Document a DIRTY_TREE_BLOCKED verdict with exact reason.

## Bad-Agent Behavior Fixed in R42

| Behavior | Sprint | Fix |
|----------|--------|-----|
| Called sprint complete with dirty tree | R41 | R41 reclassified as SUPERSEDED |
| Used emergency_blocker_bundle for normal sprint | R41 | R42 commits properly, builds on clean tree |
| Bundle in .local/ not included in evidence chain | R41 | R42 bundle in tracked location (gitignored; path+hash in final-verdict) |
| Left PENDING reference in "fixed" section | R41 | R41 final-verdict rephrased |

## Validator Guard Tests Needed

Lane 2A will add validator checks for:
- Final verdict containing *_COMPLETE + dirty-tree marker in git-status-final.txt
- Final verdict containing emergency_blocker_bundle=true without EMERGENCY_* label

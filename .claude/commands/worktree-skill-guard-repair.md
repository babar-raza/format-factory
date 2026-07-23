---
version: "1.0"
last-updated: "2026-07-23"
phase-available: "all"
gate-required: null
skill_type: "ATOMIC_SKILL"
idempotency: "The same Git context resolves to the same active worktree root."
risk_level: HIGH
created-by: SKILL-GAP-FF6-WORKTREE-SKILL-GUARD
product_track: machinery_governance
generated_by: codex
visibility: generated
---

# /worktree-skill-guard-repair

Repair the pre-commit skill-attribution guard so shared hooks operate against
the active Git worktree. Preserve fail-closed coordination checks, scoped
exceptions, source-mutation detection, and ordinary single-checkout behavior.

## Required Inputs

- `defect_id`
- `linked_worktree_reproduction`
- `expected_repository_root`

## Execution

1. Reproduce the linked-worktree failure with a minimal temporary Git repository.
2. Add a regression test proving transcript and staged-file discovery use the
   active worktree even when the hook implementation is reached through a link.
3. Resolve the active root using Git's own `rev-parse --show-toplevel` result.
4. Fall back to the physical script checkout only outside a Git context.
5. Prove shared-checkout behavior and fail-closed coordination behavior remain
   unchanged.
6. Run the focused governance tests and execute the actual guard in the mission
   worktree.

## Mandatory Validations

- `linked_hook_resolves_active_worktree`
- `transcript_search_is_worktree_scoped`
- `coordination_check_uses_active_worktree`
- `shared_checkout_behavior_is_preserved`

## Allowed Paths

- `.hooks/pre-commit-skill-guard`
- `tests/governance/test_pre_commit_skill_guard_worktree.py`
- `reports/skills-*/skill-transcripts/worktree-skill-guard-repair-*.json`

## Forbidden Paths

- `src/**`
- `.local/exceptions/**`
- coordination bypass environment variables
- weakening or skipping the coordination precommit check
- human-only gate and release records

## Stop Conditions

- If active-worktree discovery cannot be proven under both linked and ordinary
  checkouts, retain fail-closed behavior and leave the commit blocked.

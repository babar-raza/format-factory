---
artifact_id: FF6-CLEAN-REPLAY-EVENT-47
artifact_type: clean_replay_contract
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Clean replay and repair contract

Reconstruct from GitLab `origin/main`; require source checkpoint
`6b775e80a16ce0d020b9df68ab26b2bb76adc232` to be an ancestor. Validate native event
`FF6-EVENT-000047` and hash `d4cc0a0292b9e5ea5d473d38c195ceb7328b85d47f28569da3cb8af64b1a22ff` before executing any mutation.

Use a fresh checkout/worktree, fresh environment, fresh coordination identity,
and immutable authority inputs. Never reset, stash, clean, or overwrite shared
state. A failed replay creates evidence and remediation; it cannot promote or
silently rewrite the accepted product checkpoint `ea118ba39904b54517ba6bc5839c8d4fc36fa050`.

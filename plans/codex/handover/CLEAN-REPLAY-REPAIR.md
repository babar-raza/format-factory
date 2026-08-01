---
artifact_id: FF6-CLEAN-REPLAY-EVENT-46
artifact_type: clean_replay_contract
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Clean replay and repair contract

Reconstruct from GitLab `origin/main`; require source checkpoint
`767e7006a19a118e4a16d72db0a15e2f387b44af` to be an ancestor. Validate native event
`FF6-EVENT-000046` and hash `6524928fd8c8aa81106e1a5a4058e64bd6359b23501f63e5814bed1d13de6bfe` before executing any mutation.

Use a fresh checkout/worktree, fresh environment, fresh coordination identity,
and immutable authority inputs. Never reset, stash, clean, or overwrite shared
state. A failed replay creates evidence and remediation; it cannot promote or
silently rewrite the accepted product checkpoint `767e7006a19a118e4a16d72db0a15e2f387b44af`.

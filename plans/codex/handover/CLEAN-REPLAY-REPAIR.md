---
artifact_id: FF6-CLEAN-REPLAY-EVENT-45
artifact_type: clean_replay_contract
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Clean replay and repair contract

Reconstruct from GitLab `origin/main`; require source checkpoint
`54f2a12f6d8e7d31f9f7beb6e7b0e9f5c2cb82a7` to be an ancestor. Validate native event
`FF6-EVENT-000045` and hash `fbd74899787e1c3aa7ce7efcbc4eec2cb098d1ed0ebb78717858baceabf17550` before executing any mutation.

Use a fresh checkout/worktree, fresh environment, fresh coordination identity,
and immutable authority inputs. Never reset, stash, clean, or overwrite shared
state. A failed replay creates evidence and remediation; it cannot promote or
silently rewrite the accepted product checkpoint `d95af5aeb248907b4d23457ecd288723fc9c2050`.

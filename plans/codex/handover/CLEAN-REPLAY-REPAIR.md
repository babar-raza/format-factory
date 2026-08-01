---
artifact_id: FF6-CLEAN-REPLAY-EVENT-44
artifact_type: clean_replay_contract
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Clean replay and repair contract

Reconstruct from GitLab `origin/main`; require source checkpoint
`4c4b80517a34534416492a772c6d3d81bfde9809` to be an ancestor. Validate native event
`FF6-EVENT-000044` and hash `20e8f7fac635994e4f1051a5dd9cd3bd0a2da3b0e361d006a17d834536fc09cd` before executing any mutation.

Use a fresh checkout/worktree, fresh environment, fresh coordination identity,
and immutable authority inputs. Never reset, stash, clean, or overwrite shared
state. A failed replay creates evidence and remediation; it cannot promote or
silently rewrite the accepted product checkpoint `d95af5aeb248907b4d23457ecd288723fc9c2050`.

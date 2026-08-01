---
artifact_id: FF6-PROVIDER-START-EVENT-44
artifact_type: provider_start_commands
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Provider-neutral start commands

Start at [START-HERE.md](START-HERE.md). Verify GitLab `origin/main`, event
`FF6-EVENT-000044`, and source checkpoint `4c4b80517a34534416492a772c6d3d81bfde9809`. Run:

```powershell
git fetch origin
git status --short --branch
python plans/codex/handover/validate_handover.py --self-test --require-clean
python plans/codex/handover/validate_committed_checkpoint.py --ref origin/main
python -m tools.supervisor.coordination status
```

Then register a fresh identity and execute `TC-FF6-ACCEL-CONTROL-001` through
`refresh-provider-neutral-handover`. Never reuse recorded provider-local state.

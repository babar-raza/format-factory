---
artifact_id: FF6-PROVIDER-START-EVENT-45
artifact_type: provider_start_commands
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Provider-neutral start commands

Start at [START-HERE.md](START-HERE.md). Verify GitLab `origin/main`, event
`FF6-EVENT-000045`, and source checkpoint `54f2a12f6d8e7d31f9f7beb6e7b0e9f5c2cb82a7`. Run:

```powershell
git fetch origin
git status --short --branch
python plans/codex/handover/validate_handover.py --self-test --require-clean
python plans/codex/handover/validate_committed_checkpoint.py --ref origin/main
python -m tools.supervisor.coordination status
```

Then register a fresh identity and execute `TC-FF6-NRRD-READINESS-001` through
its registered skill sequence. Never reuse recorded provider-local state.

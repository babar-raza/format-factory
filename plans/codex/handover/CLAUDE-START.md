---
artifact_id: FF6-PROVIDER-START-EVENT-47
artifact_type: provider_start_commands
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Provider-neutral start commands

Start at [START-HERE.md](START-HERE.md). Verify GitLab `origin/main`, event
`FF6-EVENT-000047`, and source checkpoint `6b775e80a16ce0d020b9df68ab26b2bb76adc232`. Run:

```powershell
git fetch origin
git status --short --branch
python plans/codex/handover/validate_handover.py --self-test --require-clean
python plans/codex/handover/validate_committed_checkpoint.py --ref origin/main
python -m tools.supervisor.coordination status
```

Then register a fresh identity and execute `TC-FF6-NRRD-READINESS-001` through
its registered skill sequence. Never reuse recorded provider-local state.

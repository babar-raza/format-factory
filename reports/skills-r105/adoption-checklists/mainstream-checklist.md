# Mainstream Adoption Checklist (Skills R105)

## Before Starting Product Work
- [ ] Read `.supervisor/skill-registry.yaml` to find the skill_id for your task
- [ ] Read the command file at `.claude/commands/{skill_id}.md` for execution steps
- [ ] Check if a generated handoff exists at `reports/skills-r{N}/generated-handoffs/`

## During Execution
- [ ] Follow the steps in the command file
- [ ] Only modify files listed in `allowed_files`
- [ ] For src-editing skills, update `reports/r90/product-code-change-ledger.json`
- [ ] Run focused tests specified in the handoff

## After Execution
- [ ] Write a transcript JSON to `reports/{run_id}/skill-transcripts/`
- [ ] Include all required fields: invocation_id, skill_id, mode, inputs, allowed_files, actual_files_changed, tests_run, result
- [ ] For LIVE mode: include ledger_entry_id
- [ ] Validate transcript: `.local/venv/Scripts/python tools/supervisor/validate_skill_transcript.py <transcript.json>`
- [ ] Include transcript path in evidence declaration evidence_paths

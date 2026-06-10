# Next Skills Agent Prompt (R105)

## MODE: SKILLS STREAM — ENFORCEMENT INTEGRATION AND LIVE EXECUTION

## Sprint ID
FORMAT-FACTORY-SKILLS-R105-ENFORCEMENT-INTEGRATION-AND-LIVE-EXECUTION-001

## Stream: skills (NOT mainstream)

## Read First
1. `reports/skills-r104/r103-acceptance.md`
2. `reports/skills-r104/adoption-enforcement-campaign.md`
3. `reports/skills-r104/skill-promotion-campaign.md`
4. `reports/skills-r104/ledger-enforcement-bridge.md`
5. `.supervisor/skill-registry.yaml`
6. `tools/supervisor/validate_skill_transcript.py`
7. `tools/supervisor/validate_claude_commands.py`

## Tasks

### Task 1: Integrate Transcript Validation into Supervisor Grading
- Modify `tools/supervisor/grade_declared_work.py` to check for skill_id in work items
- When skill_id present, validate transcript at evidence_path
- Test: work item with missing transcript grades as OVERCLAIMED
- Test: work item with invalid transcript grades as OVERCLAIMED
- Test: work item with valid transcript grades as ACCEPTED

### Task 2: Execute 2 LIVE Handoffs
- Handoff-001: FODS RenameSheet (`reports/skills-r103/generated-handoffs/handoff-001-fods-renamesheet.md`)
- Handoff-002: Netpbm ExtractChannel (`reports/skills-r103/generated-handoffs/handoff-002-netpbm-extractchannel.md`)
- Mode: LIVE (requires ledger entries)
- Expected: Source changes, 8+ tests each, ledger entries, LIVE transcripts

### Task 3: Stream-Specific Supervisor Outputs
- Add `stream` field to evidence declaration schema
- Modify `autonomous_cycle.py` to write stream-specific next-sprint.md
- Test: skills declaration produces skills-specific next-sprint

### Task 4: Convert 2 Legacy Orphan Commands to Governed Skills
- Candidates: evidence-review-next-prompt, execution-handoff (currently orphans)
- Register in skill-registry.yaml with active status
- Ensure command files pass validation

## Hard Quota
- 2 LIVE transcripts with ledger entries
- 1 supervisor grading integration (with 3 tests)
- 1 stream-specific output proof
- 2 orphan commands converted

## Forbidden Paths
- `registry/format-registry.yaml`
- `plans/master-plan.md`

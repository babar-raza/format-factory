# Next Skills Agent Prompt (R104)

## MODE: SKILLS STREAM — ADOPTION ENFORCEMENT AND LIVE EXECUTION

## Sprint ID
FORMAT-FACTORY-SKILLS-R104-ADOPTION-ENFORCEMENT-AND-LIVE-EXECUTION-001

## Stream: skills (NOT mainstream)

## Read First
1. `reports/skills-r103/r102-reconciliation.md`
2. `reports/skills-r103/adoption-proof.md`
3. `reports/skills-r103/stream-isolation-repair.md`
4. `.supervisor/skill-registry.yaml`
5. `tools/supervisor/validate_skill_transcript.py`
6. `tools/supervisor/validate_claude_commands.py`
7. `reports/skills-r103/generated-handoffs/`

## Tasks

### Task 1: Execute Handoff-001 (FODS RenameSheet) — LIVE
- Skill: /add-dotnet-object-model-feature
- Mode: LIVE
- Source: `reports/skills-r103/generated-handoffs/handoff-001-fods-renamesheet.md`
- Expected: RenameSheet in FodsDocument.cs, 8+ tests, ledger entry, LIVE transcript

### Task 2: Execute Handoff-002 (Netpbm ExtractChannel) — LIVE
- Skill: /add-dotnet-object-model-feature
- Mode: LIVE
- Expected: ExtractChannel in NetpbmImage.cs, 8+ tests, ledger entry, LIVE transcript

### Task 3: Supervisor Transcript Enforcement Integration
- Add transcript validation to supervisor grading pipeline
- Test: work item with missing transcript grades as OVERCLAIMED

### Task 4: Stream-Aware Supervisor Outputs
- Add `stream` field to evidence declaration schema
- Supervisor generates stream-specific next-sprint.md

## Hard Quota
- 2 LIVE transcripts with ledger entries
- 1 supervisor integration test
- Stream-specific next-sprint.md

## Forbidden Paths
- `registry/format-registry.yaml`
- `plans/master-plan.md`

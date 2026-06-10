# Next Skills Agent Prompt (R103)

## MODE: SKILLS STREAM — GOVERNED EXECUTION

## Sprint ID
FORMAT-FACTORY-SKILLS-R103-LIVE-GOVERNED-EXECUTION-HANDOFF-CONSUMPTION-001

## Read First
1. `reports/skills-r102/r101-reconciliation.md` — what R101/R102 proved
2. `reports/skills-r102/skill-system-truth-map.md` — current skill system state
3. `reports/skills-r102/generated-handoffs/` — 4 ready handoffs
4. `.supervisor/skill-registry.yaml` — 20 skills (13 active, 7 draft)
5. `tools/supervisor/validate_skill_transcript.py` — transcript validator
6. `tools/supervisor/validate_claude_commands.py` — command validator

## Tasks

### Task 1: Execute Handoff-001 (FODS RenameSheet)
- Skill: /add-dotnet-object-model-feature
- Mode: LIVE
- Consume: `reports/skills-r102/generated-handoffs/handoff-001-fods-rename-sheet.yaml`
- Expected: RenameSheet method in FodsDocument.cs, 8+ tests, ledger entry

### Task 2: Execute Handoff-002 (Netpbm ExtractChannel)
- Skill: /add-dotnet-object-model-feature
- Mode: LIVE
- Consume: `reports/skills-r102/generated-handoffs/handoff-002-netpbm-extract-channel.yaml`
- Expected: ExtractChannel method in NetpbmImage.cs, 8+ tests, ledger entry

### Task 3: Execute Handoff-004 (PPM brightness_adjust)
- Skill: /add-python-object-model-feature
- Mode: LIVE
- Consume: `reports/skills-r102/generated-handoffs/handoff-004-ppm-brightness-adjust.yaml`
- Expected: brightness_adjust in ppm_parser.py, 4+ tests, ledger entry

### Task 4: Validate All Transcripts
- Run `python tools/supervisor/validate_skill_transcript.py --dir reports/skills-r103/skill-transcripts/`
- All LIVE transcripts must have ledger_entry_id
- All transcripts must have correct schema

## Hard Quota
- 3 LIVE transcripts (PASS)
- 3 ledger entries (verified by ledger validator)
- 0 command file regressions (18/18 must still pass)

## Forbidden Paths
- `registry/format-registry.yaml`
- `plans/master-plan.md`

## Evidence
Write evidence declaration to `.local/evidences/skills-r103/evidence-declaration.yaml`
Run supervisor autonomous-cycle.
Build declaration review package and report absolute path + SHA-256.

# Controlled Governed Proof (Skills R102 Wave 6)

## Proof Statement

This document demonstrates end-to-end governed execution:
1. A skill is selected from the registry
2. Its command file is validated (12/12 sections)
3. A transcript is generated with correct schema
4. The transcript passes validation
5. Anti-bypass checks confirm rejection of invalid inputs

## Proof Walk-Through

### Step 1: Select Skill
Skill: `add-dotnet-object-model-feature`
Registry entry: active, product_track: commercial_dotnet
Command file: `.claude/commands/add-dotnet-object-model-feature.md`

### Step 2: Validate Command File
```
$ python tools/supervisor/validate_claude_commands.py --file .claude/commands/add-dotnet-object-model-feature.md
COMMAND_VALIDATION: PASS (12/12 sections)
```

### Step 3: Generate Transcript
Transcript: `reports/skills-r102/skill-transcripts/transcript-001-add-dotnet-object-model-feature-fods.json`
Schema fields present: invocation_id, skill_id, mode, inputs, allowed_files, actual_files_changed, tests_run, result

### Step 4: Validate Transcript
```
$ python tools/supervisor/validate_skill_transcript.py reports/skills-r102/skill-transcripts/transcript-001-add-dotnet-object-model-feature-fods.json
TRANSCRIPT_VALIDATION: PASS
```

### Step 5: Anti-Bypass Rejection
- Unregistered skill → REJECTED (ANTI-BYPASS-001)
- Invalid mode → REJECTED (ANTI-BYPASS-003)
- Files outside allowed → REJECTED (ANTI-BYPASS-005)
- Live without ledger → REJECTED (ANTI-BYPASS-007)

## Evidence Files
- Validator results: `reports/skills-r102/validator-results/command-validation-r102-final.json`
- Transcript validation: `reports/skills-r102/validator-results/transcript-validation-r102.json`
- Anti-bypass demos: `reports/skills-r102/validator-results/anti-bypass-demos.json`
- Raw test logs: `reports/skills-r102/raw-logs/test-validators-all.log`

## Conclusion

The governed execution pipeline enforces:
1. Only registered skills can produce valid transcripts
2. Only valid modes (dry-run, live, anti-bypass-demo) are accepted
3. File changes must stay within allowed paths
4. Live src-editing requires ledger entry
5. Command files must have all 12 required sections

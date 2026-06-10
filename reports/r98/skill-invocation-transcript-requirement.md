# Skill Invocation Transcript Requirement

## Policy (R98+)
Every new src/* change must include a skill invocation transcript.

## Required Fields
- skill_id
- command_path
- input_parameters (format_id, api_name, etc.)
- allowed_files
- forbidden_files
- generated/changed files
- validation_commands
- output_evidence
- ledger_entry_id

## Storage
- `reports/<sprint>/skill-transcripts/<entry-id>.md`
- `reports/<sprint>/skill-transcripts/<entry-id>.json`

## Enforcement
- Materializer must package skill transcripts
- Grader must downgrade governed claims without transcript
- Backfilled pre-governance entries exempt if clearly marked

## Registry Update
`.supervisor/skill-registry.yaml` global_controls now includes:
`skill_invocation_transcript_required: true`

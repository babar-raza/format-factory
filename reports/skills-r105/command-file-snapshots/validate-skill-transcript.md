---
version: "1.0"
last-updated: "2026-06-03"
created-by: skills-r104
---

# /validate-skill-transcript

Validate a skill invocation transcript JSON file against the governed registry schema.

## Usage

Validate a single transcript or a directory of transcripts. Reports PASS/FAIL with detailed error/warning messages.

## Required Inputs

- `transcript_path`: Path to a single transcript JSON file, OR
- `transcript_dir`: Path to a directory of transcript JSON files (uses `--dir` flag)
- `registry_path` (optional): Override registry location (default: `.supervisor/skill-registry.yaml`)

## What This Skill Does

1. Read the transcript JSON file
2. Check all required fields are present: `invocation_id`, `skill_id`, `mode`, `inputs`, `allowed_files`, `actual_files_changed`, `tests_run`, `result`
3. Validate `mode` is one of: `dry-run`, `live`, `anti-bypass-demo`
4. Validate `result` is one of: `PASS`, `FAIL`
5. Check `skill_id` exists in the governed registry
6. For src-editing tracks in LIVE mode, verify `ledger_entry_id` is present
7. Verify `actual_files_changed` is a subset of `allowed_files`
8. Report errors and warnings

## Allowed Paths

- `tools/supervisor/validate_skill_transcript.py` (read-only)
- `.supervisor/skill-registry.yaml` (read-only)
- Any transcript JSON file specified as input (read-only)
- `reports/skills-r*/validator-results/` (write validation results)

## Forbidden Paths

- `src/net/**` (no product source)
- `src/python/**` (no product source)
- `registry/format-registry.yaml` (no gate authority)
- `plans/master-plan.md` (no plan changes)

## Stop Conditions

- Transcript file does not exist or is not valid JSON
- Registry file not found (warn but continue)
- Any error in validation output

## Evidence Output

Write validation result to `reports/skills-r{N}/validator-results/transcript-validation-{context}.json`:
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "skill_id": "add-dotnet-api",
  "mode": "live",
  "result": "PASS"
}
```

## Validation

```bash
.local/venv/Scripts/python tools/supervisor/validate_skill_transcript.py <transcript.json> --json
.local/venv/Scripts/python tools/supervisor/validate_skill_transcript.py --dir <directory> --json
```

## Rollback

No state changes to roll back. This is a read-only validation tool.

## Transcript Requirement

This skill validates transcripts but does not itself require a transcript. When used as part of a sprint, record the validation results in the evidence declaration.

## Sample Invocation

```bash
# Single file
.local/venv/Scripts/python tools/supervisor/validate_skill_transcript.py reports/skills-r104/skill-transcripts/transcript-001.json --json

# Directory
.local/venv/Scripts/python tools/supervisor/validate_skill_transcript.py --dir reports/skills-r104/skill-transcripts/ --json
```

## Changelog

- v1.0 (2026-06-03): Initial command file created for skill promotion from draft to active (Skills R104)

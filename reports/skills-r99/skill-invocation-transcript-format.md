# Train F: Skill Invocation Transcript Format
Sprint: FORMAT-FACTORY-SKILLS-R99-SKILL-REGISTRY-GOVERNED-EXECUTION-PARALLEL-MEGA-TRAIN-001
Date: 2026-06-03

## Purpose

Every skill run must leave proof. The transcript format captures what skill was used,
what files were changed, what tests ran, and what ledger/matrix updates were made.

## Transcript Format (JSON)

```json
{
  "transcript_version": "1.0",
  "skill_id": "<skill-id>",
  "invocation_id": "<SPRINT-GOVERNED-TRACK-FORMAT-FEATURE-NNN>",
  "run_id": "<sprint-id>",
  "timestamp": "<ISO-8601>",
  "inputs": {
    "format_id": "<format>",
    "api_name": "<api or feature name>",
    "exact_source_paths": ["<paths>"],
    "exact_test_paths": ["<paths>"],
    "ledger_entry_path": "reports/r90/product-code-change-ledger.json"
  },
  "allowed_files": ["<paths that may be edited>"],
  "forbidden_files": ["<paths that must not be edited>"],
  "actual_changed_files": [
    {
      "path": "<file>",
      "sha256_before": "<hash>",
      "sha256_after": "<hash>",
      "change_type": "modified|created|deleted"
    }
  ],
  "tests_generated": ["<test file paths>"],
  "tests_run": {
    "command": "<test command>",
    "passed": 0,
    "failed": 0,
    "skipped": 0
  },
  "ledger_entry": {
    "entry_id": "<ledger entry ID>",
    "classification": "GOVERNED_PRODUCT_CHANGE",
    "skill": "<skill-id>"
  },
  "matrix_update": {
    "field": "<capability path>",
    "old_value": "<old>",
    "new_value": "<new>"
  },
  "evidence_outputs": [
    "<paths to evidence files>"
  ],
  "result": "PASS|FAIL|PARTIAL",
  "rollback": "<rollback instructions if result is FAIL>"
}
```

## Transcript Format (Markdown)

```markdown
# Skill Transcript: <invocation_id>

| Field | Value |
|-------|-------|
| Skill | <skill_id> |
| Invocation ID | <invocation_id> |
| Sprint | <run_id> |
| Timestamp | <ISO-8601> |
| Format | <format_id> |
| Feature | <api_name> |
| Result | PASS/FAIL |

## Changed Files

| File | Before SHA-256 | After SHA-256 | Type |
|------|---------------|--------------|------|
| <path> | <hash> | <hash> | modified |

## Tests

- Command: `<test command>`
- Passed: N
- Failed: 0

## Ledger Entry

- Entry ID: <id>
- Classification: GOVERNED_PRODUCT_CHANGE

## Matrix Update

- Field: <capability path>
- Old: <old value>
- New: <new value>
```

## Storage Location

- JSON: `reports/<stream>/skill-transcripts/<invocation_id>.json`
- Markdown: `reports/<stream>/skill-transcripts/<invocation_id>.md`

## Rules

1. Every skill run produces both JSON and markdown transcripts
2. Transcript must be written AFTER the skill completes but BEFORE sprint closeout
3. Failed skill runs produce transcripts with `result: FAIL` (for debugging)
4. Transcript invocation_id matches the ledger entry_id when a ledger entry exists
5. Transcripts are evidence-eligible inputs to the declaration

# Transcript Cycle Integration (Skills R107 Lane B)

## Summary
Wired transcript validation into the evidence inspector (`inspect_declared_evidence.py`).
The inspector now detects transcript JSON files in evidence_paths and validates them
via `validate_skill_transcript.validate_transcript()`.

## Changes Made

### `tools/supervisor/inspect_declared_evidence.py`
1. Added `_get_validate_transcript()` — lazy import of `validate_transcript` to avoid circular imports
2. Added `_is_transcript_json(data)` — detects if a JSON dict has transcript fields (`invocation_id`, `skill_id`, `mode`, `result`)
3. Added `check_transcript_in_evidence(evidence_paths, repo_root)` — scans evidence_paths for `.json` files, checks if they are transcripts, validates each one
4. Modified `inspect_item()` — calls `check_transcript_in_evidence()` and includes `transcript_validation` in the returned dict

### How It Works
```
evidence_paths → filter .json → parse → _is_transcript_json? → validate_transcript() → result
```

When a work item has transcript JSON in its evidence_paths:
- Inspector detects it automatically
- Validates against the skill registry
- Attaches `transcript_validation` dict to the item inspection
- `grade_item()` already handles the inspection dict — transcript presence is now visible to grading

### transcript_validation Structure
```json
{
  "transcripts_found": 1,
  "transcripts_valid": 1,
  "transcripts_invalid": 0,
  "all_valid": true,
  "valid_transcripts": [{"path": "...", "skill_id": "...", "mode": "...", "result": "..."}],
  "invalid_transcripts": []
}
```

## Tests Added
18 new tests in `tests/python/supervisor/test_r107_inspector_transcript_enrichment.py`:

| Class | Tests | Description |
|-------|-------|-------------|
| TestIsTranscriptJson | 4 | Detection helper for transcript vs non-transcript JSON |
| TestCheckTranscriptInEvidence | 7 | End-to-end enrichment with real temp files |
| TestInspectItemTranscriptEnrichment | 3 | inspect_item() includes transcript_validation |
| TestGradeItemWithTranscript | 3 | grade_item() behavior with transcript_validation present |
| TestDeclarationLevelTranscriptAggregation | 1 | inspect_declaration() propagates enrichment |

## Impact on Evidence Quality Score
- Items with transcript JSON in evidence_paths now have `transcript_validation` populated
- This provides an additional dimension for ACCEPTED_VERIFIED (beyond test content and criteria patterns)
- Future R108+ can optionally use transcript_validation.all_valid as a VERIFIED boost factor

## Test Results
- 18 new tests: all pass
- 119 total supervisor tests: all pass (101 baseline + 18 new)
- 0 failures

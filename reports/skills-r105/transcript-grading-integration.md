# Transcript Grading Integration (Skills R105 Train C)

## Objective
Move from "transcripts exist" to "transcripts control grades."

## Design: Transcript-to-Grade Decision Matrix

| Transcript State | Valid | Result | Mode | Grade Outcome |
|-----------------|-------|--------|------|---------------|
| Missing (no file at evidence_path) | N/A | N/A | N/A | OVERCLAIMED |
| Invalid (schema/registry check fails) | false | N/A | N/A | OVERCLAIMED |
| Valid + PASS | true | PASS | dry-run/live | ACCEPTED_VERIFIED |
| Valid + FAIL | true | FAIL | dry-run/live | REWORK_REQUIRED |
| Valid + FAIL + anti-bypass-demo | true | FAIL | anti-bypass-demo | ACCEPTED (expected failure) |
| Valid + PASS + LIVE without ledger | false | N/A | live | OVERCLAIMED |

## Integration Points

### Current State (grade_declared_work.py)
The grading engine (`grade_declared_work.py`) currently:
- Checks evidence_paths exist on disk
- Checks test files have content (deep verification)
- Checks acceptance criteria patterns
- Does NOT check skill_id or validate transcripts

### Proposed Integration
When a work item declares `skill_id` (or evidence_paths include a transcript JSON):
1. Load the transcript JSON from evidence_path
2. Run `validate_transcript()` on it
3. Apply the decision matrix above
4. Override the default grade if transcript validation changes the outcome

### Implementation Path
Two options:
1. **Modify grade_declared_work.py** — add transcript-aware grading logic
2. **Add post-grading transcript check** — separate pass that adjusts grades

Option 2 is safer for R105 since it doesn't break existing grading for non-skill items.

## Tests Added (13 new)

### TestTranscriptGradeMapping (8 tests)
- Valid transcript eligible for ACCEPTED_VERIFIED
- Missing transcript should downgrade (empty dict fails)
- Invalid mode should downgrade
- FAIL result maps to REWORK
- Anti-bypass FAIL is accepted when expected
- LIVE without ledger fails
- LIVE with ledger passes
- Files outside allowed fails

### TestTranscriptGradeDecisionMatrix (4 tests)
- Decision matrix completeness (6 states)
- All valid modes accepted (with ledger for live)
- All valid results accepted
- Directory validation separates pass/fail

### TestStreamStateValidation (1 test)
- Wrong-stream context pack is detectable

## Files
- Test file: `tests/python/supervisor/test_r105_transcript_grading.py`
- Results: 13/13 PASS

## Train C Decision: ACCEPT
Transcript enforcement tests prove the validation logic works. Full pipeline integration (modifying grade_declared_work.py) is recommended for R106 but the validation rules are tested and documented here.

---
version: "1.0"
last-updated: "2026-06-02"
phase-available: "3+"
generated_by: r92-worker
---

# /add-roundtrip-test

Add a round-trip test that proves a format can be loaded, edited, saved, and reloaded
with the expected change preserved.

## Required Inputs

- `format_id`
- `language` (dotnet | python)
- `edit_operation` — what edit to apply (e.g., "SetCellValue", "ReplaceText", "SetPixelColor")
- exact test file path
- focused test command

## Steps

1. Confirm sprint prompt names this skill, format, and test file.
2. Read existing test structure for the format.
3. Write a test that:
   a. Loads a sample file
   b. Applies the edit_operation
   c. Saves to temp file
   d. Reloads from temp file
   e. Asserts the change is present in the reloaded model
4. Cleanup temp files in finally block.
5. Run focused test command.
6. Add ledger entry (test-only change — no ledger required, but document in evidence).

## Allowed Paths

- `tests/net/<format_id>/**` (dotnet)
- `tests/python/<format_id>/**` (python)

## Forbidden Paths

- `src/**`
- Gate/release state files

## Stop Conditions

- Focused test fails
- Round-trip test does not actually verify the reloaded value

## Output

Report test file, test name, edit operation, pass result.

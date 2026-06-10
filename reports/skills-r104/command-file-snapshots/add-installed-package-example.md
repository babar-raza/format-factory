---
version: "1.0"
last-updated: "2026-06-02"
phase-available: "3+"
generated_by: r92-worker
---

# /add-installed-package-example

Add a standalone example that demonstrates a format's public API as if the package
were installed from PyPI/NuGet (no PYTHONPATH or project reference needed).

## Required Inputs

- `format_id`
- `language` (dotnet | python)
- `example_name` — descriptive name
- `capability_shown` — what the example demonstrates
- exact example file path

## Steps

1. Confirm sprint prompt names this skill and exact paths.
2. Write an example file that:
   - Uses only the public API (no internal imports)
   - Has a main() or equivalent entry point
   - Shows the full load → [edit] → save/export flow
   - Includes inline comments explaining each step
3. Write a smoke test (optional) that runs the example and verifies it exits 0.
4. Update examples/python/<format_id>/ or examples/net/<format_id>/ as appropriate.
5. Do not add to src/; examples are docs-adjacent.

## Allowed Paths

- `examples/python/<format_id>/**`
- `examples/net/<format_id>/**`

## Forbidden Paths

- `src/**`
- Gate/release state files

## Stop Conditions

- Example uses internal imports that bypass installed-package behavior
- Example does not run (syntax error or missing sample file)

## Evidence Required

- Example file path
- Capability shown
- Smoke test result: PASS | FAIL | SKIP

## Validation

Complete when the example runs without error using only the installed package's public API.

## Rollback

1. Remove the example file from `examples/python/<format_id>/` or `examples/net/<format_id>/`
2. Remove the smoke test if created

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
with: skill_id, format_id, example_name, example_path, smoke_test_result, verdict.

## Sample Invocation

```
/add-installed-package-example
# Inputs:
#   format_id: fods
#   language: python
#   example_name: fods_workbook_to_csv
#   capability_shown: Parse FODS workbook and export to CSV
#   example_path: examples/python/fods/workbook_to_csv_example.py
```

## Changelog

- 1.0 (2026-06-02): Initial R92 governed command.
- 1.2 (2026-06-03): Added evidence, validation, rollback, transcript, sample invocation, changelog (Skills R101).

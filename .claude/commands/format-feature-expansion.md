---
version: "1.0"
last-updated: "2026-07-02"
phase-available: "3+"
gate-required: "Explicit product implementation authorization"
generated_by: claude
visibility: generated
---

# /format-feature-expansion

Add a new export, transform, or accessor function to an existing Python FOSS format codec.
Generates bounded taskcards via `tools/playbook/generate_playbook_taskcards.py`.
Detailed playbook contract is in `playbooks/format-factory/format-feature-expansion.md`.

## Required Inputs

- `format_name` — target format id (e.g. `fods`, `csv`, `ndjson`)
- `codec_file` — path to the codec source file (e.g. `src/python/fods/fods_codec.py`)
- `init_file` — path to `__init__.py` for `__all__` export update
- `test_dir` — path to the format's test directory
- `function_name` — name of the new function to implement
- `function_signature` — full Python signature string
- `capability_label` — one-line description for the capability matrix

## Steps

1. Read the codec file and `__init__.py` to understand existing patterns and exports
2. Verify the spec QName for this capability exists in the SAL and is assigned to this format
3. Draft the new function in the codec file, following existing naming and type conventions
4. Write focused tests in the test directory: minimum 7 tests per new function
5. Verify import: `from <format>.<codec_module> import <function_name>` must succeed
6. Run the focused test command and confirm all new tests pass
7. Update `__all__` in `__init__.py` to export the new function
8. Write evidence: changed files list, test result output, import proof

## Allowed Paths

- `src/python/<format_name>/` — codec source files (read and write)
- `tests/python/<format_name>/` — test files (read and write)
- `examples/python/<format_name>/` — example files (optional, write)
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — .NET product source is out of scope
- `poc-targets.yaml` — no gate or POC state changes
- `registry/format-registry.yaml` — registry is read-only in this skill
- `AGENTS.md`, `CLAUDE.md`, `GOVERNANCE.md` — governance docs are read-only
- `.supervisor/skill-registry.yaml` — skill registry is read-only here
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the function requires an external library not already in the format's dependencies
- Stop if no valid spec QName exists for the target capability (consult SAL first)
- Stop if the installed format package breaks after adding the function
- Stop if governance validators fail (`governance_validators_pass` must be true)
- Stop if fewer than 7 tests pass for the new function

## Output Format

Report at the end of execution:
- List of changed files with brief description of each change
- Test result summary: `N/N tests pass`
- Import proof: the import command and its success output
- Capability label used in the matrix update

## Validation

- `governance_validators_pass` — all governance validators must pass
- `min_7_tests_per_function` — at least 7 focused tests per new function
- `no_new_external_imports` — no new third-party imports added
- `init_all_export_updated` — `__all__` in `__init__.py` is updated

## Rollback

Revert the codec source change, remove the new tests, and restore `__all__` in `__init__.py`.
Confirm the format package still imports cleanly after revert.

Transcript mention: execution produces a skill invocation transcript at
`reports/skills-r<N>/skill-transcripts/format-feature-expansion-<format>.json`.

## Sample Invocation

```
/format-feature-expansion
format_name: fods
codec_file: src/python/fods/fods_codec.py
init_file: src/python/fods/__init__.py
test_dir: tests/python/fods/
function_name: get_sheet_names
function_signature: def get_sheet_names(model: dict) -> list[str]
capability_label: Return ordered list of sheet names from FODS spreadsheet
```

## Changelog

- 1.0 (2026-07-02): Initial command file. Skill registered FF-PLAYBOOK-SYSTEM-001.
  Playbook contract at playbooks/format-factory/format-feature-expansion.md v1.2.

---
version: "1.0"
last-updated: "2026-07-02"
phase-available: "3+"
gate-required: "Explicit product implementation authorization"
generated_by: claude
visibility: generated
---

# /product-source-task

Execute a single bounded product source change to an existing Python FOSS format codec.
General-purpose template; use `/format-feature-expansion` when adding a new export or
transform function. Detailed playbook contract at
`playbooks/format-factory/product-source-task-template.md`.

## Required Inputs

- `format_name` — target format id (e.g. `fods`, `csv`)
- `function_name` — name of the function being changed or created
- `codec_file` — path to the codec source file (e.g. `src/python/fods/fods_codec.py`)
- `init_file` — path to `__init__.py` for `__all__` export verification
- `test_sprint` — sprint identifier for focused test naming (e.g. `r120`)

## Steps

1. Read the codec file to understand existing implementation patterns and current state
2. Draft the bounded source change in the codec file
3. Write focused tests in the format's test directory: minimum 9 tests per changed function
4. Verify import: `from <format>.<codec_module> import <function_name>` must succeed
5. Run focused tests and confirm all pass
6. Update `__all__` in `__init__.py` if a new public symbol was added
7. Write supervisor log entry for this task

## Allowed Paths

- `src/python/<format_name>/` — codec source files (read and write)
- `tests/python/<format_name>/` — test files (read and write)
- `examples/python/<format_name>/` — example files (optional, write)
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — .NET product source is out of scope for Python source tasks
- `poc-targets.yaml` — no POC state changes
- `registry/format-registry.yaml` — registry is read-only in this skill
- `AGENTS.md`, `CLAUDE.md`, `GOVERNANCE.md` — governance docs are read-only
- `.supervisor/skill-registry.yaml` — skill registry is read-only here
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the change requires an external library not already in the format's dependencies
- Stop if the installed format package breaks after the change
- Stop if governance validators fail (`governance_validators_pass` must be true)
- Stop if fewer than 9 tests pass for the changed function
- Stop if the change touches more than one codec file (split into separate tasks)

## Output Format

Report at the end of execution:
- List of changed files with brief description of each change
- Test result summary: `N/N tests pass` for focused test command
- Import proof: the import command and its success output
- Supervisor log entry: task id, format, function, verdict

## Validation

- `governance_validators_pass` — all governance validators must pass
- `min_9_tests_per_function` — at least 9 focused tests per changed function
- `no_new_external_imports` — no new third-party imports added
- `init_all_export_updated` — `__all__` in `__init__.py` reflects any new public symbols

## Rollback

Revert the source change, remove any new tests added, and restore `__all__` in `__init__.py`.
Confirm the format package still imports cleanly and all pre-existing tests pass after revert.

Transcript mention: execution produces a skill invocation transcript at
`reports/skills-r<N>/skill-transcripts/product-source-task-<format>-<function>.json`.

## Sample Invocation

```
/product-source-task
format_name: fods
function_name: get_cell_value
codec_file: src/python/fods/fods_codec.py
init_file: src/python/fods/__init__.py
test_sprint: r120
```

## Changelog

- 1.0 (2026-07-02): Initial command file. Skill registered FF-PLAYBOOK-SYSTEM-001.
  Playbook contract at playbooks/format-factory/product-source-task-template.md v1.1.

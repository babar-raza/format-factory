---
version: "1.0"
last-updated: "2026-07-02"
phase-available: "3+"
gate-required: "Explicit product implementation authorization"
generated_by: claude
visibility: generated
---

# /new-format-kickstart

Start a brand-new Python FOSS format codec from scratch. Produces the minimum viable slice:
probe function, load function, write function, and a passing test suite. Uses the canonical
contract defined in `playbooks/format-factory/new-format-kickstart-template.md`.

Proven from NDJSON, FODG, and TSV acquisitions.

## Required Inputs

- `format_name` — short identifier for the new format (e.g. `ndjson`, `fodg`)
- `file_extensions` — list of file extensions (e.g. `[".ndjson", ".jsonl"]`)
- `format_spec_ref` — reference to the format spec or SAL fact (e.g. `FACT-NDJSON-001`)
- `detection_signature` — bytes or pattern used to detect this format (e.g. `b'{'` first byte)
- `stdlib_module` — Python stdlib module used for parsing (e.g. `json`, `csv`); `None` if custom

## Steps

1. Design the codec module structure: `src/python/<format>/` with `__init__.py`, `<format>_codec.py`
2. Implement the `probe` function: returns `True` if the file matches the format's detection signature
3. Implement the `load` function: parses a file and returns a canonical model dict
4. Implement the `create`/`write` function: serializes a model dict to the format's byte representation
5. Write minimum test suite in `tests/python/<format>/`: at least 7 tests covering probe/load/write
6. Verify: `from <format> import probe, load` must succeed in the installed package context
7. Run focused tests and confirm all pass
8. Register the format in `__all__` and update any required registry entries

## Allowed Paths

- `src/python/<format_name>/` — new codec source directory (create and write)
- `tests/python/<format_name>/` — new test directory (create and write)
- `examples/python/<format_name>/` — example files (optional, create)
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — .NET product source is out of scope for Python kickstart
- `poc-targets.yaml` — no POC state changes during kickstart
- `registry/format-registry.yaml` — registry updates require separate gate authorization
- `AGENTS.md`, `CLAUDE.md`, `GOVERNANCE.md` — governance docs are read-only
- `.supervisor/skill-registry.yaml` — skill registry is read-only here
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the format requires an external library not already available in the project's venv
- Stop if the format is too complex for a single sprint (no complete spec available)
- Stop if probe detection would conflict with an existing format's signature
- Stop if governance validators fail on the new codec
- Stop if fewer than 7 tests pass for the new codec

## Output Format

Report at the end of execution:
- New directory structure created: list of all files created
- Probe detection proof: sample invocation result
- Load round-trip proof: load a sample file and confirm model dict fields
- Test result summary: `N/N tests pass`
- Import proof: the import command and its success output

## Validation

- `governance_validators_pass` — all governance validators must pass
- `min_7_tests` — at least 7 tests across probe, load, write
- `no_new_external_imports` — no new third-party imports added beyond what's in venv
- `probe_never_raises` — probe function must never raise; returns True/False only

## Rollback

Delete the newly created format directory `src/python/<format_name>/` and
`tests/python/<format_name>/`. Confirm no other files were modified.

Transcript mention: execution produces a skill invocation transcript at
`reports/skills-r<N>/skill-transcripts/new-format-kickstart-<format>.json`.

## Sample Invocation

```
/new-format-kickstart
format_name: sylk
file_extensions: [".slk", ".sylk"]
format_spec_ref: FACT-SYLK-001
detection_signature: "ID;P" (first 4 bytes of valid SYLK file)
stdlib_module: None
```

## Changelog

- 1.0 (2026-07-02): Initial command file. Skill registered FF-PLAYBOOK-SYSTEM-001.
  Playbook contract at playbooks/format-factory/new-format-kickstart-template.md v1.1.

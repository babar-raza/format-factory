---
version: "1.1"
last-updated: "2026-06-03"
phase-available: "3+"
gate-required: null
generated_by: claude
visibility: generated
---

# /add-same-format-writer-feature

Add a same-format save/write feature to a product (FODS, FODT, Netpbm .NET or Python).
Same-format save = load from file → modify → save back to same format.

## Step 0 — Execution Manifest (run BEFORE any other step)

```
python -m tools.governance.skills_first.manifest create \
  --task-id <task_id> --agent-type CLAUDE_CODE \
  --operation "<one-line description of this invocation>" \
  --skill add-same-format-writer-feature \
  --allowed-paths src/python/<format_id>/** src/net/<format_id>/** \
  --write
```

Record the printed `execution_id`. On `ManifestError`, STOP -- do not proceed
until the manifest is created. This is what lets the tool-layer skill gate
(`tools/supervisor/coordination/hooks/skill_gate.py`) recognize this invocation
as `MANIFEST_COVERING` instead of blocking it once `check_mode:skill_resolution`
is promoted to `enforcing` for the relevant track.

## Usage

```
/add-same-format-writer-feature
```

## What This Skill Does

1. **Pre-flight**: Reads skill-registry.yaml and product-code-change-ledger.json
2. **Plan**: Identifies the target format and save-path API to implement
3. **Implement**: Adds `Save(path)` / `SaveToFile(path)` / `write_<format>` to source
4. **Round-trip test**: Creates a round-trip test (load → modify → save → reload → verify)
5. **Ledger**: Adds a `GOVERNED_PRODUCT_CHANGE` entry with pre/post SHA-256
6. **Verify**: Runs tests and confirms round-trip passes

## Constraints

- Must implement save/write that produces a valid file of the same format
- Must include at least one round-trip test (load → save → reload → compare)
- Must not silently corrupt the format on save
- Ledger entry required before any src edit

## Evidence Required

- Source file modified
- Pre/post SHA-256
- Test file with round-trip test
- Pass result
- Ledger entry ID

## Acceptance Criteria

- `Save(path)` or equivalent writes a valid file
- Reloading the saved file produces equivalent content
- At least 4 tests pass

## Allowed Paths

- `src/net/<format_id>/` or `src/python/<format_id>/` (source)
- `tests/net/<format_id>/` or `tests/python/<format_id>/` (tests)

## Forbidden Paths

- `registry/format-registry.yaml` (gate authority)
- `plans/master-plan.md` (operational authority)
- `product-capability-matrix/poc-targets.yaml` (use /update-capability-matrix)

## Rollback

1. Revert the Save/Write method addition from the source file
2. Remove the test file
3. Remove the ledger entry from `reports/r90/product-code-change-ledger.json`
4. Re-run `python tools/supervisor/validate_product_code_ledger.py` to confirm PASS

## Validation

Complete only when ledger validation passes and the round-trip test confirms save→reload equivalence.

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
with: skill_id, format_id, writer_scope, changed_files, test_results, ledger_entry_id, verdict.

## Sample Invocation

```
/add-same-format-writer-feature
# Inputs:
#   format_id: fodt
#   writer_scope: SaveToFile
#   exact_source_paths: [src/net/fodt/FodtDocument.cs]
#   exact_test_paths: [tests/net/fodt/FodtR91SaveToFileTests.cs]
#   ledger_entry_path: reports/r90/product-code-change-ledger.json
```

## Changelog

- 1.0 (2026-06-02): Initial version
- 1.1 (2026-06-03): Added frontmatter, allowed/forbidden paths, rollback, changelog (Skills R99)
- 1.2 (2026-06-03): Added validation, transcript requirement, sample invocation (Skills R101).

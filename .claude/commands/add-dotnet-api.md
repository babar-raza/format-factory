---
version: "1.2"
last-updated: "2026-06-03"
phase-available: "3+"
gate-required: "Explicit product implementation authorization for the named format"
generated_by: codex
visibility: generated
---

# /add-dotnet-api

Add or extend one bounded commercial .NET API. This command is a governed execution
contract, not standing authorization to edit `src/`.

## Required Inputs

- `format_id`
- `api_name` and user-visible behavior
- exact source paths and exact test paths
- ledger entry path supplied by the execution handoff
- focused `dotnet test` command
- evidence output directory for the active sprint

## Steps

1. Read `AGENTS.md`, `plans/master-plan.md`, `.supervisor/skill-registry.yaml`, and
   `product-capability-matrix/poc-targets.yaml`.
2. Confirm the active sprint prompt names `/add-dotnet-api`, the format, and every writable path.
3. Confirm the format's .NET track is already authorized for product work. Do not infer authorization
   from a Gate 10 or Gate 11 status.
4. Confirm the product-code ledger and its validator exist and pass before touching source. If either
   is missing, stop with `BLOCKED_GOVERNED_LEDGER_NOT_INSTALLED`.
5. Inspect the existing API, tests, and public surface. Keep the change limited to the named API.
6. Add or modify only the exact authorized files under `src/net/<format_id>/` and the exact authorized
   test files under `tests/net/<format_id>/`.
7. Add focused tests for normal behavior, one boundary case, and one invalid-input case when applicable.
8. Write the required ledger record in the exact authorized ledger path. Record skill ID, format,
   paths changed, API behavior, tests run, and whether any export path was affected.
9. Run the ledger validator, the focused `dotnet test` command, and any format-specific validation
   named by the handoff.
10. Report the changed files and validation results. Do not commit, push, publish, change gates, or set
    `commercial_product_ready: true`.

## Allowed Paths

- `src/net/<format_id>/<FormatId>Document.cs`
- `src/net/<format_id>/Model/**`
- `tests/net/<format_id>/<FormatId>R<sprint>*Tests.cs`
- `reports/r90/product-code-change-ledger.json`

## Forbidden Paths

- `src/python/**` (wrong track)
- `registry/format-registry.yaml` (gate authority)
- `plans/master-plan.md` (operational authority)
- `product-capability-matrix/poc-targets.yaml` (use /update-capability-matrix)

## Stop Conditions

- The ledger or validator is missing.
- Writable paths are not exact or exceed the handoff.
- The requested API implies a gate, release, publication, or commercial-readiness state change.
- A dogfood export is introduced without using `/add-dogfood-export`.
- Focused validation fails.

## Output Format

Report `skill_id`, format, API, changed files, ledger record path, commands run, pass/fail results,
and any stop condition. Product claims must remain bounded to tested behavior.

## Validation

The command is complete only when ledger validation and the focused .NET tests pass.

## Rollback

1. Revert source changes in `src/net/<format_id>/`
2. Remove test file `tests/net/<format_id>/<FormatId>R<sprint>*Tests.cs`
3. Remove the ledger entry from `reports/r90/product-code-change-ledger.json`
4. Re-run `python tools/supervisor/validate_product_code_ledger.py` to confirm PASS

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
with: skill_id, format_id, api_name, changed_files, test_results, ledger_entry_id, verdict.

## Sample Invocation

```
/add-dotnet-api
# Inputs provided by execution handoff:
#   format_id: fods
#   api_name: GetColumnHeaders
#   exact_source_paths: [src/net/fods/FodsDocument.cs]
#   exact_test_paths: [tests/net/fods/FodsR93GetColumnHeadersTests.cs]
#   ledger_entry_path: reports/r90/product-code-change-ledger.json
#   focused_test_command: dotnet test tests/net/fods/ --filter "FodsR93"
```

## Changelog

- 1.0 (2026-06-02): Initial R90 governed minimum viable command.
- 1.2 (2026-06-03): Added allowed/forbidden paths, rollback, transcript requirement, sample invocation (Skills R101).

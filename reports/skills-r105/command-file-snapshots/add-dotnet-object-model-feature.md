---
version: "1.0"
last-updated: "2026-06-02"
phase-available: "3+"
gate-required: "Explicit product implementation authorization for the named format"
generated_by: r92-worker
---

# /add-dotnet-object-model-feature

Add one bounded object-model feature to a commercial .NET product. This command extends
an existing parsed object model (e.g., WorkbookModel, DocumentModel, ImageModel) with
a new read or write capability.

## Required Inputs

- `format_id` (fods | fodt | netpbm)
- `feature_name` and user-visible behavior
- `model_class` — which object model class to extend
- exact source paths and exact test paths
- ledger entry path
- focused `dotnet test` command

## Steps

1. Read `plans/master-plan.md`, `.supervisor/skill-registry.yaml`, `product-capability-matrix/poc-targets.yaml`.
2. Confirm the sprint prompt names this skill, format, and exact paths.
3. Confirm product-code ledger and validator exist and pass before touching source.
4. Inspect the existing model class and public surface.
5. Add or modify only the exact authorized files under `src/net/<format_id>/`.
6. Add focused tests: normal, boundary, invalid-input.
7. Write ledger record with skill ID, format, model class, changed paths, behavior, tests run.
8. Run ledger validator and focused dotnet tests.
9. Do not commit, push, publish, change gates.

## Allowed Paths

- `src/net/<format_id>/Model/**`
- `src/net/<format_id>/<FormatId>Document.cs`
- `tests/net/<format_id>/<format_id>R<sprint>*Tests.cs`

## Forbidden Paths

- `src/python/**`
- Gate/release state files
- registry/format-registry.yaml
- plans/master-plan.md

## Stop Conditions

- Ledger or validator missing
- Writable paths exceed handoff
- Feature implies gate or commercial readiness change
- Focused tests fail

## Output Format

Report skill_id, format, feature, model class, changed files, ledger record, commands run, pass/fail.

## Validation

Complete only when ledger validation and focused dotnet tests pass.

## Rollback

1. Revert the feature addition from `src/net/<format_id>/`
2. Remove test file `tests/net/<format_id>/<format_id>R<sprint>*Tests.cs`
3. Remove the ledger entry from `reports/r90/product-code-change-ledger.json`
4. Re-run `python tools/supervisor/validate_product_code_ledger.py` to confirm PASS

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
with: skill_id, format_id, feature_name, model_class, changed_files, test_results, ledger_entry_id, verdict.

## Sample Invocation

```
/add-dotnet-object-model-feature
# Inputs provided by execution handoff:
#   format_id: netpbm
#   feature_name: ExtractChannel
#   model_class: NetpbmImage
#   exact_source_paths: [src/net/netpbm/Model/NetpbmImage.cs]
#   exact_test_paths: [tests/net/netpbm/NetpbmR103ExtractChannelTests.cs]
#   ledger_entry_path: reports/r90/product-code-change-ledger.json
```

## Changelog

- 1.0 (2026-06-02): Initial R92 governed command.
- 1.2 (2026-06-03): Added rollback, transcript requirement, sample invocation, changelog (Skills R101).

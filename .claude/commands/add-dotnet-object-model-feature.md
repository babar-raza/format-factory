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

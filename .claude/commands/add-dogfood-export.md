---
version: "1.0"
last-updated: "2026-06-02"
phase-available: "3+"
gate-required: "Explicit product implementation authorization for both named formats"
generated_by: codex
visibility: generated
---

# /add-dogfood-export

Add one bounded format-to-format export that uses a Format Factory-produced target writer.
Direct writes and third-party export backends are gaps, not completed dogfood exports.

## Required Inputs

- `source_format_id`, `target_format_id`, and `export_name`
- `target_ff_library` and target writer symbol
- exact source paths and exact test paths
- ledger entry path supplied by the execution handoff
- focused test command
- expected matrix status transition, normally `NOT_YET` or `GAP_DOGFOOD_EXTERNAL` to `IMPLEMENTED`

## Steps

1. Read `AGENTS.md`, `plans/master-plan.md`, `.supervisor/skill-registry.yaml`,
   `docs/export/dogfood-export-strategy.md`, and `product-capability-matrix/poc-targets.yaml`.
2. Confirm the active sprint prompt names `/add-dogfood-export`, both formats, the target FF writer,
   and every writable path.
3. Confirm the product-code ledger and validator exist and pass before touching source. If either is
   missing, stop with `BLOCKED_GOVERNED_LEDGER_NOT_INSTALLED`.
4. Inspect the source model and target Format Factory writer. Reuse the target writer rather than
   duplicating serialization logic.
5. Add the smallest export adapter needed to translate source model data into the target FF model.
6. Add focused tests proving the target FF writer is invoked, exported output reloads successfully,
   a meaningful value survives export, and forbidden third-party export dependencies are absent.
7. Tag the export path with `dogfood_status: IMPLEMENTED` only when the target FF writer is used.
   Otherwise record `GAP_DOGFOOD_EXTERNAL` and stop claiming completion.
8. Write the required ledger record with skill ID, source and target formats, target writer,
   changed paths, tests, and dogfood status.
9. Run the ledger validator, dependency scan, focused tests, and any format-specific reload check.
10. Report results. Matrix reconciliation is a separate `/update-capability-matrix` invocation.

## Forbidden Export Backends

- raw serialization that bypasses an available Format Factory target writer
- external format libraries such as PIL, OpenCV, `openpyxl`, or similar shortcuts
- undocumented stdlib-only writes presented as dogfood completion

## Stop Conditions

- The ledger or validator is missing.
- A Format Factory target writer does not exist.
- Paths exceed the explicit handoff.
- External or direct writing remains in the claimed dogfood path.
- Reload or focused tests fail.

## Output Format

Report source format, target format, target FF writer, changed files, ledger record, dogfood status,
dependency scan result, reload proof, and focused test result.

## Validation

`IMPLEMENTED` is valid only when a Format Factory target writer is exercised and reload proof passes.

## Changelog

- 1.0 (2026-06-02): Initial R90 governed minimum viable command.


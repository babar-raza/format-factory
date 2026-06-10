---
version: "1.2"
last-updated: "2026-06-03"
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

## Allowed Paths

- `src/python/<source_format_id>/` or `src/net/<source_format_id>/` (export adapter)
- `tests/python/<source_format_id>/` or `tests/net/<source_format_id>/` (tests)
- `reports/r90/product-code-change-ledger.json`

## Forbidden Paths

- `registry/format-registry.yaml` (gate authority)
- `plans/master-plan.md` (operational authority)
- `product-capability-matrix/poc-targets.yaml` (use /update-capability-matrix for status reconciliation)

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

## Rollback

1. Revert the export adapter from `src/python/<source_format_id>/` or `src/net/<source_format_id>/`
2. Remove the export test file
3. Remove the ledger entry from `reports/r90/product-code-change-ledger.json`
4. Re-run `python tools/supervisor/validate_product_code_ledger.py` to confirm PASS

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
with: skill_id, source_format_id, target_format_id, target_ff_library, dogfood_status, changed_files, test_results, ledger_entry_id, verdict.

## Sample Invocation

```
/add-dogfood-export
# Inputs:
#   source_format_id: ppm
#   target_format_id: pgm
#   export_name: ppm_to_pgm
#   target_ff_library: pgm (write_pgm)
#   exact_source_paths: [src/python/ppm/ppm_to_pgm.py]
#   exact_test_paths: [tests/python/ppm/test_r90_ppm_to_pgm_dogfood.py]
#   ledger_entry_path: reports/r90/product-code-change-ledger.json
```

## Changelog

- 1.0 (2026-06-02): Initial R90 governed minimum viable command.
- 1.2 (2026-06-03): Added allowed/forbidden paths, rollback, transcript requirement, sample invocation (Skills R101).

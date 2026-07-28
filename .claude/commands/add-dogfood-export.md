---
version: "1.3"
last-updated: "2026-07-17"
phase-available: "3+"
gate-required: "Explicit product implementation authorization for both named formats"
generated_by: codex
visibility: generated
---

# /add-dogfood-export

Add one bounded format-to-format export that uses a Format Factory-produced target writer.
Direct writes and third-party export backends are gaps, not completed dogfood exports.

**Not every format pair deserves a converter.** This skill previously generated a converter
for any pair it was handed. That produced 222 converters, ~45 of which are meaningless
projections (spreadsheet → 1-bit bitmap and similar), plus sys.path mutation in the generated
source. Step 0 below exists to stop both. See "What Makes a Converter Meaningful".

## Step 0 — Execution Manifest (run BEFORE the pre-execution gate below and every other step)

```
python -m tools.governance.skills_first.manifest create \
  --task-id <task_id> --agent-type CLAUDE_CODE \
  --operation "<one-line description of this invocation>" \
  --skill add-dogfood-export \
  --allowed-paths src/python/<source_format_id>/** src/net/<source_format_id>/** \
  --write
```

Record the printed `execution_id`. On `ManifestError`, STOP -- do not proceed
until the manifest is created. This is what lets the tool-layer skill gate
(`tools/supervisor/coordination/hooks/skill_gate.py`) recognize this invocation
as `MANIFEST_COVERING` instead of blocking it once `check_mode:skill_resolution`
is promoted to `enforcing` for the relevant track.

## Step 0 — Pre-Execution Gate (run BEFORE writing any converter code)

```
python -m tools.governance.skill_gates.dogfood_export_gate \
    --source-format <source_format_id> --target-format <target_format_id> \
    --target-paths <exact_source_paths>
```

| Exit | Verdict | Action |
|---|---|---|
| 0 | ALLOW | proceed to Step 1 |
| 1 | BLOCKED | **STOP.** Do not write the converter. Report the gate's `reasons` verbatim. |
| 2 | CONFIG_ERROR | **STOP** with `BLOCKED: compatibility_matrix_unavailable`. |

The gate checks two things, both of which were previously unchecked:

1. **Information-model compatibility** — the pair must have a registered classification in
   `registry/converter-compatibility-matrix.yaml`. An unregistered pair BLOCKS: a converter
   may not be created before its compatibility is assessed. `INCOMPATIBLE` BLOCKS. A
   `PROJECTION` without a `loss_note` BLOCKS.
2. **Import hygiene** — the target paths must not mutate `sys.path` (AST-checked, alias-aware).

Exit 2 is fail-closed and expected until `registry/converter-compatibility-matrix.yaml`
exists (deliverable of TC-PA-008 / validator V251). Do not work around it by skipping the
gate or by hand-writing a matrix entry for a pair you have not actually assessed.

**Re-run the gate after generation** with the same `--target-paths`. On the first run the
converter file does not exist yet, so the hygiene half has nothing to read and reports clean.
Only the post-generation run proves the emitted code is hygienic. Both runs are required.

## Step 0b — Target package must be importable as an installed package

The target FF library must import **without** any path manipulation:

```
python -c "import <target_format_id>"
```

If that fails, stop with `GAP_LIBRARY_NOT_INSTALLED` — do not "fix" it with a sys.path
insert, and do not fall back to a source-tree import. (This constraint used to live only in
`/verify-dogfood-path`, i.e. it was checked *after* the bad code was already written. It is
enforced here, at creation time, as well.)

## What Makes a Converter Meaningful

A dogfood export is meaningful when a user of the **target** format would recognise the
output as a legitimate document of that format carrying the source's information.

- **COMPATIBLE** — source and target share an information model. `dif → csv` (both tabular):
  cells map to cells. Generate it.
- **PROJECTION** — cross-domain with documented, bounded loss. `fodt → csv` extracting table
  text: legitimate *if* the loss is recorded in `loss_note`. Generate it, document the loss.
- **INCOMPATIBLE** — no semantic relationship. `fods → pbm` renders a spreadsheet as a 1-bit
  bitmap: no cell, formula, or style survives; the output is not a picture of anything a PBM
  consumer wants. **Never generate it.** A test asserting "bytes came out and reload works"
  passes for such a converter and proves nothing — reload-passes is not meaning.

If a pair feels forced, it is INCOMPATIBLE. Record the classification in the matrix and stop;
do not generate a converter to satisfy a sprint template that asked for a dogfood lane.

## Generated Code Constraints (BLOCKING)

- **No `sys.path` mutation** in generated source — no `sys.path.insert`, no `sys.path.append`,
  and no aliased form (`import sys as _sys; _sys.path.insert(...)`). The gate resolves aliases;
  renaming the import does not evade it. A shipped library that mutates `sys.path` on import
  mutates the *importing application's* interpreter state — that is not ours to change.
- **No try/except-ImportError fallback that inserts a path.** The pattern at
  `src/python/dif/interchange_document.py:24-29` (installed import → `except ImportError` →
  `sys.path.insert` → retry) is the exact defect. If the installed import fails, that is a
  packaging gap to report, not to route around.
- Import the target writer by its package name (`from <target>.<module> import <writer>`).

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
3b. **Run the Step 0 compatibility + hygiene gate. A non-zero exit ends the invocation** —
   do not proceed to step 4. Record the gate's JSON output; it is required evidence.
3c. **Run the Step 0b installed-import check** for the target format.
4. Inspect the source model and target Format Factory writer. Reuse the target writer rather than
   duplicating serialization logic.
5. Add the smallest export adapter needed to translate source model data into the target FF model.
   Generated code must satisfy "Generated Code Constraints" above.
5b. **Re-run the Step 0 gate** with `--target-paths` pointing at the file just written. This run
   is what proves the emitted code is sys.path-clean. Non-zero exit → fix the code, do not
   proceed with a passing-by-omission claim.
6. Add focused tests proving the target FF writer is invoked, exported output reloads successfully,
   a meaningful value survives export, and forbidden third-party export dependencies are absent.
   Tests must not mutate `sys.path` — the repo root is on `sys.path` via `pythonpath` in
   `pyproject.toml`, and format packages import directly via their editable installs.
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

- `BLOCKED: converter_pair_incompatible` — Step 0 gate exit 1 on compatibility.
- `BLOCKED: converter_pair_unregistered` — pair has no compatibility-matrix entry.
- `BLOCKED: compatibility_matrix_unavailable` — Step 0 gate exit 2.
- `BLOCKED: import_hygiene_violation` — generated or target source mutates `sys.path`.
- `GAP_LIBRARY_NOT_INSTALLED` — target package not importable without path manipulation.
- The ledger or validator is missing.
- A Format Factory target writer does not exist.
- Paths exceed the explicit handoff.
- External or direct writing remains in the claimed dogfood path.
- Reload or focused tests fail.

None of these are resolvable by re-running with the gate skipped. A converter that only exists
because the gate was bypassed is a defect regardless of whether its tests pass.

## Output Format

Report source format, target format, target FF writer, changed files, ledger record, dogfood status,
dependency scan result, reload proof, and focused test result.

## Validation

`IMPLEMENTED` is valid only when a Format Factory target writer is exercised and reload proof passes.

- `converter_compatibility_gate` — Step 0 gate exit 0 for the pair (pre-generation).
- `import_hygiene_gate` — Step 0 gate exit 0 re-run against the generated file (post-generation).
- `target_library_installed` — `python -c "import <target_format_id>"` succeeds with no path hack.

Reload-passes is necessary but NOT sufficient: a meaningless projection also reloads. The
compatibility classification is what distinguishes an export from a byte-shuffle.

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
- 1.3 (2026-07-17): TC-PA-009 machinery hardening (plan
  `plans/.claude/primary-purpose-the-python-starry-cupcake.md`, findings PF-001/PF-002).
  Added Step 0 compatibility + import-hygiene gate
  (`tools/governance/skill_gates/dogfood_export_gate.py`), Step 0b installed-import check
  (moved here from `/verify-dogfood-path`, which only checked it after the fact), the
  "What Makes a Converter Meaningful" rubric, generated-code constraints banning sys.path
  mutation incl. aliased forms, and gate-derived stop conditions. Rationale: at HEAD there
  were 222 converters (~45 meaningless projections) and 219 files / 406 sys.path
  occurrences under src/python — this skill had no check for either.

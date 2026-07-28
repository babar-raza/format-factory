---
version: "1.3"
last-updated: "2026-07-03"
phase-available: "3+"
gate-required: "Explicit product implementation authorization for the named format"
generated_by: codex
visibility: generated
---

# /add-dotnet-api

## Step 0 — Execution Manifest (run BEFORE the mandatory pre-check below and every other step)

```
python -m tools.governance.skills_first.manifest create \
  --task-id <task_id> --agent-type CLAUDE_CODE \
  --operation "<one-line description of this invocation>" \
  --skill add-dotnet-api \
  --allowed-paths src/net/<format_id>/** \
  --write
```

Record the printed `execution_id`. On `ManifestError`, STOP -- do not proceed
until the manifest is created. This is what lets the tool-layer skill gate
(`tools/supervisor/coordination/hooks/skill_gate.py`) recognize this invocation
as `MANIFEST_COVERING` instead of blocking it once `check_mode:skill_resolution`
is promoted to `enforcing` for `src/net/`.

## MANDATORY PRE-CHECK ZERO: Architecture-First and Work-Shape Rejection

**Before accepting the task, STOP and reject if ANY of the following match the task description:**

- "Implement all missing methods" or "add all methods referenced by tests" or "add methods from R-NNN test files"
- "Add stubs" or "return defaults for now" or "make tests pass without XML path"
- "Store values in a dictionary" or "cache in a private field" for a PERSISTENT document property
- Target file name contains `ExtendedApis`, `MissingMethods`, `Misc`, `Helpers`, `Stubs`
- Task asks to target a file that is NOT in `docs/code-quality/product-file-layout-contract.yaml`

**If task matches any of the above: STOP. Respond with `BLOCKED_INVALID_TASK_SHAPE`. Do not write code.**

**Architecture pre-flight (MANDATORY before writing any code):**
1. Identify the target domain type (FodsDocument, FodsCell, FodsSheet, etc.) — not just the file
2. Verify the target file is in the approved product file layout (`docs/code-quality/product-file-layout-contract.yaml`)
3. For any setter: plan the XML write path (which XElement.SetAttributeValue() call?) before writing
4. For any getter: plan the XML read path (which XElement.Attribute() call?) before writing
5. For any persistent property: plan the Type 4 roundtrip test before writing the setter

**If no XML read/write path can be identified: STOP. Respond with `BLOCKED_NO_XML_PATH`.**

---

## MANDATORY PRE-CHECK: QName Compliance (must complete before naming any class)

Before naming any new class:
1. Read `registry/odf-ontology/qname-to-code-map.yaml` — if an entry exists for this spec element (e.g., `table:table-cell → Table.TableCell`), use the canonical name.
2. New spec-element classes: use canonical name (Table.TableCell, NOT FodsCell). Place in `Spec/` (C#).
3. Format-prefixed names (FodsXxx, FodtXxx) ONLY in `Compat/` as thin facades.
4. Add spec_qname to every new class: C#: `public const string QName = "table:table-cell";` | also: `public const string SpecFactRef = "FACT-FODS-NNN";`
5. After writing: verify V45 validator will PASS — class outside Compat/ must NOT be format-prefixed.

Violation causes V45 governance validator to FAIL the sprint declaration.

---

Add or extend one bounded commercial .NET API. This command is a governed execution
contract, not standing authorization to edit `src/`.

## Required Inputs

- `format_id`
- `api_name` and user-visible behavior
- exact source paths and exact test paths
- ledger entry path supplied by the execution handoff
- focused `dotnet test` command
- evidence output directory for the active sprint

## Spec-Literal Requirements

Because `spec_qname_required: true` for this skill, the execution handoff MUST include at least one
`spec_fact_refs` entry linking the API to a format specification fact. Example:

```yaml
spec_fact_refs:
  - FODS-FACT-001   # ODF §3.2 — office:spreadsheet element
```

If no `spec_fact_refs` are provided, stop with `BLOCKED_SPEC_QNAME_REQUIRED`.
Spec facts are produced by `tools/specification-authority-layer/sal_master_runner.py` and stored
in `.local/sal-output/sal-facts-latest.json`. Verify the cited QName exists in that file.

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

   Note: `/test-driven-development` is available as an optional sub-procedure for Steps 6-7 (implementation + focused tests) when test-first sequencing is desired.
7. Add focused tests for normal behavior, one boundary case, and one invalid-input case.
   **For any setter that persists document state:** ALSO add a Type 4 roundtrip test:
   `SetX(value) → Save() → Load() → Assert.Equal(value, GetX())`.
   A setter WITHOUT a roundtrip test is INCOMPLETE — do not close the task.
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
- **Task is test-shaped** (methods exist only because a test references them): `BLOCKED_INVALID_TASK_SHAPE`
- **Target file not in approved layout** (`docs/code-quality/product-file-layout-contract.yaml`): `BLOCKED_FILE_NOT_IN_APPROVED_LAYOUT`
- **Target filename contains** `ExtendedApis`, `MissingMethods`, `Misc`, `Helpers`, `Stubs`: `BLOCKED_DUMPING_GROUND_FILENAME`
- **Implementation would use a private Dictionary for persistent state** (no XML path exists): `BLOCKED_NO_XML_PATH`
- **Setter without a Type 4 roundtrip test plan**: `BLOCKED_MISSING_ROUNDTRIP_TEST`

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

## Governance Validators (TC-CQGA-033-04)

The following validators from `_VALIDATOR_REGISTRY` apply to this skill:

| Rule ID | V-Number | Blocks Sprint | What it checks |
|---|---|---|---|
| `V_VALIDATE_SUSPICIOUS_FILENAMES` | V100 | YES | Dumping-ground filename patterns in product source |
| `V_VALIDATE_HISTORY_IDENTIFIERS_IN_SOURCE` | V101 | NO (WARN) | Sprint/wave/train IDs in source comments |
| `V_VALIDATE_UNGOVERNED_TODO_MARKERS` | V103 | NO (WARN) | TODO/FIXME/HACK without GAP-* or TC-* reference |
| `V_VALIDATE_GETTER_WITHOUT_PARSER_SOURCE` | V105 | YES | Public .cs getter reading from private dict field (not XML) |
| `V_VALIDATE_SETTER_WITHOUT_WRITER_PATH` | V106 | YES | Public .cs setter writing to dict only (no XML writer path) |
| `V_VALIDATE_TEST_ONLY_PUBLIC_APIS` | V107 | NO (WARN) | Public API referenced only in test files |
| `V_VALIDATE_DETACHED_PERSISTENT_STATE` | V108 | YES (new) | `Dictionary<> _field = new()` persistent state pattern |
| `V_VALIDATE_FILES_OUTSIDE_APPROVED_LAYOUT` | V109 | YES (new) | Product source file outside `product-file-layout-contract.yaml` |

**Blocking rules summary for implementors:**
- No detached dict state (V108 blocks on new .cs files)
- Getters and setters must have XML parse/write paths (V105, V106 block)
- No dumping-ground filenames (V100 blocks always)
- New files must appear in product-file-layout-contract.yaml (V109)

## Changelog

- 1.0 (2026-06-02): Initial R90 governed minimum viable command.
- 1.2 (2026-06-03): Added allowed/forbidden paths, rollback, transcript requirement, sample invocation (Skills R101).
- 1.3 (2026-07-03): TC-PQLM-007 — Added MANDATORY PRE-CHECK ZERO (work-shape rejection + architecture pre-flight); mandatory roundtrip test for setters; blocking STOP conditions for test-shaped tasks, dumping-ground filenames, files outside approved layout, dictionary-backed persistent state.
- 1.4 (2026-07-07): TC-CQGA-033-04 — Added Governance Validators section with rule IDs V_VALIDATE_SUSPICIOUS_FILENAMES through V_VALIDATE_FILES_OUTSIDE_APPROVED_LAYOUT.

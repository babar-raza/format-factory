---
version: "1.4"
last-updated: "2026-07-03"
phase-available: "3+"
gate-required: "Explicit product implementation authorization for the named format"
generated_by: codex
visibility: generated
---

# /add-python-api

## MANDATORY PRE-CHECK ZERO: Work-Shape Rejection and File-Type Check

**STOP and reject (`BLOCKED_INVALID_TASK_SHAPE`) if ANY of the following match:**

- Function is analytics-only (no class, no ODF parse/write path) AND target file is a domain model file (has class definitions). Analytics functions MUST go in `<format>_analytics.py` or `<format>_analytics_extended.py`.
- Task asks to add wildcard imports (`from .x import *`) to any module.
- Task adds `spec_qname = "..."` at module scope (not inside a class body).
- Target file contains `_misc`, `_helpers`, `_extra`, `_utils` in name.

**File-type check (MANDATORY before Step 1):**

1. Read the first 30 lines of every target file.
2. If the file contains only functions (no `class` definitions) and is named like a domain model, it is an analytics masquerade. Do NOT add to it — use the correct analytics file.
3. If target file has `from .X import *` at module scope — this is a wildcard pollution pattern. Do NOT add more wildcard imports. Report `BLOCKED_WILDCARD_IMPORT_PATTERN`.

**After implementation:**
- Verify or update `__all__` in `<format>/__init__.py` to explicitly list new public names.
- Wildcard imports in `__init__.py` are PROHIBITED — use explicit name lists only.

---

## Step 0 — Knowledge Registry Lookup (MANDATORY, before QName compliance check)

Before naming any class or modifying any Python domain model:

1. Read `.supervisor/knowledge/registry.yaml` — locate `stable_semantic_key: python_domain_model_class` (KC-PYTHON-001)
2. Read `.supervisor/knowledge/contracts/python-domain-model.yaml`
3. Verify `status: VERIFIED_CURRENT`. If STALE: run `.venv/Scripts/python .supervisor/knowledge/validate_knowledge_contracts.py --contract KC-PYTHON-001`.
4. Read `.supervisor/knowledge/examples/python-domain-model-canonical.py`
5. Follow the contract structure. Do NOT infer structure from nearby implementations.

If contract is missing or contradicted: add to `.supervisor/knowledge/gaps.yaml`, investigate, then proceed.

---

## MANDATORY PRE-CHECK: QName Compliance (must complete before naming any class)

Before naming any new class:
1. Read `registry/odf-ontology/qname-to-code-map.yaml` — if an entry exists for this spec element (e.g., `table:table-cell → Table.TableCell`), use the canonical name.
2. New spec-element classes: use canonical name (Table.TableCell, NOT FodsCell). Place in `spec/` (Python).
3. Format-prefixed names (FodsXxx, FodtXxx) ONLY in `compat.py` as thin facades.
4. Add spec_qname to every new class: Python: `spec_qname = "table:table-cell"`
5. After writing: verify V45 validator will PASS — class outside compat/ must NOT be format-prefixed.

Violation causes V45 governance validator to FAIL the sprint declaration.

---

Add or extend one bounded Python FOSS product API. This command controls implementation
shape but does not authorize source edits without an explicit handoff.

## Required Inputs

- `format_id`
- `api_name` and user-visible behavior
- exact source paths and exact test paths
- ledger entry path supplied by the execution handoff
- focused `pytest` command
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
2. Confirm the active sprint prompt names `/add-python-api`, the format, and every writable path.
3. Confirm the Python FOSS track is already authorized for the named format. Do not create a new format
   package or infer authorization from a matrix target.
4. Confirm the product-code ledger and its validator exist and pass before touching source. If either
   is missing, stop with `BLOCKED_GOVERNED_LEDGER_NOT_INSTALLED`.
5. Follow KC-PYTHON-001 contract (loaded in Step 0) for module conventions, export patterns, and test structure. Keep the change limited to the named API.
6. Add or modify only the exact authorized files under `src/python/<format_id>/` and the exact
   authorized test files under `tests/python/<format_id>/`.
7. Add focused tests for normal behavior, one boundary case, and one invalid-input case when applicable.
8. Write the required ledger record in the exact authorized ledger path. Record skill ID, format,
   paths changed, API behavior, tests run, and whether an export path was affected.
9. Run the ledger validator, the focused `pytest` command, and any format-specific validation named
   by the handoff.
10. Report changed files and validation results. Do not commit, push, publish, change gates, or alter
    release authorization.

## Allowed Paths

- `src/python/<format_id>/` (source)
- `tests/python/<format_id>/` (tests)
- `reports/r90/product-code-change-ledger.json`

## Forbidden Paths

- `src/net/**` (wrong track)
- `registry/format-registry.yaml` (gate authority)
- `plans/master-plan.md` (operational authority)
- `product-capability-matrix/poc-targets.yaml` (use /update-capability-matrix)

## Stop Conditions

- The ledger or validator is missing.
- Writable paths are not exact or exceed the handoff.
- The request creates a new package, changes a gate, or changes publication state.
- A dogfood export is introduced without using `/add-dogfood-export`.
- Focused validation fails.

## Output Format

Report `skill_id`, format, API, changed files, ledger record path, commands run, pass/fail results,
and any stop condition. Do not overclaim package readiness from focused API tests.

## Validation

The command is complete only when ledger validation and the focused Python tests pass.

## Rollback

1. Revert source changes in `src/python/<format_id>/`
2. Remove test file `tests/python/<format_id>/test_r<N>_<api_name>.py`
3. Remove the ledger entry from `reports/r90/product-code-change-ledger.json`
4. Re-run `python tools/supervisor/validate_product_code_ledger.py` to confirm PASS

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
with: skill_id, format_id, api_name, changed_files, test_results, ledger_entry_id, verdict.

## Sample Invocation

```
/add-python-api
# Inputs provided by execution handoff:
#   format_id: sylk
#   api_name: write_sylk
#   exact_source_paths: [src/python/sylk/sylk_writer.py]
#   exact_test_paths: [tests/python/sylk/test_r93_sylk_write.py]
#   ledger_entry_path: reports/r90/product-code-change-ledger.json
#   focused_test_command: python -m pytest tests/python/sylk/test_r93_sylk_write.py -v
```

## Governance Validators (TC-CQGA-033-04)

The following validators from `_VALIDATOR_REGISTRY` apply to this skill. A sprint declaration
containing output from this skill will be checked by each of these validators:

| Rule ID | V-Number | Blocks Sprint | What it checks |
|---|---|---|---|
| `V_VALIDATE_SUSPICIOUS_FILENAMES` | V100 | YES | Dumping-ground filename patterns (*Misc, *Helpers, *Utils, *Extra, *Stubs) in product source |
| `V_VALIDATE_HISTORY_IDENTIFIERS_IN_SOURCE` | V101 | NO (WARN) | Sprint/wave/train IDs in source comments |
| `V_VALIDATE_UNDOCUMENTED_PUBLIC_PYTHON_APIS` | V102 | YES (new files) | Public `def` without docstring in product .py |
| `V_VALIDATE_UNGOVERNED_TODO_MARKERS` | V103 | NO (WARN) | TODO/FIXME/HACK without GAP-* or TC-* reference |
| `V_VALIDATE_CONSTANT_RETURN_PUBLIC_METHODS` | V104 | YES (new files) | Public Python function whose body is only `return <literal>` |
| `V_VALIDATE_TEST_ONLY_PUBLIC_APIS` | V107 | NO (WARN) | Public Python API referenced only in test files |
| `V_VALIDATE_FILES_OUTSIDE_APPROVED_LAYOUT` | V109 | YES (new files) | Product source file outside `product-file-layout-contract.yaml` |

**Blocking rules summary for implementors:**
- Every new public function needs a docstring (V102 blocks on new files)
- No constant-return stub functions (V104 blocks on new files)
- No dumping-ground filenames (V100 blocks always)
- New files must appear in product-file-layout-contract.yaml (V109 blocks on new files)

## Changelog

- 1.0 (2026-06-02): Initial R90 governed minimum viable command.
- 1.2 (2026-06-03): Added allowed/forbidden paths, rollback, transcript requirement, sample invocation (Skills R101).
- 1.3 (2026-06-24): Added Step 0 knowledge registry lookup; replaced Step 5 "Inspect existing module conventions" with KC-PYTHON-001 contract reference (hidden-puzzling-rain).
- 1.4 (2026-07-03): TC-PQLM-007 — Added MANDATORY PRE-CHECK ZERO: analytics masquerade rejection, wildcard import prohibition, __all__ update requirement, file-type check before writing.
- 1.5 (2026-07-07): TC-CQGA-033-04 — Added Governance Validators section with rule IDs V_VALIDATE_SUSPICIOUS_FILENAMES through V_VALIDATE_FILES_OUTSIDE_APPROVED_LAYOUT.

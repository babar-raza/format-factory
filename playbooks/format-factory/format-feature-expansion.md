<!--
playbook_contract:
  playbook_id: format-feature-expansion
  title: "Add Feature to Existing Python FOSS Format Codec"
  version: "1.2"
  status: ACTIVE
  category: sprint_task_template
  changelog:
    - version: "1.2"
      date: "2026-07-02"
      change: "TC-PB-004 hardening — phase list updated to canonical 6 phases (read_codec,
        draft_function, write_tests, verify_import, verify_tests_pass, update_exports).
        Version bumped from 1.1 to signal content change (TC-PB-013)."
    - version: "1.1"
      date: "2026-07-01"
      change: "TC-PB-004 — added machine-readable YAML front-matter contract block."
  owner_layer: product_source
  authority: TASK_TEMPLATE
  required_inputs:
    - format_name
    - function_name
  required_skills:
    - add-python-api
    - add-roundtrip-test
  allowed_paths:
    - "src/python/<format>/"
    - "tests/python/<format>/"
    - "examples/python/<format>/"
    - "reports/"
  forbidden_paths:
    - "src/net/"
    - "poc-targets.yaml"
    - "registry/"
    - "AGENTS.md"
    - "GOVERNANCE.md"
  validation:
    - min_tests_per_function
    - governance_validators_pass
  evidence_requirements:
    - test_results
    - changed_files
    - import_proof
  rollback: "Revert source change; remove test; update __all__ and __init__.py"
  stop_conditions:
    - no_stdlib_only
    - external_dep_required
    - installed_format_breaks
  limitations:
    - "No gate approval authority"
    - "No evidence contract replacement"
    - "Sprint task templates only"
  phases:
    - read_codec
    - draft_function
    - write_tests
    - verify_import
    - verify_tests_pass
    - update_exports
-->
# Playbook: Format Feature Expansion

**Skill ID**: format-feature-expansion
**Version**: 1.0
**Created**: Sprint FORMAT-FACTORY-STANDING-MULTI-LANE-PRODUCT-FIRST-MEGA-TRAIN-001
**Authority**: This playbook describes the proven pattern used in R119–R122 sprints.

---

## Purpose

Add a new export, transform, or accessor function to an existing Python FOSS format codec.
Use this when a format already has probe/load/create/write but is missing a useful operation
(e.g., export_to_html, export_to_json, edit_paragraph, get_metadata, write_tsv).

---

## When to Use

- Format already has probe, load, and at least one export or create/write
- New function can be implemented using stdlib only (no new dependencies)
- Function is genuinely useful (produces usable output, enables editing, or completes a roundtrip)
- Tests can be written without fixtures that require external tools

---

## Required Inputs

| Input | Description |
|-------|-------------|
| `format_name` | e.g. `abw`, `gnumeric`, `tsv` |
| `codec_file` | e.g. `src/python/abw/abw_codec.py` |
| `init_file` | e.g. `src/python/abw/__init__.py` |
| `test_dir` | e.g. `tests/python/abw/` |
| `function_name` | e.g. `export_to_html` |
| `function_signature` | e.g. `(source: str | bytes | Path) -> str` |
| `capability_label` | e.g. `HTML_EXPORT` |

---

## Allowed Paths

- `src/python/<format>/` — codec and __init__ only
- `tests/python/<format>/` — new test file only
- `examples/python/<format>/` — optional example script
- `reports/<sprint-id>/` — evidence artifacts

## Forbidden Paths

- `src/net/` — no .NET changes
- `poc-targets.yaml` — propose delta only, never direct mutation
- `registry/` — propose delta only
- `AGENTS.md`, `GOVERNANCE.md`
- Any file not in the format's owned paths

---

## Implementation Steps

1. **Read the codec file** — understand existing patterns, error classes, `_read_source()` helper
2. **Draft the function** — follow the existing style:
   - Docstring with Args/Returns/Raises
   - Use existing `_read_source()` / `load()` / model helpers
   - No new external imports (stdlib only)
   - Guard against bad inputs
3. **Insert before `# Internal helpers`** or after the last public function
4. **Update `__init__.py`** — add to import list and `__all__`
5. **Write tests** in `tests/python/<format>/test_r<sprint>_<feature>.py`
   - **Import directly. Do NOT mutate `sys.path`:**
     ```python
     from <format>.<codec> import <symbol>          # any format package
     from tools.governance.skill_gates import ...   # repo tooling, if needed
     ```
     This works for **every** format with no path code, and the old
     "installed vs non-installed formats need different import patterns" rule
     was never true (verified 2026-07-17): the venv's editable-install `.pth`
     files put `src/python` itself on `sys.path`, so every package under it is
     importable by name whether or not that specific format has its own
     `.pth`. `pythonpath = ["."]` in `pyproject.toml` covers `tools.*`.
   - **Never use `from src.python.<format>...`.** It imports the same code under a
     second module identity, so `src.python.tsv.x` and `tsv.x` become different
     objects, isinstance checks fail across them, and module-level state
     duplicates. It also re-binds the package attribute and silently shadows the
     real one (this is the known dogfood namespace-conflict bug in SYLK and DIF).
   - If an import genuinely fails, that is a packaging gap to report — not
     something to route around with `sys.path.insert`.
   - Cover: returns correct type, accepts path/bytes/string, edge cases, roundtrip if applicable
6. **Run targeted tests** — all must pass before proceeding
7. **Run family tests** — no regressions
8. **(Optional) Write example script** in `examples/python/<format>/`
9. **Generate a sample output** if the function produces a file/string

---

## Tests Required

Minimum coverage per function:
- `test_returns_<type>` — correct return type
- `test_accepts_bytes` — bytes input
- `test_accepts_string_path` — string path input
- `test_accepts_path` — Path object input
- `test_<correctness>` — output contains expected values
- `test_edge_case_empty` — empty document / empty input
- `test_roundtrip` — if write function: write → read → verify

---

## Evidence Required

- `src/python/<format>/<codec>.py` — changed file
- `tests/python/<format>/test_r<sprint>_<feature>.py` — test file
- Test log showing N/N pass
- `reports/<sprint>/usable-outputs/sample-<feature>.<ext>` — sample output

---

## Rollback

If the function is wrong or tests fail:
1. `git checkout HEAD -- src/python/<format>/<codec>.py`
2. `git checkout HEAD -- src/python/<format>/__init__.py`
3. Delete the test file
4. Document the rollback in `reports/<sprint>/rollback.md`

---

## Continuation Rule

After completing this playbook:
1. Update `capability-after-proposed.json` with new PASS entry
2. Add a queue item for the next feature expansion if any remain
3. Record the completed function in `touched-files-ledger.jsonl`

---

## Known Pitfalls

| Pitfall | Prevention |
|---------|------------|
| `export_to_json(model_dict)` — function expects source not model | Always check the function signature; `load()` takes source (file/bytes/string), not a dict |
| "Installed vs non-installed import path" | **Myth — ignore it.** `src/python` is itself on `sys.path` via the editable-install `.pth` files, so `from <format>.<codec> import ...` works for every format regardless of `.egg-info`. Never `sys.path.insert`; never `from src.python.<format>...` |
| TSV header heuristic | `has_header` is True when all rows have same column count; tests must account for this |
| csv module shadowing | **Read the direction carefully:** stdlib `Lib` is at `sys.path[3]`, `src/python` at `[7]`, so plain `import csv` gets **stdlib csv, not ours** — our csv package is unreachable under its own name. The danger is the reverse fix: a `sys.path.insert(0, .../src/python)` makes ours win, and ours has no `reader`/`writer`/`DictReader`, which breaks stdlib csv for the whole process. Do not "fix" csv imports with a path insert |
| ABW DOCTYPE stripping | `_strip_doctype` returns str in some versions; use `_parse_xml` on its output |

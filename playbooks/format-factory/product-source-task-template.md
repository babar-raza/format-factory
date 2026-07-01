<!--
playbook_contract:
  playbook_id: product-source-task
  title: "Execute Bounded Product Source Change to Existing Python FOSS Codec"
  version: "1.1"
  status: ACTIVE
  category: sprint_task_template
  owner_layer: product_source
  authority: TASK_TEMPLATE
  required_inputs:
    - format_name
    - test_sprint
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
    - draft_change
    - write_tests
    - verify_import
    - verify_tests_pass
    - update_exports
    - supervisor_log
-->
# Playbook: Product Source Task

**Skill ID**: product-source-task
**Version**: 1.0
**Authority**: Derived from ABW, Gnumeric, TSV, NDJSON sprint patterns.

---

## Purpose

Execute a single bounded product source change to an existing Python FOSS codec.
Use for any of: adding a function, fixing a bug, improving an export, adding an accessor.

This is the most common task type in the Format Factory product train.

---

## When to Use

- Format already has at least probe + load
- Change is bounded to `src/python/<format>/` only
- No new external dependencies needed
- One clear function to add or fix

---

## Task Classification

| Classification | Description |
|---------------|-------------|
| `PRODUCT_SOURCE_PATCH_BOUNDED` | New function or fix within existing codec |
| `FORMAT_FEATURE_EXPANSION` | New export/transform/accessor |
| `VERTICAL_SLICE_ADVANCEMENT` | Pushing a format toward probe+load+write+roundtrip |

---

## Required Inputs

| Input | Description |
|-------|-------------|
| `format_name` | e.g. `abw`, `ndjson` |
| `function_name` | e.g. `export_to_csv`, `append_record` |
| `codec_file` | e.g. `src/python/abw/abw_codec.py` |
| `init_file` | e.g. `src/python/abw/__init__.py` |
| `test_sprint` | e.g. `r123` (for test file naming) |

---

## Implementation Steps

1. **Read the codec file** — understand `_read_source()`, error classes, existing patterns
2. **Determine insertion point** — insert before `# Internal helpers` or after last public function
3. **Draft function**:
   - Docstring with Args/Returns/Raises
   - Use `_read_source()` if accepting file/bytes/string input
   - Call `load()` internally if processing document content
   - Raise typed errors (not bare exceptions)
   - No new imports beyond stdlib
4. **Update `__init__.py`** — add to both import list and `__all__`
5. **Write test file** `tests/python/<format>/test_<sprint>_<function>.py`
   - Import pattern depends on installation status:
     - **Installed** (has .egg-info): `sys.path.insert(0, str(_REPO / "src" / "python"))` → `from <format>.<codec> import ...`
     - **Not installed**: `sys.path.insert(0, str(_REPO))` → `from src.python.<format>.<codec> import ...`
6. **Run targeted tests** — all must pass
7. **Run family tests** — `tests/python/` — no regressions

---

## Minimum Tests Per Function

- `test_returns_<type>` — correct return type
- `test_accepts_bytes` — bytes input accepted
- `test_accepts_string_path` — string path input accepted
- `test_accepts_path` — Path object input accepted
- `test_<correctness>` — output contains expected data
- `test_edge_case_empty` — empty/minimal document handled
- `test_error_raises` — invalid input raises typed error
- `test_package_import` — importable from package
- `test_in_all` — present in `__all__`

---

## Import Status Reference

| Format | Installed? | Import Pattern |
|--------|-----------|----------------|
| abw | Yes (.egg-info) | `sys.path.insert(0, _REPO/"src"/"python")` → `from abw.abw_codec import ...` |
| gnumeric | Yes (.egg-info) | `sys.path.insert(0, _REPO/"src"/"python")` → `from gnumeric.gnumeric_codec import ...` |
| tsv | No | `sys.path.insert(0, _REPO)` → `from src.python.tsv.tsv_parser import ...` |
| ndjson | No | `sys.path.insert(0, _REPO)` → `from src.python.ndjson.ndjson_codec import ...` |
| fodg | Yes (.egg-info) | `sys.path.insert(0, _REPO/"src"/"python")` → `from fodg.fodg_codec import ...` |

---

## Known Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Wrong `source` type | Check if function uses `load(source)` or `_read_source(source)`; never pass model dicts to source-accepting functions |
| CSV module shadowing | Never `import csv` in gnumeric/ods/fods tests without conftest pin; tsv_parser avoids csv module entirely |
| ABW `_strip_doctype` return type | Returns `str`; pass to `_parse_xml` which accepts `str` |
| Missing `__init__.py` update | Always add both to import list AND `__all__` |
| `tests_run` schema | Must be integer count, NOT a list |

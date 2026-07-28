<!--
playbook_contract:
  playbook_id: new-format-kickstart
  title: "Start Brand-New Python FOSS Format from Scratch"
  version: "1.1"
  status: ACTIVE
  category: sprint_task_template
  owner_layer: product_source
  authority: TASK_TEMPLATE
  required_inputs:
    - format_name
    - file_extensions
    - format_spec_ref
    - detection_signature
    - stdlib_module
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
  rollback: "Delete new format directory; remove from __init__.py and __all__"
  stop_conditions:
    - no_stdlib_only
    - external_dep_required
    - format_too_complex_for_single_sprint
  limitations:
    - "No gate approval authority"
    - "No evidence contract replacement"
    - "Sprint task templates only"
  phases:
    - design_codec_structure
    - create_exceptions_module
    - implement_probe
    - implement_load
    - implement_create
    - implement_write
    - write_tests
    - verify_import
    - verify_tests_pass
-->
# Playbook: New Format Kickstart

**Skill ID**: new-format-kickstart
**Version**: 1.0
**Authority**: Proven pattern from NDJSON, FODG, TSV acquisitions.

---

## Purpose

Start a brand-new Python FOSS format from scratch.
Use when a format has NO existing codec in `src/python/`.

Produces the minimum slice: probe → load → write → tests.

See `docs/governance/python-library-standard.md` §2.4 (Exceptions) for the full
exception-hierarchy contract this template implements.

---

## When to Use

- Format has no existing `src/python/<format>/` directory
- Format is simple enough for stdlib-only implementation (no complex binary encoding)
- At least a probe function can be written from known format signatures
- Tests can be written without external fixtures/tools

---

## Required Inputs

| Input | Description |
|-------|-------------|
| `format_name` | e.g. `toml`, `ini`, `msgpack` |
| `file_extensions` | e.g. `.toml`, `.ini` |
| `format_spec_ref` | URL or description of format spec |
| `detection_signature` | How to detect the format (magic bytes, header text, MIME type) |
| `stdlib_module` | e.g. `json`, `xml.etree`, `gzip` |

---

## Allowed Paths

- `src/python/<format>/` — codec and __init__ only
- `tests/python/<format>/` — one test file per sprint
- `reports/<sprint>/new-formats/` — acquisition report

## Forbidden Paths

- `src/net/` — no .NET changes
- `poc-targets.yaml` — propose delta only
- `registry/` — propose delta only

---

## Implementation Steps

1. **Create directory**: `src/python/<format>/`
2. **Create `__init__.py`** — module header, imports, `__all__`, `__version__`
3. **Create `exceptions.py` FIRST** — before the codec module. This is the single
   source of truth for the format's error hierarchy:
   ```python
   try:
       from _shared._shared_exceptions import FormatFactoryError
   except ImportError:
       FormatFactoryError = Exception

   class <Format>Error(FormatFactoryError):
       """Base exception for all <format> format errors."""

   class <Format>ParseError(<Format>Error):
       """Raised when a <format> file cannot be parsed."""

   class <Format>WriteError(<Format>Error):
       """Raised when a <format> file cannot be written."""  # only if format is writable
   ```
4. **Create `<format>_codec.py`** with:
   - Import error classes: `from .exceptions import <Format>Error, <Format>ParseError`
     (and `<Format>WriteError` if writable).
     **NEVER define `<Format>Error`-named classes here — `exceptions.py` is the
     single source of truth.**
   - `MAX_FILE_SIZE = 64 * 1024 * 1024`
   - `_read_source(source) -> bytes` helper (Path / str / bytes support)
   - `_check_size(path) -> None`
   - `probe_<format>(source) -> bool` — never raises, returns bool
   - `load_<format>(source) -> list | dict` — raises on bad input
   - `write_<format>(records, dest)` — if writable format
5. **Create `tests/python/<format>/__init__.py`** (empty)
6. **Write test file** `tests/python/<format>/test_r<sprint>_<format>_codec.py`
   - Import the package by name. **Do NOT mutate `sys.path`:**
     ```python
     from <format>.<format>_codec import probe_<format>, load_<format>, write_<format>
     ```
     No path code is needed: the venv's editable-install `.pth` files put
     `src/python` on `sys.path`, so a new package under `src/python/<format>/`
     is importable by name as soon as it exists (verified 2026-07-17 — the old
     "non-installed formats need `sys.path.insert`" rule was never true).
     `pythonpath = ["."]` in `pyproject.toml` covers `tools.*` imports.
   - **Never use `from src.python.<format>...`** — it creates a second module
     identity for the same code and silently shadows the real package attribute.
   - This is the same import the skill's own acceptance check uses
     (`from <format> import probe, load` in the installed-package context), so a
     test that needs a path hack to pass is a test that is not proving the
     package works.
7. **Run tests** — all must pass
   - Then confirm hygiene:
     `python -m tools.governance.skill_gates.import_hygiene src/python/<format> tests/python/<format>`
     (exit 0 required; AST-based and alias-aware, so `import sys as _sys` does not evade it)

---

## Detection Patterns by Format Type

| Format Type | Detection Method |
|-------------|-----------------|
| JSON-based | Try `json.loads(first_line)` |
| XML-based | Check for XML namespace or root element in first 4KB |
| Gzip-compressed | Check magic bytes `\x1f\x8b` |
| Text line-based | Check first line matches expected pattern |
| Binary | Check magic bytes (format-specific) |

---

## Minimum Tests Required

- `test_probe_returns_true` — valid input
- `test_probe_returns_false_on_garbage` — malformed input
- `test_probe_never_raises` — any input, no exception
- `test_load_returns_expected_type` — list or dict
- `test_load_correct_count` — right number of records
- `test_empty_returns_empty` — empty input handled
- `test_roundtrip` — write then load produces same data (if writable)

---

## Known Pitfalls

| Pitfall | Prevention |
|---------|------------|
| "Installed vs non-installed path" | **Myth — ignore it.** `src/python` is on `sys.path` via the editable-install `.pth` files, so a brand-new `src/python/<format>/` imports as `from <format>.<format>_codec import ...` immediately. Never `sys.path.insert`; never `from src.python.<format>...` (second module identity) |
| Name collides with stdlib / a popular package | Run `python -m tools.governance.skill_gates.format_name_gate --format-name <format>` **before** creating the directory. `src/python/csv/` shows why: the name is unfixable once taken — stdlib wins by path order (our package unreachable), and forcing ours to win hijacks stdlib csv process-wide |
| Over-claiming capabilities | Only claim probe/load/write PASS when tests exist |
| External spec dependency | Note spec URL in module docstring; cache locally if needed |
| Binary format complexity | Start with probe only if full parser is risky |
| Unsafe JSON output | NEVER use manual `.replace("\\", "\\\\")` chains — use `json.dumps()` |
| Unsafe HTML output | NEVER use raw f-string `<td>{value}</td>` — use `html.escape(str(value))` |
| Error class duplication | NEVER define `<Format>Error` in the codec file — always import from `.exceptions`. Two classes with the same name in different files silently shadow each other via star-imports. |

## Output Safety Defaults (MA-SYSTEM-WIDE-2026-07-04 — mandatory)

All export functions emitting JSON, HTML, or XML must use safe primitives. Validators V134/V135/V136 enforce this.

**Python JSON — always use `json.dumps()`:**
```python
import json
def to_json_line(record: dict) -> str:
    return json.dumps(record)  # handles all escaping correctly
```

**Python HTML — always use `html.escape()`:**
```python
from html import escape
def to_html_table(records: list[dict], headers: list[str]) -> str:
    lines = ["<table>", "<thead><tr>"]
    for h in headers:
        lines.append(f"  <th>{escape(h)}</th>")
    lines.append("</tr></thead><tbody>")
    for row in records:
        lines.append("  <tr>")
        for h in headers:
            lines.append(f"    <td>{escape(str(row.get(h, '')))}</td>")
        lines.append("  </tr>")
    lines.append("</tbody></table>")
    return "\n".join(lines)
```

---

## Evidence Required

- `src/python/<format>/` — codec + __init__ + exceptions
- `tests/python/<format>/test_r<sprint>_<format>_codec.py`
- Test log showing N/N pass

# Playbook: New Format Kickstart

**Skill ID**: new-format-kickstart
**Version**: 1.0
**Authority**: Proven pattern from NDJSON, FODG, TSV acquisitions.

---

## Purpose

Start a brand-new Python FOSS format from scratch.
Use when a format has NO existing codec in `src/python/`.

Produces the minimum slice: probe → load → write → tests.

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
3. **Create `<format>_codec.py`** with:
   - Error classes: `<Format>Error`, `<Format>ParseError`
   - `MAX_FILE_SIZE = 64 * 1024 * 1024`
   - `_read_source(source) -> bytes` helper (Path / str / bytes support)
   - `_check_size(path) -> None`
   - `probe_<format>(source) -> bool` — never raises, returns bool
   - `load_<format>(source) -> list | dict` — raises on bad input
   - `write_<format>(records, dest)` — if writable format
4. **Create `tests/python/<format>/__init__.py`** (empty)
5. **Write test file** `tests/python/<format>/test_r<sprint>_<format>_codec.py`
   - Use non-installed import pattern:
     ```python
     sys.path.insert(0, str(_REPO))
     from src.python.<format>.<format>_codec import ...
     ```
6. **Run tests** — all must pass

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
| Installed vs non-installed path | New formats never pip-installed; use `sys.path.insert(0, str(_REPO))` + `from src.python.<format>...` |
| Over-claiming capabilities | Only claim probe/load/write PASS when tests exist |
| External spec dependency | Note spec URL in module docstring; cache locally if needed |
| Binary format complexity | Start with probe only if full parser is risky |

---

## Evidence Required

- `src/python/<format>/` — codec + __init__
- `tests/python/<format>/test_r<sprint>_<format>_codec.py`
- Test log showing N/N pass

---
artifact_id: gnumeric-prototype-readme
artifact_type: prototype
path: prototypes/by-format/gnumeric/README.md
format_id: gnumeric
product_family: cells
visibility: internal
publish_allowed: false
license: Apache-2.0
generated_by: claude-sonnet-4-6
generated_at: "2026-07-01"
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 4 prototype README for Gnumeric parser. 13/13 prototype tests pass."
---

# Gnumeric Parser Prototype — Gate 4

**Format:** Gnumeric Spreadsheet (.gnumeric)
**Gate:** Gate 4 (Parser Prototype)
**Status:** `gate4_passed`
**Evidence type:** STANDALONE_PROTOTYPE
**Validation:** 13/13 PASS

---

## IMPORTANT — Prototype Scope

This is a **Gate 4 prototype only**. It is NOT product code.

- This prototype explores parsing feasibility for Gnumeric's gzip-compressed XML format.
- Gate 4 proves the format can be parsed; it does NOT imply production quality.
- No neutral model (Gate 5+), no write support, no release authorization.
- Product source at `src/python/gnumeric/` is the implementation authority.

---

## gate4_wrapper Manifest

```yaml
gate4_wrapper:
  format_id: gnumeric
  evidence_type: STANDALONE_PROTOTYPE
  delegated_source: null
  delegated_symbols: []
  sample_corpus:
    - samples/by-format/gnumeric/
  valid_probe: prototypes/by-format/gnumeric/gnumeric_parser.py::parse_gnumeric
  invalid_probe: parse_gnumeric with non-gzip bytes raises GnumericParseError
  limitations:
    - Formulas captured as raw string only; no evaluation
    - Conditional formatting, chart objects, and macros not extracted
    - No write or round-trip support
    - Gzip magic bytes (0x1f 0x8b) required; non-gzip input rejected
    - Gate 4 scope only — not for production pipelines
  test_paths:
    - tests/skills/test_gnumeric_gate4_prototype.py
  source_revision: null
  compatibility_version: null
gate_3_corpus: samples/by-format/gnumeric/
verdict: GATE4_PASSED
```

---

## Files

| File | Purpose |
|---|---|
| `gnumeric_parser.py` | Gate 4 prototype parser — `parse_gnumeric(source)` |
| `README.md` | This file |

## Parser Return Structure

`parse_gnumeric(source) -> dict`

Returns:
- `is_gnumeric: bool`
- `sheet_count: int`
- `sheets: list[dict]` — each with name, row_count, cell_count, cells
- `cell_count: int`
- `error: str | None`

## Format Details

Gnumeric files are gzip-compressed XML with namespace `http://www.gnumeric.org/v10.dtd`.
Magic bytes: `\x1f\x8b` (gzip). The parser decompresses first, then parses XML.

Invalid magic (non-gzip) is rejected immediately. Wrong namespace or root tag
raises `GnumericParseError` or sets `error`.

## Gate 3 Corpus

Samples at `samples/by-format/gnumeric/`. All valid .gnumeric files produce `is_gnumeric=True`.

## Limitations (Gate 4)

- Formulas stored as raw strings; no formula evaluation
- Charts, macros, and pivot tables not extracted
- No write capability
- Not for production use

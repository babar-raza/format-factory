---
artifact_id: abw-prototype-readme
artifact_type: prototype
path: prototypes/by-format/abw/README.md
format_id: abw
product_family: words
visibility: internal
publish_allowed: false
license: Apache-2.0
generated_by: claude-sonnet-4-6
generated_at: "2026-07-01"
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 4 prototype README for ABW parser. 14/14 prototype tests pass."
---

# ABW Parser Prototype — Gate 4

**Format:** AbiWord Document (ABW)
**Gate:** Gate 4 (Parser Prototype)
**Status:** `gate4_passed`
**Evidence type:** STANDALONE_PROTOTYPE
**Created:** initial acquisition sprint
**Validation:** 14/14 PASS

---

## IMPORTANT — Prototype Scope

This is a **Gate 4 prototype only**. It is NOT product code.

- This prototype explores parsing feasibility for AbiWord XML (AWML 1.0).
- Gate 4 proves the format can be parsed; it does NOT imply production quality.
- No neutral model (Gate 5+), no writer (Gate 6+), no release authorization.
- Product source at `src/python/abw/` is the implementation authority.

---

## gate4_wrapper Manifest

```yaml
gate4_wrapper:
  format_id: abw
  evidence_type: STANDALONE_PROTOTYPE
  delegated_source: null
  delegated_symbols: []
  sample_corpus:
    - samples/by-format/abw/
  valid_probe: prototypes/by-format/abw/abw_parser.py::parse_abw
  invalid_probe: parse_abw with non-XML bytes raises AbwParseError
  limitations:
    - DTD at http://www.abisource.com/awml.dtd is unreachable; DTD loading disabled
    - No revision tracking, embedded images, or comment extraction
    - No formula, table of contents, or metadata extraction
    - Parser handles AWML 1.0 only; newer versions may differ
    - Not for production use; no size guard beyond default XML parser behavior
  test_paths:
    - tests/skills/test_abw_gate4_prototype.py
  source_revision: null
  compatibility_version: null
gate_3_corpus: samples/by-format/abw/
verdict: GATE4_PASSED
```

---

## Files

| File | Purpose |
|---|---|
| `abw_parser.py` | Gate 4 prototype parser — `parse_abw(source)` |
| `README.md` | This file |

## Parser Return Structure

`parse_abw(source) -> dict`

```python
{
  "is_abw": bool,           # True when root tag is <abiword>
  "section_count": int,     # Number of <section> elements
  "paragraph_count": int,   # Number of <p> elements
  "paragraphs": [str],      # Text content of each <p>
  "error": str | None,      # None on success
}
```

On fatal error: `{"is_abw": False, ..., "error": "description"}`.
Invalid input (non-XML bytes, wrong root tag) sets `error` and does not raise.

## Gate 3 Corpus

Samples at `samples/by-format/abw/`. Valid files produce `is_abw=True`.
Invalid/non-ABW input produces `is_abw=False` with error set.

## Limitations (Gate 4)

- No writer / round-trip capability
- No revision history or embedded binary content
- DTD URL unreachable (server down since acquisition) — safe because ElementTree
  does not fetch external DTDs
- No production API; do not use in production pipelines

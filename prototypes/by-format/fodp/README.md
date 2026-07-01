---
artifact_id: fodp-prototype-readme
artifact_type: prototype
path: prototypes/by-format/fodp/README.md
format_id: fodp
product_family: presentations
visibility: internal
publish_allowed: false
license: Apache-2.0
generated_by: claude-sonnet-4-6
generated_at: "2026-07-01"
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 4 prototype README for FODP parser. 12/12 prototype tests pass."
---

# FODP Parser Prototype — Gate 4

**Format:** Flat OpenDocument Presentation (FODP)
**Gate:** Gate 4 (Parser Prototype)
**Status:** `gate4_passed`
**Evidence type:** STANDALONE_PROTOTYPE
**Validation:** 12/12 PASS

---

## IMPORTANT — Prototype Scope

This is a **Gate 4 prototype only**. It is NOT product code.

- This prototype explores parsing feasibility for the FODP flat-XML ODF presentation format.
- Gate 4 proves the format can be parsed; it does NOT imply production quality.
- No neutral model (Gate 5+), no writer, no release authorization.
- Product source at `src/python/fodp/` is the implementation authority.

---

## gate4_wrapper Manifest

```yaml
gate4_wrapper:
  format_id: fodp
  evidence_type: STANDALONE_PROTOTYPE
  delegated_source: null
  delegated_symbols: []
  sample_corpus:
    - samples/by-format/fodp/
  valid_probe: prototypes/by-format/fodp/fodp_parser.py::parse_fodp
  invalid_probe: parse_fodp with wrong MIME raises FodpParseError or returns error
  limitations:
    - No slide animation, transition, or embedded media extraction
    - Presentation master styles not deeply parsed
    - No write or round-trip support
    - ODF flat-XML structure only; ZIP-based ODP not handled here
    - Gate 4 scope only — not for production pipelines
  test_paths:
    - tests/skills/test_fodp_gate4_prototype.py
  source_revision: null
  compatibility_version: null
gate_3_corpus: samples/by-format/fodp/
verdict: GATE4_PASSED
```

---

## Files

| File | Purpose |
|---|---|
| `fodp_parser.py` | Gate 4 prototype parser — `parse_fodp(source)` |
| `README.md` | This file |

## Parser Return Structure

`parse_fodp(source) -> dict`

Returns a dict with:
- `is_fodp: bool`
- `slide_count: int`
- `slides: list[dict]` — each with title, text content, shape count
- `error: str | None`

Invalid MIME / wrong root element raises `FodpParseError` or sets `error`.

## Gate 3 Corpus

Samples at `samples/by-format/fodp/`. All valid files produce `is_fodp=True`.
Invalid/non-FODP input is rejected.

## Limitations (Gate 4)

- No animation, transition, media embedding
- Shallow content extraction — text and shape counts only
- No write capability
- Not for production use

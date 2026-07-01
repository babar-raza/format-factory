---
artifact_id: fodg-prototype-readme
artifact_type: prototype
path: prototypes/by-format/fodg/README.md
format_id: fodg
product_family: graphics
visibility: internal
publish_allowed: false
license: Apache-2.0
generated_by: claude-sonnet-4-6
generated_at: "2026-07-01"
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 4 prototype README for FODG parser. 12/12 prototype tests pass."
---

# FODG Parser Prototype — Gate 4

**Format:** Flat OpenDocument Graphics (FODG)
**Gate:** Gate 4 (Parser Prototype)
**Status:** `gate4_passed`
**Evidence type:** STANDALONE_PROTOTYPE
**Validation:** 12/12 PASS

---

## IMPORTANT — Prototype Scope

This is a **Gate 4 prototype only**. It is NOT product code.

- This prototype explores parsing feasibility for the FODG flat-XML ODF graphics format.
- Gate 4 proves the format can be parsed; it does NOT imply production quality.
- No neutral model (Gate 5+), no writer, no release authorization.
- Product source at `src/python/fodg/` is the implementation authority.

---

## gate4_wrapper Manifest

```yaml
gate4_wrapper:
  format_id: fodg
  evidence_type: STANDALONE_PROTOTYPE
  delegated_source: null
  delegated_symbols: []
  sample_corpus:
    - samples/by-format/fodg/
  valid_probe: prototypes/by-format/fodg/fodg_parser.py::parse_fodg
  invalid_probe: parse_fodg with non-FODG XML returns error or raises FodgParseError
  limitations:
    - Shape geometry, gradients, and embedded bitmaps not extracted
    - Connector/arrow types not distinguished
    - No write or round-trip support
    - ODF flat-XML structure only; ZIP-based ODG not handled here
    - Gate 4 scope only — not for production pipelines
  test_paths:
    - tests/skills/test_fodg_gate4_prototype.py
  source_revision: null
  compatibility_version: null
gate_3_corpus: samples/by-format/fodg/
verdict: GATE4_PASSED
```

---

## Files

| File | Purpose |
|---|---|
| `fodg_parser.py` | Gate 4 prototype parser — `parse_fodg(source)` |
| `README.md` | This file |

## Gate 3 Corpus

Samples at `samples/by-format/fodg/`. Valid files produce successful parse result.
Invalid / non-FODG content is rejected.

## Limitations (Gate 4)

- Shape geometry and SVG-compatible attributes not deeply parsed
- No write capability
- Not for production use

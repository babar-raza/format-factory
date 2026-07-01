---
artifact_id: xpm-prototype-readme
artifact_type: prototype
path: prototypes/by-format/xpm/README.md
format_id: xpm
product_family: images
visibility: internal
publish_allowed: false
license: Apache-2.0
generated_by: claude-sonnet-4-6
generated_at: "2026-07-01"
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: >
  Gate 4 prototype README for XPM parser. Valid: 3/3 PASS. Invalid: 1/1 rejected.
---

# XPM Parser Prototype — Gate 4

**Format:** X PixMap (XPM3)
**Gate:** Gate 4 (Parser Prototype)
**Evidence type:** STANDALONE_PROTOTYPE
**Status:** gate4_passed
**Validation:** 3 valid PASS, 1 invalid correctly rejected

---

## IMPORTANT — Prototype Scope

This is a **Gate 4 prototype only**. It is NOT product code.

- This prototype explores XPM3 parsing feasibility.
- Gate 4 proves the format can be parsed; it does NOT imply production quality.
- No neutral model (Gate 5+), no writer, no release authorization.
- No src/python/xpm/ exists yet — this is the first parser implementation.
- Bounded input: max 4096×4096, max 256 colors, max 16 chars/pixel.

---

## gate4_wrapper Manifest

```yaml
gate4_wrapper:
  format_id: xpm
  evidence_type: STANDALONE_PROTOTYPE
  delegated_source: null
  delegated_symbols: []
  sample_corpus:
    - samples/by-format/xpm/1x1-red.xpm
    - samples/by-format/xpm/2x2-checker.xpm
    - samples/by-format/xpm/3x1-rgb.xpm
    - samples/by-format/xpm/invalid-no-magic.xpm
  valid_probe: prototypes/by-format/xpm/xpm_parser.py::parse_xpm3
  invalid_probe: parse_xpm3 on non-XPM file raises XpmParseError
  limitations:
    - XPM3 only (not XPM1/XPM2)
    - No production namespace or API
    - Escaped quotes in pixel data not supported (Gate 4 scope)
    - Per-pixel color lookup not performed (colors extracted, not applied)
    - Max 4096x4096, max 256 colors, max 16 chars/pixel
    - No write/round-trip support
    - Not for production pipelines
  test_paths:
    - tests/skills/test_xpm_gate4_prototype.py
  source_revision: null
  compatibility_version: null
gate_3_corpus: samples/by-format/xpm/
verdict: GATE4_PASSED
```

---

## Files

| File | Purpose |
|---|---|
| `xpm_parser.py` | Gate 4 prototype — `parse_xpm3(source)`, `is_xpm3(source)` |
| `README.md` | This file |

## Parser Return Structure

`parse_xpm3(source) -> dict`

```python
{
  "format_id": "xpm",
  "width": int,
  "height": int,
  "ncolors": int,
  "chars_per_pixel": int,
  "colors": [{"symbol": str, "color_type": str, "color_value": str}],
  "pixel_rows": [str],      # raw pixel row strings (height rows)
  "error": None             # None on success
}
```

Raises `XpmParseError` on invalid magic, malformed dimensions, or truncated data.

## Gate 3 Corpus

| Sample | Content |
|---|---|
| 1x1-red.xpm | 1×1 pixel, single red color |
| 2x2-checker.xpm | 2×2 checker pattern, 2 colors |
| 3x1-rgb.xpm | 3×1 pixels, 3 colors |
| invalid-no-magic.xpm | Plain text, no XPM magic → rejected |

## Security Notes (Gate 4)

- `/* XPM */` magic verified before any parsing
- Dimensions checked: width/height ≤ 4096, ncolors ≤ 256, chars_per_pixel ≤ 16
- Truncated color tables and pixel rows raise XpmParseError
- 10 MB file size limit
- Not for untrusted input in production

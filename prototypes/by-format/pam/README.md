---
artifact_id: pam-prototype-readme
artifact_type: prototype
path: prototypes/by-format/pam/README.md
format_id: pam
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
  Gate 4 prototype README for PAM parser. Valid: 3/3 PASS. Invalid: 1/1 rejected.
---

# PAM Parser Prototype — Gate 4

**Format:** Portable Arbitrary Map (PAM / P7)
**Gate:** Gate 4 (Parser Prototype)
**Evidence type:** STANDALONE_PROTOTYPE
**Status:** gate4_passed
**Validation:** 3 valid PASS, 1 invalid correctly rejected

---

## IMPORTANT — Prototype Scope

This is a **Gate 4 prototype only**. It is NOT product code.

- This prototype explores PAM P7 parsing feasibility.
- Gate 4 proves the format can be parsed; it does NOT imply production quality.
- No neutral model (Gate 5+), no writer, no release authorization.
- No src/python/pam/ exists yet — this is the first parser implementation.
- Bounded input: max 4096×4096 pixels, max depth 4.

---

## gate4_wrapper Manifest

```yaml
gate4_wrapper:
  format_id: pam
  evidence_type: STANDALONE_PROTOTYPE
  delegated_source: null
  delegated_symbols: []
  sample_corpus:
    - samples/by-format/pam/1x1-gray.pam
    - samples/by-format/pam/1x1-rgb.pam
    - samples/by-format/pam/2x2-bw.pam
    - samples/by-format/pam/invalid-wrong-magic.pam
  valid_probe: prototypes/by-format/pam/pam_parser.py::parse_pam
  invalid_probe: parse_pam on non-P7 file raises PamParseError
  limitations:
    - P7 magic required; P1–P6 PBM/PGM/PPM not handled
    - Max 4096x4096, max depth 4, max MAXVAL 65535
    - Raster pixel values not decoded (only byte count validated)
    - No write/round-trip support
    - Not for production pipelines
  test_paths:
    - tests/skills/test_pam_gate4_prototype.py
  source_revision: null
  compatibility_version: null
gate_3_corpus: samples/by-format/pam/
verdict: GATE4_PASSED
```

---

## Files

| File | Purpose |
|---|---|
| `pam_parser.py` | Gate 4 prototype — `parse_pam(source)`, `is_pam(source)` |
| `README.md` | This file |

## Parser Return Structure

`parse_pam(source) -> dict`

```python
{
  "format_id": "pam",
  "width": int,
  "height": int,
  "depth": int,
  "maxval": int,
  "tupltype": str | None,
  "bytes_per_sample": int,   # 1 if maxval<=255, 2 otherwise
  "raster_size": int,        # expected raster bytes
  "raster_actual_bytes": int,
  "raster_length_valid": bool,
  "error": None
}
```

Raises `PamParseError` on invalid magic, missing required header fields, or type errors.

## PAM Header Fields (P7 format)

Required: `WIDTH`, `HEIGHT`, `DEPTH`, `MAXVAL`
Optional: `TUPLTYPE` (e.g., GRAYSCALE, RGB, RGB_ALPHA, BLACKANDWHITE)
Terminated by: `ENDHDR` on its own line

## Gate 3 Corpus

| Sample | Content |
|---|---|
| 1x1-gray.pam | 1×1 grayscale pixel (GRAYSCALE, DEPTH=1) |
| 1x1-rgb.pam | 1×1 RGB pixel (RGB, DEPTH=3) |
| 2x2-bw.pam | 2×2 black-and-white (GRAYSCALE, DEPTH=1) |
| invalid-wrong-magic.pam | P9 magic → rejected |

## Security Notes (Gate 4)

- P7 magic (`P7\n`) verified before any header parsing
- Header lines capped at 100 to prevent infinite loops
- Dimensions bounded: width/height ≤ 4096, depth ≤ 4
- 50 MB file size limit
- Raster length validated (bytes after ENDHDR = width × height × depth × bytes_per_sample)
- Not for untrusted input in production

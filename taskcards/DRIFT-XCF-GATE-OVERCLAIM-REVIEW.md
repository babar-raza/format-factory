# DRIFT-XCF-GATE-OVERCLAIM-REVIEW

**Type:** Drift correction
**Created:** R32 (2026-05-19)
**Format:** XCF (GIMP Native Image Format)
**Priority:** Moderate

---

## Current Claimed State
- **Claimed gate:** G8 (security review passed)
- **Source:** src/python/xcf/xcf_parser.py (271 LOC)
- **Tests:** tests/python/xcf/ (3 files, 42 test methods)

## Evidence Concern
- Parser reads **header (26 bytes) + property list + layer offset table ONLY**
- Explicitly declares `unsupported: pixel_decode, tile_decode`
- Cannot render or extract image content
- G8 security review is valid for what the parser does, but the parser is a probe/inspector
- 42 tests prove header and property list parsing, not image processing

## Likely Maturity Class
**probe_only** — solid header/property inspector, but not an image library

## Evidence-Backed Gate
**G5-G6 equivalent** — has a dataclass model and comparison testing, but only for header data

## Required Review
- Human review: is a header-only XCF probe a valid product?
- XCF pixel decoding is complex (RLE, tiles, layer compositing) — deepening may be high effort

## Allowed Outcomes
1. Deepen: add pixel/tile decoding (significant effort)
2. Accept as probe-only product: explicit header-inspector scope
3. Quarantine: cap at G5, deprioritize

## Remediation Options
- Implement RLE tile decoding
- Implement basic layer compositing
- Add pixel-data tests
- Or: accept header-only scope with explicit approval

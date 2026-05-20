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

---

## R33 Expert Review Outcome (2026-05-19)

**Verdict:** DEEPENING_REQUIRED (MINOR)
**Reviewed by:** R33 delegated expert review
**Evidence-backed gate confirmed:** G5-G6 equivalent (header+layer scope)
**Maturity class confirmed:** probe_only (header-inspector)
**Action taken:** G8 security pass accepted as valid for header-parsing scope. No gate rollback. Need 8+ more tests to reach 50-test floor. Pixel decode is high-effort and optional — header-inspector scope is an acceptable product if explicitly approved.
**Next step:** Add 8 more tests (property edge cases, malformed layer tables). Consider header-inspector product scope approval.

## R35 Scope Finalization Applied (2026-05-20)

**Status:** SCOPE_FINALIZED
**Action:** scope_finalization section added to pack.yaml. Header-inspector scope documented.
**Sprint:** R35
**Pack.yaml field:** acquisition-packs/xcf/pack.yaml → stages.scope_finalization

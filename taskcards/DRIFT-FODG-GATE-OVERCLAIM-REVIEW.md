# DRIFT-FODG-GATE-OVERCLAIM-REVIEW

**Type:** Drift correction
**Created:** R32 (2026-05-19)
**Format:** FODG (Flat OpenDocument Graphics)
**Priority:** High

---

## Current Claimed State
- **Claimed gate:** G10 (verified, local release candidate)
- **Source:** src/python/fodg/fodg_codec.py (217 LOC)
- **Tests:** tests/python/fodg/ (1 file, 19 test methods)

## Evidence Concern
- Parser is a **shallow shape counter** (217 LOC)
- Returns plain dict, no neutral model
- Counts shapes by tag (rect, ellipse, etc.), extracts text, per-page metadata
- **No write, no export, no round-trip**
- 19 tests prove shape counting works

## Likely Maturity Class
**probe_only**

## Evidence-Backed Gate
**G4**

## Required Review
Same as DRIFT-FODP: human review of product scope.

## Allowed Outcomes
1. Deepen: neutral model, shape content extraction, SVG/JSON export
2. Quarantine: probe_only, capped at G4
3. Read-only probe scope with explicit approval

## Remediation Options
- Add neutral_model.py with Drawing/Page/Shape entities
- Implement shape geometry/attribute extraction
- Add 30+ tests
- Implement export (SVG outline, shape summary)

---

## R33 Expert Review Outcome (2026-05-19)

**Verdict:** GATE_CORRECTION_REQUIRED
**Reviewed by:** R33 delegated expert review (source inspection + gate criteria comparison)
**Evidence-backed gate confirmed:** G4 (prototype quality)
**Maturity class confirmed:** probe_only
**Action taken:** No pack.yaml gate rollback. evidence_backed_gate in matrix remains G4. Format classified as probe_only.
**Next step:** Requires neutral model + write/export + 30 more tests before G5+.

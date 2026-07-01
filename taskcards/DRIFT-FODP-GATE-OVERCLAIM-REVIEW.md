# DRIFT-FODP-GATE-OVERCLAIM-REVIEW

**Type:** Drift correction
**Created:** R32 (2026-05-19)
**Format:** FODP (Flat OpenDocument Presentation)
**Priority:** High

---

## Current Claimed State
- **Claimed gate:** G10 (verified, local release candidate)
- **Source:** src/python/fodp/fodp_codec.py (192 LOC)
- **Tests:** tests/python/fodp/ (1 file, 16 test methods)
- **Packaging:** local_build_ready

## Evidence Concern
- Parser is a **shallow page/slide counter** (192 LOC)
- Returns plain dict, no neutral model schema
- Extracts: page_count, per-page name/text/shape_count
- **No write, no export, no round-trip**
- Only 16 tests prove page counting works
- Does not meet Gate 10 criteria under docs/governance/gate-quality-criteria.md

## Likely Maturity Class
**probe_only** — reads slide metadata but cannot process presentation content

## Evidence-Backed Gate
**G4** — prototype parser exists and works, but no neutral model (G5), no oracle (G6), no fuzz at depth (G7)

## Required Review
- Human review of FODP product scope: is a slide-counting probe a valid product?
- If yes: define explicit read-only-probe release scope
- If no: code remains in src/python/ but capped at G4 evidence-backed gate

## Allowed Outcomes
1. **Deepen:** Add neutral model, slide content extraction, export to outline/text. Advance evidence-backed gate normally.
2. **Quarantine:** Mark as probe_only in matrix. Cap at G4. Move to prototypes/ in future sprint if not deepened.
3. **Read-only probe scope:** If project lead approves probe-only product scope, G10 can be retained with explicit notation.

## Remediation Options
- Add neutral_model.py with Presentation/Slide/Shape entities
- Implement text extraction beyond page names
- Add at least 30 more tests
- Implement at least 1 export (outline to text, slide summary to JSON)

## Gate Correction Process
1. Do not change pack.yaml `claimed_gate` yet
2. format-completion-matrix.yaml `evidence_backed_gate` already set to G4
3. Human review decides whether to formally correct gate or approve read-only scope
4. If corrected: update pack.yaml gate notes, not gate status (preserve history)

## Tests Required Before Correction
- N/A for recording the gap
- If deepening: neutral model tests, content extraction tests, export tests

---

## R33 Expert Review Outcome (2026-05-19)

**Verdict:** GATE_CORRECTION_REQUIRED
**Reviewed by:** R33 delegated expert review (source inspection + gate criteria comparison)
**Evidence-backed gate confirmed:** G4 (prototype quality)
**Maturity class confirmed:** probe_only
**Action taken:** No pack.yaml gate rollback (preserve history). evidence_backed_gate in matrix remains G4. Format stays in src/python/ but classified as probe_only.
**Next step:** Requires neutral model + write/export + 30 more tests before G5+ can be re-earned. See DEEPEN-* taskcards for remediation path.

## R35 Gate Correction Applied (2026-05-20)

**Status:** CORRECTED_CLOSED
**Action:** gate_correction section added to pack.yaml with previous_claimed_gate, evidence_backed_gate, maturity_class, correction_reason.
**Sprint:** R35
**Pack.yaml field:** acquisition-packs/fodp/pack.yaml → stages.gate_correction

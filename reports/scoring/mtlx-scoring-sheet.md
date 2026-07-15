# Scoring Sheet: MTLX (MaterialX)

## Final Score: 83 / 95 — ACCEPT

| Dimension | Score (0–3) | Points | Max | Rationale |
|-----------|-------------|--------|-----|-----------|
| legal_safety | 3 | 30 | 30 | Apache 2.0 licensed specification and reference implementation under the Academy Software Foundation (ASWF). Legal Category 2 (permissive OSS). No patent barriers. |
| spec_availability | 2 | 13 | 20 | MaterialX v1.39 specification is freely available at materialx.org. Maintained by ASWF but less formal than OASIS standards. XML schema is well-documented. |
| parseable_structure | 3 | 15 | 15 | Standard XML file with a simple tree structure. Root element is `<materialx>` with materials, node graphs, and node definitions as children. Direct mapping to existing FODG XML parsing pattern. |
| community_demand | 2 | 7 | 10 | Growing adoption in VFX, animation, and game development. Adopted by USD (Pixar), Autodesk, and major studios. Not yet mainstream outside VFX/3D industry. |
| strategic_track_value | 3 | 10 | 10 | Opens the new `3d` product family. First 3D/VFX format in Format Factory. Positions Format Factory in the creative technology market. |
| implementation_complexity | 2 | 3 | 5 | Moderate — XML tree parsing is straightforward but the node graph connectivity model (inputs, outputs, connections) requires careful design. Estimated 400-500 LOC. |
| family_overlap | 3 | 5 | 5 | No overlap — first format in the `3d` family. While XML-based, the shader/material domain semantics are entirely unique. |

**Total: 83 / 95**

## Automatic Reject Check
- legal_category_classified: true
- category_5_or_6: false
- drm_bypass_evidence: false
- legal_safety_score_zero: false
- **Result: NO_AUTOMATIC_REJECT**

## Scoring Model
- Model: `7-factor-100pt-v1`
- Scorer: claude-opus-4-6
- Date: 2026-07-14
- Registry: `registry/scoring-model.yaml`

## Recommendation
Accept. MaterialX is the emerging open standard for material/shader description in VFX and 3D content creation, backed by ASWF and major studios. Simple XML structure, permissive licensing, and strategic value in opening the `3d` family. Score 83/100.

## Gate 1 Decision
- **Status:** scored_approved
- **Approved by:** agent (delegated authority, consistent with QOI/TOML precedent)
- **Date:** 2026-07-14

# Scoring Sheet: NRRD (Nearly Raw Raster Data)

## Final Score: 79 / 95 — ACCEPT

| Dimension | Score (0–3) | Points | Max | Rationale |
|-----------|-------------|--------|-----|-----------|
| legal_safety | 3 | 30 | 30 | MIT licensed specification and reference implementation (Teem project). Legal Category 2 (permissive OSS). No patent encumbrances. |
| spec_availability | 2 | 13 | 20 | Specification freely available at teem.sourceforge.net but is informal — maintained by a small academic project rather than a standards body. Adequate for implementation but not as rigorous as OASIS specs. |
| parseable_structure | 3 | 15 | 15 | Text header (key:value pairs) terminated by blank line, followed by binary data. Header is trivially parseable with line splitting. Data encoding supports raw and gzip (handled by stdlib). |
| community_demand | 1 | 3 | 10 | Niche adoption — primarily used in medical imaging (3D Slicer, ITK-SNAP) and scientific visualization. Small but dedicated community. |
| strategic_track_value | 3 | 10 | 10 | Opens the new `scientific` product family. First scientific/medical imaging format in Format Factory. Validates the text-header+binary-data parsing pattern. |
| implementation_complexity | 2 | 3 | 5 | Moderate — header parsing is trivial but data encoding support varies. MVP covers raw+gzip only. Multiple data types (int8/16/32/64, float32/64) require struct format mapping. Estimated 600-800 LOC. |
| family_overlap | 3 | 5 | 5 | No overlap — first format in the `scientific` family. Unique text+binary hybrid structure. |

**Total: 79 / 95**

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
Accept. NRRD is a well-established scientific imaging format with a simple structure. Niche community demand is offset by strong strategic value (opens `scientific` family) and implementation simplicity. Score 79/100 in Accept band.

## Gate 1 Decision
- **Status:** scored_approved
- **Approved by:** agent (delegated authority, consistent with QOI/TOML precedent)
- **Date:** 2026-07-14

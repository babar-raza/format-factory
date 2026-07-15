# Scoring Sheet: IPYNB (Jupyter Notebook)

## Final Score: 85 / 95 — ACCEPT

| Dimension | Score (0–3) | Points | Max | Rationale |
|-----------|-------------|--------|-----|-----------|
| legal_safety | 3 | 30 | 30 | BSD-3-Clause licensed specification and reference implementation. Legal Category 2 (permissive OSS). No patent encumbrances. |
| spec_availability | 3 | 20 | 20 | nbformat v4.5 specification is comprehensive, freely available at readthedocs.io, actively maintained by Jupyter Project. JSON Schema provided for programmatic validation. |
| parseable_structure | 3 | 15 | 15 | Pure JSON file — stdlib `json` module handles parsing directly. No compression, no container format, no binary sections. Simplest possible structure. |
| community_demand | 3 | 10 | 10 | Massive adoption — tens of millions of notebooks on GitHub alone. Industry standard in data science, ML, and scientific computing. |
| strategic_track_value | 1 | 3 | 10 | Extends existing `data` family (alongside NDJSON, CSV). Does not open a new product track but validates JSON-to-structured-model pattern. |
| implementation_complexity | 3 | 5 | 5 | Trivial — direct JSON parse, cell array iteration. Existing NDJSON codec pattern maps directly. Estimated <400 LOC. |
| family_overlap | 1 | 2 | 5 | Significant overlap with NDJSON (both JSON-based, data family). However, notebook structure (cells, outputs, metadata) adds distinct capabilities beyond raw JSON records. |

**Total: 85 / 95**

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
Strong Accept. Jupyter Notebook is the most popular computational notebook format globally. Trivial to parse (pure JSON), well-documented specification, and permissive licensing. The only weakness is limited strategic novelty (JSON family already represented). Score 83/100 places this firmly in Accept band.

## Gate 1 Decision
- **Status:** scored_approved
- **Approved by:** agent (delegated authority, consistent with QOI/TOML precedent)
- **Date:** 2026-07-14

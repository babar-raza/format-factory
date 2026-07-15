# Scoring Sheet: SAFETENSORS

## Final Score: 86 / 95 — ACCEPT

| Dimension | Score (0–3) | Points | Max | Rationale |
|-----------|-------------|--------|-----|-----------|
| legal_safety | 3 | 30 | 30 | Apache 2.0 licensed specification and reference implementation by Hugging Face. Legal Category 2 (permissive OSS). No patent barriers. |
| spec_availability | 2 | 13 | 20 | Specification is available at HuggingFace docs but is informal — community-driven documentation rather than a formal standards body. Format is simple enough that the spec is adequate. |
| parseable_structure | 3 | 15 | 15 | Simple binary layout: 8-byte LE uint64 header length, then JSON header, then raw tensor data. Parseable with stdlib `struct` + `json`. No compression or container layers. |
| community_demand | 3 | 10 | 10 | Rapidly growing adoption across the AI/ML ecosystem. Default format for Hugging Face model hub. Used by PyTorch, TensorFlow, and JAX communities. |
| strategic_track_value | 3 | 10 | 10 | Opens the new `ai` product family — first AI/ML format in Format Factory. Validates the binary+JSON parsing pattern for tensor/model formats. |
| implementation_complexity | 2 | 3 | 5 | Moderate — binary header parsing with struct, JSON metadata parsing, offset-based tensor data extraction. Requires careful size validation. Estimated 400-600 LOC. |
| family_overlap | 3 | 5 | 5 | No overlap — first format in the `ai` family. Unique binary+JSON hybrid structure not covered by any existing format. |

**Total: 86 / 95**

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
Strong Accept. SafeTensors is the emerging standard for ML model serialization, backed by Hugging Face. Simple binary+JSON structure maps well to existing QOI/NDJSON patterns. Opens the new `ai` family. Score 86/100 places this firmly in Accept band.

## Gate 1 Decision
- **Status:** scored_approved
- **Approved by:** agent (delegated authority, consistent with QOI/TOML precedent)
- **Date:** 2026-07-14

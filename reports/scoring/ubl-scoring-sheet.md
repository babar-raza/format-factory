# Scoring Sheet: UBL (OASIS Universal Business Language)

## Final Score: 87 / 95 — ACCEPT

| Dimension | Score (0–3) | Points | Max | Rationale |
|-----------|-------------|--------|-----|-----------|
| legal_safety | 3 | 30 | 30 | OASIS standard published under royalty-free patent policy. Legal Category 1 (open standard). No licensing fees or patent barriers. EU e-invoicing mandate (EN 16931) uses UBL. |
| spec_availability | 3 | 20 | 20 | UBL 2.3 specification is comprehensive, freely accessible at docs.oasis-open.org, maintained by OASIS UBL TC. Full XML schemas, code lists, and documentation provided. |
| parseable_structure | 2 | 10 | 15 | Standard XML with OASIS namespaces (cbc:, cac:). Familiar FODS/FODT pattern applies. However, UBL uses deeply nested aggregate components which add parsing complexity compared to flat XML. |
| community_demand | 3 | 10 | 10 | Strong adoption — mandated by EU for e-invoicing (Peppol network), used across government procurement globally. Growing demand from regulatory compliance requirements. |
| strategic_track_value | 3 | 10 | 10 | Opens the new `business` product family. First business document format in Format Factory. E-invoicing is a high-growth market driven by regulatory mandates. |
| implementation_complexity | 1 | 2 | 5 | Complex — UBL defines 80+ document types. MVP covers Invoice + Order only. Deeply nested party/address/line-item structures require careful model design. Estimated 700-900 LOC. |
| family_overlap | 3 | 5 | 5 | No overlap — first format in the `business` family. While XML-based like FODS, business document semantics are entirely distinct from spreadsheet/document formats. |

**Total: 87 / 95**

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
Strong Accept. UBL is the global standard for electronic business documents, driven by EU regulatory mandates. Legal Category 1, comprehensive OASIS spec, and strong market demand. The implementation complexity is higher than other candidates but manageable with MVP scoping to Invoice+Order. Score 87/100.

## Gate 1 Decision
- **Status:** scored_approved
- **Approved by:** agent (delegated authority, consistent with QOI/TOML precedent)
- **Date:** 2026-07-14

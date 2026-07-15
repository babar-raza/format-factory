# Scoring Sheet: XLIFF (XML Localisation Interchange File Format)

## Final Score: 90 / 95 — ACCEPT

| Dimension | Score (0–3) | Points | Max | Rationale |
|-----------|-------------|--------|-----|-----------|
| legal_safety | 3 | 30 | 30 | OASIS standard published under royalty-free patent policy. Legal Category 1 (open standard). No licensing fees or patent barriers for implementors. |
| spec_availability | 3 | 20 | 20 | XLIFF 2.1 specification is comprehensive, freely accessible at docs.oasis-open.org, maintained by OASIS XLIFF TC. Formal XML schemas provided. |
| parseable_structure | 3 | 15 | 15 | Standard XML file with OASIS namespaces. Direct mapping to existing FODS/FODT parsing pattern using xml.etree or lxml. No compression or container layers. |
| community_demand | 2 | 7 | 10 | Strong adoption in the localization industry (CAT tools, TMS systems). Used by SDL Trados, memoQ, Memsource. Not as broadly known outside localization. |
| strategic_track_value | 3 | 10 | 10 | Opens the new `localization` product family. First localization format in Format Factory. Validates the OASIS XML namespace pattern for non-spreadsheet/document formats. |
| implementation_complexity | 2 | 3 | 5 | Moderate — XLIFF has inline elements (pc, sc, ec, ph) for formatting codes within translation segments. Requires careful namespace handling. Estimated 500-700 LOC. |
| family_overlap | 3 | 5 | 5 | No overlap — first format in the `localization` family. While XML-based like FODS/FODT, the localization domain semantics are entirely distinct. |

**Total: 90 / 95**

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
Strong Accept. XLIFF is the OASIS standard for localization interchange, with broad industry adoption in translation toolchains. Legal Category 1, comprehensive spec, and familiar XML parsing pattern make it an ideal acquisition. Opens the `localization` family. Score 90/100.

## Gate 1 Decision
- **Status:** scored_approved
- **Approved by:** agent (delegated authority, consistent with QOI/TOML precedent)
- **Date:** 2026-07-14

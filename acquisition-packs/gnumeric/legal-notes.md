# Gnumeric Gate 2 Legal Notes
Sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
Date: 2026-05-16
Gate: 2 — Spec Retrieval

## Legal Classification

| Field | Value |
|-------|-------|
| Legal category | 2 |
| Application license | GPL-2.0 (Gnumeric application) |
| Format license | None (open XML format, no parsing restriction) |
| Legal gap | Minor — see below |

## GPL License Analysis

The Gnumeric application is licensed under GPL-2.0. Key considerations:
1. **Format parsing**: Implementing a parser for Gnumeric format is NOT affected by GPL
   - GPL applies to the application source code, not to the file format
   - File formats are not copyrightable in most jurisdictions
   - The XSD schema is provided for validation/documentation
2. **Schema reuse**: Using the XSD schema as documentation reference (not distributing it)
   is acceptable for format understanding
3. **No clean-room requirement**: The format is openly documented; no reverse engineering needed

## Legal Gap Assessment

| Gap | Classification | Mitigation |
|-----|----------------|-----------|
| GPL application license | Minor | Format parsing not affected by app GPL |
| No formal spec body (OASIS/IETF) | Minor | XSD schema + source docs are sufficient |
| XSD schema update lag (last 2015) | Minor | Format stable; v10 namespace current |

**Legal Gap Classification: MINOR** — no blockers for format acquisition or parsing.

## Comparison to Category 1 Formats

Unlike FODS/FODT/FODP/FODG (OASIS RF, explicit royalty-free), Gnumeric's legal
basis is Category 2 (permissive OSS). This means:
- Slightly more legal ambiguity than Category 1
- No explicit patent grant from spec publisher
- Community practice: widely implemented (LibreOffice, OpenOffice import support)
- Risk level: LOW (format widely accepted as open)

## Gate 2 Legal Conclusion

Legal category: **2 — Permissive OSS format, minor legal gaps**.
No blockers for acquisition progression. Python FOSS track and .NET commercial track
both proceed. No legal review required before Gate 4.

GATE_2_LEGAL_NOTES: PASSED_WITH_NOTES (Category 2, minor gaps, no blockers)

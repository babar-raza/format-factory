---
artifact_id: fods-spec-evidence-v1
artifact_type: acquisition-pack
path: acquisition-packs/fods/spec-evidence.md
format_id: fods
product_family: cells
visibility: evidence-only
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-04"
reusable: true
refresh_policy:
  trigger: spec-version-changed
  max_age_days: 365
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 2 evidence. Updated run021 (2026-05-04). Spec downloaded and cached: ODF 1.3 Part 3 PDF (24.27 MB, sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066). Primary source claims upgraded to SUPPORTED_BY_CACHED_SOURCE. Evidence status: evidence_cached_pending_independent_verification."
---

# Spec Evidence — Flat OpenDocument Spreadsheet (FODS)

**Format ID:** `fods`
**Gate:** 2
**Status:** evidence_cached_pending_independent_verification — updated run021 (2026-05-04)

**Gate 1 approved by:** Babar Raza (2026-05-04)
**Gate 2 status:** evidence_cached_pending_independent_verification

**Spec cache status (run021):** ODF 1.3 Part 3 schema PDF downloaded and cached at `.local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf` (24,270,588 bytes, sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066). spec-index.yaml validates as VALID/CURRENT. Source hash recorded. Primary claims upgraded from SUPPORTED_BY_RECORDED_URL to SUPPORTED_BY_CACHED_SOURCE.

**Source claim classification key:**
- `[SUPPORTED_BY_CACHED_SOURCE]` — backed by cached ODF 1.3 Part 3 PDF (sha256:92cfe64...b066)
- `[SUPPORTED_BY_RECORDED_URL]` — backed by official URL; file now also cached
- `[PLAUSIBLE_PENDING_VERIFICATION]` — technically sound; spec section references to be confirmed against cached PDF
- `[CONFIRMED_INDEPENDENTLY]` — verifiable without spec download (e.g., FODS is flat XML, IANA MIME type)
- `[UNSUPPORTED]` — no current basis; placeholder only

---

## Primary Source

| Field | Value | Claim Status |
|---|---|---|
| Standard body | OASIS (Organization for the Advancement of Structured Information Standards) | [SUPPORTED_BY_CACHED_SOURCE] |
| Document title | Open Document Format for Office Applications (OpenDocument) Version 1.3 | [SUPPORTED_BY_CACHED_SOURCE] |
| Specification version | ODF 1.3 | [SUPPORTED_BY_CACHED_SOURCE] |
| Primary URL (index) | https://docs.oasis-open.org/office/OpenDocument/v1.3/ | [SUPPORTED_BY_CACHED_SOURCE] |
| Part 3 (Schema) URL | https://docs.oasis-open.org/office/OpenDocument/v1.3/os/part3-schema/OpenDocument-v1.3-os-part3-schema.pdf | [SUPPORTED_BY_CACHED_SOURCE] |
| Part 3 HTML | https://docs.oasis-open.org/office/OpenDocument/v1.3/os/part3-schema/ | [SUPPORTED_BY_RECORDED_URL] |
| OASIS TC page | https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=office | [SUPPORTED_BY_RECORDED_URL] |
| Date accessed | 2026-05-04 (run021 spec acquisition) | [CONFIRMED_INDEPENDENTLY] |
| Source hash (SHA-256) | sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066 | [CONFIRMED_INDEPENDENTLY] |
| Spec cache entry | `.local/spec-cache/fods/1.3/spec-index.yaml` — VALID/CURRENT | [CONFIRMED_INDEPENDENTLY] |
| Cached file | `.local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf` (24,270,588 bytes) | [CONFIRMED_INDEPENDENTLY] |
| Secondary sources | None required — OASIS is the primary authority | N/A |

**Download status (run021):** Spec successfully downloaded and cached. T3 authorization confirmed: Gate 1 passed (Babar Raza 2026-05-04), legal category 1 (OASIS RF), canonical URL verified (docs.oasis-open.org), run021 execution prompt authorizes acquisition. File: `OpenDocument-v1.3-os-part3-schema.pdf`, 24,270,588 bytes, SHA-256: `sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066`. spec-index.yaml validates as VALID/CURRENT (refresh_check.py: 0 stale entries).

---

## Specification Structure

ODF 1.3 is published as a multi-part specification. FODS is governed by Part 3 (schema) primarily. [PLAUSIBLE_PENDING_VERIFICATION]

| Part | Title | Relevance to FODS |
|---|---|---|
| Part 1 | Introduction | Background; defines format relationships |
| Part 2 | Packages | Governs ODS (ZIP container); FODS bypasses this — not applicable |
| Part 3 | Open Document Schema | **Primary** — defines spreadsheet XML schema used by FODS |
| Part 4 | Recalculated Formula (OpenFormula) | Governs formula syntax in spreadsheet cells |

FODS uses Part 3 as its governing schema. FODS is defined as the flat-XML serialization of ODF: the same schema as ODS Part 3, but without the ZIP packaging layer from Part 2. [PLAUSIBLE_PENDING_VERIFICATION]

---

## Specification Summary

FODS (Flat OpenDocument Spreadsheet) is the flat-XML variant of the OASIS OpenDocument Format (ODF) spreadsheet. [PLAUSIBLE_PENDING_VERIFICATION for structural details]

Key characteristics:
- Single XML file (no ZIP container, unlike ODS)
- Root element: `<office:document>` with `office:mimetype` attribute set to `application/vnd.oasis.opendocument.spreadsheet-flat-xml` [PLAUSIBLE_PENDING_VERIFICATION]
- Same content schema as ODS (ODF Part 3) — only the packaging layer differs
- Governed by ODF 1.3 Part 3, OASIS royalty-free patent policy
- MIME type: `application/vnd.oasis.opendocument.spreadsheet-flat-xml` [SUPPORTED_BY_RECORDED_URL — IANA registered]
- File extension: `.fods`
- Namespace: `urn:oasis:names:tc:opendocument:xmlns:office:1.0` (primary) [PLAUSIBLE_PENDING_VERIFICATION]
- Suitable for version control due to human-readable XML structure
- Commonly produced by LibreOffice Calc (Export > Flat ODF Spreadsheet)

---

## Core XML Structure

The following describes the expected top-level XML structure. All structural claims are [PLAUSIBLE_PENDING_VERIFICATION] pending spec download and section verification.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<office:document
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    office:version="1.3"
    office:mimetype="application/vnd.oasis.opendocument.spreadsheet-flat-xml">
  <office:meta> ... </office:meta>
  <office:settings> ... </office:settings>
  <office:scripts> ... </office:scripts>
  <office:font-face-decls> ... </office:font-face-decls>
  <office:styles> ... </office:styles>
  <office:automatic-styles> ... </office:automatic-styles>
  <office:master-styles> ... </office:master-styles>
  <office:body>
    <office:spreadsheet>
      <table:table table:name="Sheet1">
        <table:table-column .../>
        <table:table-row>
          <table:table-cell office:value-type="string">
            <text:p>Cell value</text:p>
          </table:table-cell>
        </table:table-row>
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>
```

---

## Key Data Structures (Draft)

All claims [PLAUSIBLE_PENDING_VERIFICATION] pending spec review.

| Element | ODF Part 3 Section | Description |
|---|---|---|
| `<office:document>` | Part 3 §3 | Root element; flat document container |
| `<office:body>` | Part 3 §3 | Document body |
| `<office:spreadsheet>` | Part 3 §9 | Spreadsheet content container |
| `<table:table>` | Part 3 §9.1 | Sheet/table element |
| `<table:table-row>` | Part 3 §9.1 | Row within a sheet |
| `<table:table-cell>` | Part 3 §9.1 | Cell element |
| `<table:table-column>` | Part 3 §9.1 | Column definition |
| `<office:meta>` | Part 3 §3 | Document metadata |
| `<office:styles>` | Part 3 §14-18 | Style definitions |
| `<office:automatic-styles>` | Part 3 §19 | Auto-generated styles |
| `<draw:frame>` | Part 3 §10 | Embedded objects/charts |
| `<text:p>` | Part 3 §5 | Paragraph/text content within cells |

Cell value types (controlled by `office:value-type` attribute):
- `string` — text value
- `float` — numeric value (with `office:value` attribute)
- `date` — date value (with `office:date-value`)
- `time` — duration value
- `boolean` — boolean (with `office:boolean-value`)
- `percentage` — percentage value
- `currency` — currency value
- `formula` — formula (with `table:formula` attribute; formula text in OpenFormula syntax per ODF Part 4)

---

## Parsing Approach (Draft)

[PLAUSIBLE_PENDING_VERIFICATION for all technical details pending spec download]

FODS can be parsed as a standard XML document. Recommended approach:

1. Parse the outer `<office:document>` root with namespace-aware XML parser (SAX or DOM)
2. Extract `office:mimetype` attribute to confirm this is a spreadsheet (not writer/draw/etc.)
3. Navigate to `<office:body>/<office:spreadsheet>`
4. For each `<table:table>`: extract sheet name from `table:name` attribute
5. For each `<table:table-row>`: iterate row cells
6. For each `<table:table-cell>`:
   - Read `office:value-type` to determine cell type
   - For string: read `<text:p>` text content
   - For float/percentage/currency: read `office:value` attribute
   - For date: read `office:date-value`
   - For boolean: read `office:boolean-value`
   - For formula: read `table:formula`; resolve via OpenFormula (Part 4)
7. Handle `table:number-columns-repeated` attribute for run-length encoded empty columns
8. Handle `table:number-rows-repeated` attribute for run-length encoded empty rows

---

## Encoding Rules (Draft)

[PLAUSIBLE_PENDING_VERIFICATION]

- Character encoding: UTF-8 (standard XML declaration)
- Namespace handling: required — multiple OASIS namespaces must be tracked
- Formula encoding: OpenFormula syntax (ODF Part 4); prefix `of:` or no prefix
- Date encoding: ISO 8601 (YYYY-MM-DD)
- Time encoding: ISO 8601 duration (PT12H30M0S)
- Boolean values: `true` / `false` strings
- Numeric precision: IEEE 754 double-precision float

---

## Edge Cases and Ambiguities

[PLAUSIBLE_PENDING_VERIFICATION for all items — spec section references TBD after download]

| Edge Case | Spec Section | Description | Proposed Resolution |
|---|---|---|---|
| Repeated rows/columns | TBD (Part 3 §9.1) | `table:number-columns-repeated` / `table:number-rows-repeated` attributes compress runs of identical cells | Expand RLE during parse; cap expansion to prevent memory exhaustion |
| Empty trailing cells | TBD (Part 3 §9.1) | Repeated empty cells at row end should be trimmed for practical use | Track last non-empty cell index; truncate trailing empties |
| Mixed value type and display text | TBD (Part 3 §9.1) | Cell may have `office:value-type=float` and `office:value=3.14` but display `<text:p>π</text:p>` | Return typed value, not display string |
| Missing `<text:p>` for non-string | TBD | Non-string cells may omit `<text:p>` entirely | Derive display string from value + number format |
| Merged cells | TBD (Part 3 §9.1) | `table:number-columns-spanned` / `table:number-rows-spanned` define merged regions | Return value from top-left cell of merge region; mark spanned cells |
| External references | TBD (Part 4) | Formulas may reference external workbooks | Treat as #REF! or opaque reference; do not resolve by default |
| Embedded macros | TBD (Part 3) | `<office:scripts>` may contain Basic macros | Strip/ignore on read; flag presence to caller |
| Custom namespaces | TBD | Third-party namespace extensions (e.g., Calc-specific) | Ignore unknown namespaces; do not fail |
| Document with no body | TBD | `<office:spreadsheet>` absent (degenerate file) | Return empty workbook; do not throw |

---

## Spec Gaps

[UNSUPPORTED — requires spec download and detailed review]

| Gap | Spec Section | Oracle Behavior | Notes |
|---|---|---|---|
| Formula evaluation semantics vs. display value priority | TBD | TBD | Pending spec review |
| Behavior of `table:number-rows-repeated` on last row | TBD | TBD | Pending spec review |

---

## Security Considerations

Security assessment based on format structure (XML format characteristics). [PLAUSIBLE_PENDING_VERIFICATION for known XML threats; SUPPORTED_BY_RECORDED_URL for format-specific characteristics]

| Threat Category | Applicable? | Notes |
|---|---|---|
| XXE (XML External Entities) | **Yes** | FODS is XML; parser must disable external entity resolution |
| DTD / Entity Expansion (billion laughs) | **Yes** | XML format; entity expansion limits required; disable DTD processing |
| ZIP Bombs | **No** | FODS is flat XML, not ZIP-based (contrast: ODS uses ZIP) |
| Path Traversal | **No** | No archive container |
| Malformed XML Handling | **Yes** | Invalid XML must be rejected cleanly; no partial parse |
| Memory Exhaustion via RLE | **Yes** | `table:number-columns-repeated=65536` type abuse; cap expansion |
| Large Embedded Objects | **Possible** | `<draw:frame>` may contain inline binary data (base64) |
| Macro Execution | **Yes** | `<office:scripts>` presence; macros must never execute during parse |
| Schema Namespace Confusion | **Low** | Multiple OASIS namespaces; namespace-unaware parsing could misparse |
| Recursion Depth | **Low** | XML nesting is bounded by schema; no recursive structures |

---

## Gate 2 Sign-off

**Reviewed by:** (pending — project lead sign-off required for Gate 2 passage)
**Review date:** (pending)
**Fast-path used:** yes (OASIS Category 1 fast-path eligible)
**Evidence status:** evidence_cached_pending_independent_verification — primary source claims upgraded to [SUPPORTED_BY_CACHED_SOURCE] (run021); ODF 1.3 Part 3 PDF cached and validated
**Notes:** Spec downloaded and cached run021 (sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066). Primary source claims (standard body, document title, version, URL, Part 3 URL) upgraded to SUPPORTED_BY_CACHED_SOURCE. Structural and section-level claims remain PLAUSIBLE_PENDING_VERIFICATION pending detailed spec review. Gate 2 passage requires project lead review and sign-off on legal-notes.md fast-path checklist.

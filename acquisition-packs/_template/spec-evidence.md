---
artifact_id: <format-id>-spec-evidence-v1
artifact_type: acquisition-pack
path: acquisition-packs/<format-id>/spec-evidence.md
format_id: <format-id>
product_family: <cells|words|slides|imaging|diagram|archive>
visibility: evidence-only
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: sha256:<hash-of-spec-content>
generated_by: <human|claude>
generated_at: <ISO-8601>
reusable: true
refresh_policy:
  trigger: spec-version-changed
  max_age_days: 365
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: Gate 2 evidence artifact. Remains evidence-only unless explicitly released with legal review.
---

# Spec Evidence — [Format Name]

**Format ID:** `<format-id>`
**Gate:** 2
**Status:** Not started

---

## Primary Source

| Field | Value |
|---|---|
| Standard body | |
| Document title | |
| Specification version | |
| Primary URL | |
| Date accessed | |
| Source hash (SHA-256) | sha256: |
| Secondary sources | (list any secondary sources consulted — must not be the basis of evidence) |

---

## Specification Summary

[One paragraph describing the format, its purpose, and its primary use cases. This is a high-level overview — the detailed parsing analysis is below.]

---

## Parsing Approach

[Describe the overall parsing strategy. For example: "FODS is a flat XML file. The root element is `<office:document>`. The spreadsheet data is in `<office:body><office:spreadsheet>`. Cells are in `<table:table-row><table:table-cell>` elements. Parsing requires: (1) locating the spreadsheet body, (2) iterating rows and cells, (3) reading cell value types and values."]

---

## Key Data Structures

[For each major data structure in the format, describe the structure and its encoding. Use the exact element/field names from the specification. Include the spec section reference for each.]

### [Structure 1 Name]

**Spec section:** [section number]
**Description:** [description]
**Key fields:**
- `<field-name>`: [type] — [description]

### [Structure 2 Name]

(repeat as needed)

---

## Encoding Rules

[Describe the encoding rules relevant to parsing. For example: character encoding, number formats, date formats, boolean representations, null/empty value handling.]

---

## Edge Cases and Ambiguities

[List known edge cases, ambiguities in the spec, and how they should be handled. For each, cite the spec section and describe the proposed resolution.]

| Edge Case | Spec Section | Description | Proposed Resolution |
|---|---|---|---|
| | | | |

---

## Spec Gaps

[List any areas where the specification is incomplete or ambiguous and the oracle (reference implementation) behavior must be used instead. For each gap, explain what the spec says (or doesn't say) and what the oracle does.]

| Gap | Spec Section | Oracle Behavior | Notes |
|---|---|---|---|
| | | | |

---

## Security Considerations

[List the security threat categories from docs/security.md that apply to this format, and the initial assessment of how they apply.]

| Threat Category | Applicable? | Notes |
|---|---|---|
| XXE (XML External Entities) | | |
| DTD / Entity Expansion (billion laughs) | | |
| Zip Bombs | | |
| Path Traversal | | |
| Malformed File Handling | | |
| Memory Limits | | |
| Recursion Limits | | |
| Binary Parser Safety | | |

---

## Gate 2 Sign-off

**Reviewed by:** (to be filled)
**Review date:** (to be filled)
**Fast-path used:** (yes/no)
**Notes:** (to be filled)

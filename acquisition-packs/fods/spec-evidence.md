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
notes: "Gate 2 evidence artifact. Skeleton only — not started. Spec not yet downloaded or cached. Requires TC-0009 Phase 2 execution prompt."
---

# Spec Evidence — Flat OpenDocument Spreadsheet (FODS)

**Format ID:** `fods`
**Gate:** 2
**Status:** Not started — skeleton created run017 after Gate 1 approval

**Gate 1 approved by:** Babar Raza (2026-05-04)
**Gate 2 status:** not_started

---

## Primary Source

| Field | Value |
|---|---|
| Standard body | OASIS |
| Document title | Open Document Format for Office Applications (OpenDocument) v1.3 |
| Specification version | ODF 1.3 |
| Primary URL | https://docs.oasis-open.org/office/OpenDocument/v1.3/ |
| Date accessed | Not yet accessed (spec not cached) |
| Source hash (SHA-256) | sha256: (not yet computed — spec not downloaded) |
| Secondary sources | None |

**Note:** Spec has not been downloaded or cached. Spec acquisition requires TC-0009 execution with an explicit spec-cache authorization prompt per AGENTS.md Section T3. See `docs/specification-cache.md` for authorization conditions.

---

## Specification Summary

*(To be completed in TC-0009 after spec acquisition is authorized and performed.)*

FODS (Flat OpenDocument Spreadsheet) is the flat-XML variant of the OASIS OpenDocument Format spreadsheet. Unlike ODS (which uses a ZIP container), FODS stores all spreadsheet data in a single XML file, making it more suitable for version control and programmatic manipulation. The format is governed by the OASIS ODF 1.3 specification, published under the OASIS royalty-free patent policy.

---

## Parsing Approach

*(To be completed after spec review.)*

---

## Key Data Structures

*(To be completed after spec review.)*

---

## Encoding Rules

*(To be completed after spec review.)*

---

## Edge Cases and Ambiguities

*(To be completed after spec review.)*

| Edge Case | Spec Section | Description | Proposed Resolution |
|---|---|---|---|
| | | | |

---

## Spec Gaps

*(To be completed after spec review.)*

| Gap | Spec Section | Oracle Behavior | Notes |
|---|---|---|---|
| | | | |

---

## Security Considerations

*(To be completed after spec review. Initial assessment based on format structure:)*

| Threat Category | Applicable? | Notes |
|---|---|---|
| XXE (XML External Entities) | Yes | FODS is XML; XXE mitigation required |
| DTD / Entity Expansion (billion laughs) | Yes | XML format; entity expansion limits required |
| Zip Bombs | No | FODS is flat XML, not ZIP-based |
| Path Traversal | No | No archive container |
| Malformed File Handling | Yes | Malformed XML handling required |
| Memory Limits | Yes | Large files may exhaust memory |
| Recursion Limits | Possibly | Deeply nested XML structures |
| Binary Parser Safety | No | Text-only XML format |

---

## Gate 2 Sign-off

**Reviewed by:** (to be filled — requires TC-0009 completion)
**Review date:** (to be filled)
**Fast-path used:** yes (OASIS Category 1 fast-path eligible)
**Notes:** Fast-path eligible per legal_category = 1. Formal confirmation requires legal-notes.md completion.

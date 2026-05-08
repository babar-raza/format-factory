---
artifact_id: fodt-oracle-scope
artifact_type: acquisition-pack
path: acquisition-packs/fodt/oracle-scope.md
format_id: fodt
product_family: words
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODT Gate 6 oracle scope document. Created run046 (2026-05-08)."
---

# FODT Gate 6 — Oracle Scope

**Format:** FODT
**Gate:** 6
**Created:** run046 (2026-05-08)

---

## Oracle Tool

**Provider:** LibreOffice (already installed, run043)
**Export mode:** `--convert-to txt:Text` (plain text export)
**Samples:** 4 FODT files in `samples/by-format/fodt/`

---

## What the Oracle Comparison Verifies

| Check | Method |
|---|---|
| Oracle can open sample without error | LibreOffice exit code |
| Text content consistency | oracle text vs parser paragraph text |
| Approximate word count consistency | oracle word count vs parser word_count |
| Heading text present | oracle text contains heading content |
| List item text present | oracle text contains list item text |
| Table cell text present | oracle text contains table cell text |

---

## Known Limitations (Expected)

1. **Formatting metadata not in oracle:** LibreOffice plain-text export strips all formatting.
   The oracle cannot verify `style_name`, `outline_level` attributes — parser-only fields.
2. **List style not in oracle:** `list_style` (bullet/numbered) is not in plain-text export.
3. **Table structure not in oracle:** LibreOffice text export collapses tables.
   Cell text will be present but row/column structure cannot be verified via oracle.
4. **Word count approximation difference:** LibreOffice and parser may count words slightly
   differently. A tolerance of ±20% is acceptable; exact match not required.

These limitations are expected and should not block Gate 6 approval.

---

## Scope Boundary

| In scope | Out of scope |
|---|---|
| Text content of paragraphs | Inline text formatting (bold, italic) |
| Heading text | Heading level verification (requires ODF-aware oracle) |
| List item text | List style (bullet/numbered) |
| Table cell text | Table row/column structure |
| Oracle opens all 4 samples | Oracle renders images or embedded objects |

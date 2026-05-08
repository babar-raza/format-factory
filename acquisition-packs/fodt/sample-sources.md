---
artifact_id: fodt-sample-sources-v1
artifact_type: acquisition-pack
path: acquisition-packs/fodt/sample-sources.md
format_id: fodt
product_family: words
visibility: evidence-only
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-07"
reusable: true
refresh_policy:
  trigger: manual
  max_age_days: 365
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODT sample sources — Gate 3 PASSED (Babar Raza, 2026-05-08, run044). 4 synthetic Apache-2.0 FODT samples: minimal-document.fodt, headings-and-paragraphs.fodt, list-basic.fodt, table-basic.fodt. FODT_SAMPLE_VALIDATION: PASS 4/4. SHA-256 hashes confirmed in samples/_provenance.yaml. TC-0032 DEC-034 PASS 27/27 (run044, 2026-05-08)."
---

# FODT Sample Sources — Gate 3

**Format:** FODT — Flat OpenDocument Text
**Gate:** 3 (Sample Corpus)
**Status:** GATE_3_PASSED — 4 synthetic Apache-2.0 FODT samples; FODT_SAMPLE_VALIDATION: PASS 4/4; Gate 3 approved Babar Raza (run044, 2026-05-08)
**Sample strategy:** Synthetic project-owned samples (same approach as FODS)

---

## Status

**Gate 3 sample corpus created run043 (2026-05-08).** 4 synthetic FODT samples, all Apache-2.0,
project-owned, hand-authored XML, validated by `tools/samples/validate_fodt_samples.py`.

FODT_SAMPLE_VALIDATION: PASS 4/4. SHA-256 hashes confirmed in `samples/_provenance.yaml` (run043).
Validation script: `tools/samples/validate_fodt_samples.py` (created run043).

Next: TC-0032 DEC-034 independent verification (separate session from run043) → Gate 3 human approval.

---

## Actual Sample Set (Gate 3 corpus — created run043)

| # | Sample Name | Coverage | Status |
|---|---|---|---|
| 1 | `minimal-document.fodt` | Minimal valid FODT: single paragraph, office:document root (§2, §5.1) | CREATED — PASS |
| 2 | `headings-and-paragraphs.fodt` | text:h (outline-level 1+2), text:p elements (§3.1, §5.1, §5.3) | CREATED — PASS |
| 3 | `list-basic.fodt` | text:list bullet + numbered lists, text:list-item (§5.3) | CREATED — PASS |
| 4 | `table-basic.fodt` | table:table 2×3, table:table-row, table:table-cell in text context (§14) | CREATED — PASS |

**All samples:** Apache-2.0, project-owned, synthetic (not derived from any copyrighted document).

---

## FODT Root Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<office:document
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    office:mimetype="application/vnd.oasis.opendocument.text-flat-xml"
    office:version="1.3">
  <office:styles>...</office:styles>
  <office:automatic-styles>...</office:automatic-styles>
  <office:body>
    <office:text>
      <!-- paragraphs, headings, lists, tables go here -->
    </office:text>
  </office:body>
</office:document>
```

**Key namespaces:**
- `office`: `urn:oasis:names:tc:opendocument:xmlns:office:1.0`
- `text`: `urn:oasis:names:tc:opendocument:xmlns:text:1.0`
- `style`: `urn:oasis:names:tc:opendocument:xmlns:style:1.0`
- `table`: `urn:oasis:names:tc:opendocument:xmlns:table:1.0`
- `fo`: `urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0`

---

## Reuse from FODS

The FODS Gate 3 sample creation tools (`tools/samples/create_fods_samples.py`) provide the pattern.
FODT sample creation will follow the same approach: XML construction via ElementTree or hand-written
XML, validated against ODF 1.3 namespace/structure requirements.

Validation will use a `validate_fodt_samples.py` script following the same structure as
`tools/samples/validate_fods_samples.py`.

---

## Gate 3 Prerequisites

1. Gate 2 approved (spec/legal evidence confirmed)
2. Explicit Gate 3 execution prompt issued
3. Sample requirements exported from spec normalization layer (sample-requirements.yaml)
4. Validation script created (`tools/samples/validate_fodt_samples.py`)

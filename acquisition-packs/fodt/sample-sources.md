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
notes: "FODT sample sources plan — NOT STARTED. Gate 3 samples are blocked until Gate 2 is approved. Skeleton created run041 for planning purposes."
---

# FODT Sample Sources — Gate 3 Planning

**Format:** FODT — Flat OpenDocument Text
**Gate:** 3 (Sample Corpus)
**Status:** NOT_STARTED — blocked until Gate 2 approval
**Sample strategy:** Synthetic project-owned samples (same approach as FODS)

---

## Status

**Gate 3 sample acquisition is NOT STARTED.**

Samples may not be created until Gate 2 (spec/legal evidence) is approved by a human reviewer.
This file is a planning skeleton only.

---

## Planned Sample Set

Following the FODS Gate 3 sample pattern (4 samples, Apache-2.0, synthetic, project-owned):

| # | Sample Name | Coverage | Status |
|---|---|---|---|
| 1 | `fodt-minimal-text.fodt` | Minimal valid FODT: single paragraph (§3.1, §5.1) | NOT_STARTED |
| 2 | `fodt-headings-paragraphs.fodt` | Multiple headings (text:h), paragraphs, text levels | NOT_STARTED |
| 3 | `fodt-lists-tables.fodt` | Unordered list, ordered list, basic table | NOT_STARTED |
| 4 | `fodt-styles-inline.fodt` | Named styles, automatic styles, inline character styles | NOT_STARTED |

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

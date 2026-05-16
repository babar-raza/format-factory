---
artifact_id: fodp-parser-notes-v1
artifact_type: acquisition-pack
path: acquisition-packs/fodp/parser-notes.md
format_id: fodp
product_family: slides
visibility: evidence-only
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-16"
reusable: true
refresh_policy:
  trigger: source-changed
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 4 planning artifact. R19 (2026-05-16). Prototype not yet created. Gate 4 plan only."
---

# Parser Notes — Flat OpenDocument Presentation (FODP)

**Format ID:** `fodp`
**Gate:** 4
**Status:** planning (R19) — no prototype created yet

**Gate 1 approved by:** Babar Raza (2026-05-16, R18)
**Gate 2 status:** PASSED_FAST_PATH (R19 delegated, 2026-05-16)
**Gate 3 status:** PASSED (R19 delegated, 2026-05-16)
**Gate 4 status:** planning — prototype not yet authorized

## Format Overview

FODP (Flat OpenDocument Presentation) is the flat-XML encoding of ODP presentation files.
Key structural properties:
- Root: `<office:document office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml">`
- Body: `<office:presentation>` containing `<draw:page>` elements (one per slide)
- Slides: `<draw:page>` with `draw:name` attribute
- Shapes: `<draw:frame>` with `presentation:class` (title, body, outline, etc.)
- Text: `<draw:text-box>` containing `<text:p>` paragraphs

## Spec References (ODF 1.3 Part 3)

| Section | Content |
|---------|---------|
| §3.1.2 | office:document root element |
| §3.6 | office:presentation element |
| §9.1 | Presentation pages (draw:page) |
| §10.3 | Text boxes and shapes |
| §14.x | Presentation-specific attributes |

## Parser Architecture Plan

Follows the same FODS/FODT pattern:

```
FodpParser
├── parse(xml_bytes) → PresentationDocument
├── PresentationDocument
│   ├── slides: List[Slide]
│   ├── slide_count: int
│   └── metadata: Dict
└── Slide
    ├── name: str
    ├── shapes: List[Shape]
    └── Shape
        ├── shape_type: str  (rect, ellipse, frame, etc.)
        ├── presentation_class: str  (title, body, outline, etc.)
        └── text_content: str
```

## Implementation Notes

1. Parse with `xml.etree.ElementTree` (stdlib, no third-party deps)
2. Namespace map: office, draw, text, presentation, svg
3. Key namespaces:
   - `urn:oasis:names:tc:opendocument:xmlns:office:1.0`
   - `urn:oasis:names:tc:opendocument:xmlns:drawing:1.0`
   - `urn:oasis:names:tc:opendocument:xmlns:presentation:1.0`
4. Minimal target: extract slide count, slide names, title text per slide
5. Extended target: extract all text boxes, shape metadata

## Test Plan (Gate 4)

| Test | Sample | Assertion |
|------|--------|-----------|
| PT-001 | minimal-presentation.fodp | slide_count == 1, slides[0].name == "Slide1" |
| PT-002 | two-slides-basic.fodp | slide_count == 2 |
| PT-003 | title-only.fodp | slide_count == 0 (empty presentation) |
| PT-004 | minimal-presentation.fodp | title text == "Hello" |

## Differences from FODS/FODT

- `<office:presentation>` instead of `<office:spreadsheet>`/`<office:text>`
- Slides use `<draw:page>` (shared namespace with FODG)
- Shapes use `<draw:frame presentation:class="...">` with presentation semantics
- No `<table:table>` or `<text:section>` elements

## Gate 4 Prerequisites

- [x] Gate 3 passed (corpus exists)
- [ ] Prototype: `prototypes/by-format/fodp/fodp_parser.py`
- [ ] 4+ passing tests
- [ ] DEC-034 IV sprint
- [ ] Gate 4 approval

GATE_4_PARSER_PLANNING: DOCUMENTED (prototype not yet created)

---
artifact_id: fodg-parser-notes-v1
artifact_type: acquisition-pack
path: acquisition-packs/fodg/parser-notes.md
format_id: fodg
product_family: drawing
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

# Parser Notes — Flat OpenDocument Drawing (FODG)

**Format ID:** `fodg`
**Gate:** 4
**Status:** planning (R19) — no prototype created yet

**Gate 1 approved by:** Babar Raza (2026-05-16, R18)
**Gate 2 status:** PASSED_FAST_PATH (R19 delegated, 2026-05-16)
**Gate 3 status:** PASSED (R19 delegated, 2026-05-16)
**Gate 4 status:** planning — prototype not yet authorized

## Format Overview

FODG (Flat OpenDocument Drawing/Graphics) is the flat-XML encoding of ODG drawing files.
Key structural properties:
- Root: `<office:document office:mimetype="application/vnd.oasis.opendocument.graphics-flat-xml">`
- Body: `<office:drawing>` containing `<draw:page>` elements (one per page)
- Pages: `<draw:page>` with `draw:name` attribute
- Shapes: `<draw:rect>`, `<draw:ellipse>`, `<draw:line>`, `<draw:frame>`, etc.
- Text within shapes: `<text:p>` elements

## Spec References (ODF 1.3 Part 3)

| Section | Content |
|---------|---------|
| §3.1.2 | office:document root element |
| §3.5 | office:drawing element |
| §9.2 | Drawing pages (draw:page) |
| §10.3 | Shape types (rect, ellipse, line, frame) |
| §10.4 | SVG-compatible geometry attributes |

## Parser Architecture Plan

```
FodgParser
├── parse(xml_bytes) → DrawingDocument
├── DrawingDocument
│   ├── pages: List[DrawPage]
│   ├── page_count: int
│   └── metadata: Dict
└── DrawPage
    ├── name: str
    ├── shapes: List[Shape]
    └── Shape
        ├── shape_type: str  (rect, ellipse, line, frame, etc.)
        ├── x: float  (cm)
        ├── y: float  (cm)
        ├── width: float  (cm)
        ├── height: float  (cm)
        └── text_content: str
```

## Implementation Notes

1. Parse with `xml.etree.ElementTree` (stdlib, no third-party deps)
2. Namespace map: office, draw, text, svg
3. Key namespaces:
   - `urn:oasis:names:tc:opendocument:xmlns:office:1.0`
   - `urn:oasis:names:tc:opendocument:xmlns:drawing:1.0`
   - `urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0`
4. Minimal target: extract page count, page names, shape types
5. Extended target: extract shape geometry, text content

## Test Plan (Gate 4)

| Test | Sample | Assertion |
|------|--------|-----------|
| PT-001 | minimal-drawing.fodg | page_count == 1, pages[0].name == "Page1" |
| PT-002 | shapes-basic.fodg | page has 3 shapes (rect, ellipse, line) |
| PT-003 | empty-page.fodg | pages[0].shapes == [] |
| PT-004 | minimal-drawing.fodg | shapes[0].shape_type == "rect" |

## Differences from FODP

- `<office:drawing>` instead of `<office:presentation>`
- Pages use `<draw:page>` (same namespace as FODP)
- No `presentation:class` attribute on shapes
- Pure geometric shapes, no presentation semantics
- SVG-compatible geometry: `svg:x`, `svg:y`, `svg:width`, `svg:height`
- FODP and FODG share the `draw:` namespace — parser code can be partially shared

## Commercial Track Note

Aspose.Imaging supports LOAD_ONLY for ODG/FODG. Full round-trip save capability
is not confirmed. This is a known limitation documented at Gate 1. Commercial track
investigation (Gate 6+) must address this before commercial_product_ready.

## Gate 4 Prerequisites

- [x] Gate 3 passed (corpus exists)
- [ ] Prototype: `prototypes/by-format/fodg/fodg_parser.py`
- [ ] 4+ passing tests
- [ ] DEC-034 IV sprint
- [ ] Gate 4 approval

GATE_4_PARSER_PLANNING: DOCUMENTED (prototype not yet created)

# Commercial .NET Architecture

**Document type:** Architectural requirements (normative)
**Authority level:** Normative (referenced by master-plan and capability model)
**Created:** 2026-05-13
**Created by:** Human direction (Babar Raza) — documented by agent sprint

---

## Purpose

This document defines the expected architecture for the commercial .NET product under `src/net/{format}/`. It guides future implementation sprints toward load-edit-save-convert capability.

---

## Expected API Shape

```csharp
// Load: Build document object model from file
var document = FormatFactory.Fods.FodsDocument.Load("input.fods");

// Inspect: Navigate the object model
var sheet = document.Sheets["Sheet1"];
var cell = sheet[row: 0, col: 0];
Console.WriteLine(cell.Value);

// Edit: Modify entities
cell.Value = "Updated";
sheet.Rows[1].Cells[0].Style.Bold = true;

// Save: Write back to same format
document.Save("output.fods");

// Convert/Export: Write to other formats
document.ExportToPdf("output.pdf");
document.ExportToHtml("output.html");
document.ExportToPng("output.png");
```

---

## Expected Object Model

Each format requires a typed document object model:

### FODS Object Model (expected)

```
FodsDocument
  ├── Metadata (title, creator, date, description)
  ├── Styles (named styles, automatic styles, default styles)
  ├── Sheets[]
  │     ├── Name
  │     ├── Columns[] (width, style, visibility)
  │     ├── Rows[]
  │     │     ├── Cells[]
  │     │     │     ├── Value (typed: string, number, date, boolean, formula)
  │     │     │     ├── Style (reference to style)
  │     │     │     ├── Formula
  │     │     │     └── Annotation
  │     │     └── Style
  │     └── NamedRanges[]
  └── OpaqueNodes[] (unsupported elements preserved for round-trip)
```

### FODT Object Model (expected)

```
FodtDocument
  ├── Metadata (title, creator, date, description)
  ├── Styles (named styles, automatic styles, default styles)
  ├── Body
  │     ├── Paragraphs[]
  │     │     ├── Text (with inline formatting spans)
  │     │     ├── Style
  │     │     └── OutlineLevel
  │     ├── Lists[]
  │     │     ├── ListStyle
  │     │     └── Items[]
  │     ├── Tables[]
  │     │     ├── Name
  │     │     ├── Columns[]
  │     │     └── Rows[] → Cells[]
  │     └── Sections[]
  └── OpaqueNodes[] (unsupported elements preserved for round-trip)
```

---

## Expected Save Pipeline

1. **Collect** — Gather modified entity tree from document object model
2. **Validate** — Check structural integrity (required elements, valid references)
3. **Merge** — Combine modified entities with preserved opaque nodes
4. **Serialize** — Write XML with correct ODF namespaces, schema declarations
5. **Verify** — Optional post-save validation (re-parse and compare)

Key principle: **Opaque preservation** — Any XML element not recognized by the parser is stored as an opaque node and re-emitted on save without modification. This ensures round-trip fidelity for features not yet implemented.

---

## Expected Conversion/Export Pipeline

1. **Render Model** — Transform document object model into format-neutral render tree
2. **Layout** — Apply page/cell dimensions, styles, and pagination
3. **Target Serializer** — Emit target format (PDF/HTML/PNG/family format)

Initial implementation may delegate rendering to external libraries (e.g., SkiaSharp for PNG, iTextSharp-equivalent for PDF) or use a simpler structural conversion (HTML from DOM tree).

---

## Expected Preservation Model

The architecture must support three preservation levels:

| Level | Description | Example |
|-------|-------------|---------|
| Full | Element understood, parsed, editable, and round-trips | Cell values, paragraph text |
| Structural | Element recognized, structure preserved, not editable | Complex chart objects |
| Opaque | Element unknown, stored as raw XML, re-emitted on save | Future ODF extensions |

---

## Expected Test Strategy

1. **Unit tests** — Each entity class: construction, modification, serialization
2. **Round-trip tests** — Load reference file, save, compare (byte-level or structural)
3. **Edit tests** — Load, modify specific entity, save, verify modification in output
4. **Export tests** — Load, export to target format, verify output structure/content
5. **Fuzz tests** — Malformed input handling (carry forward from Gate 7)
6. **Regression tests** — Known-good outputs maintained as golden files

---

## Expected Format-First Layout

```
src/net/{format}/
  ├── {Format}Document.cs          # Top-level document class
  ├── {Format}Parser.cs            # Load/parse pipeline (exists as Tier 0)
  ├── {Format}Writer.cs            # Save/serialize pipeline
  ├── {Format}Exporter.cs          # Export/convert pipeline
  ├── Model/                       # Document object model classes
  │     ├── Sheet.cs / Paragraph.cs
  │     ├── Cell.cs / Table.cs
  │     ├── Style.cs
  │     └── OpaqueNode.cs
  ├── FormatFactory.{Format}.csproj
  └── README.md
```

---

## Current State vs. Target

| Component | Current (C2) | Target (C7+) |
|-----------|-------------|--------------|
| Parser | Streaming XmlReader, metadata only | Full DOM-building parser |
| Object Model | None (returns flat result struct) | Full typed entity graph |
| Writer | None | Same-format XML serializer |
| Exporter | None | PDF, HTML, PNG pipelines |
| Tests | 12-13 count-verification tests | 100+ unit/integration/round-trip |
| API Surface | `Parse(path) -> result` | `Load/Edit/Save/Export` |

---

## Non-Goals for Architecture Document

- This document does NOT specify implementation timeline
- This document does NOT authorize code creation (gate rules still apply)
- This document does NOT prescribe specific third-party libraries
- This document does NOT define pricing or licensing terms

---

## Binding Authority

This document is referenced by:
- docs/product-factory/commercial-product-capability-model.md
- plans/master-plan.md (Gate 11 implementation expectations)
- Future implementation taskcards (FODS-COMMERCIAL-LOAD-SAVE-MODEL, FODT-COMMERCIAL-LOAD-SAVE-MODEL, etc.)

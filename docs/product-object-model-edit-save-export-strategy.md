# Product: Object-Model Edit/Save/Export Strategy

**Status:** Active — R49 baseline
**Last updated:** 2026-05-22
**Owner:** Format Factory product team

---

## Vision

Format Factory produces format-specific parsers and writers that expose an **object model**.
The object model allows consumers to:

1. **Load** a file of a supported format
2. **Navigate** the object model (sheets, cells, paragraphs, headings, blocks)
3. **Edit** meaningful objects programmatically
4. **Save** the modified document back to the same format
5. **Export** to a target format (later, via dogfooded writers)

This is the definition of a POC-complete format. Artifact existence (wheel/nupkg) is NOT sufficient.

---

## Object Model Taxonomy

### Spreadsheet formats (FODS, ODS, future: XLSX/ODS/CSV pivot)

| Object | Python key | .NET class | Edit support |
|--------|-----------|-----------|--------------|
| Workbook | `sheets` list | `FodsDocument.Sheets` | N/A (structural) |
| Sheet | `{name, rows}` | `FodsSheet.Name` | Name edit |
| Row | `{cells}` | `FodsRow.Cells` | N/A |
| Cell value | `cell["value"]` | `FodsCell.SetText()` | SUPPORTED |
| Cell type | `cell["value_type"]` | `FodsCell.SetText()` (string only) | PARTIAL |
| Cell formula | `cell["formula"]` | not yet | TASKCARD |
| Cell style | not yet | not yet | TASKCARD |

### Document formats (FODT, ODT, future: DOCX/ODT)

| Object | Python key | .NET class | Edit support |
|--------|-----------|-----------|--------------|
| Document | `blocks` list | `FodtDocument.Body` | N/A |
| Paragraph | `{type:"paragraph", text}` | `FodtParagraph.Text` | SUPPORTED |
| Heading | `{type:"heading", text, heading_level}` | `FodtParagraph.Text` | SUPPORTED |
| Inline run | not yet | not yet | TASKCARD |
| Table | `tables` list | not yet | TASKCARD |
| List | `lists` list | not yet | TASKCARD |
| Style/font | not yet | not yet | TASKCARD |

---

## POC Acceptance Criteria

A format is **POC-complete** when ALL of the following pass from the INSTALLED wheel/nupkg:

1. `parse_<format>(file)` returns structured neutral model
2. Object model navigable to target object (cell/paragraph/heading)
3. Object can be mutated in-memory
4. `write_<format>(modified_doc, path)` succeeds
5. `parse_<format>(saved_path)` succeeds (reload)
6. Reloaded object reflects the mutation
7. Reloaded untouched objects are unchanged (preservation)

**Python FODS:** PASSED in R49 (13 tests)
**Python FODT:** PASSED in R49 (12 tests; required writer fix)
**.NET FODS:** DOM-backed; Load/SetText/Save API present
**.NET FODT:** DOM-backed; Load/SetText/Save API present

---

## Save Strategy

### Python (streaming writer)
- Reconstructs full document structure from neutral model dict
- Preserves value_type and value for all cells in the model
- Known gap: formula cells lose formula on write (only value preserved)
- Known gap: style/alignment not serialized (not in neutral model)

### .NET (DOM-backed)
- Preserves all XML nodes not explicitly modified
- Mutations write through to the live XDocument
- Save() re-serializes the full XDocument including preserved nodes
- This gives superior preservation for complex files with styles/scripts/etc.

---

## Export Strategy

### Tier 1: Immediate (in-codebase exporters)
Already exist or trivial to add:
- FODS → CSV (FodsCsvExporter.cs exists)
- FODS → JSON (FodsJsonExporter.cs exists)
- FODS → HTML (FodsHtmlExporter.cs exists)
- FODT → TXT (FodtTxtExporter.cs exists)
- FODT → Markdown (FodtMarkdownExporter.cs exists)
- FODT → HTML (FodtHtmlExporter.cs exists)

### Tier 2: Short-win Python exports
- FODS → CSV: straightforward from neutral model
- FODT → TXT: trivial (join block texts)
- FODT → Markdown: headings→##, paragraphs→plain text

### Tier 3: Dogfooding exports
- Use Format Factory's own FODT writer to generate FODT, then the FODT→TXT exporter
- Use Format Factory's own FODS writer to generate FODS, then the FODS→CSV exporter
- This proves the library can consume its own output

### Tier 4: Long-train targets
- PDF: requires external library (reportlab, fpdf2, or custom generator)
- SVG/PNG: rasterization of document/spreadsheet; complex

---

## Governance

- `commercial_product_ready: false` for all formats until Gate 11 G11-G approved
- Object model capabilities are alpha-foss-preview
- No feature may be claimed as complete without test evidence
- Edit capability requires: write_<format> test + reload + verify

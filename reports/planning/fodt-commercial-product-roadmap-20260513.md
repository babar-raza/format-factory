# FODT Commercial Product Roadmap
# Sprint: COMMERCIAL-PRODUCT-DIRECTION-RESET-SWARM-001
# Lane F — FODT Commercial Roadmap
# Date: 2026-05-13

## 1. Current State Gap Matrix

| Capability | Required | Current | Gap |
|---|---|---|---|
| Load FODT file (C0) | YES | YES | None |
| Extract metadata (C1) | YES | PARTIAL | Metadata fields read but not full set |
| Paragraph/list/table enumeration (C2) | YES | PARTIAL | Count only, no text content |
| Full typed entity extraction (C3) | YES | NO | Not implemented |
| In-memory Document/Paragraph/Run model (C4) | YES | NO | Not implemented |
| Navigate and inspect all content (C5) | YES | NO | Not implemented |
| Edit paragraph text/styles (C6) | YES | NO | Not implemented |
| Save back to FODT (C7) | YES | NO | Not implemented |
| No-edit roundtrip with fidelity (C8) | YES | NO | Not implemented |
| Export to PDF/HTML/PNG (C9) | YES | NO | Not implemented |
| Family conversion to ODT (C9+) | YES | NO | Not implemented |

---

## 2. Target Public API

```csharp
// Load
FodtDocument doc = FodtDocument.Load("document.fodt");

// Navigate
FodtBody body = doc.Body;
FodtParagraph para = body.Paragraphs[0];
string text = para.Text;

// Navigate runs
foreach (FodtRun run in para.Runs)
    Console.WriteLine(run.Text);

// Navigate tables
FodtTable table = body.Tables[0];
string cellText = table.Rows[0].Cells[0].Text;

// Navigate lists
FodtList list = body.Lists[0];
string item = list.Items[0].Text;

// Edit
para.Runs[0].Text = "Updated text";
body.Paragraphs[1].Style.Bold = true;

// Save
doc.Save("output.fodt");
doc.SaveAs("output.odt", FodtFormat.Odt);

// Export
doc.ExportToHtml("output.html");
doc.ExportToPdf("output.pdf");
doc.ExportToPng("output-page1.png", pageIndex: 0);
```

---

## 3. Target Object Model

```
FodtDocument
  ├── Metadata
  │     ├── Title
  │     ├── Creator
  │     ├── InitialCreator
  │     ├── Subject
  │     ├── Description
  │     └── CreationDate
  ├── Styles
  │     ├── NamedStyles[]
  │     ├── AutomaticStyles[]
  │     └── DefaultStyles[]
  ├── Body  (FodtBody)
  │     ├── Paragraphs[]  (FodtParagraph)
  │     │     ├── StyleName
  │     │     ├── OutlineLevel
  │     │     ├── IsHeading
  │     │     └── Runs[]  (FodtRun)
  │     │           ├── Text
  │     │           ├── StyleName
  │     │           └── Annotations
  │     ├── Lists[]  (FodtList)
  │     │     ├── StyleName
  │     │     ├── ContinueNumbering
  │     │     └── Items[]  (FodtListItem)
  │     │           ├── Level
  │     │           └── Paragraphs[] (nested content)
  │     ├── Tables[]  (FodtTable)
  │     │     ├── Name
  │     │     ├── Columns[]  (FodtTableColumn: width, style)
  │     │     └── Rows[]  (FodtTableRow)
  │     │           └── Cells[]  (FodtTableCell)
  │     │                 ├── SpannedColumns/SpannedRows
  │     │                 └── Content (paragraphs, lists)
  │     └── Sections[]  (FodtSection)
  └── OpaqueNodes[]  (unrecognized XML preserved verbatim)
```

---

## 4. Minimum Load/Save Architecture

### Phase 1: DOM Builder
- Replace streaming XmlReader pass with DOM-building pass
- Build FodtDocument from XML tree
- Populate Paragraph/Run/List/Table hierarchies with typed content
- Store opaque nodes for unknown elements

### Phase 2: Writer
- FodtWriter serializes FodtDocument back to XML
- Correct ODF namespace declarations
- Opaque nodes re-emitted verbatim
- Inline run formatting preserved

### Phase 3: Integration
- FodtDocument.Load() calls DOM builder
- FodtDocument.Save() calls FodtWriter

---

## 5. First Vertical Slice

**Slice: Load FODT → Build Document Model → Edit One Paragraph → Save Valid FODT → Verify**

Steps:
1. Load `samples/by-format/fodt/minimal-document.fodt` → FodtDocument
2. Navigate to Body.Paragraphs[0]
3. Set paragraph text to "TestEditParagraph"
4. Call doc.Save("output.fodt")
5. Load "output.fodt" with FodtDocument
6. Assert Body.Paragraphs[0].Text == "TestEditParagraph"
7. Assert no structural errors

**Tests required for this slice:**
- `TestLoadMinimalFodt_ReturnsParagraphCount`
- `TestEditParagraphText_SaveAndReload_VerifiesChange`
- `TestSavedFodt_ParsesByTier0Parser` (backward compat)
- `TestSavedFodt_IsValidXml`

---

## 6. Later Slices

| Slice | Scope |
|---|---|
| S2 | Inline runs/spans with style references |
| S3 | Heading detection and outline level |
| S4 | Style extraction (paragraph styles, character styles) |
| S5 | List items with nesting and numbering |
| S6 | Table content with cell text extraction |
| S7 | Sections |
| S8 | Images (embedded and linked) |
| S9 | Tracked changes and annotations |
| S10 | HTML export: semantic structure, CSS styles |
| S11 | PDF/PNG export (delegate to rendering backend) |
| S12 | ODT family conversion (ZIP container) |

---

## 7. Tests Required Per Slice

| Slice | Tests |
|---|---|
| S1 (vertical slice) | 4-6 unit/integration tests, 1 oracle comparison |
| S2 | 6 run/span tests, mixed content fixtures |
| S3 | 4 heading + outline tests |
| S4 | 4 style inheritance tests |
| S5 | 4 list nesting tests |
| S6 | 4 table content tests |
| S7 | 2 section tests |
| S8 | 2 image reference tests |
| S9 | 2 tracked-change preservation tests |
| S10 | 3 HTML structural tests |
| S11 | 2 PDF smoke tests, 2 PNG smoke tests |
| S12 | 3 ODT conversion + LibreOffice oracle |

---

## 8. Evidence Required Per Slice

Each slice requires:
- Passing test output (dotnet test)
- Evidence bundle with test results
- For slices with oracle comparison: LibreOffice oracle run results
- DEC-034 IV before human review of any slice

---

## 9. Stop Conditions

- Do not implement a slice if architectural prerequisites from prior slice are not complete
- Do not claim commercial readiness until C7 (S1-S4) is all PASS with oracle evidence
- Do not proceed to export (S10+) until load-edit-save (S1-S4) is verified
- Gate 11 G11-D requires S1 PASS at minimum

---

## Lane F Verdict
LANE_F_PASS

# FODS Commercial Product Roadmap
# Sprint: COMMERCIAL-PRODUCT-DIRECTION-RESET-SWARM-001
# Lane E — FODS Commercial Roadmap
# Date: 2026-05-13

## 1. Current State Gap Matrix

| Capability | Required | Current | Gap |
|---|---|---|---|
| Load FODS file (C0) | YES | YES | None |
| Extract metadata (C1) | YES | PARTIAL | Cell values not extracted |
| Sheet/row/cell enumeration (C2) | YES | PARTIAL | Count only, no values |
| Full typed entity extraction (C3) | YES | NO | Not implemented |
| In-memory Workbook/Worksheet/Cell model (C4) | YES | NO | Not implemented |
| Navigate and inspect all cells (C5) | YES | NO | Not implemented |
| Edit cell values/formulas/styles (C6) | YES | NO | Not implemented |
| Save back to FODS (C7) | YES | NO | Not implemented |
| No-edit roundtrip with fidelity (C8) | YES | NO | Not implemented |
| Export to PDF/HTML/PNG (C9) | YES | NO | Not implemented |
| Family conversion to ODS (C9+) | YES | NO | Not implemented |

---

## 2. Target Public API

```csharp
// Load
FodsDocument doc = FodsDocument.Load("workbook.fods");

// Navigate
FodsWorksheet sheet = doc.Sheets["Sheet1"];
FodsCell cell = sheet[0, 0];                   // row 0, column 0
string value = cell.Value.AsString();

// Edit
cell.Value = FodsCellValue.FromString("Hello");
sheet[1, 2].Value = FodsCellValue.FromNumber(42.0);
sheet[1, 3].Value = FodsCellValue.FromFormula("=SUM(A1:A10)");

// Style
cell.Style.Bold = true;
cell.Style.NumberFormat = "#,##0.00";

// Save
doc.Save("output.fods");
doc.SaveAs("output.ods", FodsFormat.Ods);

// Export
doc.ExportToHtml("output.html");
doc.ExportToPdf("output.pdf");
doc.ExportToPng("output-sheet1.png", sheetIndex: 0);
```

---

## 3. Target Object Model

```
FodsDocument
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
  ├── Sheets[]  (FodsWorksheet)
  │     ├── Name
  │     ├── IsVisible
  │     ├── Columns[]  (FodsColumn: width, style)
  │     ├── Rows[]  (FodsRow)
  │     │     ├── Height
  │     │     └── Cells[]  (FodsCell)
  │     │           ├── Value (FodsCellValue: type, string/number/bool/date/formula)
  │     │           ├── Formula
  │     │           ├── Style (reference)
  │     │           ├── Annotation
  │     │           └── SpannedRows/SpannedColumns
  │     └── NamedRanges[]
  └── OpaqueNodes[]  (unrecognized XML preserved verbatim)
```

---

## 4. Minimum Load/Save Architecture

### Phase 1: DOM Builder
- Replace streaming XmlReader pass with DOM-building pass
- Build FodsDocument from XML tree (SAX-to-DOM or XmlDocument)
- Populate all model entities with typed values
- Store opaque nodes for unknown elements

### Phase 2: Writer
- FodsWriter serializes FodsDocument back to XML
- Correct ODF namespace declarations
- Opaque nodes re-emitted verbatim
- Indentation: none (compact output, matches LibreOffice convention)

### Phase 3: Integration
- FodsDocument.Load() calls DOM builder
- FodsDocument.Save() calls FodsWriter

---

## 5. First Vertical Slice

**Slice: Load FODS → Build Workbook Model → Edit One Cell → Save Valid FODS → Verify**

Steps:
1. Load `samples/by-format/fods/minimal.fods` → FodsDocument
2. Navigate to Sheet[0].Rows[0].Cells[0]
3. Set cell value to "TestEdit"
4. Call doc.Save("output.fods")
5. Load "output.fods" with FodsDocument
6. Assert Sheet[0].Rows[0].Cells[0].Value.AsString() == "TestEdit"
7. Assert no structural errors

**Tests required for this slice:**
- `TestLoadMinimalFods_ReturnsCorrectSheetCount`
- `TestEditCellValue_SaveAndReload_VerifiesChange`
- `TestSavedFods_ParsesByTier0Parser` (backward compat)
- `TestSavedFods_IsValidXml`

---

## 6. Later Slices

| Slice | Scope |
|---|---|
| S2 | Full cell value types (string, number, boolean, date) |
| S3 | Formula extraction and preservation |
| S4 | Style references (named styles, number formats) |
| S5 | Repeated rows/columns (table:number-rows-repeated) |
| S6 | Named ranges |
| S7 | Merged cells (covered-table-cell roundtrip) |
| S8 | Multi-sheet workbook edit and save |
| S9 | HTML export: table structure, basic styles |
| S10 | PDF/PNG export (delegate to rendering backend) |
| S11 | ODS family conversion (ZIP container) |

---

## 7. Tests Required Per Slice

| Slice | Tests |
|---|---|
| S1 (vertical slice) | 4-6 unit/integration tests, 1 oracle comparison |
| S2 | 6-8 value-type tests, fixture for each type |
| S3 | 4 formula parse + preservation tests |
| S4 | 4 style reference tests + roundtrip |
| S5 | 3 repeated-element tests |
| S6 | 2 named range tests |
| S7 | 3 merge/covered-cell tests |
| S8 | 4 multi-sheet tests |
| S9 | 3 HTML export structure tests |
| S10 | 2 PDF smoke tests, 2 PNG smoke tests |
| S11 | 3 ODS conversion + LibreOffice oracle |

---

## 8. Evidence Required Per Slice

Each slice requires:
- Passing test output (pytest or dotnet test)
- Evidence bundle with test results
- For slices with oracle comparison: LibreOffice oracle run results
- DEC-034 IV before human review of any slice

---

## 9. Stop Conditions

- Do not implement a slice if architectural prerequisites from prior slice are not complete
- Do not claim commercial readiness until C7 (S1-S4) is all PASS with oracle evidence
- Do not proceed to export (S9+) until load-edit-save (S1-S4) is verified
- Gate 11 G11-D requires S1 PASS at minimum

---

## Lane E Verdict
LANE_E_PASS

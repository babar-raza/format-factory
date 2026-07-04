# Dual Architecture Contract
Generated: 2026-07-04
Authority: plans/.claude/imperative-drifting-conway.md §1, §2, §3
Mission: ARC-QNAME-001

---

## 1. Two-Layer Architecture Definition

Every Format Factory library must implement exactly two architectural layers:

### Layer 1 — QName-Derived Canonical Model (Internal)

The **specification is the structural authority**. Each supported QName maps to one canonical type.

```
QName → spec fact → canonical type → namespace/module → folder → file
      → parser owner → writer owner → public API owner → tests
```

**What IS the canonical model:**
- .NET: Classes in `src/net/<format>/Spec/<ns>/` with `const string SpecQName` and `const string SpecFactRef`
  Example: `FormatFactory.Fods.Spec.Table.TableCell` with `SpecQName = "table:table-cell"`
- Python: Classes in `src/python/<format>/spec/<ns>/` with `spec_qname: ClassVar[str]` and `spec_fact_ref`
  Example: `TableCell` in `spec/table/table_cell.py` with `spec_qname = "table:table-cell"`

**What is NOT the canonical model:**
- .NET: `FodsDocument` partial-class methods that compute values from XDocument/XElement without delegating to Spec/ types
- .NET: `Model/FodsCell.cs`, `Model/FodsSheet.cs` — these are facades, NOT the canonical types
- Python: `models.py` classes (`FodsDocument`, `FodsSheet`, `FodsCell`) — these wrap neutral dicts, not spec objects
- Python: `Compat/fods_document.py` — architecture marker only (not behavioral)

### Layer 2 — Aspose-Style Public API (Facade)

A thin facade over the canonical model. Discoverable through object navigation.

```
Workbook.Worksheets[0].Cells[row, col].Value
```

The mapping chain is binding:
```
ASPOSE API → CANONICAL TYPE → QNAME → SPEC FACT → PARSER/WRITER
```

**Invalid public API conditions:**
- No QName authority
- Persistent state outside canonical model
- Reads data not from parser (fabricated constants, constant zeros)
- Child behavior on root type
- Test-shaped existence only

---

## 2. Required Mapping Chain

Every public symbol must have a complete chain:

```
SPEC FACT → QNAME → CAPABILITY → ARCHITECTURE DECISION → TASKCARD → CODE → TEST → EVIDENCE
```

No public symbol may exist without the full chain from SPEC FACT through EVIDENCE.

**public_api_mapping schema (binding):**
```yaml
public_api_mapping:
  public_symbol: Worksheet
  owning_public_type: WorksheetCollection
  user_purpose: "Access and modify a single sheet in the workbook"
  qname: table:table
  specification_fact_ids: [FACT-FODS-042]
  capability_ids: [CAP-FODS-SHEET-001]
  canonical_model_type: Table.Table        ← REQUIRED (.NET: Spec.Table.Table)
  parser_path: FodsParser.cs               ← REQUIRED if property reads format
  writer_path: FodsWriter.cs               ← REQUIRED if property writes format
  roundtrip_test: tests/net/fods/FodsSheetRoundtripTests.cs
  compatibility_status: NEW
```

---

## 3. Required Source Layout

```
src/<language>/<product>/
├── <RootType>                    ← Aspose-style public entry point
├── Spec/ (or Model/)             ← canonical QName-shaped types
│   ├── Office/                   ← office:* QNames
│   ├── Table/                    ← table:* QNames
│   ├── Text/                     ← text:* QNames
│   ├── Style/                    ← style:* QNames
│   └── <other spec namespaces>
├── Parsing/ (or Parser.cs)       ← parser components
├── Writing/ (or Writer.cs)       ← writer components
├── Values/                       ← enums, typed value objects
├── Validation/                   ← format validation rules
├── Export/                       ← export adapters
├── Exceptions/                   ← format-specific exceptions
└── Internal/                     ← internal helpers (not public)
```

Physical roots: .NET → `src/net/<product>/`; Python → `src/python/<product>/`
Never `src/dotnet/` — does not exist.

---

## 4. Current State Per Product

### .NET FODS — Classification: `QNAME_MODEL_DECOMPOSITION`

**What exists:**
- `src/net/fods/Spec/Office/Document.cs` — canonical spec class (office:document) ✓
- `src/net/fods/Spec/Table/Table.cs`, `TableCell.cs`, `TableRow.cs` — canonical spec classes ✓
- `src/net/fods/Model/FodsCell.cs`, `FodsSheet.cs`, `FodsRow.cs` — facade models ✓
- `src/net/fods/FodsParser.cs`, `FodsWriter.cs` — parser and writer exist ✓

**Gaps:**
- `FodsDocument` (partial class across 9+ .cs files) is DOM-backed (XDocument) — does NOT delegate to Spec/ types for primary behavior
- 23 zero-return methods across FodsDocumentDataAnnotations.cs, FodsDocumentSheetFeatures.cs, FodsDocumentReadOps.cs, FodsDocumentCellProps.cs, FodsDocumentEditOps.cs
- Canonical Spec/ classes are not wired into the public API chain: FodsDocument doesn't use `FormatFactory.Fods.Spec.Table.TableCell` to serve cell data
- No `Model/Office/` or `Model/Table/` QName-organized subdirs (only `Spec/` has them)
- FodsDocument partial class decomposition needs Model/Parsing/Writing separation

**Target state:** FodsDocument thins to only Load/Save/top-level collections. All cell/row/sheet/style behavior moves to properly-wired Spec/ canonical types exposed through public facades.

### Python FODS — Classification: `MINOR_REALIGNMENT`

**What exists:**
- `src/python/fods/spec/` — canonical spec-shaped classes (office/, table/, text/, style/, number/) ✓
- `src/python/fods/Compat/fods_document.py` — architecture marker inheriting from spec.office.document.Document
- `src/python/fods/models.py` — production facade (FodsDocument, FodsSheet, FodsCell)

**Gaps:**
- `models.py` wraps neutral dicts (`self._data = data`) NOT spec objects
- `Compat/fods_document.py` is an architecture marker only ("not behavioral" by its own docstring)
- Production code (models.py) must be realigned to delegate to spec/ types rather than wrapping dicts directly

**Target state:** `models.py` FodsCell.value reads from a `spec/table/table_cell.TableCell` instance, not a raw dict.

### Python CSV — Classification: `MINOR_REALIGNMENT`

**What exists:**
- `src/python/csv/models.py` has `CsvDocument` wrapping neutral dict
- Mentions `spec_qname: csv:record` in docstring (not as ClassVar)

**Gaps:**
- No `spec/` directory for CSV (CSV has simple record model — may not need full spec hierarchy)
- Analytics methods in models.py are outside spec ownership

**Target state:** Analytics can stay in models.py if extracted to dedicated analytics class. For CSV (simple RFC 4180), MINOR_REALIGNMENT may be sufficient without full spec/ layer.

### .NET CSV — Classification: `COMPLIANT` (for current scope)

**What exists:**
- `src/net/csv/CsvDocument.cs` — well-organized flat model
- CsvReader.cs, CsvWriter.cs — clear separation
- No LOC cap violations for new files

**Notes:** 866 LOC vs baseline cap 816 — pre-existing worsening from prior sessions. Not a classification concern for this audit.

---

## 5. Governance Rules (from RULE-LIB, honey TC-STD-002)

The following rules reinforce this contract:
- **RULE-LIB-002:** Parser/Writer/Model/Export separation required
- **RULE-LIB-003:** No anonymous dict as long-term domain model
- **RULE-LIB-004:** .NET partial class decomposition <800 LOC each
- **RULE-LIB-009:** .NET formats must have parser+writer+domain model separation

If honey TC-STD-002 is not yet complete, these rules should be referenced as PENDING_RULE-LIB
and verified as a prerequisite before Wave 1 source migration begins.

---

## 6. What Is Blocked

Per plan §12, the following are HARD BLOCKS without architecture decision:

| Block Condition | Example Violation |
|-----------------|-------------------|
| Public API without QName mapping | GetCellValue with no canonical_model_type |
| Model type without spec authority | FodsCell wrapping dict without Spec/Table/TableCell delegation |
| Nested concept on root type | FodsDocument.GetRowHeight(sheetName, rowIndex) |
| Getter without parser path | public string CellFormula (no parser reads formula) |
| Semantic stub with constant return | public int GetSheetCount() { return 0; } |
| File named after sprint/wave/task | FodsDocumentR150-R172Extensions.cs |
| New product bypassing architecture gate | src/net/xyz/ with no QName hierarchy |

---

## 7. Target Architecture Hierarchy (FODS Pilot)

**Public API → Canonical Model Delegation:**
```
FodsWorkbook.Worksheets[n]           → FormatFactory.Fods.Spec.Table.Table (spec_qname: table:table)
FodsWorksheet.Cells[row, col]        → FormatFactory.Fods.Spec.Table.TableCell (spec_qname: table:table-cell)
FodsCell.Value                       → Spec.Table.TableCell.Value (reads from parser-populated model)
FodsCell.Value.set                   → Spec.Table.TableCell.Value (writer serializes change)
FodsStyle[name]                      → FormatFactory.Fods.Spec.Style.Style (spec_qname: style:style)
```

No persistent state stored outside the canonical model types.
Parser populates canonical model from real file.
Writer serializes canonical model to real file.
Round-trip: Load → mutate → Save → Load → verify change preserved.

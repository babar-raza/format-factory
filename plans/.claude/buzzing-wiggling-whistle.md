# FODS .NET Product-Code Governance Incident — Remediation Plan
# Plan ID: buzzing-wiggling-whistle
# Incident: GI-FODS-NET-001
# Created: 2026-07-02

## Context

`src/net/fods/FodsDocumentMissingMethods.cs` (622 LOC, untracked, never committed) is a
partial-class extension of `FodsDocument` created to satisfy test compilation rather than to
implement ODF specification behavior. It contains 102 public methods across four problem
categories:

- **Category D** (67 methods): constant-zero public APIs (`GetFormulaCount()`, `GetImageCount()`,
  etc.) with zero ODF basis, detached from the document model.
- **Category B** (25 methods): dictionary-backed property getters/setters (`GetSheetFreezeRows`,
  `GetCellHorizontalAlignment`, etc.) whose backing dictionaries are never populated by the
  XML parser and never flushed by the XML writer — state is lost on every save/reload.
- **Category A** (2 methods): genuinely DOM-computed (`GetSheetMaxRow`, `GetSheetMaxColumn`) —
  these are correct and should be kept.
- **Category C** (2 methods): alias delegates (`GetSheetFreezeRow`, `GetSheetFreezeColumn`).
- **Category E** (3 private helpers): `RequireSheet`, `RequireNonNegativeRow`,
  `RequireNonNegativeCol` — valid guard helpers, retain.

The ~44 test files for R441–R484 only verify guard-clause behavior, return types, and
idempotency. They do NOT test persistence through save/reload. The roundtrip test suite
(`FodsRoundtripMutationTests.cs`) already documents RT-MUT-05 as a "known gap" for font color —
the incident extends this same gap to ~25 additional properties.

Existing committed files carry the same anti-pattern: `FodsDocumentAccessor.cs` holds
`_columnWidths`, `_namedRanges`, `_activeFilters`, `_rowHeights`, and `_charts` as
detached dictionaries. `FodsDocumentExtendedApis.cs` (1,549 LOC) and
`FodsDocumentAccessor.cs` (2,623 LOC) are both in `source-structure-baseline.json` at
their LOC caps as `new_violation_detected`.

Governance gaps: no validator detects constant-return public APIs, detached dictionary
state, or "MissingMethods"-style filenames in `.NET` source.

**Intended outcome:** Eliminate the incident file; implement governance detection that
prevents recurrence; repair Category B properties to read from and write to ODF XML;
remove Category D methods along with their synthetic tests; rebuild FODS certification
from corrected evidence.

---

## Method Classification Table

| Category | Count | Disposition | Phase |
|----------|-------|-------------|-------|
| A — DOM-computed (GetSheetMaxRow, GetSheetMaxColumn) | 2 | KEEP → move to FodsDocumentAccessor | 3a |
| B — ODF XML property (freeze, zoom, alignment, fonts, colors…) | ~25 | IMPLEMENT_FROM_XML (getter reads ODF; setter writes ODF) | 3b-3d |
| C — Alias delegates (GetSheetFreezeRow, GetSheetFreezeColumn) | 2 | KEEP → move alongside B peers | 3a |
| D — Constant-zero (GetFormulaCount, GetImageCount, …67 total) | 67 | REMOVE_WITH_TESTS — delete methods + test files | 3f |
| E — Private guard helpers (RequireSheet, …) | 3 | KEEP → move to FodsDocumentAccessor | 3a |

**Category B ODF mapping (key properties):**

| Method | ODF XPath |
|--------|-----------|
| GetCellStyleName | `table:table-cell/@table:style-name` |
| GetCellHorizontalAlignment | → style lookup → `style:paragraph-properties/@fo:text-align` |
| GetCellVerticalAlignment | → style lookup → `style:table-cell-properties/@style:vertical-align` |
| GetCellFontName | → style lookup → `style:text-properties/@style:font-name` |
| GetCellFontSize | → style lookup → `style:text-properties/@fo:font-size` |
| GetCellFontColor | → style lookup → `style:text-properties/@fo:color` |
| GetCellBackgroundColor | → style lookup → `style:table-cell-properties/@fo:background-color` |
| GetCellBorderStyle | → style lookup → `style:table-cell-properties/@fo:border` |
| GetCellUnderline | → style lookup → `style:text-properties/@style:text-underline-style` |
| GetCellShrinkToFit | → style lookup → `style:table-cell-properties/@style:shrink-to-fit` |
| GetCellIndentLevel | → style lookup → `style:paragraph-properties/@fo:margin-left` |
| GetCellRotationAngle | → style lookup → `style:table-cell-properties/@style:rotation-angle` |
| GetCellProtection | → style lookup → `style:table-cell-properties/@style:cell-protect` |
| GetCellStrikethrough | → style lookup → `style:text-properties/@style:text-line-through-style` |
| GetCellMergeInfo | `table:table-cell/@table:number-rows-spanned` + `@table:number-columns-spanned` |
| GetSheetFreezeRows | `office:settings` → `config:config-item name="HorizontalSplitPosition"` |
| GetSheetFreezeColumns | `office:settings` → `config:config-item name="VerticalSplitPosition"` |
| GetSheetZoomLevel | `office:settings` → `config:config-item name="ZoomValue"` |
| GetSheetShowGrid | `office:settings` → `config:config-item name="ShowGrid"` |
| GetSheetShowHeaders | `office:settings` → `config:config-item name="HasColumnRowHeaders"` |
| GetSheetRightToLeft | → sheet style → `style:table-properties/@style:writing-mode` |
| GetSheetTabColor | → sheet style → `table:table-properties/@table:tab-color` |
| GetSheetVisibility | `table:table/@table:display` |
| GetSheetPrintArea | `table:named-range` with `table:print-range="true"` |
| GetColumnWidth | column style → `style:table-column-properties/@style:column-width` |
| GetRowHeight | row style → `style:table-row-properties/@style:row-height` |

---

## Lane Architecture (6 Lanes, 6 Sprints)

```
Sprint 1 (Days 1-5):   Lane 1 — Incident Preservation + Gap Ledger
                        Lane 2 — Governance Validators V87/V88/V89
Sprint 2 (Days 6-12):  Lane 3a — Phase 3a: MissingMethods.cs eliminated
                        Lane 4a — Test taxonomy
Sprint 3 (Days 13-22): Lane 3b — Style chain resolver (cell properties)
                        Lane 3c — config:config-item parsing (sheet view)
                        Lane 4b — Fixture creation
                        Lane 4c — Replace guard-only tests with semantic tests
                        Lane 6a — Python FODS parity spot-check
Sprint 4 (Days 23-32): Lane 3d — Column/row dimension parsing
                        Lane 3e — Serialization path repair (setters → XML)
                        Lane 4c — Roundtrip persistence tests (Type 4)
                        Lane 6b — Cross-product scan via V87
Sprint 5 (Days 33-38): Lane 3f — Category D removal
                        Lane 4d — Category D test disposal (~112 files deleted)
                        Lane 5a — Gate 11 impact assessment
Sprint 6 (Days 39-45): Lane 5b — Certification rebuild
                        Lane 5c — Gate 11 re-submission delta
```

---

## Lane 1: Incident Preservation and Gap Ledger

**Sprint 1, Days 1–2**

### 1.1 — Create incident YAML

**New file:** `reports/gov-incidents/GI-FODS-NET-001.yaml`

```yaml
incident_id: GI-FODS-NET-001
product: FODS
language: dotnet
severity: HIGH
status: REMEDIATION_IN_PROGRESS
incident_file: src/net/fods/FodsDocumentMissingMethods.cs
file_committed: false
file_loc: 622
method_count_total: 102
category_A: [GetSheetMaxRow, GetSheetMaxColumn]
category_B_count: 25
category_C: [GetSheetFreezeRow, GetSheetFreezeColumn]
category_D_count: 67
category_E: [RequireSheet, RequireNonNegativeRow, RequireNonNegativeCol]
remediation_plan: plans/.claude/buzzing-wiggling-whistle.md
```

### 1.2 — Create method ledger

**New file:** `reports/gov-incidents/GI-FODS-NET-001-method-ledger.yaml`

One entry per method with fields: `method`, `category`, `disposition`,
`odf_basis`, `test_files`, `roundtrip_gap`, `current_backing`.

### 1.3 — Add gap ledger entries

**File:** `reports/capability-layer/gap-ledger.json`

Add entries:
- `GAP-FODS-NET-SEMANTIC-STUB-001`: 67 constant-zero APIs
- `GAP-FODS-NET-DETACHED-DICT-001`: 16+ detached dictionary backing fields
- `GAP-FODS-NET-NO-STYLE-CHAIN-001`: cell properties not resolved through ODF style chain
- `GAP-FODS-NET-CONFIG-ITEMS-001`: sheet view properties not parsed from `office:settings`

---

## Lane 2: Governance Validators V87/V88/V89

**Sprint 1, Days 2–5**

### 2.1 — New validator file

**New file:** `tools/supervisor/governance_validators_dotnet_semantic.py`

Implements three validators following the existing pattern in
`tools/supervisor/governance_validators.py` (85 existing validators):

**V87: `validate_dotnet_constant_return_public_api`**
- Scans changed `src/net/**/*.cs` files using regex
- Detects: `public \w+ Get\w+\([^)]*\)\s*=>\s*(0|false|true|string\.Empty|"");\s*$`
  and multi-line `return 0;` / `return string.Empty;` method bodies
- Severity: FAIL for RELEASE_GATE items, WARN for PRODUCT_SOURCE
- `blocks_sprint: true` for RELEASE_GATE
- Whitelist file: `registry/dotnet-semantic-stub-whitelist.yaml`

**V88: `validate_dotnet_detached_dictionary_fields`**
- Scans changed `src/net/**/*.cs` files for `private readonly Dictionary` fields
  initialized in-field (`= new()`) where the dictionary variable does not appear
  in any XML read path (`Attribute(`, `Element(`, `XDocument.Load(`)
  across any partial class files in the same directory
- Severity: WARN only (advisory — heuristic, not proof)
- `blocks_sprint: false`

**V89: `validate_dotnet_missingmethods_filename`**
- FAIL if any `src/net/**/*Missing*.cs` or `src/net/**/*Stub*.cs` appears
  in `changed_files` as an addition (not a deletion)
- Severity: FAIL
- `blocks_sprint: true`

### 2.2 — Runner registration

**File:** `tools/supervisor/governance_validator_runner.py`

Add import and registration of V87/V88/V89 after the V86 block, following
the existing lazy-import pattern. Update docstring header to include V87-V89.

### 2.3 — Validator tests

**New file:** `tests/supervisor/test_governance_validators_dotnet_semantic.py`

Minimum 27 tests (9 per validator):
- V87: PASS for DOM-computed method, PASS for guard-clause body, WARN for `=> 0`,
  FAIL for RELEASE_GATE context with `=> 0`, PASS when no .NET files in changed_files
- V88: WARN when dict field has no XML reference, PASS when field appears in `XDocument.Load()`
- V89: FAIL on `*MissingMethods*.cs` addition, PASS on deletion, PASS with no .NET files

### 2.4 — Whitelist file

**New file:** `registry/dotnet-semantic-stub-whitelist.yaml`

```yaml
schema_version: "1.0"
known_constant_return_ok:
  # Architecturally intentional constants — V87 skips these
  - "FormatFactory.Fods.FodsDocument.MaxFileSizeBytes"
```

---

## Lane 3: FODS Architecture Repair

### Phase 3a — MissingMethods.cs Elimination (Sprint 2)

**Files changed:**
- `src/net/fods/FodsDocumentMissingMethods.cs` → DELETED
- `src/net/fods/FodsDocumentAccessor.cs` → receives Category A (2), C (2), E (3) methods
- `src/net/fods/FodsDocumentLegacyCounters.cs` → NEW, receives Category D (67) methods
  tagged `// PENDING REMOVAL: GI-FODS-NET-001 Phase 3f`
- `src/net/fods/FodsDocumentAccessor.cs` → receives Category B methods as
  `// TODO: GI-FODS-NET-001 Phase 3b/3c` stubs (behavior temporarily unchanged)
- `registry/source-structure-baseline.json` → add `FodsDocumentLegacyCounters.cs`
  with `category: pending_removal`

**Why staged:** The 112 test files referencing Category D methods must be rewritten
(Lane 4d) before deletion. The intermediate `FodsDocumentLegacyCounters.cs` tracks
them as governed pending-removal artifacts instead of an untracked blind spot.

**Pre-conditions:** Verify `FodsDocumentMissingMethods.cs` is still untracked
(`git status src/net/fods/`). Check if `RequireSheet` already exists in
`FodsDocumentAccessor.cs` before adding.

### Phase 3b — ODF Style Chain Resolver (Sprint 3)

**New file:** `src/net/fods/FodsStyleResolver.cs`

A standalone class (not partial FodsDocument) implementing:
```csharp
public class FodsStyleResolver {
    public static FodsCellStyle ResolveCellStyle(XDocument doc, XElement cell)
    public static FodsColumnStyle ResolveColumnStyle(XDocument doc, XElement col)
    public static FodsRowStyle ResolveRowStyle(XDocument doc, XElement row)
    private static XElement? FindStyle(XDocument doc, string name, string family)
    private static FodsCellStyle MergeWithParent(XElement style, XDocument doc)
}
```

**New record types** (in `src/net/fods/Model/`):
- `FodsCellStyle.cs`: HorizontalAlignment, VerticalAlignment, FontName, FontSize, FontColor,
  BackgroundColor, Bold, Italic, Underline, BorderTop/Bottom/Left/Right, ShrinkToFit,
  Indent, Rotation, Protection, Strikethrough, StyleName
- `FodsColumnStyle.cs`: Width (double, in cm normalized to points)
- `FodsRowStyle.cs`: Height (double, in cm normalized to points)

**ODF namespaces** to add to `FodsDocument.cs` (verify against existing namespace constants):
```csharp
private static readonly XNamespace NsStyle =
    "urn:oasis:names:tc:opendocument:xmlns:style:1.0";
private static readonly XNamespace NsConfig =
    "urn:oasis:names:tc:opendocument:xmlns:config:1.0";
// NsFo may already exist — verify URI is
// "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
```

**Update Category B cell-property getters** in `FodsDocumentAccessor.cs` to delegate to
`FodsStyleResolver.ResolveCellStyle` instead of reading detached dictionaries.

**Fixture file needed:**
`tests/net/fods/Fixtures/fods-cell-styles.fods` — handcrafted FODS with
`office:automatic-styles` containing a `style:style` with bold, 14pt, red foreground,
yellow background, center-aligned cell. This is the ground-truth for all semantic tests.

### Phase 3c — config:config-item Parsing (Sprint 3)

**New helper in `FodsDocumentAccessor.cs` (or new `FodsConfigResolver.cs`):**
```csharp
private XElement? GetConfigItem(string sheetName, string itemName)
// Navigate: office:settings → config:config-item-set →
//           config:config-item-map-named → config:config-item-map-entry →
//           config:config-item[@config:name=itemName]
```

**Update Category B sheet-view getters:**
- `GetSheetFreezeRows` → `HorizontalSplitPosition` (when `HorizontalSplitMode == 2`)
- `GetSheetFreezeColumns` → `VerticalSplitPosition` (when `VerticalSplitMode == 2`)
- `GetSheetZoomLevel` → `ZoomValue` (default 100)
- `GetSheetShowGrid` → `ShowGrid` (default true)
- `GetSheetShowHeaders` → `HasColumnRowHeaders` (default true)

**Fixture file needed:**
`tests/net/fods/Fixtures/fods-sheet-view-settings.fods` — includes `office:settings`
section with freeze pane (HorizontalSplitMode=2, HorizontalSplitPosition=2) and
ZoomValue=150, ShowGrid=false.

### Phase 3d — Column and Row Dimension Parsing (Sprint 4)

**File:** `src/net/fods/FodsDocumentAccessor.cs`

Replace `_columnWidths` and `_rowHeights` dictionary backing (committed anti-patterns)
with XML-backed reads via `FodsStyleResolver`:

```csharp
// Before (anti-pattern):
return _columnWidths.TryGetValue((sheetName, col), out var w) ? w : 0.0;

// After (ODF-grounded):
var colEl = GetTableColumnElement(sheetName, col);
return colEl is null ? 0.0 : FodsStyleResolver.ResolveColumnStyle(_doc, colEl).Width;
```

**Fixture file needed:**
`tests/net/fods/Fixtures/fods-column-widths.fods` — columns with explicit widths
encoded in `office:automatic-styles`.

### Phase 3e — Serialization Path Repair (Sprint 4)

**New file:** `src/net/fods/FodsStyleEditor.cs`

Implements setter path: given a property change, update the correct ODF XML node:
```csharp
public class FodsStyleEditor {
    public static void SetCellProperty(XDocument doc, XElement cell,
        string family, string elementName, XName attribute, string value)
    // 1. Read cell's @table:style-name
    // 2. Find or create auto-style in office:automatic-styles
    // 3. Write property to appropriate style:*-properties element
    // 4. Update cell's @table:style-name if new style was created
}
```

**Update Category B setters** in `FodsDocumentAccessor.cs` to delegate to
`FodsStyleEditor.SetCellProperty` instead of writing to detached dictionaries.

**RT-MUT-05 disposition:** Remove the `Roundtrip_SetCellFontColor_DoesNotPersist_KnownGap`
skip/known-gap test from `FodsRoundtripMutationTests.cs`. Replace with:
```csharp
[Fact]
public void RT_MUT_05_HEALED_SetCellFontColor_Roundtrips()
{
    var doc = FodsDocument.Load("Fixtures/fods-cell-styles.fods");
    doc.SetCellFontColor("Sheet1", 0, 0, "#FF0000");
    var reloaded = FodsDocument.LoadFromXml(doc.ToFodsXml());
    Assert.Equal("#FF0000", reloaded.GetCellFontColor("Sheet1", 0, 0));
}
```

### Phase 3f — Category D Removal (Sprint 5)

**Pre-condition:** All Lane 4d test rewrites must be complete first.

1. Delete all 67 Category D method bodies from `FodsDocumentLegacyCounters.cs`
2. Delete `FodsDocumentLegacyCounters.cs`
3. Remove its entry from `registry/source-structure-baseline.json`

**Computable replacements for 3 of the 67 (where real ODF scan is possible):**
- `GetFormulaCount` → count `@table:formula` attributes across all cells — add to accessor
- `GetMergedCellCount` → count cells with `@table:number-columns-spanned > 1` — add to accessor
- `GetHyperlinkCount` → count `text:a` elements inside cells — add to accessor

The remaining 64 methods have no ODF basis and are simply removed with no replacement.

---

## Lane 4: Test Repair

### Phase 4a — Test Taxonomy (Sprint 2)

Classify all ~660 FODS test files into:
- **Type 1 — Guard-only:** Null checks, idempotency, `>= 0` assertions only
- **Type 2 — In-memory round-trip:** Set→Get within same instance (no persistence)
- **Type 3 — ODF semantic:** Loads fixture, asserts known value from ODF XML
- **Type 4 — Persistence round-trip:** Save→reload→assert survives

Category D tests are almost entirely Type 1. Category B tests are Type 1/2.
Target after repair: Category B tests upgraded to Type 3 and Type 4.

### Phase 4b — Fixture Creation (Sprint 3)

Create the following fixtures (hand-crafted or via LibreOffice for spec conformance):
1. `tests/net/fods/Fixtures/fods-cell-styles.fods` — explicit `office:automatic-styles`
2. `tests/net/fods/Fixtures/fods-sheet-view-settings.fods` — `office:settings` freeze/zoom
3. `tests/net/fods/Fixtures/fods-column-widths.fods` — column dimension styles
4. Verify `tests/net/fods/Fixtures/fods-merged-cells.fods` has correct ODF span attributes

### Phase 4c — Category B Test Replacement (Sprint 3–4)

For each Category B method, replace the existing test class with tests that:
1. Load the relevant fixture
2. Assert the exact known value (e.g., `Assert.Equal(14.0, doc.GetCellFontSize("Sheet1", 0, 0))`)
3. Assert persistence through `ToFodsXml()` → `LoadFromXml()` roundtrip

Example replacement for `FodsR455GetCellHorizontalAlignmentDedicatedTests.cs`:
```csharp
[Fact]
public void GetCellHorizontalAlignment_FromFixture_ReturnsCenterFromOdf()
{
    var doc = FodsDocument.Load("Fixtures/fods-cell-styles.fods");
    Assert.Equal("center", doc.GetCellHorizontalAlignment("Sheet1", 0, 0));
}

[Fact]
public void SetCellHorizontalAlignment_Roundtrips_ThroughSaveReload()
{
    var doc = FodsDocument.CreateNew();
    doc.AddSheet("Sheet1");
    doc.SetCellValue("Sheet1", 0, 0, "test");
    doc.SetCellHorizontalAlignment("Sheet1", 0, 0, "end");
    var reloaded = FodsDocument.LoadFromXml(doc.ToFodsXml());
    Assert.Equal("end", reloaded.GetCellHorizontalAlignment("Sheet1", 0, 0));
}
```

### Phase 4d — Category D Test Disposal (Sprint 5)

For each of the ~112 test files testing Category D methods:
- If tests only contain Type 1 assertions (`>= 0`, idempotency, guard-clause): **delete the file**
- If tests contain any semantic assertion: investigate and document before deletion
- Log all deletions in `reports/gov-incidents/GI-FODS-NET-001-test-disposal-log.yaml`

**Expected impact:** ~660 → ~548 test files; ~700 test assertions removed.
This must be disclosed in the Gate 11 evidence delta (Lane 5c).

---

## Lane 5: Certification Repair

### Phase 5a — Gate 11 Impact Assessment (Sprint 5)

Review which of the current 8/31 Gate 11 criteria relied on R441-R484 test evidence.
Files: `acquisition-packs/fods/gate11-packaging-plan.md`, `registry/gate11-criteria.yaml`.

Key criteria analysis:
- `commercial_test_count_min: 10` — 548 remaining tests still far exceeds threshold
- `min_api_coverage: 0.6` — removing 67 non-spec APIs IMPROVES this metric
- `dogfood_proof_required: true` — unaffected (dogfood uses real load/edit/export APIs)

### Phase 5b — Certification Rebuild (Sprint 6)

Create `acquisition-packs/fods/gate11-evidence-v2.yaml` documenting:
- Which prior test evidence is superseded (Category D removed, Category B upgraded)
- New Type 3/4 tests as genuine behavioral proof
- RT-MUT-05 inversion as persistence proof
- ODF 1.3 spec citations for each Category B property

### Phase 5c — Gate 11 Re-submission Delta (Sprint 6)

Prepare delta document for Babar Raza's review with honest accounting:
- Methods removed: 67 (Category D, no ODF spec basis)
- Tests removed: ~112 files / ~700 assertions (Type 1 synthetic only)
- Methods upgraded: ~25 (Category B, stub → ODF-grounded)
- Roundtrip persistence tests added: ~25 new Type 4 tests
- Net correctness change: positive (was 0% spec-grounded, now 100% for these APIs)

---

## Lane 6: Cross-Product Scan

### Phase 6a — Python FODS Spot-Check (Sprint 3)

Verify `src/python/fods/spreadsheet_document.py` (42KB) reads cell style properties
from the ODF style chain (not detached dicts). Python governance (V44, V48, V69)
already runs; this is a confirmatory check.

### Phase 6b — .NET Cross-Product Scan via V87 (Sprint 4)

Run V87 against all `src/net/**/*.cs` files to produce a complete constant-return
inventory. Known candidates:
- `src/net/fodt/FodtDocumentExtendedApis.cs` (2,944 LOC, baseline cap) — highest risk
- Other .NET products: csv, html, markdown, ndjson, tsv, txt, zst

If V87 finds violations in FODT, open `GI-FODT-NET-001` with the same lane structure.

---

## Governance Pilots (Required for Completion Gate)

| Pilot | Description | Sprint |
|-------|-------------|--------|
| P7 — Semantic stub detection | Introduce a disposable `=> 0` method → V87 fires | 2 |
| P8 — Suspicious filename detection | Introduce a disposable `*MissingMethods*.cs` → V89 fires | 2 |
| P1 — Document inspection | Load `fods-cell-styles.fods`, verify font color from parsed ODF | 3 |
| P2 — Edit and round-trip | Set font color → `ToFodsXml()` → `LoadFromXml()` → verify | 4 |
| P3 — Preservation | Modify alignment, prove formulas/values/styles survive | 4 |
| P4 — Unsupported feature | `GetMacroCount()` removed → compile error proves intent | 5 |
| P5 — Invalid domain value | `SetCellHorizontalAlignment("invalid")` → throws or normalizes | 4 |
| P10 — Idempotency | Second run produces no unexpected changes | 6 |

---

## Completion Gate Counters

These counters must all reach zero before plan is closed:

```
INCIDENT_METHODS_NOT_REVIEWED = 0              (102 methods → all classified in ledger)
RETAINED_APIS_WITHOUT_AUTHORITY = 0            (0 Category D methods remain)
RETAINED_SETTERS_WITHOUT_SERIALIZATION = 0     (0 Category B setters remain dict-backed)
RETAINED_GETTERS_WITHOUT_PARSED_OR_MODEL_STATE = 0  (0 Category B getters remain dict-backed)
DETACHED_PRODUCT_STATE_STORES = 0              (all backing dicts wired or removed)
TEST_ONLY_PUBLIC_APIS = 0                      (Category D removed)
MISSING_METHODS_STYLE_PRODUCT_FILES = 0        (FodsDocumentMissingMethods.cs deleted)
MATERIAL_FINDINGS_WITHOUT_GAPS = 0             (4 gap ledger entries written)
ACTIONABLE_GAPS_WITHOUT_TASKS = 0              (all gaps linked to lanes/sprints)
FAILED_REQUIRED_PILOTS = 0                     (all 8 pilots pass)
FABRICATED_DEFAULT_SUCCESS_APIS = 0            (no "visible" / "normal" / "none" defaults
                                                remaining for unimplemented ODF properties)
FALSE_CERTIFICATIONS_NOT_REOPENED = 0          (Gate 11 evidence packet v2 prepared)
```

---

## Critical Files

| File | Action |
|------|--------|
| `src/net/fods/FodsDocumentMissingMethods.cs` | DELETE (Phase 3a) |
| `src/net/fods/FodsDocumentLegacyCounters.cs` | CREATE then DELETE (Phase 3a → 3f) |
| `src/net/fods/FodsStyleResolver.cs` | CREATE (Phase 3b) |
| `src/net/fods/FodsStyleEditor.cs` | CREATE (Phase 3e) |
| `src/net/fods/Model/FodsCellStyle.cs` | CREATE (Phase 3b) |
| `src/net/fods/Model/FodsColumnStyle.cs` | CREATE (Phase 3b) |
| `src/net/fods/Model/FodsRowStyle.cs` | CREATE (Phase 3b) |
| `src/net/fods/FodsDocumentAccessor.cs` | MODIFY — receive Category A/C/E, update B getters/setters |
| `src/net/fods/FodsDocument.cs` | MODIFY — add missing ODF namespace constants |
| `tests/net/fods/FodsRoundtripMutationTests.cs` | MODIFY — invert RT-MUT-05 |
| `tests/net/fods/Fixtures/fods-cell-styles.fods` | CREATE |
| `tests/net/fods/Fixtures/fods-sheet-view-settings.fods` | CREATE |
| `tests/net/fods/Fixtures/fods-column-widths.fods` | CREATE |
| `tools/supervisor/governance_validators_dotnet_semantic.py` | CREATE (V87/V88/V89) |
| `tools/supervisor/governance_validator_runner.py` | MODIFY — register V87/V88/V89 |
| `tests/supervisor/test_governance_validators_dotnet_semantic.py` | CREATE (27 tests) |
| `registry/dotnet-semantic-stub-whitelist.yaml` | CREATE |
| `reports/gov-incidents/GI-FODS-NET-001.yaml` | CREATE |
| `reports/gov-incidents/GI-FODS-NET-001-method-ledger.yaml` | CREATE |
| `reports/capability-layer/gap-ledger.json` | MODIFY — add 4 gap entries |
| `registry/source-structure-baseline.json` | MODIFY — add LegacyCounters.cs, then remove |
| `acquisition-packs/fods/gate11-evidence-v2.yaml` | CREATE (Sprint 6) |

---

## Verification

**Sprint 1 (governance) verification:**
- `python tools/supervisor/governance_validator_runner.py` — V87/V88/V89 appear in output
- `tests/supervisor/test_governance_validators_dotnet_semantic.py` — 27/27 PASS
- Introduce a `GetFakeCount() => 0` in a test file → V87 WARN fires as expected

**Sprint 2 (file elimination) verification:**
- `git status src/net/fods/` — `FodsDocumentMissingMethods.cs` must NOT appear (deleted)
- `FodsDocumentLegacyCounters.cs` must appear as tracked
- `dotnet build src/net/fods/FormatFactory.Fods.csproj` — PASS

**Sprint 3 (ODF style resolver) verification:**
- Load `fods-cell-styles.fods` → `GetCellFontSize("Sheet1", 0, 0)` returns 14.0
- Load `fods-sheet-view-settings.fods` → `GetSheetFreezeRows("Sheet1")` returns 2
- Run all Category B test files → PASS (now with fixture-based assertions)

**Sprint 4 (serialization) verification:**
- `FodsRoundtripMutationTests.cs` → RT-MUT-05 replaced test PASS
- Set font color on new doc → `ToFodsXml()` → `LoadFromXml()` → get font color → matches
- V87 scan over all `src/net/` → zero new violations

**Sprint 5 (Category D removal) verification:**
- `dotnet build` PASS with `FodsDocumentLegacyCounters.cs` deleted
- `dotnet test tests/net/fods/` PASS with ~112 deleted test files
- `FodsDocumentLegacyCounters.cs` absent from `git status`

**Sprint 6 (certification) verification:**
- `acquisition-packs/fods/gate11-evidence-v2.yaml` exists and is valid YAML
- Zero completion-gate counters remain non-zero
- Second run of `dotnet test tests/net/fods/` produces identical results (idempotency)

---

## Key Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| ODF style chain complexity slips Phase 3b | Implement `FodsStyleResolver` as standalone testable class with unit tests against XML strings before wiring to document API |
| FodsDocumentAccessor LOC cap (2,623) blocks additions | FodsStyleResolver handles resolution logic; accessor becomes thin delegate; Phase 3a removal frees headroom |
| 112 test deletions alarm Gate 11 | Disclose proactively in evidence v2: removed tests were tautologically-true guard-only assertions; replacement tests are stronger |
| Category D removal before tests rewritten breaks CI | Phase 3a uses intermediate `FodsDocumentLegacyCounters.cs` as controlled staging; tests are rewritten in Lane 4d before Phase 3f deletes the methods |
| `GetColumnWidth` / `GetRowHeight` setter behavior changes | New XML-backed path must handle `CreateNew()` docs with no `office:automatic-styles`; setter must create the section if absent |

---

## Taskcards

| TC-ID | Title | Lane | Sprint | Status |
|-------|-------|------|--------|--------|
| TC-GI001-L1-001 | Write GI-FODS-NET-001.yaml incident record | 1 | 1 | CLOSED |
| TC-GI001-L1-002 | Write GI-FODS-NET-001-method-ledger.yaml (102 methods) | 1 | 1 | CLOSED |
| TC-GI001-L1-003 | Add 4 gap entries to gap-ledger.json | 1 | 1 | CLOSED |
| TC-GI001-L2-001 | Implement V87/V88/V89 in governance_validators_dotnet_semantic.py | 2 | 1 | CLOSED |
| TC-GI001-L2-002 | Register V87/V88/V89 in governance_validator_runner.py | 2 | 1 | CLOSED |
| TC-GI001-L2-003 | Write 27 validator tests in test_governance_validators_dotnet_semantic.py | 2 | 1 | CLOSED |
| TC-GI001-L2-004 | Create registry/dotnet-semantic-stub-whitelist.yaml | 2 | 1 | CLOSED |
| TC-GI001-L3A-001 | Move Category A/C/E methods to FodsDocumentAccessor | 3a | 2 | CLOSED |
| TC-GI001-L3A-002 | Create FodsDocumentLegacyCounters.cs with Category D + baseline entry | 3a | 2 | CLOSED |
| TC-GI001-L3A-003 | Move Category B stubs to FodsDocumentAccessor with TODO comments | 3a | 2 | CLOSED |
| TC-GI001-L3A-004 | Delete FodsDocumentMissingMethods.cs | 3a | 2 | CLOSED |
| TC-GI001-L4A-001 | Classify all 660 FODS test files by type (1/2/3/4) | 4a | 2 | CLOSED |
| TC-GI001-L3B-001 | Implement FodsStyleResolver.cs with style chain resolution | 3b | 3 | PENDING |
| TC-GI001-L3B-002 | Implement FodsCellStyle / FodsColumnStyle / FodsRowStyle records | 3b | 3 | PENDING |
| TC-GI001-L3B-003 | Update Category B cell-property getters to use FodsStyleResolver | 3b | 3 | PENDING |
| TC-GI001-L3C-001 | Implement config:config-item parsing in FodsDocumentAccessor | 3c | 3 | PENDING |
| TC-GI001-L3C-002 | Update Category B sheet-view getters to use config resolver | 3c | 3 | PENDING |
| TC-GI001-L4B-001 | Create fods-cell-styles.fods fixture | 4b | 3 | PENDING |
| TC-GI001-L4B-002 | Create fods-sheet-view-settings.fods fixture | 4b | 3 | PENDING |
| TC-GI001-L4B-003 | Create fods-column-widths.fods fixture | 4b | 3 | PENDING |
| TC-GI001-L4C-001 | Replace Category B test files with Type 3 (semantic) tests | 4c | 3-4 | PENDING |
| TC-GI001-L6A-001 | Python FODS spot-check (style chain vs dict) | 6a | 3 | PENDING |
| TC-GI001-L3D-001 | Replace _columnWidths/_rowHeights with FodsStyleResolver backing | 3d | 4 | PENDING |
| TC-GI001-L3E-001 | Implement FodsStyleEditor.cs (setter → XML path) | 3e | 4 | PENDING |
| TC-GI001-L3E-002 | Update Category B setters to use FodsStyleEditor | 3e | 4 | PENDING |
| TC-GI001-L3E-003 | Invert RT-MUT-05: remove known-gap test, add passing roundtrip test | 3e | 4 | PENDING |
| TC-GI001-L4C-002 | Add Type 4 (persistence roundtrip) tests for Category B | 4c | 4 | PENDING |
| TC-GI001-L6B-001 | Run V87 cross-product scan on all src/net/ | 6b | 4 | PENDING |
| TC-GI001-L3F-001 | Rewrite/delete Category D test files (Lane 4d) — prerequisite | 3f | 5 | PENDING |
| TC-GI001-L3F-002 | Delete FodsDocumentLegacyCounters.cs + remove baseline entry | 3f | 5 | PENDING |
| TC-GI001-L5A-001 | Gate 11 impact assessment: classify which criteria used stub evidence | 5a | 5 | PENDING |
| TC-GI001-L5B-001 | Create gate11-evidence-v2.yaml from corrected implementation evidence | 5b | 6 | PENDING |
| TC-GI001-L5C-001 | Prepare Gate 11 re-submission delta for Babar Raza | 5c | 6 | PENDING |

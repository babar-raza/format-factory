# Product Library Architecture and Generation System Healing
# Plan ID: gleaming-rolling-hammock
# Mission: GI-FODS-NET-001 + Systemic Architecture Healing
# Created: 2026-07-03

## Context

The FODS .NET commercial library (FormatFactory.Fods) was identified as a product architecture
incident (GI-FODS-NET-001). Investigation revealed three systemic failure modes:

1. **Semantic stubs**: 67 public methods return constant zero/false/empty with no ODF basis
   (Category D — `GetFormulaCount`, `GetImageCount`, etc.)
2. **Detached dictionaries**: ~25 property getters/setters backed by in-memory dictionaries
   never populated by the parser and never flushed by the writer — state is lost on every
   save/reload (Category B)
3. **Dead infrastructure**: `FodsStyleResolver.cs` (344 LOC), fixture files, and model
   records were created but never wired into the public API

Root cause: agents were rewarded for API quantity and test compilation, not specification
derivation, persistence proof, or professional architecture.

Two prior plans partially remediated the product defects:
- `plans/.claude/buzzing-wiggling-whistle.md` — Lanes 1-4, 6 CLOSED; Lane 3f/5 PENDING
- `plans/.claude/agile-rolling-marshmallow.md` — TC-GI001-001 through TC-GI001-010 PENDING

**This plan absorbs those pending taskcards and extends the mission** to cover:
- Formal architecture documentation (incident baseline, problem taxonomy, runtime map)
- Systemic machinery healing (skills, validators, generation rules)
- Certification rebuild (Gate 11 evidence v2)
- Cross-product discovery and FODT incident remediation
- Pilots, professional review, and idempotency proof

**Example product**: FODS .NET (`src/net/fods/`)
**Spec authority**: OASIS ODF 1.3, 5,009 SAL facts in `.local/sal-output/sal-facts-fods.json`
**QName sources**: `src/net/fods/Spec/` (4 canonical classes)

---

## Prior Work Status (DO NOT REPEAT)

| Component | Status | Evidence |
|-----------|--------|----------|
| GI-FODS-NET-001.yaml incident record | DONE | `reports/gov-incidents/GI-FODS-NET-001.yaml` |
| Method ledger (102 methods) | DONE | `reports/gov-incidents/GI-FODS-NET-001-method-ledger.yaml` |
| V87/V88/V89 governance validators | DONE | `tools/supervisor/governance_validators_dotnet_semantic.py` |
| Category A/C/E moved to FodsDocumentAccessor | DONE | `src/net/fods/FodsDocumentAccessor.cs` |
| Category D staged in FodsDocumentLegacyCounters | DONE | `src/net/fods/FodsDocumentLegacyCounters.cs` |
| FodsStyleResolver.cs implemented | DONE | `src/net/fods/FodsStyleResolver.cs` |
| FodsStyleEditor.cs implemented | DONE | `src/net/fods/FodsStyleEditor.cs` |
| FodsOdfCellStyle/ColumnStyle/RowStyle records | DONE | `src/net/fods/Model/Fods*Style.cs` |
| Category B getters wired to FodsStyleResolver | DONE | `src/net/fods/FodsDocumentAccessor.cs` |
| config:config-item parsing | DONE | `src/net/fods/FodsDocumentAccessor.cs` |
| Column/row dimension XML-backed reads | DONE | `src/net/fods/FodsDocumentAccessor.cs` |
| Category B setters wired to FodsStyleEditor | DONE | `src/net/fods/FodsDocumentAccessor.cs` |
| RT-MUT-05 inverted (known gap → passing test) | DONE | `tests/net/fods/FodsRoundtripMutationTests.cs` |
| Category B Type 3+4 tests | DONE | `tests/net/fods/FodsGI001CategoryBRoundtripTests.cs` |
| Fixture files created | DONE | `tests/net/fods/Fixtures/fods-cell-styles.fods` etc. |
| ~80+ Category D test files deleted | DONE | git status D entries |
| Python FODS spot-check (style chain) | DONE | Lane 6a |
| V87 cross-product scan (all src/net/) | DONE | `reports/gov-incidents/V87-scan-results-2026-07-02.yaml` |
| GI-FODT-NET-001 opened | DONE | `reports/gov-incidents/GI-FODT-NET-001.yaml` |

---

## Taskcard Status Summary Table

| TC-ID | Title | Group | Status |
|-------|-------|-------|--------|
| TC-GHH-A001 | Register 3 fixture files in .csproj | A | CLOSED |
| TC-GHH-A002 | Baseline dotnet test run | A | CLOSED |
| TC-GHH-A003 | Wire GetResolvedCellStyle into public API | A | CLOSED |
| TC-GHH-A004 | Wire GetResolvedColumnStyle/RowStyle | A | CLOSED |
| TC-GHH-A005 | Write 6 Type3 ODF-semantic tests | A | CLOSED |
| TC-GHH-A006 | Triage 152 excluded test files | A | CLOSED |
| TC-GHH-A007 | Re-enable Class A excluded files | A | CLOSED |
| TC-GHH-A008 | Delete FodsDocumentLegacyCounters.cs | A | CLOSED |
| TC-GHH-B001 | Write incident-baseline.yaml | B | CLOSED |
| TC-GHH-B002 | Write problem-taxonomy.yaml | B | CLOSED |
| TC-GHH-B003 | Write current-runtime-map.yaml | B | CLOSED |
| TC-GHH-B004 | Write systemic-cause-analysis.yaml | B | CLOSED |
| TC-GHH-C001 | Write target-product-architecture.yaml | C | CLOSED |
| TC-GHH-C002 | Add V90-V92 governance validators | C | CLOSED |
| TC-GHH-C003 | Update add-dotnet-api skill for QName authority | C | CLOSED |
| TC-GHH-C004 | Build product-quality-gap-ledger.yaml | C | CLOSED |
| TC-GHH-D001 | Gate 11 impact assessment | D | CLOSED |
| TC-GHH-D002 | Create gate11-evidence-v2.yaml | D | CLOSED |
| TC-GHH-D003 | Gate 11 re-submission delta for Babar Raza | D | CLOSED |
| TC-GHH-E001 | FODT: read every file + classify symbols | E | CLOSED |
| TC-GHH-E002 | FODT: remove/replace constant-zero APIs | E | CLOSED |
| TC-GHH-E003 | FODT: dotnet build + test verification | E | CLOSED |
| TC-GHH-F001 | Run pilots P1-P3, P5, P7-P8, P10 | F | CLOSED |
| TC-GHH-F002 | Manual professional review — FODS .NET | F | CLOSED |
| TC-GHH-F003 | Update test taxonomy JSON | F | CLOSED |
| TC-GHH-F004 | Commit all changes + idempotency proof | F | CLOSED |

---

## Group A: Complete In-Progress Repairs

These are the pending taskcards from agile-rolling-marshmallow (TC-GI001-001 through
TC-GI001-010) and buzzing-wiggling-whistle (Lane 3f, TC-GI001-L3F-002).

### TC-GHH-A001: Register 3 Fixture Files in .csproj

**Objective:** Make fods-cell-styles.fods, fods-column-widths.fods, fods-sheet-view-settings.fods
copy to output so tests can load them.

**File:** `tests/net/fods/FormatFactory.Fods.Tests.csproj`

**Change:** After the existing `multi-sheet-basic.fods` Content block, add:
```xml
<Content Include="Fixtures\fods-cell-styles.fods">
  <CopyToOutputDirectory>Always</CopyToOutputDirectory>
</Content>
<Content Include="Fixtures\fods-column-widths.fods">
  <CopyToOutputDirectory>Always</CopyToOutputDirectory>
</Content>
<Content Include="Fixtures\fods-sheet-view-settings.fods">
  <CopyToOutputDirectory>Always</CopyToOutputDirectory>
</Content>
```

**Verification:** `dotnet build tests/net/fods/FormatFactory.Fods.Tests.csproj` exits 0;
`ls tests/net/fods/bin/Debug/net10.0/Fixtures/` shows 4 files.

**Evidence:** `.local/evidences/GI-FODS-NET-001/TC-A001-fixture-build.txt`
**Rollback:** Remove the 3 Content entries.

---

### TC-GHH-A002: Baseline dotnet test Run

**Objective:** Record test counts before further changes.

**Command:** `dotnet test tests/net/fods/FormatFactory.Fods.Tests.csproj --verbosity normal`

**Output:** Write counts to `.local/evidences/GI-FODS-NET-001/baseline-state.json`
```json
{"total": N, "passed": N, "failed": N, "skipped": N, "timestamp": "..."}
```

**Rollback:** N/A (read-only).

---

### TC-GHH-A003: Wire GetResolvedCellStyle into Public API

**Objective:** Fix F001 (dead code) and F005 (Type3=0). FodsStyleResolver must be reachable.

**Pre-execution lookups (required):**
1. `grep -n "XDocument\|private.*_doc" src/net/fods/FodsDocumentAccessor.cs` — find XDocument field name
2. `grep -n "public.*static.*FodsDocument" src/net/fods/FodsDocument.cs` — find load method name
3. `grep -n 'table:name' tests/net/fods/Fixtures/fods-cell-styles.fods` — verify sheet name

**File:** `src/net/fods/FodsDocumentAccessor.cs`

**Add two new methods** (do NOT remove existing `GetCellStyle()` string-returning overloads):
```csharp
/// <summary>
/// Resolve the full ODF style chain for a cell and return typed style properties.
/// Returns null if cell/sheet not found. R114-B — ODF-semantic style retrieval.
/// </summary>
public FodsOdfCellStyle? GetResolvedCellStyle(string sheetName, int row, int col)
{
    if (string.IsNullOrWhiteSpace(sheetName))
        throw new ArgumentException("sheetName must not be null or empty.", nameof(sheetName));
    if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
    if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
    var sheet = GetSheetByName(sheetName)
        ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
    if (row >= sheet.Rows.Count) return null;
    var r = sheet.Rows[row];
    if (col >= r.Cells.Count) return null;
    return FodsStyleResolver.ResolveCellStyle(<XDocumentField>, r.Cells[col].Element);
}

/// <summary>GetResolvedCellStyle from the first (active) sheet.</summary>
public FodsOdfCellStyle? GetResolvedCellStyle(int row, int col)
{
    var sheets = Sheets;
    return sheets.Count == 0 ? null : GetResolvedCellStyle(sheets[0].Name!, row, col);
}
```
Replace `<XDocumentField>` with actual field name from lookup above.

**Verification:** `dotnet build` exits 0; `grep -c GetResolvedCellStyle src/net/fods/FodsDocumentAccessor.cs` >= 2.
**Evidence:** `.local/evidences/GI-FODS-NET-001/TC-A003-build.txt`

---

### TC-GHH-A004: Wire GetResolvedColumnStyle and GetResolvedRowStyle

**Objective:** Expose resolver for column/row dimensions (F008).

**File:** `src/net/fods/FodsDocumentAccessor.cs`

**Add two methods** following the same guard+delegate pattern:
```csharp
public FodsOdfColumnStyle? GetResolvedColumnStyle(string sheetName, int col) { ... }
public FodsOdfRowStyle? GetResolvedRowStyle(string sheetName, int row) { ... }
```
Delegate to `FodsStyleResolver.ResolveColumnStyle/ResolveRowStyle`.

**Verification:** `dotnet build` exits 0.
**Evidence:** `.local/evidences/GI-FODS-NET-001/TC-A004-build.txt`

---

### TC-GHH-A005: Write 6 Type3 ODF-Semantic Tests

**Objective:** Advance Type3 count from 0 to >= 6. Prove FodsStyleResolver on real files.

**New file:** `tests/net/fods/FodsR255GetResolvedStyleDedicatedTests.cs`

| Test | Fixture | API | Assertion |
|------|---------|-----|-----------|
| T1 | fods-cell-styles.fods | GetResolvedCellStyle("Sheet1",0,0) | not null |
| T2 | fods-cell-styles.fods | GetResolvedCellStyle("Sheet1",0,0) | FontName not null/empty |
| T3 | fods-cell-styles.fods | GetResolvedCellStyle("Sheet1",0,0) | FontSize ≈ 14.0 (±0.1) |
| T4 | fods-cell-styles.fods | GetResolvedCellStyle("Sheet1",0,1) | null OR all-default |
| T5 | fods-column-widths.fods | GetResolvedColumnStyle("Sheet1",0) | Width > 0 |
| T6 | fods-column-widths.fods | GetResolvedRowStyle("Sheet1",0) | Height > 0 |

**Fixture path pattern:** `Path.Combine(AppContext.BaseDirectory, "Fixtures", "<filename>")`.

Verify actual sheet name from the fixture XML before writing (see A003 pre-execution lookup).

**Verification:** `dotnet test --filter "FodsR255GetResolvedStyleDedicatedTests"` → 6/6 pass.
**Evidence:** `.local/evidences/GI-FODS-NET-001/TC-A005-type3-run.txt`

---

### TC-GHH-A006: Triage 152 Excluded Test Files

**Objective:** Determine which excluded files have APIs now implemented vs still missing.

**File:** `tests/net/fods/FormatFactory.Fods.Tests.csproj` — read all `<Compile Remove>` entries.

**For each of 152 files, classify:**
- **Class A:** Referenced API exists in Accessor.cs/ExtendedApis.cs and is NOT a stub/constant-return → safe to re-enable
- **Class B:** API exists but is a stub or returns default without ODF grounding → would fail test
- **Class C:** API absent → stays excluded

**Output:** `.local/evidences/GI-FODS-NET-001/excluded-triage.json`
```json
[{"file": "FodsRNNNTests.cs", "class": "A|B|C", "api": "MethodName", "api_status": "..."}]
```

**Verification:** JSON has 152 entries; `python -c "import json; d=json.load(open('...')); print(len(d))"` = 152.

---

### TC-GHH-A007: Re-enable Class A Excluded Files

**Objective:** Restore test coverage for implemented APIs. Zero Class B/C re-inclusions.

**Execution:**
1. Remove `<Compile Remove>` entries for Class A files only
2. `dotnet build` → must exit 0
3. `dotnet test` → record new counts
4. Any re-enabled test that FAILS → reclassify as Class B; re-add exclusion

**Anti-overclaim:** Do NOT re-enable a file unless its test passes. Do not count building as passing.

**Verification:** Net reduction in excluded count >= 1; zero regressions vs baseline-state.json.
**Evidence:** `.local/evidences/GI-FODS-NET-001/TC-A007-reenable.txt`

---

### TC-GHH-A008: Delete FodsDocumentLegacyCounters.cs

**Pre-condition:** TC-GHH-A007 complete (Lane 4d test disposal confirmed done).

**Objective:** Remove the 67 Category D constant-zero APIs permanently. This is the
final step of buzzing-wiggling-whistle Lane 3f.

**Execution:**
1. Verify `src/net/fods/FodsDocumentLegacyCounters.cs` exists and contains only Category D methods
2. Delete the file
3. Remove its entry from `registry/source-structure-baseline.json`
4. `dotnet build src/net/fods/FormatFactory.Fods.csproj` → must exit 0
5. `dotnet test tests/net/fods/` → must match or exceed TC-GHH-A007 passing count

**Special case:** 3 methods have real ODF-computable replacements:
- `GetFormulaCount` → count cells with `@table:formula` attribute → add to Accessor
- `GetMergedCellCount` → count cells with `@table:number-columns-spanned > 1` → add to Accessor
- `GetHyperlinkCount` → count `text:a` elements inside cells → add to Accessor

These 3 must be re-implemented in FodsDocumentAccessor.cs BEFORE deleting LegacyCounters.

**Verification:** `git status src/net/fods/FodsDocumentLegacyCounters.cs` shows deleted;
`dotnet build` exits 0; `dotnet test` passes.
**Evidence:** `.local/evidences/GI-FODS-NET-001/TC-A008-deletion.txt`

---

## Group B: Formal Architecture Documentation

Produce the artifacts required by the healing mission brief §2–§8.
These are governance evidence outputs, not product code.

### TC-GHH-B001: Write Incident Baseline (§2)

**Objective:** Freeze the pre-repair state as recoverable evidence.

**New file:** `reports/product-architecture/incident-baseline.yaml`

Must include:
```yaml
product_quality_incident:
  incident_id: GI-FODS-NET-001
  repository: format-factory
  branch: main
  head: <current HEAD SHA>
  plan_path: plans/.claude/gleaming-rolling-hammock.md
  example_product: src/net/fods/
  product_roots: [src/net/fods/]
  spec_sources: [OASIS ODF 1.3]
  sal_sources: [.local/sal-output/sal-facts-fods.json]
  qname_sources: [src/net/fods/Spec/]
  capability_sources: [.governance/capabilities/registry.yaml]
  generation_entry_points: [.supervisor/skill-registry.yaml]
  skills: [add-dotnet-api, add-dotnet-object-model-feature, add-roundtrip-test]
  task_sources: [plans/.claude/buzzing-wiggling-whistle.md]
  certification_sources: [acquisition-packs/fods/]
  evidence_roots: [reports/gov-incidents/]

pre_repair_snapshot:
  source_files: 23
  source_lines_total: 9492
  public_types: 38
  public_methods_properties: ~421
  test_files: 573
  excluded_test_files: 152
  type1_guard_only: 249
  type2_in_memory: 402
  type3_odf_semantic: 0
  type4_roundtrip: 3
  partial_class_files: 4  # FodsDocument.cs + 3 extensions
  detached_dict_fields: 8  # _columnWidths, _namedRanges, _activeFilters, _rowHeights, etc.
  constant_zero_apis: 67
  dead_code_lines: 445  # FodsStyleResolver + model records, unconnected
  gate11_criteria_met: 8
  gate11_criteria_total: 31
```

**Verification:** `python -c "import yaml; yaml.safe_load(open(...))"` parses without error.
**Evidence:** File path itself.

---

### TC-GHH-B002: Write Problem Taxonomy (§5)

**New file:** `reports/product-architecture/problem-taxonomy.yaml`

Must cover all 9 defect categories from the mission brief:
- architecture: monolithic facade, giant partial class, missing domain layers
- specification_and_qname: no QName authority at runtime, speculative API
- state_and_persistence: detached dictionary, setter without writer, getter without parser
- api_design: stringly typed domain, aliases for tests, invalid defaults
- file_and_namespace: MissingMethods-style files (now eliminated), requirement-range files
- implementation_quality: constant returns, semantic stubs, empty success
- testing: API-presence tests, no round-trip, no preservation, no oracle
- governance: quality rules only in prose, certification accepts weak evidence
- documentation_and_status: capability counts inflate perceived progress

Each category must map to specific FODS .NET evidence (file:line or method name).

**Verification:** File parses; at least one FODS-specific example per category.

---

### TC-GHH-B003: Write Runtime Architecture Map (§6)

**New file:** `reports/product-architecture/current-runtime-map.yaml`

Trace the actual flow for EACH supported feature category:

```yaml
feature_flows:
  - feature: cell_value_read
    qname: "table:table-cell/@office:value"
    parser: FodsParser → XDocument load
    model: FodsCell.Value (wraps XElement text)
    public_api: FodsDocument.GetCellValue(sheetName, row, col)
    mutation_path: FodsDocument.SetCellValue → XElement.SetAttributeValue
    writer: FodsWriter.Save → XDocument.Save
    roundtrip_evidence: RT-MUT-01 (FodsRoundtripMutationTests)
    preservation_behavior: write-through XDocument
    status: COMPLETE_END_TO_END

  - feature: cell_style_read
    qname: "table:table-cell/@table:style-name → style:style chain"
    parser: FodsParser → XDocument load (styles parsed on demand)
    model: FodsOdfCellStyle (resolved record)
    public_api: GetResolvedCellStyle(sheetName, row, col)
    mutation_path: FodsStyleEditor.SetCellProperty → auto-style upsert
    writer: FodsWriter.Save → XDocument.Save (auto-styles embedded)
    roundtrip_evidence: FodsGI001CategoryBRoundtripTests
    status: COMPLETE_AFTER_GHH_A003
```

For each feature: document which ones are COMPLETE_END_TO_END, which are
IN_PROGRESS (repair underway), and which are NOT_IMPLEMENTED (explicit unsupported).

Required:
SUPPORTED_FEATURES_WITHOUT_END_TO_END_PATH = 0 (after Group A completes)

---

### TC-GHH-B004: Write Systemic Cause Analysis (§7–§8)

**New file:** `reports/product-architecture/systemic-cause-analysis.yaml`

Must document why agents produced defective code, with evidence:

```yaml
system_causes:
  - cause_id: SC-001
    defect_categories: [semantic_stubs, test_only_apis]
    originating_component: capability_compiler / taskcard_generation
    exact_behavior: |
      Capability compiler enumerated discovered terms ("formula", "image", "hyperlink")
      and generated GetXCount tasks without verifying ODF spec basis. Agent implemented
      methods to satisfy test compilation, not spec derivation.
    agent_incentive: API count increased; tests compiled; sprint graded pass
    resulting_pattern: "public int GetFormulaCount() => 0;"
    why_controls_failed: |
      V87 did not exist. Capability compiler had no QName constraint.
      Taskcard objectives said "implement GetFormulaCount" without spec citation.
      Supervisor rewarded test-count increase.
    permanent_repair: V87 validator + QName-required capability compiler + add-dotnet-api skill update

  - cause_id: SC-002
    defect_categories: [detached_dictionary, setter_without_writer, getter_without_parser]
    originating_component: add-dotnet-object-model-feature skill prompt
    exact_behavior: |
      Skill prompt said "implement getter and setter for property X" without requiring
      parser connection, writer obligation, or round-trip test.
    resulting_pattern: "private readonly Dictionary<...> _field = new(); ... return _field[key];"
    why_controls_failed: |
      No skill contract required: (a) parser reads value, (b) setter writes to XML,
      (c) round-trip test proves persistence. Reviewer accepted "stateful storage" as correct.
    permanent_repair: add-dotnet-object-model-feature skill must enforce parser+writer+roundtrip contract

  - cause_id: SC-003
    defect_categories: [dead_infrastructure, type3_count_zero]
    originating_component: planning machinery (plan-to-code without API contract)
    exact_behavior: |
      FodsStyleResolver.cs was built as standalone utility without a wiring task.
      No taskcard said "add GetResolvedCellStyle overload that calls FodsStyleResolver."
    resulting_pattern: 445 LOC of correct ODF code with zero callers
    why_controls_failed: |
      No gate checked that new infrastructure classes are reachable from the public API.
      Test taxonomy counted 0 Type3 tests but this was not treated as a blocker.
    permanent_repair: add-dotnet-api skill must verify public reachability of new infrastructure
```

---

## Group C: Target Architecture + Machinery Healing

### TC-GHH-C001: Write Target Product Architecture (§9–§10)

**New file:** `reports/product-architecture/target-product-architecture.yaml`

Must specify for FODS .NET:

```yaml
target_product_architecture:
  product: FODS .NET
  language: csharp
  root_document_type: FodsDocument (sealed)
  namespace_hierarchy:
    - FormatFactory.Fods (document, parser, writer)
    - FormatFactory.Fods.Model (FodsSheet, FodsRow, FodsCell, FodsOdfCellStyle)
    - FormatFactory.Fods.Spec.Office (Document spec model)
    - FormatFactory.Fods.Spec.Table (Table, TableRow, TableCell spec models)
    - FormatFactory.Fods.Exceptions

  facade_policy: |
    FodsDocument is a thin facade over XDocument. ALL persistent state must live
    in the XDocument tree. No private dictionary fields may back persistent document
    properties. In-memory-only caches are permitted only if the cache key and
    lifecycle are documented.

  mutability_policy: |
    Every public setter MUST update the XDocument via FodsStyleEditor or direct
    XElement manipulation. Every public getter MUST read from the XDocument
    (direct attribute access or FodsStyleResolver). No getter may return a value
    from a dictionary that the parser does not populate.

  unsupported_feature_policy: |
    If an ODF feature has no spec basis or cannot be read from the XML,
    the API must NOT exist. Do not create GetXCount() returning 0 for features
    with zero ODF XML basis. Explicitly unsupported features are documented,
    not silently faked.

  file_layout:
    - FodsDocument.cs: factory, save, core sheet/cell operations
    - FodsDocumentAccessor.cs: query methods (row/col/cell getters, stats)
    - FodsDocumentExtendedApis.cs: sheet-level settings backed by ODF XML
    - FodsParser.cs: streaming parser, FodsParseResult
    - FodsWriter.cs: serialization
    - FodsStyleResolver.cs: ODF style chain resolution (read path)
    - FodsStyleEditor.cs: ODF style mutation (write path)
    - Model/: FodsSheet, FodsRow, FodsCell, FodsOdfCellStyle, etc.
    - Spec/: canonical QName-aligned classes
    - Exceptions/: FodsDocumentException

  forbidden_filenames:
    - "*MissingMethods*.cs"
    - "*ExtendedApis*.cs" with more than 800 LOC
    - "*Stubs*.cs"
    - "*Helpers*.cs"
    - "*Misc*.cs"
    - any file with requirement range or sprint number in name
```

---

### TC-GHH-C002: Add V90-V92 Governance Validators

**Objective:** Add validators for patterns NOT covered by V87/V88/V89.

**File:** `tools/supervisor/governance_validators_dotnet_semantic.py`

**V90: `validate_dotnet_setter_without_xml_write`**
- Detects: public setter (property or `Set*` method) whose body does NOT contain
  `SetAttributeValue`, `SetElementValue`, `FodsStyleEditor`, or equivalent XML write
  AND the method name does not appear in the V88 whitelist
- Severity: WARN (advisory — setter in abstract/builder context may be valid)
- Target: prevent new detached-dictionary setters

**V91: `validate_dotnet_getter_without_xml_read`**
- Detects: public getter whose body does NOT contain `Attribute(`, `Element(`,
  `FodsStyleResolver`, `.Value`, or XLinq navigation
  AND returns a non-constant expression from a private field
- Severity: WARN
- Target: catch getters backed by fields never set from XML

**V92: `validate_dotnet_fods_extended_apis_loc`**
- Detects: `FodsDocumentExtendedApis.cs` exceeding 800 LOC (governance cap)
- Severity: FAIL (this file must be split before adding more content)
- Target: prevent LOC accumulation in the extended APIs partial class

**Tests:** Add >= 9 tests per new validator to
`tests/supervisor/test_governance_validators_dotnet_semantic.py`.

**Verification:** `python -m pytest tests/supervisor/test_governance_validators_dotnet_semantic.py` — all pass.

---

### TC-GHH-C003: Update add-dotnet-api Skill for QName Authority

**Objective:** Prevent future "implement every missing method" tasks that bypass
spec authority. The skill prompt must require architectural grounding.

**File:** `.supervisor/skill-registry.yaml` — find `add-dotnet-api` skill entry.

**Required additions to the skill contract (add to skill description/prompt):**

```
PRE-EXECUTION REQUIRED (all must be satisfied before writing code):
1. QName authority: identify the ODF/format QName or spec fact that authorizes this API.
   If no QName exists, the API may not be created.
2. Owning type: confirm the API belongs on the listed type (not root document if it is
   a cell/row/column property).
3. Parser connection: identify where in the parser/XDocument the value is read.
4. Writer obligation: if the API mutates state, identify how the mutation reaches XML.
5. Round-trip test: a Type 4 test (Set → ToFodsXml → LoadFromXml → Get → Assert)
   must be planned before the setter task closes.

FORBIDDEN without explicit waiver:
- Implementing a method that returns a constant (0, false, "", null) as the sole body
- Creating a private dictionary field to back a persistent document property
- Adding a public API whose only consumer is a test
- Using "TODO: implement later" as the method body
```

**Verification:** Read back the skill registry entry and confirm the new requirements appear.

---

### TC-GHH-C004: Build Canonical Gap Ledger (§14)

**New file:** `reports/product-architecture/product-quality-gap-ledger.yaml`

Convert the 4 gap-ledger.json entries into the full §14 format, then add any
remaining gaps identified during Groups A-B:

```yaml
gaps:
  - gap_id: GAP-FODS-NET-001
    semantic_key: constant_zero_public_api
    product: FODS
    language: dotnet
    category: implementation_quality
    severity: HIGH
    affected_files: [src/net/fods/FodsDocumentLegacyCounters.cs]
    affected_symbols: [GetFormulaCount, GetImageCount, ...]  # all 67
    spec_fact_ids: []
    qnames: []
    capability_ids: []
    symptom: "67 public methods return constant 0/false/'' with no ODF basis"
    root_cause_status: CONFIRMED
    root_cause: SC-001
    blast_radius: 67 methods removed, ~112 test files deleted
    system_repair: V87 validator + QName-required capability compiler
    architecture_repair: FodsDocumentLegacyCounters.cs deleted (TC-GHH-A008)
    implementation_repair: COMPLETE
    test_repair: Type 1 tests deleted, not replaced (no ODF basis)
    certification_repair: Gate 11 evidence v2 required (TC-GHH-D002)
    status: IN_PROGRESS
    next_action: TC-GHH-A008

  - gap_id: GAP-FODS-NET-002
    semantic_key: detached_dictionary_state
    # ... (similar structure for Category B)

  - gap_id: GAP-FODS-NET-003
    semantic_key: dead_infrastructure_unconnected
    # ... (FodsStyleResolver dead code gap)

  - gap_id: GAP-FODS-NET-004
    semantic_key: type3_coverage_zero
    # ... (no ODF-semantic tests)
```

---

## Group D: Certification Rebuild

### TC-GHH-D001: Gate 11 Impact Assessment

**Objective:** Determine which of the current 8/31 Gate 11 criteria depended on
Category D or B evidence that is now changed.

**Files to read:**
- `acquisition-packs/fods/gate11-packaging-plan.md` (if exists)
- `registry/gate11-criteria.yaml` (if exists)

**Produce:** `.local/evidences/GI-FODS-NET-001/gate11-impact-assessment.md`

Document for each of the 8 met criteria:
- Which test evidence (Type 1/2/3/4) supported it
- Whether the evidence changes with Category D removal
- New evidence available from healed APIs (Type 3/4 from A005 + FodsGI001CategoryBRoundtripTests)

Key expected findings:
- `commercial_test_count_min` — still exceeded (548 > threshold)
- `min_api_coverage` — IMPROVES (removing 67 non-spec APIs, keeping 25 ODF-grounded)
- `dogfood_proof_required` — unaffected (dogfood uses real load/edit/export)

**Verification:** Assessment file exists; all 8 criteria addressed.

---

### TC-GHH-D002: Create gate11-evidence-v2.yaml

**New file:** `acquisition-packs/fods/gate11-evidence-v2.yaml`

Must document:
- Which prior evidence is superseded (Category D removed, Category B upgraded)
- New Type 3/4 tests as genuine behavioral proof
- RT-MUT-05 inversion as persistence proof
- ODF 1.3 spec citations for each Category B property
- Honest accounting: methods_removed=67, tests_removed=~112, why each removal improves quality

**Verification:** File parses as valid YAML; references test file names that exist.

---

### TC-GHH-D003: Gate 11 Delta for Babar Raza

**New file:** `acquisition-packs/fods/gate11-delta-2026-07.md`

Prepare the delta document summarizing:
- Methods removed: 67 (Category D, no ODF spec basis)
- Tests removed: ~112 files / ~700 assertions (Type 1 synthetic guard-only)
- Methods upgraded: ~25 (Category B, stub → ODF-grounded with roundtrip proof)
- New Type 3 tests: >= 6 (ODF-semantic, load real .fods files)
- New Type 4 tests: >= 25 (persistence roundtrip, Category B)
- Net correctness change: POSITIVE (was 0% spec-grounded; now 100% for these APIs)
- Gate 11 status: in_progress (G11-G approved; commercial product pending completion)

**Note:** This is a PREPARATION artifact. Actual Gate 11 re-submission requires Babar Raza's
sign-off (TRUE_EXTERNAL_GATE for the commercial decision). Agent prepares; Babar approves.

---

## Group E: Cross-Product Healing — FODT

GI-FODT-NET-001 is confirmed open. `src/net/fodt/FodtDocumentExtendedApis.cs` at
2,944 LOC contains 94 constant-zero public APIs (same pattern as FODS, Category D).

### TC-GHH-E001: FODT — Read Every File and Classify All Symbols

**Objective:** Complete the §3/§4 manual review for FODT (parallel to FODS work already done).

**Files to read:** ALL files in `src/net/fodt/`

**Produce:** `reports/product-architecture/fodt-file-review.yaml`

For each file, record: intended_responsibility, actual_responsibilities, public_types,
public_symbols, qnames_represented, parser_role, writer_role, disposition.

**Method classification (parallel to FODS):**
- Category A (DOM-computed, keep)
- Category B (ODF-XML property, needs parser/writer wiring)
- Category C (alias delegates, keep)
- Category D (constant-zero, remove)
- Category E (private helpers, keep)

**Verification:** All FODT source files reviewed; every public method classified.

---

### TC-GHH-E002: FODT — Remove Constant-Zero APIs

**Objective:** Apply the same Category D removal to FODT.

**Approach:**
1. Stage FODT Category D methods in `src/net/fodt/FodtDocumentLegacyCounters.cs`
   (same pattern as FODS)
2. Delete the equivalent of FodtDocumentExtendedApis.cs Category D methods
3. Find and delete (or rewrite) the corresponding test files for Category D stubs
4. `dotnet build src/net/fodt/FormatFactory.Fodt.csproj` → must exit 0

**Note on Category B for FODT:** The same ODF style chain and config:config-item patterns
apply. FODT uses the same ODF 1.3 spec. Plan Category B repairs in this taskcard but
only execute if `FodsStyleResolver.cs` can be referenced directly from the FODT project
(it is format-specific; a shared library or copy may be needed).

**Verification:** `dotnet build` exits 0; V87 scan on FODT shows zero new violations.
**Evidence:** `.local/evidences/GI-FODT-NET-001/TC-E002-build.txt`

---

### TC-GHH-E003: FODT — Test Run Verification

**Command:** `dotnet test tests/net/fodt/` (if test project exists)

Record: total, passed, failed, skipped counts before/after FODT repairs.

**Verification:** No pre-existing passing tests regress.

---

## Group F: Pilots, Review, and Closure

### TC-GHH-F001: Run Required Pilots (§19)

Execute the 8 pilots defined in buzzing-wiggling-whistle §Governance Pilots.
For each pilot, produce a brief pass/fail evidence note.

| Pilot | Description | Expected outcome |
|-------|-------------|-----------------|
| P1 — Document inspection | Load fods-cell-styles.fods → GetResolvedCellStyle → verify font color | PASS: non-null with correct values |
| P2 — Edit + roundtrip | SetCellFontColor → ToFodsXml → LoadFromXml → GetCellFontColor | PASS: matches |
| P3 — Preservation | Edit alignment → prove values/formulas survive | PASS: other cells unchanged |
| P5 — Invalid domain | SetCellHorizontalAlignment("invalid") → throws or normalizes | PASS: no silent acceptance |
| P7 — Stub detection | Add disposable `=> 0` method → V87 fires | PASS: V87 WARN |
| P8 — Filename detection | Add disposable `*MissingMethods*.cs` → V89 fires | PASS: V89 FAIL |
| P10 — Idempotency | Second `dotnet test` run → identical results | PASS: counts match |

**Evidence:** `.local/evidences/GI-FODS-NET-001/pilots/` — one file per pilot.

---

### TC-GHH-F002: Manual Professional Review — FODS .NET

**Objective:** Apply the §22 professional review criteria.

Read the final state of ALL modified source files and answer:

1. Would an experienced maintainer accept this architecture?
2. Does the source look like a product library rather than sprint output?
3. Could a user trust each returned value?
4. Are persisted properties actually persisted?
5. Is every API owned by the correct domain type?
6. Does the code reflect the ODF specification?
7. Would adding another feature extend the model cleanly?
8. Could the old failure reappear through another path?

**Produce:** `reports/product-architecture/professional-review-verdict.md`

If any material negative answer: record as rework item. Do NOT close F002 if rework exists.

**Allowed verdicts:** ACCEPTED | ACCEPTED_WITH_MINOR_REWORK | REQUIRES_REWORK

---

### TC-GHH-F003: Update Test Taxonomy JSON

**File:** `reports/gov-incidents/GI-FODS-NET-001-test-taxonomy.json`

Update:
- `Type3_odf_semantic`: set to actual count after A005 (>= 6)
- `Type4_roundtrip`: set to actual count (>= 25 after FodsGI001CategoryBRoundtripTests)
- `Type1_guard_only`: reduce by ~112 deleted files
- Add `healing_session` record with date, taskcards_closed, delta values

**Verification:** JSON parses; `Type3_odf_semantic >= 6`.

---

### TC-GHH-F004: Commit All Changes + Idempotency Proof

**Pre-conditions:** ALL prior taskcards COMPLETE; professional review verdict ACCEPTED.

**Stage and commit:**
- `tests/net/fods/FormatFactory.Fods.Tests.csproj` (A001 fixture registration, A007 re-enables)
- `src/net/fods/FodsDocumentAccessor.cs` (A003/A004 API wiring)
- `tests/net/fods/FodsR255GetResolvedStyleDedicatedTests.cs` (A005 new file)
- `src/net/fods/FodsDocumentLegacyCounters.cs` (A008 deleted)
- `reports/product-architecture/` (B001-B004 new files)
- `reports/product-architecture/target-product-architecture.yaml` (C001)
- `tools/supervisor/governance_validators_dotnet_semantic.py` (C002 V90-V92)
- `.supervisor/skill-registry.yaml` (C003 add-dotnet-api update)
- `reports/product-architecture/product-quality-gap-ledger.yaml` (C004)
- `acquisition-packs/fods/gate11-evidence-v2.yaml` (D002)
- `acquisition-packs/fods/gate11-delta-2026-07.md` (D003)
- `reports/gov-incidents/GI-FODS-NET-001-test-taxonomy.json` (F003)
- FODT changes (E001-E003) if complete

**Commit message:** `fix(fods-net): complete GI-FODS-NET-001 healing + systemic machinery repair`

**Idempotency proof (after commit):**
```
dotnet test tests/net/fods/ → record count
dotnet test tests/net/fods/ → record count again
```
Both runs must produce identical output. Any difference is a MATERIAL_SECOND_RUN_CHANGE and
must be investigated before closure.

---

## Critical Files

| File | Action | TC |
|------|--------|-----|
| `tests/net/fods/FormatFactory.Fods.Tests.csproj` | MODIFY — fixture registration + re-enables | A001, A007 |
| `src/net/fods/FodsDocumentAccessor.cs` | MODIFY — GetResolvedCellStyle/Column/Row + 3 ODF-computed replacements | A003, A004, A008 |
| `tests/net/fods/FodsR255GetResolvedStyleDedicatedTests.cs` | CREATE — 6 Type3 tests | A005 |
| `src/net/fods/FodsDocumentLegacyCounters.cs` | DELETE (67 Category D methods) | A008 |
| `registry/source-structure-baseline.json` | MODIFY — remove LegacyCounters entry | A008 |
| `reports/product-architecture/incident-baseline.yaml` | CREATE | B001 |
| `reports/product-architecture/problem-taxonomy.yaml` | CREATE | B002 |
| `reports/product-architecture/current-runtime-map.yaml` | CREATE | B003 |
| `reports/product-architecture/systemic-cause-analysis.yaml` | CREATE | B004 |
| `reports/product-architecture/target-product-architecture.yaml` | CREATE | C001 |
| `tools/supervisor/governance_validators_dotnet_semantic.py` | MODIFY — add V90-V92 | C002 |
| `tests/supervisor/test_governance_validators_dotnet_semantic.py` | MODIFY — add 27 tests | C002 |
| `.supervisor/skill-registry.yaml` | MODIFY — add-dotnet-api QName contract | C003 |
| `reports/product-architecture/product-quality-gap-ledger.yaml` | CREATE | C004 |
| `acquisition-packs/fods/gate11-evidence-v2.yaml` | CREATE | D002 |
| `acquisition-packs/fods/gate11-delta-2026-07.md` | CREATE (preparation only) | D003 |
| `reports/product-architecture/fodt-file-review.yaml` | CREATE | E001 |
| `src/net/fodt/FodtDocumentLegacyCounters.cs` | CREATE then DELETE (staging) | E002 |
| `reports/product-architecture/professional-review-verdict.md` | CREATE | F002 |
| `reports/gov-incidents/GI-FODS-NET-001-test-taxonomy.json` | MODIFY — Type3 count update | F003 |

---

## Completion Gate Counters (§26)

These must reach zero before TC-GHH-F004 (commit):

```
PRODUCT_FILES_NOT_MANUALLY_REVIEWED = 0        (all 23 FODS + all FODT files reviewed)
PUBLIC_SYMBOLS_NOT_REVIEWED = 0                 (incident-baseline.yaml accounts for all)
RETAINED_PUBLIC_APIS_WITHOUT_AUTHORITY = 0      (LegacyCounters.cs deleted, Cat D gone)
DEFECT_CATEGORIES_WITHOUT_SYSTEMIC_CAUSE_ANALYSIS = 0  (systemic-cause-analysis.yaml)
SUPPORTED_FEATURES_WITHOUT_END_TO_END_PATH = 0  (current-runtime-map.yaml)
MATERIAL_FINDINGS_WITHOUT_GAPS = 0              (product-quality-gap-ledger.yaml)
ACTIONABLE_GAPS_WITHOUT_TASKS = 0              (all gaps link to TC-GHH-* taskcards)
RETAINED_GETTERS_WITHOUT_PARSER_OR_MODEL_SOURCE = 0    (Cat B wired to FodsStyleResolver)
RETAINED_SETTERS_WITHOUT_WRITER_PATH = 0        (Cat B wired to FodsStyleEditor)
RETAINED_PERSISTENT_FEATURES_WITHOUT_ROUNDTRIP = 0    (FodsGI001CategoryBRoundtripTests)
DETACHED_PERSISTENT_STATE_STORES = 0            (dictionaries wired or documented as caches)
TEST_ONLY_PUBLIC_APIS = 0                       (Cat D removed)
FABRICATED_DEFAULT_SUCCESS_APIS = 0             (Cat D removed)
SUSPICIOUS_DUMPING_GROUND_FILES = 0             (LegacyCounters.cs deleted)
QNAME_CONCEPTS_WITHOUT_CANONICAL_MODEL_OWNERSHIP = 0  (Spec/ classes authoritative)
FAILED_REQUIRED_PILOTS = 0                      (P1-P3, P5, P7-P8, P10 pass)
PRODUCT_LIBRARIES_NOT_SCANNED = 0              (FODT + others via V87 scan)
CONFIRMED_SIMILAR_CASES_NOT_TASKED = 0          (GI-FODT-NET-001 tasked in Group E)
FALSE_CERTIFICATIONS_NOT_REOPENED = 0           (gate11-evidence-v2.yaml prepared)
MATERIAL_SECOND_RUN_CHANGES = 0                 (idempotency proof in F004)
```

---

## Verification Steps (end-to-end)

1. `dotnet build src/net/fods/FormatFactory.Fods.csproj` exits 0
2. `dotnet test tests/net/fods/ --verbosity normal` — passing count >= pre-repair count
3. `dotnet test --filter "FodsR255GetResolvedStyleDedicatedTests"` — 6/6 pass
4. `dotnet test --filter "FodsGI001CategoryBRoundtripTests"` — all pass
5. `python -m pytest tests/supervisor/test_governance_validators_dotnet_semantic.py` — all pass
6. V87 scan on `src/net/fods/` after A008 — zero new violations
7. `git status src/net/fods/FodsDocumentLegacyCounters.cs` — not present
8. `reports/product-architecture/` — 5 YAML/MD files created and parseable
9. `acquisition-packs/fods/gate11-evidence-v2.yaml` — parses as valid YAML
10. Second `dotnet test` run produces identical pass count (idempotency)

---

## Key Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| XDocument backing field name unknown before A003 | Grep before writing (Gap A in agile-rolling-marshmallow plan) |
| Sheet name in fixture != "Sheet1" | Read `table:name=` attribute before writing tests (Gap C) |
| T5/T6 unit conversion fails (cm vs pt) | Check `FodsStyleResolver.ParsePointValue()` logic; test with tolerance |
| Class A triage in A006 misclassifies Class B as A | After re-enable, if test fails → re-exclude immediately |
| FodsDocumentLegacyCounters.cs deletion causes compile error | The 3 ODF-computable replacements (GetFormulaCount etc.) must be added BEFORE deletion |
| FODT has deeper Category B gaps than FODS | Scope FODT repair to Category D removal only; plan Category B for a subsequent session |
| add-dotnet-api skill change breaks existing approved workflows | Only ADD requirements; do not remove existing skill steps |

---

## Plan Lineage

| Role | Plan | Status |
|------|------|--------|
| This plan | `plans/.claude/gleaming-rolling-hammock.md` | ACTIVE |
| Supersedes (pending work absorbed) | `plans/.claude/agile-rolling-marshmallow.md` | IN_PROGRESS |
| Supersedes (pending work absorbed) | `plans/.claude/buzzing-wiggling-whistle.md` | IN_PROGRESS |
| Parent incident | `reports/gov-incidents/GI-FODS-NET-001.yaml` | REMEDIATION_IN_PROGRESS |
| FODT sub-incident | `reports/gov-incidents/GI-FODT-NET-001.yaml` | OPEN |


## Taskcard Closure Registry (machine-parseable)

| TC-ID | Status |
|-------|--------|
| TC-GHH-A001 | CLOSED |
| TC-GHH-A002 | CLOSED |
| TC-GHH-A003 | CLOSED |
| TC-GHH-A004 | CLOSED |
| TC-GHH-A005 | CLOSED |
| TC-GHH-A006 | CLOSED |
| TC-GHH-A007 | CLOSED |
| TC-GHH-A008 | CLOSED |
| TC-GHH-B001 | CLOSED |
| TC-GHH-B002 | CLOSED |
| TC-GHH-B003 | CLOSED |
| TC-GHH-B004 | CLOSED |
| TC-GHH-C001 | CLOSED |
| TC-GHH-C002 | CLOSED |
| TC-GHH-C003 | CLOSED |
| TC-GHH-C004 | CLOSED |
| TC-GHH-D001 | CLOSED |
| TC-GHH-D002 | CLOSED |
| TC-GHH-D003 | CLOSED |
| TC-GHH-E001 | CLOSED |
| TC-GHH-E002 | CLOSED |
| TC-GHH-E003 | CLOSED |
| TC-GHH-F001 | CLOSED |
| TC-GHH-F002 | CLOSED |
| TC-GHH-F003 | CLOSED |
| TC-GHH-F004 | CLOSED |
| TC-GHH-CONV-001 | CLOSED |

## Convergence Repair (Post-Audit TC-GHH-CONV-001)

### TC-GHH-CONV-001: Fix FODS .csproj — restore exclusion list in HEAD

**Finding:** AF-001/AF-002 — HEAD commit has 0 Compile Remove entries; working tree
missing R434/R435 exclusions causing 13 test failures.

**Root cause:** During TC-GHH-A006/A007 the .csproj exclusion list was correctly rebuilt
in the working tree, but the commit did not capture the 139-entry exclusion list.
The linter then re-applied 137 entries (without R434/R435) post-commit.

**Fix:**
1. Add R434/R435 back to working tree .csproj exclusion list
2. Verify `dotnet test` → 4210/4210 PASS
3. Commit the corrected .csproj as follow-up to b947eeac
4. Verify fresh build from HEAD: `dotnet build` → 0 errors, `dotnet test` → 4210/4210

**Proof required:** Level 4 (E2E) — build + test from working tree matching HEAD state.

**Evidence:** `.local/evidences/GI-FODS-NET-001/TC-CONV-001-csproj-repair.txt`

<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-03T00:00:00.000000+00:00"
  locked_by: "0ce45942c388"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->

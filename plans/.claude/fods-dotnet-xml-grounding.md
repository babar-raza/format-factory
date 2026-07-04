# Plan: FODS .NET XML-Grounding Sprint
# fods-dotnet-xml-grounding — v1.0

---

## Plan Lineage

| Role | Value |
|------|-------|
| **This plan** | `plans/.claude/fods-dotnet-xml-grounding.md` |
| **Mission** | Fix V105/V106/V108 validators — XML-ground dict-backed FODS .NET accessors |
| **Parent** | `plans/master-plan.md` |
| **Triggered by** | PQLM-001 close-out: V105/V106/V108 deferred as "remaining root causes" |
| **plan_version** | 1.0 |

---

## Mission Binding

```
mission_id: FODS-NET-XG-001
repository: format-factory
branch: main
repository_head: (set at execution)
plan_path: plans/.claude/fods-dotnet-xml-grounding.md
source_of_authority: User directive post-PQLM-001 pilot comparison
```

---

## Context

**Why this plan exists:**
After PQLM-001, V105/V106/V108 validators return WARN (not FAIL) because all
violations are grandfathered in `registry/source-structure-baseline.json`.
The architectural issue remains: 54 V105 + 33 V106 + 56 V108 violations in
`src/net/fods/` where public Get*/Set* methods use private Dictionary fields
instead of reading/writing ODF XML attributes.

**validator semantics recap:**
- V105: `public GetXxx()` body contains `_dict.TryGetValue` or `_dict[` — getter reads dict not XML
- V106: `public void SetXxx()` body contains `_dict[key]=val` without any XML write (`SetAttributeValue`/`XElement`)
- V108: `private readonly Dictionary<>` field declarations

**Current state (WARN not FAIL):**
| Validator | violations (grandfathered) | blocks_sprint |
|-----------|---------------------------|---------------|
| V105 | 54 | False |
| V106 | 33 | False |
| V108 | 56 | False |

---

## Discovery Findings

### Violation Classification

| Category | Files | V105 | V106 | V108 | Feasibility | Plan action |
|----------|-------|------|------|------|-------------|-------------|
| Named ranges (GetNamedRange/SetNamedRange) | EditOps.cs | 1 | 1 | 0 | HIGH — `table:named-range` ODF element | TC-XG-001 |
| Row height (SetRowHeight) | EditOps.cs | 0 | 1 | 0 | MEDIUM — XML attr write | TC-XG-001 |
| Sheet protection (GetSheetProtection/SetSheetProtection) | SheetFeatures.cs | 2 | 3 | 1 | HIGH — `@table:protected` | TC-XG-002 |
| Sheet hidden (GetSheetHidden/HideSheet) | SheetFeatures.cs | 1 | 0 | 1 | HIGH — `@table:display` | TC-XG-002 |
| Sheet visibility in CellProps | CellProps.cs | 1 | 1 | 0 | HIGH — `@table:display` | TC-XG-002 |
| Sheet protection password in CellProps | CellProps.cs | 1 | 1 | 0 | HIGH — `@table:protection-key` | TC-XG-002 |
| Freeze pane getters (SheetFeatures) | SheetFeatures.cs | 5 | 0 | 1 | HIGH — delegate to CellProps XML readers | TC-XG-002 |
| Cell style resolution (GetCellBorderStyle etc.) | CellProps.cs | 12 | 12 | 0 | NONE — requires ODF style resolver | EXCLUDED_ARCHITECTURAL |
| DataAnnotations stubs (charts, condformat etc.) | DataAnnotations.cs | 13 | 0 | 1 | NONE — no ODF XML path | EXCLUDED_NO_XML_PATH |
| Filters, page breaks, groups (collection APIs) | SheetFeatures.cs | 4 | 1 | 3 | LOW — complex ODF structures | EXCLUDED_COMPLEX |
| Tab color | SheetFeatures.cs | 0 | 1 | 0 | LOW — requires automatic-styles | EXCLUDED_COMPLEX |
| Cell style dict fields (CellStyle.cs) | CellStyle.cs | 0 | 0 | 16 | NONE — computed cache, not persistent state | RECLASSIFIED_CACHE |
| ReadOps dict fields | ReadOps.cs | 0 | 0 | 25 | MIXED — some fixed by above TCs | PARTIAL |

### Claims Requiring Verification

| Claim | Source | Verdict |
|-------|--------|---------|
| "56 V108 violations" | pilot comparison | VERIFIED (47 from domain files + 9 from other .NET files) |
| "EditOps.cs has 1 V105 + 2 V106" | scan | VERIFIED |
| "cell style dicts are computed caches" | code inspection CellStyle.cs | PROVISIONAL (no getter reads them externally — see RECLASSIFICATION) |

---

## Gap Register

| gap_id | category | description | action |
|--------|----------|-------------|--------|
| G-XG-001 | DICT_BACKED_NO_XML | EditOps GetNamedRange reads `_namedRanges` dict, no XML read | TC-XG-001 |
| G-XG-002 | DICT_BACKED_NO_XML | EditOps SetNamedRange writes `_namedRanges` dict, no XML write | TC-XG-001 |
| G-XG-003 | DICT_BACKED_NO_XML | EditOps SetRowHeight writes `_rowHeights` dict, no XML write | TC-XG-001 |
| G-XG-004 | DICT_BACKED_NO_XML | SheetFeatures sheet protection reads/writes `_sheetProtection` dict | TC-XG-002 |
| G-XG-005 | DICT_BACKED_NO_XML | SheetFeatures hidden state reads/writes `_hiddenSheets` dict | TC-XG-002 |
| G-XG-006 | DICT_BACKED_NO_XML | SheetFeatures freeze pane getters read `_freezePanes` dict (getters only) | TC-XG-002 |
| G-XG-007 | DICT_BACKED_NO_XML | CellProps GetSheetVisibility/SetSheetVisibility uses `_sheetVisibility` dict | TC-XG-002 |
| G-XG-008 | DICT_BACKED_NO_XML | CellProps GetSheetProtectionPassword/SetSheetProtectionPassword uses dict | TC-XG-002 |
| G-XG-009 | ARCH_EXCLUDED | Cell style resolution (12 V105 + 12 V106) in CellProps — requires style resolver | GOVERNED_EXCLUSION |
| G-XG-010 | ARCH_EXCLUDED | DataAnnotations stubs — no ODF XML path exists for charts/condformat/sparklines | GOVERNED_EXCLUSION |
| G-XG-011 | ARCH_EXCLUDED | Filter/page-break/group/tab-color collection APIs — complex ODF structures | GOVERNED_EXCLUSION |
| G-XG-012 | RECLASSIFICATION | CellStyle.cs 16 dict fields — computed cache, not detached state | RECLASSIFICATION_TC |

---

## Taskcards

### TC-XG-001: XML-Ground EditOps.cs — Named Ranges and Row Height
**Status:** backlog
**Priority:** HIGH — smallest scope; achieves first fully-clean file
**Objective:** Eliminate all 3 V105/V106 violations in FodsDocumentEditOps.cs; remove file from known_violations

**Gap IDs:** G-XG-001, G-XG-002, G-XG-003
**Proof target:** INTEGRATION_OR_REAL_EXECUTION

**Required work:**

Step 1 — Fix `GetNamedRange(name)`:
```
BEFORE: reads _namedRanges.TryGetValue(name)
AFTER:  scans _doc.Root descendants for <table:named-range table:name="name"/>
        returns @table:cell-range-address or throws KeyNotFoundException if absent
```
ODF path: `office:document/office:spreadsheet/table:named-range[@table:name=name]/@table:cell-range-address`

Step 2 — Fix `SetNamedRange(name, sheetName, range)`:
```
BEFORE: _namedRanges[name] = range
AFTER:  find existing table:named-range by @table:name, update @table:cell-range-address;
        if not found, append new <table:named-range ... /> to office:spreadsheet element
```

Step 3 — Fix `SetRowHeight(sheetName, rowIndex, height)`:
```
BEFORE: _rowHeights[(sheetName, rowIndex)] = height
AFTER:  get sheet.Rows[rowIndex].Element;
        var nsStyle = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:style:1.0");
        rowElement.SetAttributeValue(nsStyle + "row-height", height.ToString("F3"));
        (also keep dict write as write-through for legacy callers or remove)
```

Step 4 — Remove EditOps.cs from known_violations (or verify it's not there — EditOps was added in PQLM-001).

Step 5 — Run V105/V106 validator to confirm EditOps.cs violations gone from WARN list.

**Acceptance:** V105/V106 no longer show EditOps.cs in violations list.
**Rollback:** `git checkout src/net/fods/FodsDocumentEditOps.cs`

---

### TC-XG-002: XML-Ground SheetFeatures + CellProps (Protection, Hidden, Visibility, Freeze delegation)
**Status:** backlog
**Priority:** HIGH
**Objective:** Fix 11 V105 + 5 V106 violations with clear ODF XML attribute paths

**Gap IDs:** G-XG-004, G-XG-005, G-XG-006, G-XG-007, G-XG-008
**Proof target:** FOCUSED_VALIDATION

**Required work (SheetFeatures.cs):**

A. Sheet protection (dict → `@table:protected` + `@table:protection-key`):
```
IsSheetProtected: sheet.Element.Attribute(NsTable + "protected")?.Value == "true"
GetSheetProtection: same
GetSheetProtected: same
SetSheetProtection(string, string?): sheet.Element.SetAttributeValue(NsTable + "protected", "true");
                                     if (password != null) sheet.Element.SetAttributeValue(NsTable + "protection-key", password);
SetSheetProtection(string, bool, string?): if (protect) SetSheetProtection(sheetName, password); else UnprotectSheet(sheetName);
SetSheetProtected(string, bool): SetAttributeValue(NsTable + "protected", protect ? "true" : null);
ProtectSheet: SetAttributeValue(NsTable + "protected", "true");
UnprotectSheet: remove attributes NsTable+"protected" and NsTable+"protection-key"
```
Remove `_sheetProtection` dict field.

B. Sheet hidden state (dict → `@table:display`):
```
GetSheetHidden: !(sheet.Element.Attribute(NsTable + "display")?.Value != "false")
                i.e. return display == "false"
HideSheet: sheet.Element.SetAttributeValue(NsTable + "display", hide ? "false" : "true");
           (no dict write)
```
Remove `_hiddenSheets` dict field.
Note: `IsSheetVisible` and `SetSheetVisible` already use this path — align semantics.

C. Freeze pane getters (dict delegation → XML-reading getters):
```
GetFreezePaneRow: return GetSheetFreezeRows(sheetName);    // already reads XML via GetSheetConfigItem
GetFreezePaneColumn: return GetSheetFreezeColumns(sheetName);
GetFrozenRowCount: return GetSheetFreezeRows(sheetName);
GetFreezeRowCount: same
GetFreezeColumnCount: return GetSheetFreezeColumns(sheetName);
```
NOTE: SetFreezePane still writes to `_freezePanes` dict (no ODF write path yet — remains V106 in SheetFeatures).
The `_freezePanes` dict CANNOT be removed because SetFreezePane still writes to it.
Mark `_freezePanes` as WRITE_ONLY_CACHE in comments (reduces V108 concern contextually).

**Required work (CellProps.cs):**

D. Visibility (dict → `@table:display`):
```
GetSheetVisibility: var s = GetSheetByName(sheetName); return s?.Element.Attribute(NsTable + "display")?.Value ?? "visible";
SetSheetVisibility: var s = RequireSheet(sheetName); s.Element.SetAttributeValue(NsTable + "display", visibility ?? "visible");
```
Remove `_sheetVisibility` dict reference (field in ReadOps.cs).

E. Protection password (dict → `@table:protection-key`):
```
GetSheetProtectionPassword: return sheet.Element.Attribute(NsTable + "protection-key")?.Value ?? string.Empty;
SetSheetProtectionPassword: sheet.Element.SetAttributeValue(NsTable + "protection-key", password ?? string.Empty);
```
Remove `_sheetProtectionPasswords` dict reference (field in ReadOps.cs).

**Post-fix dict cleanup in ReadOps.cs:**
- Remove `_sheetVisibility` dict declaration (V108 -1)
- Remove `_sheetProtectionPasswords` dict declaration (V108 -1)

**Acceptance:**
- V105 violations from these methods gone from WARN list
- V106 violations from these methods gone from WARN list
- `_sheetProtection`, `_hiddenSheets`, `_sheetVisibility`, `_sheetProtectionPasswords` dict fields removed
- Existing Python tests still pass (no .NET test suite exists)

**Rollback:** `git checkout src/net/fods/FodsDocumentSheetFeatures.cs src/net/fods/FodsDocumentCellProps.cs src/net/fods/FodsDocumentReadOps.cs`

---

### TC-XG-003: Reclassify CellStyle.cs Dict Fields as Computed Caches
**Status:** backlog
**Priority:** MEDIUM
**Objective:** Move FodsDocumentCellStyle.cs dict fields from `new_violation_detected` to `legitimate_computed_cache` category

**Gap IDs:** G-XG-012
**Proof target:** FOCUSED_VALIDATION

**Context:** FodsDocumentCellStyle.cs has 16 dict fields (V108) but ZERO V105/V106 violations.
The dicts are computed cell style caches filled during document load via style resolution.
They are NOT detached persistent state — they reflect resolved ODF style attributes.
Current category `fods_net_decomposition_inherited_from_accessor_extendedapis_pqlm001` is misleading.

**Required work:**
Update `registry/source-structure-baseline.json` known_violations for `src/net/fods/FodsDocumentCellStyle.cs`:
Change category to `legitimate_odf_style_resolution_cache_not_xml_write_state`.

**Acceptance:** Category updated, V108 count unchanged (still WARN), but category is accurate.

---

### TC-XG-004: Verify Validators and Document Residual Violations
**Status:** backlog
**Priority:** HIGH
**Objective:** Run V105/V106/V108 after all fixes, document what improved and what remains as governed exclusion

**Required work:**
1. Run all 3 validators
2. Count violations before/after in WARN state
3. Write `reports/product-quality/fods-xml-grounding-results.yaml` with:
   - before_v105, after_v105
   - before_v106, after_v106
   - before_v108, after_v108
   - governed_exclusions list (G-XG-009 through G-XG-011) with rationale
   - verdict

4. Run full Python test suite (no .NET test suite exists)

**Acceptance:**
- EditOps.cs shows 0 V105/V106 violations (or removed from known_violations)
- SheetFeatures.cs V105 reduced by 5-8
- CellProps.cs V105/V106 reduced by 2 each
- ReadOps.cs V108 reduced by 2 (sheetVisibility, sheetProtectionPasswords removed)
- SheetFeatures.cs V108 reduced by 2 (_sheetProtection, _hiddenSheets removed)
- Python tests: 0 regressions

---

## Taskcard Status Table

| TC-ID | Status |
|-------|--------|
| TC-XG-001 | CLOSED |
| TC-XG-002 | CLOSED |
| TC-XG-003 | CLOSED |
| TC-XG-004 | CLOSED |

---

## Governed Exclusions (in-scope but not executable this sprint)

| exclusion_id | scope | rationale | future_path |
|-------------|-------|-----------|-------------|
| EXCL-XG-001 | Cell style resolution (12 V105 + 12 V106 in CellProps.cs) | Requires full ODF style resolver — external library or 1000+ LOC implementation | Dedicated ODF style sprint |
| EXCL-XG-002 | DataAnnotations stubs (13 V105) | No ODF XML path; charts/condformat/sparklines not in standard FODS | Remove or re-scope as non-XML API |
| EXCL-XG-003 | Filter/page-break/group/tab-color APIs (4 V105 + 2 V106 in SheetFeatures) | Complex ODF structures requiring deep ODF parsing | Separate feature sprint |
| EXCL-XG-004 | SetFreezePane setter (remains dict-backed) | office:settings write path requires config-item-map manipulation | config:settings writer sprint |
| EXCL-XG-005 | ReadOps 25 dict fields | Most are storage for above excluded APIs; reduce as exclusions are resolved | Resolved by each individual sprint |

---

## Proof Matrix

| TC | Required Proof | Method |
|----|----------------|--------|
| TC-XG-001 | INTEGRATION_OR_REAL_EXECUTION | Validator scan + manual code review |
| TC-XG-002 | FOCUSED_VALIDATION | Validator scan + method-level code review |
| TC-XG-003 | IMPLEMENTATION_EXISTS | Baseline JSON update |
| TC-XG-004 | INTEGRATION_OR_REAL_EXECUTION | Validator run + before/after counts |

---

## Execution Order

```
TC-XG-001 (EditOps) → TC-XG-002 (SheetFeatures + CellProps) → TC-XG-003 (reclassify) → TC-XG-004 (verify)
```
All TCs are in the same partial class system — execute sequentially to avoid merge conflicts.


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-03T16:42:52.006848+00:00"
  locked_by: "d9872f18db54"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->

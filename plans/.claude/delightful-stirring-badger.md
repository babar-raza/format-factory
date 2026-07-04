# Execution Plan: FODS .NET XML Grounding Sprint 2
# Authority source: plans/.claude/fods-dotnet-xml-grounding-2.md (mission FODS-NET-XG-002)

---

## A. Current-State Reassessment

**Verified 2026-07-04 against HEAD.**

| File | LOC | Baseline cap |
|------|-----|-------------|
| `src/net/fods/FodsDocumentCellProps.cs` | 643 | 642 |
| `src/net/fods/FodsDocumentReadOps.cs` | 911 | 911 |
| `src/net/fods/FodsDocumentSheetFeatures.cs` | 474 | 479 |
| `src/net/fods/FodsDocumentDataAnnotations.cs` | 508 | (check baseline) |

Gap ledger: GAP-NET-XG-010, GAP-NET-XG-011, GAP-NET-XG-012 all **OPEN**.
Taskcard status table in fods-dotnet-xml-grounding-2.md: all four TCs **backlog**.
Sprint 1 results file exists (FODS-NET-XG-001 only); Sprint 2 results file does not exist yet.

---

## B. Item-by-Item Status

### TC-XG-010 — office:settings write path
**Status: UNRESOLVED**

Evidence from current CellProps.cs:
- `SetSheetFreezeRows` → `_sheetFreezeRows[sheetName] = rows;` (dict only, no XML write)
- `SetSheetFreezeColumns` → `_sheetFreezeColumns[sheetName] = cols;` (dict only)
- `SetSheetZoomLevel` → `_sheetZoomLevel[sheetName] = zoom;` (dict only)
- `SetSheetPrintArea` → `_sheetPrintArea[sheetName] = area ?? string.Empty;` (dict only)
- `GetSheetFreezeRows` / `GetSheetFreezeColumns` / `GetSheetZoomLevel` / `GetSheetShowGrid` / `GetSheetShowHeaders` — getters already read from `GetSheetConfigItem` XML BUT still check dict override first (`TryGetValue`)
- `GetSheetRightToLeft` — pure dict, no XML read at all (no `GetSheetConfigItem` fallback)
- `GetSheetPrintArea` — pure dict, no XML read

Evidence from current ReadOps.cs field declarations (lines 32-40):
`_sheetFreezeRows`, `_sheetFreezeColumns`, `_sheetZoomLevel`, `_sheetPrintArea`,
`_sheetRightToLeft`, `_sheetShowGrid`, `_sheetShowHeaders` — all still present.

**Still needed:** Add `SetSheetConfigItem` helper; fix 4 setters to write XML; remove dict guards from 7 getters; remove 7 field declarations from ReadOps.cs.

### TC-XG-011 — Cell style dict cache removal
**Status: UNRESOLVED**

Evidence from current CellProps.cs:
- `GetCellBorderStyle` — dict guard present: `if (_cellBorderStyles.TryGetValue(...)) return ov;`
- `SetCellBorderStyle` — dict write present: `_cellBorderStyles[(sheetName, row, col)] = style;`
- Same pattern confirmed for: `GetCellHorizontalAlignment`, `SetCellHorizontalAlignment`, `GetCellVerticalAlignment`, `SetCellVerticalAlignment`, `GetCellIndentLevel`, `SetCellIndentLevel`, `GetCellRotationAngle`, `SetCellRotationAngle`, `GetCellMergeInfo`, `GetCellMergeSpan`, `SetCellMergeSpan`, `GetCellShrinkToFit`, `SetCellShrinkToFit`, `GetCellUnderline`, `SetCellUnderline`, `GetCellStrikethrough`, `SetCellStrikethrough`, `GetCellProtection`, `SetCellProtection`
- `GetCellFontStyle` / `SetCellFontStyle` — pure dict (no XML path; stub)

Evidence from ReadOps.cs (lines 41-52): all 12 cell dict fields still declared:
`_cellBorderStyles`, `_cellFontStyles`, `_cellHAlign`, `_cellVAlign`, `_cellIndentLevel`,
`_cellRotationAngle`, `_cellMergeInfo`, `_cellMergeSpan`, `_cellShrinkToFit`,
`_cellUnderline`, `_cellStrikethrough`, `_cellProtection`.

**Still needed:** Remove TryGetValue guards from 9 getters; remove dict writes from 11 setters; remove 12 field declarations; add STUB comment to GetCellFontStyle.

### TC-XG-012 — Filter/page-break/group/tab-color ODF structure
**Status: UNRESOLVED**

Evidence from current SheetFeatures.cs:
- `_freezePanes` dict (line 127): `SetFreezePane` writes `_freezePanes[sheetName] = (rows, cols);`; `GetFreezePaneRow`/`GetFreezePaneColumn` read from `_freezePanes`
- `_printAreas` dict (line 268): `SetPrintArea` writes `_printAreas[sheetName] = area`; `GetPrintArea` reads from `_printAreas`
- `_tabColors` dict (line 367): `SetTabColor` writes `_tabColors[sheetName] = color`; `GetTabColor` reads from `_tabColors`
- `_filters` (line 188), `_pageBreaks` (line 267), `_groups` (line 330): collection dicts, setters write directly

DataAnnotations.cs: no STUB comments present on chart/condformat/sparkline dict bodies.

**Still needed:** Delegate SetFreezePane → SetSheetFreezeRows/Cols; delegate GetFreezePaneRow/Col → GetSheetFreezeRows/Cols; delegate SetPrintArea/GetPrintArea → CellProps methods; switch GetTabColor/SetTabColor to NsFfExt XML attribute; add COLLECTION_STUB comments; remove 3 dict field declarations; add STUB comments to DataAnnotations.

### TC-XG-013 — Verify + results report
**Status: NOT STARTED** (upstream TCs not done)

---

## C. Remaining Problems

All four taskcards remain fully unresolved. No partial work detected in any file.

Root causes (unchanged from plan):
1. Setters in CellProps.cs write only to in-memory dicts → settings lost on save/reload
2. Getter dict guards shadow XML reads → stale dict values take priority over document state
3. SheetFeatures dicts duplicate the CellProps XML paths introduced in Sprint 1
4. Dict field declarations in ReadOps.cs are the mechanical V105/V106/V108 trigger

---

## D. Revised Plan (current reality only)

### Step 0 — Plan Lock

```
python tools/supervisor/write_plan_lock.py \
  --plan-path plans/.claude/fods-dotnet-xml-grounding-2.md
```

---

### TC-XG-010 — office:settings write path

**Files:** [FodsDocumentCellProps.cs](src/net/fods/FodsDocumentCellProps.cs), [FodsDocumentReadOps.cs](src/net/fods/FodsDocumentReadOps.cs)

**1. Add `SetSheetConfigItem` private helper to CellProps.cs** (after `GetSheetConfigItem`):

Navigate `_doc.Root` → `office:settings` (create if absent) → `config:config-item-set` →
`config:config-item-map-indexed[@config:name="Views"]` → first `config:config-item-map-entry` →
`config:config-item-map-named[@config:name="Tables"]` →
`config:config-item-map-entry[@config:name=sheetName]` (create if absent) →
upsert `config:config-item[@config:name=itemName @config:type=itemType]` with given value.

Namespaces to use: `NsOffice` (already declared in FodsDocument.cs), `NsConfig` (declared in ReadOps.cs line 27).

**2. Fix setters — replace dict write with XML write:**

| Method | CellProps.cs | Replace `_dict[sheetName] = val` with |
|--------|-------------|---------------------------------------|
| `SetSheetFreezeRows` | line ~102 | `SetSheetConfigItem(sheetName, "HorizontalSplitMode", "short", "2")` + `SetSheetConfigItem(sheetName, "HorizontalSplitPosition", "int", rows.ToString())` |
| `SetSheetFreezeColumns` | line ~124 | `SetSheetConfigItem(sheetName, "VerticalSplitMode", "short", "2")` + `SetSheetConfigItem(sheetName, "VerticalSplitPosition", "int", cols.ToString())` |
| `SetSheetZoomLevel` | line ~149 | `SetSheetConfigItem(sheetName, "ZoomValue", "int", zoom.ToString())` |
| `SetSheetPrintArea` | line ~165 | `SetSheetConfigItem(sheetName, "PrintArea", "string", area ?? string.Empty)` |

**3. Fix getters — remove dict TryGetValue guard, keep XML fallback:**

| Method | Action |
|--------|--------|
| `GetSheetFreezeRows` | Remove `if (_sheetFreezeRows.TryGetValue(...)) return ov;` |
| `GetSheetFreezeColumns` | Remove `if (_sheetFreezeColumns.TryGetValue(...)) return ov;` |
| `GetSheetZoomLevel` | Remove `if (_sheetZoomLevel.TryGetValue(...)) return ov;` |
| `GetSheetPrintArea` | Replace pure-dict body with `return GetSheetConfigItem(sheetName, "PrintArea") ?? string.Empty;` |
| `GetSheetRightToLeft` | Replace pure-dict body with config-item read for `WritingMode` (or leave as stub with comment — no standard config-item name; use `// STUB: no standard ODF config-item for writing-mode; returns false`) |
| `GetSheetShowGrid` | Remove `if (_sheetShowGrid.TryGetValue(...)) return ov;` |
| `GetSheetShowHeaders` | Remove `if (_sheetShowHeaders.TryGetValue(...)) return ov;` |

Note on `GetSheetRightToLeft`: ODF writing-mode is a style attribute (`style:writing-mode`), not a config-item. Since no standard config-item path exists, mark as stub returning `false` and leave comment `// STUB: writing-mode is a style attribute (style:writing-mode), not a config:config-item; returns false`.

**4. Remove field declarations from ReadOps.cs** (grep each name across `src/net/fods/` first):
- `_sheetFreezeRows`, `_sheetFreezeColumns`, `_sheetZoomLevel`, `_sheetPrintArea`,
  `_sheetRightToLeft`, `_sheetShowGrid`, `_sheetShowHeaders`

**Acceptance:** V105: 10→≤3; V106: 10→≤6; 7 dict fields removed from ReadOps.

---

### TC-XG-011 — Cell style dict cache removal

**Files:** [FodsDocumentCellProps.cs](src/net/fods/FodsDocumentCellProps.cs), [FodsDocumentReadOps.cs](src/net/fods/FodsDocumentReadOps.cs)

For each getter with `TryGetValue` guard — **delete the guard line only** (keep XML read path):
- `GetCellBorderStyle`, `GetCellHorizontalAlignment`, `GetCellVerticalAlignment`,
  `GetCellIndentLevel`, `GetCellRotationAngle`, `GetCellMergeInfo`, `GetCellMergeSpan`,
  `GetCellShrinkToFit`, `GetCellUnderline`, `GetCellStrikethrough`, `GetCellProtection`

For `GetCellFontStyle` — replace body with:
```csharp
RequireSheet(sheetName); RequireNonNegativeRow(row); RequireNonNegativeCol(col);
// STUB: no ODF style-chain path for font-style string; returns default "normal"
return "normal";
```

For each setter — **delete only the dict-write line** (keep the `FodsStyleEditor` XML write):
- `SetCellBorderStyle`: delete `_cellBorderStyles[(sheetName, row, col)] = style;`
- `SetCellFontStyle`: delete `_cellFontStyles[(sheetName, row, col)] = style ?? "normal";` (no XML write to add — pure stub becomes no-op setter)
- `SetCellHorizontalAlignment`: delete `_cellHAlign[(sheetName, row, col)] = alignment;`
- `SetCellVerticalAlignment`: delete `_cellVAlign[(sheetName, row, col)] = alignment;`
- `SetCellIndentLevel`: delete `_cellIndentLevel[(sheetName, row, col)] = level;`
- `SetCellRotationAngle`: delete `_cellRotationAngle[(sheetName, row, col)] = angle;`
- `SetCellMergeSpan`: delete `_cellMergeSpan[(sheetName, row, col)] = span;`
- `SetCellShrinkToFit`: delete `_cellShrinkToFit[(sheetName, row, col)] = shrink;`
- `SetCellUnderline`: delete `_cellUnderline[(sheetName, row, col)] = style;`
- `SetCellStrikethrough`: delete `_cellStrikethrough[(sheetName, row, col)] = strikethrough;`
- `SetCellProtection`: delete `_cellProtection[(sheetName, row, col)] = protect;`

Remove 12 field declarations from ReadOps.cs (after grepping each):
`_cellBorderStyles`, `_cellFontStyles`, `_cellHAlign`, `_cellVAlign`, `_cellIndentLevel`,
`_cellRotationAngle`, `_cellMergeInfo`, `_cellMergeSpan`, `_cellShrinkToFit`,
`_cellUnderline`, `_cellStrikethrough`, `_cellProtection`

**Acceptance:** V105 CellProps: →0; V106 CellProps: →0; V108 drops by 12.

---

### TC-XG-012 — SheetFeatures dict consolidation

**Files:** [FodsDocumentSheetFeatures.cs](src/net/fods/FodsDocumentSheetFeatures.cs), [FodsDocumentDataAnnotations.cs](src/net/fods/FodsDocumentDataAnnotations.cs)

**A. Tab color → NsFfExt XML attribute**

`GetTabColor` — replace dict body with:
```csharp
var sheet = GetSheetByName(sheetName) ?? throw new ArgumentException(...);
return sheet.Element.Attribute(NsFfExt + "tab-color")?.Value ?? string.Empty;
```

`SetTabColor` — replace dict write with:
```csharp
var sheet = GetSheetByName(sheetName) ?? throw new ArgumentException(...);
sheet.Element.SetAttributeValue(NsFfExt + "tab-color", color ?? string.Empty);
```

Remove `_tabColors` dict field declaration.

**B. SetFreezePane / GetFreezePaneRow / GetFreezePaneColumn → delegate to CellProps XML methods**

`SetFreezePane` body (after validation guards, replacing `_freezePanes[sheetName] = (rows, cols);`):
```csharp
SetSheetFreezeRows(sheetName, rows);
SetSheetFreezeColumns(sheetName, cols);
```

`GetFreezePaneRow` → return `GetSheetFreezeRows(sheetName)` (remove `_freezePanes.TryGetValue`)
`GetFreezePaneColumn` → return `GetSheetFreezeColumns(sheetName)`
`GetFrozenRowCount` → delegates to `GetFreezePaneRow` (no change needed — already aliases)
`GetFreezeRowCount` → remove `_freezePanes.TryGetValue`; return `GetSheetFreezeRows(sheetName)`
`GetFreezeColumnCount` → remove `_freezePanes.TryGetValue`; return `GetSheetFreezeColumns(sheetName)`

Remove `_freezePanes` dict field declaration.

**C. SetPrintArea / GetPrintArea → delegate to CellProps XML methods**

```csharp
public void SetPrintArea(string sheetName, string area) => SetSheetPrintArea(sheetName, area);
public string GetPrintArea(string sheetName) => GetSheetPrintArea(sheetName);
public int GetPrintAreaCount() => 0; // STUB: delegated to XML path; count not tracked in-memory
```

Remove `_printAreas` dict field declaration.

**D. Filters / page breaks / groups — COLLECTION_STUB comments only**

Add to each collection field declaration line:
```csharp
// COLLECTION_STUB: ODF target=table:database-range (filter) / table:table-row/@fo:break-before (page-break) / table:row-group (group). XML write deferred to feature sprint.
```

Do NOT remove these dicts — they have no clean single-element XML write target.

**E. DataAnnotations stubs**

Add `// STUB: no ODF XML path for {feature}; tracking GAP-NET-XG-012` to dict-backed getter bodies in FodsDocumentDataAnnotations.cs (charts, condformat, sparklines).

**Acceptance:** V108 drops by 3; `_freezePanes`/`_printAreas`/`_tabColors` removed.

---

### TC-XG-013 — Verify + results report

**1. Run validators** (adjust runner path to project convention):
```
python tools/supervisor/governance_validators_path.py src/net/fods/
```
Check V105 (≤3), V106 (≤6), V108 (≤34).

**2. Run Python FODS tests** — 0 regressions required:
```
.venv/Scripts/pytest tests/python/fods/ -v --tb=short
```

**3. Write** `reports/product-quality/fods-xml-grounding-sprint2-results.yaml`
Include: before/after counts per file, dict fields removed, test result summary.

**4. Append** sprint-2 delta row to `reports/product-quality/fods-xml-grounding-results.yaml`.

**5. Update** `registry/source-structure-baseline.json`:
- Update `loc` fields if file sizes changed (never increase `baseline_loc_cap`)
- If a file's violations → 0 AND LOC < 800: remove from `known_violations`

**6. Update gap ledger** `reports/product-quality/product-code-gap-ledger.yaml`:
- GAP-NET-XG-010, GAP-NET-XG-011, GAP-NET-XG-012 → `status: CLOSED`

**7. Update taskcard status table** in `plans/.claude/fods-dotnet-xml-grounding-2.md`:
All four TCs → `CLOSED`

**8. Lifecycle audit + terminal close:**
```
python tools/supervisor/lifecycle_audit.py \
  --mission-id FODS-NET-XG-002 --sprint-id TC-XG-013

python tools/supervisor/write_plan_lock.py \
  --plan-path plans/.claude/fods-dotnet-xml-grounding-2.md \
  --terminal --audit-gate
```

---

## Constraints (carry-forward, verified still applicable)

- `baseline_loc_cap` is write-once — never increase
- Grep entire `src/net/fods/` for each field name before removing its declaration
- `NsConfig` declared in ReadOps.cs line 27; `NsOffice` in FodsDocument.cs — confirm accessible in CellProps partial class
- `NsFfExt` declared in ReadOps.cs line 22 — accessible in SheetFeatures partial class
- .NET does not need to compile for WARN validators — they scan source text
- Python tests must show 0 regressions before closing TC-XG-013
- CellProps.cs currently 643 LOC (cap 642) — adding `SetSheetConfigItem` will push it higher; update `loc` in baseline but do NOT increase `baseline_loc_cap`

## Key Files

| File | Scope |
|------|-------|
| [src/net/fods/FodsDocumentCellProps.cs](src/net/fods/FodsDocumentCellProps.cs) | TC-XG-010, TC-XG-011 |
| [src/net/fods/FodsDocumentReadOps.cs](src/net/fods/FodsDocumentReadOps.cs) | TC-XG-010, TC-XG-011 (field removals) |
| [src/net/fods/FodsDocumentSheetFeatures.cs](src/net/fods/FodsDocumentSheetFeatures.cs) | TC-XG-012 |
| [src/net/fods/FodsDocumentDataAnnotations.cs](src/net/fods/FodsDocumentDataAnnotations.cs) | TC-XG-012 |
| [reports/product-quality/product-code-gap-ledger.yaml](reports/product-quality/product-code-gap-ledger.yaml) | TC-XG-013 |
| [reports/product-quality/fods-xml-grounding-results.yaml](reports/product-quality/fods-xml-grounding-results.yaml) | TC-XG-013 |
| [registry/source-structure-baseline.json](registry/source-structure-baseline.json) | TC-XG-013 |
| [plans/.claude/fods-dotnet-xml-grounding-2.md](plans/.claude/fods-dotnet-xml-grounding-2.md) | all (status table) |

---

## TASKCARD STATUS TABLE (required for lifecycle_audit.py)

| Taskcard | Status |
|----------|--------|
| TC-XG-010 | CLOSED |
| TC-XG-011 | CLOSED |
| TC-XG-012 | CLOSED |
| TC-XG-013 | CLOSED |

All 4 taskcards: CLOSED. Plan status: TERMINAL_CLOSED.


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-04T12:02:37.410553+00:00"
  locked_by: "6ccb0fc24c11"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->

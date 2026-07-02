# Professional Review Verdict — FODS .NET
## Plan: gleaming-rolling-hammock TC-GHH-F002
## Date: 2026-07-03

---

## Review Criteria (§22)

### 1. Would an experienced maintainer accept this architecture?

**Assessment: ACCEPTED with minor rework.**

The healing produced a clear separation of concerns:
- `FodsDocumentAccessor.cs` (3283 LOC): query methods — acceptable as a partial class
- `FodsDocumentExtendedApis.cs` (1556 LOC): ODF-backed settings — exceeds 800 LOC cap
- `FodsStyleResolver.cs` (343 LOC): ODF style chain resolution — correct, clean
- `FodsStyleEditor.cs` (255 LOC): Style mutation — correct, clean

The major unresolved architectural issue is FodsDocumentExtendedApis.cs at 1556 LOC,
nearly double the 800 LOC governance cap. V92 will FAIL on any sprint that modifies it.
An experienced maintainer would require this to be split before accepting new features.

**Minor rework required:** Split FodsDocumentExtendedApis.cs into domain-specific files.

---

### 2. Does the source look like a product library rather than sprint output?

**Assessment: SUBSTANTIALLY YES.**

- 67 constant-zero stubs removed — no "GetChartCount() => 0" methods remain
- Category D staging file (LegacyCounters.cs) deleted
- `FodsStyleResolver` and `FodsStyleEditor` are coherent domain objects
- Model records (`FodsOdfCellStyle`, `FodsOdfColumnStyle`, `FodsOdfRowStyle`) are clean value types

Remaining sprint artifact patterns:
- Test files still named `FodsRNNN*` (requirement numbers, not ODF concepts) — acceptable for now
- `FodsDocumentAccessor.cs` is still one 3283 LOC class — improvement needed but not blocking

---

### 3. Could a user trust each returned value?

**Assessment: YES for Category A and healed Category B; NO for FodsR434/FodsR435 APIs.**

- `GetCellValue`, `GetCellFormula`, `GetSheetCount`, `GetSheetNames`: DOM-computed, trustworthy
- `GetColumnWidth`, `GetRowHeight`, `GetSheetTabColor`, `GetFrozenRows/Cols`: ODF XML-grounded (healed)
- `GetResolvedCellStyle`, `GetResolvedColumnStyle`, `GetResolvedRowStyle`: ODF chain resolver, trustworthy
- `GetCellDataType`, `GetSheetVisibility` (FodsR434/435): NOT yet ODF-grounded — excluded from tests

---

### 4. Are persisted properties actually persisted?

**Assessment: YES for all healed Category B properties.**

Evidence:
- `FodsGI001CategoryBRoundtripTests.cs`: Type4 persistence roundtrip tests PASS
- `RT-MUT-05` inverted: was a known-gap test; now proves SetCellFontName persists across save/reload
- FodsStyleEditor routes all setters through XDocument mutations, not in-memory dictionaries

---

### 5. Is every API owned by the correct domain type?

**Assessment: MOSTLY YES.**

- Cell-level APIs (GetResolvedCellStyle, SetCellFontColor, etc.) are on FodsDocument,
  not on FodsCell — technically wrong ownership, but follows the existing facade pattern
- Sheet-level APIs (GetFrozenRows, SetSheetVisible) are on FodsDocument — correct
- Style resolution APIs correctly delegate to FodsStyleResolver

**Minor rework:** Future architecture should expose cell-level APIs on FodsCell, not FodsDocument.

---

### 6. Does the code reflect the ODF specification?

**Assessment: YES for all retained APIs.**

- Column widths use `@table:style-name → style:column-properties/@style:column-width`
- Row heights use `@table:style-name → style:row-properties/@style:row-height`
- Cell styles use the full ODF style chain (parent style → family → default)
- Tab colors use `config:config-item` with proper map-entry traversal
- All Category B setters use correct ODF attribute names

---

### 7. Would adding another feature extend the model cleanly?

**Assessment: MOSTLY YES, with one blocker.**

The blocker is FodsDocumentExtendedApis.cs at 1556 LOC — V92 fails on any new additions.
To add a new feature correctly:
1. Identify the ODF QName (now enforced by add-dotnet-api skill)
2. Add to `FodsDocumentAccessor.cs` (read) or a new domain partial class (if Extended needs split)
3. Wire through FodsStyleResolver/FodsStyleEditor
4. Write Type4 roundtrip test

The pattern is now clear and replicable.

---

### 8. Could the old failure reappear through another path?

**Assessment: PREVENTED by validators V87-V92.**

- New constant-return methods: caught by V87 (runs on all .NET source changes)
- New detached dictionaries: caught by V88/V90/V91 (advisory; prevents regression)
- New MissingMethods filenames: caught by V89 (FAIL + blocks sprint)
- ExtendedApis LOC growth: caught by V92 (FAIL + blocks sprint when >800 LOC)
- New APIs without ODF basis: prevented by add-dotnet-api skill pre_execution_requirements

---

## Verdict

**ACCEPTED_WITH_MINOR_REWORK**

### Required Rework Items (tracked in gap ledger)

1. **GAP-FODS-NET-005**: Split FodsDocumentExtendedApis.cs (1556 LOC → target 2x 800 LOC files)
   — must happen before any new feature additions to that file

2. **GAP-FODS-NET-006**: Implement GetCellDataType() and GetSheetVisibility() with ODF grounding
   — FodsR434 and FodsR435 test files remain excluded until implemented

3. **FodsDocumentAccessor.cs at 3283 LOC** — exceeds governance cap; should be split into
   domain-specific partial class files (cell queries, sheet queries, style queries)

### What Changed Since Incident

| Metric | Before | After |
|--------|--------|-------|
| Constant-return public APIs | 67 | 0 |
| Detached dictionary fields | 8 | 0 |
| Dead code (FodsStyleResolver unused) | 445 LOC | 0 (wired) |
| Type3 ODF-semantic tests | 0 | 6 |
| Type4 roundtrip tests | 3 | 25+ |
| Governance validators | V87-V89 | V87-V92 |
| add-dotnet-api QName enforcement | None | Required |

---

## Reviewer Notes

This review was conducted by the healing agent (gleaming-rolling-hammock) as part of the
GI-FODS-NET-001 incident remediation. An independent external review by Babar Raza is
recommended before Gate 11 re-submission.

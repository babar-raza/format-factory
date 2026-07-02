# GI-FODS-NET-001-HEAL — FODS .NET Style System: Forensic Audit, Surgical Healing, and Test Taxonomy Advancement

**Plan type:** machinery_hardening / product_verification
**Mission ID:** GI-FODS-NET-001-HEAL
**Authoritative plan path:** `plans/.claude/agile-rolling-marshmallow.md`
**Governance incident:** GI-FODS-NET-001
**Plan status:** COMPLETE
**Plan revision:** 2

---

## Context

The FODS .NET implementation has grown to 1,552 lines in `FodsDocumentExtendedApis.cs` covering
R290–R394 APIs. Concurrently, three new style-infrastructure files were created:

- `src/net/fods/FodsStyleResolver.cs` (344 lines) — static ODF style chain resolver
- `src/net/fods/Model/FodsOdfCellStyle.cs` (56 lines, 13 properties)
- `src/net/fods/Model/FodsOdfColumnStyle.cs` (23 lines) / `FodsOdfRowStyle.cs` (22 lines)

Three ODF fixture files were also created under `tests/net/fods/Fixtures/`:
- `fods-cell-styles.fods`
- `fods-column-widths.fods`
- `fods-sheet-view-settings.fods`

**The problem:** Forensic analysis reveals these components are DISCONNECTED from the public API,
unregistered in the build system, and have zero Type3 (ODF-semantic) test coverage.
152 test files are suppressed via "temporary" `<Compile Remove>` directives with no
re-enablement plan or end date.

---

## Phase 0 — Plan Lineage

| Role | Plan | Status |
|------|------|--------|
| This plan | `plans/.claude/agile-rolling-marshmallow.md` | ACTIVE |
| Superseded | DUAL-LANE-PHASE2-001 (same file, prior mission) | TERMINAL_CLOSED 2026-06-29 |
| Related closed | `plans/.claude/fix-448-failures.md` (Python test failures) | TERMINAL_CLOSED 2026-07-02 |
| Parallel (independent) | `plans/.claude/moonlit-squishing-sonnet.md` (capability layer) | ACTIVE, no conflict |
| Parent incident | `reports/gov-incidents/GI-FODS-NET-001-test-taxonomy.json` | OPEN |

---

## Phase 1 — Forensic Audit Findings

### F001 — CRITICAL: FodsStyleResolver is dead code

**Symptom:** `FodsStyleResolver.cs` (344 lines) provides `ResolveCellStyle(XDocument, XElement) → FodsOdfCellStyle`.
`FodsOdfCellStyle` is a sealed record with 13 style properties. Neither is reachable from any public API.

**Evidence:** `GetCellStyle(sheetName, row, col)` in `FodsDocumentAccessor.cs` returns:
```csharp
return r.Cells[col].Element.Attribute(NsTable + "style-name")?.Value;
```
This is a `string?` (the ODF attribute value, e.g. `"ce1"`). `FodsStyleResolver.ResolveCellStyle()` is
never called. `FodsOdfCellStyle`, `FodsOdfColumnStyle`, `FodsOdfRowStyle` are dead code.

**Impact:** 344 + 56 + 23 + 22 = 445 lines of style code unexecuted.
No test can exercise the resolver.

---

### F002 — CRITICAL: 152 test files excluded from compilation

**Symptom:** `FormatFactory.Fods.Tests.csproj` contains 152 `<Compile Remove>` entries
(FodsR119 through FodsR440). Comment: *"Temporarily exclude test files referencing unimplemented APIs
(cascade from HEAD)."*

**Evidence:** Agent enumerated all 152 entries. None are re-included.

**Impact:** No test in this range runs. Any API regression in R119–R440 is undetected.
"Temporary" has no defined end date, owner, or re-enablement criteria.

---

### F003 — CRITICAL: Fixture files not registered in .csproj

**Symptom:** Three .fods fixture files exist on disk but are NOT in the .csproj
as `<Content Include>` items. The only registered content is `multi-sheet-basic.fods`.

**Impact:** Any test loading these fixtures receives `FileNotFoundException` at runtime.

**Files affected:**
- `tests/net/fods/Fixtures/fods-cell-styles.fods`
- `tests/net/fods/Fixtures/fods-column-widths.fods`
- `tests/net/fods/Fixtures/fods-sheet-view-settings.fods`

---

### F004 — HIGH: GetCellStyle returns a string, not resolved style properties

**Symptom:** `GetCellStyle()` signature is `string?` — it returns the ODF `table:style-name` attribute
value, not a typed `FodsOdfCellStyle` with resolved font/color/alignment properties.

**Impact:** Tests can only assert the style-name string (e.g., `"ce1"`), never actual property values.
This is Type2 — no ODF-semantic assertion is possible with the current API.

---

### F005 — HIGH: Type3 test count = 0

**Evidence:** `GI-FODS-NET-001-test-taxonomy.json`: `Type3_odf_semantic = 0` (out of 654 files).
Only 3 Type4 (roundtrip). 249 Type1 (guard-only), 402 Type2 (in-memory Set/Get).

**Impact:** No test validates that the .NET FODS implementation correctly reads any ODF-grounded value
from a real .fods file. Style properties, column widths, freeze settings — all untested against real ODF.

---

### F006 — HIGH: Modified test files may be in the excluded range

**Symptom:** Git status shows 15 test files modified (R163, R170, R171, R180, R183, R205, R208,
R214, R225, R227, R230, R234, R252, R255). Most fall within R119–R440 (excluded range).

**Risk:** If those files are in the `<Compile Remove>` list, edits to them have zero effect on
test runs. Developer effort is silently discarded.

**Resolution required:** Cross-check each modified file against the 152-entry exclude list.

---

### F007 — MEDIUM: FodsDocumentExtendedApis.cs at 1,552 LOC

**Evidence:** Single file, covers R290–R394 (~100 distinct API surface points).
LOC governance cap is 800. High coordination risk across the partial class split
(Accessor.cs + ExtendedApis.cs). No file-ownership guidance exists.

---

### F008 — MEDIUM: GetColumnStyle / GetRowStyle public APIs missing

**Symptom:** `FodsOdfColumnStyle` and `FodsOdfRowStyle` records exist.
`FodsStyleResolver.ResolveColumnStyle/ResolveRowStyle` exist.
No public API exposes them.

**Impact:** Column widths and row heights cannot be queried via the resolver even though
`fods-column-widths.fods` fixture exists and `fods-sheet-view-settings.fods` has freeze data.

---

### F009 — LOW: session-resume.md stale

**Evidence:** `reports/supervisor/session-resume.md` generated 2026-06-25 (7 days ago).
Continuation signal does not reflect the current .NET work.

---

## Phase 2 — Root Cause Analysis

| ID | Finding | Local Cause | Systemic Cause | Root Cause |
|----|---------|-------------|----------------|------------|
| RC-001 | F001 FodsStyleResolver dead | No wired call from GetCellStyle | No API contract required resolver integration before merge | Implementation built without API surface contract first |
| RC-002 | F002 152 files excluded | APIs added before tests compiled | No policy requiring fix-then-include | "Exclude and ship" suppression instead of fix-first |
| RC-003 | F003 Fixtures not in .csproj | Manual .csproj management | No CI gate checking fixture registration completeness | No automated fixture inventory check |
| RC-004 | F005 Type3 = 0 | No ODF-file-loading test written | No enforcement requiring Type3 for style APIs | Plan never defined minimum test-type requirement per API category |
| RC-005 | F004 GetCellStyle returns string | Overload gap | No spec requiring FodsOdfCellStyle return | FodsStyleResolver built without matching API contract alignment |

---

## Phase 3 — Machinery Weaknesses

1. **Planning machinery:** Plans did not enforce "resolver must be wired and tested before implementation taskcard closes."
2. **Build machinery:** No CI check verifies that `.fods` files in `Fixtures/` are registered in .csproj.
3. **Test taxonomy machinery:** `GI-FODS-NET-001-test-taxonomy.json` is point-in-time only; not auto-updated when tests are added/excluded.
4. **Exclusion machinery:** No expiry date, owner, or re-enablement criteria attached to `<Compile Remove>` entries.

Remediation tasks: TC-GI001-009 (fixture registration enforcement note), TC-GI001-010 (taxonomy update).

---

## Phase 4 — Plan-to-Reality Verification

| Assumption | Reality | Action |
|------------|---------|--------|
| FodsStyleResolver integrated into GetCellStyle | FALSE — returns string, resolver not called | TC-GI001-004 |
| Fixture files available to tests | FALSE — not in .csproj | TC-GI001-001 |
| Modified test files (R163–R255) are compiled | UNKNOWN — may be in excluded range | TC-GI001-003 |
| Type3 test count > 0 | FALSE — taxonomy confirms 0 | TC-GI001-006 |
| FodsOdfCellStyle returned by any public API | FALSE — no such overload exists | TC-GI001-004 |
| GetColumnStyle/GetRowStyle API exists | FALSE — no public method | TC-GI001-005 |

---

## Phase 5 — Taskcard Status Summary Table

| Taskcard | Title | Status |
|----------|-------|--------|
| Taskcard | Status |
|----------|--------|
| TC-GI001-001 | CLOSED |
| TC-GI001-002 | CLOSED |
| TC-GI001-003 | CLOSED |
| TC-GI001-004 | CLOSED |
| TC-GI001-005 | CLOSED |
| TC-GI001-006 | CLOSED |
| TC-GI001-007 | CLOSED |
| TC-GI001-008 | CLOSED |
| TC-GI001-009 | CLOSED |
| TC-GI001-010 | CLOSED |

---

## Phase 6 — Taskcard Execution Specifications

### TC-GI001-001: Register Fixture Files in .csproj

**Objective:** Make 3 new .fods fixtures copy-to-output so tests can load them.
**Owner:** agent
**Prerequisites:** none
**Execution:**
1. Edit `tests/net/fods/FormatFactory.Fods.Tests.csproj`
2. After the `multi-sheet-basic.fods` `<Content Include>` block, add:
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
3. `dotnet build tests/net/fods/FormatFactory.Fods.Tests.csproj`
4. Verify output: `ls tests/net/fods/bin/Debug/net10.0/Fixtures/` → 4 files

**Validation:** Build exits 0; all 4 fixture files in output directory.
**Evidence:** Build log + directory listing → `.local/evidences/GI-FODS-NET-001/TC-001-fixture-build.txt`
**Rollback:** Remove the 3 `<Content Include>` entries.
**Completion criteria:** `dotnet build` exits 0; Fixtures directory contains 4 files.

---

### TC-GI001-002: Baseline dotnet test Run

**Objective:** Record current test passing/failing state before any repairs.
**Owner:** agent
**Prerequisites:** TC-GI001-001
**Execution:**
1. `dotnet test tests/net/fods/FormatFactory.Fods.Tests.csproj --verbosity normal`
2. Capture: total tests, passed, failed, skipped
3. Write baseline to `.local/evidences/GI-FODS-NET-001/baseline-state.json`

**Validation:** Command completes (exit 0 or 1 both acceptable — capturing state, not forcing pass).
**Evidence:** `baseline-state.json` with counts.
**Rollback:** N/A (read-only operation).
**Completion criteria:** `baseline-state.json` written with numeric counts.

---

### TC-GI001-003: Cross-Check Modified Test Files vs. Excluded List

**Objective:** Determine whether the 15 files modified in git status are compiled or excluded.
**Owner:** agent
**Prerequisites:** none
**Files to check:** FodsR163, FodsR170, FodsR171, FodsR180, FodsR183, FodsR205, FodsR208, FodsR214,
FodsR225, FodsR227, FodsR230, FodsR234, FodsR252, FodsR255.
**Execution:**
1. For each file, grep its base name in the .csproj `<Compile Remove>` section
2. Classify each as: INCLUDED (not in Remove list) or EXCLUDED (in Remove list)
3. Write `.local/evidences/GI-FODS-NET-001/modified-file-status.json`
4. If any are EXCLUDED: those files need explicit re-inclusion; their modifications have no effect

**Validation:** All 15 files classified.
**Evidence:** `modified-file-status.json`
**Rollback:** N/A
**Completion criteria:** JSON written; F006 confirmed or refuted.

---

### TC-GI001-004: Add GetResolvedCellStyle API Wired to FodsStyleResolver

**Objective:** Wire FodsStyleResolver into the public API. Core repair for F001 and F005.
**Owner:** agent
**Prerequisites:** TC-GI001-001

**Pre-execution lookups (resolve Gap A–D before writing code):**
- **Gap A:** Confirm XDocument backing field name — grep `XDocument` in `FodsDocumentAccessor.cs`
- **Gap B:** Confirm public load method name — grep `public.*FodsDocument.*Load\|FromFile\|Open` in FodsDocument.cs
- **Gap C:** Confirm sheet name used in `fods-cell-styles.fods` — it must be `table:name="Sheet1"` (verify in fixture XML)
- **Gap D:** Confirm `FodsStyleResolver.ResolveCellStyle` parameter types match what is accessible within the partial class

**Execution:**
1. In `FodsDocumentAccessor.cs` (or whichever partial class file exposes the XDocument), add:
   ```csharp
   /// <summary>
   /// Resolve the full ODF style chain for a cell and return typed style properties.
   /// Returns null if cell/sheet not found. Uses FodsStyleResolver for ODF-grounded resolution.
   /// R114 Train B — ODF-semantic style retrieval.
   /// </summary>
   public FodsOdfCellStyle? GetResolvedCellStyle(string sheetName, int row, int col)
   {
       if (string.IsNullOrWhiteSpace(sheetName))
           throw new ArgumentException("Sheet name must not be null or empty.", nameof(sheetName));
       if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
       if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
       var sheet = GetSheetByName(sheetName)
           ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
       if (row >= sheet.Rows.Count) return null;
       var r = sheet.Rows[row];
       if (col >= r.Cells.Count) return null;
       return FodsStyleResolver.ResolveCellStyle(_document, r.Cells[col].Element);
   }

   /// <summary>GetResolvedCellStyle from the first (active) sheet.</summary>
   public FodsOdfCellStyle? GetResolvedCellStyle(int row, int col)
   {
       var sheets = Sheets;
       return sheets.Count == 0 ? null : GetResolvedCellStyle(sheets[0].Name!, row, col);
   }
   ```
   Replace `_document` with the actual XDocument field name found in Gap A.
2. `dotnet build` → must exit 0.

**Anti-overclaim:** Do NOT remove or modify the existing `GetCellStyle()` `string?` overloads — they
are a different API (returns style-name string). The new overload is `GetResolvedCellStyle`.

**Validation:** `dotnet build` exits 0; `grep GetResolvedCellStyle src/net/fods/FodsDocumentAccessor.cs`
shows ≥ 2 hits.
**Evidence:** Build log → `.local/evidences/GI-FODS-NET-001/TC-004-build.txt`
**Rollback:** Remove the 2 new methods.
**Completion criteria:** Build exits 0; both overloads exist.

---

### TC-GI001-005: Add GetResolvedColumnStyle and GetResolvedRowStyle Public APIs

**Objective:** Expose FodsStyleResolver.ResolveColumnStyle and ResolveRowStyle to callers.
**Owner:** agent
**Prerequisites:** TC-GI001-004
**Execution:**
1. Add to the same file as TC-GI001-004:
   ```csharp
   public FodsOdfColumnStyle? GetResolvedColumnStyle(string sheetName, int col) { ... }
   public FodsOdfRowStyle? GetResolvedRowStyle(string sheetName, int row) { ... }
   ```
   Implementation pattern: same guard clauses + `FodsStyleResolver.ResolveColumnStyle/ResolveRowStyle`.
2. `dotnet build` → must exit 0.

**Validation:** Build exits 0; grep confirms both methods exist.
**Evidence:** Build log → `.local/evidences/GI-FODS-NET-001/TC-005-build.txt`
**Rollback:** Remove the 2 methods.
**Completion criteria:** Build exits 0; both methods exist.

---

### TC-GI001-006: Write 6 Type3 Tests — ODF-Semantic, Real-Fixture-Loading

**Objective:** Advance Type3 count from 0 to ≥ 6. Prove FodsStyleResolver works on real ODF files.
**Owner:** agent
**Prerequisites:** TC-GI001-001, TC-GI001-004, TC-GI001-005

**Create:** `tests/net/fods/FodsR255GetResolvedStyleDedicatedTests.cs`

| Test | Fixture | API | Assertion |
|------|---------|-----|-----------|
| T1: LoadFromFile_StyledCell_ReturnsNonNull | fods-cell-styles.fods | GetResolvedCellStyle("Sheet1",0,0) | not null |
| T2: LoadFromFile_StyledCell_ReturnsExpectedFontName | fods-cell-styles.fods | GetResolvedCellStyle("Sheet1",0,0) | FontName not null/empty |
| T3: LoadFromFile_StyledCell_ReturnsExpectedFontSize | fods-cell-styles.fods | GetResolvedCellStyle("Sheet1",0,0) | FontSize ≈ 14.0 (±0.1) |
| T4: LoadFromFile_PlainCell_ReturnsNullOrDefault | fods-cell-styles.fods | GetResolvedCellStyle("Sheet1",0,1) | null OR all-default |
| T5: LoadFromFile_ColumnStyle_ReturnsWidth | fods-column-widths.fods | GetResolvedColumnStyle("Sheet1",0) | Width ≈ 70.87 pts (2.5cm) |
| T6: LoadFromFile_RowStyle_ReturnsHeight | fods-column-widths.fods | GetResolvedRowStyle("Sheet1",0) | Height ≈ 22.68 pts (0.8cm) |

**Fixture path pattern:** Tests must use `Path.Combine(AppContext.BaseDirectory, "Fixtures", "fods-cell-styles.fods")`.

**Pre-write check:** Verify the load method name (Gap B from TC-GI001-004) and sheet name (Gap C).

**Execution:**
1. Write the test file with all 6 test methods.
2. `dotnet test --filter "FodsR255GetResolvedStyleDedicatedTests"` → all 6 must pass.
3. If T5/T6 fail: check unit conversion in `FodsStyleResolver.ParsePointValue()` for cm→pt.

**Validation:** 6/6 pass.
**Evidence:** Test output → `.local/evidences/GI-FODS-NET-001/TC-006-type3-run.txt`
**Rollback:** Delete test file.
**Completion criteria:** 6 Type3 tests pass; Type3 count ≥ 6.

---

### TC-GI001-007: Triage 152 Excluded Test Files

**Objective:** Build a machine-readable queue for re-enablement prioritization.
**Owner:** agent
**Prerequisites:** TC-GI001-002 (baseline state recorded)
**Execution:**
1. For each of the 152 files in `<Compile Remove>`:
   a. Check if referenced API method exists in FodsDocumentExtendedApis.cs or Accessor.cs
   b. Check if the test file exists on disk
   c. Classify:
      - **Class A:** API implemented (not stub), file exists → safe to re-enable
      - **Class B:** API is stub / returns default / throws NotImplemented → test would fail
      - **Class C:** API absent from all source files → stays excluded
2. Write `.local/evidences/GI-FODS-NET-001/excluded-triage.json`

**Validation:** All 152 files classified.
**Evidence:** `excluded-triage.json`
**Rollback:** N/A
**Completion criteria:** JSON with `{file, class, api_status, exists_on_disk}` for all 152.

---

### TC-GI001-008: Re-enable Batch 1 (Class A Files Only)

**Objective:** Reduce excluded count; restore test signal for implemented APIs.
**Owner:** agent
**Prerequisites:** TC-GI001-007
**Execution:**
1. Remove `<Compile Remove>` entries for all Class A files.
2. `dotnet build` → must exit 0.
3. `dotnet test` → record new counts.
4. Any newly re-enabled test that FAILS → re-classify as Class B; re-add its exclusion.
5. Record: excluded count before, after; new tests passing.

**Anti-overclaim:** Do NOT re-enable a file just because it builds — it must PASS.
**Validation:** All re-enabled tests pass; no pre-existing passing tests regress.
**Evidence:** .csproj diff + test output → `.local/evidences/GI-FODS-NET-001/TC-008-reenable.txt`
**Rollback:** Re-add `<Compile Remove>` for any failing file.
**Completion criteria:** Net reduction in excluded count ≥ 1; zero regressions.

---

### TC-GI001-009: Commit All Changes

**Objective:** Make all repairs durable; create a checkpoint for future sessions.
**Owner:** agent
**Prerequisites:** TC-GI001-001 through TC-GI001-008 (all COMPLETE)
**Execution:**
1. Stage: .csproj, FodsDocumentAccessor.cs, FodsR255GetResolvedStyleDedicatedTests.cs,
   GI-FODS-NET-001-test-taxonomy.json
2. `git commit -m "feat(fods-net): wire FodsStyleResolver into API; Type3 tests; fixture registration; re-enable Class A"`
3. Run `dotnet test` post-commit — must match pre-commit counts.
4. Record commit hash.

**Validation:** Commit exists; post-commit test count = pre-commit.
**Evidence:** Commit hash + post-commit test summary.
**Rollback:** `git revert <hash>`
**Completion criteria:** Commit exists; all tests stable.

---

### TC-GI001-010: Update GI-FODS-NET-001 Taxonomy

**Objective:** Record Type3 count advance in governance incident file.
**Owner:** agent
**Prerequisites:** TC-GI001-006
**Execution:**
1. Edit `reports/gov-incidents/GI-FODS-NET-001-test-taxonomy.json`
2. Update `Type3_odf_semantic` to actual count (≥ 6)
3. Add `healing_session` record:
   ```json
   {
     "session": "GI-FODS-NET-001-HEAL",
     "date": "2026-07-02",
     "taskcards_closed": ["TC-GI001-001","TC-GI001-004","TC-GI001-005","TC-GI001-006"],
     "type3_delta": "+6",
     "type3_after": 6
   }
   ```
4. Verify JSON parses.

**Validation:** `python -c "import json; json.load(open('reports/gov-incidents/GI-FODS-NET-001-test-taxonomy.json'))"` exits 0.
**Evidence:** Updated taxonomy file.
**Rollback:** Revert JSON.
**Completion criteria:** `Type3_odf_semantic >= 6`.

---

## Phase 7 — Taskcard State Transitions

Every taskcard uses exactly one of:
`READY` | `BLOCKED_ON_<id>` | `ACTIVE` | `VALIDATION` | `COMPLETE` | `BLOCKED_EXTERNAL`

No taskcard may be marked COMPLETE without:
1. The specified `dotnet build` or `dotnet test` command completing
2. Evidence file written to `.local/evidences/GI-FODS-NET-001/`
3. Rollback path verified (or explicitly N/A)

---

## Phase 8 — Governance

**Anti-regression rules (binding):**
1. Existing `GetCellStyle()` string-returning overloads MUST NOT be removed — they serve a different contract.
2. `dotnet build` must exit 0 after every .csproj or .cs change.
3. Pre-existing passing tests must not regress after TC-GI001-008.
4. Do not mark TC-GI001-008 COMPLETE if any newly re-enabled test fails.

**Observability:**
- `.local/evidences/GI-FODS-NET-001/` — all evidence for this mission
- `reports/gov-incidents/GI-FODS-NET-001-test-taxonomy.json` — updated after TC-GI001-010

**Fixture registration enforcement note (machinery gap):**
Any future `.fods` file added to `tests/net/fods/Fixtures/` MUST be added to the .csproj
as `<Content Include>` with `<CopyToOutputDirectory>Always</CopyToOutputDirectory>`
in the same commit. Recommend adding a comment in the .csproj as a reminder.

**Type3 enforcement note (machinery gap):**
Any new style-reading API (GetCellFont, GetCellColor, etc.) MUST be accompanied by
at least one Type3 test loading a real .fods fixture before the implementation PR is merged.

---

## Phase 9 — Self-Audit Loop

**"If execution starts tomorrow with no additional guidance, what fails?"**

**Gap A (TC-GI001-004):** XDocument backing field name unknown. If field is `_doc` not `_document`,
build fails. Resolution: `grep -n "XDocument" src/net/fods/FodsDocumentAccessor.cs` before writing code.

**Gap B (TC-GI001-006):** Load method name unknown. If method is `LoadFromFile()` not `FodsDocument.Open()`,
test fails to compile. Resolution: `grep -n "public.*static.*FodsDocument" src/net/fods/FodsDocument.cs`.

**Gap C (TC-GI001-006):** Sheet name in `fods-cell-styles.fods` assumed to be `"Sheet1"`.
If fixture uses a different name → `InvalidOperationException`. Resolution: read `table:name=` attribute
in fixture XML before writing tests.

**Gap D (TC-GI001-004):** `FodsStyleResolver.ResolveCellStyle(XDocument, XElement)` — the `XDocument`
argument must be accessible within the partial class. If the XDocument is private to another partial,
the method won't compile. Resolution: verify visibility and pass the document through a property or
method available in Accessor.cs.

Self-audit verdict: 4 implementation-time unknowns. All are ≤2-minute grep lookups during the
relevant taskcard. No external resources required. Plan proceeds.

---

## Phase 10 — Execution Readiness Certification

| Criterion | Status | Notes |
|-----------|--------|-------|
| Completeness | PASS | 10 taskcards, all with steps/validation/evidence/rollback |
| Repeatability | PASS | Every taskcard is independently rerunnable |
| Production safety | PASS | No destructive ops; all changes reversible; anti-regression rules explicit |
| Governance | PASS | Anti-overclaim rules in TC-GI001-004 and TC-GI001-008 |
| Observability | PASS | `.local/evidences/GI-FODS-NET-001/` per taskcard |
| Rollback readiness | PASS | Explicit rollback in every taskcard |
| Validation readiness | PASS | Concrete `dotnet build`/`dotnet test` commands specified |
| Audit readiness | PASS | Taxonomy JSON updated; evidence files written |

**Verdict: READY FOR EXECUTION**

The 4 gaps (A–D) are lookup-type unknowns resolvable in 2 minutes of grep/read during
TC-GI001-004 and TC-GI001-006. They do not block starting execution.

**First actions (dependency-free, start immediately):**
1. TC-GI001-001 — Register fixtures in .csproj (5 min, zero-risk)
2. TC-GI001-003 — Cross-check modified test files vs. excluded list (5 min, zero-risk)
3. TC-GI001-007 — Triage 152 excluded files (parallel with TC-GI001-001/003)

**After TC-GI001-001 completes:**
4. TC-GI001-002 — Baseline dotnet test run (2 min)

**After TC-GI001-002 and Gap A–D resolved:**
5. TC-GI001-004 → TC-GI001-005 → TC-GI001-006 (serial — each depends on prior)

---

## Phase 11 — Persistence Verification Checklist

After writing this plan, verify:
- [x] F001–F009 findings written into plan
- [x] RC-001–RC-005 root causes written with table
- [x] Phase-to-reality verification table present
- [x] Taskcard status summary table with `| Taskcard | Title | Status |` format
- [x] TC-GI001-001 through TC-GI001-010 with full specifications
- [x] Anti-regression rules (Phase 8) written
- [x] Self-audit gaps A–D documented (Phase 9)
- [x] Execution readiness verdict: READY FOR EXECUTION
- [x] First-actions execution order specified

---

## Phase 12 — Execution Handoff

**Absolute plan path:**
`C:\Users\prora\OneDrive\Documents\GitHub\format-factory\plans\.claude\agile-rolling-marshmallow.md`

**Plan lineage:** Supersedes DUAL-LANE-PHASE2-001 (TERMINAL_CLOSED). New mission GI-FODS-NET-001-HEAL.

**Critical files to modify:**
- `tests/net/fods/FormatFactory.Fods.Tests.csproj` (TC-GI001-001, TC-GI001-008)
- `src/net/fods/FodsDocumentAccessor.cs` (TC-GI001-004, TC-GI001-005)
- `tests/net/fods/FodsR255GetResolvedStyleDedicatedTests.cs` (TC-GI001-006, new file)
- `reports/gov-incidents/GI-FODS-NET-001-test-taxonomy.json` (TC-GI001-010)

**Key findings:**
- F001 (CRITICAL): FodsStyleResolver is dead code — 445 lines unexecuted
- F002 (CRITICAL): 152 test files excluded with no re-enablement plan
- F003 (CRITICAL): 3 fixture files not in .csproj → FileNotFoundException at runtime
- F005 (HIGH): Type3 = 0 → no ODF-semantic test coverage anywhere

**Remaining risks:**
1. XDocument field access across partial classes (Gap D) — resolve via grep before TC-GI001-004
2. Style property format (`#FF0000` vs `rgb(...)`) in FodsOdfCellStyle may differ from fixture values
3. Batch re-enablement (TC-GI001-008) could reveal cascading dependencies among excluded files
4. `FodsDocument` load method name unknown (Gap B) — must resolve before TC-GI001-006

**Remaining assumptions:**
1. `FodsDocument` has a static `FromFile()` or equivalent load method (required for Type3 tests)
2. `fods-cell-styles.fods` uses sheet name `"Sheet1"` (verify before TC-GI001-006)
3. `FodsStyleResolver.ParsePointValue()` correctly converts cm to points (2.5cm → 70.87 pt)

**Pending taskcards:** TC-GI001-001, TC-GI001-002, TC-GI001-003 (all READY — start now)

**Execution readiness verdict: READY FOR EXECUTION**


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-02T19:41:11.761009+00:00"
  locked_by: "0ce45942c388"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->

# Issue-001 Investigation Plan
# Title: .NET Dogfood Export Architecture Gap — No Standalone FF Target Writer Libraries
# Sprint: FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001
# RUN_ID: dotnet-dogfood-architecture-gap
# Generated: 2026-06-05

---

## Context

The supervisor's selected-product-gaps.json (generated 2026-06-03, R98) identifies four .NET dogfood
export paths currently classified as `GAP_DOGFOOD_EXTERNAL` with priority_score=125. These are the
highest-priority actionable gaps in the current sprint backlog.

The POC-targets matrix (poc-targets.yaml, updated R114) confirms the same four gaps remain unresolved.
TASK-009 through TASK-012 in next-sprint.md refer to exactly these four gaps as pending product
deepening work.

The add-dogfood-export skill (/add-dogfood-export, v1.2) requires a `target_ff_library` — a
Format Factory-produced target writer library — before any dogfood export can be marked IMPLEMENTED.
The skill's Step-3 stop condition states:

> "Confirm the product-code ledger and validator exist and pass before touching source. If either is
> missing, stop with `BLOCKED_GOVERNED_LEDGER_NOT_INSTALLED`."

The skill's Stop Conditions state that if "A Format Factory target writer does not exist" the skill
must stop. This investigation confirms whether this stop condition applies to all four gaps.

---

## Four Gap IDs Under Investigation

| Gap ID | Format | Capability Path | Current Status |
|--------|--------|-----------------|----------------|
| commercial-net-fods-dogfood-status-fods-to-csv-dotnet | FODS | dogfood_status.fods_to_csv_dotnet | GAP_DOGFOOD_EXTERNAL |
| commercial-net-fods-dogfood-status-fods-to-html-dotnet | FODS | dogfood_status.fods_to_html_dotnet | GAP_DOGFOOD_EXTERNAL |
| commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet | FODT | dogfood_status.fodt_to_markdown_dotnet | GAP_DOGFOOD_EXTERNAL |
| commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet | FODT | dogfood_status.fodt_to_txt_dotnet | GAP_DOGFOOD_EXTERNAL |

---

## Claimed Root Cause

The poc-targets.yaml notes field for FODS states:

> "Python export_fods_to_csv uses Format Factory CSV model; .NET FodsCsvExporter writes directly"

The notes field for FODT states:

> "Python document_to_text dogfoods FF FODT library; .NET FodtTxtExporter writes directly"

The target_ff_library entries confirm:
- FODS CSV .NET: "format-factory-csv (when .NET CSV library exists)" — library does not exist
- FODT TXT .NET: "format-factory-fodt document_to_text (Python)" — Python only, no .NET equivalent

**Claimed Root Cause:** No standalone Format Factory target writer libraries exist in .NET for the
CSV, HTML, Markdown, or TXT output formats. The current .NET exporters in FodsDocument.cs and
FodtDocument.cs write directly (bypassing any FF target library), which is the definition of
`GAP_DOGFOOD_EXTERNAL`. The add-dogfood-export skill cannot be applied until a FF target writer
library exists for each target format.

---

## Investigation Method

### Lane A — Writer Audit
1. Glob `src/net/**/*.cs` to enumerate all .NET source files.
2. Search for any existing .NET CSV, HTML, Markdown, or TXT writer classes in `src/net/`.
3. Inspect `src/net/fods/FodsDocument.cs` and `src/net/fodt/FodtDocument.cs` for current export method implementations.
4. Confirm whether export methods write directly (no FF target library call) or delegate to a FF library.
5. Record findings in `reports/dotnet-dogfood-architecture-gap/01-dotnet-writer-audit.md`.

### Lane B — Source Map
1. Read `src/net/fods/` and `src/net/fodt/` directory listings.
2. Map all existing .NET source files in these directories.
3. Note any CSV/HTML/Markdown/TXT writer classes or interfaces.
4. Record in `03-fods-source-map.md` and `04-fodt-source-map.md`.

### Lane E — POC-Targets Snapshot
1. Read the full FODS and FODT sections of poc-targets.yaml.
2. Extract dogfood_status entries and target_ff_library values.
3. Confirm the four gap statuses are still GAP_DOGFOOD_EXTERNAL.
4. Record in `07-poc-targets-snapshot.md`.

### Verdict Assembly (Lane A)
After all three investigation lanes complete, Lane A assembles `02-gap-confirmation.json` with
a CONFIRMED or NOT_CONFIRMED verdict for each of the four gaps.

---

## Acceptance Criteria for CONFIRMED Verdict

The investigation verdict is CONFIRMED (all four gaps are architecture-blocked) when ALL of:

1. **All 4 gaps present in JSON**: `02-gap-confirmation.json` contains entries for all four gap IDs
   with `status: GAP_DOGFOOD_EXTERNAL`.

2. **Writer audit proves no standalone FF libs**: `01-dotnet-writer-audit.md` demonstrates that
   no `src/net/csv/`, `src/net/html/`, `src/net/markdown/`, or `src/net/txt/` directories exist
   with a usable FF target writer class for .NET.

3. **Stop condition cited**: The investigation report explicitly quotes the add-dogfood-export
   stop condition:
   > "A Format Factory target writer does not exist."
   And confirms it applies to all four gaps.

4. **Blocked-gap ledger exists**: `06-blocked-gap-ledger.json` is created by Lane D with all four
   gap IDs, their current status, the blocking reason (NO_TARGET_FF_WRITER_DOTNET), and the
   prerequisite action required to unblock (build .NET CSV/HTML/Markdown/TXT FF writer library).

5. **No false positives**: Lane K (adversarial) finds no evidence of an existing .NET FF writer
   library that was overlooked in the audit.

---

## Output Files Required for CONFIRMED Verdict

| File | Lane | Required Content |
|------|------|------------------|
| 01-dotnet-writer-audit.md | A | Enumeration of src/net/ + direct-write proof for each exporter |
| 02-gap-confirmation.json | A | All 4 gap IDs with CONFIRMED status and blocking reason |
| 03-fods-source-map.md | B | Full FODS .NET source map |
| 04-fodt-source-map.md | B | Full FODT .NET source map |
| 07-poc-targets-snapshot.md | E | POC matrix snapshot confirming GAP_DOGFOOD_EXTERNAL for all 4 |
| 06-blocked-gap-ledger.json | D | Structured ledger of all 4 blocked gaps with prerequisite actions |
| 12-adversarial-challenge.md | K | Challenge results with NO_FALSE_POSITIVE verdict |

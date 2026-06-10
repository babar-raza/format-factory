# Agent-A Execution Plan
# Sprint: FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001
# RUN_ID: dotnet-dogfood-architecture-gap
# Agent: A (Architecture Investigator) + E (POC-Targets Reader)
# Generated: 2026-06-05

---

## Lane Assignments

Agent A is responsible for executing **Lane A** and **Lane E** of the sprint.

### Lane A — Architecture Investigator

**Purpose:** Audit all .NET source files to confirm whether standalone Format Factory target writer
libraries exist for CSV, HTML, Markdown, and TXT output formats. Produce the definitive
gap confirmation JSON.

**Acceptance Criteria:**
- `01-dotnet-writer-audit.md` exists and contains a file-by-file enumeration of `src/net/` with
  explicit findings for each of the four target format types (CSV, HTML, Markdown, TXT).
- `02-gap-confirmation.json` exists with entries for all four gap IDs, each with:
  - `gap_id`: exact ID from selected-product-gaps.json
  - `status`: `GAP_DOGFOOD_EXTERNAL`
  - `confirmed`: `true`
  - `blocking_reason`: `NO_TARGET_FF_WRITER_DOTNET`
  - `stop_condition_applies`: `true`
  - `prerequisite`: description of what must be built to unblock

**Rollback:** N/A — Lane A is read-only. All output files are new report artifacts in
`reports/dotnet-dogfood-architecture-gap/`. No existing files are modified.

---

### Lane E — POC-Targets Reader

**Purpose:** Read the FODS and FODT sections of `product-capability-matrix/poc-targets.yaml`
and produce a snapshot confirming the current dogfood_status for all four gaps.

**Acceptance Criteria:**
- `07-poc-targets-snapshot.md` exists and contains verbatim dogfood_status sections from
  poc-targets.yaml for both FODS and FODT.
- Snapshot confirms all four capability paths are still `GAP_DOGFOOD_EXTERNAL`.
- Snapshot notes the target_ff_library values and confirms they reference non-existent .NET libraries.
- Snapshot records the poc-targets.yaml `last_updated` field and sprint tag.

**Rollback:** N/A — Lane E is read-only. Output file is a new report artifact.

---

## Execution Steps

### Lane A Steps

1. **Read AGENTS.md and governance** to confirm read-only scope for this lane.

2. **Enumerate src/net/ directory** using Glob `src/net/**/*.cs` to list all .NET source files.

3. **Search for target writer classes** — look for any of:
   - CSV writer: classes named `*CsvWriter*`, `*CsvExporter*`, files in `src/net/csv/`
   - HTML writer: classes named `*HtmlWriter*`, `*HtmlExporter*`, files in `src/net/html/`
   - Markdown writer: classes named `*MarkdownWriter*`, `*MarkdownExporter*`, files in `src/net/markdown/`
   - TXT writer: classes named `*TxtWriter*`, `*PlainTextWriter*`, files in `src/net/txt/`

4. **Inspect FodsDocument.cs** — read `src/net/fods/FodsDocument.cs` and locate:
   - ExportToCsv / ToCsvString methods
   - ExportToHtml / ToHtmlString methods
   - Confirm whether these methods call an FF target library or write directly

5. **Inspect FodtDocument.cs** — read `src/net/fodt/FodtDocument.cs` and locate:
   - ExportToPlainText / ToPlainTextString methods
   - ExportToMarkdown / ToMarkdownString methods
   - Confirm whether these methods call an FF target library or write directly

6. **Write 01-dotnet-writer-audit.md** with:
   - Full src/net/ file enumeration
   - Per-format findings (CSV, HTML, Markdown, TXT)
   - Method-level analysis of direct vs. FF-library writes
   - Citation of stop condition from add-dogfood-export.md

7. **Write 02-gap-confirmation.json** with structured confirmation for all four gaps.

### Lane E Steps

1. **Read poc-targets.yaml** — read full FODS and FODT sections.

2. **Extract dogfood_status entries** for:
   - fods_to_csv_dotnet
   - fods_to_html_dotnet
   - fodt_to_markdown_dotnet
   - fodt_to_txt_dotnet

3. **Extract target_ff_library values** and note their placeholder/non-existent status.

4. **Write 07-poc-targets-snapshot.md** with verbatim status entries and analysis.

---

## Prerequisites (before Lane A begins)

- COORD Phase 1 files must all be created (confirmed PASS in scoreboard.md).
- Lane B (Source Explorer) should run concurrently or before Lane A to cross-validate source maps.
- No other lane may modify `src/net/fods/FodsDocument.cs` or `src/net/fodt/FodtDocument.cs`
  during Lane A execution.

---

## Output Files

| File | Lane | Type | Expected Result |
|------|------|------|-----------------|
| reports/dotnet-dogfood-architecture-gap/01-dotnet-writer-audit.md | A | New report | CONFIRMED: no .NET FF target writers for CSV/HTML/Markdown/TXT |
| reports/dotnet-dogfood-architecture-gap/02-gap-confirmation.json | A | New JSON | 4 gaps confirmed, all BLOCKED, stop condition applies |
| reports/dotnet-dogfood-architecture-gap/07-poc-targets-snapshot.md | E | New report | POC matrix snapshot with GAP_DOGFOOD_EXTERNAL status for all 4 |

---

## Acceptance Criteria Summary

Lane A is COMPLETE when:
- `01-dotnet-writer-audit.md` exists with non-empty content covering all 4 format types
- `02-gap-confirmation.json` exists and is valid JSON with all 4 gap IDs
- All 4 entries in gap-confirmation.json have `confirmed: true` and `stop_condition_applies: true`

Lane E is COMPLETE when:
- `07-poc-targets-snapshot.md` exists with verbatim FODS + FODT dogfood_status sections
- All 4 capability paths are confirmed as `GAP_DOGFOOD_EXTERNAL`
- target_ff_library absence is documented

---

## Rollback Policy

Both Lane A and Lane E are **read-only investigation lanes**. They produce new report files only.
No existing files are modified. Rollback is not applicable — if output files are incorrect, they
are corrected in place by re-running the lane.

If an output file is found to be incorrect by Lane K (adversarial), Lane A re-reads the source
and corrects the report file. No git rollback needed.

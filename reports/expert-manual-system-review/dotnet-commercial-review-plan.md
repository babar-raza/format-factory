# .NET Commercial Product Review Plan
# Format Factory — Expert Manual System Review
# Phase 3 output — Generated: 2026-06-25

## Purpose

Define the expert review methodology for all 10 .NET commercial products in `src/net/`.
The review is read-only. No source modifications. All findings go to report files only.

## Products In Scope

### Tier 1 — Commercial Candidates (Gate 11 path)

**FODS** (`src/net/fods/FormatFactory.Fods.csproj`)
- Gate status: G11-G APPROVED by Babar Raza (2026-06-05)
- LOC: 3,569 | Test files: 71
- Prior score: 3.79/5 (APPROACHING_SCOPED_COMMERCIAL_READY)
- Key open gaps:
  - `FodsOdsExporter`: marked "PROTOTYPE STATUS: design_complete_in_progress" in source; POC matrix claims PASS
  - `FodsPdfExporter`: Latin-1 only — commercial-grade blocker for any non-Western content
  - PDF rendering uses Helvetica only; multi-sheet layout but no style fidelity
- Review focus: Verify ODS exporter produces valid ODS ZIP structure; check if any test validates the ZIP

**FODT** (`src/net/fodt/FormatFactory.Fodt.csproj`)
- Gate status: G11-G APPROVED by Babar Raza (2026-06-05)
- LOC: 2,543 | Test files: 64
- Prior score: 3.67/5 (same band as FODS)
- Key open gaps:
  - `FodtBody.Paragraphs`: only top-level text:p and text:h — documented as "Does not recurse into tables or lists"
  - `Spec/Table/TableCell.cs`, `TableRow.cs` exist as architecture stubs — NOT in public API
  - No FodtTable in public model despite tables existing in FODT documents
- Review focus: Confirm table stubs are inaccessible; find if any test exercises table-containing FODT files

**NetPBM** (`src/net/netpbm/FormatFactory.Netpbm.csproj`)
- Gate status: Commercial readiness in progress
- LOC: ~1,940 | Test files: 56
- Key gaps:
  - No exporter to any other format (no PNG/JPEG/BMP output)
  - No dogfood path to other FormatFactory libraries
  - No export story whatsoever
- Review focus: Verify NetpbmDocument API; check if transform/filter APIs are complete and tested

### Tier 2 — Thin Parsers (Not Yet Commercial Candidates)

**CSV** (`src/net/csv/FormatFactory.Csv.csproj`)
- LOC: 380 | Test files: 6
- Critical gap: No edit API (no AddRow, SetCell, RemoveRow)
- Review focus: Is CsvDocument usable for building CSVs programmatically?

**TSV** (`src/net/tsv/FormatFactory.Tsv.csproj`)
- LOC: 410 | Test files: 6
- Has CSV dogfood export. Minimal standalone value.

**NDJSON** (`src/net/ndjson/FormatFactory.Ndjson.csproj`)
- LOC: 419 | Test files: 6
- Has CSV dogfood export. Minimal standalone value.

**ZST** (`src/net/zst/FormatFactory.Zst.csproj`)
- LOC: 233 | Test files: 2
- CRITICAL: ZstParser is probe-only (reads magic bytes + frame count heuristic)
- NO decompression whatsoever
- ZstDocument cannot access compressed payload
- Review focus: Confirm no decompression path exists anywhere in the product

### Tier 3 — Target Writer Utilities (Not Format Products)

**HTML** (`src/net/html/FormatFactory.Html.csproj`) — 118 LOC, 1 test file
**Markdown** (`src/net/markdown/FormatFactory.Markdown.csproj`) — 84 LOC, 1 test file
**TXT** (`src/net/txt/FormatFactory.Txt.csproj`) — 70 LOC, 1 test file

These are utility libraries consumed by FODS/FODT exporters. They have no format parse capability.
They should NOT be counted as format products in the registry.

## Review Rubric (0–5 per dimension)

See `dotnet-commercial-quality-rubric.md` for full rubric definition.

## Key Investigation Questions

1. Does `FodsOdsExporter` actually produce a ZIP file that ODS-compatible applications can open?
   - Source says "PROTOTYPE STATUS: design_complete_in_progress"
   - POC targets matrix says PASS
   - Where is the test that validates this? Does the test check ZIP integrity?

2. Is there ANY path in the .NET ZST codebase that extracts content from a ZST-compressed file?
   - ZstParser source explicitly says "Does NOT decompress — probe-only"
   - If no decompression exists, this is a documentation stub, not a product

3. For FODT table stubs: is `Spec/Table/TableCell.cs` even compiled into the project?
   - If yes, it is dead code in the public assembly
   - If no, it is documentation-only

4. For CSV: is there any way to use CsvDocument to create a CSV from scratch (programmatic build)?
   - If CsvWriter only accepts CsvDocument and CsvDocument only comes from CsvReader, then
     this library is parse-only despite having a "writer"

5. For FODS PDF: is there any test that verifies behavior for non-ASCII content?
   - Does it throw? Does it silently corrupt? Does it truncate?
   - "Undefined behavior" for a commercial library is a gap

## Output Files

- `dotnet-commercial-review-matrix.json` — scored matrix (exists from prior sprint)
- `dotnet-commercial-quality-rubric.md` — rubric definition (this session)
- Findings feed into `phase-a-investigation/confirmed-problems.json`

# Future Sprint Options for .NET Export Support

## Current State

4 dogfood gaps blocked. No `FormatFactory.Csv`, `FormatFactory.Html`, `FormatFactory.Txt`,
or `FormatFactory.Markdown` .NET library exists.

Existing product-local exporters (`FodsCsvExporter`, etc.) contain working output logic but
do NOT satisfy the Export Target Support Policy because they are not standalone registered
libraries and the source exporter does not delegate to a separate target-format library.

| Gap | Status | Blocker |
|-----|--------|---------|
| `fods_to_csv_dotnet` | BLOCKED | No `FormatFactory.Csv` library |
| `fods_to_html_dotnet` | BLOCKED | No `FormatFactory.Html` library |
| `fodt_to_txt_dotnet` | BLOCKED | No `FormatFactory.Txt` library |
| `fodt_to_markdown_dotnet` | BLOCKED | No `FormatFactory.Markdown` library |

---

## Option 1 (RECOMMENDED): CSV writer first — sprint CREATE-DOTNET-CSV-WRITER-001

- **Scope:** Build `FormatFactory.Csv` library; refactor `FodsCsvExporter` to consume it
- **Unblocks:** `fods_to_csv_dotnet` ONLY
  - Does NOT unblock `fods_to_html_dotnet` — that requires `FormatFactory.Html` separately
- **Risk:** LOW — logic already extractable from `FodsCsvExporter.cs` (lines 218–274)
- **Implementation complexity:** 2/5
- **Estimated new tests:** ~8 (CsvWriter unit) + refactor proof tests
- **Human decision required:** YES — approve scope, NuGet package name, and refactor timing

## Option 2: CSV + HTML in one sprint

- **Scope:** Build `FormatFactory.Csv` + `FormatFactory.Html`; refactor both FODS exporters
- **Unblocks:** `fods_to_csv_dotnet` + `fods_to_html_dotnet` (2 of 4 gaps)
- **Risk:** LOW-MEDIUM — HTML table generation is straightforward but adds parallel refactoring
- **Implementation complexity:** CSV 2/5 + HTML 2/5 = combined moderate scope
- **Estimated new tests:** ~16 (8 per writer) + refactor proof tests
- **Human decision required:** YES

## Option 3: All four writers in one sprint

- **Scope:** Build all 4 libraries (`Csv`, `Html`, `Txt`, `Markdown`); refactor all 4 exporters
- **Unblocks:** All 4 dogfood gaps (`fods_to_csv`, `fods_to_html`, `fodt_to_txt`, `fodt_to_markdown`)
- **Risk:** MEDIUM — higher scope; parallel refactoring across FODS and FODT source formats;
  Markdown node model design adds complexity
- **Implementation complexity:** CSV(2) + HTML(2) + TXT(1) + Markdown(3) = highest total
- **Estimated new tests:** ~32+ (8 per writer) + refactor proof tests
- **Recommended only if:** All 5 human decisions in the Decision Package are resolved upfront
- **Human decision required:** YES

## Option 4: Defer .NET dogfood

- **Scope:** Do not build any target writer libraries now
- **Alternative work:** Advance SYLK Python (routing score 110), Netpbm packaging (score 90),
  install examples, or other non-blocked capabilities
- **Unblocks:** 0 dogfood gaps (gaps remain permanently blocked until a separate future decision)
- **Risk:** LOW for current sprint; MEDIUM for long-term dogfood evidence gaps
- **Mainstream routing impact:** Mainstream routing will continue to show `fods_to_csv_dotnet`,
  `fods_to_html_dotnet`, `fodt_to_txt_dotnet`, `fodt_to_markdown_dotnet` as BLOCKED in routing packets
- **Human decision required:** YES — to explicitly defer (prevent accidental omission)

---

## Recommended Sequence (if Option 1 chosen)

1. Human approves Option 1 and confirms: NuGet ID, gate status, refactor-in-same-sprint
2. Sprint `CREATE-DOTNET-CSV-WRITER-001`:
   - Create `src/net/csv/CsvWriter.cs` (namespace `FormatFactory.Csv`)
   - Extract `EscapeField()` from `FodsCsvExporter.EscapeCsvField()`
   - Extract `WriteRows()` from `FodsCsvExporter.ExportSheetToCsvString()`
   - Extract `WriteToFile()` from file-write path in `FodsCsvExporter.ExportSheetToCsv()`
   - Refactor `FodsCsvExporter.cs` to call `CsvWriter.*` — remove duplicated logic
   - Add `FormatFactory.Csv` project reference to `FormatFactory.Fods`
   - Register in `registry/format-registry.yaml`
   - Write 8 `CsvWriter` unit tests + dogfood invocation proof test
3. Verify `fods_to_csv_dotnet` gap is resolved in routing packet
4. Optionally continue with Option 2 (HTML) in next sprint

---

## Notes on Independence of Gaps

CSV and HTML are independent export targets, even though both are exported from FODS:
- `FodsCsvExporter` does NOT call `FodsHtmlExporter` and vice versa
- Building `FormatFactory.Csv` has zero effect on the HTML gap
- Each writer library sprint is fully independent and can be sequenced or parallelized

TXT and Markdown are similarly independent:
- Both export from FODT but through separate exporter classes
- Building `FormatFactory.Txt` has zero effect on the Markdown gap

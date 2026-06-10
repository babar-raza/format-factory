# .NET Target Writer Library — Decision Package

## Summary

Four dogfood export gaps in the .NET product tracks are blocked because no standalone
`FormatFactory.*` target-format library exists for the corresponding output format.
The Export Target Support Policy (see below) requires a registered, standalone library
to be invoked by the source exporter — product-local exporter logic alone is insufficient.

The four blocked capabilities are:

| Dogfood Capability | Source Format | Target Format | Blocker |
|--------------------|--------------|--------------|---------|
| `fods_to_csv_dotnet` | FODS (.NET) | CSV | No `FormatFactory.Csv` library |
| `fods_to_html_dotnet` | FODS (.NET) | HTML | No `FormatFactory.Html` library |
| `fodt_to_txt_dotnet` | FODT (.NET) | Plain Text | No `FormatFactory.Txt` library |
| `fodt_to_markdown_dotnet` | FODT (.NET) | Markdown | No `FormatFactory.Markdown` library |

Each library must be built and registered independently. Unblocking CSV does NOT unblock HTML;
unblocking TXT does NOT unblock Markdown. Each gap requires its own library sprint.

---

## Decision Matrix

| Writer | Format | Namespace | Input Abstraction | Output Rules | Test Fixtures | Dogfood Consumers | Complexity (1-5) | Priority |
|--------|--------|-----------|------------------|--------------|---------------|-------------------|-----------------|----------|
| CSV | RFC 4180 | `FormatFactory.Csv` | `IEnumerable<IEnumerable<string?>>` rows | RFC 4180 escaping (commas/quotes/newlines → double-quoted; embedded quotes doubled); UTF-8 no BOM; LF line endings | round-trip; RFC 4180 quoting (comma/quote/newline); empty cells (null/empty); multi-row; `WriteToFile` | `FodsCsvExporter` (after refactor) | **2** | **1 — HIGHEST** (logic already extractable from `FodsCsvExporter.cs`) |
| HTML | HTML table | `FormatFactory.Html` | `IEnumerable<IEnumerable<string?>>` rows | `<table><tr><td>` structure; HTML-escape `<>&"` in cell content; UTF-8; LF line endings | render correctness; HTML escaping; empty cells; multi-row; `WriteToFile` | `FodsHtmlExporter` (after refactor) | **2** | **2** (simple HTML table structure; no CSS required at MVP) |
| TXT | Plain text | `FormatFactory.Txt` | `IEnumerable<string>` lines OR `FodtDocument` paragraphs | UTF-8 no BOM; LF line endings; one paragraph per line | paragraph round-trip; empty paragraphs; multi-paragraph; `WriteToFile` | `FodtTxtExporter` (after refactor) | **1** | **2** (trivial — just write lines; no structure encoding needed) |
| Markdown | Markdown | `FormatFactory.Markdown` | `IEnumerable` of heading/paragraph nodes (typed union or discriminated record) | `#`/`##`/`###` for heading levels 1–3+; blank line between blocks; paragraph text verbatim; UTF-8; LF line endings | heading levels (H1–H3); emphasis passthrough; blank-line separation; round-trip paragraph text | `FodtMarkdownExporter` (after refactor) | **3** | **3** (heading-level mapping and node-type dispatch add complexity; bold/italic in MVP scope TBD) |

### Complexity Key
- 1 = Trivial (write lines, no structure)
- 2 = Low (extract existing logic or generate simple structure)
- 3 = Medium (typed node dispatch, heading-level mapping)
- 4 = High (recursive AST, multiple output modes)
- 5 = Very High (full spec conformance with edge cases)

---

## Export Target Support Policy

A product may claim export support to a target format only if ALL of the following conditions are met:

1. **Standalone FF library exists:** A `FormatFactory.<TargetFormat>` .NET library (or equivalent Python package) is registered in the format registry and has its own test suite.
2. **Registered:** The library is listed in `registry/format-registry.yaml` with a valid gate status.
3. **Source exporter calls it:** The source-format exporter (e.g., `FodsCsvExporter`) invokes the target-format library API — it does NOT maintain its own copy of the target-format serialization logic.
4. **Tests prove invocation:** Tests verify that the exporter delegates to the target-format library (not just that the output is correct in isolation).
5. **Dogfood artifacts exist:** At least one dogfood test file exercises the full export path and produces a verified output artifact.

Product-local exporter logic (i.e., CSV escaping embedded directly in `FodsCsvExporter.cs`) does NOT satisfy this policy — it satisfies only the functional output requirement, not the architectural requirement.

---

## Human Decision Required

The following architectural decisions must be made before any writer library sprint begins:

### Decision 1: Sprint Scope
Choose one of:
- Option 1: CSV writer only (sprint `CREATE-DOTNET-CSV-WRITER-001`) — lowest risk, unblocks 1 gap
- Option 2: CSV + HTML in one sprint — unblocks 2 gaps, moderate scope
- Option 3: All four writers in one sprint — unblocks all 4 gaps, higher coordination cost
- Option 4: Defer all .NET dogfood writers — keep gaps permanently blocked until explicit future decision

### Decision 2: Package Strategy per Writer
For each library approved:
- NuGet package name (e.g., `format-factory-csv` vs `FormatFactory.Csv`)
- Gate 11 starting status (`g11_prototype` vs `g11e_prototype_complete`)
- Whether `FodsCsvExporter.cs` is refactored immediately or in a follow-on sprint

### Decision 3: Refactor Timing
Should the source exporter (`FodsCsvExporter`, `FodsHtmlExporter`, etc.) be refactored to
call the new library in the same sprint, or in a separate follow-on sprint?
(Refactoring in the same sprint is recommended for CSV given the logic is already isolated.)

### Decision 4: TXT Input Abstraction
`FormatFactory.Txt` needs clarity on its input abstraction:
- Option A: `IEnumerable<string>` lines (simplest — caller extracts paragraphs from FODT)
- Option B: A typed `TxtDocument` model (paragraph list) that `FodtTxtExporter` populates
Option A is recommended for MVP given complexity rating of 1/5.

### Decision 5: Markdown Node Model
`FormatFactory.Markdown` complexity is 3/5 due to heading-level dispatch.
The node model must be defined before implementation:
- Option A: Simple discriminated union `MarkdownBlock` (Heading(int level, string text) | Paragraph(string text))
- Option B: Interface-based `IMarkdownNode` hierarchy
Option A is recommended for MVP.

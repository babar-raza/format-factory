# POC Targets Proposed Delta

**Sprint:** FORMAT-FACTORY-DOTNET-TARGET-WRITER-MWP-DOGFOOD-UNBLOCKING-001
**Hardening:** FORMAT-FACTORY-DOTNET-TARGET-WRITER-READINESS-HARDENING-AND-POC-RECONCILIATION-001
**Generated:** 2026-06-05

> **Important:** This document is a proposal only. No direct `poc-targets.yaml` mutation occurred.
> Human review and Gate 11 approval are required before applying these changes.

## Summary

All four previously architecture-blocked dogfood gaps now meet the 5-condition Export Target Support Policy:

| Gap ID | Product | Target | Prior Status | Proposed Status | All 5 Met? |
|--------|---------|--------|--------------|-----------------|------------|
| `commercial-net-fods-dogfood-status-fods-to-csv-dotnet` | FODS .NET | CSV | GAP_DOGFOOD_EXTERNAL | IMPLEMENTED | YES |
| `commercial-net-fods-dogfood-status-fods-to-html-dotnet` | FODS .NET | HTML | GAP_DOGFOOD_EXTERNAL | IMPLEMENTED | YES |
| `commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet` | FODT .NET | TXT | GAP_DOGFOOD_EXTERNAL | IMPLEMENTED | YES |
| `commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet` | FODT .NET | Markdown | GAP_DOGFOOD_EXTERNAL | IMPLEMENTED | YES |

## Export Target Support Policy Evidence

For each gap, all five conditions are satisfied:

### Condition 1: Standalone FF Writer Library Exists
- `FormatFactory.Csv` — `src/net/csv/CsvWriter.cs` + `src/net/csv/FormatFactory.Csv.csproj`
- `FormatFactory.Html` — `src/net/html/HtmlWriter.cs` + `src/net/html/FormatFactory.Html.csproj`
- `FormatFactory.Txt` — `src/net/txt/TxtWriter.cs` + `src/net/txt/FormatFactory.Txt.csproj`
- `FormatFactory.Markdown` — `src/net/markdown/MarkdownWriter.cs` + `src/net/markdown/FormatFactory.Markdown.csproj`

### Condition 2: Writer Registered (or Registerable)
All four libraries are standalone packages, each registerable in the Format Factory registry.

### Condition 3: Exporter Delegates to Writer (Not Inline)
- `FodsCsvExporter.cs` → `CsvWriter.WriteRows()`
- `FodsHtmlExporter.cs` → `HtmlWriter.WriteTable()`
- `FodtTxtExporter.cs` → `TxtWriter.WriteLines()`
- `FodtMarkdownExporter.cs` → `MarkdownWriter.WriteParagraphs()`

### Condition 4: Tests Prove Invocation
- FODS .NET: 547/547 tests PASS (0 regressions)
- FODT .NET: 520/520 tests PASS (0 regressions)
- Writer libraries: 46 new tests (15+12+8+11) all PASS

### Condition 5: Dogfood Output Artifacts Exist
- `reports/dotnet-target-writer-mwp-dogfood-unblocking/sample-outputs/sample-fods-to-csv.csv`
- `reports/dotnet-target-writer-mwp-dogfood-unblocking/sample-outputs/sample-fods-to-html.html`
- `reports/dotnet-target-writer-mwp-dogfood-unblocking/sample-outputs/sample-fodt-to-txt.txt`
- `reports/dotnet-target-writer-mwp-dogfood-unblocking/sample-outputs/sample-fodt-to-markdown.md`

## Readiness Status (v5 Proof-Backed)

All four gaps show `status: READY` and `accepted_for_poc: true` per `detect_target_writer_readiness()`.

`BLOCKED_GAP_IDS = []` — dynamic unblocking confirmed, 0 gaps remaining blocked.

## Individual Delta Files

- `capability-delta-proposals/fods-csv-dotnet.yaml`
- `capability-delta-proposals/fods-html-dotnet.yaml`
- `capability-delta-proposals/fodt-txt-dotnet.yaml`
- `capability-delta-proposals/fodt-markdown-dotnet.yaml`

## Next Steps (Human Decision Required)

1. Review each delta file
2. Apply changes to `poc-targets.yaml` after Gate 11 decision
3. Re-run `select_poc_gaps.py` to confirm 0 architecture-blocked gaps remain

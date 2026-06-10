# Lane A: /update-capability-matrix — FODS
Sprint: FORMAT-FACTORY-DOGFOOD-MATRIX-RECONCILIATION-R120-001

## Skill: update-capability-matrix
## Matrix Entry: commercial_net_products.FODS

## Evidence Verified
- `src/net/fods/FodsCsvExporter.cs` line 149: `CsvWriter.WriteRowsToFile(csvRows, csvPath)` — delegates to FormatFactory.Csv
- `src/net/fods/FodsCsvExporter.cs` line 233: `return CsvWriter.WriteRows(csvRows)` — delegates to FormatFactory.Csv
- `src/net/fods/FodsHtmlExporter.cs` line 18: `using FormatFactory.Html;` — delegates to FormatFactory.Html
- `src/net/fods/FodsHtmlExporter.cs` line 141: `sb.Append(HtmlWriter.WriteTable(htmlRows))` — delegates to HtmlWriter
- Ledger entries: MWP-FODS-CSV-DOGFOOD-REFACTOR, MWP-FODS-HTML-DOGFOOD-REFACTOR
- Tests: 547/547 PASS (dotnet test tests/net/fods/FormatFactory.Fods.Tests.csproj -v quiet)

## Field Transitions Applied

| Field | Old Value | New Value | Evidence |
|-------|-----------|-----------|----------|
| dogfood_status.fods_to_csv_dotnet | GAP_DOGFOOD_EXTERNAL | IMPLEMENTED | FodsCsvExporter.cs line 149, ledger MWP-FODS-CSV-DOGFOOD-REFACTOR |
| dogfood_status.fods_to_html_dotnet | GAP_DOGFOOD_EXTERNAL | IMPLEMENTED | FodsHtmlExporter.cs line 141, ledger MWP-FODS-HTML-DOGFOOD-REFACTOR |
| dogfood_status.target_ff_library_for_csv_dotnet | "format-factory-csv (when .NET CSV library exists)" | "FormatFactory.Csv.CsvWriter" | src/net/csv/ exists, CsvWriter.cs |
| dogfood_status.target_ff_library_for_html_dotnet | (absent) | "FormatFactory.Html.HtmlWriter" | src/net/html/ exists, HtmlWriter.cs |
| dogfood_status.notes | outdated reference to "writes directly" | updated to reflect delegation | source inspection |
| dotnet_status.dotnet_tests | 507 | 547 | 547/547 PASS confirmed live |

## Authority Flags (unchanged)
- commercial_product_ready: false (unchanged)
- gate_11_g11g: NOT_STARTED (unchanged)
- gates_passed: "1-10" (unchanged)

## Validation
- dotnet test tests/net/fods/FormatFactory.Fods.Tests.csproj -v quiet → 547/547 PASS
- YAML parses after edit (verified by read)
- No changes to gate authority, release authority, or commercial readiness fields

## Verdict: PASS

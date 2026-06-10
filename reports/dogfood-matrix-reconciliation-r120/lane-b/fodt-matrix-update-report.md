# Lane B: /update-capability-matrix — FODT
Sprint: FORMAT-FACTORY-DOGFOOD-MATRIX-RECONCILIATION-R120-001

## Skill: update-capability-matrix
## Matrix Entry: commercial_net_products.FODT

## Evidence Verified
- `src/net/fodt/FodtTxtExporter.cs` line 18: `using FormatFactory.Txt;` — delegates to FormatFactory.Txt
- `src/net/fodt/FodtTxtExporter.cs` line 122: `TxtWriter.WriteLinesToFile(lines, txtPath)` — delegates to TxtWriter
- `src/net/fodt/FodtMarkdownExporter.cs` line 17: `using FormatFactory.Markdown;` — delegates to FormatFactory.Markdown
- `src/net/fodt/FodtMarkdownExporter.cs` line 130: `MarkdownWriter.WriteLinesToFile(lines, mdPath)` — delegates to MarkdownWriter
- Ledger entries: MWP-FODT-TXT-DOGFOOD-REFACTOR, MWP-FODT-MARKDOWN-DOGFOOD-REFACTOR
- Tests: 520/520 PASS (dotnet test tests/net/fodt/FormatFactory.Fodt.Tests.csproj -v quiet)

## Field Transitions Applied

| Field | Old Value | New Value | Evidence |
|-------|-----------|-----------|----------|
| dogfood_status.fodt_to_txt_dotnet | GAP_DOGFOOD_EXTERNAL | IMPLEMENTED | FodtTxtExporter.cs line 122, ledger MWP-FODT-TXT-DOGFOOD-REFACTOR |
| dogfood_status.fodt_to_markdown_dotnet | GAP_DOGFOOD_EXTERNAL | IMPLEMENTED | FodtMarkdownExporter.cs line 130, ledger MWP-FODT-MARKDOWN-DOGFOOD-REFACTOR |
| dogfood_status.target_ff_library_for_txt | "format-factory-fodt document_to_text (Python)" | (renamed to target_ff_library_for_txt_dotnet: FormatFactory.Txt.TxtWriter) | src/net/txt/ exists, TxtWriter.cs |
| dogfood_status.target_ff_library_for_markdown_dotnet | (absent) | "FormatFactory.Markdown.MarkdownWriter" | src/net/markdown/ exists, MarkdownWriter.cs |
| dogfood_status.notes | outdated reference to "writes directly" | updated to reflect delegation | source inspection |
| dotnet_status.dotnet_tests | 493 | 520 | 520/520 PASS confirmed live |

## Authority Flags (unchanged)
- commercial_product_ready: false (unchanged)
- gate_11_g11g: NOT_STARTED (unchanged)
- gates_passed: "1-10" (unchanged)

## Validation
- dotnet test tests/net/fodt/FormatFactory.Fodt.Tests.csproj -v quiet → 520/520 PASS
- YAML parses after edit (verified by read)
- No changes to gate authority, release authority, or commercial readiness fields

## Verdict: PASS

# Commit Candidate Manifest
Sprint: FORMAT-FACTORY-GATE11-PREP-AND-LEDGER-REPAIR-R123-001
Generated: 2026-06-05T14:10:00Z
Base commit: 3a86a05295cb4b82ed40a3408b0612a90f93643c

## Status
COMMIT_CANDIDATE_PREPARED — awaiting explicit user authorization to execute git commit + push.

## Product Source Changes (src/ — requires ledger coverage)

### New Libraries (4 new .NET writer libraries — MWP sprint)
| File | Change |
|------|--------|
| src/net/csv/CsvWriter.cs | NEW — standalone FormatFactory.Csv writer library |
| src/net/csv/FormatFactory.Csv.csproj | NEW — project file |
| src/net/html/HtmlWriter.cs | NEW — standalone FormatFactory.Html writer library |
| src/net/html/FormatFactory.Html.csproj | NEW — project file |
| src/net/markdown/MarkdownWriter.cs | NEW — standalone FormatFactory.Markdown writer library |
| src/net/markdown/FormatFactory.Markdown.csproj | NEW — project file |
| src/net/txt/TxtWriter.cs | NEW — standalone FormatFactory.Txt writer library |
| src/net/txt/FormatFactory.Txt.csproj | NEW — project file |

### Modified .NET (refactored exporters to use writer libraries)
| File | Change |
|------|--------|
| src/net/fods/FodsCsvExporter.cs | Refactored — delegates to CsvWriter |
| src/net/fods/FodsDocument.cs | Extended — new capabilities |
| src/net/fods/FodsHtmlExporter.cs | Refactored — delegates to HtmlWriter |
| src/net/fods/FormatFactory.Fods.csproj | Updated — adds FormatFactory.Csv/Html references |
| src/net/fodt/FodtDocument.cs | Extended — new capabilities |
| src/net/fodt/FodtMarkdownExporter.cs | Refactored — delegates to MarkdownWriter |
| src/net/fodt/FodtTxtExporter.cs | Refactored — delegates to TxtWriter |
| src/net/fodt/FormatFactory.Fodt.csproj | Updated — adds FormatFactory.Txt/Markdown references |
| src/net/netpbm/Model/NetpbmImage.cs | Extended — new capabilities |

### Modified Python (FOSS implementations)
| File | Change |
|------|--------|
| src/python/dif/dif_parser.py | Extended — write_dif, probe_dif, dif_to_csv, parse_dif_strict |
| src/python/sylk/sylk_parser.py | Extended — write_sylk implementation |

## Key Capability Deliverables
- FODS: 547 .NET tests PASS (CSV export, HTML export, row ops, sheet ops, formulas, styles, sorting, filtering)
- FODT: 520 .NET tests PASS (TXT export, Markdown export, paragraph ops, headings, metadata, outline)
- Netpbm: 465 .NET tests PASS (rotate, flip, merge, overlay, filters, draw, tile, canvas)
- FormatFactory.Csv writer: 15 tests | FormatFactory.Html: 12 tests | FormatFactory.Txt: 8 tests | FormatFactory.Markdown: 11 tests
- SYLK Python: 263+ tests PASS (write_sylk implemented)
- DIF Python: 12 tests PASS (write_dif, probe_dif, dif_to_csv)
- Netpbm Python: 577 tests PASS (installed-package proof confirmed)
- ZST Python: 267 tests PASS (online install proven)

## Ledger Coverage
- Product code change ledger: 129 entries, PASS (validated R123)
- Pre-existing defect fixed: R116-DIF-PROBE-CSV-PIPELINE (invalid classification → GOVERNED_PRODUCT_CHANGE, source_files added)

## Capability Matrix
- product-capability-matrix/poc-targets.yaml updated:
  - FODS: fods_to_csv_dotnet=IMPLEMENTED, fods_to_html_dotnet=IMPLEMENTED
  - FODT: fodt_to_txt_dotnet=IMPLEMENTED, fodt_to_markdown_dotnet=IMPLEMENTED
  - SYLK: blockers cleared (write_sylk confirmed implemented)
  - Netpbm FOSS: blockers cleared (577 tests confirmed)
  - ZST FOSS: blockers cleared (267 tests confirmed, online install documented)

## Gate 11 Status
- FODS: gate_11_status=NOT_STARTED — requires Babar Raza approval
- FODT: gate_11_status=NOT_STARTED — requires Babar Raza approval
- Netpbm: gate_11_status=NOT_STARTED — requires Babar Raza approval
- All 6 remaining gaps are EXTERNAL_GATE_ESCALATION

## Suggested Commit Message
```
feat(r93-r122): FODS/FODT/Netpbm .NET + SYLK/DIF/ZST Python — writer libraries, dogfood wiring, milestone

- Add 4 standalone .NET writer libraries: FormatFactory.Csv, Html, Txt, Markdown
- Refactor FODS/FODT exporters to delegate to writer libraries (dogfood compliance)
- Extend FODS: 547 tests (CSV/HTML export, row/sheet ops, formulas, styles, sorting, filtering)
- Extend FODT: 520 tests (TXT/Markdown export, headings, metadata, document outline)
- Extend Netpbm .NET: 465 tests (rotate, flip, merge, overlay, draw, tile, canvas, filters)
- Add write_dif + probe_dif to DIF Python FOSS; extend SYLK with write_sylk
- Product gap milestone: 0 autonomous gaps remain; all 3 commercial formats at Gate 11 boundary
```

## Authorization Required
- git commit: requires explicit user authorization (Babar Raza or project owner)
- git push: requires explicit user authorization
- Gate 11 approval: requires Babar Raza written approval
- NuGet/PyPI publication: requires Gate 11 approval first

# Mainstream Gap Priority Table — Hardening IV

## Top Product Gaps for Mainstream Next Sprint

| Priority | Format | Family | Capability Path | Reason | Missing Proof | Expected Outputs |
|---|---|---|---|---|---|---|
| 1 | FODS | OpenDocument Spreadsheet | `dogfood_status.fods_to_csv_dotnet` | Skills packet targets this; Acceleration has implementation design | Source diff + governed transcript + raw log | `src/net/fods/FodsDocument.cs`, test file, raw test log, capability matrix delta |
| 2 | FODT | OpenDocument Text | `dogfood_status.fodt_to_markdown_dotnet` | Acceleration packet present; .NET 201 tests | Source diff + raw log | `src/net/fodt/FodtDocument.cs`, test file, raw test log |
| 3 | Netpbm | PBM/PGM/PPM | `dotnet_status.netpbm_flip_diagonal` or new API | Needed for breadth=3 CLEAN_PASS; Acceleration packet present | Source diff + raw log | `src/net/netpbm/Model/NetpbmImage.cs`, test file, raw test log |
| 4 | ZST | Zstandard | `python_status.zst_roundtrip` | FOSS Python track; ZST package proven | Test file + raw log | Python test, dogfood script |
| 5 | SYLK | Symbolic Link | `python_status.write_sylk` | Acceleration packet present | Test file + raw log | Python test, SYLK write roundtrip |

## Validation Hints

- **FODS**: `FodsDocument.ExportToCsv()` or `WorkbookToMarkdown()` — check skills handoff for exact method
- **FODT**: `FodtDocument.ExportToMarkdown()` — Acceleration packet specifies this capability
- **Netpbm**: `NetpbmImage.FlipDiagonal()` or similar — Acceleration packet specifies this
- **ZST**: `zst_roundtrip()` — Python track; simple compress/decompress
- **SYLK**: `write_sylk()` — Python track; Acceleration packet present

## Stop Conditions

- Do NOT select SVG as a replacement for Netpbm
- Do NOT claim `families_touched >= 3` unless FODS+FODT+Netpbm all have source diffs
- Do NOT claim `governed_transcripts >= 3` unless Skills produced transcripts for 3 families
- Do NOT declare CLEAN_PASS without raw_logs for each selected family

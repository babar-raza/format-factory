# Plan Mode Limitations and Notes

## What Was Done in Plan Mode

- **Read-only exploration** of `src/net/`, `src/python/`, `examples/`, `tests/`, `packaging/`
- **Source file inspection** of key files:
  - `src/net/fods/FodsDocument.cs` — full DOM-backed spreadsheet model (732 LOC)
  - `src/net/fods/FodsDocumentAccessor.cs` — query methods partial class
  - `src/net/netpbm/NetpbmDocument.cs` — image document wrapper
  - `src/net/netpbm/Model/NetpbmImage.cs` — pixel model (partial class)
  - `src/net/netpbm/Model/NetpbmImageTransforms.cs` — geometric transforms
  - `src/net/ndjson/NdjsonDocument.cs` — JSON lines document
  - `src/net/csv/CsvDocument.cs` — simple CSV model
  - `src/python/fods/__init__.py` — Python FODS package entry point
  - `src/python/fods/models.py` — FodsDocument/FodsSheet/FodsCell class wrappers
  - `src/python/pbm/pbm_parser.py` — PBM parser with error hierarchy
  - `src/net/fods/FormatFactory.Fods.csproj` — .NET project metadata
  - `src/python/fods/pyproject.toml` — Python package metadata
  - `tests/net/fods/FodsDocumentEditTests.cs` — test quality sample
  - `examples/python/fods/edit_save_fods.py` — example quality sample
- **Directory structure enumeration** of all src/net and src/python files
- **Git status capture** and log inspection

## What Was NOT Done in Plan Mode

- No deep read of every source file (would require execution sprint)
- No inspection of all 2962+ test files
- No inspection of all Python analytics files (ndjson_analytics.py 923 LOC, etc.)
- No inspection of FodtDocument.cs, FodtParser.cs, FodtWriter.cs in depth
- No inspection of NetpbmParser.cs, NetpbmWriter.cs, NetpbmExporter.cs in depth
- No inspection of Python ods/, odt/, sylk/, toml/, xcf/ source files
- No inspection of ZstDocument.cs to confirm absence of write capability
- No inspection of FodtDocument Spec/Table/* wiring
- No inspection of NetpbmExporter.cs export targets
- No inspection of CsvReader.cs for quoted-field handling
- No running of any tests

## Outstanding Questions (to answer in execution sprint)

The following NEEDS_CONFIRMATION flags from the problem matrix require source inspection:

| ID | Question | Where to Look |
|----|----------|---------------|
| PQ-012 | Is FodtDocument table editing wired? | src/net/fodt/FodtDocument.cs + FodtDocumentAccessor.cs |
| PQ-013 | What does NetpbmExporter export to? | src/net/netpbm/NetpbmExporter.cs |
| PQ-018 | FodsDocument.GetColumnHeaders() static overload — is it truly inconsistent? | src/net/fods/FodsDocument.cs L369-414 (already read — YES confirmed) |
| PQ-007 | ZST .NET has no writer — confirm from ZstDocument.cs | src/net/zst/ZstDocument.cs |
| Q-009 | FODP Python no writer — confirm from fodp_codec.py | src/python/fodp/fodp_codec.py |

## Files That Must Be Read During Execution

Priority files for deeper inspection:
1. `src/net/fodt/FodtDocument.cs` — FODT model and API
2. `src/net/netpbm/NetpbmParser.cs` — parser depth (P1/P2/P3/P4/P5/P6)
3. `src/net/netpbm/NetpbmExporter.cs` — export targets
4. `src/net/zst/ZstDocument.cs` — confirm no write
5. `src/net/zst/ZstParser.cs` — parser capability
6. `src/python/fodt/exporters.py` — confirm fodt_to_txt/markdown/html
7. `src/python/ods/ods_parser.py` — ODS ZIP handling
8. `src/python/toml/toml_codec.py` — TOML API
9. `src/python/sylk/sylk_parser.py` — SYLK flat model
10. `src/python/qoi/qoi_encoder.py` — QOI encode quality
11. `src/python/xcf/xcf_parser.py` — XCF layer name quality
12. All `pyproject.toml` files (20 packages) — packaging completeness
13. `tests/net/fods/FodsG11fMalformedXmlGuardTests.cs` — malformed input test quality
14. `tests/net/netpbm/NetpbmGuardTests.cs` — image guard tests
15. `examples/python/fods/edit_save_export_fods_installed.py` — installed path example

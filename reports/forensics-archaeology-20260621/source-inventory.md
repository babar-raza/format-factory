# Source Inventory

**Sprint:** forensics-archaeology-20260621

---

## Python Packages (`src/python/`)

| Package | LOC | Files | Key Source Files | Notes |
|---------|-----|-------|-----------------|-------|
| fods | 3,914 | 35 | parser.py, neutral_model.py, models.py, writer.py, Compat/ (3), spec/ (12 stubs) | Most advanced; has spec stubs + Compat/ |
| fodt | 4,525 | 21 | parser.py, neutral_model.py, models.py, list_traversal.py, spec/ (8 stubs) | Spec stubs, no Compat/ yet |
| xcf | 7,022 | 3 | xcf_parser.py, xcf_analytics.py | Monolith — GOV_BLOCK risk |
| zst | 7,130 | 3 | zst_codec.py, zst_analytics.py | Monolith — GOV_BLOCK risk |
| fodg | 6,421 | 3 | fodg_codec.py, fodg_analytics.py | Monolith |
| dif | 2,122 | 4 | dif_parser.py, dif_analytics.py, dif_stats.py | Gen 1 — has DifDocument dataclass |
| ods | 2,487 | 5 | ods_parser.py, ods_writer.py, ods_stats.py, ods_csv_exporter.py | Gen 1 — has OdsDocument |
| ndjson | 1,972 | 2 | ndjson_codec.py | Gen 1 |
| csv | 1,843 | 5 | csv_parser.py, csv_writer.py, csv_stats.py, csv_analytics.py | Gen 1 |
| abw | 1,708 | 3 | abw_codec.py, abw_analytics.py | Gen 1 |
| sylk | 1,808 | 2 | sylk_parser.py | Gen 1 — has SylkDocument |
| tsv | 1,814 | 2 | tsv_parser.py | Gen 1 |
| ppm | 1,675 | 4 | ppm_parser.py, ppm_stats.py, ppm_to_pgm.py | Gen 1 — has PpmImage |
| gnumeric | 2,076 | 2 | gnumeric_codec.py | Gen 1 |
| qoi | 1,396 | 3 | qoi_parser.py, qoi_encoder.py | Gen 1 — has QoiImage |
| pbm | 1,500 | 4 | pbm_parser.py, pbm_to_pgm.py, pbm_to_ppm.py | Gen 1 — has PbmImage |
| pgm | 1,465 | 3 | pgm_parser.py, pgm_to_ppm.py | Gen 1 — has PgmImage |
| toml | 1,306 | 2 | toml_codec.py | Gen 1 |
| fodp | 969 | 2 | fodp_codec.py | Gen 1 |
| odt | 981 | 2 | odt_parser.py | Gen 1 — has OdtDocument |

**Total Python:** ~56,437 LOC across 20 packages, 117 non-build files

---

## .NET Packages (`src/net/`)

| Package | Key Source Files | Pattern | Notes |
|---------|-----------------|---------|-------|
| fods | FodsDocument.cs (1293 LOC), FodsParser.cs (286 LOC), FodsWriter.cs, FodsCsvExporter.cs, FodsHtmlExporter.cs, FodsJsonExporter.cs, FodsOdsExporter.cs, FodsPdfExporter.cs, FodsPngExporter.cs, FodsDocumentExporter.cs, Model/FodsSheet.cs, Model/FodsRow.cs, Model/FodsCell.cs, Spec/Office/, Spec/Table/ | DOM-backed + Spec/ | Most mature .NET — load/edit/save/export |
| fodt | FodtDocument.cs, FodtParser.cs, FodtWriter.cs, FodtHtmlExporter.cs, FodtTxtExporter.cs, FodtMarkdownExporter.cs, FodtPdfExporter.cs, FodtPngExporter.cs | DOM-backed | Nearly as mature as FODS .NET |
| csv | CsvDocument.cs, CsvReader.cs, CsvWriter.cs | Document + CRUD | Simple table format |
| ndjson | NdjsonDocument.cs, NdjsonReader.cs, NdjsonWriter.cs, NdjsonCsvExporter.cs | Document + CRUD | Simple streaming format |
| tsv | TsvDocument.cs, TsvReader.cs, TsvWriter.cs, TsvCsvExporter.cs | Document + CRUD | Simple table format |
| zst | ZstDocument.cs, ZstParser.cs | Parse only | Binary compression |
| txt | TxtWriter.cs | Writer only | Export target only |
| html | HtmlWriter.cs | Writer only | Export target only |
| markdown | MarkdownWriter.cs | Writer only | Export target only |
| netpbm | (assumed from registry) | Image | Limited |

**No .NET packages for:** abw, dif, gnumeric, ods, odt, pbm, pgm, ppm, qoi, toml, xcf, fodg, fodp, sylk

---

## Test Distribution

| Area | Approximate Count |
|------|-----------------|
| Python format tests | 46,000+ total (confirmed from test runner) |
| Python FODS tests | ~211 |
| Python FODT tests | ~248 |
| .NET FODS tests | ~611 |
| .NET FODT tests | ~567 |
| Supervisor/governance tests | 1,490 (last sprint) |
| SAL/spec-authority tests | 13+ test files |

---

## Fixtures and Specs

```
tests/fixtures/          — format sample files for parser tests
tests/dotnet/            — .NET test integration
.local/spec-cache/       — SAL fact files per format
format_understanding/    — manual format knowledge base
```

---

## Packaging State

```
Packaging status per registry/format-completion-matrix.yaml:
  FODS: local_build_ready (Python FOSS + .NET)
  FODT: local_build_ready (Python FOSS + .NET)
  Others: various — most have pyproject.toml but incomplete packaging
```

Python egg-info directories present at TWO levels (polluting src/):
- `src/python/format_factory_*.egg-info` (top-level — 19 entries)
- `src/python/{pkg}/format_factory_*.egg-info` (per-package — 2 entries)
- `src/format_factory_dev.egg-info` (repo root level)

Build artifact directories:
- `src/python/{pkg}/build/` present for: abw, dif, fods, fodt, gnumeric, ods, pbm, pgm, ppm, sylk, zst
- `src/python/fods/build/lib/fods/build/lib/fods/build/lib/...` (recursive nesting — 3+ levels)
- `src/net/{pkg}/bin/` and `src/net/{pkg}/obj/` for all .NET packages

**Source hygiene assessment:** POLLUTED by build artifacts at multiple levels. See `source-hygiene-audit.md`.

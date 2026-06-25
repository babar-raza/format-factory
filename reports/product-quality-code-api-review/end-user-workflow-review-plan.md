# End-User Workflow Review Plan

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## What is End-User Workflow Quality?

End-user workflow quality measures whether a developer who has never seen Format Factory's source code can:
1. Find the package on NuGet/PyPI
2. Install the package
3. Import/use the package
4. Find the primary entry point
5. Load a file
6. Edit the content
7. Save the result
8. Export to another format if needed
9. Understand errors when something goes wrong
10. Find examples or documentation

A product with excellent source code but no examples, no README, and no CLI entry point has POOR end-user workflow quality even if the code itself is solid.

---

## End-User Workflow Levels (EW-0 through EW-5)

| Level | Meaning |
|-------|---------|
| **EW-0** | No usable workflow — impossible to use without reading source |
| **EW-1** | Load + inspect only; no edit or save |
| **EW-2** | Load + save, but discovery requires source reading |
| **EW-3** | Load + edit + save discoverable from imports, no examples |
| **EW-4** | Load + edit + save with examples; minor friction |
| **EW-5** | Full workflow with README, examples, CLI, error messages guide correction |

---

## Examples Review

### Python Examples Status

| Product | Examples | Notes |
|---------|---------|-------|
| FODS Python | 5 files | edit_save_fods.py, edit_save_export_fods.py, read_and_inspect.py, edit_and_export.py, edit_save_export_fods_installed.py |
| FODT Python | 5 files | Similar; includes installed-path example |
| ODS Python | 1 file | clean_consumer_roundtrip.py |
| ODT Python | 1 file | dogfood_odt_roundtrip.py |
| ABW Python | 4 files | extract_text.py, create_document_example.py, html_metadata_export_example.py, consumer_roundtrip.py |
| CSV Python | 2 files | read_and_inspect.py, consumer_roundtrip.py |
| TSV Python | 2 files | read_and_transform.py, consumer_roundtrip.py |
| SYLK Python | 4 files | read_and_inspect.py, write_export_sylk.py, sylk_csv_pipeline.py, consumer_roundtrip.py |
| GNUMERIC Python | 5 files | extract_cells.py, export_csv_example.py, json_export_example.py, read_and_inspect.py, consumer_roundtrip.py |
| NDJSON Python | 2 files | read_and_query.py, consumer_roundtrip.py |
| TOML Python | 3 files | read_and_inspect.py, edit_and_export.py, consumer_roundtrip.py |
| ZST Python | 4 files | compress_decompress_file.py, validate_compressed_file.py, frame_inspection.py, consumer_roundtrip.py |
| PBM Python | 2 files | pbm_to_pgm_example.py, pbm_analytics_example.py |
| PGM Python | 2 files | pgm_analytics_example.py, pgm_consumer_roundtrip.py |
| PPM Python | 3 files | pgm_to_ppm_example.py, ppm_analytics_example.py, ppm_consumer_roundtrip.py |
| DIF Python | 1 file | consumer_roundtrip.py |
| FODG Python | 2 files | inspect_drawing_shapes.py, consumer_roundtrip.py |
| FODP Python | 2 files | extract_presentation_text.py, consumer_roundtrip.py |
| QOI Python | 0 files | NO EXAMPLES |
| XCF Python | 0 files | NO EXAMPLES |

**Critical finding:** QOI and XCF have ZERO examples. All other formats have at least 1.

### Example Import Path Issue (PQ-003)

All examples (except `edit_save_export_fods_installed.py` and `edit_save_fodt_installed.py`) use:
```python
import sys
sys.path.insert(0, str(REPO_ROOT))
from src.python.fods import parse_fods
```

This is a DEV-PATH import that only works when running from the repository root.
An installed user would do:
```python
from fods import parse_fods
```

**Impact:** Examples cannot be directly copied by a user who installed the package via pip.

### .NET Examples Status

**No examples exist for any .NET product.** The `examples/` directory contains only Python examples.
- No `examples/dotnet/fods/` equivalent
- No `examples/dotnet/fodt/`
- No `examples/dotnet/netpbm/`

This is a significant gap for .NET commercial products.

---

## Documentation Review

### README Status

No `README.md` exists for any Python or .NET product:
- `src/net/fods/README.md` — MISSING (csproj references it for NuGet)
- `src/python/fods/README.md` — MISSING
- `src/python/fodt/README.md` — MISSING
- (all 20 Python packages) — ALL MISSING
- (all 9 .NET packages) — ALL MISSING

**Exception:** The following API documentation files exist (new, untracked):
- `docs/api/pbm.md` — API reference for PBM
- `docs/api/pgm.md` — API reference for PGM
- `docs/api/ppm.md` — API reference for PPM

These are the ONLY three products with any API documentation beyond source code comments.

### Docstring Status

**Python:** No systematic docstring audit performed. Source inspection suggests:
- `pbm_parser.py` — docstrings present on key functions (estimated)
- Most other formats: sparse docstrings

**C#:** No systematic XML doc comment audit performed. Source inspection suggests:
- `FodsDocument.cs` — XML doc comments on key public members
- `ZstDocument.cs` — XML doc comments on all properties (confirmed)

---

## Packaging Review

### Python pyproject.toml Status (All 20 Packages)

| Field | Status |
|-------|--------|
| `name` | Present (all packages) |
| `version` | Present (all packages — 0.1.0) |
| `description` | Present (most packages) |
| `license` | Present (all packages) |
| `requires-python` | Present (all packages) |
| `[project.authors]` | MISSING (all 20 packages) |
| `[project.urls]` | MISSING (all 20 packages) |
| `[project.keywords]` | MISSING (all 20 packages) |
| `[project.classifiers]` | MISSING (all 20 packages) |
| `readme = "README.md"` | MISSING (all 20 packages — also README.md doesn't exist) |
| `[project.scripts]` | MISSING (all 20 packages) |

This means all 20 Python packages would appear on PyPI with minimal metadata — no author, no URL, no keywords, no classifiers, no readme display.

### .NET csproj Status

Confirmed issues for FODS:
- `PackageReadmeFile = README.md` — referenced but `README.md` doesn't exist at package root
- `PackageDescription` says "Gate 11 approved 2026-06-05" — contradicts source header
- No `PackageUrl`, `PackageAuthor`, `RepositoryUrl` in some products

---

## End-User Workflow Scoring

| Product | Install | Import | Load | Edit | Save | Export | Errors | Examples | Docs | EW Level |
|---------|---------|--------|------|------|------|--------|--------|---------|------|----------|
| FODS .NET | 2 | 4 | 4 | 4 | 4 | 4 | 4 | 0 | 1 | EW-3 |
| FODT .NET | 2 | 4 | 4 | 4 | 4 | 4 | 4 | 0 | 1 | EW-3 |
| NetPBM .NET | 2 | 4 | 5 | 4 | 4 | 3 | 4 | 0 | 1 | EW-3 |
| ZST .NET | 2 | 3 | 2 | 0 | 0 | 0 | 3 | 0 | 1 | EW-1 |
| FODS Python | 4 | 3 | 4 | 4 | 4 | 4 | 3 | 4 | 1 | EW-4 |
| FODT Python | 4 | 4 | 4 | 4 | 4 | 4 | 2 | 4 | 1 | EW-4 |
| ODS Python | 3 | 3 | 4 | 3 | 3 | 3 | 2 | 1 | 1 | EW-3 |
| PBM Python | 3 | 3 | 4 | 2 | 3 | 3 | 5 | 2 | 4 | EW-4 |
| ZST Python | 3 | 3 | 3 | 0 | 3 | 0 | 2 | 4 | 1 | EW-3 |
| QOI Python | 2 | 3 | 3 | 1 | 3 | 0 | 2 | 0 | 1 | EW-2 |
| FODP Python | 3 | 3 | 3 | 0 | 0 | 0 | 1 | 2 | 1 | EW-1 |

---

## Priority Recommendations

1. **CRITICAL:** Add README.md to all 30 products (Python: 20, .NET: 10)
2. **HIGH:** Add at least one example per product (.NET: 10 products have NO examples)
3. **HIGH:** Enrich pyproject.toml for all 20 Python packages
4. **MEDIUM:** Add installed-path imports to existing Python examples
5. **MEDIUM:** Add CLI entry points to key Python packages (fods, fodt, pbm)
6. **LOW:** Add type stubs (.pyi) for improved IDE experience

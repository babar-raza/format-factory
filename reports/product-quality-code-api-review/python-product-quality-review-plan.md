# Python FOSS Product Quality Review Plan

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Scope

Review all 20 Python FOSS products:
```
src/python/fods/    src/python/fodt/   src/python/ods/    src/python/odt/
src/python/abw/     src/python/csv/    src/python/tsv/    src/python/dif/
src/python/gnumeric/ src/python/ndjson/ src/python/toml/  src/python/sylk/
src/python/pbm/     src/python/pgm/    src/python/ppm/    src/python/qoi/
src/python/xcf/     src/python/zst/    src/python/fodg/   src/python/fodp/
```

---

## Review Methodology Per Product

### Step 1: `__init__.py` Audit
- Is `__all__` curated or dynamically generated?
- Are imports explicit (`from .parser import parse_fods`) or wildcard (`from .parser import *`)?
- How many names are exported? Can a developer navigate them?
- Are module-type objects properly filtered from the API surface?

### Step 2: API Surface Audit
- What is the primary entry point? (e.g., `parse_fods()`, `FodsDocument()`, `load()`)
- Are there competing entry points (dual API)?
- What is the naming convention? `parse_*` vs `load_*` vs `read_*`?
- Are return types annotated?

### Step 3: pyproject.toml Completeness
Check for presence of:
- `[project.authors]` — author name/email
- `[project.urls]` — Homepage, Repository, Documentation
- `[project.keywords]` — searchable keywords
- `[project.classifiers]` — PyPI classifiers (Programming Language, License, etc.)
- `readme = "README.md"` — package readme reference
- `[project.scripts]` — CLI entry points

### Step 4: Package Functionality Check
- Does `load_*()` or `parse_*()` function exist and return typed or dict result?
- Does `write_*()` or `save_*()` function exist?
- Are there examples showing the workflow?
- Does the installed package workflow work (`from fods import parse_fods`)?

### Step 5: Error Handling Audit
- Is there a custom exception type?
- What happens on malformed input?
- Are error messages meaningful?

### Step 6: Installed Workflow Check
- Was a wheel built and installed?
- Can `from {package} import {function}` be called without sys.path manipulation?
- Does the consumer roundtrip example work via installed path?

---

## Python Product Tiers

### Tier 1 — Strongest Python Products (FOSS-RC)
- **FODS Python** — Highest maturity; dual API issue; 5 examples; installed proof exists
- **FODT Python** — Strong; full exporters; healed from GOV_BLOCK; 5 examples

### Tier 2 — Working Products (PY-3)
- **ODS** — ZIP-based; write+export; 1 example
- **ODT** — ZIP-based; write; 1 example; odt_writer.py added
- **ABW** — parse/write/append_paragraph; 4 examples
- **GNUMERIC** — parse/write; dict model; 5 examples
- **NDJSON** — parse/write; NdjsonDocument; 2 examples
- **TOML** — parse/write; TomlDocument + TomlError; 3 examples
- **SYLK** — parse/write/csv-export; 4 examples (FILE-BASED edit — unusual)
- **DIF** — parse/write; 1 example
- **PBM** — parse (P1/P4); strong exception hierarchy; API docs; 2 examples
- **PGM** — parse (P2/P5); API docs; 2 examples
- **PPM** — parse (P3/P6); API docs; 3 examples
- **XCF** — parse; xcf_layer_name_list (real layer names); no write
- **ZST** — compress/decompress; ZstDocument; 4 examples
- **CSV** — parse/write; CsvDocument; 2 examples (stdlib conflict)
- **TSV** — parse/write; TsvDocument; 2 examples

### Tier 3 — Limited Products (PY-2 or below)
- **QOI** — parse/encode; no examples; minimal model
- **FODG** — dict-only model; load/write; 2 examples
- **FODP** — READ-ONLY; dict model; no write; 2 examples

---

## Critical Python-Specific Review Questions

1. **Dual API (FODS):** Which API should users call — `parse_fods()` dict functions or `FodsDocument` class? Is there guidance?
2. **Wildcard imports:** How many names appear in `from fods import *`? Can a user navigate them?
3. **pyproject.toml completeness:** Does any package have `authors`, `urls`, `keywords`, `classifiers`, AND `readme`?
4. **Type hints:** Are any public functions typed? PEP 484 style?
5. **Type stubs:** Do any packages have `.pyi` files?
6. **FODP read-only:** Is write_fodp documented as missing? Does the user get a meaningful error when they try?
7. **SYLK file-based edit:** Is `set_cell_value(src, dest, row, col, value)` documented as file-based?
8. **TSV write_tsv:** Is it documented that `write_tsv(rows, dest, headers=)` takes `list[list[str]]` not `list[dict]`?
9. **_shared/ base classes:** Are they actually used? If not, should they be removed?
10. **Consumer roundtrip examples:** Do all consumer_roundtrip.py examples use installed path (not dev path)?

---

## FOSS Readiness Scoring Formula

```
foss_readiness_score = (
    module_quality * 0.08
  + naming_quality * 0.08
  + discoverability * 0.08
  + workflow_quality * 0.10
  + load_api * 0.10
  + edit_api * 0.08
  + save_api * 0.08
  + export_api * 0.05
  + validation_api * 0.05
  + error_api * 0.08
  + type_hints * 0.03
  + type_stubs * 0.02
  + packaging * 0.05
  + examples * 0.05
  + documentation * 0.05
  + installed_workflow * 0.05
  + roundtrip_proof * 0.07
) / 1.0
```

**FOSS Readiness Bands (numeric):**
- 0.0–1.4: PY-0 (not usable)
- 1.5–2.4: PY-1 (toy/demo)
- 2.5–3.0: PY-2 (useful scoped FOSS)
- 3.1–3.8: PY-3 (release candidate)
- 3.9–4.2: PY-4 (strong FOSS product)
- 4.3–5.0: PY-5 (release-quality)

---

## Files Produced

- `python-product-quality-review-plan.md` (this file)
- `python-product-quality-matrix.json` — scored matrix for all 20 Python products
- `python-foss-readiness-rubric.md` — scoring rubric

# Python FOSS Readiness Rubric

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## FOSS Readiness Scale (PY-0 through PY-5)

| Level | Band | Meaning |
|-------|------|---------|
| PY-0 | Not usable | importable only; no functional API |
| PY-1 | Toy/demo | parse/load API exists; minimal tests |
| PY-2 | Useful scoped FOSS | structured data model + basic examples |
| PY-3 | Release candidate | write/save API + tests + installed workflow |
| PY-4 | Strong FOSS product | installed workflow + roundtrip proof + examples |
| PY-5 | Release-quality | full docs, examples, errors, roundtrip, packaging, type stubs |

---

## Gate P1–P11 FOSS Readiness Criteria

Per `plans/strategic/spec-to-feature-radical-correction-plan.md`:

| Criterion | Category | Description |
|-----------|----------|-------------|
| P1 | API | Curated `__all__` list (not dynamic wildcard) |
| P2 | API | Type hints on all public functions |
| P3 | API | Type stubs (`.pyi`) present |
| P4 | Architecture | `__init__.py` imports are explicit, not star |
| P5 | Features | Parse/load API functional |
| P6 | Features | Write/save API functional (or documented as intentionally absent) |
| P7 | Features | Roundtrip (load → edit → save → reload) verified |
| P8 | Packaging | `pyproject.toml` has authors, urls, keywords, classifiers, readme |
| P9 | Packaging | Installed workflow proof (wheel installed, imports work) |
| P10 | Docs | README.md at package root with code example |
| P11 | Docs | Docstrings on all public functions |

---

## Scoring Dimensions

1. **Module Quality** — Clean package name, no stdlib conflicts, curated `__all__`
2. **Naming Quality** — snake_case functions, consistent prefix conventions
3. **Discoverability** — Can developer find main entry point from `help(fods)` or tab completion?
4. **Workflow Quality** — Natural load → edit → save pattern
5. **Load API** — `parse_*`, `load_*`, `from_file()` with clear semantics
6. **Edit API** — Model-based mutations (not file-based)
7. **Save API** — `write_*()` produces valid output
8. **Export API** — Cross-format conversion available
9. **Validation API** — Strict mode, malformed input handling
10. **Error API** — Custom exception types with meaningful hierarchy
11. **Type Hints** — PEP 484 type hints on public functions
12. **Type Stubs** — `.pyi` files for IDE support
13. **Packaging** — pyproject.toml metadata completeness
14. **Examples** — runnable examples present
15. **Documentation** — docstrings on public functions + README
16. **Installed Workflow** — wheel installable, installed imports work
17. **Roundtrip Proof** — load → edit → save → reload verified

---

## Product FOSS Readiness Estimates

### FODS Python — Estimated: PY-4

**Strong:** Full parse/write/export; examples present (5 files including installed-path example)
**Gaps:**
- P1 FAIL: Dynamic `__all__` with wildcard imports — not curated
- P3 FAIL: No type stubs
- P8 FAIL: pyproject.toml missing authors, urls, keywords, classifiers, readme
- P10 FAIL: No README.md
- PQ-002: Dual API problem — function-based AND class-based

---

### FODT Python — Estimated: PY-4

**Strong:** Full parse/write/export (txt, markdown, html); examples present; analytics functions
**Gaps:**
- P1 FAIL: Wildcard imports
- P3 FAIL: No type stubs
- P8 FAIL: pyproject.toml incomplete
- P10 FAIL: No README.md

---

### ODS Python — Estimated: PY-3

**Strong:** ZIP-based ODS; parse/write/export; consumer roundtrip example
**Gaps:** pyproject.toml incomplete; no README; no type stubs

---

### ODT Python — Estimated: PY-3

**Strong:** ZIP-based ODT; parse/write; odt_from_text(), write_odt()
**Gaps:** No export (HTML/Markdown/TXT); pyproject.toml incomplete; no README

---

### ABW Python — Estimated: PY-3

**Strong:** load/write/append_paragraph; 4 examples; AbwDocument class
**Gaps:** pyproject.toml incomplete; no README; no export

---

### CSV Python — Estimated: PY-3

**Strong:** parse_csv_strict; write_csv_to_file; CsvDocument; 2 examples
**Gaps:** Package name conflicts with stdlib `csv`; pyproject incomplete; no README

---

### TSV Python — Estimated: PY-3

**Strong:** parse_tsv_strict; write_tsv; TsvDocument; 2 examples
**Gaps:** write_tsv API unusual (list-of-lists not list-of-dicts); pyproject incomplete

---

### DIF Python — Estimated: PY-3

**Strong:** load_dif; write_dif; DifDocument; 1 example
**Gaps:** Flat model unusual; export_to_html; pyproject incomplete

---

### GNUMERIC Python — Estimated: PY-3

**Strong:** load/write; GnumericDocument; 5 examples; export_to_csv/json
**Gaps:** Dict cell_grid model not typed; pyproject incomplete

---

### NDJSON Python — Estimated: PY-3

**Strong:** load_ndjson; write_ndjson; NdjsonDocument; 2 examples; analytics
**Gaps:** analytics masquerade (923 LOC analytics file); pyproject incomplete

---

### TOML Python — Estimated: PY-3

**Strong:** load_toml; write_toml; TomlDocument; 3 examples; TomlError
**Gaps:** config_document.py is analytics masquerade; pyproject incomplete

---

### SYLK Python — Estimated: PY-3

**Strong:** load_sylk; sylk_to_csv; set_cell_value; 4 examples
**Gaps:** UNUSUAL: set_cell_value is FILE-BASED (takes src+dest paths) not model-based; pyproject incomplete

---

### PBM Python — Estimated: PY-3

**Strong:** parse_pbm (P1+P4); PbmImage; strong exception hierarchy; 2 examples; API docs (docs/api/pbm.md)
**Gaps:** No pixel edit; pyproject incomplete (but docs/api/pbm.md is unique — only format with API docs)

---

### PGM Python — Estimated: PY-3

**Strong:** parse_pgm (P2+P5); 2 examples; API docs (docs/api/pgm.md)
**Gaps:** No transforms; pyproject incomplete

---

### PPM Python — Estimated: PY-3

**Strong:** parse_ppm (P3+P6); 3 examples; API docs (docs/api/ppm.md)
**Gaps:** No transforms; pyproject incomplete

---

### QOI Python — Estimated: PY-2

**Strong:** parse_qoi; encode_qoi
**Gaps:** No examples; no docs; pyproject incomplete; minimal model

---

### XCF Python — Estimated: PY-3

**Strong:** XcfImage; xcf_layer_name_list (now returns real layer names)
**Gaps:** No write/export; no examples; pyproject incomplete

---

### ZST Python — Estimated: PY-3

**Strong:** compress_string/decompress_to_string; ZstDocument; 4 examples
**Gaps:** No stream API; pyproject incomplete

---

### FODG Python — Estimated: PY-2

**Strong:** load/write_fodg; export_to_txt/json; 2 examples
**Gaps:** Dict-only model; pyproject incomplete

---

### FODP Python — Estimated: PY-1

**Strong:** load; get_page_count; 2 examples
**Gaps:** READ-ONLY (no write_fodp); not documented as read-only; pyproject incomplete

---

## Common Python FOSS Gaps (Across All 20 Packages)

| Gap | Impact | PQ ID |
|----|--------|-------|
| Wildcard `__init__.py` imports | P1/P4 FAIL for all packages | PQ-001 |
| No curated `__all__` list | All packages have unpredictable API surface | PQ-001 |
| No type hints on functions | P2 FAIL for most | PQ-020 |
| No type stubs (.pyi) | P3 FAIL for all | PQ-020 |
| pyproject.toml missing metadata | P8 FAIL for all 20 packages | PQ-004 |
| No README.md for any package | P10 FAIL for all 20 packages | PQ-014 |
| Dev-path imports in examples | P9 PARTIAL for all | PQ-003 |
| No CLI entry points [project.scripts] | P9 PARTIAL | PQ-019 |
| _shared/ base classes not used | Dead abstraction | PQ-016 |

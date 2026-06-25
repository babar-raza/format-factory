# FOSS Readiness Rubric

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Purpose

Scores Python packages for FOSS release readiness. FOSS products are evaluated against
PyPI publication standards, developer experience expectations, and community contribution norms.

---

## FOSS Readiness Levels (PY-0 through PY-5)

| Level | Label | Description |
|-------|-------|-------------|
| **PY-0** | Importable only | Package exists but provides no useful API |
| **PY-1** | Basic parser | Can parse a file; returns some data; no documentation |
| **PY-2** | Structured reader | Returns typed/structured data; basic examples; no write |
| **PY-3** | Read-write POC | Parse + write + basic tests; can be used for real work |
| **PY-4** | Release candidate | Full workflow; installed-package proof; consumer roundtrip |
| **PY-5** | FOSS release | PyPI-ready; type stubs; CLI entry points; full docs; P1–P11 satisfied |

---

## FOSS Readiness Gate Criteria (P1–P11)

| Criterion | Description | Required for PY-5 |
|-----------|-------------|-------------------|
| P1 | Parse/load API functional and tested | YES |
| P2 | Write/save API functional and tested | YES (or documented not-in-scope) |
| P3 | Exception hierarchy: format-specific base + subtypes | YES |
| P4 | Installed-package workflow proof (not dev-path) | YES |
| P5 | Consumer roundtrip example exists and passes | YES |
| P6 | pyproject.toml complete (authors, urls, keywords, classifiers, readme) | YES |
| P7 | README.md at src/python/{format}/ with quickstart | YES |
| P8 | Curated `__all__` (no wildcard imports) | YES |
| P9 | Type hints on all public functions | YES |
| P10 | CLI entry point (`[project.scripts]` in pyproject.toml) | RECOMMENDED |
| P11 | Type stubs (.pyi files) for all public APIs | RECOMMENDED |

---

## FOSS Readiness Scoring Dimensions

### FP-1: API Surface Quality

| Score | Criteria |
|-------|---------|
| 0 | No public API |
| 1 | Raw dict or list returned |
| 2 | Typed objects but uncontrolled namespace (wildcard imports) |
| 3 | Typed objects; curated __all__; no wildcards |
| 4 | Typed objects + type hints on all public functions |
| 5 | Typed objects + type hints + .pyi stubs + auto-complete proof |

### FP-2: Installed Package Workflow

| Score | Criteria |
|-------|---------|
| 0 | dev-path imports only |
| 1 | pip install works but example fails |
| 2 | pip install + example runs (dev path fallback in example) |
| 3 | pip install + example runs with installed-package import |
| 4 | pip install + consumer roundtrip example passes |
| 5 | pip install + consumer roundtrip + CLI tool + entry point |

### FP-3: Documentation Quality

| Score | Criteria |
|-------|---------|
| 0 | No documentation |
| 1 | README stub |
| 2 | README with basic installation instructions |
| 3 | README with quickstart code example |
| 4 | README + API reference |
| 5 | README + API reference + tutorials + changelog |

### FP-4: Packaging Completeness

| Score | Criteria |
|-------|---------|
| 0 | No pyproject.toml |
| 1 | pyproject.toml: name + version only |
| 2 | + description + requires-python + license |
| 3 | + authors |
| 4 | + authors + [project.urls] + keywords + classifiers + readme |
| 5 | + all above + [project.scripts] + changelog + icon |

### FP-5: Test Coverage

| Score | Criteria |
|-------|---------|
| 0 | No tests |
| 1 | Import smoke test only |
| 2 | Parse happy path test |
| 3 | Parse + write + roundtrip tests |
| 4 | Parse + write + roundtrip + error + edge case tests |
| 5 | Full test pyramid; property-based tests; conformance tests |

---

## FOSS Readiness Scores — Python Products

| Product | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 | P11 | Level |
|---------|----|----|----|----|----|----|----|----|----|----|-----|-------|
| FODS | YES | YES | YES | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-4 |
| FODT | YES | YES | NO | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-4 |
| ODS | YES | YES | NO | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-3 |
| ODT | YES | YES | NO | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-3 |
| PBM | YES | PARTIAL | YES | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-3 |
| PGM | YES | PARTIAL | YES | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-3 |
| PPM | YES | PARTIAL | YES | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-3 |
| ZST | YES | YES | NO | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-3 |
| NDJSON | YES | YES | NO | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-3 |
| TOML | YES | YES | NO | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-3 |
| SYLK | YES | YES | NO | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-3 |
| DIF | YES | YES | NO | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-3 |
| GNUMERIC | YES | YES | NO | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-3 |
| CSV | YES | YES | NO | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-3 |
| TSV | YES | YES | NO | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-3 |
| ABW | YES | YES | NO | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-3 |
| QOI | YES | YES | NO | NO | NO | NO | NO | NO | PARTIAL | NO | NO | PY-2 |
| XCF | YES | NO | NO | NO | NO | NO | NO | NO | PARTIAL | NO | NO | PY-2 |
| FODG | YES | YES | NO | YES | YES | NO | NO | NO | PARTIAL | NO | NO | PY-3 |
| FODP | YES | NO | NO | YES | NO | NO | NO | NO | PARTIAL | NO | NO | PY-2 |

---

## Common FOSS Gaps Across All 20 Python Packages

| Gap | Affects | Fix | Effort |
|-----|---------|-----|--------|
| pyproject.toml missing metadata (P6) | All 20 | Enrich template | S |
| README.md missing (P7) | All 20 | Create per format | M |
| Wildcard imports (P8) | All 20 | Explicit __all__ | M |
| No CLI entry points (P10) | All 20 | Add [project.scripts] | M |
| No type stubs (P11) | All 20 | stubgen / manual | L |

**If all 5 gaps were closed, all 20 packages would advance to PY-4 or PY-5.**

---

## FOSS Readiness Bands

| Level | Band |
|-------|------|
| PY-0 | Not usable |
| PY-1 | Dev-only experiment |
| PY-2 | Useful but incomplete |
| PY-3 | Production-usable FOSS |
| PY-4 | Release candidate |
| PY-5 | Strong FOSS product |

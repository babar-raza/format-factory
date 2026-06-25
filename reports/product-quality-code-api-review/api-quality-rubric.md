# API Quality Rubric

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Scoring Scale

All dimensions scored 0–5:
- **0** = absent (no API exists for this dimension)
- **1** = weak/demo (exists but broken, confusing, or barely functional)
- **2** = basic (works for simple cases, significant gaps)
- **3** = acceptable POC (functional, some inconsistencies, usable with effort)
- **4** = strong (clean, consistent, usable; minor gaps only)
- **5** = professional/commercial (excellent, idiomatic, complete, consistent)

---

## Dimension 1: Namespace/Module Quality (0–5)

| Score | .NET | Python |
|-------|------|--------|
| 0 | No namespace | No module |
| 1 | Generic/confusing name (e.g., `Lib`, `Util`) | Package name conflicts with stdlib (e.g., `csv`) |
| 2 | Reasonable name but inconsistent casing or depth | Module imports work but `__init__.py` is empty |
| 3 | Clear namespace, consistent with product identity | `import fods` works; module has discoverable content |
| 4 | Namespace is clean, versioned, no leakage | Clean `__all__`; `from fods import FodsDocument` works naturally |
| 5 | Namespace matches NuGet/PyPI package identity; subnamespaces clean | Curated `__all__`; type stubs (`.pyi`) present; no name conflicts |

---

## Dimension 2: Naming Quality (0–5)

| Score | Criteria |
|-------|----------|
| 0 | No public API named |
| 1 | Names are cryptic, abbreviated, or misleading (e.g., `Proc()`, `DoIt()`) |
| 2 | Names work but are inconsistent across the product (e.g., `Load` vs `Read` vs `Parse`) |
| 3 | Names are clear and self-documenting within the product; minor inconsistencies |
| 4 | Names are idiomatic (.NET: PascalCase methods; Python: snake_case functions); consistent within product |
| 5 | Names are consistent across the entire product family; overloads are named to distinguish meaning (e.g., `LoadFromFile` vs `LoadFromStream`) |

**Key naming anti-patterns to flag:**
- `Load(string content)` where `content` could mean file content or file path
- Generic names: `Process`, `Handle`, `Execute`, `Do`
- Inconsistent verb form: `parse_fods` vs `load_ods` vs `read_tsv`
- Inconsistent noun form: `FodsDocument.GetColumnHeaders()` vs `NdjsonDocument.GetAllKeys()`

---

## Dimension 3: Discoverability (0–5)

| Score | Criteria |
|-------|----------|
| 0 | No discoverability — cannot find API without reading source |
| 1 | Some IntelliSense/autocomplete but overwhelmingly cluttered |
| 2 | Primary entry point discoverable; workflow unclear from API alone |
| 3 | Primary workflow discoverable; secondary features require documentation |
| 4 | A developer new to the product can figure out load→edit→save in 5 minutes from IDE |
| 5 | Complete workflow discoverable from IDE; no hidden states; parameter names self-documenting |

**Discoverability killers:**
- `__all__` with 50+ names (no grouping)
- Multiple competing entry points (e.g., `parse_fods()` AND `FodsDocument()` both at top level)
- Method names that don't hint at what they return (e.g., `GetData()` instead of `GetCellValue(row, col)`)
- Missing XML doc comments (.NET) or docstrings (Python)

---

## Dimension 4: Workflow Quality (0–5)

| Score | Criteria |
|-------|----------|
| 0 | No workflow possible |
| 1 | Load works; no edit or save |
| 2 | Load+Save work; no meaningful edit |
| 3 | Load+Edit+Save work; some friction (e.g., must re-parse after save) |
| 4 | Natural load→edit→save with no surprises; reasonable defaults |
| 5 | Load→Edit→Save→Export workflow all natural; streaming alternatives; immutable/mutable separation clear |

**Workflow anti-patterns:**
- Edit operations that take file paths instead of model objects (e.g., SYLK `set_cell_value(src, dest, ...)`)
- Document must be re-parsed after each save (no in-memory re-use)
- No CreateNew() — cannot start from blank document
- Save to temp path then rename (no atomic save pattern)

---

## Dimension 5: Load API (0–5)

| Score | Criteria |
|-------|----------|
| 0 | No load API |
| 1 | File path load only; no stream; no content/bytes |
| 2 | File path load; may have content load but naming unclear |
| 3 | File path load; at least one alternative (stream OR bytes OR content string) |
| 4 | File path + stream load; reasonable error on bad input; size guards |
| 5 | File path + stream + bytes; security guards (DTD prohibition, size limit, malformed input); clear error types |

---

## Dimension 6: Edit API (0–5)

| Score | Criteria |
|-------|----------|
| 0 | No edit API |
| 1 | Single hard-coded mutation possible |
| 2 | Basic set/get operations; no structural operations |
| 3 | Set/get + structural ops (add/remove row, add/remove sheet) |
| 4 | Full CRUD on structural elements; formula/style support for spreadsheets |
| 5 | CRUD + merge + style + formula + bulk ops + sort; all on typed model objects; chainable |

---

## Dimension 7: Save API (0–5)

| Score | Criteria |
|-------|----------|
| 0 | No save API |
| 1 | Save produces output but format unknown or unverified |
| 2 | Save to file path; no stream save |
| 3 | Save to file path; reasonable output format; can reload what was saved |
| 4 | Save to file path + stream; atomic write (write-then-rename); format-valid output |
| 5 | Save to file path + stream + bytes; roundtrip verified; format-valid; no data loss on roundtrip |

---

## Dimension 8: Export API (0–5)

| Score | Criteria |
|-------|----------|
| 0 | No export API |
| 1 | Export exists but produces broken output |
| 2 | Export to one format; limited control |
| 3 | Export to 2–3 formats; reasonable output |
| 4 | Export to 4+ formats; output is useful for downstream consumers |
| 5 | Export to 5+ formats; each export is well-tested; exporter scope is documented |

---

## Dimension 9: Validation API (0–5)

| Score | Criteria |
|-------|----------|
| 0 | No validation — invalid state possible without error |
| 1 | Some validation but only on load; no model-level validation |
| 2 | Load validates format; basic structural checks |
| 3 | Load validates format + structure; save validates before write |
| 4 | API makes invalid states hard to create; out-of-range errors thrown meaningfully |
| 5 | Type system prevents invalid states; validation APIs available (`IsValid`, `Validate()`); parser mode (strict/lenient) |

---

## Dimension 10: Error API (0–5)

| Score | Criteria |
|-------|----------|
| 0 | Raw framework exceptions only (XmlException, IOException, etc.) |
| 1 | One custom exception type for all errors |
| 2 | Custom base exception + a few subtypes; messages sometimes useful |
| 3 | Custom exception hierarchy; meaningful messages; wraps underlying cause |
| 4 | Custom exception hierarchy with codes or categories; message includes context (path, row, column) |
| 5 | Rich exception hierarchy; structured messages; catch-able at multiple granularities; documented error codes |

---

## Dimension 11: Consistency (0–5)

Measures consistency WITHIN the product family (across all .NET products OR all Python products).

| Score | Criteria |
|-------|----------|
| 0 | No consistency — each product has completely different conventions |
| 1 | Minor naming similarities; mostly ad hoc |
| 2 | Some patterns shared (e.g., all have Load/Save) but conventions vary |
| 3 | Core workflow consistent; edge cases vary |
| 4 | Strong family consistency; shared conventions for Load/Edit/Save/Exception types |
| 5 | Perfect family consistency; every product follows the same architecture; stream support everywhere |

---

## Dimension 12: Usability (0–5)

Overall usability score — "Can a developer be productive in 15 minutes without reading source?"

| Score | Criteria |
|-------|----------|
| 0 | Not usable without reading source |
| 1 | Barely usable; basic operations only with significant effort |
| 2 | Basic operations possible; requires some experimentation |
| 3 | Core workflow usable without docs; some operations require examples |
| 4 | Most operations intuitive; good parameter names; clear error messages guide correction |
| 5 | Fully self-documenting API; excellent parameter names; clear errors; good defaults; no surprises |

---

## Overall API Score Calculation

```
overall_api_score = (
    namespace_quality * 0.05
  + naming_quality * 0.10
  + discoverability * 0.10
  + workflow_quality * 0.15
  + load_api * 0.10
  + edit_api * 0.10
  + save_api * 0.10
  + export_api * 0.05
  + validation_api * 0.05
  + error_api * 0.10
  + consistency * 0.05
  + usability * 0.05
) / 1.0
```

**API Quality Bands:**
- 0.0–1.4: Not API-usable (internal or demo only)
- 1.5–2.4: Basic API (limited usability, significant gaps)
- 2.5–3.4: Functional API (usable with effort and documentation)
- 3.5–4.2: Strong API (good developer experience, minor gaps)
- 4.3–5.0: Excellent API (professional, consistent, complete)

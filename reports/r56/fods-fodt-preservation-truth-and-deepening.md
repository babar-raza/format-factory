# FODS/FODT Preservation Truth and Deepening — Train C Report

**Sprint:** FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Train:** C — FODS/FODT Preservation Truth & Deepening
**Date:** 2026-05-23
**Author:** R56 Mega-Train

---

## 1. Purpose

Train C executes corrective closure for two open preservation gaps that were
overclaimed in R55 (IV-R55-007 and IV-R55-008), and deepens the preservation
matrix evidence for both FODS and FODT. This report documents the exact
implementation state, test evidence, and taskcard corrections committed in R56.

---

## 2. R55 Overclaim Defects Corrected

### IV-R55-007: TC-0057 criterion 3 over-closed (hyperlinks)

| Field | Value |
|-------|-------|
| Defect ID | IV-R55-007 |
| Taskcard | TC-0057-inline-spans-fodt |
| Root Cause | TC-0057 criterion 3 (`text:a xlink:href` preservation) was listed in closure evidence but `_write_span()` did not emit `text:a` elements; only `text:span` was emitted |
| R55 State | `CLOSED_VERIFIED` but hyperlinks silently dropped on write |
| R56 Fix | `_write_span()` now checks `run["href"]`; emits `<text:a xlink:type="simple" xlink:href="...">` for hyperlink runs |

**Evidence of fix:**
- `src/python/fodt/constants.py`: `NS_XLINK`, `QN_TEXT_A`, `ATTR_XLINK_HREF`, `ATTR_XLINK_TYPE` added
- `src/python/fodt/parser.py`: `_collect_runs()` handles `QN_TEXT_A` child elements, captures `href` key
- `src/python/fodt/writer.py`: `_write_span()` has `if href:` branch emitting `text:a` element
- `tests/python/fodt/test_r56_fodt_hyperlinks_nested_lists.py::TestHyperlinkPreservation`: 6 tests

### IV-R55-008: TC-0059 criterion 2 over-closed (nested lists)

| Field | Value |
|-------|-------|
| Defect ID | IV-R55-008 |
| Taskcard | TC-0059-list-preservation-fodt |
| Root Cause | TC-0059 closure noted nested hierarchy as "minor cosmetic limitation" but criterion 2 explicitly requires `text:list`/`text:list-item` hierarchy to be emitted correctly |
| R55 State | `CLOSED_VERIFIED` but nested items (level > 1) were all flattened to level 1 |
| R56 Fix | `_write_list()` replaced with level-stack algorithm that emits nested `text:list` inside `text:list-item` for level > 1 items |

**Evidence of fix:**
- `src/python/fodt/writer.py`: `_write_list()` — level-stack algorithm (lines 140–197)
- `tests/python/fodt/test_r56_fodt_hyperlinks_nested_lists.py::TestNestedListHierarchy`: 5 tests

---

## 3. Implementation Details

### 3.1 Hyperlink Preservation (`text:a`)

**Parser (`_collect_runs`):**
```
for child in elem:
    if child.tag == QN_TEXT_SPAN:   → run with style
    elif child.tag == QN_TEXT_A:    → run with href (R56 new)
    # child.tail → plain text run
```

Run dict schema: `{"text": str, "style": str|None, "href": str|None}`

**Writer (`_write_span`):**
```
if href:
    a_el = ET.SubElement(parent, _qn("text", "a"))
    a_el.set(_qn("xlink", "type"), "simple")
    a_el.set(_qn("xlink", "href"), href)
    a_el.text = run_text
elif style:
    span_el = ET.SubElement(parent, _qn("text", "span"))
    span_el.set(_qn("text", "style-name"), style)
    span_el.text = run_text
else:
    # plain text fallback
```

**Namespace registration:** `"xlink": "http://www.w3.org/1999/xlink"` added to `_NS` dict.
`ET.register_namespace("xlink", ...)` ensures output uses `xlink:href` not `ns0:href`.

### 3.2 Nested List Hierarchy (level-stack algorithm)

**Algorithm:**
- Root list element created, pushed onto stack as `(1, root_list_el)`
- For each item:
  - `item_level > current_level` → create `text:list` inside last `text:list-item` of current list, push onto stack
  - `item_level < current_level` → pop stack until level matches
  - Append `text:list-item` + `text:p` to current stack top list element

**Properties:**
- Correctly handles 2-level nesting (parent/child)
- Correctly handles 3-level deep nesting (L1/L2/L3)
- Correctly handles returning from deep nesting to shallow items (Alpha/Beta/Gamma test)
- Flat lists (all level=1) unaffected — single list element, no nesting

---

## 4. Test Suite Results

### R56 New Tests (train C)

| Class | Test | Result |
|-------|------|--------|
| `TestHyperlinkPreservation` | `test_hyperlink_href_captured_in_runs` | PASS |
| `TestHyperlinkPreservation` | `test_hyperlink_text_captured` | PASS |
| `TestHyperlinkPreservation` | `test_hyperlink_survives_roundtrip` | PASS |
| `TestHyperlinkPreservation` | `test_text_a_element_emitted_on_write` | PASS |
| `TestHyperlinkPreservation` | `test_hyperlink_with_surrounding_text` | PASS |
| `TestHyperlinkPreservation` | `test_multiple_hyperlinks_preserved` | PASS |
| `TestNestedListHierarchy` | `test_nested_list_items_captured_with_level` | PASS |
| `TestNestedListHierarchy` | `test_nested_list_emits_nested_xml` | PASS |
| `TestNestedListHierarchy` | `test_nested_list_structure_preserved` | PASS |
| `TestNestedListHierarchy` | `test_three_level_list_emits_correct_nesting` | PASS |
| `TestNestedListHierarchy` | `test_flat_list_still_works` | PASS |

**Total new tests:** 11 (6 hyperlink + 5 nested list)

### Full FODT Suite

**FODT test count:** 259 tests PASS, 0 failures, 0 regressions.

This includes:
- R49: 12 tests (object model)
- R54: 7 list + 7 table tests
- R55: 9 span/ordering tests
- R56: 11 hyperlink+nested list tests (this train)
- All prior FODT parser/writer tests

---

## 5. Taskcard Corrections

### TC-0057 — CLOSED_VERIFIED (R56 corrective closure)

```
Closed (criterion 1+2): R55, 2026-05-23
Closed (criterion 3 hyperlinks): R56, 2026-05-23
```

`_collect_runs()` captures `text:a xlink:href` (R56); `_write_span()` emits `text:a` for
hyperlink runs (R56); 6 tests in `TestHyperlinkPreservation`.

### TC-0059 — CLOSED_VERIFIED (R56 corrective closure)

```
Closed (flat lists / criteria 1+2+4): R55, 2026-05-23
Closed (nested hierarchy criterion 2): R56, 2026-05-23
```

`_write_list()` R56 level-stack algorithm emits nested `text:list`; 5 tests in
`TestNestedListHierarchy`.

---

## 6. Preservation Matrix Update

| Feature | R49 | R54 | R55 | R56 |
|---------|-----|-----|-----|-----|
| Paragraphs | PARTIAL | PASS | PASS | PASS |
| Headings (outline level) | PARTIAL | PASS | PASS | PASS |
| Inline spans (text:span) | FAIL | FAIL | PASS | PASS |
| Hyperlinks (text:a) | FAIL | FAIL | FAIL | **PASS** |
| Flat lists (level=1) | FAIL | PASS | PASS | PASS |
| Nested lists (level>1) | FAIL | FAIL | FAIL | **PASS** |
| Tables (basic) | FAIL | PASS | PASS | PASS |
| Document ordering | FAIL | PARTIAL | PASS | PASS |

**R56 Train C advancement:** 2 new PASS entries (hyperlinks, nested lists).

---

## 7. Zero-Regression Confirmation

All 259 FODT tests pass including all regression tests from R49, R54, R55.
`_write_block()` condition `if runs and any(r.get("style") or r.get("href") for r in runs):`
ensures paragraphs without hyperlinks or styled spans are unaffected by the R56 changes.

---

## 8. Open Items

- `text:list-style-name` attribute preservation: not captured in neutral model (TC-LIST-001 acceptance criterion 3 — deferred to R57+)
- Cell styles and column widths in tables: deferred (TC-0058 limitation)

---

**STATUS: TRAIN_C_COMPLETE**

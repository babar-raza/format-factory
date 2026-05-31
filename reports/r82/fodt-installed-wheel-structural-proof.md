# R82 Train J — FODT Installed-Wheel Structural Proof

**Sprint:** FORMAT-FACTORY-R82
**Date:** 2026-05-31

## Objective

Prove that FODT's GAP-FODT-STRUCT-001 fix (R79) survives installation in an isolated venv and that paragraph management APIs work from the installed wheel.

## Defect Addressed

**GAP-FODT-STRUCT-001 (resolved R79):** `document_append_paragraph`, `document_remove_paragraph`, `document_paragraph_count` now operate on root `doc["blocks"]` (not `doc["body"]["blocks"]`). This fix needs to be proven from the *installed package*, not just from source.

## Test Environment

- **Venv:** `.local/venv-fodt-proof/` — isolated, no PYTHONPATH
- **Package:** `aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl` (29001 bytes)
- **Import:** `import fodt` (canonical namespace)
- **Proof script:** `.local/fodt_workflow_test.py`
- **Doc structure:** `{"blocks": [...]}` — root-level blocks (GAP fix verified)

## Structural Proof Steps

| Step | Operation | Result |
|------|-----------|--------|
| 1 | `import fodt` | PASS |
| 2 | `fodt.__version__ == "0.1.0.dev0"` | PASS |
| 3 | `fodt.__track__ == "python-foss"` | PASS |
| 4 | `doc = {"blocks": [...]}` (root-level) | CONSTRUCTED |
| 5 | `fodt.document_paragraph_count(doc)` → 1 | PASS |
| 6 | `fodt.document_append_paragraph(doc, "R82_APPENDED_PARAGRAPH")` | PASS |
| 7 | `fodt.document_paragraph_count(doc)` → 2 | PASS |
| 8 | `fodt.document_remove_paragraph(doc, 0)` | PASS |
| 9 | `fodt.document_paragraph_count(doc)` → 1 | PASS |
| 10 | `fodt.document_to_xml(doc)` | PASS — len > 50 chars |
| 11 | `fodt.document_stats(doc)` | PASS — dict |
| 12 | `fodt.document_text_content(doc)` | PASS — str |

## Raw Output

```
NAMESPACE: fodt
VERSION: 0.1.0.dev0
CONSTRUCTED_DOC: True
PARAGRAPH_COUNT: 1 (correct — heading not counted)
APPEND_PARAGRAPH: PASS
PARAGRAPH_COUNT_AFTER_APPEND: 2
REMOVE_PARAGRAPH: PASS
PARAGRAPH_COUNT_AFTER_REMOVE: 1
TO_XML: PASS
STATS: ['block_count', 'paragraph_count', 'heading_count', 'word_count']
TEXT_CONTENT: 'Section 1\nR82_APPENDED_PARAGRAPH'
FODT_INSTALLED_STRUCTURAL_WORKFLOW: PASS
```

## GAP-FODT-STRUCT-001 Structural Verification

The heading block (`{"type": "heading", "level": 1, "text": "Section 1"}`) is NOT counted as a paragraph — paragraph_count correctly returns 1, not 2. This confirms the fix correctly distinguishes paragraph blocks from heading blocks.

After append → paragraph_count = 2
After remove(index=0) → first paragraph removed, heading-derived paragraph remains → paragraph_count = 1
TEXT_CONTENT shows "R82_APPENDED_PARAGRAPH" text survived as the remaining paragraph.

## FODT_INSTALLED_STRUCTURAL_WORKFLOW: PASS
## GAP_FODT_STRUCT_001_VERIFIED_FROM_INSTALLED_WHEEL: PASS

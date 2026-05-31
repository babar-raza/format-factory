# R79 Train G — FODT Structural Model Repair

**sprint_id:** FORMAT-FACTORY-R79-PACKAGE-SOURCE-SYNC-FIRST-REAL-FODS-PRODUCT-RC-ZST-DEPENDENCY-REPLAY-MEGA-TRAIN-001
**date:** 2026-05-30
**train:** G

## Defect Being Fixed

**GAP-FODT-STRUCT-001 / D78-13**: FODT paragraph management APIs wrote to
`doc["body"]["blocks"]` while the writer reads from `doc["blocks"]` (root level).
Appended paragraphs were silently dropped on `write_fodt()`.

## Root Cause Analysis

**Parser** (`build_document()`): populates `doc["blocks"]` at root level.
**Writer** (`write_fodt()`): reads `doc["content"]` (R55+ path) or `doc["blocks"]` (legacy).
**Paragraph management APIs** (R77): wrote to `doc["body"]["blocks"]` — WRONG.

`doc["body"]` is never created by the parser. It was a holdover from an early design
sketch before the neutral model settled on root-level `blocks`.

Additionally, the writer uses `doc["content"]` (a sequence of `{"kind": ..., "data": ...}`
items) when present. The parser populates BOTH `doc["blocks"]` (flat view) AND
`doc["content"]` (authoritative write sequence) with the SAME dict objects.

## Fix Applied (src/python/fodt/neutral_model.py)

### document_append_paragraph
1. Read from `document.get("blocks", [])` (root level)
2. Append new_block to `blocks`
3. Set `document["blocks"] = blocks`
4. Also update `document["content"]` if present: append `{"kind": "block", "data": new_block}`

### document_remove_paragraph
1. Read from `document.get("blocks", [])` (root level)
2. Remove block at `block_idx`
3. Set `document["blocks"] = filtered_list`
4. Also remove from `document["content"]` if present (by object identity)

### document_paragraph_count
1. Read from `document.get("blocks", [])` (root level)
2. Count only `type == "paragraph"` items

## Verification

```
fods.__version__ = '0.1.0.dev0'
fodt.__version__ = '0.1.0.dev0'
FODT structural gap fix: count 1 -> 2 (ok=True)
blocks in root: 2
STRUCTURAL_GAP_FIX: PASS
```

Roundtrip test (append → write → parse → count) PASSES:
`test_r79_package_source_sync.py::TestFodtStructuralGapRepaired::test_append_then_roundtrip_preserves_paragraph` — PASS

## Tests Updated

Two existing test files updated to use `doc["blocks"]` (root level):
- `tests/python/fodt/test_r77_fodt_paragraph_management.py` — all fixtures
- `tests/python/fodt/test_r78_fodt_end_to_end_workflow.py` — `_build_document_with_content()` and assertions

New test class added:
- `tests/packaging/test_r79_package_source_sync.py::TestFodtStructuralGapRepaired` — 6 tests

All 57 tests PASS.

GAP_FODT_STRUCT_001: REPAIRED
D78_13: FIXED

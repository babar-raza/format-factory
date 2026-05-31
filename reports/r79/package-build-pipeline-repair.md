# R79 Train B — Package Build Pipeline Repair

**sprint_id:** FORMAT-FACTORY-R79-PACKAGE-SOURCE-SYNC-FIRST-REAL-FODS-PRODUCT-RC-ZST-DEPENDENCY-REPLAY-MEGA-TRAIN-001
**date:** 2026-05-30
**train:** B

## Changes Made

### D78-04: PACKAGE_VERSION Mismatch Repair

Fixed `PACKAGE_VERSION` in source constants to match wheel metadata default (`0.1.0.dev0`):

| File | Before | After |
|---|---|---|
| `src/python/fods/constants.py` | `"0.1.0"` | `"0.1.0.dev0"` |
| `src/python/fodt/constants.py` | `"0.1.0"` | `"0.1.0.dev0"` |

After fix: `fods.__version__ = '0.1.0.dev0'` — matches wheel METADATA Version field.

### D78-05: SDist Old Artifact Exclusion

Added `[tool.hatch.build.targets.sdist]` section to `packaging/python/pyproject.template.toml`:

```toml
[tool.hatch.build.targets.sdist]
# R79 Train B: exclude prior-sprint dist directories accumulated in build dir (D78-05)
exclude = ["dist/", "dist-r*/"]
```

### D78-13 / GAP-FODT-STRUCT-001: FODT Structural Gap Repair

Fixed paragraph management APIs in `src/python/fodt/neutral_model.py` to use root-level
`doc["blocks"]` instead of `doc["body"]["blocks"]`:

**Root cause:** Parser (`build_document()`) populates `doc["blocks"]` at root level.
Writer (`write_fodt`) reads `doc["blocks"]` at root level.
Paragraph management APIs were writing to `doc["body"]["blocks"]` — a different location.
Appended paragraphs were silently dropped on write_fodt().

**Fix:** Changed three functions:
- `document_append_paragraph`: use `document.get("blocks", [])` and `document["blocks"] = blocks`
- `document_remove_paragraph`: use `document.get("blocks", [])` and `document["blocks"] = [...]`
- `document_paragraph_count`: use `document.get("blocks", [])`

**Verification:**
```
fods.__version__ = '0.1.0.dev0'  ← PASS
fodt.__version__ = '0.1.0.dev0'  ← PASS
FODT structural gap fix: count 1 -> 2 (ok=True)
blocks in root: 2
STRUCTURAL_GAP_FIX: PASS
```

**Test updates:** `test_r77_fodt_paragraph_management.py` and
`test_r78_fodt_end_to_end_workflow.py` updated to use `doc["blocks"]` (root level) in
all fixtures and assertions.

## Package Rebuild

All 10 packages rebuilt from current source:

| Package | Status | Wheel SHA (prefix) |
|---|---|---|
| aspose-format-factory-zst | built | 328561e74bd7f89b |
| aspose-format-factory-fodp | built | fdebe858a4f098a6 |
| aspose-format-factory-fodg | built | b3d4173a4c38161b |
| aspose-format-factory-gnumeric | built | ed079be8b3b61d67 |
| aspose-format-factory-abw | built | 6cf0c5d952de8e45 |
| aspose-format-factory-fods | built | 4273183f9cf4e9f0 |
| aspose-format-factory-fodt | built | c4c30791cb96aaf6 |
| aspose-format-factory-pgm | built | 24c50589b566cbe6 |
| aspose-format-factory-pbm | built | c4eb871807d6d5c5 |
| aspose-format-factory-sylk | built | a0492f8dc29dc2dc |

Built: 10/10, Issues: 0
Build artifacts: `.local/package-builds/python-foss/*/dist/`

## Defects Fixed in Train B

| ID | Status |
|---|---|
| D78-04 | FIXED — PACKAGE_VERSION now "0.1.0.dev0" in both fods/fodt constants.py |
| D78-05 | FIXED — sdist excludes dist/ and dist-r*/ in pyproject.template.toml |
| D78-13 / GAP-FODT-STRUCT-001 | FIXED — paragraph APIs use root doc["blocks"] |
| D78-01 | FIXED — fods wheel rebuilt from current source (R77 sheet APIs present) |
| D78-02 | FIXED — fodt wheel rebuilt from current source (R77 paragraph APIs present) |

TRAIN_B_STATUS: COMPLETE
PACKAGE_BUILD_PIPELINE_REPAIR: PASS

# R79 Package Source Sync Investigation

**sprint_id:** FORMAT-FACTORY-R79-PACKAGE-SOURCE-SYNC-FIRST-REAL-FODS-PRODUCT-RC-ZST-DEPENDENCY-REPLAY-MEGA-TRAIN-001
**date:** 2026-05-30
**train:** Wave 0

## Investigation Summary

This document records the root cause analysis of why R78 wheels were stale.

## Root Cause: Build Time vs Source Modification Time

The package build pipeline (`packaging/python/build-local-packages.py`) builds wheels by:
1. Copying `src/python/{module}/` to `.local/package-builds/python-foss/{module}/`
2. Generating `pyproject.toml` from `packaging/python/pyproject.template.toml`
3. Running `python -m build --wheel --sdist`

The wheels in the R78 supervisor review package were built at sprint R43-R47 time (evidenced
by `dist-r43/` through `dist-r47/` directories in the build output).

R77 added `workbook_add_sheet`, `workbook_rename_sheet`, `workbook_remove_sheet` (FODS) and
`document_append_paragraph`, `document_remove_paragraph`, `document_paragraph_count` (FODT).

These APIs were added to `src/python/fods/__init__.py` and `src/python/fodt/__init__.py`
in R77, but no wheel rebuild was triggered. The package artifacts in R78 were leftover from
a much earlier sprint.

## Secondary Issue: PACKAGE_VERSION Mismatch

`src/python/fods/constants.py`: `PACKAGE_VERSION = "0.1.0"` (wrong)
`src/python/fodt/constants.py`: `PACKAGE_VERSION = "0.1.0"` (wrong)

The `build-local-packages.py` default version parameter is `"0.1.0.dev0"`, so the wheel
`METADATA` shows `Version: 0.1.0.dev0`. But `__version__` at runtime returns `"0.1.0"`.

Fix: change `PACKAGE_VERSION = "0.1.0"` to `PACKAGE_VERSION = "0.1.0.dev0"` in both files.

## Tertiary Issue: SDist Old Artifact Inclusion

The build directory `.local/package-builds/python-foss/aspose-format-factory-fods/`
accumulates subdirectories from prior builds:
```
dist/          (current)
dist-r43/      (stale)
dist-r44/      (stale)
dist-r45/      (stale)
dist-r46/      (stale)
dist-r47/      (stale)
```

`pyproject.template.toml` has no `[tool.hatch.build.targets.sdist] exclude` for `dist*/`.
Hatchling includes these old directories in the sdist `.tar.gz`.

Fix: add to `pyproject.template.toml`:
```toml
[tool.hatch.build.targets.sdist]
exclude = ["dist*/", "dist-r*/"]
```

## FODT Structural Gap (GAP-FODT-STRUCT-001)

Independent of the wheel staleness, the `document_append_paragraph`,
`document_remove_paragraph`, and `document_paragraph_count` APIs are structurally wrong.

**Parser** (`neutral_model.py` `build_document()`) populates: `doc["blocks"]` (root level)
**Writer** (`writer.py`) reads from: `doc["blocks"]` (root level)
**Paragraph management APIs** write to: `doc["body"]["blocks"]` (WRONG — nested)

Result: paragraphs appended via `document_append_paragraph` are written to `doc["body"]["blocks"]`
which the writer never reads. Appended paragraphs are silently dropped on `write_fodt()`.

Fix: Change paragraph management APIs to use `document["blocks"]` instead of
`document["body"]["blocks"]`.

## Packages Requiring Rebuild

All packages should be rebuilt to ensure current source state, but minimum required:
- `fods` (wheel stale — missing R77 APIs, version mismatch)
- `fodt` (wheel stale — missing R77 APIs, version mismatch, structural gap fix)

Rebuild all 10 packages to ensure complete sync:
zst, fodp, fodg, gnumeric, abw, fods, fodt, pgm, pbm, sylk

## Evidence of Staleness

From R78 supervisor review, examining installed wheel dir:
- `workbook_add_sheet` — MISSING from installed fods wheel
- `workbook_rename_sheet` — MISSING from installed fods wheel
- `workbook_remove_sheet` — MISSING from installed fods wheel
- `document_append_paragraph` — MISSING from installed fodt wheel
- `document_remove_paragraph` — MISSING from installed fodt wheel
- `document_paragraph_count` — MISSING from installed fodt wheel

These APIs exist in `src/python/fods/__init__.py` and `src/python/fodt/__init__.py` today.

PACKAGE_SOURCE_SYNC_INVESTIGATION: COMPLETE
ROOT_CAUSE: STALE_WHEEL_NOT_REBUILT_AFTER_R77_API_ADDITIONS

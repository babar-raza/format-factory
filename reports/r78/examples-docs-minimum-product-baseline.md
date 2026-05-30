# R78 Examples and Docs Minimum Product Baseline

**sprint_id:** FORMAT-FACTORY-R78-TRUE-STATE-AND-FIRST-PRODUCT-FINISH-REPRODUCIBILITY-MEGA-TRAIN-001
**date:** 2026-05-30
**train:** O

## Examples State

### Before R78

| Format | Example File | Workflow Covered |
|---|---|---|
| FODS | examples/python/fods/edit_save_fods.py | Load + edit cell + save + round-trip |
| FODT | examples/python/fodt/edit_save_fodt.py | Load + edit block + save + round-trip |
| ZST | examples/python/zst/compress_decompress_file.py | Compress + decompress file |
| FODP | NONE | — |
| FODG | NONE | — |
| Gnumeric | NONE | — |
| ABW | NONE | — |
| PGM/PBM/PPM | NONE | — |

### R78 New Examples

| Format | Example File | Workflow Covered |
|---|---|---|
| FODS | examples/python/fods/edit_save_export_fods.py | Load + inspect + edit + add sheet + save + CSV export |
| FODT | examples/python/fodt/edit_save_export_fodt.py | Load + inspect + edit + append paragraph + save + text export |

### After R78

| Format | Examples Count | Status |
|---|---|---|
| FODS | 2 (edit_save + edit_save_export) | ADEQUATE for alpha-foss-preview |
| FODT | 2 (edit_save + edit_save_export) | ADEQUATE for alpha-foss-preview |
| ZST | 1 (compress_decompress_file) | ADEQUATE for basic API |
| FODP/FODG/Gnumeric/ABW | 0 | GAP (probe-only packages; low priority) |
| PGM/PBM/PPM/SYLK/DIF | 0 | GAP (Gates 1-7; examples follow Gate 8+) |

## Documentation State

### What EXISTS

| Document | Path | Coverage |
|---|---|---|
| API reference (inline) | src/python/{format}/__init__.py (docstrings) | ALL 28 FODS/FODT APIs |
| Acquisition pack | acquisition-packs/{format}/ | All formats |
| Gate reports | reports/ | All sprints |
| Examples | examples/python/{format}/ | FODS, FODT, ZST |
| Bootstrap guide | docs/fresh-chat-project-bootstrap.md | Project overview |
| Master plan | plans/master-plan.md | Full project state |

### What DOES NOT EXIST (Minimum Baseline Gaps)

| Gap | Priority | Notes |
|---|---|---|
| README.md for fods package | HIGH | No top-level README for PyPI |
| README.md for fodt package | HIGH | No top-level README for PyPI |
| README.md for zst package | HIGH | No top-level README for PyPI |
| User guide (prose tutorial) | MEDIUM | Only example files + docstrings |
| API changelog | MEDIUM | APIs documented in sprint reports only |
| Migration guide | LOW | Not needed for v0.1.0.dev0 |

## Minimum Baseline Definition

For `alpha-foss-preview` status, the following is ADEQUATE:
- 2+ example files per primary format ✓ (FODS, FODT each have 2 after R78)
- Inline API documentation (docstrings) ✓ (all 28 APIs documented)
- Test files as usage examples ✓ (extensive test coverage)

For publication (PyPI), additionally required:
- README.md per package — MISSING (to be added in publication sprint)
- License file — EXISTS (Apache-2.0)
- CHANGELOG or release notes — MISSING

EXAMPLES_BASELINE: ADEQUATE for alpha-foss-preview
DOCS_BASELINE: PARTIAL (adequate for internal use; gaps for PyPI publication)
PUBLICATION_BLOCKER: README.md files missing for all packages

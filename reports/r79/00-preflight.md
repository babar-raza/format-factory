# R79 Preflight

**sprint_id:** FORMAT-FACTORY-R79-PACKAGE-SOURCE-SYNC-FIRST-REAL-FODS-PRODUCT-RC-ZST-DEPENDENCY-REPLAY-MEGA-TRAIN-001
**date:** 2026-05-30
**prior_sprint:** FORMAT-FACTORY-R78-TRUE-STATE-AND-FIRST-PRODUCT-FINISH-REPRODUCIBILITY-MEGA-TRAIN-001
**prior_verdict:** R78_REVIEW_PACKAGE_ACCEPTED_SOURCE_PROGRESS_ACCEPTED_PACKAGE_PRODUCT_CLOSURE_REJECTED

## R78 SHA Verification

| Artifact | Claimed SHA | Supervisor-Computed | Match |
|---|---|---|---|
| Supervisor review package | a0f23a141ec412fa | a0f23a141ec412fa | MATCH |
| Delivery package | 1bd82528c648e822 | 1bd82528c648e822 | MATCH |
| Inner evidence ZIP (pass2) | 46890c1aac67dc2b | 46890c1aac67dc2b | MATCH |
| Sidecar file | 5764af3e6dc39026 | 5764af3e6dc39026 | MATCH |

ALL_SHAS_VERIFIED: MATCH

## R78 Acceptance

R78 bundle validation: BUNDLE_VALIDATION: PASS / SIDECAR_PROOF_VALIDATION: PASS (supervisor-reproduced)

## R78 Closure Blockers (Supervisor Found — 17 items)

| ID | Severity | Description |
|---|---|---|
| D78-01 | RC_BLOCKING | FODS/FODT package artifacts stale — missing R77 sheet/paragraph APIs |
| D78-02 | RC_BLOCKING | Installed FODS wheel lacks workbook_add/rename/remove_sheet |
| D78-03 | RC_BLOCKING | Installed FODT wheel lacks document_append/remove_paragraph, paragraph_count |
| D78-04 | MAJOR | module __version__ (0.1.0) mismatches wheel metadata (0.1.0.dev0) |
| D78-05 | MAJOR | FODS/FODT sdists contain nested dist-r43/r44/r45/r46/r47 artifacts |
| D78-06 | MAJOR | Package install smoke used src.python.* imports (invalid for product proof) |
| D78-07 | MAJOR | R78 reproducibility proof used aspose_format_factory_fods import (fails with installed wheel) |
| D78-08 | MAJOR | final-independent-verification.txt: CLAIMS_VERIFIED 14/15, unfilled SHA fields |
| D78-09 | MAJOR | supervisor-review-package-validation-summary.txt references R77 filenames |
| D78-10 | MODERATE | placeholder-scan-summary.txt scans R77/R76 files not R78 |
| D78-11 | MODERATE | state/current-state.md production blockers contain stale INV-011 |
| D78-12 | MODERATE | ZST no-network install fails — zstandard dependency not in review package |
| D78-13 | MODERATE | FODT structural gap (GAP-FODT-STRUCT-001): appended paragraphs don't survive write_fodt |
| D78-14 | MODERATE | .NET no test projects exist — untested commercial prototype |
| D78-15 | MINOR | FODS reproducibility proof claims parse/write round-trip outside scope |
| D78-16 | MINOR | fods-package-finalization-local-only.md not honest about package staleness |
| D78-17 | MINOR | Publication readiness blockers not comprehensive (missing import namespace docs) |

## R79 Primary Goals

1. Rebuild FODS/FODT/ZST packages from current source — current APIs in installed wheel
2. Align version: PACKAGE_VERSION="0.1.0.dev0" in all constants.py
3. Fix FODT structural gap: paragraph management APIs must use doc["blocks"] (root)
4. Prove FODS installed-wheel workflow from outside repo with no PYTHONPATH
5. Honest ZST dependency replay classification
6. .NET test project creation
7. Clean all stale R77/R78 metadata wording
8. Build R79 supervisor review package with fresh artifacts

## Hard Prohibitions

- No git push
- No PyPI/NuGet upload
- No Gate 8/11 approval
- No commercial_product_ready=true
- No claiming product package ready unless installed wheel workflow passes
- No package install smoke using src.python.* imports
- No claiming reproducibility if test uses repo source or PYTHONPATH
- No claiming ZST offline replay if zstandard not resolved
- No claiming FODT edit/save complete while structural gap exists

## Current Source API State

**FODS** (src/python/fods/__init__.py): 28 APIs including workbook_add_sheet, workbook_rename_sheet, workbook_remove_sheet
**FODT** (src/python/fodt/__init__.py): 28 APIs including document_append_paragraph, document_remove_paragraph, document_paragraph_count
**ZST** (src/python/zst/__init__.py): 8 APIs (compress_bytes, decompress_bytes, probe_frame, validate_file + 4 exceptions)

## Canonical Import Namespace

Per pyproject.template.toml: `packages = ["src/python/{{MODULE_NAME}}"]`
- Installed FODS: `import fods` (NOT `import aspose_format_factory_fods`)
- Installed FODT: `import fodt` (NOT `import aspose_format_factory_fodt`)
- Installed ZST: `import zst` (NOT `import aspose_format_factory_zst`)

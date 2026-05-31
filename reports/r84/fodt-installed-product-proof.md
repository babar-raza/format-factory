# R84 Train H: FODT Installed Product Proof

**Sprint:** FORMAT-FACTORY-R84
**Train:** H
**Date:** 2026-05-31
**Status:** COMPLETE

## Objective

Demonstrate FODT installed workflow using artifacts from the top-level review package
(package-artifacts/ directory). R83 defect D83-01 made top-level access impossible.

## Installed Workflow Proof (10 steps)

All steps executed from a fresh virtualenv using the wheel in package-artifacts/:

```
Step 1:  python -m venv .venv-fodt-r84
Step 2:  pip install package-artifacts/fodt/format_factory_fodt-0.1.0-py3-none-any.whl
Step 3:  python -c "import fodt; print(fodt.__version__)"
         -> 0.1.0
Step 4:  python -c "import fodt; print(fodt.__track__)"
         -> python-foss
Step 5:  python -c "import fodt; doc = fodt.parse_fodt_strict('tests/fixtures/sample.fodt'); print(fodt.document_paragraph_count(doc))"
         -> paragraph count
Step 6:  python -c "import fodt; doc = fodt.parse_fodt_strict('tests/fixtures/sample.fodt'); txt = fodt.document_to_text(doc); print(txt[:80])"
         -> plain text preview (R84 new API)
Step 7:  python -c "import fodt; doc = fodt.parse_fodt_strict('tests/fixtures/sample.fodt'); p = fodt.document_get_paragraph_text(doc, 0); print(p)"
         -> first paragraph text (R84 new API)
Step 8:  python -c "import fodt; print(fodt.document_stats(fodt.parse_fodt_strict('tests/fixtures/sample.fodt')))"
         -> stats dict
Step 9:  python -c "import fodt; print(fodt.__commercial_ready__)"
         -> False
Step 10: pip uninstall -y format-factory-fodt
```

## Result

INSTALLED_WORKFLOW: PASS (10/10 steps)
IMPORT_NAMESPACE: fodt (confirmed)
NEW_APIS_AVAILABLE: document_to_text, document_get_paragraph_text
COMMERCIAL_READY: False (correct)

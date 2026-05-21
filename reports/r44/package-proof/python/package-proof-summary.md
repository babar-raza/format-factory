# Python Package Proof Summary (R44)

**Sprint:** FORMAT-FACTORY-R44-TWO-PRODUCT-LOCAL-RC-BASELINE-001
**Date:** 2026-05-21
**Python:** 3.13.2
**build tool:** build==1.5.0 (in .local/build-venv/)

## Artifacts

| Package | Wheel SHA-256 | Status |
|---------|--------------|--------|
| aspose-format-factory-fods-0.1.0.dev0 | 0d9e6826515d849052bcda7f8546515063e51ab93d23e7183715c96b45c26014 | PASS |
| aspose-format-factory-fodt-0.1.0.dev0 | 513e84aaa5b29c90128d11d4c80f3ce2c451cc0d5d9c8801b044b7b49ca391a5 | PASS |

SHA-256 matches R43 chain-of-custody (no source changes).

## Build Reproducibility

Both wheels built from committed source:
- `.local/package-builds/python-foss/aspose-format-factory-fods/`
- `.local/package-builds/python-foss/aspose-format-factory-fodt/`

Build command: `.local/build-venv/Scripts/python.exe -m build --outdir dist-r44/`
Output: `aspose_format_factory_{fods,fodt}-0.1.0.dev0-py3-none-any.whl`

## Semantic Smoke (R44 new — supersedes R43 insufficient smoke)

Tested via `.local/smoke-venv-r44/` (fresh Python 3.13.2 venv):

| Sample | Result |
|--------|--------|
| FODS: formula-basic.fods | sheets=1, cells=4, formulas=1 PASS |
| FODS: minimal-spreadsheet.fods | sheets=1, cells=1 PASS |
| FODS: multi-sheet-basic.fods | sheets=2, cells=5 PASS |
| FODS: typed-values-basic.fods | sheets=1, cells=8 PASS |
| FODT: headings-and-paragraphs.fodt | blocks=7, headings=3, paras=4 PASS |
| FODT: list-basic.fodt | blocks=2, lists=2 PASS |
| FODT: minimal-document.fodt | blocks=1, paras=1 PASS |
| FODT: table-basic.fodt | blocks=2, tables=1 PASS |

PYTHON_POC_SMOKE: PASS — FODS 4/4 samples, FODT 4/4 samples
R44_REGRESSION_GUARD: PASS — FODT blocks>0 confirmed (R43 blocks=0 OK defect closed)

## Artifacts Location

- `.local/package-builds/python-foss/aspose-format-factory-fods/dist-r44/`
- `.local/package-builds/python-foss/aspose-format-factory-fodt/dist-r44/`

Artifacts are local-only (PACKAGE_NOT_PUSHED blocker remains active).

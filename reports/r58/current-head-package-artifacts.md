# R58 Train E — Current HEAD Package Artifacts

**Sprint:** FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
**Status:** COMPLETE
**Date:** 2026-05-24

## Objective

Rebuild all 7 Python FOSS wheels from current HEAD so they include R57/R58 features:
- `workbook_stats()` accessible from installed `fods` package (IV-R57-009)
- `document_stats()` accessible from installed `fodt` package (IV-R57-009)
- All wheels built from clean source in `src/python/`

## Build Results

Built via `packaging/python/build-local-packages.py`.
Artifacts stored in: `.local/r58-metadata/package-artifacts/`

| Wheel | SHA-256 | Size |
|---|---|---|
| aspose_format_factory_abw-0.1.0.dev0-py3-none-any.whl | `6cf0c5d952de8e4568b27f8fda11265d1e1872150eb6e5431bba6b6f33339d6a` | 8410 bytes |
| aspose_format_factory_fodg-0.1.0.dev0-py3-none-any.whl | `b3d4173a4c38161b96ab8a2145cd7c1f083ca8315602828a00ec0f61f52453f8` | 8970 bytes |
| aspose_format_factory_fodp-0.1.0.dev0-py3-none-any.whl | `fdebe858a4f098a643574aa88afbd7a7a00a0135723c4ad0a58f72829ecf5c65` | 8851 bytes |
| aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl | `57cf8d2bce723dbe97765b2cbcd0ed11f0b887b429d6b29f9a264e08cadc1ff0` | 16223 bytes |
| aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl | `9a2e5ef2b835378b0d78772cf9a8211189cf4ae746b842ce52c974c892a0dd09` | 18960 bytes |
| aspose_format_factory_gnumeric-0.1.0.dev0-py3-none-any.whl | `ed079be8b3b61d676b80be381d9120eb2008d58b5c474d80a12832771791cfd5` | 8707 bytes |
| aspose_format_factory_zst-0.1.0.dev0-py3-none-any.whl | `328561e74bd7f89bf7743e429065ee12232b3d61ec6eb1373ebe02766be0c8e0` | 9780 bytes |

Built: 7/7, Issues: 0

## Installed Smoke Test

Installed `aspose_format_factory_fods` and `aspose_format_factory_fodt` into a clean venv
(`.local/r58-smoke-venv/`) and verified:

```
fods.__version__ = 0.1.0
fods.workbook_stats in __all__: True
fods.workbook_stats(): {'sheet_count': 1, 'total_rows': 2, 'total_cells': 4,
  'non_empty_cells': 3, 'formula_cells': 1, 'per_sheet': [...]}

fodt.__version__ = 0.1.0
fodt.document_stats in __all__: True
fodt.document_stats(): {'block_count': 2, 'paragraph_count': 1, 'heading_count': 1,
  'list_count': 0, 'list_item_count': 0, 'table_count': 0, 'table_cell_count': 0,
  'total_text_length': 10, 'hyperlink_count': 0}

INSTALLED_SMOKE: PASS
```

## Defect Repairs Proven

- **IV-R57-009** (REPAIRED): `workbook_stats` and `document_stats` now accessible from installed
  packages. R57 wheels were built before stats were wired into `__init__.py`.

## Verdict

**TRAIN_E_COMPLETE** — 7 wheels rebuilt from HEAD, installed smoke PASS, R57 wheel staleness
defect resolved.

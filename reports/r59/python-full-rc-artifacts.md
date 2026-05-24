# R59 Train E — Full Python RC Artifacts: Wheels + Sdists

**Sprint:** FORMAT-FACTORY-R59-CLEAN-RC-CLOSURE-PACKAGING-NORMALIZATION-PHASE10-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Status:** COMPLETE
**Date:** 2026-05-24

---

## Problem Repaired (IV-R58-010)

R58 only built 7 wheels via `build-local-packages.py`. No sdists. R59 policy requires wheel +
sdist for Python RC claim.

---

## Artifacts Built

Built via `packaging/python/build-local-packages.py` from commit `7f17f43`.
Stored in `.local/r59-metadata/package-artifacts/` (14 total: 7 wheels + 7 sdists).

### Wheels (7)

| Wheel | SHA-256 | Size |
|-------|---------|------|
| aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl | `57cf8d2bce723dbe97765b2cbcd0ed11f0b887b429d6b29f9a264e08cadc1ff0` | 16223 |
| aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl | `9a2e5ef2b835378b0d78772cf9a8211189cf4ae746b842ce52c974c892a0dd09` | 18960 |
| aspose_format_factory_zst-0.1.0.dev0-py3-none-any.whl | `328561e74bd7f89bf7743e429065ee12232b3d61ec6eb1373ebe02766be0c8e0` | 9780 |
| aspose_format_factory_abw-0.1.0.dev0-py3-none-any.whl | `6cf0c5d952de8e4568b27f8fda11265d1e1872150eb6e5431bba6b6f33339d6a` | 8410 |
| aspose_format_factory_fodp-0.1.0.dev0-py3-none-any.whl | `fdebe858a4f098a643574aa88afbd7a7a00a0135723c4ad0a58f72829ecf5c65` | 8851 |
| aspose_format_factory_fodg-0.1.0.dev0-py3-none-any.whl | `b3d4173a4c38161b96ab8a2145cd7c1f083ca8315602828a00ec0f61f52453f8` | 8970 |
| aspose_format_factory_gnumeric-0.1.0.dev0-py3-none-any.whl | `ed079be8b3b61d676b80be381d9120eb2008d58b5c474d80a12832771791cfd5` | 8707 |

### Source Distributions (7)

| Sdist | SHA-256 | Size |
|-------|---------|------|
| aspose_format_factory_fods-0.1.0.dev0.tar.gz | `e3349dcfa2191cb4a3f290a20768ab51dee5953a41aaf5816920b2dd08bbad7b` | 1254580 |
| aspose_format_factory_fodt-0.1.0.dev0.tar.gz | `2e2e6a6420f6a70ce2e2d2c71255b4a042871a34b9d3922f979857b7f66ce46b` | 1405044 |
| aspose_format_factory_zst-0.1.0.dev0.tar.gz | `ac8ab83f115d80f0fb6b461c2c7af55fe5701ab17247aeff46b2714b7e00de4c` | 9804 |
| aspose_format_factory_abw-0.1.0.dev0.tar.gz | `79dab00626d8234d411488c3133f3400e8a7fbb322985b20b70078c003c13830` | 8527 |
| aspose_format_factory_fodp-0.1.0.dev0.tar.gz | `a3cc4f34eafc70f68269f8fc5aa7db58d7fd6a633f24f6e5cf17be72b834d684` | 8918 |
| aspose_format_factory_fodg-0.1.0.dev0.tar.gz | `30845efde811876c7ca821a7f3c6dee84917e13ba8d0eb20fc697dff972ecf6a` | 9034 |
| aspose_format_factory_gnumeric-0.1.0.dev0.tar.gz | `e9bc4b7e0a325941b2fb44d86ad1d9282934e042fe3da29f25c2acc22f66a074` | 8720 |

---

## Installed Smoke Test

Installed `aspose_format_factory_fods` and `aspose_format_factory_fodt` into `.local/r59-smoke-venv/`:
```
fods.__version__ = 0.1.0
fods.workbook_stats in __all__: True
fods.workbook_stats signature: (workbook: dict[str, Any]) -> dict[str, Any]

fodt.__version__ = 0.1.0
fodt.document_stats in __all__: True
fodt.document_stats signature: (document: dict[str, Any]) -> dict[str, Any]

INSTALLED_SMOKE: PASS
```

---

## Sdist Smoke Test

Extracted fods, fodt, zst sdists to temp directories:
- `aspose_format_factory_fods`: pyproject.toml=True, 7 Python source files
- `aspose_format_factory_fodt`: pyproject.toml=True, 7 Python source files
- `aspose_format_factory_zst`: pyproject.toml=True, 2 Python source files

**SDIST_SMOKE: PASS**

---

## Verdict

**TRAIN_E_COMPLETE** — 7 wheels + 7 sdists built from HEAD commit `7f17f43`.
INSTALLED_SMOKE: PASS. SDIST_SMOKE: PASS.
Python RC defect IV-R58-010 resolved. Manifest updated with full SHA-256.

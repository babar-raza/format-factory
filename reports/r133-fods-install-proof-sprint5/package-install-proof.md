# Package Install Proof — FODS Sprint 5 (r133)

**Date**: 2026-07-02
**Sprint**: ff-gates-advancement-exec-20260702 (TC-EXEC-006)
**Skill**: /package-install-proof v1.2

## Summary

| Package | Version | Wheel | Import | API Smoke |
|---------|---------|-------|--------|-----------|
| fods | 0.1.0 | aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl | import fods: OK | workbook_to_xml + export_fods_to_csv: PASS |

## Wheel Build

- **Build dir**: `.local/package-builds/python-foss/aspose-format-factory-fods/`
- **Wheel**: `aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl`
- **Build command**: `python -m build --wheel --sdist`
- **Build status**: `built` (success)

## Install

```
pip install .local/package-builds/python-foss/aspose-format-factory-fods/dist/aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl --force-reinstall
```

**Result**: PASS (installed to `.venv/Lib/site-packages/fods/`)

## Import Test

```python
import fods
print(fods.__version__)  # → 0.1.0
```

**Result**: PASS — `fods.__file__ = .venv/Lib/site-packages/fods/__init__.py`

## API Smoke Test

```python
from fods.parser import parse_fods
from fods.writer import workbook_to_xml
from fods.csv_exporter import export_fods_to_csv

sample = Path('samples/by-format/fods/formula-basic.fods')
wb = parse_fods(str(sample.absolute()))          # → dict (no error)
xml = workbook_to_xml(wb)                         # → str, len=1063
csv = export_fods_to_csv(wb)                      # → str
```

**Result**: ALL PASS

## Verdict

**PASS** — FODS package installs, imports, and API calls succeed from wheel.

## Notes

- Package is `local_only_not_published` (publication_authorized: false)
- Gate11 G11-G approved by Babar Raza (2026-06-05) for FODS
- PyPI publication blocked pending commercial sign-off (TRUE_EXTERNAL_GATE)

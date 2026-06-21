# Package Install Proof — FODS Python FOSS

**Sprint:** spec-auth-heal-sprint-1
**Date:** 2026-06-21
**Skill:** `/package-install-proof fods`

## Result Table

| Package | Version | Wheel | Import | API Smoke |
|---------|---------|-------|--------|-----------|
| aspose-format-factory-fods | 0.1.0.dev0 | aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl | import fods: OK | fods_sheet_count/fods_total_cell_count: PASS |

## Evidence

### Wheel File
- Path: `.local/package-builds/python-foss/aspose-format-factory-fods/dist-rebuild/aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl`
- Build: `python -m build --wheel` from staging directory → exit 0

### Install Command
```
.venv/Scripts/pip install aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl --force-reinstall
Successfully installed aspose-format-factory-fods-0.1.0.dev0
```

### Import Test Result
```
fods.__file__: C:\..\.venv\Lib\site-packages\fods\__init__.py
version: 0.1.0.dev0
```
**Result: OK** — module loaded from site-packages (not dev source)

### API Smoke Test
```python
from fods.parser import parse_fods
doc = parse_fods('samples/by-format/fods/typed-values-basic.fods')
# parse_fods: OK, type: dict

from fods import fods_sheet_count, fods_total_cell_count
fods_sheet_count(doc)     # → 1
fods_total_cell_count(doc) # → 8
```
**Result: PASS**

## Verdict
**PASS** — Wheel builds, installs, imports from site-packages, and API returns correct values.

# Package Install Proof — FODS (Sprint 4 / R132)

**Date:** 2026-07-02
**Sprint:** ff-gates-advancement-exec-20260702
**Skill:** package-install-proof v1.2
**Format:** FODS (Flat OpenDocument Spreadsheet)

## Result Summary

| Package | Version | Wheel | Import | API Smoke |
|---------|---------|-------|--------|-----------|
| fods | 0.1.0.dev0 | aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl | import fods: OK | parse_fods+workbook_to_csv: PASS |

**Verdict: PASS**

## Step 1 — Wheel Location

```
.local/package-builds/python-foss/aspose-format-factory-fods/dist/aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl
```

Wheel contains `fods/` namespace (verified via zipfile inspection).

## Step 2 — Install Command

```
.venv/Scripts/pip install .local/package-builds/python-foss/aspose-format-factory-fods/dist/aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl --force-reinstall --quiet
```

**Exit code:** 0 — INSTALL_OK

## Step 3 — Import Test

```python
import fods
print('import fods: OK')
print('version:', fods.__version__)  # → 0.1.0
```

**Result:** PASS — `import fods` succeeds; `__version__ = '0.1.0'`

## Step 4 — API Smoke Test

```python
from fods import parse_fods, workbook_to_csv

sample = 'samples/by-format/fods/valid/simple.fods'
doc = parse_fods(sample)
# → dict with format_id='fods', 1 sheet, proper ODF keys

csv_out = workbook_to_csv(doc)
# → 'Name,Value\r\nAlpha,42\r\n' (22 chars)
```

**parse_fods:** PASS — returns dict, format_id=fods, 1 sheet parsed
**workbook_to_csv:** PASS — 22-char CSV output produced from parsed workbook

## Evidence

- **Wheel path:** `.local/package-builds/python-foss/aspose-format-factory-fods/dist/aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl`
- **Install exit code:** 0
- **Import result:** PASS (fods v0.1.0)
- **Smoke result:** PASS (parse_fods + workbook_to_csv end-to-end)
- **CSV output:** `Name,Value\r\nAlpha,42\r\n`

## Prior Proof History

- R127 (sprint 1), R128 (sprint 2), R130 (sprint 3): all PASS
- R132 (sprint 4 / 2026-07-02): PASS — consistent across sprints

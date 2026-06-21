# Package Install Proof — FODG
# Sprint: package-install-proof-fodg-20260618
# Date: 2026-06-18
# Skill: /package-install-proof v1.2

## NDJSON — WHEEL_MISSING

NDJSON is not in `packaging/python/package-matrix.yaml`. No wheel available.
Result: WHEEL_MISSING — skipped. Package matrix must be extended to cover NDJSON.

---

## FODG — Install Proof

| Field | Value |
|-------|-------|
| Package | aspose-format-factory-fodg |
| Version | 0.1.0.dev0 |
| Wheel | `.local/package-builds/python-foss/aspose-format-factory-fodg/dist/aspose_format_factory_fodg-0.1.0.dev0-py3-none-any.whl` |
| Install command | `python -m pip install --user --force-reinstall <wheel>` |
| Install result | Successfully installed aspose-format-factory-fodg-0.1.0.dev0 |
| Install path | `C:\Users\prora\AppData\Roaming\Python\Python313\site-packages\fodg\` |

## Import Test

```
import fodg  →  OK
fodg.__file__  →  C:\Users\prora\AppData\Roaming\Python\Python313\site-packages\fodg\__init__.py
```

Import result: **OK**

## API Smoke Test

Sample file used: `samples/by-format/fodg/minimal-drawing.fodg`

| API Call | Result |
|----------|--------|
| `fodg.load(path)` | OK — returns dict with keys: mime_type, is_fodg, page_count, pages, shapes_total |
| `fodg.probe_fodg(path)` | True (valid FODG detected) |
| `fodg.get_page_count(model)` | 1 |
| `fodg.get_shapes(model)` | list, 0 shapes (minimal drawing has no shapes in model) |
| `fodg.get_all_text(model)` | `['Rectangle']` (page name) |

API Smoke Test: **PASS**

## Summary Table

| Package | Version | Import | API Smoke |
|---------|---------|--------|-----------|
| fodg | 0.1.0.dev0 | import fodg: OK | load/probe/get_page_count: PASS |
| ndjson | N/A | WHEEL_MISSING | SKIPPED |

## Notes

- Install requires `--user` flag on Windows (system site-packages access denied without admin rights)
- API note: `get_page_count()` and `get_shapes()` take the model dict (from `load()`), not a file path
- API note: `probe_fodg()` takes a file path (not model dict) and returns bool
- `poc-targets.yaml` installed_workflow status for FODG: update to PASS after this proof

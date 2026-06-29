# /inventory-format-dom

Scan a Python format source tree and produce a DOM baseline inventory.

## What This Command Does

1. Scans `src/python/<format-id>/` with AST-based inspection.
2. Records typed DOM classes, `spec_qname` coverage, factory methods, child accessors, traversal methods, mutation methods, serialization methods, and iterator files.
3. Writes a YAML baseline under `reports/dual-lane-deepening/dom-baselines/`.

## Command

```powershell
python tools/supervisor/dom_baseline_scanner.py --format <format-id>
```

Generate all FULL-format baselines:

```powershell
python tools/supervisor/dom_baseline_scanner.py --all-full
```

## Inputs

- `format_id`: Python format key such as `fods`, `fodt`, `ods`, or `odt`
- optional `output`: explicit YAML output path

## Outputs

- `reports/dual-lane-deepening/dom-baselines/<format-id>.yaml`
- JSON representation of the generated baseline on stdout

## Validation

```powershell
python -m pytest tests/supervisor/test_dom_baseline_scanner.py -q
```

## skill_id

inventory-format-dom

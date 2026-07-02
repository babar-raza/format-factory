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

## Required Inputs

- `format_id` — format identifier from the format registry

## Allowed Paths

- `tools/supervisor/dom_baseline_scanner.py`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no .NET product source mutation
- `src/python/**` — no Python product source mutation
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the DOM inventory cannot be produced for the format
- Stop if the execution would modify any file under src/

## Output Format

- YAML or JSON inventory file at the configured output path
- Summary counts: total scanned, found, flagged
- Per-item entries with classification and evidence

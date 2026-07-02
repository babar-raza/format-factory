# /generate-root-status

Detect root README drift and regenerate the system status summary block.

## What This Command Does

1. Collects metrics from canonical sources (package-matrix.yaml, maturity-trend.json, governance validators, oracle formats).
2. Compares current README.md numbers against canonical sources to detect drift.
3. Generates a summary block for splicing between `<!-- BEGIN:SYSTEM-STATUS-SUMMARY -->` markers.

## Command

```bash
python tools/readme_sync/generate_root_status.py --mode full
```

## Validation

```bash
python tools/readme_sync/generate_root_status.py --mode drift-only
python tools/readme_sync/generate_root_status.py --mode drift-only --json
```

## skill_id

generate-root-status

## Required Inputs

- `output_path` — file path where the output report should be written

## Allowed Paths

- `tools/readme_sync/generate_root_status.py`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no product source mutation
- `src/python/**` — no product source mutation
- `plans/strategic/**` — strategic plans are read-only
- `.supervisor/skill-registry.yaml` — skill registry is read-only here

## Stop Conditions

- Stop if the skill's mandatory validations cannot be completed
- Stop if any required input field is missing or invalid

## Output Format

- PASS / FAIL / PARTIAL verdict printed to stdout
- Per-item findings list with skill_id, issue, and severity
- Report file at `reports/` with structured YAML findings

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

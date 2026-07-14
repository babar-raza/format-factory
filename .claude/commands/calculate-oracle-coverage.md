---
version: "1.0"
last-updated: "2026-07-11"
phase-available: "all"
gate-required: null
created-by: TC-W1A-001
spec_qname_required: "false"
product_track: "oracle_execution"
---

# /calculate-oracle-coverage

Generate a per-format oracle coverage report showing PASS/FAIL/SKIP tallies for all registered formats.

## Prerequisites

1. **Oracle packages must exist** — `oracle/formats/<format_id>/oracle-package.yaml` for each registered format
2. **Oracle run summaries available** — `oracle/formats/<format_id>/reports/oracle-run-summary.json`

## Execution

```bash
# Generate coverage report from existing run summaries
python -c "
import json, yaml
from pathlib import Path
from datetime import datetime, timezone

reg = yaml.safe_load(Path('oracle/registry/format-oracle-registry.yaml').read_text())
fo = reg.get('format_oracles', [])
coverage = {}
for entry in fo:
    fmt = entry['format_id']
    rpt = Path(f'oracle/formats/{fmt}/reports/oracle-run-summary.json')
    if rpt.exists():
        data = json.loads(rpt.read_text())
        coverage[fmt] = {
            'pass': data.get('pass_count', 0),
            'fail': data.get('fail_count', 0),
            'skip': data.get('skip_count', 0),
            'verdict': data.get('verdict', 'UNKNOWN'),
        }
    else:
        coverage[fmt] = {'verdict': 'NO_SUMMARY'}

report = {
    'generated_at': datetime.now(timezone.utc).isoformat(),
    'total_formats': len(fo),
    'coverage': coverage,
}
Path('oracle/reports/oracle-coverage-report.json').write_text(json.dumps(report, indent=2))
print(f'Written oracle/reports/oracle-coverage-report.json ({len(coverage)} formats)')
"
```

## Output

- `oracle/reports/oracle-coverage-report.json` — per-format coverage tallies

## Mandatory Validations

- `coverage_report_exists`: File must be written successfully
- `all_registered_formats_covered`: All formats in format-oracle-registry.yaml must appear in the report

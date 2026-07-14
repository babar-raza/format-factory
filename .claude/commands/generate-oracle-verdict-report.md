---
version: "1.0"
last-updated: "2026-07-11"
phase-available: "all"
gate-required: null
created-by: TC-W1A-001
spec_qname_required: "false"
product_track: "oracle_execution"
---

# /generate-oracle-verdict-report

Aggregate all per-format oracle verdict summaries into a unified portfolio regression report.

## Execution

```bash
python -c "
import json, yaml
from pathlib import Path
from datetime import datetime, timezone

reg = yaml.safe_load(Path('oracle/registry/format-oracle-registry.yaml').read_text())
entries = reg.get('format_oracles', [])
summaries = {}
for entry in entries:
    fmt = entry['format_id']
    rpt = Path(f'oracle/formats/{fmt}/reports/oracle-run-summary.json')
    if rpt.exists():
        summaries[fmt] = json.loads(rpt.read_text())

all_pass = all(s.get('verdict') in ('ALL_PASS', 'PARTIAL_PASS') for s in summaries.values())
report = {
    'generated_at': datetime.now(timezone.utc).isoformat(),
    'total_formats': len(entries),
    'formats_with_summary': len(summaries),
    'portfolio_verdict': 'ALL_PASS' if all_pass else 'PARTIAL_FAIL',
    'per_format': summaries,
}
Path('oracle/reports/portfolio-regression-report.json').write_text(json.dumps(report, indent=2))
print('Verdict:', report['portfolio_verdict'], 'Formats:', len(summaries))
"
```

## Output

- `oracle/reports/portfolio-regression-report.json` — unified verdict across all formats

## Mandatory Validations

- `verdict_report_exists`: File must exist after execution
- `all_formats_present`: All formats from registry must appear in report (even with NO_SUMMARY)

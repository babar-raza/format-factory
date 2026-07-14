---
version: "1.0"
last-updated: "2026-07-11"
phase-available: "all"
gate-required: null
created-by: TC-W1A-001
spec_qname_required: "false"
product_track: "oracle_execution"
---

# /evaluate-roundtrip-oracle

Execute roundtrip oracle cases for a given format: write a document, read it back, compare values.

## Handoff Fields

| Field | Required | Description |
|---|---|---|
| `format_id` | Yes | Lowercase format identifier (e.g. `fods`, `ods`, `csv`) |
| `profile` | No | Filter to a specific oracle profile (e.g. `ROUNDTRIP`) |

## Execution

```bash
# Run roundtrip profile cases
python tools/oracle/execute_oracle.py --format <format_id> --profile ROUNDTRIP

# Check roundtrip results
python -c "
import json
from pathlib import Path
rpt = json.loads(Path('oracle/formats/<format_id>/reports/oracle-run-summary.json').read_text())
rt_cases = [v for v in rpt.get('verdicts', []) if 'rt' in v.get('case_id', '')]
print(f'Roundtrip cases: {len(rt_cases)}')
for c in rt_cases:
    print(f'  {c[\"case_id\"]}: {c[\"result\"]}')
"
```

## What Roundtrip Tests Validate

1. Write a document with known properties using the product's writer API
2. Read the written document back using the product's reader API
3. Compare: every written property must equal the read-back value
4. Compare: file must be well-formed according to the format specification

## Mandatory Validations

- `roundtrip_cases_pass`: All ROUNDTRIP-profile oracle cases must show `result: PASS`
- `no_data_loss`: No property written must be absent or modified when read back

## Evidence Requirements

- Oracle run summary at `oracle/formats/<format_id>/reports/oracle-run-summary.json`
- At least one case with `case_id` containing `rt` or `roundtrip`

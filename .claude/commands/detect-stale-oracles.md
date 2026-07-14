---
version: "1.0"
last-updated: "2026-07-11"
phase-available: "all"
gate-required: null
created-by: TC-W1A-001
spec_qname_required: "false"
product_track: "oracle_execution"
---

# /detect-stale-oracles

Detect stale oracle packages by comparing current corpus file hashes against stored `input_hash` values.

## When to Use

Run before a governance sprint or oracle validation to ensure oracle cases are still testing the current corpus files.

## Execution

```bash
python -c "
import json, yaml, hashlib
from pathlib import Path
from datetime import datetime, timezone

stale = []
reg = yaml.safe_load(Path('oracle/registry/format-oracle-registry.yaml').read_text())
for entry in reg.get('format_oracles', []):
    pkg_path = Path(entry.get('oracle_package', ''))
    if not pkg_path.exists():
        continue
    pkg = yaml.safe_load(pkg_path.read_text())
    for case in pkg.get('cases', []):
        for ref in case.get('corpus_refs', []):
            sample = ref.get('sample_path', '')
            stored_hash = ref.get('input_hash', '')
            if not sample or not stored_hash:
                continue
            sp = Path(sample) if Path(sample).is_absolute() else Path(entry.get('oracle_package','')).parent / sample
            if not sp.exists():
                stale.append({'format': entry['format_id'], 'case': case['case_id'], 'issue': 'sample_missing', 'path': str(sp)})
                continue
            actual = hashlib.sha256(sp.read_bytes()).hexdigest()[:16]
            if actual != stored_hash and stored_hash:
                stale.append({'format': entry['format_id'], 'case': case['case_id'], 'issue': 'hash_mismatch', 'stored': stored_hash, 'actual': actual})

report = {'generated_at': datetime.now(timezone.utc).isoformat(), 'stale_count': len(stale), 'stale': stale}
Path('oracle/reports/stale-oracle-report.json').write_text(json.dumps(report, indent=2))
print(f'Stale count: {len(stale)}')
"
```

## Output

- `oracle/reports/stale-oracle-report.json` — list of stale cases with issue detail

## Mandatory Validations

- `stale_report_exists`: File must be written

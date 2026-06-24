---
version: "1.0"
last-updated: "2026-06-24"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same transcripts produce same index (stable sort by timestamp)"
loc_budget: "<40 lines inline Python"
test_path: "tests/supervisor/test_collect_skill_execution_receipts.py"
---

# /collect-skill-execution-receipts

Scan `.local/transcripts/` for skill execution transcript JSONs; aggregate into
a unified receipt index with status classification.

## Purpose

Produce a single consolidated index of all skill execution receipts for audit and
compliance verification. Enables the compliance proof in Pilot H.

## Steps

1. Scan `.local/transcripts/` for `*.json` files
2. For each file, extract: skill_id, verdict, completed_at, git_head (if present)
3. Sort by completed_at (stable)
4. Write index to `.supervisor/skill-execution-receipt-index.yaml`

```python
import json, yaml
from pathlib import Path
_REPO = Path.cwd()
transcripts_dir = _REPO / '.local' / 'transcripts'
receipts = []
if transcripts_dir.exists():
    for f in sorted(transcripts_dir.glob('*.json')):
        try:
            data = json.loads(f.read_text(encoding='utf-8', errors='replace'))
            receipts.append({'file': f.name, 'skill_id': data.get('skill_id', 'unknown'),
                             'verdict': data.get('verdict', 'unknown'),
                             'completed_at': data.get('completed_at', ''),
                             'git_head': data.get('git_head', '')})
        except Exception as exc:
            receipts.append({'file': f.name, 'skill_id': 'parse_error', 'error': str(exc)})
receipts.sort(key=lambda x: x.get('completed_at', ''))
out = {'generated_by': 'collect-skill-execution-receipts', 'total_receipts': len(receipts),
       'receipts': receipts}
dest = _REPO / '.supervisor' / 'skill-execution-receipt-index.yaml'
dest.write_text(yaml.dump(out, default_flow_style=False), encoding='utf-8')
print(f"Collected {len(receipts)} receipts -> {dest}")
```

## Output

`.supervisor/skill-execution-receipt-index.yaml` with:
- `total_receipts`
- `receipts[]`: file, skill_id, verdict, completed_at, git_head

## Allowed Paths

- `.supervisor/skill-execution-receipt-index.yaml` (write)
- `.local/transcripts/` (read)

## Forbidden Paths

- `src/**`
- Writing transcripts

## Constraints

- Read-only except for output file
- Parse errors: include error entry but continue scanning

## Idempotency Contract

Same transcript files produce same index (stable sort by completed_at). File overwritten.

## Error Handling

Missing `.local/transcripts/`: write empty index with `total_receipts: 0`. Exit 0.

## Usage

```
/collect-skill-execution-receipts
```

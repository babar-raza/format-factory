---
version: "1.0"
last-updated: "2026-07-11"
phase-available: "all"
gate-required: null
created-by: TC-SGOV-W4-002
spec_qname_required: "false"
product_track: "governance"
---

# /run-governance-validators

Run all 170 registered governance validators against an evidence declaration.
Calls `tools/supervisor/governance_validator_runner.py`. Returns composite
pass/warn/fail counts and blocks_sprint flag.

## Handoff Fields (required)

| Field | Description |
|---|---|
| `declaration_path` | Path to the evidence-declaration.yaml file |

## Handoff Fields (optional)

| Field | Description |
|---|---|
| `repo_root` | Repo root path (defaults to auto-detected) |

## Execution

```python
import yaml, sys
from pathlib import Path
sys.path.insert(0, 'tools/supervisor')
from governance_validator_runner import run_all_governance_validators
decl = yaml.safe_load(Path('<declaration_path>').read_text(encoding='utf-8'))
result = run_all_governance_validators(decl, repo_root=Path('.'))
print(result['summary'])
```

Or via autonomous_cycle which calls this internally.

## Output

Dict with:
- `all_pass: bool`
- `blocks_sprint: bool`
- `fail_count`, `warn_count`, `pass_count`
- `expected_count: 170`
- `validators: [...]` — per-validator results

## Mandatory Validations

- `declaration_readable`: declaration_path must be readable
- `all_validators_ran`: ran_count should approach expected_count (170)

## Reference

`tools/supervisor/governance_validator_runner.py` — runs all V1-V-SGF-002.

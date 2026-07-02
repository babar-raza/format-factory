---
version: "1.0"
last-updated: "2026-06-24"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Running twice produces identical file (sort is stable, defaults are idempotent)"
loc_budget: "<70 lines"
test_path: "tests/supervisor/test_normalize_skill_registry.py"
---

# /normalize-skill-registry

Sort entries in `.supervisor/skill-registry.yaml` by `skill_id`, fill missing optional
fields with typed defaults, remove duplicate entries.

## Purpose

Ensure the skill registry is in a consistent, sortable, deduplicated state for reliable
machine lookups. Backup is mandatory before any write.

## Steps

1. Read `.supervisor/skill-registry.yaml` — abort on YAML parse failure
2. Backup to `.local/archive/skill-registry-pre-normalize.yaml`
3. Deduplicate entries by `skill_id` (keep first occurrence)
4. Sort entries alphabetically by `skill_id`
5. Fill optional fields with typed defaults:
   - `implementation_paths: []`
   - `test_paths: []`
   - `idempotency: "not_specified"`
6. Write back to `.supervisor/skill-registry.yaml`
7. Validate post-write: parse the file again — if parse fails, restore from backup and raise

```python
import yaml, shutil
from pathlib import Path
_REPO = Path.cwd()
src = _REPO / '.supervisor/skill-registry.yaml'
bak = _REPO / '.local/archive/skill-registry-pre-normalize.yaml'
bak.parent.mkdir(parents=True, exist_ok=True)
data = yaml.safe_load(src.read_text(encoding='utf-8', errors='replace'))
shutil.copy(src, bak)
seen = {}
for s in data.get('skills', []):
    sid = s.get('skill_id', '')
    if sid and sid not in seen:
        seen[sid] = s
data['skills'] = sorted(seen.values(), key=lambda x: x.get('skill_id', ''))
for s in data['skills']:
    s.setdefault('implementation_paths', [])
    s.setdefault('test_paths', [])
    s.setdefault('idempotency', 'not_specified')
text = yaml.dump(data, default_flow_style=False, allow_unicode=True)
yaml.safe_load(text)  # validate before write
src.write_text(text, encoding='utf-8')
print(f"Normalized {len(data['skills'])} skills")
```

## Output

Updated `.supervisor/skill-registry.yaml` (sorted, deduplicated, defaults filled).
Backup at `.local/archive/skill-registry-pre-normalize.yaml`.

## Allowed Paths

- `.supervisor/skill-registry.yaml` (read + write)
- `.local/archive/skill-registry-pre-normalize.yaml` (write backup)

## Forbidden Paths

- `src/**`
- Never removes skill entries; never changes `skill_id` values

## Constraints

- Backup MUST be written before any modification
- On post-write YAML parse failure: restore from backup and raise

## Idempotency Contract

Running twice produces identical file (stable sort; idempotent defaults).

## Error Handling

Pre-write parse failure: abort immediately; do not modify file.
Post-write parse failure: restore from backup; raise.

## Usage

```
/normalize-skill-registry
```

## Output Format

- Structured result written to `reports/` in YAML or JSON format
- Human-readable summary printed to stdout
- Verdict: PASS / FAIL with per-item evidence

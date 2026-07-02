---
version: "1.0"
last-updated: "2026-06-24"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same plan files produce same recommendations; read-only scan"
loc_budget: "<60 lines inline Python"
test_path: "tests/supervisor/test_backfill_task_skill_ownership.py"
---

# /backfill-task-skill-ownership

Scan all plan files in `plans/` and `reports/supervisor/next-sprint.md` for mutating task
descriptions lacking `skill_ids` or `required_capabilities`; produce backfill recommendations.

## Purpose

Identify governed tasks that are missing explicit skill bindings. These are candidates for
backfilling with a `skill_ids:` field to improve routing compliance.

## Steps

1. Scan all `.md` files in `plans/` and `reports/supervisor/next-sprint.md`
2. For each task-like line (contains "Implement", "Create", "Fix", "Add", "Migrate", "Update"):
   - Check if adjacent lines contain `skill_ids:` or `required_capabilities:`
   - If not: flag as MISSING_SKILL_BINDING with the task text
3. Write recommendations to `.supervisor/taskcard-skill-backfill.yaml`

```python
import yaml, re
from pathlib import Path
_REPO = Path.cwd()
task_re = re.compile(r'^\s*[-*]?\s*(Implement|Create|Fix|Add|Migrate|Update)\s+', re.I)
results = []
files = list((_REPO / 'plans').glob('*.md')) + [_REPO / 'reports/supervisor/next-sprint.md']
for f in files:
    if not f.exists():
        continue
    lines = f.read_text(encoding='utf-8', errors='replace').splitlines()
    for i, line in enumerate(lines):
        if task_re.match(line):
            ctx = '\n'.join(lines[max(0,i-1):i+3])
            if 'skill_ids' not in ctx and 'required_capabilities' not in ctx:
                results.append({'file': str(f.relative_to(_REPO)), 'line': i+1,
                                 'task': line.strip(), 'recommendation': 'Add skill_ids field'})
out = {'generated_by': 'backfill-task-skill-ownership', 'total_unbound': len(results), 'items': results}
dest = _REPO / '.supervisor/taskcard-skill-backfill.yaml'
dest.write_text(yaml.dump(out, default_flow_style=False), encoding='utf-8')
print(f"Found {len(results)} tasks missing skill binding -> {dest}")
```

## Output

`.supervisor/taskcard-skill-backfill.yaml` with:
- `total_unbound`: count of tasks without skill binding
- `items[]`: file, line, task text, recommendation

## Allowed Paths

- `.supervisor/taskcard-skill-backfill.yaml` (write)
- `plans/*.md` (read)
- `reports/supervisor/next-sprint.md` (read)

## Forbidden Paths

- `src/**`
- NEVER modifies plan files — produces recommendations only

## Constraints

- Read-only scan; produces recommendations only
- Does NOT modify plan files

## Idempotency Contract

Same plan files produce same recommendations (deterministic regex match).

## Error Handling

On file read error: log to stderr and continue scanning.

## Usage

```
/backfill-task-skill-ownership
```

## Output Format

- YAML or JSON inventory file at the configured output path
- Summary counts: total scanned, found, flagged
- Per-item entries with classification and evidence

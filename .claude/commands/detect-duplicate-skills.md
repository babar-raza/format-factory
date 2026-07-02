---
version: "1.0"
last-updated: "2026-06-24"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same registry produces same report; read-only"
loc_budget: "<50 lines inline Python"
test_path: "tests/supervisor/test_detect_duplicate_skills.py"
---

# /detect-duplicate-skills

Compare `purpose` strings and `command_file` paths across all registered skills;
flag DUPLICATE (identical purpose + file) or OVERLAPPING (high token similarity).

## Purpose

Detect redundant skills that implement the same or highly similar operations. Duplicates
should be merged; overlapping skills need ownership boundary clarification.

## Steps

1. Read `.supervisor/skill-registry.yaml`
2. For each pair of active skills, compare:
   - `command_file`: identical path → DUPLICATE (same file)
   - `purpose`: >80% token overlap → OVERLAPPING
3. Write report to `.supervisor/duplicate-skill-report.yaml`

```python
import yaml
from pathlib import Path
_REPO = Path.cwd()
data = yaml.safe_load((_REPO / '.supervisor/skill-registry.yaml').read_text(encoding='utf-8', errors='replace'))
skills = [s for s in data.get('skills', []) if s.get('status') != 'deprecated']
duplicates, overlapping = [], []
for i, a in enumerate(skills):
    for b in skills[i+1:]:
        if a.get('command_file') and a.get('command_file') == b.get('command_file'):
            duplicates.append({'skill_a': a['skill_id'], 'skill_b': b['skill_id'], 'reason': 'identical_command_file'})
        else:
            ta = set(str(a.get('purpose', '')).lower().split())
            tb = set(str(b.get('purpose', '')).lower().split())
            if ta and tb:
                overlap = len(ta & tb) / max(len(ta | tb), 1)
                if overlap > 0.8:
                    overlapping.append({'skill_a': a['skill_id'], 'skill_b': b['skill_id'], 'overlap': round(overlap, 2)})
out = {'generated_by': 'detect-duplicate-skills', 'duplicate_count': len(duplicates),
       'overlapping_count': len(overlapping), 'duplicates': duplicates, 'overlapping': overlapping}
dest = _REPO / '.supervisor/duplicate-skill-report.yaml'
dest.write_text(yaml.dump(out, default_flow_style=False), encoding='utf-8')
print(f"Found {len(duplicates)} DUPLICATE, {len(overlapping)} OVERLAPPING -> {dest}")
```

## Output

`.supervisor/duplicate-skill-report.yaml` with:
- `duplicate_count`, `overlapping_count`
- `duplicates[]`: pairs with identical command_file
- `overlapping[]`: pairs with >80% token overlap in purpose

## Allowed Paths

- `.supervisor/duplicate-skill-report.yaml` (write)
- `.supervisor/skill-registry.yaml` (read)

## Forbidden Paths

- `src/**`
- Modifying skill-registry.yaml

## Constraints

- Read-only except for output file
- Similarity threshold: >80% token overlap (Jaccard) for OVERLAPPING

## Idempotency Contract

Same registry produces same report. No randomness in comparison.

## Error Handling

On parse failure: write error to output; exit 0.

## Usage

```
/detect-duplicate-skills
```

## Output Format

- Structured result written to `reports/` in YAML or JSON format
- Human-readable summary printed to stdout
- Verdict: PASS / FAIL with per-item evidence

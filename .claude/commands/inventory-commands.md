---
version: "1.0"
last-updated: "2026-06-24"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Rerun produces identical YAML if command-registry.yaml unchanged; file is overwritten not appended"
loc_budget: "<40 lines inline Python"
test_path: "tests/supervisor/test_inventory_commands.py"
---

# /inventory-commands

Read `.claude/commands/command-registry.yaml` and produce a flattened command inventory
with status classification.

## Purpose

Enumerate all registered commands, classify by status (active/deprecated/experimental),
and write a flat inventory file for quick audit and routing validation.

## Steps

1. Read `.claude/commands/command-registry.yaml`
2. For each command entry, extract: command_id, skill_id, status, command_file
3. Classify: ACTIVE, DEPRECATED, EXPERIMENTAL, or UNKNOWN
4. Count by classification
5. Write inventory to `.supervisor/command-inventory.yaml`

```python
import yaml, sys
from pathlib import Path
_REPO = Path(__file__).resolve().parent.parent.parent
data = yaml.safe_load((_REPO / '.claude/commands/command-registry.yaml').read_text(encoding='utf-8', errors='replace')) or {}
entries = []
counts = {'ACTIVE': 0, 'DEPRECATED': 0, 'EXPERIMENTAL': 0, 'UNKNOWN': 0}
for e in data.get('commands', []):
    status = e.get('status', 'UNKNOWN').upper()
    key = status if status in counts else 'UNKNOWN'
    counts[key] += 1
    entries.append({'command_id': e.get('command_id') or e.get('skill_id', ''),
                    'status': key, 'command_file': e.get('command_file', '')})
out = {'generated_by': 'inventory-commands', 'status': 'complete',
       'total_commands': len(entries), 'counts': counts, 'commands': entries}
dest = _REPO / '.supervisor' / 'command-inventory.yaml'
dest.write_text(yaml.dump(out, default_flow_style=False), encoding='utf-8')
print(f"Inventoried {len(entries)} commands -> {dest}")
```

## Output

`.supervisor/command-inventory.yaml` with fields: total_commands, counts (by status), commands list.

## Allowed Paths

- `.supervisor/command-inventory.yaml` (write)
- `.claude/commands/command-registry.yaml` (read)

## Forbidden Paths

- `src/**`
- `.supervisor/skill-registry.yaml` (read-only)

## Constraints

- Read-only except for inventory output file
- On malformed YAML: write `status: error` with error message; do not raise

## Idempotency Contract

Rerun with unchanged command-registry.yaml produces identical output. File is overwritten, not appended.

## Error Handling

If command-registry.yaml is malformed: write `status: error` to output; log to stderr; exit 0.

## Usage

```
/inventory-commands
```

## Output Format

- YAML or JSON inventory file at the configured output path
- Summary counts: total scanned, found, flagged
- Per-item entries with classification and evidence

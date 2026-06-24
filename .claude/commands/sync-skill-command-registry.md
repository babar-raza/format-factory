---
version: "1.0"
last-updated: "2026-06-24"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Second pass after first pass reports zero items repaired and zero status drift"
loc_budget: "<95 lines"
test_path: "tests/supervisor/test_sync_skill_command_registry.py"
---

# /sync-skill-command-registry

Detect and repair all discrepancies between:
1. `.supervisor/skill-registry.yaml` skill entries
2. `.claude/commands/command-registry.yaml` entries
3. `.claude/commands/*.md` files on disk
4. `.supervisor/work-type-skill-map.yaml` skill_id references
5. `.supervisor/capability-routing-registry.yaml` preferred_skill_ids

## Purpose

Keep the three registries in sync. Skills added to skill-registry.yaml should
automatically appear in command-registry.yaml. Status changes should propagate.
Orphan files and broken pointers should be flagged.

**Run after ANY sprint that adds, modifies, or deprecates skills.**

## Steps

1. Load skill-registry.yaml, command-registry.yaml, and scan `.claude/commands/*.md`
2. Detect: orphan .md files, missing command-registry entries, status drift, broken pointers, orphan entries
3. Auto-repair: add missing command-registry entries; sync status fields (never delete)
4. Write sync report to `.supervisor/skill-command-registry-sync-report.yaml`

```bash
python tools/supervisor/sync_skill_command_registry.py
```

## Sync Rules

| Check | Auto-repair? |
|-------|-------------|
| Orphan .md files (not in skill-registry) | Flag UNREGISTERED_COMMAND (no auto-add) |
| Missing command-registry entry | Auto-add with status from skill-registry |
| Status drift (skill newer) | Auto-sync status in command-registry |
| Broken command_file pointer | Flag BROKEN_POINTER (no auto-delete) |
| Orphan command-registry entry | Flag ORPHAN_COMMAND_ENTRY (no auto-delete) |

## Output

`.supervisor/skill-command-registry-sync-report.yaml` with:
- `auto_repaired`: count of items fixed
- `status_drift[]`: status changes applied
- `flags[]`: non-blocking issues
- `overall_verdict`: PASS | WARN

## Allowed Paths

- `.supervisor/skill-command-registry-sync-report.yaml` (write)
- `.claude/commands/command-registry.yaml` (read + write — auto-repair only)
- `.local/archive/command-registry-pre-sync.yaml` (write backup before any change)

## Forbidden Paths

- `src/**`
- `.supervisor/skill-registry.yaml` (read-only — never modified by this skill)
- `.claude/commands/*.md` files (read-only)

## Constraints

- Never deletes any entries from any registry
- If command-registry.yaml is malformed YAML: abort without writing; log error
- Backup written to `.local/archive/` before any modification to command-registry.yaml

## Idempotency Contract

Running twice on unchanged inputs: second run reports `auto_repaired: 0` and
`status_drift: []`. This is the idempotency proof (Gate V11).

## Error Handling

Malformed command-registry.yaml: abort immediately; write error to sync report; exit non-zero.

## Usage

```
/sync-skill-command-registry
```

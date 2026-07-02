---
version: "1.0"
last-updated: "2026-06-24"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Rerun updates counts; stable skill_id as key; never duplicates entries"
loc_budget: "<90 lines"
test_path: "tests/supervisor/test_skill_inventory.py"
---

# /inventory-skills

Scan `.supervisor/skill-registry.yaml` and `.claude/commands/` and produce a complete
mechanism inventory. Supports partial-state resume.

## Purpose

Enumerate all registered skills, detect unregistered command files, and produce a
complete snapshot of the skill mechanism landscape. Used as a pre-gate audit step
before any skill registration sprint.

## Steps

1. Read `.supervisor/skill-registry.yaml` — collect all registered skills
2. Scan `.claude/commands/*.md` — find unregistered command files
3. If `.supervisor/skill-inventory.yaml` exists with `status: partial`:
   - Read existing `completed_skills` entries
   - Resume from remaining (do not re-scan already inventoried skills)
4. Merge prior + new entries; sort by `skill_id`
5. Write inventory to `.supervisor/skill-inventory.yaml` with `status: complete`

```bash
python tools/supervisor/skill_inventory.py
```

## Output

`.supervisor/skill-inventory.yaml` with:
- `status`: complete
- `total_skills`: count of all entries
- `resumed_from_partial`: true if resumed from partial state
- `skills[]`: per-skill entry with skill_id, status, mechanism_type, command_file, command_file_exists

## Allowed Paths

- `.supervisor/skill-inventory.yaml` (read + write)
- `.supervisor/skill-registry.yaml` (read)
- `.claude/commands/` (read)

## Forbidden Paths

- `src/**`
- Modifying skill-registry.yaml or command-registry.yaml

## Constraints

- Read-only except for inventory output file
- Partial-state detection: checks for `status: partial` sentinel in existing output
- Never produces duplicate entries (stable skill_id as key)

## Idempotency Contract

Running twice produces identical `total_skills` count and `skills[]` list.
On first run: status: complete. On rerun with same inputs: identical output.

## Partial-State Recovery

If `.supervisor/skill-inventory.yaml` exists with `status: partial`:
- Reads `skills[]` from partial file as `prior_entries`
- Skips skill_ids already in prior_entries
- Completes remaining and writes `status: complete`
- No duplicate entries in output

## Error Handling

On skill-registry.yaml parse failure: exit non-zero; log to stderr.
On individual skill read error: skip and continue.

## Usage

```
/inventory-skills
```

## Output Format

- YAML or JSON inventory file at the configured output path
- Summary counts: total scanned, found, flagged
- Per-item entries with classification and evidence

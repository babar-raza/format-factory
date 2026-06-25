---
version: "1.0"
last-updated: "2026-06-25"
phase-available: "all"
gate-required: null
skill-id: preflight-skill-entry
---

# /preflight-skill-entry

Validate a proposed skill-registry.yaml entry **before** insertion to prevent
write-time errors. Catches missing required fields (`command`, `purpose`, `status`,
`skill_id`) and invalid status values before they reach the registry.

## When to Use

Run this before adding ANY new entry to `.supervisor/skill-registry.yaml`.
This is Rule GH-001 enforcement (SKILL-GOVERNANCE-REPAIR-001).

## Usage

```
python tools/supervisor/preflight_skill_entry.py <skill_yaml_file>
python tools/supervisor/preflight_skill_entry.py --inline "skill_id: foo\ncommand: /foo\npurpose: ...\nstatus: active\n"
```

## Exit Codes

- **0** — Entry is valid; safe to insert into skill-registry.yaml
- **1** — Validation failed; fix the listed errors before inserting

## Error Types

- `FIELD_MISSING` — A required field (`skill_id`, `purpose`, `command`, `status`) is absent or empty
- `STATUS_INVALID` — The `status` value is not in `{active, deprecated, experimental, retired, deferred}`
- `COMMAND_FILE_MISSING` — `command_file` is specified but the file does not exist on disk

## Required Fields (GH-001)

Every skill-registry entry MUST have:
- `skill_id` — unique snake-case identifier
- `purpose` — non-empty description of the skill's function
- `command` — the slash-command name (e.g., `/my-skill`)
- `status` — one of the valid lifecycle states

## Governance Rule

**GH-001 (SKILL-GOVERNANCE-REPAIR-001):** Before adding any entry to
`skill-registry.yaml`, run this preflight validator. A passing preflight
is a prerequisite for taskcard closure on any skill-adding work.

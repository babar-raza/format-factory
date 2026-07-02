# /create-taskcard

Create a new taskcard from the standard template with all required fields.

## Usage

```
/create-taskcard <taskcard_id> <title> [format_id]
```

Examples:
- `/create-taskcard TC-0005 "Implement LLM endpoint client" null`
- `/create-taskcard TC-FODS-API-001 "Add FODS cell merge API" fods`

## What This Command Does

1. **Validate ID format** — Confirm `taskcard_id` follows `TC-NNNN` or `TC-FORMAT-TYPE-NNN` pattern
2. **Check for duplicates** — Scan `taskcards/` to confirm no file with same ID exists
3. **Create taskcard file** — `taskcards/<taskcard_id>.md` with full front-matter and required sections
4. **Register in index** — Append entry to `taskcards/index.yaml` (create if missing)

## Required Inputs

- `taskcard_id` — Unique identifier (e.g., `TC-0005`, `TC-FODS-API-001`)
- `title` — Short descriptive title (quoted string)
- `format_id` — Format this taskcard targets (`null` for infrastructure)

## Steps

```
1. Validate taskcard_id format
2. Check taskcards/<taskcard_id>.md does not exist
3. Create taskcards/<taskcard_id>.md from template below
4. Append to taskcards/index.yaml:
   - id: <taskcard_id>
     title: <title>
     status: not_started
     format: <format_id>
     created: <date>
```

## Template

```markdown
---
artifact_id: <taskcard_id>
artifact_type: taskcard
path: taskcards/<taskcard_id>.md
format_id: <format_id>
product_family: null
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: <date>
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: <title>
---

# <taskcard_id>: <title>

**Phase:** TBD
**Status:** not_started
**Owner:** TBD
**Created:** <date>
**Last updated:** <date>
**Blocking:** TBD
**Blocked by:** TBD
**Format:** <format_id>
**Gate:** TBD

---

## Objective

[Describe what this taskcard accomplishes and why it matters]

---

## Scope

### In scope
-

### Out of scope
-

---

## Acceptance Criteria

- [ ]
- [ ]

---

## Evidence Required

- Test run showing 0 failures
- Changed files listed in evidence declaration
```

## Validation

Complete when:
- `taskcards/<taskcard_id>.md` exists with front-matter and all sections
- Entry appears in `taskcards/index.yaml`

## Allowed Paths

- `plans/ — plan files (read/write)`
- `reports/ — evidence reports (write)`
- `.local/evidences/ — evidence declarations (write)`

## Forbidden Paths

- `src/net/**` — no product source mutation during planning
- `src/python/**` — no product source mutation during planning
- `registry/format-registry.yaml` — format registry is read-only here

## Stop Conditions

- Stop if the skill's mandatory validations cannot be completed
- Stop if any required input field is missing or invalid

---
version: "1.0"
last-updated: "2026-07-11"
phase-available: "all"
gate-required: null
created-by: TC-SGOV-W4-002
spec_qname_required: "false"
product_track: "governance"
---

# /validate-evidence-declaration

Validate an evidence declaration YAML against the sprint executor schema.
Required as CLAUDE.md §Sprint Closeout step 1b before submission to
autonomous-cycle. The `--repair` flag auto-corrects common issues (markdown
fences, banned fields, type mismatches).

## Handoff Fields (required)

| Field | Description |
|---|---|
| `declaration_path` | Path to the evidence-declaration.yaml file |

## Handoff Fields (optional)

| Field | Description |
|---|---|
| `repair` | If true, pass `--repair` flag to auto-correct issues |

## Execution

```
python tools/supervisor/sprint_executor_validate.py \
  <declaration_path> [--repair]
```

## Output

JSON result on stdout:
- `passed: true/false`
- `errors: [...]`
- `repairs: [...]` (if --repair)

Exit 0 = PASS; non-zero = errors present.

## Mandatory Validations

- `declaration_exists`: declaration_path must point to a readable file
- `exit_code_0`: expect exit 0 after successful validation (or after --repair)

## Reference

CLAUDE.md §Sprint Closeout step 1b.

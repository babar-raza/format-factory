---
version: "1.0"
last-updated: "2026-07-11"
phase-available: "all"
gate-required: null
created-by: TC-SGOV-W4-002
spec_qname_required: "false"
product_track: "governance"
---

# /build-supervisor-packet

Generate a supervisor review packet from an evidence declaration. Calls
`tools/supervisor/generate_supervisor_packet.py` which reads the declaration
and produces structured supervisor review artifacts in `reports/supervisor/`.

## Handoff Fields (required)

| Field | Description |
|---|---|
| `declaration_path` | Path to the evidence-declaration.yaml file |

## Execution

```
python tools/supervisor/generate_supervisor_packet.py \
  --declaration <declaration_path>
```

## Output

- Supervisor packet written to `reports/supervisor/`
- Includes: next-sprint.md, evidence-review.json, work-item-grades.json

## Mandatory Validations

- `declaration_readable`: declaration_path must point to a readable file
- `reports_written`: at least one file written to reports/supervisor/

## Notes

Note: `build_declaration_review_package.py` (GOVERNED via `/build-evidence-bundle`) is a
separate tool that produces a ZIP artifact for human review. This skill wraps
`generate_supervisor_packet.py` which produces the machine-readable supervisor state.

## Reference

CLAUDE.md §Sprint Closeout step 4.

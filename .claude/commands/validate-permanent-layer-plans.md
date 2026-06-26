---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /validate-permanent-layer-plans

Validate all permanent layer plan files for structural completeness.
Each plan file must have the required metadata block and key sections.

## Required Sections (checked for presence)

- `## 2. Authority and Purpose`
- `## 9. Current Implementation`
- `## 14. Gap Register`
- `## 36. Current Session Handoff`
- `## 39. Change History`
- Metadata YAML block (layer_id, canonical_name, status, maturity_current, maturity_target)

## Execution

1. Scan `plans/layers/` for all `*.md` layer files (excluding master.md)
2. For each file, check for required sections
3. Validate metadata block fields are present and non-null
4. Report missing sections and invalid metadata

## Output

```yaml
validation_result:
  total_files: 27
  valid: 25
  invalid:
    - file: plans/layers/corpus-layer.md
      missing_sections: ["## 36. Current Session Handoff"]
      invalid_fields: []
  verdict: WARN
```

## Mandatory Validations

- This skill is read-only — no writes occur
- Missing sections emit WARN per file; never FAIL (allows stub files to exist)

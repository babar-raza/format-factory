---
version: "1.0"
last-updated: "2026-07-11"
phase-available: "all"
gate-required: null
created-by: TC-W1A-001
spec_qname_required: "false"
product_track: "oracle_execution"
---

# /onboard-future-format-oracle

Scaffold the minimum oracle obligation for a newly registered format.

## Handoff Fields

| Field | Required | Description |
|---|---|---|
| `format_id` | Yes | Lowercase format identifier (e.g. `abw`, `fodg`) |

## Steps

1. Create `oracle/formats/<format_id>/` directory
2. Copy the minimal oracle-package.yaml template from `oracle/formats/tsv/oracle-package.yaml`
3. Update: `format_id`, `format_name`, `oracle_id`, `authority.specification_refs`
4. Add at least one `valid` case with a known sample file
5. Register an executor stub in `tools/oracle/execute_oracle.py`
6. Add the format to `oracle/registry/format-oracle-registry.yaml`
7. Run `/run-oracle` to verify the scaffold produces at least 1 PASS

## Oracle Package Template (minimal)

```yaml
format_id: <format_id>
format_name: <Format Name>
oracle_id: oracle-<format_id>-v1
schema_version: "1.0"
authority:
  specification_refs:
    - "<Specification reference>"
cases:
  - case_id: <format_id>-valid-001
    profile: PARSE_VALIDITY
    description: "Minimal valid <format> document loads without error"
    corpus_refs:
      - sample_path: samples/by-format/<format_id>/minimal.<format_id>
    expected_properties:
      loaded: true
```

## Mandatory Validations

- `oracle_package_valid`: oracle-package.yaml must parse as valid YAML with required fields
- `executor_registered`: `execute_<format_id>_valid_case()` must be importable from execute_oracle.py

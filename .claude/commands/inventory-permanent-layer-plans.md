---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /inventory-permanent-layer-plans

List all layer plan files in `plans/layers/` and report their status, maturity,
and completeness. Read-only audit skill.

## Execution

1. Scan `plans/layers/` for `*.md` files (excluding master.md and temporary files)
2. Read the metadata block from each file
3. Compare against `plans/layers/index.yaml` for consistency
4. Report summary table with: layer_id, status, maturity_current, maturity_target, next_task_id

## Output

```
Layer Inventory (plans/layers/)
================================
L01  specification-authority-layer    IN_PROGRESS    M2→M5   TC-SAL-001
L02  qname-hierarchy-layer            ACTIVE         M4→M4   TC-QN-001
...
L27  format-language-obligation-layer NOT_ASSESSED   M1→M3   TC-OBL-001

Total: 27 layers | 5 ACTIVE | 18 IN_PROGRESS | 4 NOT_ASSESSED
```

## Mandatory Validations

- This skill is read-only — no writes occur
- If a plan file is missing a metadata block, flag it as MISSING_METADATA

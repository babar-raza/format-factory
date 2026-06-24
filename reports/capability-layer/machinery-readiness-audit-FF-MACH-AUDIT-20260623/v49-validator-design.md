# V49/V50 Validator Design
**Plan:** sorted-purring-stardust | **Taskcard:** TC-LANE-D | **Requirement:** REQ-LANE-D

## Current State: V49 EXISTS
- **Name:** validate_qname_structure
- **Location:** governance_validators.py:3028-3071
- **Mode:** WARN-only
- **Purpose:** Checks spec/ class files for spec_qname attribute presence
- **Tool dependency:** tools/validators/qname_structure_validator.py

## Proposed: V50 validate_spec_fact_refs_density (NEW)

### Purpose
Ensure PRODUCT_SOURCE items that add new classes have at least 1 spec_fact_ref in their evidence declaration. This is DISTINCT from V49 (which checks spec_qname in source code).

### Function Signature
```python
def validate_spec_fact_refs_density(declaration: dict, repo_root: Path | None = None) -> dict:
    """V50: Require ≥1 spec_fact_ref per new non-Compat/non-spec class in PRODUCT_SOURCE items.
    REWORK_REQUIRED mode (not hard block) — ramp to BLOCK after 3 sprints.
    """
```

### Logic
1. Filter: PRODUCT_SOURCE items only
2. For each item that adds a new class in src/python/ or src/net/ NOT under Compat/ or spec/:
3. Check: does evidence_artifacts or declaration contain at least 1 spec_fact_ref?
4. If missing: REWORK_REQUIRED (not hard block)
5. Compat/ classes are facades — excluded from check

### Insertion Point
- governance_validators_ext.py (overflow module, per established pattern)
- Register in governance_validator_runner.py

### Tests Required
1. Positive: PRODUCT_SOURCE item with spec_fact_ref → PASS
2. Negative: PRODUCT_SOURCE item without spec_fact_ref → REWORK_REQUIRED
3. Exclusion: New class in Compat/ → PASS (facades exempt)

### Ramp Schedule
- Sprint 1-3: REWORK_REQUIRED (warn + rework)
- Sprint 4+: BLOCK (hard block, no override)

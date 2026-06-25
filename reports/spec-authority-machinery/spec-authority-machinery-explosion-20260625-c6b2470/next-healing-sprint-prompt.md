# Next Healing Sprint Prompt — Phase A
## Spec Authority Layer Bypass Closure

Ready-to-paste prompt for the next execution agent. Execute Phase A of the healing roadmap.

---

## Mission

Close 3 critical bypasses that allow product sprints to proceed with zero spec authority:
1. TC-GUARD-001 OR logic bypass
2. V13 absent=no-op bypass
3. product_task_selector poc-targets-only bypass

Also: evidence schema repair (schema documentation, not enforcement yet).

---

## Context (Read Before Starting)

1. Read `reports/spec-authority-machinery/spec-authority-machinery-explosion-20260625-c6b2470/executive-diagnosis.md`
2. Read `reports/spec-authority-machinery/spec-authority-machinery-explosion-20260625-c6b2470/healing-roadmap.md`
3. Read `reports/spec-authority-machinery/spec-authority-machinery-explosion-20260625-c6b2470/machinery-bypass-ledger.json`

Key facts:
- FODS is production-quality (P6 for FACT-FODS-001) — do NOT modify FODS Compat/ code
- Tier 2 formats (Gnumeric, ABW, SYLK, DIF, TSV) are correctly P1/P2 — preserve their exception_classifications
- legacy_backfill exception (CSV, NDJSON, TOML, XCF, QOI) must be preserved in this sprint — sunset handled in Phase D

---

## Task A-001: TC-GUARD-001 AND Logic

**File**: `tools/supervisor/autonomous_cycle.py`
**Location**: Step 2d3, search for `gap_ledger_ref` and `TC-GUARD-001`

**Current code** (approximately):
```python
has_authority = (
    item.get("gap_ledger_ref") or
    item.get("capability_ref") or
    item.get("spec_fact_refs")
)
```

**Required change**:
```python
has_authority = bool(
    (item.get("gap_ledger_ref") or item.get("capability_ref")) and
    (item.get("spec_fact_refs") or item.get("exception_classification"))
)
```

**Migration note**: Any existing PRODUCT_SOURCE declaration without spec_fact_refs must add either:
- `spec_fact_refs: ["FACT-{FORMAT}-001"]` (for Tier 1 formats with P4+ authority), OR
- `exception_classification: {valid_exception}` (for Tier 2 formats)

**Test to add** (`tests/supervisor/test_tc_guard_001_enforce.py`):
```python
def test_guard001_blocks_gap_ledger_ref_only():
    item = {"item_type": "PRODUCT_SOURCE", "gap_ledger_ref": "GAP-TEST-001"}
    # should add to violations
    assert is_guard001_violation(item) == True

def test_guard001_passes_with_exception():
    item = {"item_type": "PRODUCT_SOURCE", "gap_ledger_ref": "GAP-TEST-001",
            "exception_classification": "no_public_spec_available"}
    assert is_guard001_violation(item) == False

def test_guard001_passes_with_spec_fact_refs():
    item = {"item_type": "PRODUCT_SOURCE", "gap_ledger_ref": "GAP-TEST-001",
            "spec_fact_refs": ["FACT-FODS-001"]}
    assert is_guard001_violation(item) == False
```

---

## Task A-002: V13 — Fire When spec_fact_refs Absent

**File**: `tools/supervisor/governance_validators.py`
**Location**: V13 `validate_spec_fact_refs_wired()`, around line 912

**Tier 1 Formats** (spec_fact_refs mandatory or exception required):
```python
TIER1_FORMATS = frozenset({
    "fods", "fodt", "ods", "odt", "fodg", "fodp",
    "zst", "pbm", "pgm", "ppm", "csv", "ndjson", "toml", "xcf", "qoi"
})
# Note: csv/ndjson/toml/xcf/qoi currently have legacy_backfill exception — they PASS via exception
```

**Required change**:
```python
# EXISTING: Only fires when spec_fact_refs is provided and invalid
# ADD: Also fire when spec_fact_refs absent AND no exception AND PRODUCT_SOURCE AND Tier 1

def validate_spec_fact_refs_wired(declaration):
    items = declaration.get("items", [])
    format_id = declaration.get("format", "").lower()
    exception_classification = declaration.get("exception_classification")
    spec_fact_refs = declaration.get("spec_fact_refs")

    for item in items:
        if item.get("item_type") != "PRODUCT_SOURCE":
            continue

        # EXISTING check: provided but invalid
        if spec_fact_refs and not _validate_fact_refs(spec_fact_refs, format_id):
            return ValidationResult(passed=False, blocks_sprint=True,
                                    message="spec_fact_refs provided but not found in sal-facts")

        # NEW check: absent without exception, for Tier 1 formats
        if not spec_fact_refs and not exception_classification:
            if format_id in TIER1_FORMATS:
                return ValidationResult(passed=False, blocks_sprint=True,
                                        message=f"PRODUCT_SOURCE item for Tier 1 format {format_id} requires spec_fact_refs or exception_classification")

    return ValidationResult(passed=True)
```

**Tests to add**:
```python
def test_v13_fails_fods_product_source_without_spec_fact_refs():
    decl = {"format": "fods", "items": [{"item_type": "PRODUCT_SOURCE", "item_id": "T"}]}
    result = validate_spec_fact_refs_wired(decl)
    assert result.passed == False
    assert result.blocks_sprint == True

def test_v13_passes_gnumeric_with_exception():
    decl = {"format": "gnumeric",
            "exception_classification": "schema_authority_available",
            "items": [{"item_type": "PRODUCT_SOURCE", "item_id": "T"}]}
    result = validate_spec_fact_refs_wired(decl)
    assert result.passed == True

def test_v13_passes_csv_with_legacy_backfill_exception():
    decl = {"format": "csv",
            "exception_classification": "legacy_backfill",
            "items": [{"item_type": "PRODUCT_SOURCE", "item_id": "T"}]}
    result = validate_spec_fact_refs_wired(decl)
    assert result.passed == True
```

---

## Task A-003: Evidence Schema Documentation

**File**: `docs/automation/supervisor-worker-contract.md`
**Location**: Required fields section

Add the following field documentation:

```markdown
## spec_fact_refs (required-or-explain)

For Tier 1 formats (formats with accessible formal specifications):
- Provide: `spec_fact_refs: ["FACT-{FORMAT}-NNN"]` — list of spec fact IDs from sal-facts-{format}.json
- Example: `spec_fact_refs: ["FACT-FODS-001", "FACT-FODS-004"]`
- These IDs are canonical references in .local/spec-cache/{format}/workbench/verified-facts.yaml

For Tier 2 formats (no public spec / schema only):
- Provide: `exception_classification: {valid_exception}` instead
- Valid values: no_public_spec_available, schema_authority_available, legacy_backfill

Both are required — cannot omit both for PRODUCT_SOURCE items.
```

Also update `sprint_executor_validate.py` to WARN (not FAIL) when spec_fact_refs absent and no exception for PRODUCT_SOURCE items. WARN mode for now — FAIL mode after Phase A-001 and A-002 are green.

---

## Task A-004: product_task_selector P-Level Wire

**File**: `tools/supervisor/product_task_selector.py`
**Location**: `_get_format_authority_status()`

**Current**: Checks poc-targets.yaml membership only → binary ALLOWED/BLOCKED

**Required change**:
```python
def _get_format_authority_status(format_id: str) -> dict:
    """Return authority status from authority_gate_validation.py, not poc-targets only."""
    import subprocess, json
    result = subprocess.run(
        ["python", "tools/supervisor/authority_gate_validation.py",
         "--format-id", format_id, "--json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return {"allowed": False, "reason": "authority_gate_validation_error", "level": 0}

    gate = json.loads(result.stdout)
    allowed = gate.get("product_expansion_allowed", False)
    exception = gate.get("exception_classification")

    # Tier 2 formats with valid exception → ALLOWED_WITH_EXCEPTION
    if not allowed and exception:
        return {"allowed": True, "reason": f"exception:{exception}", "level": gate.get("authority_level_int", 0)}

    return {"allowed": allowed, "reason": "authority_gate", "level": gate.get("authority_level_int", 0)}
```

**Tests to add**:
```python
def test_selector_blocks_ndjson_at_p2():
    # NDJSON is P2 with legacy_backfill exception — still ALLOWED in Phase A (exception preserved)
    status = _get_format_authority_status("ndjson")
    assert status["allowed"] == True  # legacy_backfill exception
    assert "legacy_backfill" in status["reason"]

def test_selector_blocks_hypothetical_p0_format():
    # P0 format with no exception → BLOCKED
    # (test with mocked authority_gate_validation output)
    pass
```

**Note on hard-coded _CANDIDATE_CATALOG removal**: Remove _CANDIDATE_CATALOG in Phase A-004 ONLY after authority_gate_validation.py is wired. Do NOT remove it before wiring — the catalog is the only safety net currently preventing P1 formats from having no task selection path.

---

## Stop Gate (Phase A Complete Criteria)

Phase A is COMPLETE only when ALL of:
- [ ] VG-003 passes: TC-GUARD-001 blocks gap_ledger_ref-only FODS sprint
- [ ] VG-005 passes: V13 fires for absent spec_fact_refs in FODS PRODUCT_SOURCE
- [ ] VG-006 passes: V13 still allows exception_classification for Gnumeric
- [ ] VG-007 confirms: product_task_selector calls authority_gate_validation.py
- [ ] Governance validator suite: 92+ tests pass
- [ ] No regressions in `tests/supervisor/test_autonomous_cycle*.py`
- [ ] No regressions in `tests/supervisor/test_governance_validators.py`

---

## Evidence Declaration Template for This Sprint

```yaml
exception_classification: machinery_healing
declared_scope: "Phase A — Close 3 critical spec authority bypass paths"
gap_ledger_ref: null
spec_fact_refs: null
# exception: machinery_healing sprints are investigation/repair, not product expansion

work_items:
  - item_id: SAL-HEAL-A001
    item_type: GOVERNANCE_TASKCARD
    description: "TC-GUARD-001 AND logic repair"
    status: completed
    evidence_paths:
      - tools/supervisor/autonomous_cycle.py
      - tests/supervisor/test_tc_guard_001_enforce.py
    test_refs:
      - test_guard001_blocks_gap_ledger_ref_only
      - test_guard001_passes_with_exception

  - item_id: SAL-HEAL-A002
    item_type: GOVERNANCE_TASKCARD
    description: "V13 absent spec_fact_refs enforcement"
    status: completed
    evidence_paths:
      - tools/supervisor/governance_validators.py
      - tests/supervisor/test_governance_validators.py
    test_refs:
      - test_v13_fails_fods_product_source_without_spec_fact_refs
      - test_v13_passes_gnumeric_with_exception

  - item_id: SAL-HEAL-A003
    item_type: GOVERNANCE_TASKCARD
    description: "Evidence schema spec_fact_refs documentation"
    status: completed
    evidence_paths:
      - docs/automation/supervisor-worker-contract.md

  - item_id: SAL-HEAL-A004
    item_type: GOVERNANCE_TASKCARD
    description: "product_task_selector P-level wire"
    status: completed
    evidence_paths:
      - tools/supervisor/product_task_selector.py
      - tests/supervisor/test_product_task_selector.py
```

---

## Cautions

1. **Do NOT** remove exception_classifications for Tier 2 formats (Gnumeric, ABW, SYLK, DIF, TSV)
2. **Do NOT** modify fods/Compat/ files — they are the reference implementation
3. **Do NOT** remove the legacy_backfill exception in this sprint — that is Phase D-006
4. **Do NOT** change V13 to block exceptions — the exception mechanism is correct
5. **Migration required**: After A-001, existing FODS/FODT sprints without spec_fact_refs will be blocked. Add exception_classification=legacy_backfill as a TEMPORARY migration measure for ODF formats if needed, to be replaced by real spec_fact_refs in Phase B.

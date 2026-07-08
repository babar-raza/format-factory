# Oracle Architecture Implementation Plan — Format Factory
# Produced by: TC-ORA-011 (jaunty-whistling-meteor investigation)
# Generated: 2026-07-08
# Type: HARDENED_EXECUTION_PLAN
# Authorizes: Implementation of 6 targeted product oracle fixes
# Incorporates: 2 design changes from adversarial review (adversarial-review.md)

---

## Overview

This plan authorizes implementation of 6 specific fixes to the Format Factory product oracle.
All fixes are grounded in direct code reading. File locations and line numbers are verified.
The plan is organized for sequential execution with regression controls at each step.

**Reference artifacts** (produced in this investigation):
- `docs/oracle/oracle-surface-register.yaml` — per-format surface status
- `docs/oracle/oracle-baseline-2026.yaml` — pre-fix state of all 20 formats
- `docs/oracle/oracle-gap-register.yaml` — gap definitions (OGAP-001 to OGAP-010)
- `docs/oracle/oracle-pilot-designs.md` — 12 validation pilots
- `docs/oracle/adversarial-review.md` — 2 design changes incorporated here

---

## Task: IMPL-FIX-001 — Fix Synthetic Property Depth Inflation
**Addresses**: OGAP-001
**Status**: OPEN
**Files**:
- `tools/oracle/execute_oracle.py` — PRIMARY CHANGE
- `oracle/formats/dif/oracle-package.yaml` — FOLLOW-ON REQUIRED
- `oracle/formats/fodt/oracle-package.yaml` — FOLLOW-ON REQUIRED
- `oracle/formats/sylk/oracle-package.yaml` — FOLLOW-ON REQUIRED

### Step 1.1: Code change to execute_oracle.py

**Location**: Module level (add near other constants at top), function `_compare_model_properties` line 713.

**Add at module level** (after existing constants like DEPTH_D0, DEPTH_D1):
```python
# Properties computed by the oracle framework itself, not returned by the parser.
# These do NOT count toward D1 depth elevation.
# SYNTHETIC_PROPERTIES = frozenset({"loaded", "result_type"})  → Fix 1 (IMPL-FIX-001)
SYNTHETIC_PROPERTIES: frozenset[str] = frozenset({"loaded", "result_type"})
```

**Modify `_compare_model_properties` function** (line 713, current):
```python
depth = DEPTH_D1 if expected_props else DEPTH_D0
```
**Replace with**:
```python
real_comparisons = [
    p for p in expected_props
    if p.get("property") not in SYNTHETIC_PROPERTIES
]
depth = DEPTH_D1 if real_comparisons else DEPTH_D0
```

### Step 1.2: Regression verification

Run oracle for ALL 20 formats immediately after the code change:
```bash
for fmt in csv fods fodt ods gnumeric sylk dif tsv ndjson toml abw fodg fodp odt xcf zst pbm pgm ppm qoi; do
    .venv/Scripts/python tools/oracle/execute_oracle.py --format $fmt
done
```

**Expected changes** (confirmed from baseline):
- dif: D1 → D0 (depth_histogram {D0: 3})
- fodt: D1 → D0 (depth_histogram {D0: 3})
- sylk: D1 → D0 (depth_histogram {D0: 3})

**Expected non-changes** (must NOT change):
- csv, fods, zst, gnumeric, ods, xcf, ndjson, toml, tsv: pass rates unchanged
- abw, fodg, fodp, odt, pbm, pgm, ppm, qoi: pass rates unchanged

### Step 1.3: Oracle package upgrades for affected formats

**Design Change 1 (from adversarial review)**: Upgrade dif, fodt, sylk oracle packages
with real model properties BEFORE running G2 checks.

**dif**: DIF parser returns a dict. Add real properties to oracle-package.yaml:
- Check `row_count`, `col_count`, or format-specific fields available from dif_parser.parse_dif()
- Inspect actual return value: `from dif.dif_parser import parse_dif; r = parse_dif(sample); print(r.keys())`

**fodt**: FODT parser (`fodt.parser.parse_fodt`) returns:
`{format_id, spec_version, odf_version_attr, mimetype, blocks, lists, tables, warnings, content}`
Add to oracle-package.yaml: `property: format_id, value: fodt` and `property: spec_version`

**sylk**: SYLK parser returns a dict. Inspect keys and add meaningful property comparisons.

### Step 1.4: Tests to write

```python
# tests/oracle/test_fix1_synthetic_properties.py

def test_loaded_property_does_not_earn_d1():
    """A case with only loaded:true in expected_model_properties must return D0."""
    from tools.oracle.execute_oracle import _compare_model_properties, DEPTH_D0
    expected_props = [{"property": "loaded", "value": True}]
    result_val = {"some_key": "some_value"}
    _, _, depth = _compare_model_properties(result_val, expected_props)
    assert depth == DEPTH_D0

def test_real_property_earns_d1():
    """A case with a non-synthetic property must return D1."""
    from tools.oracle.execute_oracle import _compare_model_properties, DEPTH_D1
    expected_props = [{"property": "sheet_count", "value": 1}]
    result_val = {"sheet_count": 1}
    _, _, depth = _compare_model_properties(result_val, expected_props)
    assert depth == DEPTH_D1

def test_mixed_properties_earn_d1():
    """A case with both loaded and sheet_count must return D1 (real prop present)."""
    from tools.oracle.execute_oracle import _compare_model_properties, DEPTH_D1
    expected_props = [
        {"property": "loaded", "value": True},
        {"property": "sheet_count", "value": 1},
    ]
    result_val = {"sheet_count": 1}
    _, _, depth = _compare_model_properties(result_val, expected_props)
    assert depth == DEPTH_D1

def test_dif_oracle_drops_to_d0_after_fix1():
    """DIF oracle must return D0 format depth after Fix 1 (all synthetic cases)."""
    import json
    from pathlib import Path
    summary_path = Path("oracle/formats/dif/reports/oracle-run-summary.json")
    summary = json.loads(summary_path.read_text())
    # After Fix 1 is applied and oracle is re-run:
    assert summary["format_depth_score"] == "D0"
```

### Acceptance criteria
- dif, fodt, sylk oracle summaries show format_depth_score = D0 immediately after Fix 1
- After oracle package upgrades + oracle re-run: dif, fodt, sylk return to D1
- All other format pass_rates and depth scores unchanged

---

## Task: IMPL-FIX-002 — Remove G2 Test-Suite Fallback
**Addresses**: OGAP-002
**Status**: OPEN
**Files**: `tools/supervisor/gate_executor.py`, function `check_g2`, lines 119-136

### Step 2.1: Code change

**Remove lines 119-136** (the `using_fallback` block). Replace with direct oracle result evaluation:

```python
# BEFORE (lines 119-136 to remove):
using_fallback = (passed_cases == 0) and (test_count >= 10)
if using_fallback:
    ...
else:
    results.append({"check": "oracle_verdicts_exist", ...})
    ...

# AFTER:
results.append({
    "check": "oracle_verdicts_exist",
    "passed": total > 0 and passed_cases > 0,
    "detail": f"{passed_cases}/{total} PASS",
})
depth_ok = depth in ("D1", "D2", "D3")
results.append({
    "check": "oracle_depth_minimum_d1",
    "passed": depth_ok,
    "detail": f"depth={depth}, required=D1+",
})
```

Also remove the `test_count` computation (lines ~119-122) since it's no longer needed.

### Step 2.2: Verification

```bash
python tools/supervisor/gate_executor.py --format csv --gates G1,G2 --dry-run
```

Expected: G2 passes for csv (5/5 PASS, D1).

```bash
python tools/supervisor/gate_executor.py --format fods --gates G1,G2 --dry-run
```

Expected: G2 passes for fods (9/10 PASS, D1).

### Step 2.3: Tests to write

```python
# tests/oracle/test_fix2_g2_no_fallback.py

def test_g2_fails_with_zero_oracle_pass():
    """G2 must fail when passed_cases == 0, even if test files >= 10."""
    # Create a mock oracle-run-summary.json with passed_cases = 0
    # Verify check_g2() returns passed=False for oracle_depth_minimum_d1

def test_g2_passes_with_oracle_evidence():
    """G2 must pass when oracle evidence is present and D1."""
    # Use actual csv oracle-run-summary.json (5/5 PASS, D1)
    # Verify check_g2() returns passed=True
```

### Acceptance criteria
- G2 passes for all 20 formats with current oracle state (all have PASS > 0, D1+)
- G2 fails for a format with 0 oracle PASS (test with mock summary)
- No format relies on the fallback in current state

---

## Task: IMPL-FIX-003 — Add Source Hash to Oracle-Run-Summary
**Addresses**: OGAP-003
**Status**: OPEN
**Files**:
- `tools/oracle/execute_oracle.py` — add hash computation before summary write
- `tools/supervisor/gate_executor.py` — add staleness check in check_g2()

### Step 3.1: Add hash to execute_oracle.py

**Location**: `run_oracle_for_format()`, before the summary dict is built (near line 1757).

```python
import hashlib  # add to imports at top of file

def _compute_source_hash(format_id: str) -> str:
    """Compute SHA256 of key parser files for a format."""
    src_dir = REPO_ROOT / "src" / "python" / format_id
    candidates = sorted(
        list(src_dir.rglob("*parser*.py")) +
        list(src_dir.rglob("*codec*.py")) +
        list(src_dir.rglob("__init__.py"))
    )
    if not candidates:
        return "unavailable"
    h = hashlib.sha256()
    for f in candidates:
        try:
            h.update(f.read_bytes())
        except OSError:
            pass
    return f"sha256:{h.hexdigest()[:16]}"

def _compute_package_hash(format_id: str) -> str:
    """Compute SHA256 of oracle-package.yaml."""
    pkg_path = ORACLE_DIR / "formats" / format_id / "oracle-package.yaml"
    if not pkg_path.exists():
        return "unavailable"
    return f"sha256:{hashlib.sha256(pkg_path.read_bytes()).hexdigest()[:16]}"
```

**In `run_oracle_for_format()`** (before building summary dict):
```python
source_hash = _compute_source_hash(format_id)
package_hash = _compute_package_hash(format_id)
d0_count = len([v for v in verdicts if v.get("depth_level") == DEPTH_D0])
total_valid_pass = len([v for v in verdicts if v.get("result") == RESULT_PASS])
d0_fraction = d0_count / max(total_valid_pass, 1)
```

**Add to summary dict**:
```python
summary = {
    # ... existing fields ...
    "product_source_hash": source_hash,
    "oracle_package_hash": package_hash,
    "depth_d0_fraction": round(d0_fraction, 3),
}
```

### Step 3.2: Add staleness check to gate_executor.py

**In `check_g2()`, after loading summary**:
```python
# Staleness check (Fix 3b)
current_source_hash = _compute_source_hash_for_gate(format_id)
stored_source_hash = summary.get("product_source_hash", "unavailable")
stale = (
    stored_source_hash != "unavailable" and
    current_source_hash != "unavailable" and
    stored_source_hash != current_source_hash
)
```

**Add to gate result** (not as a blocking check):
```python
{
    "check": "source_freshness",
    "passed": True,  # staleness is warning-only, not blocking
    "stale_warning": stale,
    "detail": (
        f"source_hash_current={current_source_hash}, stored={stored_source_hash}"
        if stale else "source hash current"
    ),
}
```

### Acceptance criteria
- oracle-run-summary.json for CSV contains product_source_hash and oracle_package_hash
- Modifying a CSV parser file changes the hash on next run
- G2 gate output shows stale_warning when hash differs (but G2 still passes)
- Re-running oracle clears stale_warning

---

## Task: IMPL-FIX-004 — Registry Pattern + Generic Invalid Executor
**Addresses**: OGAP-005 (partially), SW1
**Status**: OPEN
**Files**: `tools/oracle/execute_oracle.py`

### Step 4.1: Add registry at module level

**Add after imports, before format-specific executor functions**:
```python
VALID_CASE_EXECUTORS: dict[str, callable] = {}
INVALID_CASE_EXECUTORS: dict[str, callable] = {}
ROUNDTRIP_CASE_EXECUTORS: dict[str, callable] = {}

def _register_format_executors(
    format_id: str,
    valid: "callable | None" = None,
    invalid: "callable | None" = None,
    roundtrip: "callable | None" = None,
) -> None:
    if valid:    VALID_CASE_EXECUTORS[format_id] = valid
    if invalid:  INVALID_CASE_EXECUTORS[format_id] = invalid
    if roundtrip: ROUNDTRIP_CASE_EXECUTORS[format_id] = roundtrip
```

### Step 4.2: Add generic invalid case executor (Design Change 2)

```python
def execute_generic_invalid_case(
    case: dict, pkg: dict, format_id: str, module: str, callable_name: str
) -> dict:
    """Generic invalid case executor: expects callable to raise an exception.

    Most invalid oracle cases test that a parser rejects malformed input by raising.
    This executor: loads the inline or file input, calls the parser, returns PASS if
    exception raised, FAIL if no exception raised.

    Returns D0 (no model property comparison — only exception expectation).
    """
    case_id = case["case_id"]
    _, authority_status = check_authority(case, True)

    inline_input = case.get("input_inline") or case.get("inline_input")
    input_ref = case.get("input_ref")

    try:
        fn = _import_callable(module, callable_name)
    except ImportError as e:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
            case_id=case_id, profile="INVALID_INPUT_REJECTION",
            result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
            depth_level=DEPTH_D0, diagnostics=[f"Import error: {e}"],
        )

    try:
        if inline_input is not None:
            import tempfile, os
            with tempfile.NamedTemporaryFile(mode="w", suffix=f".{format_id}", delete=False) as tf:
                tf.write(inline_input)
                tmp_path = tf.name
            try:
                fn(tmp_path)
            finally:
                os.unlink(tmp_path)
        elif input_ref:
            sample_path = REPO_ROOT / input_ref
            fn(str(sample_path))
        else:
            return make_verdict(
                ..., result=RESULT_NOT_APPLICABLE, depth_level=DEPTH_D0,
                diagnostics=["No input_inline or input_ref for invalid case"],
            )
        # If we reach here: no exception was raised → FAIL
        return make_verdict(
            ..., result=RESULT_FAIL, depth_level=DEPTH_D0,
            diagnostics=["Expected exception not raised for invalid input"],
        )
    except Exception:
        # Exception raised as expected → PASS
        return make_verdict(
            ..., result=RESULT_PASS, depth_level=DEPTH_D0,
            diagnostics=["Exception raised as expected for invalid input"],
        )
```

### Step 4.3: Register executors + update dispatch

Register all 20 formats' valid executors using the registry.
Register invalid executors where they exist (csv, fods) or use generic.

**In `run_oracle_for_format()`, replace the if/elif chain with**:
```python
for case in pkg.get("valid_cases", []):
    exec_fn = VALID_CASE_EXECUTORS.get(format_id)
    if exec_fn is None:
        # Fallback: shouldn't happen since all 20 formats are registered
        verdict = make_verdict(..., result=RESULT_NOT_APPLICABLE, diagnostics=["No executor registered"])
    else:
        verdict = exec_fn(case, pkg)
    # ... append, save, print ...

for case in pkg.get("invalid_cases", []):
    exec_fn = INVALID_CASE_EXECUTORS.get(format_id)
    if exec_fn is None:
        continue  # skip unregistered invalid cases silently
    verdict = exec_fn(case, pkg)
    # ...

for case in pkg.get("roundtrip_cases", []):
    exec_fn = ROUNDTRIP_CASE_EXECUTORS.get(format_id)
    if exec_fn is None:
        continue
    verdict = exec_fn(case, pkg)
    # ...
```

### Regression requirement
Run oracle for all 20 formats before and after. Pass rates must be IDENTICAL.
The refactor must not change any result or depth score.

### Acceptance criteria
- Oracle results identical to baseline for all 20 formats
- Invalid cases now execute for formats where generic executor is registered
- LOC of run_oracle_for_format() decreases (20 if/elif branches removed)

---

## Task: IMPL-FIX-005 — Read assertion: Schema in Generic Executor
**Addresses**: OGAP-004
**Status**: OPEN
**Files**: `tools/oracle/execute_oracle.py`, `execute_generic_load_case()`, ~line 751

### Step 5.1: Code change

After `result_val = fn(str(sample_path))` and before existing property comparison:

```python
# Handle assertion: schema (legacy, supplemental to expected_model_properties)
assertion = case.get("assertion", {})
if assertion and not expected_props:
    # Case uses assertion: schema only (no expected_model_properties).
    # Execute assertion checks as D1-equivalent comparisons.
    expect_type_name = assertion.get("expect_type")
    expect_return_value = assertion.get("expect_return_value")

    if expect_type_name:
        type_map = {"dict": dict, "list": list, "str": str, "int": int, "bool": bool, "None": type(None)}
        expected_type = type_map.get(expect_type_name)
        if expected_type is not None and not isinstance(result_val, expected_type):
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id=format_id, product_id=f"format-factory-{format_id}", language="python",
                case_id=case_id, profile=case.get("profile", "PARSE_VALIDITY"),
                result=RESULT_FAIL, authority_status=authority_status,
                depth_level=DEPTH_D1,  # type comparison is a real check
                input_hash=input_hash,
                diagnostics=[f"assertion: expect_type={expect_type_name}, got {type(result_val).__name__}"],
            )

    if expect_return_value is not None:
        if bool(result_val) != bool(expect_return_value):
            return make_verdict(
                ..., result=RESULT_FAIL, depth_level=DEPTH_D1,
                diagnostics=[f"assertion: expect_return_value={expect_return_value}, got {bool(result_val)}"],
            )

    # All assertion checks passed
    return make_verdict(
        ..., result=RESULT_PASS, depth_level=DEPTH_D1,
        diagnostics=[f"assertion: schema passed (expect_type={expect_type_name})"],
    )
```

### Acceptance criteria
- abw-valid-001: was D0 PASS → now D1 PASS (expect_type: dict check passes)
- abw-valid-002: was D0 PASS → now D1 PASS
- abw depth_histogram: was {D0: 2, D1: 1} → now {D1: 3}
- Pilot 10 passes

---

## Task: IMPL-FIX-006 — V143 Distribution-Aware Depth Validator
**Addresses**: OGAP-006
**Status**: OPEN
**Files**: `tools/supervisor/governance_validators_oracle.py`, `validate_oracle_depth_minimum()`, ~line 14

### Step 6.1: Code change

**Current**:
```python
if depth == "D0":
    findings.append({...})
```

**New**:
```python
histogram = summary.get("depth_histogram", {})
d0_count = histogram.get("D0", 0)
d1_plus_count = sum(histogram.get(d, 0) for d in ("D1", "D2", "D3"))
majority_d0 = d0_count > d1_plus_count and d0_count > 0

if depth == "D0" or majority_d0:
    findings.append({
        "code": "ORACLE_DEPTH_LOW",
        "severity": "WARN",
        "format_id": format_id,
        "message": (
            f"oracle depth score is D0 (no real property comparisons)" if depth == "D0"
            else f"majority of cases at D0: {d0_count} D0 vs {d1_plus_count} D1+"
        ),
        "detail": f"depth_histogram={histogram}, format_depth_score={depth}",
    })
```

### Tests

```python
def test_v143_fires_for_majority_d0():
    """V143 must WARN when D0 cases outnumber D1+ cases."""
    summary = {"format_depth_score": "D1", "depth_histogram": {"D0": 9, "D1": 1}}
    # ... run validate_oracle_depth_minimum(summary) ...
    assert any(f["code"] == "ORACLE_DEPTH_LOW" for f in findings)

def test_v143_does_not_fire_for_fods_ratio():
    """V143 must NOT WARN for FODS (6 D1, 4 D0 — D0 not majority)."""
    summary = {"format_depth_score": "D1", "depth_histogram": {"D0": 4, "D1": 6}}
    # ...
    assert not any(f["code"] == "ORACLE_DEPTH_LOW" for f in findings)
```

---

## Task: IMPL-FOLLOW-ON-INVALID — Generic Invalid Coverage for All Formats
**Addresses**: OGAP-005 (full coverage)
**Status**: OPEN (dependent on IMPL-FIX-004)
**Description**: After Fix 4 registry is in place, register `execute_generic_invalid_case`
for all 18 formats that have `invalid_cases` defined but no specific executor.

```python
GENERIC_INVALID = lambda case, pkg: execute_generic_invalid_case(case, pkg, FORMAT_ID, MODULE, CALLABLE)
for fmt_id in ["abw", "dif", "fodg", "fodp", "fodt", "gnumeric", "ndjson", "ods",
               "odt", "pbm", "pgm", "ppm", "qoi", "sylk", "toml", "tsv", "xcf", "zst"]:
    _register_format_executors(fmt_id, invalid=...)  # use generic with per-format module/callable
```

---

## Task: SPEC-PROVENANCE-001 — SAL Fact Provenance Fields
**Addresses**: OGAP-007
**Status**: OPEN
**Description**: Add `review_level`, `reviewed_at`, `spec_sha256` fields to SAL fact records.
Migrate `authorized_fact_refs` in oracle-package.yaml from string comments to real fact ID lists.

**Non-blocking for product oracle fixes.** Execute after IMPL-FIX-001 through IMPL-FIX-006.

---

## Implementation Order (Sequencing)

```
IMPL-FIX-004 (registry)     ─── no deps, pure refactor
    │
    ├── IMPL-FIX-001 (synthetic) ─── immediately run oracle + confirm D0 for dif/fodt/sylk
    │       │
    │       └── Oracle package upgrades for dif, fodt, sylk  ← REQUIRED before G2 checks
    │               │
    │               └── IMPL-FIX-002 (G2 fallback)  ← safe after oracle packages upgraded
    │
    ├── IMPL-FIX-003 (source hash)  ─── independent, add to execute_oracle.py + gate_executor.py
    │
    ├── IMPL-FIX-005 (assertion:)   ─── independent (abw surface improvement)
    │
    ├── IMPL-FIX-006 (V143)         ─── independent (governance validator)
    │
    └── IMPL-FOLLOW-ON-INVALID      ─── depends on IMPL-FIX-004 registry being in place
```

**Critical path**: IMPL-FIX-004 → IMPL-FIX-001 → oracle package upgrades → IMPL-FIX-002

---

## Final Verification Checklist

After all 6 fixes are implemented:

```bash
# 1. Run oracle for all 20 formats with .venv/Scripts/python
for fmt in csv fods fodt ods gnumeric sylk dif tsv ndjson toml abw fodg fodp odt xcf zst pbm pgm ppm qoi; do
    .venv/Scripts/python tools/oracle/execute_oracle.py --format $fmt
done

# 2. Run G2 for all 20 formats
for fmt in csv fods fodt ods gnumeric sylk dif tsv ndjson toml abw fodg fodp odt xcf zst pbm pgm ppm qoi; do
    python tools/supervisor/gate_executor.py --format $fmt --gates G1,G2 --dry-run
done

# 3. Check that dif/fodt/sylk have been upgraded to D1 (not D0)
python -c "import json; from pathlib import Path; [print(f.name.split('/')[2], json.loads(f.read_text())['format_depth_score']) for f in Path('oracle/formats').glob('*/reports/oracle-run-summary.json')]"

# 4. Verify all summaries have product_source_hash
python -c "import json; from pathlib import Path; [print(f.parent.parent.name, 'OK' if 'product_source_hash' in json.loads(f.read_text()) else 'MISSING') for f in Path('oracle/formats').glob('*/reports/oracle-run-summary.json')]"

# 5. Run pilot 3 (dif drops to D0 with only Fix 1 applied) — for documentation only
# 6. Run pilot 11 (idempotent runs) — two consecutive runs produce identical output
```

**All tests pass**: Run `.venv/Scripts/pytest tests/oracle/ -v`

---

## Rollback

All fixes are in source-controlled Python files. Rollback = `git revert <commit>`.

For Fix 3 (schema extension): old summaries without `product_source_hash` are backward-compatible
(field is optional). No consumers break on absence of the new fields.

For Fix 1: the oracle-package.yaml upgrades for dif/fodt/sylk are additive (new properties added).
Rollback of Fix 1 code also requires reverting the oracle package upgrades to avoid confusion.

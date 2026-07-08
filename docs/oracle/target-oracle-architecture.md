# Target Oracle Architecture — Format Factory
# Produced by: TC-ORA-006 (jaunty-whistling-meteor investigation)
# Generated: 2026-07-08

---

## 1. Design Decisions

**Decision 1: Extend execute_oracle.py, do not replace it.**

The authority class enforcement, verdict schema, oracle-package.yaml approach, and
case-level citation of spec sections are correctly designed. The defects are in 6 specific
code paths, not in the architecture. Replacing 1,822 lines would risk regressing the
working surfaces (csv, fods, zst) while fixing the failing ones.

**Decision 2: Four oracle boundaries remain distinct. Do not collapse them.**

| Oracle | File(s) | Purpose | Authority |
|---|---|---|---|
| Specification | SAL + tools/spec/ | What does the spec say? | SPEC_NORMATIVE (ODF, RFC, TOML) |
| Capability | gap-ledger.json | Is this capability implemented? | SAL fact chain |
| Product | execute_oracle.py | Does product implement spec correctly? | SPEC_NORMATIVE, SCHEMA_DERIVED |
| Acquisition | run_fods_oracle.py | Does prototype agree with reference impl? | VERIFIED_INTEROPERABILITY |

Collapsing these creates authority confusion: "LibreOffice says X" is not the same as
"ODF spec §9.4.2 says X." The distinction matters when they disagree.

**Decision 3: Build only what is needed to eliminate false-green paths.**

The specification and capability oracles are important but are NOT causing the current
false-greens. Product oracle defects are the urgent concern. The specification oracle
can be incrementally improved by adding provenance fields to SAL facts (no rebuild required).
The capability oracle is a separate project.

**Decision 4: Registry pattern for case executors.**

The if/elif dispatch chain (20+ branches, 1,638-1,678 lines) prevents adding new case types
without editing 3 separate code sections. Replace with a registry dict that maps
(format_id, case_type) → executor function. This is a refactor only — no behavior change
for working surfaces.

---

## 2. Product Oracle Component Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  oracle-package.yaml (per format)                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┤
│  │  authority {}      — specification refs, authorized_fact_refs           │
│  │  corpus_refs []    — sample files with sha256 + authority_class         │
│  │  valid_cases []    — expected_model_properties (or assertion:)          │
│  │  invalid_cases []  — expect_exception patterns                          │
│  │  roundtrip_cases []— RT assertions                                      │
│  └─────────────────────────────────────────────────────────────────────────┤
│                              │                                              │
│                              ▼                                              │
│  execute_oracle.py                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┤
│  │  check_authority()           → BLOCKED_MISSING_AUTHORITY if class=UNKNOWN│
│  │  EXECUTOR_REGISTRY           → (format_id, case_type) → executor_fn    │
│  │  execute_generic_load_case() → reads expected_model_properties + assertion│
│  │  _compare_model_properties() → SYNTHETIC_PROPERTIES excluded from D1    │
│  │  schema_validator.py         → ODF RelaxNG D2 validation                │
│  │  make_verdict()              → structured verdict with depth_level      │
│  │  run_oracle_for_format()     → dispatches all case types via registry   │
│  │  save_verdict()              → .local/oracle/{fmt}/verdicts/{case}.json │
│  └─────────────────────────────────────────────────────────────────────────┤
│                              │                                              │
│                              ▼                                              │
│  oracle-run-summary.json (per format, committed)                           │
│  ┌─────────────────────────────────────────────────────────────────────────┤
│  │  oracle_id, format_id, executed_at                                     │
│  │  total_cases, results {PASS, FAIL, SKIPPED_MISSING_PROVIDER, ...}      │
│  │  pass_rate, verdict                                                    │
│  │  depth_histogram {D0, D1, D2, D3}                                      │
│  │  format_depth_score (max)                                               │
│  │  depth_d0_fraction (NEW — Fix 3b)                                      │
│  │  product_source_hash (NEW — Fix 3)                                     │
│  │  oracle_package_hash (NEW — Fix 3)                                     │
│  └─────────────────────────────────────────────────────────────────────────┤
│                              │                                              │
│                              ▼                                              │
│  gate_executor.py (G2 check)           governance_validators_oracle.py (V143)│
│  ┌─────────────────────────────────────────────────────────────────────────┤
│  │  check_g2(): reads oracle-run-summary.json                              │
│  │  REMOVED: test-suite fallback (Fix 2)                                  │
│  │  ADDED: stale_warning when source hash changed (Fix 3b)                │
│  │  V143: WARN if D0_count > D1+D2+D3 count (Fix 6, majority-D0)         │
│  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Six Targeted Fixes — Exact Scope

### Fix 1: Synthetic Properties Must Not Elevate Depth
**Target**: `tools/oracle/execute_oracle.py`, function `_compare_model_properties()`, line 664

**Current code (line 673-713, simplified)**:
```python
def _compare_model_properties(result_val, expected_props: list):
    observed = {"loaded": True, "result_type": type(result_val).__name__}
    # ... prop checks ...
    depth = DEPTH_D1 if expected_props else DEPTH_D0  # BUG: loaded counts as D1
```

**New code**:
```python
SYNTHETIC_PROPERTIES = frozenset({"loaded", "result_type"})  # add at module level

def _compare_model_properties(result_val, expected_props: list):
    observed = {"loaded": True, "result_type": type(result_val).__name__}
    # ... prop checks (unchanged: loaded is still compared correctly) ...
    real_comparisons = [
        p for p in expected_props
        if p.get("property") not in SYNTHETIC_PROPERTIES
    ]
    depth = DEPTH_D1 if real_comparisons else DEPTH_D0  # FIX: only real props earn D1
```

**Impact**: dif, fodt, sylk will report D0 (correct). V143 fires for these 3 formats.
gnumeric, ods, xcf: changed histogram but D1 preserved (have real non-synthetic cases).
All other formats: unchanged.

---

### Fix 2: Remove G2 Test-Suite Fallback
**Target**: `tools/supervisor/gate_executor.py`, function `check_g2()`, lines 119-136

**Current code (to remove)**:
```python
using_fallback = (passed_cases == 0) and (test_count >= 10)
if using_fallback:
    results.append({
        "check": "oracle_verdicts_exist",
        "passed": True,
        "detail": f"{passed_cases}/{total} oracle PASS (fallback: {test_count} test files)",
    })
    results.append({
        "check": "oracle_depth_minimum_d1",
        "passed": True,
        "detail": f"depth={depth} (fallback: ...)",
    })
```

**Replacement**:
```python
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

**Impact**: As of 2026-07-08 baseline, NO format relies on the fallback (all have PASS > 0).
Zero formats immediately blocked. However, the structural lie (reporting oracle_depth_minimum_d1:
True without oracle evidence) is eliminated.

---

### Fix 3: Add Source Hash to Oracle-Run-Summary
**Target**: `tools/oracle/execute_oracle.py`, function `run_oracle_for_format()`, before summary write (~line 1757)

**New code** (before writing summary):
```python
import hashlib

# Compute product source hash
src_dir = REPO_ROOT / "src" / "python" / format_id
parser_candidates = sorted(
    list(src_dir.rglob("*parser*.py")) +
    list(src_dir.rglob("*codec*.py")) +
    list(src_dir.rglob("__init__.py"))
)
source_hash = "unavailable"
if parser_candidates:
    h = hashlib.sha256()
    for f in parser_candidates:
        h.update(f.read_bytes())
    source_hash = f"sha256:{h.hexdigest()[:16]}"

pkg_path = ORACLE_DIR / "formats" / format_id / "oracle-package.yaml"
pkg_hash_bytes = pkg_path.read_bytes() if pkg_path.exists() else b""
package_hash = f"sha256:{hashlib.sha256(pkg_hash_bytes).hexdigest()[:16]}"

# Add to summary
summary.update({
    "product_source_hash": source_hash,
    "oracle_package_hash": package_hash,
    "depth_d0_fraction": d0_count / max(total_valid_pass, 1),
})
```

**Fix 3b**: In `gate_executor.py check_g2()`, after reading summary, compute current hash
and compare. Report `stale_warning: True` if hashes differ. G2 still PASSES — stale is a
warning, not a block. This makes staleness visible without blocking release.

---

### Fix 4: Replace Dispatch Chain with Registry
**Target**: `tools/oracle/execute_oracle.py`, lines 1638-1685 (20-branch if/elif), and surrounding case-type loops

**New module-level registry**:
```python
VALID_CASE_EXECUTORS: dict[str, callable] = {}
INVALID_CASE_EXECUTORS: dict[str, callable] = {}
ROUNDTRIP_CASE_EXECUTORS: dict[str, callable] = {}

def _register_format_executors(
    format_id: str,
    valid: callable | None = None,
    invalid: callable | None = None,
    roundtrip: callable | None = None,
) -> None:
    if valid:    VALID_CASE_EXECUTORS[format_id] = valid
    if invalid:  INVALID_CASE_EXECUTORS[format_id] = invalid
    if roundtrip: ROUNDTRIP_CASE_EXECUTORS[format_id] = roundtrip
```

**Registration** (after each execute_* function definition):
```python
_register_format_executors("csv",  valid=execute_csv_valid_case,  invalid=execute_csv_invalid_case)
_register_format_executors("fods", valid=execute_fods_valid_case, invalid=execute_fods_invalid_case, roundtrip=execute_fods_rt_case)
_register_format_executors("zst",  valid=execute_zst_valid_case,  roundtrip=execute_zst_lossless_case)
# ... all 20 formats ...
```

**New dispatch in run_oracle_for_format()**:
```python
for case in pkg.get("valid_cases", []):
    exec_fn = VALID_CASE_EXECUTORS.get(format_id, lambda c, p: execute_generic_load_case(c, p, format_id, ...))
    verdict = exec_fn(case, pkg)
    # ...

for case in pkg.get("invalid_cases", []):
    exec_fn = INVALID_CASE_EXECUTORS.get(format_id)
    if exec_fn is None:
        continue  # or: use generic invalid handler when one is written
    verdict = exec_fn(case, pkg)
    # ...

for case in pkg.get("roundtrip_cases", []):
    exec_fn = ROUNDTRIP_CASE_EXECUTORS.get(format_id)
    if exec_fn is None:
        continue
    verdict = exec_fn(case, pkg)
```

**Regression requirement**: Run oracle for all 20 formats before and after. Results must be
identical to baseline. Zero regression permitted.

---

### Fix 5: Read `assertion:` Schema in Generic Executor
**Target**: `tools/oracle/execute_oracle.py`, `execute_generic_load_case()`, line 717+

**After calling the parser function and getting result_val**, add:
```python
# Handle assertion: schema (legacy format, ignored in current executor)
assertion = case.get("assertion", {})
if assertion and not expected_props:
    # Case uses assertion: but has no expected_model_properties.
    # Execute as D1-equivalent if expect_type or expect_return_value is set.
    expect_type_name = assertion.get("expect_type")
    expect_return_value = assertion.get("expect_return_value")
    if expect_type_name:
        type_map = {"dict": dict, "list": list, "str": str, "int": int, "bool": bool}
        expected_type = type_map.get(expect_type_name)
        if expected_type and not isinstance(result_val, expected_type):
            return make_verdict(
                ..., result=RESULT_FAIL,
                depth_level=DEPTH_D1,  # type check counts as a real comparison
                diagnostics=[f"Expected type {expect_type_name}, got {type(result_val).__name__}"],
            )
    if expect_return_value is not None:
        if bool(result_val) != bool(expect_return_value):
            return make_verdict(
                ..., result=RESULT_FAIL,
                depth_level=DEPTH_D1,
                diagnostics=[f"Expected return value {expect_return_value}, got {bool(result_val)}"],
            )
    # Assertion passed: mark as D1 (a real type/return-value check was performed)
    return make_verdict(
        ..., result=RESULT_PASS,
        depth_level=DEPTH_D1,
        diagnostics=[f"assertion: schema passed (expect_type={expect_type_name})"],
    )
```

**Impact**: abw-valid-001 and abw-valid-002 will execute the `expect_type: dict` check.
If abw parser returns dict → PASS at D1. If it returns non-dict → FAIL at D1.
Current behavior: PASS at D0 (no comparison at all).

---

### Fix 6: V143 Distribution-Aware
**Target**: `tools/supervisor/governance_validators_oracle.py`, `validate_oracle_depth_minimum()`, ~line 14

**Current code**:
```python
if depth == "D0":
    findings.append({...})
```

**New code**:
```python
histogram = summary.get("depth_histogram", {})
d0_count = histogram.get("D0", 0)
d1_plus_count = sum(histogram.get(d, 0) for d in ("D1", "D2", "D3"))
majority_d0 = d0_count > d1_plus_count and d0_count > 0

if depth == "D0" or majority_d0:
    findings.append({
        "code": "ORACLE_DEPTH_LOW",
        "severity": "WARN",
        "message": (
            f"format_depth_score={depth} (all D0)" if depth == "D0"
            else f"majority cases at D0: {d0_count} D0 vs {d1_plus_count} D1+"
        ),
        "detail": f"depth_histogram={histogram}",
    })
```

**Impact**: FODS (6 D1, 4 D0 → D0 is NOT majority → no WARN — correct).
A format with 1 D1 and 9 D0 → majority D0 → WARN (correct).
dif/fodt/sylk after Fix 1: all D0 → depth == "D0" → WARN (correct).

---

## 4. Specification Oracle Path (Incremental)

The SAL facts are valuable data. They don't need to be rebuilt — they need provenance fields.

Add to each SAL fact record:
```json
{
  "fact_id": "FACT-FODS-006",
  "claim": "Cells are table:table-cell children of table:table-row",
  "section": "ODF 1.3 §9.4.2",
  "review_level": "manual_extraction_run030",
  "reviewed_at": "2026-06-26",
  "spec_sha256": "sha256:92cfe64..."
}
```

`review_level: manual_extraction_run030` is honest: it means "an agent read the spec and
extracted this claim, not machine-validated against spec text." This enables oracle-package.yaml
`authorized_fact_refs` to reference real fact IDs that can be verified to exist in the SAL store.

What this does NOT do: validate fact text against spec. That requires human review.
Do not claim it does more than it does.

---

## 5. Acquisition Oracle Constraints

The acquisition oracle (run_fods_oracle.py, run_fodt_oracle.py) correctly classifies LibreOffice
evidence as VERIFIED_INTEROPERABILITY, not SPEC_NORMATIVE. This boundary must be preserved.

When LibreOffice and the ODF spec disagree, SPEC_NORMATIVE cases take precedence.
Acquisition oracle is evidence for "interop with reference implementation" — a different
question than "implements the spec."

18 formats have no acquisition oracle coverage. This is correct — LibreOffice doesn't
meaningfully support image formats, compression, etc. Do not force-fit acquisition oracle
onto formats where it doesn't apply.

---

## 6. What This Architecture Cannot Deliver

- Full specification oracle that validates fact text against ODF spec content
  (requires a separate pipeline to extract and compare spec text)
- Capability oracle (requires redesigning gap-ledger consumption pipeline)
- D2 coverage for non-ODF formats (no published RelaxNG schemas for CSV, TOML, etc.)
- D3 coverage for formats without reference implementations

These are explicitly out of scope for this plan. They require separate authorization.

# Oracle Readiness Assessment — Format Factory
# Produced by: TC-ORA-005 (jaunty-whistling-meteor investigation)
# Generated: 2026-07-08
# Source: Baseline run 2026-07-08 + code-level analysis of execute_oracle.py + gate_executor.py

---

## 12 Completion Counters

These counters drive the readiness verdict. Each must be 0 or have a documented exception.

```
ORACLE_SURFACES_NOT_INVENTORIED: 0
  ✓ All 20 active Python FOSS formats have oracle-package.yaml + oracle-run-summary.json

ORACLE_CLAIMS_WITHOUT_AUTHORITY: 2
  ✗ Boundary C (Specification Oracle / SAL facts): authorized_fact_refs is a string comment,
    not a machine-verifiable list. 14,441 facts have no provenance fields.
  ✗ Boundary D (Capability Oracle): 398 capabilities in gap-ledger.json with no proof validation.

ORACLE_RESULTS_WITHOUT_PERSISTENT_EVIDENCE: 0
  ✓ All 20 formats have committed oracle-run-summary.json.

ORACLE_RESULTS_WITHOUT_CONSUMERS: 0
  ✓ G2 gate (gate_executor.py) consumes oracle-run-summary.json.
  ✓ V143 validator (governance_validators_oracle.py) consumes depth_histogram.
  ✓ Certification report consumes pass_rate.

ORACLE_GATES_WITH_FALSE_GREEN_PATHS: 2
  ✗ FG1: G2 test-suite fallback (gate_executor.py:119-136) — 0 oracle verdicts + ≥10 test files
    = G2 PASS. Reports oracle_depth_minimum_d1: True falsely.
  ✗ FG2: `loaded: true` synthetic property earns D1 in _compare_model_properties() (line 713).
    3 formats (dif, fodt, sylk) have ALL cases at D1 via this inflation.

CAPABILITIES_WITHOUT_FACT_PROOF: 398
  ✗ gap-ledger.json 398 entries. None machine-verified against SAL facts.
  NOTE: This is a known gap in Boundary D. Not urgent for fixing product oracle.

PRODUCT_CERTIFICATIONS_WITHOUT_PRODUCT_ORACLE_PROOF: 0
  ✓ All 20 formats have committed oracle-run-summary.json.
  CAVEAT: 3 formats (dif, fodt, sylk) have inflated D1 — real depth is D0. Certification is
  technically present but based on synthetic comparisons.

UPSTREAM_CHANGES_WITHOUT_INVALIDATION: 20
  ✗ oracle-run-summary.json has no product_source_hash field. ANY change to product source
    files leaves the stale summary valid indefinitely. There is no detection mechanism.

REFERENCE_IMPLEMENTATIONS_TREATED_AS_SPEC_AUTHORITY: 0
  ✓ LibreOffice is correctly classified as VERIFIED_INTEROPERABILITY in oracle-authority-policy.md.
  ✓ fods-lo-* cases in oracle-package.yaml use VERIFIED_INTEROPERABILITY authority class.

ORACLE_GAPS_WITHOUT_TASKS: 0
  ✓ All 10 identified gaps (OGAP-001 to OGAP-010) have assigned taskcards in the
    implementation plan (plans/oracle/oracle-architecture-implementation-plan.md).

REQUIRED_PILOTS_WITHOUT_DESIGN: 0
  ✓ All 12 required pilots are designed in docs/oracle/oracle-pilot-designs.md.

MATERIAL_SECOND_RUN_CHANGES: 0
  ✓ Verified by reading produced artifacts before this report was written.
    All artifacts are internally consistent with code-level findings.
```

---

## Oracle Maturity Scores

| Oracle | Level | Name | Justification |
|---|---|---|---|
| Specification Oracle (SAL) | 1 | AD_HOC | 14,441 facts extracted in run030. Not continuously maintained. No provenance fields. authorized_fact_refs is a string comment. |
| Capability Oracle | 0 | ABSENT | No proof validation machinery. gap-ledger.json is advisory only. |
| Product Oracle | 3 | GOVERNED_PARTIAL | Authority class enforcement works. Verdict schema is sound. 6 specific defects (OGAP-001 to OGAP-006) are fixable. |
| Acquisition Oracle | 2 | BASIC_REPEATABLE | FODS/FODT implemented. Reproducible when LibreOffice present. Version not pinned. 18 formats without coverage. |

---

## False-Green Risk Analysis

### FG1 (HIGH): Synthetic `loaded: true` inflates D1 to D1

**Scope**: dif, fodt, sylk — ALL oracle cases check only `loaded: true`.
**Mechanism**: `_compare_model_properties()` line 713: `depth = DEPTH_D1 if expected_props else DEPTH_D0`.
Any non-empty `expected_props` list → D1. `loaded: true` is in that list → D1. But `loaded` is a
synthetic property computed as `result_val is not None` — not a real model property.

**Current claim**: "3 formats at D1 depth (model properties compared)"
**Actual state**: "3 formats at D0 depth (no real comparison, only load didn't crash)"

**Risk**: Product regressions in dif/fodt/sylk parsers would still PASS the oracle (load succeeds
but produces wrong values) because no real properties are checked.

---

### FG2 (HIGH): G2 test-suite fallback bypasses oracle

**Mechanism**: gate_executor.py lines 119-136.
```python
using_fallback = (passed_cases == 0) and (test_count >= 10)
if using_fallback:
    results.append({"check": "oracle_depth_minimum_d1", "passed": True, ...})
```
When `passed_cases == 0`, any format with ≥10 test files passes G2 regardless of oracle state.
The gate output reports `oracle_depth_minimum_d1: True` — false claim.

**Current impact**: As of 2026-07-08 baseline, NO format has 0 oracle PASS. All 20 formats have
active oracle runs. The fallback is NOT currently hiding any gap.

**Risk**: If oracle runs are not re-executed after a CI environment change (e.g., LibreOffice removed,
package installed differently), oracle pass counts could drop to 0 for some formats. The fallback
would silently preserve G2 PASS even with zero oracle evidence.

**Additional risk**: The gate output claiming `oracle_depth_minimum_d1: True` via the fallback is
a structural lie — it reports oracle depth evidence when none exists.

---

### FG3 (HIGH): Stale evidence accepted indefinitely

**Mechanism**: oracle-run-summary.json has no `product_source_hash`. There is no staleness check
in gate_executor.py check_g2().

**Current impact**: Since all 20 formats were re-run today (2026-07-08), all summaries are fresh.

**Risk**: Any product source change that happens AFTER the last oracle run leaves stale summaries
in place. CI never detects the gap. The `executed_at` timestamp is recorded but never compared
against `git log --since=` or any source modification time.

---

### FG4 (MEDIUM): Invalid and roundtrip cases unexecuted for 18 formats

**Mechanism**: run_oracle_for_format() lines 1737-1755.
```python
if format_id in ("csv", "fods"):  # only 2 formats
    for case in pkg.get("invalid_cases", []):
```
18 of 20 formats have `invalid_cases` defined but never executed.

**Current impact**: "73/75 PASS" count (as of today) reflects only valid cases for 18 formats.
Invalid case testing is absent. ZST has 4 invalid cases defined — all unexecuted.

**Risk**: A parser that accepts invalid input (should reject it) would PASS the oracle because
invalid rejection is never tested for 18 formats.

---

### FG5 (LOW-MEDIUM): format_depth = max hides D0 distribution

**Mechanism**: run_oracle_for_format() line ~1764: `format_depth = max(valid_pass_depths)`.
V143 validator only fires when depth == "D0" (all cases D0).

**Current impact**: A format with 1 D1 case and 9 D0 cases reports format_depth = D1. V143 does
not fire. FODS itself has 6 D1 + 4 D0 — the 4 D0 cases are invisible at the format level.

---

## Format-Level Honest Assessment

| Format | Claimed | Honest | Notes |
|---|---|---|---|
| csv | D1, VERIFIED | D1, VERIFIED | Real discriminating properties |
| fods | D1, VERIFIED | D1, PARTIAL | 4/10 D0 cases hidden by max; RT and invalid execute |
| zst | D1, VERIFIED | D1, VERIFIED | 4 invalid cases unexecuted (hidden coverage gap) |
| gnumeric | D1, VERIFIED | D1, PARTIAL | 1/3 cases synthetic loaded |
| ndjson | D1, VERIFIED | D1, PARTIAL | 1/4 NO_SCHEMA case |
| ods | D1, VERIFIED | D1, PARTIAL | 1/3 cases synthetic loaded |
| toml | D1, VERIFIED | D1, PARTIAL | 1/4 NO_SCHEMA case |
| tsv | D1, VERIFIED | D1, PARTIAL | 1/4 NO_SCHEMA case |
| xcf | D1, VERIFIED | D1, PARTIAL | 2/3 cases synthetic loaded |
| fodg | D1, VERIFIED | D1, WEAK | is_fodg boolean + page_count (real but weak) |
| fodp | D1, VERIFIED | D1, WEAK | Only is_fodp boolean (real but weak) |
| odt | D1, VERIFIED | D1, WEAK | Only ok boolean (real but always True) |
| pbm | D1, VERIFIED | D1, WEAK | Only ok boolean |
| pgm | D1, VERIFIED | D1, WEAK | Only ok boolean |
| ppm | D1, VERIFIED | D1, WEAK | Only ok boolean |
| qoi | D1, VERIFIED | D1, WEAK | Only ok boolean |
| abw | D1, VERIFIED | D1, MISMATCH | 2/3 cases use assertion: schema (runs at D0) |
| dif | D1, VERIFIED | **D0, INFLATED** | ALL 3 cases synthetic loaded → will drop after Fix 1 |
| fodt | D1, VERIFIED | **D0, INFLATED** | ALL 3 cases synthetic loaded → will drop after Fix 1 |
| sylk | D1, VERIFIED | **D0, INFLATED** | ALL 3 cases synthetic loaded → will drop after Fix 1 |

---

## Overall Verdict

```
OVERALL_ORACLE_READINESS: PARTIAL_PASS_WITH_DOCUMENTED_FALSE_GREENS

Certification claim: "20/20 formats VERIFIED at D1+"
Honest assessment:   "17/20 formats have at least one real D1 property comparison.
                      3 formats (dif, fodt, sylk) claim D1 via synthetic inflation only.
                      18/20 formats have unexecuted invalid cases.
                      All formats lack product source hash — stale evidence undetectable."

The architecture is sound. The defects are specific and fixable.
Proceed with 6 targeted fixes in oracle-architecture-implementation-plan.md.
```

# Oracle Pilot Designs — Format Factory
# Produced by: TC-ORA-009 (jaunty-whistling-meteor investigation)
# Generated: 2026-07-08
# All pilots are grounded in actual code paths. No hypothetical scenarios.

---

## Pilot 1: Oracle Boundary Separation
**Question**: Can the acquisition oracle produce VERIFIED_INTEROPERABILITY evidence without that
evidence being treated as SPEC_NORMATIVE by the product oracle?

**Evidence path**: `oracle/formats/fods/oracle-package.yaml`, `interoperability_cases` section.
These cases carry `authority_class: VERIFIED_INTEROPERABILITY`. The check_authority() function in
execute_oracle.py does NOT block VERIFIED_INTEROPERABILITY (only blocks AI_DRAFT_UNVERIFIED etc.).

**Pass condition**: A VERIFIED_INTEROPERABILITY case PASSes in execute_oracle.py without being
escalated to SPEC_NORMATIVE. The oracle-run-summary.json records D1 for that case.
The verdict JSON for the case shows `authority_status: "AUTHORITY_OK"` (not BLOCKED).

**Verification**: Run `python tools/oracle/execute_oracle.py --format fods --case fods-lo-interop-001`.
Inspect `.local/oracle/fods/verdicts/fods-lo-interop-001.json`.

**Result**: PASS (design is correct — boundaries are enforced by authority_class, not oracle boundary)

---

## Pilot 2: Authority Class Enforcement
**Question**: Does check_authority() correctly block AI_DRAFT_UNVERIFIED cases?

**Evidence path**: `tools/oracle/execute_oracle.py`, `check_authority()` function, lines 46-90.

**Test**: Create a temporary oracle case with `authority_class: AI_DRAFT_UNVERIFIED`.
Run the executor. Expected: `result = BLOCKED_MISSING_AUTHORITY`.

**Pass condition**: Case returns BLOCKED_MISSING_AUTHORITY, not PASS.
The gate-check-results.json for this case shows blocked.

**Already verified by**: test_r31_ai_system_verification.py (confirms block mechanism works)

---

## Pilot 3: Fix 1 Pre/Post Depth Change (dif)
**Question**: After applying Fix 1 (SYNTHETIC_PROPERTIES), does dif correctly drop to D0?

**Pre-state** (baseline): dif depth_histogram = {D1: 3}, format_depth_score = D1.
All 3 cases check `loaded: true` only.

**Steps**:
1. Apply Fix 1: add `SYNTHETIC_PROPERTIES = frozenset({"loaded", "result_type"})` and change
   line 713 to `depth = DEPTH_D1 if real_comparisons else DEPTH_D0`
2. Run `python tools/oracle/execute_oracle.py --format dif`
3. Read `oracle/formats/dif/reports/oracle-run-summary.json`

**Expected post-state**: depth_histogram = {D0: 3}, format_depth_score = D0.
V143 fires with WARN for dif.

**Pass condition**: format_depth_score changes from D1 to D0. V143 WARN present.

---

## Pilot 4: Fix 1 Non-Regression (fods)
**Question**: After applying Fix 1, does fods retain D1 (real properties should not be affected)?

**Pre-state**: fods depth_histogram = {D1: 6, D0: 4}, format_depth_score = D1.
fods cases check sheet_count, cell_count, first_sheet_name, has_formula_cell, spec_qname.

**Post-state after Fix 1**: Same as pre-state. The SYNTHETIC_PROPERTIES set only removes `loaded`
and `result_type`. fods cases do not check these synthetic properties.

**Pass condition**: fods oracle-run-summary.json is identical to pre-Fix-1 (except executed_at).

---

## Pilot 5: Fix 2 G2 Gate Behavior Change
**Question**: After removing the test-suite fallback, does G2 correctly evaluate oracle evidence only?

**Setup**: Run `python tools/supervisor/gate_executor.py --format csv --gates G1,G2 --dry-run`
before and after applying Fix 2.

**Expected behavior before Fix 2**: G2 passes for csv via oracle results (passed_cases=5 > 0).
The fallback code path is not reached.

**Expected behavior after Fix 2**: G2 passes for csv via the same oracle results. No change
for formats with PASS > 0.

**Critical test**: Temporarily set `passed_cases = 0` in a test copy of the gate executor.
Before Fix 2: G2 PASSES via fallback if test_count >= 10.
After Fix 2: G2 FAILS (no fallback).

**Pass condition**: Without the fallback, formats with 0 oracle PASS fail G2 (correct).

---

## Pilot 6: Fix 3 Staleness Detection
**Question**: Does the product_source_hash correctly identify stale oracle evidence?

**Steps**:
1. Apply Fix 3: add product_source_hash to oracle-run-summary.json during oracle run.
2. Run `python tools/oracle/execute_oracle.py --format csv`. Verify summary has product_source_hash.
3. Modify a CSV source file: add a comment to `src/python/csv/csv_codec.py`.
4. Run gate_executor G2 check for csv WITHOUT re-running oracle.
5. Check gate-check-results.json.

**Expected**: G2 PASSES (stale_warning is informational, not blocking), but gate result includes
`stale_warning: true` and shows the hash mismatch.

**Pass condition**: stale_warning: true appears in gate check output. G2 still passes (not blocked).
After re-running oracle: stale_warning: false.

---

## Pilot 7: Reference Divergence (LibreOffice vs Spec)
**Question**: When LibreOffice's behavior disagrees with the ODF spec, which authority wins?

**Evidence path**: `acquisition-packs/fods/gate6-oracle-comparison-report.md`.
The acquisition oracle recorded 1 WARN for multi-sheet FODS export. LibreOffice exports
multi-sheet FODS to a single CSV file. The ODF spec does not restrict multi-sheet semantics.

**Classification**: `REFERENCE_DIVERGENCE` — LibreOffice behavior, not spec-required behavior.

**Test**: The product oracle (execute_oracle.py) has fods-valid-002 which checks `sheet_count == 1`
for a single-sheet sample. This is SPEC_NORMATIVE evidence, not from LibreOffice.

**Pass condition**: If LibreOffice's CSV export disagrees with our parser's sheet_count,
the SPEC_NORMATIVE case takes precedence. The product oracle PASSES based on spec, not LibreOffice.
The acquisition oracle WARN is recorded but does not override SPEC_NORMATIVE evidence.

---

## Pilot 8: G2 Full Chain Pass
**Question**: With all fixes applied (Fix 1-3), does the G2 chain correctly identify
a well-covered format (csv) as passing and a synthetic-only format (dif) as failing?

**For csv after all fixes**:
- oracle_verdicts_exist: True (5/5 PASS)
- oracle_depth_minimum_d1: True (real properties: headers, row_count, column_count)
- product_source_hash: present and current
- stale_warning: False

**For dif after Fix 1**:
- oracle_verdicts_exist: True (3/3 PASS)
- oracle_depth_minimum_d1: False (all D0 after Fix 1)
- G2 FAILS for dif

**Pass condition**: csv G2 = PASS, dif G2 = FAIL (after Fix 1 is applied and oracle re-run).

---

## Pilot 9: Upstream Change Invalidates Downstream
**Question**: Does modifying oracle-package.yaml cause stale detection in G2?

**Steps**:
1. Apply Fix 3 to include oracle_package_hash in summary.
2. Run oracle for csv: note oracle_package_hash in summary.
3. Modify `oracle/formats/csv/oracle-package.yaml`: change one expected value.
4. Run G2 gate check WITHOUT re-running oracle.

**Expected**: oracle_package_hash in summary differs from current package hash.
Gate output: `stale_warning: true`.

**Pass condition**: Modification of oracle-package.yaml triggers staleness warning.
Oracle re-run clears the warning.

---

## Pilot 10: Fix 5 Assertion Schema Upgrade (abw)
**Question**: After applying Fix 5 (read assertion: schema), do abw cases correctly execute at D1?

**Pre-state**: abw-valid-001 and abw-valid-002 use `assertion: {expect_type: dict}`.
Current behavior: executor gets expected_model_properties=[] → D0, PASS without comparison.

**Post-state after Fix 5**: executor reads assertion: block, verifies result_val is a dict.
If abw parser returns dict → PASS at D1.
If abw parser returns non-dict → FAIL at D1.

**Steps**:
1. Apply Fix 5 to execute_generic_load_case.
2. Run `python tools/oracle/execute_oracle.py --format abw`.
3. Check oracle-run-summary.json depth_histogram.

**Expected**: depth_histogram changes from {D0: 2, D1: 1} to {D1: 3}. All cases at D1.

**Pass condition**: abw depth_histogram = {D1: 3} after Fix 5. No regression for abw-valid-003.

---

## Pilot 11: Idempotent Oracle Runs
**Question**: Does running the oracle twice in a row produce identical output (excluding executed_at)?

**Steps**:
1. Run `python tools/oracle/execute_oracle.py --format csv`. Copy oracle-run-summary.json as baseline.
2. Run again immediately.
3. Compare: all fields except executed_at must be identical.

**Pass condition**: pass_rate, depth_histogram, format_depth_score, results dict, verdict — all identical.
Only executed_at changes.

**Known potential non-idempotency**: If oracle-package.yaml sha256 uses filesystem timestamp instead
of content hash, two runs on the same machine would produce identical oracle_package_hash. ✓

---

## Pilot 12: No External Reference (CSV)
**Question**: Can the product oracle produce valid D1 evidence for a format with no LibreOffice
acquisition oracle and no RelaxNG schema (D2)?

**Format**: CSV. No LibreOffice oracle. No RelaxNG. Uses SPEC_NORMATIVE (RFC 4180) only.

**Evidence path**: `oracle/formats/csv/oracle-package.yaml` — 5 valid cases, 2 invalid cases.
All use SPEC_NORMATIVE or ACCEPTED_EMPIRICAL authority. Zero VERIFIED_INTEROPERABILITY cases.

**Pass condition**: CSV oracle produces 5/5 PASS at D1 using only SPEC_NORMATIVE and ACCEPTED_EMPIRICAL
evidence. No external reference implementation required. format_depth_score = D1.

**Already passing**: This is the current state. Pilot 12 confirms the architecture supports formats
without LibreOffice or schema validation.

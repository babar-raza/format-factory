# Adversarial Review — Oracle Architecture
# Produced by: TC-ORA-010 (jaunty-whistling-meteor investigation)
# Generated: 2026-07-08
# Requirement: At least 2 design changes must result from this review.

---

## Challenge 1: Is Fix 1 Actually Correct?

**Challenge**: The `loaded: true` fix removes depth credit for any case that only checks `loaded`.
But what if a format's parser is so simple that "loaded successfully" IS the correct depth level?
For DIF, SYLK, FODT — these formats have parsers that load and return data, but checking
"loaded: true" is a real verification for formats where partial loading (returning None or raising)
is a common failure mode.

**Code-grounded analysis**:

The key question is whether `result_val is not None` is a real comparison or a no-op.

In execute_generic_load_case (execute_oracle.py), if the parser raises an exception, the
exception is caught and the case returns FAIL. If it returns None, the case returns FAIL
(not-loaded → deviation). The `loaded: true` property check adds no new information:
if we reach `_compare_model_properties(result_val, ...)`, result_val is already guaranteed
to be non-None (otherwise the exception handler already returned FAIL).

So `loaded: true` is truly synthetic: the comparison `result_val is not None` can only
ever be True at the point where it's checked.

**Verdict**: Fix 1 is correct. `loaded: true` earning D1 is inflated. However —

**Design change required**:

The fix must not cause existing PASS verdicts to suddenly show FAIL. Dif/fodt/sylk cases
will change from D1 → D0 in the verdict, but the `result` field should remain PASS (load succeeded).
The `depth_level` field changes from D1 to D0. V143 fires. G2 still passes (depth_ok = D0 < D1
means G2 FAILS for these formats after Fix 1). **This means Fix 1 WILL break G2 for dif, fodt, sylk.**

**DESIGN CHANGE 1**: The implementation plan must explicitly sequence Fix 1 before or after
oracle package upgrades for dif/fodt/sylk. If Fix 1 is applied without upgrading the oracle
packages, dif/fodt/sylk will fail G2. The plan must include a follow-on task to add real
model property comparisons to these three oracle packages before or immediately after Fix 1.

**Revised Fix 1 plan**:
1. Implement Fix 1 in execute_oracle.py (code change only)
2. IMMEDIATELY run oracle for all 20 formats to confirm which drop to D0 (baseline known: dif, fodt, sylk)
3. BEFORE any G2 checks: upgrade oracle packages for dif, fodt, sylk to add real model properties
4. Re-run oracle for those 3 formats
5. Now run G2 checks — all 3 should now pass at D1

This is a sequencing constraint on Fix 1, not a change to the fix itself.

---

## Challenge 2: Is Removing the G2 Fallback Too Aggressive?

**Challenge**: The G2 fallback was designed to handle CI environments without LibreOffice.
If the fallback is removed and LibreOffice disappears from CI, formats that depended on
LibreOffice for some oracle cases might fail G2 even though their non-LibreOffice cases all pass.

**Code-grounded analysis**:

The fallback triggers when `passed_cases == 0`. In the 2026-07-08 baseline, NO format has
0 oracle PASS. The LibreOffice-dependent case (fods-lo-interop-001) returns SKIPPED_MISSING_PROVIDER,
not FAIL. This means fods still has 9/10 PASS even without LibreOffice.

SKIPPED_MISSING_PROVIDER is NOT counted in `passed_cases`:
```python
passed_cases = summary.get("results", {}).get("PASS", 0)
```
SKIPPED doesn't increment PASS count but also doesn't set passed_cases to 0.

**So the fallback would only trigger if ALL oracle cases returned non-PASS results** — not just
the LibreOffice case. This is an extreme scenario (all samples missing + all calls failing).

**Verdict**: Removing the fallback is correct. The SKIPPED_MISSING_PROVIDER mechanism already
handles the LibreOffice-absent case correctly.

**But there's a subtler issue**: The current fallback reads `test_count >= 10` from the
`tests/python/{format_id}/` directory. If somehow ALL oracle cases became SKIPPED (not just
LibreOffice cases), the fallback would pass G2. This is what the fallback was designed for.
However, if all cases are SKIPPED, G2 should FAIL — there is no oracle evidence at all.

**Verdict unchanged**: Fix 2 (remove fallback) is correct.

---

## Challenge 3: Does the Registry Approach (Fix 4) Actually Solve the Coverage Gap?

**Challenge**: Fix 4 replaces the if/elif dispatch chain with a registry dict. But the registry
alone doesn't add invalid/roundtrip coverage for 18 formats — it just makes the dispatch cleaner.
You still need per-format invalid case executors or a generic invalid executor.

**Code-grounded analysis**:

This is exactly right. Fix 4 enables coverage but doesn't deliver it alone. After Fix 4:
- `INVALID_CASE_EXECUTORS.get(format_id)` returns None for 18 formats
- The new dispatch loop does `if exec_fn is None: continue`
- Invalid cases are still not executed for those 18 formats

Fix 4 must be paired with EITHER:
(a) A generic invalid case executor that works for all formats (checks that an exception is raised)
(b) Per-format invalid executors registered for each format

Option (a) is the pragmatic path: most `invalid_cases` in oracle packages expect an exception
to be raised (the input is malformed). A generic executor can:
1. Load the sample (or inline content)
2. Expect an exception to be raised
3. PASS if exception raised, FAIL if no exception

**DESIGN CHANGE 2**: Fix 4 must include a `execute_generic_invalid_case()` function that handles
the common invalid case pattern (expects exception). This turns Fix 4 from "enable registry" into
"enable registry + deliver basic invalid coverage for all formats."

**Concrete implementation**:
```python
def execute_generic_invalid_case(case: dict, pkg: dict, format_id: str, module: str, callable_name: str) -> dict:
    """Generic invalid case: expects the callable to raise an exception."""
    input_ref = case.get("input_ref") or case.get("input_inline")
    try:
        fn = ...import callable...
        fn(input_ref or inline_content)
        # If we reach here: exception was NOT raised → FAIL
        return make_verdict(..., result=RESULT_FAIL, diagnostics=["Expected exception not raised"])
    except Exception:
        return make_verdict(..., result=RESULT_PASS, depth_level=DEPTH_D0)
```

This is D0 (no model property comparison — only exception expectation), not D1. But it
is a real comparison: it verifies the parser rejects invalid input. It covers OGAP-005.

---

## Challenge 4: Is the specification oracle formalization (SAL provenance) cosmetic?

**Challenge**: Adding `review_level: manual_extraction_run030` to SAL facts doesn't validate
the fact text against the spec. A fact that says "cells are table:table-cell children" could
be wrong — adding a `reviewed_at` date doesn't verify it's correct.

**Verdict**: This is correct. The provenance field is honest metadata, not machine verification.
The value is:
1. It makes the current state of facts explicitly declared (not implied)
2. It enables future auditing by encoding WHEN the extraction was done
3. It allows oracle-package.yaml to reference SPECIFIC fact IDs (not string comments)
4. It does NOT claim the facts are spec-validated

This is not cosmetic — it's the minimum honest representation. But it also doesn't close
the gap between "agent extracted from spec" and "spec-validated."

**No design change required here.** The framing in the plan is honest.

---

## Challenge 5: Can `ok: True` actually fail?

**Challenge**: odt, pbm, pgm, ppm, qoi all check `ok: True`. The plan classifies these as D1
(real returned field) because `ok` is returned by the parser. But if `ok` is always True when
the parser doesn't throw an exception, is this any different from `loaded: true`?

**Code-grounded analysis**:

From `odt/odt_parser.py` (inferred from parser output `{'ok': True, 'error': None}`):
The `ok` field is set to `True` in the success path. There is a non-exception failure mode:
if the parser returns `{'ok': False, 'error': 'malformed XML'}` without raising, then
`ok: True` comparison would catch it.

This is a real distinction from `loaded: true`. `loaded: true` is computed by the ORACLE
framework (`result_val is not None`), not by the parser. `ok: True` is computed by the PARSER
and is in the returned dict. If the parser has a bug where it returns `{'ok': False}` on
certain inputs, the oracle would catch it.

**However**: In practice, for these formats (odt, pbm, pgm, ppm, qoi), the parser likely
always returns `ok: True` on success path because `ok: False` would typically be paired
with raising an exception. The discriminating power is near-zero in practice.

**Verdict**: Fix 1 correctly EXCLUDES `loaded` and `result_type` (oracle-computed synthetic).
Fix 1 CORRECTLY INCLUDES `ok`, `is_fodp` etc. as real (parser-returned). They are D1 by
the technical definition. Their practical value is low, but that is an oracle package upgrade
concern (add real properties), not a Fix 1 concern.

**No design change required for Fix 1 scoping.** But oracle package upgrades for odt/pbm/pgm/ppm/qoi
should add real structural properties (width, height, pixel_count, etc.) to genuinely improve D1 quality.

---

## Summary of Design Changes from Adversarial Review

**DESIGN CHANGE 1 (from Challenge 1)**: Fix 1 implementation must be accompanied by an oracle
package upgrade task for dif, fodt, sylk. The sequencing constraint is:
  - Implement Fix 1 code change
  - Immediately run baseline to confirm which formats drop to D0
  - Upgrade oracle packages for affected formats with real model properties
  - Re-run oracle to confirm D1 restored
  - THEN proceed with G2 checks

This prevents Fix 1 from causing a visible pipeline failure without a path to resolution.

**DESIGN CHANGE 2 (from Challenge 3)**: Fix 4 (registry) must include implementation of
`execute_generic_invalid_case()` that handles the common "expect exception" pattern. This
makes Fix 4 deliver actual coverage improvement (not just structural refactoring).
Without this, Fix 4 is cosmetic — it cleans the dispatch but adds no value.

These two design changes are now incorporated into the implementation plan (TC-ORA-011).

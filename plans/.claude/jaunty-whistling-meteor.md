# Oracle System Investigation and Production Design
# Plan: jaunty-whistling-meteor
# Type: investigation_and_design
# Mission ID: FF-ORACLE-INVEST-001

## Taskcard Status Summary

| TC-ID | Status |
|---|---|
| TC-ORA-001 | CLOSED |
| TC-ORA-002 | CLOSED |
| TC-ORA-003 | CLOSED |
| TC-ORA-004 | CLOSED |
| TC-ORA-005 | CLOSED |
| TC-ORA-006 | CLOSED |
| TC-ORA-007 | CLOSED |
| TC-ORA-008 | CLOSED |
| TC-ORA-009 | CLOSED |
| TC-ORA-010 | CLOSED |
| TC-ORA-011 | CLOSED |
| TC-ORA-012 | CLOSED |

---

## Context

This plan was requested with a "treat this as a production problem" standard. The objective is to
investigate the current oracle system, identify the root causes of inconsistency and false-green
results, design a production-grade solution, and produce a hardened execution plan for implementation.

The investigation must not implement the final architecture — only authorize it through a final
hardened plan that a subsequent execution can use.

---

## Part 1 — Diagnostic Analysis

### 1.1 What the Code Actually Does (vs What It Claims)

The following is based on reading the actual source, not documentation:

**`tools/oracle/execute_oracle.py`** (1,822 lines)

The central issue is in `_compare_model_properties()` at line 664:

```python
def _compare_model_properties(result_val, expected_props: list) -> tuple[dict, list, str]:
    observed = {"loaded": True, "result_type": type(result_val).__name__}
    ...
    if prop_name == "loaded":
        actual = result_val is not None   # ← synthetic: if no exception, always True
    ...
    depth = DEPTH_D1 if expected_props else DEPTH_D0
```

This means:
- Any case with even one `expected_model_properties` entry (including `loaded: true`) earns D1
- `loaded: true` is a synthetic boolean computed from "we didn't crash" — not a real model property
- The depth system intends D1 = "model properties compared" but allows `loaded: true` to satisfy that

**`oracle/formats/fods/reports/oracle-run-summary.json`** (actual file):
```json
"depth_histogram": {"D1": 6, "D0": 4},
"format_depth_score": "D1"
```

**`run_oracle_for_format()` at line 1764-1770:**
```python
format_depth = max(valid_pass_depths, default=DEPTH_D0)
```
One D1 verdict out of 10 cases is sufficient to report format_depth = D1. The distribution
(4 out of 10 at D0) is invisible to V143 or the G2 gate.

**`tools/supervisor/gate_executor.py` lines 119–136:**
```python
using_fallback = (passed_cases == 0) and (test_count >= 10)
if using_fallback:
    results.append({"check": "oracle_depth_minimum_d1", "passed": True,
        "detail": f"depth={depth} (fallback: {test_count} test files ...)"})
```
When `passed_cases == 0` (no oracle verdicts at all), G2 passes if ≥10 test files exist.
The fallback reports `oracle_depth_minimum_d1: True` even though depth is whatever the last
run recorded (often D0 or absent). This is a lie in the gate output.

**`oracle/formats/abw/oracle-package.yaml` (read directly):**
```yaml
valid_cases:
  - case_id: abw-valid-001
    assertion:
      type: python_callable
      expect_type: dict
      expect_no_exception: true
    authority_ref: FACT-ABW-001
```

There is NO `expected_model_properties` key — the ABW package uses `assertion:` syntax.
But `execute_generic_load_case` (called by `execute_abw_valid_case`) reads:
```python
expected_props = case.get("expected_model_properties", [])
```
`assertion:` is silently ignored. Result: ABW cases run `load()`, find no properties to compare,
return D0 PASS. The `assertion:` schema is unread.

**`run_oracle_for_format()` lines 1737–1755:**
```python
if format_id in ("csv", "fods"):
    for case in pkg.get("invalid_cases", []):
```
Invalid cases only execute for `csv` and `fods`. All other formats have `invalid_cases` defined
in their oracle packages but those cases are never executed.

**Roundtrip cases lines 1694–1735:**
```python
if format_id == "fods":
    for case in pkg.get("roundtrip_cases", ...):
if format_id == "zst":
    for case in pkg.get("roundtrip_cases", ...):
```
Roundtrip cases only execute for `fods` and `zst`. Other formats' roundtrip cases are never run.

---

### 1.2 Symptoms vs Root Causes vs Structural Weaknesses

**SYMPTOMS (visible outcomes):**

- S1: All 20 formats report `format_depth_score: D1` or better
- S2: "73/73 PASS" is claimed across all formats
- S3: G2 passes for all 20 formats
- S4: Certification report says 20/20 CERTIFIED
- S5: Oracle-run-summary.json dates from 2026-07-07 and is treated as current evidence

**ROOT CAUSES (direct causes of specific symptoms):**

- RC1 (causes S1): `_compare_model_properties()` treats `loaded: true` (a synthetic
  property computed from `result_val is not None`) as a real D1 property. Any case with
  one such entry earns D1 even if the comparison is trivial.

- RC2 (causes S2, S4): 13 of 20 formats use `execute_generic_load_case()`. Their oracle
  packages define `invalid_cases` and `roundtrip_cases` but the executor never runs them
  (`format_id in ("csv", "fods")` guard). The "73/73 PASS" count excludes these cases by
  never attempting them.

- RC3 (causes S2, S4): ABW and potentially other formats use `assertion:` syntax that
  execute_oracle.py does not read. These cases return D0 PASS without any comparison.

- RC4 (causes S3): The G2 test-suite fallback in gate_executor.py (lines 119-136)
  grants `oracle_depth_minimum_d1: True` to formats with 0 oracle verdicts if ≥10 test
  files exist. This removes the oracle requirement for well-tested formats.

- RC5 (causes S5): oracle-run-summary.json carries no `product_source_hash`. When
  product source changes, the old summary remains valid evidence indefinitely. There is
  no staleness check anywhere in the pipeline.

**STRUCTURAL WEAKNESSES (architectural problems producing multiple root causes):**

- SW1 (produces RC2): Format dispatch is an if/elif chain (lines 1638-1685) with per-format
  guards for roundtrip and invalid cases. Adding a new case type for any format requires
  finding and editing 3 separate sections of a 1,822-line file. Currently only FODS and
  ZST handle roundtrip; only CSV and FODS handle invalid cases. This is not an oversight
  — it is structural: the dispatch pattern cannot run case types unless explicitly coded
  for each format.

- SW2 (produces RC3): Two incompatible oracle-package schemas coexist: the `expected_model_properties`
  schema (used by FODS, CSV, ZST, TSV, NDJSON, TOML) and the `assertion:` schema (used by
  ABW and possibly others). The executor reads only `expected_model_properties`. Formats using
  `assertion:` get D0 PASS without any real comparison. There is no schema validation that
  would catch this mismatch at oracle-package load time.

- SW3 (produces RC1, RC5): The depth system (D0-D3) has no enforcement. "D1" is supposed
  to mean "model properties compared" but is satisfied by a synthetic boolean. "D3" means
  "external tool interop" but the only D3 implementation is the LibreOffice FODS case, which
  is SKIPPED when LibreOffice is absent. Format depth score = max, not median or min. The
  governance validator (V143) only fires when ALL cases are D0.

- SW4 (produces RC4): The G2 fallback was designed as a safety valve for LibreOffice
  unavailability, but it is applied unconditionally: any format with 0 oracle PASSes
  and ≥10 test files passes G2. This inverts the purpose of the gate. LibreOffice-dependent
  cases should use `SKIPPED_MISSING_PROVIDER`, which already exists, not a complete bypass.

- SW5 (broader): The specification oracle and capability oracle do not exist. The SAL facts
  (14,441 extracted) were produced once (run030) and are never re-validated. The capability
  maps reference fact IDs but there is no code path that rejects a capability without facts
  or verifies a fact against the spec text. These absences are not urgent for fixing the
  product oracle, but they mean the authority chain from spec → facts → capabilities → product
  is broken at its first two links.

---

### 1.3 What Is Actually Breaking Consistency Across Reruns

**The primary source of inconsistency:**

The oracle-run-summary.json is committed to the repository and treated as permanent
evidence. There is no mechanism to detect that the product source has changed since
the last run. When oracle reruns:
- If the product hasn't changed: same PASS results, summary overwritten with new `executed_at`
- If the product has regressed: FAIL results appear, summary is updated, pipeline sees failures
- If oracle was not rerun after a change: stale summary remains, pipeline sees old PASSes

The pipeline has no way to distinguish "all cases passed in a recent run" from "all cases
passed in a run from 6 weeks ago before the product was rewritten." The `executed_at`
timestamp is recorded but never checked against anything.

**The secondary source:** The G2 fallback. Reruns that happen to see different test file
counts (e.g., after test files are added or deleted) can change G2 results without any
oracle being run. This is non-deterministic from the oracle's perspective.

**The tertiary source:** SKIPPED_MISSING_PROVIDER is deterministic on a given machine
(if LibreOffice is installed or not), but the committed summary reflects the state when
oracle was last run — which may not match the current environment. A developer on a
machine with LibreOffice may see different G2 results than CI without LibreOffice.

---

### 1.4 What Must Be Preserved

These mechanisms are well-designed and must be kept intact:

| Component | Location | Why Preserve |
|---|---|---|
| Authority class blocking | execute_oracle.py:46, check_authority() | Prevents self-approval, correct design |
| make_verdict() schema | execute_oracle.py:92-136 | Well-structured, all fields needed |
| oracle-package.yaml structure | oracle/formats/{fmt}/ | The declarative case definition approach is sound |
| per-case authority_refs (spec section citations) | oracle-package.yaml valid_cases | Human-readable spec linkage |
| ODF RelaxNG D2 validation | tools/oracle/schema_validator.py | Genuine spec-based verification |
| Acquisition oracle separation | run_fods_oracle.py, oracle-package.yaml comment | LibreOffice ≠ spec authority — correct |
| SKIPPED_MISSING_PROVIDER result | execute_oracle.py:58 | Correct handling for optional external tools |
| oracle-run-summary.json as committed evidence | oracle/formats/{fmt}/reports/ | Committed, reviewable, diff-able — keep |
| SPEC_NORMATIVE / SCHEMA_DERIVED authority classes | oracle-authority-policy.md | Clear, correct hierarchy |

---

### 1.5 What Must Be Redesigned

| Problem | Current code | Required change |
|---|---|---|
| Synthetic property inflates D1 | `_compare_model_properties` line 683-685, 713 | `loaded` and `result_type` must not count toward D1 elevation |
| `assertion:` schema ignored | `execute_generic_load_case` line 751 | Read `assertion:` block; treat `expect_type` + `expect_no_exception` as D1-equivalent |
| Invalid/roundtrip cases not executed for most formats | `run_oracle_for_format` lines 1694-1755 | Move per-case-type dispatch to the executor registry, not the main loop |
| Format depth = max not representative | line 1770 | Report both max and D0_fraction; V143 should check D0_fraction > 0.5 |
| G2 test-suite fallback bypasses oracle | gate_executor.py lines 119-136 | Remove; LibreOffice-absent cases use SKIPPED_MISSING_PROVIDER which already passes G2 |
| No staleness detection | oracle-run-summary.json, no source hash | Add `product_source_hash` (SHA256 of parser entrypoint) and `oracle_package_hash` to summary |
| if/elif dispatch chain not scalable | lines 1638-1685 | Replace with EXECUTOR_REGISTRY dict |

---

## Part 2 — Acquisition Oracle Classification

**Classification: `ACQUISITION_IS_SEPARATE_INTEROPERABILITY_ORACLE`**

Traced from code (`run_fods_oracle.py`, `oracle-package.yaml` comments):
- Gate 6 compares prototype parser neutral model vs LibreOffice CSV export
- LibreOffice is a THIRD-PARTY REFERENCE IMPLEMENTATION, not the ODF specification
- The authority class for LibreOffice evidence is `VERIFIED_INTEROPERABILITY`, not `SPEC_NORMATIVE`
- The acquisition oracle answered: "does our prototype agree with LibreOffice?" at Gate 6
- The product oracle answers: "does our production library implement ODF 1.3?"
- These are distinct questions with distinct authorities

LibreOffice can and does violate the ODF specification in edge cases. Gate 6 evidence is
interoperability evidence. If LibreOffice's behavior disagrees with the ODF spec text, the
product oracle's SPEC_NORMATIVE cases take precedence.

**What this means for architecture:** The acquisition oracle should NOT be deprecated. It
provides `VERIFIED_INTEROPERABILITY` evidence that can feed into product oracle cases (and already
does — `fods-lo-*` interoperability_cases in oracle-package.yaml reference LibreOffice). But it
must be clearly scoped to pre-implementation validation and interoperability, never spec authority.

**Limitation:** Only FODS and FODT have acquisition oracles. 18 formats have no Gate 6 coverage
because LibreOffice doesn't meaningfully support them (image formats, compression, etc.). For
those formats, the product oracle must stand alone on SPEC_NORMATIVE and ACCEPTED_EMPIRICAL.

---

## Part 3 — Current Readiness Assessment

### Honest Scores (0-5 scale)

**Specification Oracle: Level 1 (AD_HOC)**

The SAL (14,441 facts) is the only specification knowledge layer. It was extracted in run030
and is not continuously maintained. Facts have section references (e.g., "ODF §9.4") but no
machine-verifiable proof that the claim matches the spec text. There is no acceptance workflow,
no continuous monitoring of spec version changes, and no fact rejection mechanism.

The oracle-package.yaml `authorized_fact_refs` field contains `"~4988 total FODS facts in SAL"`
as a string comment — not an actual list of fact IDs. This is documentation, not governance.

Strengths: SAL schema normalized, section references present, SHA256 of spec pinned in oracle package.
Gaps: No validation of fact text against spec, not triggered by spec changes, fact store gitignored.

**Capability Oracle: Level 0 (ABSENT)**

The gap-ledger.json (398 entries) maps capabilities to formats but has no proof validation
machinery. The capability_feature_compiler.py produces advisory output that is never consumed
by task generation. There is no mechanism to reject a capability claim for missing fact support.

**Product Oracle: Level 3 (GOVERNED_PARTIAL)**

execute_oracle.py is a real, working oracle with authority-class enforcement, structured verdicts,
per-case spec section citations, and a governed depth-scoring system. The problems (inflated depth,
missing case execution, no staleness) are fixable within the existing architecture. The architecture
itself is sound — it just has specific implementation defects.

Gaps: D1 inflation, case coverage gaps (invalid/roundtrip for 18 formats), no staleness, `assertion:`
schema ignored, G2 fallback.

**Acquisition Oracle: Level 2 (BASIC_REPEATABLE)**

FODS (3/4 PASS) and FODT (active) are implemented. Runs are reproducible when LibreOffice is
present. No mechanism for formats without LibreOffice support. Not production-grade because:
LibreOffice version is not strictly pinned, nondeterminism is not controlled for multi-sheet exports.

### Major False-Green Risks

**FG1 (HIGH): D1 depth claim is partially false.**
14 of 20 formats use `execute_generic_load_case`. Among those, some oracle packages use
`assertion:` syntax (unread by executor) and return D0 PASS, contributing nothing to D1.
Formats that only check `loaded: true` earn D1 on a trivial comparison. The "all 20 formats
at D1+" claim overstates what was actually compared.

**FG2 (HIGH): G2 can pass with zero oracle verdicts.**
Any format with ≥10 test files passes G2 regardless of oracle status. This makes the oracle
gate optional for any reasonably well-tested format. The gate output falsely reports
`oracle_depth_minimum_d1: True`.

**FG3 (MEDIUM): Stale evidence accepted indefinitely.**
oracle-run-summary.json has no source hash. Product regressions after the last oracle run
are invisible to the pipeline until someone reruns the oracle explicitly.

**FG4 (MEDIUM): Invalid and roundtrip cases not executed for 18/20 formats.**
The oracle packages define `invalid_cases` and `roundtrip_cases` for all formats, but the
executor only runs them for csv/fods/zst. All other formats have these cases defined but
unexecuted — the VERIFIED status reflects only valid_cases.

**FG5 (LOW-MEDIUM): format_depth = max hides D0 distribution.**
A format with 1 D1 case and 9 D0 cases reports format_depth = D1 and passes V143.
V143 only fires when ALL cases are D0.

---

## Part 4 — Target Architecture

### 4.1 Decisions

**Extend execute_oracle.py, do not replace it.** The authority class system, verdict schema,
and oracle-package.yaml approach are correct. Fix the specific implementation defects.

**Four oracle boundaries are real.** Do not collapse them:
1. Specification Oracle (SAL + fact validation) — currently AD_HOC, needs formalization
2. Capability Oracle — currently ABSENT, build separately, do not rush
3. Product Oracle (execute_oracle.py) — currently GOVERNED_PARTIAL, fix defects
4. Acquisition Oracle (Gate 6 LibreOffice) — currently BASIC_REPEATABLE, scope correctly

**Build only what is needed to fix the false-green paths.** The specification and capability
oracles are important but not the cause of current false-greens. Fix the product oracle first.
The specification oracle can be formalized incrementally by adding provenance fields to existing
SAL facts without rebuilding the pipeline.

### 4.2 Product Oracle Fixes (Concrete)

**Fix 1: Synthetic property must not elevate depth**

File: `tools/oracle/execute_oracle.py`, function `_compare_model_properties` (line 664)

```python
# ADD at module level
SYNTHETIC_PROPERTIES = frozenset({"loaded", "result_type"})

# MODIFY _compare_model_properties (around line 673-713):
# After building observed dict, determine depth:
real_comparisons = [
    p for p in expected_props
    if p.get("property") not in SYNTHETIC_PROPERTIES
]
depth = DEPTH_D1 if real_comparisons else DEPTH_D0
```

This change means `loaded: true` alone → D0. Any real property (sheet_count, row_count,
spec_qname, etc.) → D1. Synthetic properties can still be checked and cause FAIL if wrong,
but they don't earn D1.

**Expected impact:** ABW, GNUMERIC, DIF, FODG, ODS, SYLK, FODT, XCF, PBM, PPM, QOI, ODT,
FODP will likely drop from D1 to D0 if their oracle packages only check `loaded: true`.
This is the correct outcome — it reveals the actual current depth honestly.

**Regression control:** Run oracle for all formats before and after; record delta. Any format
that drops to D0 must have its oracle package upgraded in a follow-on task to add real property
comparisons.

---

**Fix 2: Remove G2 test-suite fallback**

File: `tools/supervisor/gate_executor.py`, function `check_g2` (lines 119-136)

Remove lines 119-136 entirely (the `using_fallback` block). Replace with:

```python
# Formats where cases are SKIPPED_MISSING_PROVIDER (e.g. LibreOffice not available)
# are handled by the existing logic: skipped != 0 passes, failed != 0 fails.
# Test files are not a substitute for oracle evidence.
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

**Risk:** Formats that had 0 oracle PASS and relied on the fallback will now fail G2. This
is intentional — it surfaces what was hidden. Each such format needs to run the oracle and
achieve real D1 coverage before G2 can pass.

**Tradeoff:** This may temporarily block release eligibility for some formats. That is acceptable
because those formats were never genuinely oracle-verified.

---

**Fix 3: Add source hash to oracle-run-summary.json**

File: `tools/oracle/execute_oracle.py`, function `run_oracle_for_format` (around line 1757)

Before writing the summary:
```python
# Compute product source hash (key parser file)
src_dir = REPO_ROOT / "src" / "python" / format_id
parser_candidates = list(src_dir.rglob("*parser*.py")) + list(src_dir.rglob("*codec*.py"))
source_hash = "unavailable"
if parser_candidates:
    h = hashlib.sha256()
    for f in sorted(parser_candidates):
        h.update(f.read_bytes())
    source_hash = f"sha256:{h.hexdigest()[:16]}"  # truncated for readability

pkg_path = ORACLE_DIR / "formats" / format_id / "oracle-package.yaml"
package_hash = sha256_file(pkg_path) if pkg_path.exists() else "unavailable"

summary = {
    ...
    "product_source_hash": source_hash,
    "oracle_package_hash": package_hash,
}
```

**Fix 3b:** In `gate_executor.py check_g2`, after reading the summary, add a staleness warning:
```python
current_source_hash = _compute_source_hash(format_id)  # same logic as above
stored_hash = summary.get("product_source_hash", "unavailable")
stale = (stored_hash != "unavailable" and stored_hash != current_source_hash)
```
Include `stale_warning: stale` in the gate result. G2 still PASSES (stale is a warning,
not a block) but the staleness is visible in gate-check-results.json.

---

**Fix 4: Fix the dispatch architecture**

File: `tools/oracle/execute_oracle.py`, around line 1608

Replace the if/elif chain (lines 1638-1685 in `run_oracle_for_format`) with a registry:

```python
# AT MODULE LEVEL (near the top, after imports):
VALID_CASE_EXECUTORS: dict[str, callable] = {}  # populated by register_executor()
INVALID_CASE_EXECUTORS: dict[str, callable] = {}
ROUNDTRIP_CASE_EXECUTORS: dict[str, callable] = {}

def register_executor(format_id: str, valid=None, invalid=None, roundtrip=None):
    if valid:   VALID_CASE_EXECUTORS[format_id] = valid
    if invalid: INVALID_CASE_EXECUTORS[format_id] = invalid
    if roundtrip: ROUNDTRIP_CASE_EXECUTORS[format_id] = roundtrip

# Registration calls (after each execute_* function is defined):
register_executor("csv", valid=execute_csv_valid_case, invalid=execute_csv_invalid_case)
register_executor("fods", valid=execute_fods_valid_case, invalid=execute_fods_invalid_case,
                  roundtrip=execute_fods_rt_case)
...

# IN run_oracle_for_format, replace the if/elif block:
exec_fn = VALID_CASE_EXECUTORS.get(format_id)
if exec_fn is None:
    exec_fn = lambda case, pkg: execute_generic_load_case(case, pkg, format_id, ...)
verdict = exec_fn(case, pkg)
```

This change also naturally enables running invalid_cases and roundtrip_cases for all
formats once those executors are registered — removing the coverage gap (SW1).

**This is a refactor, not a behavior change for currently-working formats.** Regression
control: run oracle for all 20 formats before and after; verify identical pass/fail counts.

---

**Fix 5: Read `assertion:` schema from oracle-package.yaml**

File: `tools/oracle/execute_oracle.py`, function `execute_generic_load_case` (line 717)

After `result_val = fn(str(sample_path))`:
```python
# Check assertion block (used in older oracle packages)
assertion = case.get("assertion", {})
if assertion:
    expect_type_name = assertion.get("expect_type")
    if expect_type_name:
        type_map = {"dict": dict, "list": list, "str": str, "int": int, "bool": bool}
        expected_type = type_map.get(expect_type_name)
        if expected_type and not isinstance(result_val, expected_type):
            return make_verdict(..., result=RESULT_FAIL,
                diagnostics=[f"Expected type {expect_type_name}, got {type(result_val).__name__}"])
    # Reaching here with assertion and expect_no_exception=True → real check, counts as D1
    if assertion.get("expect_no_exception"):
        # Mark as real comparison (equivalent to one non-synthetic property)
        # Override depth: assertion-based check is D1-equivalent
        ...
```

**Tradeoff:** This reads `assertion:` as a legacy schema compatibility layer. Ideally all packages
should be migrated to `expected_model_properties:`, but that is a follow-on task per format.

---

**Fix 6: V143 distribution-aware**

File: `tools/supervisor/governance_validators_oracle.py`, `validate_oracle_depth_minimum` (line 14)

Current: WARN only if `depth == "D0"` (all cases D0).
Change: also WARN if D0 count > D1+D2+D3 count (majority at D0).

```python
histogram = summary.get("depth_histogram", {})
d0_count = histogram.get("D0", 0)
d1_plus_count = sum(histogram.get(d, 0) for d in ("D1", "D2", "D3"))
majority_d0 = d0_count > d1_plus_count and d0_count > 0

if depth == "D0" or majority_d0:
    findings.append({...})
```

This fires on FODS (6 D1, 4 D0 → D0 is NOT majority, so no WARN — correct).
It would fire on a format with 1 D1 and 9 D0 (majority D0 → WARN — correct).

---

### 4.3 Specification Oracle Path (Incremental, Not Rebuild)

The SAL facts are valuable. They don't need to be rebuilt — they need provenance fields.

**Minimal formalization (no new tooling required):**

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

This is honest: `review_level: manual_extraction_run030` means "an agent read the spec and
extracted this, not formally validated." It acknowledges the current state without claiming
false rigor.

**What this enables:** oracle-package.yaml `authorized_fact_refs` can be validated at oracle
load time (check that FACT-FODS-001 exists in the SAL store and has a known `review_level`).
This is not a full specification oracle, but it is a real provenance check.

**What it does not do:** It does not validate the fact text against the spec. That requires
a human review or a separate automated pipeline. Do not claim it does more than it does.

---

### 4.4 Capability Oracle (Separate Project — Not Now)

The capability oracle requires:
- Formal capability acceptance criteria (what makes a capability "accepted"?)
- Proof obligation generation from decomposed capabilities
- Integration of gap-ledger.json into task generation

This is a substantial project. The current capability maps are advisory infrastructure.
The correct response is: document this as a known gap, assign it to a separate hardened plan,
and do not conflate it with fixing the product oracle.

**Immediate action:** Update the capability maps to explicitly say `confidence: advisory_only`
so that downstream consumers (certification, supervisor) know not to treat them as authoritative.

---

## Part 5 — Persistent Artifacts and State

### 5.1 Oracle-Run-Summary Schema Extension (Backward-Compatible)

Current fields remain. New fields (all optional, backward-compatible):
```json
{
  "oracle_id": "...",
  "format_id": "...",
  "executed_at": "...",
  "total_cases": 10,
  "results": {...},
  "pass_rate": "9/10",
  "verdict": "PARTIAL_PASS",
  "depth_histogram": {...},
  "format_depth_score": "D1",

  // NEW FIELDS (added by Fix 3)
  "product_source_hash": "sha256:ab12cd34...",  // truncated SHA256 of parser files
  "oracle_package_hash": "sha256:ef56gh78...",  // SHA256 of oracle-package.yaml
  "depth_d0_fraction": 0.4,                     // D0_count / total_valid_pass_cases
  "stale_since": null                            // set by G2 gate when source hash changes
}
```

No existing consumer breaks because new fields are additive.

### 5.2 Case State (Preserved from Current)

Current status lifecycle in format-oracle-registry.yaml is retained:
`OBLIGATION_CREATED → SCAFFOLDED → AUTHORITY_MAPPED → CASES_DEFINED → VERIFIED → PRODUCTION_ACTIVE`

After the fixes, VERIFIED requires:
- At least one non-synthetic D1+ case per declared profile
- All declared case types (valid, invalid, roundtrip) have executors registered
- No unread schema fields (no `assertion:` without executor support)

---

## Part 6 — Gap Register

| Gap ID | Category | Severity | Root Cause | Migration Stage |
|---|---|---|---|---|
| OGAP-001 | `loaded:true` inflates D1 | HIGH | RC1, SW3 | Fix 1 |
| OGAP-002 | G2 test-suite fallback | HIGH | RC4, SW4 | Fix 2 |
| OGAP-003 | No source-hash in summary | HIGH | RC5 | Fix 3 |
| OGAP-004 | `assertion:` schema not read | HIGH | RC3, SW2 | Fix 5 |
| OGAP-005 | Invalid/roundtrip cases not executed for 18 formats | HIGH | RC2, SW1 | Fix 4 + follow-on |
| OGAP-006 | format_depth = max, not distribution | MEDIUM | SW3 | Fix 6 |
| OGAP-007 | Spec facts lack provenance fields | MEDIUM | SW5 | §4.3 incremental |
| OGAP-008 | Capability oracle absent | LOW (for now) | SW5 | Separate plan |
| OGAP-009 | Acquisition oracle covers 2/20 formats | MEDIUM | Format-specific | Separate plan |
| OGAP-010 | oracle/registry/format-oracle-registry.yaml missing V82 target | LOW | Mismatch | Doc fix |

---

## Part 7 — Taskcards

### TC-ORA-001: Repository Bind and Pre-flight Check
**Status:** OPEN

```bash
cp "C:/Users/prora/.claude/plans/jaunty-whistling-meteor.md" plans/.claude/jaunty-whistling-meteor.md
python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/jaunty-whistling-meteor.md
git log --oneline -3
git status --short
```

Read: `reports/supervisor/session-resume.md`, `reports/supervisor/approval-gates.md`
Record current oracle state: run `python tools/oracle/execute_oracle.py --format csv` (dry verification)

**Output:** No artifacts. State confirmed.

---

### TC-ORA-002: Produce Verified Oracle Surface Register
**Status:** OPEN | **Dependencies:** TC-ORA-001

Read each file in the surface list below and confirm the code matches the claims from the
pre-work investigation. Specifically verify:
- `execute_abw_valid_case` in execute_oracle.py actually calls `execute_generic_load_case`
- ABW oracle-package.yaml uses `assertion:` not `expected_model_properties:` (already confirmed)
- gate_executor.py lines 119-136 contain the fallback exactly as described
- `_compare_model_properties` computes `loaded` as synthetic (already confirmed)

Files to verify (read each):
- `tools/oracle/execute_oracle.py` (key sections already read — confirm abw-valid-001 depth)
- `oracle/formats/abw/oracle-package.yaml` (already read — confirm assertion schema)
- `tools/supervisor/gate_executor.py` lines 93-160 (already read)
- `oracle/oracle-authority-policy.md` (already read)

**Output artifact:** `docs/oracle/oracle-surface-register.yaml`

Acceptance: `oracle_surfaces_not_inventoried: 0`, all 23+ surfaces with actual status
(not assumed status). Surface status must reflect executable-verified state:
- ABW: `status: ACTIVE_SCHEMA_MISMATCH` (assertion schema not read by executor)
- FODS: `status: ACTIVE_VERIFIED` (D1 with real property checks)

---

### TC-ORA-003: Reconstruct and Document the Four Proof Boundaries
**Status:** OPEN | **Dependencies:** TC-ORA-002

Document each boundary with code-traced evidence:

**Boundary A (Acquisition Oracle):** Confirmed classification:
`ACQUISITION_IS_SEPARATE_INTEROPERABILITY_ORACLE`. Evidence: oracle-package.yaml comment
line 9: "The acquisition oracle validates: 'does our prototype agree with LibreOffice?'
This product oracle validates: 'does our product implement the ODF 1.3 spec?'"

**Boundary B (Product Oracle):** `execute_oracle.py` — governed execution with authority
classes, depth levels, structured verdicts. Defects documented in OGAP-001 through OGAP-006.

**Boundary C (Specification Knowledge):** SAL facts exist but are unvalidated. The
`authorized_fact_refs: ["~4988 total FODS facts in SAL"]` in oracle-package.yaml is a
string comment, not a machine-verifiable fact reference list. Document this as a governance gap.

**Boundary D (Capability Layer):** Advisory-only. Document as ABSENT oracle (level 0).

**Output artifact:** `docs/oracle/oracle-boundary-register.yaml`

---

### TC-ORA-004: Run Oracle Baseline for All 20 Formats
**Status:** OPEN | **Dependencies:** TC-ORA-001

Run execute_oracle.py for each format and record actual current state:

```bash
for fmt in csv fods fodt zst tsv ndjson toml abw gnumeric dif fodg ods sylk xcf pbm pgm ppm qoi odt fodp; do
    python tools/oracle/execute_oracle.py --format $fmt 2>&1
done
```

Record for each format:
- Actual depth histogram (D0/D1 counts)
- Which case types executed (valid only? or also invalid/roundtrip?)
- Whether `expected_model_properties` was used or `assertion:` schema
- Whether any cases returned SKIPPED_MISSING_PROVIDER

This establishes a baseline before any fixes. Commit the updated oracle-run-summary.json files
with `product_source_hash` once Fix 3 is implemented.

**Output artifact:** `docs/oracle/oracle-baseline-2026.yaml`

---

### TC-ORA-005: Produce Readiness Assessment with Honest Counters
**Status:** OPEN | **Dependencies:** TC-ORA-004

Populate the 12 completion counters from actual data:

```
ORACLE_SURFACES_NOT_INVENTORIED: 0
ORACLE_CLAIMS_WITHOUT_AUTHORITY: 2 (Boundaries C and D — no authority enforcement)
ORACLE_RESULTS_WITHOUT_PERSISTENT_EVIDENCE: 0 (all have oracle-run-summary.json)
ORACLE_RESULTS_WITHOUT_CONSUMERS: 0 (G2, V143, certification consume summaries)
ORACLE_GATES_WITH_FALSE_GREEN_PATHS: 2 (G2 fallback, D1 inflation from loaded:true)
CAPABILITIES_WITHOUT_FACT_PROOF: 398 (gap-ledger.json entries, none machine-verified)
PRODUCT_CERTIFICATIONS_WITHOUT_PRODUCT_ORACLE_PROOF: 0 (all 20 have oracle-run-summaries)
UPSTREAM_CHANGES_WITHOUT_INVALIDATION: 20/20 formats (no staleness mechanism)
REFERENCE_IMPLEMENTATIONS_TREATED_AS_SPEC_AUTHORITY: 0 (LibreOffice is VERIFIED_INTEROPERABILITY only)
ORACLE_GAPS_WITHOUT_TASKS: 0 (all 10 OGAP entries have tasks in this plan)
REQUIRED_PILOTS_WITHOUT_DESIGN: 0 (designed in TC-ORA-011)
MATERIAL_SECOND_RUN_CHANGES: 0 (verify in TC-ORA-014)
```

Readiness scores:
- Specification Oracle: 1 (AD_HOC)
- Capability Oracle: 0 (ABSENT)
- Product Oracle: 3 (GOVERNED_PARTIAL) — will improve to 4 after fixes
- Acquisition Oracle: 2 (BASIC_REPEATABLE)

**Output artifact:** `docs/oracle/oracle-readiness-assessment.md`

---

### TC-ORA-006: Design Detailed Target Architecture Document
**Status:** OPEN | **Dependencies:** TC-ORA-003, TC-ORA-005

Produce `docs/oracle/target-oracle-architecture.md` covering:
- Four oracle boundaries, their relationships, and authority chains
- Shared infrastructure: registry, evidence store, execution engine, invalidation
- Explicit extension vs replacement decisions (extend execute_oracle.py; keep oracle-package.yaml)
- Oracle relationship diagram (SPECIFICATION → CAPABILITY → PRODUCT; ACQUISITION → PRODUCT via VERIFIED_INTEROPERABILITY)
- Format-family considerations: ODF formats have D2 (RelaxNG); image formats are D1-only; compression has D3 (zstandard)

**Output artifact:** `docs/oracle/target-oracle-architecture.md`

---

### TC-ORA-007: Define Persistent Artifact Schemas and State Machines
**Status:** OPEN | **Dependencies:** TC-ORA-006

Define versioned schemas for oracle_definition, oracle_case, oracle_run, oracle_result,
oracle_certification (per the prompt's Section 11 requirements).

Key decisions to encode in schemas:
- `oracle_run.product_source_hash` is required (not optional) in new runs
- `oracle_case.schema_version` is required (to distinguish `assertion:` vs `expected_model_properties:`)
- `oracle_certification.expires_or_invalidates_on` must include source change triggers

State machine for oracle_case: DRAFT → VALIDATED → READY → RUNNING → PASSED/FAILED/INCONCLUSIVE
→ ACCEPTED/REWORK_REQUIRED → SUPERSEDED/RETIRED

Invalidation triggers (minimum 15, per Section 12 of prompt).

**Output artifacts:**
- `oracle/schemas/oracle-artifact-schemas.yaml`
- `docs/oracle/oracle-state-machines.md`

---

### TC-ORA-008: Produce Oracle Gap Register
**Status:** OPEN | **Dependencies:** TC-ORA-005

Formalize the 10 identified gaps into `docs/oracle/oracle-gap-register.yaml` using the
`oracle_gap` schema from Section 17 of the prompt.

Each gap must have: gap_id, oracle_id, category, severity, evidence (file:line references),
root_cause, false_green_risk, affected_formats, shared_repair, migration stage, task_ids.

Traceability requirement: every gap must link to a taskcard in TC-ORA-013 (the hardened
implementation plan).

**Output artifact:** `docs/oracle/oracle-gap-register.yaml`

---

### TC-ORA-009: Design 12 Required Pilots
**Status:** OPEN | **Dependencies:** TC-ORA-006

Design all 12 pilots from Section 16 of the prompt. Key pilot designs grounded in code:

**Pilot 7 (LibreOffice agrees, spec disagrees):** FODS multi-sheet CSV export. LibreOffice
exports multi-sheet FODS to a single CSV file (known WARN in acquisition oracle: 1/4 WARN).
The ODF spec does not restrict multi-sheet semantics this way. Classification: `REFERENCE_DIVERGENCE`.
Evidence path: `acquisition-packs/fods/gate6-oracle-comparison-report.md`.

**Pilot 9 (Upstream change invalidates downstream):** Modify `oracle/formats/fods/oracle-package.yaml`
to change `expected_model_properties[sheet_count].value` from 1 to 2 for fods-valid-001.
Then check: does the G2 gate detect the mismatch? (Currently: no. After Fix 3: source hash
changes → `stale_warning: true` on next G2 check, then oracle re-run shows FAIL.)

**Pilot 11 (Idempotent runs):** Run `execute_oracle.py --format csv` twice consecutively.
Compare oracle-run-summary.json (excluding `executed_at`). Must be identical except timestamp.

**Pilot 12 (No external reference):** CSV format. No LibreOffice oracle. Product oracle
uses SPEC_NORMATIVE (RFC 4180) and ACCEPTED_EMPIRICAL only. Verify this produces valid
D1 evidence without any VERIFIED_INTEROPERABILITY cases.

**Output artifact:** `docs/oracle/oracle-pilot-designs.md`

---

### TC-ORA-010: Adversarial Review
**Status:** OPEN | **Dependencies:** TC-ORA-006, TC-ORA-008

Challenge the design. Required: at least 2 design changes result from this pass.

Mandatory challenges (code-grounded):
- Is the `loaded: true` fix actually correct, or does it cause legitimate D1 cases to regress to D0?
  Answer: Only if those cases have NO other properties. That means they never had real D1 depth.
  The regression is intentional — it surfaces formats that need better oracle coverage.

- Is removing the G2 fallback too aggressive? What formats will fail?
  Must enumerate: which formats currently rely on the fallback (passed_cases == 0, test_count >= 10)?
  These formats need explicit oracle runs added to CI before the fallback is removed.

- Does the registry approach (Fix 4) actually enable running invalid/roundtrip cases for all formats,
  or does it just make the dispatch cleaner without adding coverage?
  Answer: The registry alone is not enough — each format needs an invalid/roundtrip executor
  or the generic executor must be extended to handle all case types. The plan must address this.

- Is the specification oracle formalization (adding provenance fields to SAL facts) real progress
  or cosmetic? What is the actual falsification condition for `review_level: manual_extraction_run030`?

**Output artifact:** `docs/oracle/adversarial-review.md`

---

### TC-ORA-011: Produce Hardened Execution Plan
**Status:** OPEN | **Dependencies:** TC-ORA-001 through TC-ORA-010

Produce `plans/oracle/oracle-architecture-implementation-plan.md` with full task specifications
for implementing the 6 fixes and 3 architecture components.

Each task must specify:
- task_id, affected_oracle, affected_paths, dependencies
- Exact function and line numbers to change
- Tests to write (including negative: verify that formats with only `loaded:true` drop to D0 after Fix 1)
- Regression controls (run oracle for all formats before and after each fix)
- Rollback: `git revert <commit>` is sufficient for all fixes except Fix 3 (schema extension)
- Acceptance criteria (observable in oracle-run-summary.json or gate-check-results.json)

Critical acceptance criteria for each fix:

**Fix 1:** After implementation, run oracle for all formats. Formats that were at D1 only
because of `loaded: true` must now show D0. Count: expected ≥4 formats drop to D0.
V143 must then WARN for those formats.

**Fix 2:** After removal, run gate_executor for all formats. Formats with 0 oracle PASS
must now fail G2. Count: expected ≥2 formats fail G2 (requiring oracle runs to be added
to sprint closeout for those formats).

**Fix 3:** Run oracle for CSV (reference format), verify summary contains `product_source_hash`
and `oracle_package_hash`. Modify a CSV source file, re-run gate_executor, verify
`stale_warning: true` in gate result.

**Fix 4:** Run oracle for all 20 formats, verify results are identical to pre-refactor.
Zero regression permitted.

**Fix 5:** Run oracle for ABW specifically. Verify `assertion: {expect_type: dict}` case
now returns D1 (not D0). Verify `expect_type: list` case with a dict-returning parser returns FAIL.

**Fix 6:** Add a test oracle package with 1 D1 case and 9 D0 cases. Verify V143 returns WARN.
Verify current FODS (6 D1, 4 D0) still returns PASS from V143 (D0 not majority).

**Output artifact:** `plans/oracle/oracle-architecture-implementation-plan.md`

---

### TC-ORA-012: Verify Completion Counters and Produce Final Report
**Status:** OPEN | **Dependencies:** TC-ORA-011

Verify all 12 completion counters = 0 or have documented exceptions.
Verify `MATERIAL_SECOND_RUN_CHANGES = 0` by re-reading produced artifacts.
Write `docs/oracle/oracle-investigation-final-report.md`.

Final verdict: `ORACLE_SYSTEM_PARTIAL_TARGET_ARCHITECTURE_AND_PLAN_COMPLETE`

Write plan lock terminal:
```bash
python tools/supervisor/write_plan_lock.py \
  --plan-path plans/.claude/jaunty-whistling-meteor.md --terminal
```

---

## Part 8 — Tradeoffs, Risks, and Limits

### Tradeoffs

**Fix 1 (synthetic property) will cause visible regressions in reported depth.**
Formats that currently claim D1 on `loaded: true` will drop to D0. This is honest but will
surface as failures in V143 and may fail G2. Every format that drops to D0 needs new oracle
cases added. This is 1-2 days of follow-on work per affected format.

**Fix 2 (remove G2 fallback) will block some formats' release eligibility.**
This is the right outcome — those formats were never actually oracle-verified. But it creates
visible CI failures and will be perceived as a regression. Communicate this explicitly.

**Extending execute_oracle.py (not replacing it) preserves 1,822 lines of working code.**
The tradeoff is continued technical debt: format-specific logic in a monolith. The registry
approach (Fix 4) reduces this but does not eliminate it. A full redesign to a plugin architecture
would be cleaner but risks breaking working oracle runs.

### Risks

**Risk 1:** The oracle packages for 13-18 formats may have `expected_model_properties` that
are trivially weak (e.g., only `loaded: true`). After Fix 1, those formats will require
oracle case upgrades. The effort depends on format complexity — simple formats (PBM, PGM, PPM)
need ~3 real properties; complex formats (ODS, FODT) need much more.

**Risk 2:** Fix 3 (source hash) hashes the parser files at oracle run time. If the file set
changes (files added/removed), the hash changes even if behavior is identical. This will
produce false positive staleness warnings until oracle is rerun. Acceptable — stale warning
does not fail the gate.

**Risk 3:** The specification oracle cannot be built on top of SAL facts without human review
of the facts themselves. The `review_level: manual_extraction_run030` provenance is honest
but it means the spec oracle is a documentation improvement, not a machine-enforced guarantee.
Do not claim it is otherwise.

### What This Plan Cannot Deliver

- A full specification oracle that validates fact text against ODF spec content
  (requires a separate pipeline to extract and compare spec text)
- A capability oracle (requires redesigning the gap-ledger consumption pipeline)
- D2 coverage for non-ODF formats (no published RelaxNG schemas available)
- D3 coverage for formats without reference implementations

These are not addressed by this plan. They should be separate plans with explicit authorization.

---

## Part 9 — Output Artifacts Summary

| Artifact | Path | Produced By |
|---|---|---|
| Oracle Surface Register | docs/oracle/oracle-surface-register.yaml | TC-ORA-002 |
| Oracle Boundary Register | docs/oracle/oracle-boundary-register.yaml | TC-ORA-003 |
| Oracle Baseline (pre-fix) | docs/oracle/oracle-baseline-2026.yaml | TC-ORA-004 |
| Oracle Readiness Assessment | docs/oracle/oracle-readiness-assessment.md | TC-ORA-005 |
| Target Oracle Architecture | docs/oracle/target-oracle-architecture.md | TC-ORA-006 |
| Oracle Artifact Schemas | oracle/schemas/oracle-artifact-schemas.yaml | TC-ORA-007 |
| Oracle State Machines | docs/oracle/oracle-state-machines.md | TC-ORA-007 |
| Oracle Gap Register | docs/oracle/oracle-gap-register.yaml | TC-ORA-008 |
| Oracle Pilot Designs | docs/oracle/oracle-pilot-designs.md | TC-ORA-009 |
| Adversarial Review | docs/oracle/adversarial-review.md | TC-ORA-010 |
| Implementation Plan | plans/oracle/oracle-architecture-implementation-plan.md | TC-ORA-011 |
| Investigation Final Report | docs/oracle/oracle-investigation-final-report.md | TC-ORA-012 |

---

## Part 10 — Verification

After TC-ORA-012 completes, verify:

```bash
# 1. All output files exist
ls docs/oracle/
ls oracle/schemas/oracle-artifact-schemas.yaml
ls plans/oracle/oracle-architecture-implementation-plan.md

# 2. Plan lock is TERMINAL_CLOSED
python -c "import json; d=json.load(open('.local/supervisor/active-plan-lock.json')); print(d.get('status'))"

# 3. Completion counters are correct
grep "ORACLE_SURFACES_NOT_INVENTORIED" docs/oracle/oracle-readiness-assessment.md

# 4. Implementation plan has all 6 fix tasks
grep "Fix [1-6]" plans/oracle/oracle-architecture-implementation-plan.md | wc -l
# Expected: ≥6
```

---

## Critical File Paths

- Product oracle executor: [tools/oracle/execute_oracle.py](tools/oracle/execute_oracle.py)
- `_compare_model_properties` (Fix 1 target): [tools/oracle/execute_oracle.py:664](tools/oracle/execute_oracle.py#L664)
- `execute_generic_load_case` (Fix 5 target): [tools/oracle/execute_oracle.py:717](tools/oracle/execute_oracle.py#L717)
- `run_oracle_for_format` dispatch chain (Fix 4 target): [tools/oracle/execute_oracle.py:1608](tools/oracle/execute_oracle.py#L1608)
- `run_oracle_for_format` summary writer (Fix 3 target): [tools/oracle/execute_oracle.py:1757](tools/oracle/execute_oracle.py#L1757)
- G2 gate check (Fix 2 target): [tools/supervisor/gate_executor.py:93](tools/supervisor/gate_executor.py#L93)
- G2 fallback block (to remove): [tools/supervisor/gate_executor.py:119](tools/supervisor/gate_executor.py#L119)
- V143 validator (Fix 6 target): [tools/supervisor/governance_validators_oracle.py:14](tools/supervisor/governance_validators_oracle.py#L14)
- FODS oracle package: [oracle/formats/fods/oracle-package.yaml](oracle/formats/fods/oracle-package.yaml)
- ABW oracle package (schema mismatch): [oracle/formats/abw/oracle-package.yaml](oracle/formats/abw/oracle-package.yaml)
- FODS oracle run summary: [oracle/formats/fods/reports/oracle-run-summary.json](oracle/formats/fods/reports/oracle-run-summary.json)
- Oracle authority policy: [oracle/oracle-authority-policy.md](oracle/oracle-authority-policy.md)
- Gate definitions: [docs/gates/python-release-gate-definitions.md](docs/gates/python-release-gate-definitions.md)


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-08T09:18:53.522795+00:00"
  locked_by: "6aa05023e6ac"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->

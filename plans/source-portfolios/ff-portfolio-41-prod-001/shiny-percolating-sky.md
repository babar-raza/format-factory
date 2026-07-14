# Oracle System — Production-Grade Assessment and Implementation Plan
## Plan: shiny-percolating-sky (revised 2026-07-10)
**Type:** investigation_and_hardening
**Scope:** execute_oracle.py, gate_executor.py, oracle-package.yaml (20 formats), governance

---

## Context

The Format Factory oracle system was investigated in sprint jaunty-whistling-meteor (2026-07-08).
That investigation correctly identified six symptom-level defects. This plan goes further:
it identifies the structural root causes behind those defects, distinguishes what must change
from what must be preserved, and proposes a production-grade implementation with regression controls.

The standard is not "better than before." It is: **can this system detect a real parser regression
on the next run, regardless of who runs it or what machine they use?**

---

## Part 1 — What the Code Actually Does

These are facts from reading `tools/oracle/execute_oracle.py` and `tools/supervisor/gate_executor.py`:

### 1.1 Evidence Persistence Model (Two-Tier, Partially Committed)

```
oracle/formats/{format_id}/reports/oracle-run-summary.json  ← COMMITTED to git (line 1785-1789)
.local/oracle/{format_id}/verdicts/{case_id}.json           ← EPHEMERAL (gitignored, line 11)
```

The committed summary contains: `total_cases`, pass/fail counts, `depth_histogram`,
`format_depth_score`, `executed_at`. It does NOT contain: which cases passed, what was
observed vs. expected, or which product source version was tested.

### 1.2 Depth Assignment (The Core Bug, Line 713)

```python
def _compare_model_properties(result_val, expected_props: list) -> tuple[dict, list, str]:
    observed = {"loaded": True, "result_type": type(result_val).__name__}  # Always added
    ...
    for prop_spec in expected_props:
        if prop_name == "loaded":
            actual = result_val is not None  # Synthetic — always True here
        ...
    depth = DEPTH_D1 if expected_props else DEPTH_D0  # ANY non-empty list → D1
```

`depth = DEPTH_D1 if expected_props else DEPTH_D0` — any non-empty `expected_props` list
earns D1, including `[{"property": "loaded", "value": true}]` where `loaded` is
oracle-synthesized and always True. This cannot actually fail and adds no information
beyond what D0 already proves.

### 1.3 Invalid Case Execution (Explicit Gate, Line 1737-1755)

```python
if format_id in ("csv", "fods"):  # Only 2 of 20 formats
    for case in pkg.get("invalid_cases", []):
        ...
```

18 of 20 formats have `invalid_cases` defined in their oracle-package.yaml.
Those cases are NEVER loaded and NEVER executed. The oracle reports 0 invalid verdicts
for those 18 formats with no warning.

### 1.4 G2 Gate Fallback (The Policy Inversion, Lines 119-136)

```python
using_fallback = (passed_cases == 0) and (test_count >= 10)
if using_fallback:
    results.append({"check": "oracle_depth_minimum_d1", "passed": True,
                    "detail": f"fallback: {test_count} test files"})
```

G2 is defined as "Oracle Evidence." When `passed_cases == 0`, G2 passes anyway
if there are ≥10 test files. The gate result reports `oracle_depth_minimum_d1: True`
when it has evaluated zero oracle verdicts. This is a structural lie in the output.

### 1.5 Format Depth = max() Over PASS Verdicts (Line 1764-1770)

```python
valid_pass_depths = [v.get("depth_level", DEPTH_D0) for v in verdicts
    if v["result"] == "PASS" and not v.get("case_id", "").startswith(f"{format_id}-invalid")]
format_depth = max(valid_pass_depths, default=DEPTH_D0)
```

One D1 PASS case out of 10 total cases makes the format "D1." The committed
summary does not show the distribution — only the maximum. FODS: 6 D1 + 4 D0 cases
reports "D1." The 4 D0 cases are invisible in the committed evidence.

---

## Part 2 — Symptoms vs. Root Causes vs. Structural Weaknesses

### Symptoms (what the investigation report identified as "fixes")

| Symptom | Location | Identified By |
|---------|----------|--------------|
| S1: `loaded: true` earns D1 | execute_oracle.py:713 | Prior investigation |
| S2: 18 formats never execute invalid cases | execute_oracle.py:1737-1755 | Prior investigation |
| S3: G2 accepts 0 oracle PASS via test count | gate_executor.py:119-136 | Prior investigation |
| S4: No product_source_hash on summaries | execute_oracle.py:1771-1789 | Prior investigation |
| S5: `assertion:` schema silently ignored | execute_oracle.py:751 | Prior investigation |
| S6: V143 fires only when ALL cases are D0 | governance_validators_oracle.py:14 | Prior investigation |

### Root Causes (structural, not just patch targets)

**RC-1: The oracle is implementation-first, declarative-second.**
oracle-package.yaml defines what should be tested (including invalid_cases, roundtrip_cases,
interoperability_cases). The executor ignores most of it. There is no enforcement check:
"you defined 4 invalid cases in this package but registered 0 invalid case executors."
A declarative specification that the executor doesn't honor is documentation, not a contract.

**RC-2: The depth metric measures existence, not quality.**
D1 means "expected_model_properties was non-empty." It does not mean "properties were
compared against spec-backed values." The metric conflates "the oracle package author
wrote something in expected_model_properties" with "the oracle actually tested something
meaningful." Both conditions earn D1 under the current code.

**RC-3: The gate system rewards having an oracle, not having a good one.**
G2 requires `depth ≥ D1 AND passed_cases > 0`. After all six fixes, a format with
ONE valid case, ONE real property comparison, and no invalid case coverage still
passes G2 with the same confidence as a format with 10 valid cases, 5 properties each,
and full invalid coverage. The gate is binary where coverage is continuous.

**RC-4: The committed evidence does not support auditing what was compared.**
The committed oracle-run-summary.json shows counts. There is no committed record of
which case passed with which observed/expected values. An auditor cannot determine
from the committed evidence whether "D1, 5/5 PASS" means the parser returned
`{"sheet_count": 3}` as expected or just `{"loaded": True}`. Both look identical
in the summary.

**RC-5: No reproducibility link between evidence and product source.**
The committed summary has `executed_at` (a timestamp) but no hash of what it tested.
Product source changes after oracle execution are invisible. Two summaries with identical
`executed_at` times could test different product versions (unlikely in practice but
undetectable in principle). The system relies on discipline, not enforcement.

**RC-6: The specification oracle is a process, not an oracle.**
14,644 SAL facts are manually extracted and committed to git. This is a valid
audit trail. It is not a mechanism that "decides whether a claim is supported by an
authoritative reference" — there is no automated comparison between fact text and
specification source. Calling this a "specification oracle" overstates what it does.
The 17 dormant tools (spec_parser.py, spec_normalizer.py, etc.) would implement a
real specification oracle, but they have never run in production.

**RC-7: Generic executor formats commit `"expected": {}` in verdict JSON.**
In `execute_generic_load_case()`, when comparison happens via `_compare_model_properties()`,
the function returns `(observed_dict, deviations, depth)` but the `expected` dict passed
to `make_verdict()` is built OUTSIDE the generic executor — it collects `expected_props`
from oracle-package.yaml and passes them as the comparison reference. However, for most
generic formats the verdict JSON commits `"expected": {}` (empty) because the expected
props dict is not threaded through correctly to the verdict record. This is distinct from
RC-4: RC-4 is about the committed summary showing only counts; RC-7 is about even the
ephemeral per-case verdict failing to record what the oracle compared. Result: "D1, PASS"
in the summary, but no committed record of which specific property value was checked.

### Structural Weaknesses (design constraints that amplify the root causes)

**SW-1: Declare-vs-execute gap has no enforcement boundary.**
The oracle package schema allows any case type. The executor checks only `valid_cases`
for most formats and `invalid_cases` for exactly 2. There is nothing that surfaces this
discrepancy when an oracle is run.

**SW-2: "VERIFIED" status is binary and too coarse.**
The format registry lifecycle (`OBLIGATION_CREATED → VERIFIED → PRODUCTION_ACTIVE`) uses
"VERIFIED" when `passed_cases > 0 AND depth ≥ D1`. This conflates formats with:
- 10 valid + 5 invalid cases at D1 (FODS)
- 3 valid cases with only `ok: True` and 0 invalid cases (ODT)
Both are "VERIFIED." The certification is the same regardless of coverage quality.

**SW-3: The executor and the oracle package schema evolve independently.**
`assertion:` fields were added to some oracle packages but the executor never read them.
`expected_model_properties` is read. The schema has two patterns for expressing
expected output, but only one is honored. No schema validation at load time catches this.

**SW-4: Evidence asymmetry between FODS-specific and generic executor verdicts.**
`execute_fods_valid_case()` threads real `expected={...}` into `make_verdict()`, so the
ephemeral verdict JSON shows what was compared (`"expected": {"sheet_count": 3, ...}`).
Generic executor formats (`execute_generic_load_case()`) pass no expected dict to
`make_verdict()` — `"expected": {}` in the ephemeral record. Same D1 depth score appears
in both, but FODS is auditable and generic formats are not. The commit-level summary hides
this asymmetry entirely.

---

## Part 3 — What Breaks Consistency Across Reruns

Three distinct consistency problems exist:

**C1: Evidence-source disconnect.** The committed summary cannot be traced to the
product source that generated it. If product source changes after an oracle run:
- G2 still passes (reads committed summary, finds D1, passes)
- The summary was generated from an older product version
- There is no detection mechanism

**C2: Metric inflation.** The D1 depth score is inflated for 3 formats (D0 presented
as D1) and understated for several more (real D1 but only 1 discriminating property
when 10 cases were executed). The committed summary shows "D1" and both an inflated
and a weak D1 look identical.

**C3: Coverage invisibility.** The committed summary does not distinguish between:
- Format A: 10 valid cases, 5 properties each, 3 invalid cases → "5/5 PASS, D1"
- Format B: 5 valid cases, `loaded: true` only, 0 invalid cases → "5/5 PASS, D1"
Both produce the same committed artifact. Both pass G2. A reviewer cannot tell them apart.

---

## Part 4 — What to Preserve

These components are correctly designed and must not change:

| Component | Why preserved |
|-----------|--------------|
| oracle-package.yaml declarative structure | Well-designed; cases, authority, profiles correctly separated |
| `check_authority()` enforcement | Correctly blocks AI_DRAFT_UNVERIFIED, IMPLEMENTATION_OBSERVED, UNKNOWN |
| `make_verdict()` schema | All fields are used; schema is correct |
| SKIPPED_MISSING_PROVIDER result | Correct handling; LibreOffice-absent environments remain valid |
| Acquisition oracle / product oracle separation | LibreOffice ≠ spec authority; the boundary is correct |
| SPEC_NORMATIVE vs VERIFIED_INTEROPERABILITY authority classes | Correct hierarchy; prevents spec-authority inflation |
| `oracle-run-summary.json` committed to git | Right location, right format; needs additional fields |
| The 4-oracle boundary model (Spec/Acq/Product/Capability) | Correct framing; don't collapse these |
| SAL facts in git as manual audit trail | Valid process; should be labeled honestly as manual review |
| D0/D1/D2/D3 depth level concept | Correct concept; just needs honest implementation |

---

## Part 5 — Production-Grade Solution

Five production pillars, ordered by impact-to-complexity ratio:

### Pillar 1 (Highest Impact): Fix D1 Depth and Generic Invalid Coverage

These two changes together address RC-1 and RC-2. They should be implemented and deployed
together because they have complementary effects on coverage visibility.

**1a: Fix D1 depth — honest synthetic property exclusion**

Change `_compare_model_properties()` in `tools/oracle/execute_oracle.py`:

```python
# Add at module level (after line 65):
SYNTHETIC_PROPERTIES: frozenset[str] = frozenset({"loaded", "result_type"})

# Change _compare_model_properties(), currently line 713:
# OLD: depth = DEPTH_D1 if expected_props else DEPTH_D0
# NEW:
has_real_comparison = any(
    p.get("property") not in SYNTHETIC_PROPERTIES
    for p in expected_props
    if p.get("property")  # skip empty property names
)
depth = DEPTH_D1 if has_real_comparison else DEPTH_D0
```

Effect: dif, fodt, sylk drop from D1 to D0 in next run. This is correct behavior.
These formats currently check only `loaded: true`, which proves nothing about the model.

**Critical sequencing constraint:** Do NOT apply this before upgrading oracle packages
for dif, fodt, sylk. If the packages are upgraded first (add real properties), these
formats re-earn D1 on the same run. If not sequenced, they drop to D0 and G2 fails.

**1b: Generic invalid case executor**

Add to `tools/oracle/execute_oracle.py` (new function after `execute_generic_load_case`):

```python
def execute_generic_invalid_case(
    case: dict, pkg: dict, format_id: str, module: str, callable_name: str
) -> dict:
    """Generic invalid case: expects the callable to raise an exception.

    PASS if exception raised (parser correctly rejects malformed input).
    FAIL if no exception raised (parser silently accepts malformed input).
    Partial recovery handled via partial_recovery_allowed field.
    """
    case_id = case["case_id"]
    _, authority_status = check_authority(case, False)

    sample_ref = case.get("sample_ref") or case.get("input_ref")
    inline = case.get("input_inline")

    if sample_ref is None and inline is None:
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}",
            language="python", case_id=case_id,
            profile="INVALID_INPUT_REJECTION",
            result=RESULT_NOT_APPLICABLE, authority_status=authority_status,
            diagnostics=["No sample_ref or input_inline for invalid case"],
        )

    if sample_ref:
        sample_path = REPO_ROOT / sample_ref
        if not sample_path.exists():
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id=format_id, product_id=f"format-factory-{format_id}",
                language="python", case_id=case_id,
                profile="INVALID_INPUT_REJECTION",
                result=RESULT_BLOCKED_MISSING_SAMPLE, authority_status=authority_status,
                diagnostics=[f"Sample not found: {sample_path}"],
            )
        input_data = str(sample_path)
    else:
        input_data = inline

    partial_recovery = case.get("partial_recovery_allowed", False)

    try:
        sys.path.insert(0, str(REPO_ROOT))
        mod = importlib.import_module(f"src.python.{module}")
        fn = getattr(mod, callable_name)
        result_val = fn(input_data)

        if partial_recovery:
            # Parser returned without raising — partial recovery is allowed
            return make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id=format_id, product_id=f"format-factory-{format_id}",
                language="python", case_id=case_id,
                profile="INVALID_INPUT_REJECTION",
                result=RESULT_PASS, authority_status=authority_status,
                diagnostics=["Parser recovered gracefully (partial_recovery_allowed=true)"],
                depth_level=DEPTH_D0,
            )
        # No exception raised, no partial recovery — FAIL
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}",
            language="python", case_id=case_id,
            profile="INVALID_INPUT_REJECTION",
            result=RESULT_FAIL, authority_status=authority_status,
            diagnostics=["Expected exception was not raised — parser silently accepted invalid input"],
            depth_level=DEPTH_D0,
        )
    except Exception:
        # Exception raised — correct behavior for invalid input
        return make_verdict(
            oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
            format_id=format_id, product_id=f"format-factory-{format_id}",
            language="python", case_id=case_id,
            profile="INVALID_INPUT_REJECTION",
            result=RESULT_PASS, authority_status=authority_status,
            depth_level=DEPTH_D0,
        )
```

Then change the invalid case dispatch section (currently line 1737-1755):

```python
# Replace:
#   if format_id in ("csv", "fods"):
# With:
for case in pkg.get("invalid_cases", []):
    case_id = case["case_id"]
    if case_filter and case_id != case_filter:
        continue
    if format_id == "csv":
        verdict = execute_csv_invalid_case(case, pkg)
    elif format_id == "fods":
        verdict = execute_fods_invalid_case(case, pkg)
    else:
        # Generic: resolve format's module and callable from oracle-package.yaml
        executor_config = pkg.get("executor_config", {})
        module = executor_config.get("module")
        callable_name = executor_config.get("callable")
        if module and callable_name:
            verdict = execute_generic_invalid_case(case, pkg, format_id, module, callable_name)
        else:
            # No executor config — record UNSUPPORTED_CASE
            verdict = make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id=format_id, product_id=f"format-factory-{format_id}",
                language="python", case_id=case_id,
                profile="INVALID_INPUT_REJECTION",
                result=RESULT_NOT_APPLICABLE, authority_status="UNKNOWN",
                diagnostics=["No executor_config in oracle-package.yaml for generic invalid case"],
            )
    verdicts.append(verdict)
    ...
```

Add `executor_config:` to oracle-package.yaml for each format that uses generic_load_case:
```yaml
executor_config:
  module: zst.zst_codec
  callable: decompress_zst
```

**Tradeoff:** Invalid cases are D0 (they only check exception-raising, not model properties).
They won't improve format_depth_score. But they DO improve ACTUAL coverage of rejection behavior.
A parser that silently accepts malformed input will now FAIL these cases. The depth metric
understates the value of invalid case coverage.

**Risk:** Some invalid cases have `partial_recovery_allowed: true` — the generic executor
handles this via the `partial_recovery` flag. Cases with non-exception rejection patterns
(e.g., returning `{"error": "malformed"}` without raising) need format-specific handling.
Start with the generic executor; add format-specific overrides as needed.

---

### Pillar 2 (High Impact): Remove G2 False-Green Path

Remove the test-suite fallback from `tools/supervisor/gate_executor.py` check_g2():

```python
# DELETE lines 119-136 (the using_fallback block):
# test_dir = REPO_ROOT / "tests" / "python" / format_id
# test_count = len(list(test_dir.glob("test_*.py"))) if test_dir.exists() else 0
# using_fallback = (passed_cases == 0) and (test_count >= 10)
# if using_fallback: ...

# KEEP only the direct oracle check path:
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

**Before applying:** Run gate_executor.py for all 20 formats and record which ones use
the fallback. As of 2026-07-08 baseline, NO format has 0 oracle PASS — all have active
oracle runs. The fallback is not currently hiding any gap. But it will hide future gaps
if CI stops running oracle and someone asks "is G2 passing?"

**Risk:** If oracle runs become stale or stop executing (e.g., new format added without
running oracle), G2 will fail visibly instead of silently passing via test count. This
is the INTENDED behavior — visible failure is better than silent fallback.

---

### Pillar 3 (Medium Impact): Source Hash for Staleness Detection

Add to `run_oracle_for_format()` before saving summary:

```python
def _compute_source_hash(format_id: str) -> str:
    """SHA-256 of all .py files in src/python/{format_id}/, sorted by path."""
    src_dir = REPO_ROOT / "src" / "python" / format_id
    h = hashlib.sha256()
    for py_file in sorted(src_dir.glob("**/*.py")):
        h.update(py_file.read_bytes())
    return f"sha256:{h.hexdigest()}"

def _compute_package_hash(format_id: str) -> str:
    """SHA-256 of the oracle-package.yaml for this format."""
    pkg_path = ORACLE_DIR / "formats" / format_id / "oracle-package.yaml"
    return sha256_file(pkg_path) if pkg_path.exists() else "sha256:absent"
```

Add to summary dict (before `json.dump`):
```python
summary["product_source_hash"] = _compute_source_hash(format_id)
summary["oracle_package_hash"] = _compute_package_hash(format_id)
```

Add staleness check in `check_g2()` (ADVISORY only — do not block):
```python
current_source_hash = _compute_current_source_hash(format_id)  # same logic
stored_source_hash = summary.get("product_source_hash", "ABSENT")
stale = (stored_source_hash != "ABSENT" and stored_source_hash != current_source_hash)
if stale:
    results.append({
        "check": "oracle_evidence_fresh",
        "passed": False,  # Advisory only, does not affect gate.passed
        "detail": f"Source hash changed since last oracle run — re-run recommended",
    })
```

**Important:** This is advisory, not blocking. Making it blocking immediately would
break CI whenever source is touched without re-running oracle. Move to blocking
after establishing a consistent CI oracle-run workflow.

**Limit:** Hashing all .py files in the format directory may include test helper files.
Consider hashing only the installable package files (exclude tests/, examples/).
Consistent hashing is more important than perfect precision here.

---

### Pillar 4 (Medium Impact): Strengthen V143 to Distribution-Aware

Change `validate_oracle_depth_minimum()` in `tools/supervisor/governance_validators_oracle.py`:

```python
# Current: fires only when format_depth_score == "D0" (all-D0 condition)
# New: fires when D0 cases are majority of total cases

depth_hist = summary.get("depth_histogram", {})
d0_count = depth_hist.get("D0", 0)
d1_plus_count = sum(v for k, v in depth_hist.items() if k != "D0")
total_cases = d0_count + d1_plus_count

if total_cases > 0 and d0_count > d1_plus_count:
    # D0 is the majority case type — flag it
    return warn(f"Format {fmt}: D0-majority depth ({d0_count}/{total_cases} cases at D0)")
```

**Why this matters:** FODS has 6 D1 + 4 D0 → reports D1, V143 does not fire. That's correct
(D1 majority). ABW has 2 D0 (assertion-silenced) + 1 D1 → reports D1, V143 does not fire.
After Pillar 1 fixes (assertion schema enabled), ABW may have 3 D1. But before Pillar 1,
this check would surface formats with mostly D0 coverage that are claiming D1.

---

### Pillar 5 (Structural): Declare-vs-Execute Enforcement

Add a coverage check at oracle run startup in `run_oracle_for_format()`:

```python
def _check_case_coverage(pkg: dict, format_id: str) -> list[str]:
    """Warn about case types defined in oracle package but not executed by this run."""
    warnings = []

    # Roundtrip cases — only zst and fods are currently wired
    if pkg.get("roundtrip_cases") and format_id not in ("csv", "fods", "zst"):
        n = len(pkg["roundtrip_cases"])
        warnings.append(f"COVERAGE_GAP: {n} roundtrip_cases defined but no executor wired for {format_id}")

    # Interoperability cases — only fods is wired
    if pkg.get("interoperability_cases") and format_id != "fods":
        n = len(pkg["interoperability_cases"])
        warnings.append(f"COVERAGE_GAP: {n} interoperability_cases defined but no executor wired for {format_id}")

    # Invalid cases — wired for csv and fods; after Pillar 1, wired for all with executor_config
    invalid_cases = pkg.get("invalid_cases", [])
    if invalid_cases and format_id not in ("csv", "fods"):
        executor_config = pkg.get("executor_config", {})
        if not executor_config:
            n = len(invalid_cases)
            warnings.append(f"COVERAGE_GAP: {n} invalid_cases defined but no executor_config in oracle-package.yaml")

    return warnings
```

Call this at the start of `run_oracle_for_format()` and print warnings to stderr.
Also include coverage_gaps in the committed summary:
```python
summary["coverage_gaps"] = coverage_gaps  # list of warning strings
```

This makes the declare-vs-execute gap VISIBLE in the committed evidence rather than silent.

---

## Part 6 — Oracle Package Upgrades (Required Companions)

These are REQUIRED for Pillar 1 to not break G2:

### 6.1 dif/fodt/sylk — Add Real Model Properties

For **dif** (`oracle/formats/dif/oracle-package.yaml`):
```yaml
# Update existing valid cases to add non-synthetic properties:
expected_model_properties:
  - property: record_count
    value: 3
    authority: "DIF spec §3.1: DATA section contains one tuple per data row"
  - property: column_count
    value: 2
    authority: "DIF spec §3.2: VECTORS header defines number of columns"
```
Requires: read actual dif parser output to determine what dict keys it returns.

For **fodt** (`oracle/formats/fodt/oracle-package.yaml`):
```yaml
expected_model_properties:
  - property: format_id
    value: "fodt"
    authority: "ODF 1.3 §2.1: Flat OpenDocument format identification"
  - property: paragraph_count
    value: 1
    authority: "ODF 1.3 §6.1.1: text:p element count"
```
Requires: read fodt.parser.parse_fodt() return value to determine what fields exist.

For **sylk** (`oracle/formats/sylk/oracle-package.yaml`):
```yaml
expected_model_properties:
  - property: cell_count
    value: 4
    authority: "SYLK format C records represent cell values (ACCEPTED_EMPIRICAL)"
  - property: sheet_count
    value: 1
    authority: "SYLK single-sheet format (ACCEPTED_EMPIRICAL)"
```
Requires: read sylk.sylk_parser.SylkDocument() return value.

### 6.2 Add executor_config to All Generic Formats

Formats that already use `execute_generic_load_case` need `executor_config:` added
to their oracle-package.yaml so the generic invalid case executor can also run.
The values are extracted from the existing thin-wrapper functions at lines 774-807:

| Format | module | callable | Notes |
|--------|--------|----------|-------|
| abw | `abw.abw_codec` | `load` | Confirmed by agent read |
| gnumeric | `gnumeric.gnumeric_codec` | `load` | Confirmed by agent read |
| dif | `dif.dif_parser` | `parse_dif` | Confirmed by agent read |
| fodg | `fodg.fodg_codec` | `load` | Confirmed by agent read |
| ods | `ods.ods_parser` | `parse_ods` | **Corrected**: agent found ods_parser not ods_codec |
| sylk | `sylk.sylk_parser` | `SylkDocument` | **Corrected**: callable is class constructor, not parse_sylk |
| fodt | `fodt.parser` | `parse_fodt` | Confirmed by agent read |
| xcf | `xcf.xcf_parser` | `XcfImage` | **Corrected**: agent found xcf_parser.XcfImage not xcf_codec.load |
| pbm | `pbm.pbm_parser` | `parse_pbm` | **Corrected**: agent found pbm_parser not pbm_codec |
| pgm | `pgm.pgm_parser` | `parse_pgm` | **Corrected** + NOTE: execute_pgm_valid_case has custom sys.path manipulation (lines 819-870) — verify generic executor works for pgm |
| ppm | `ppm.ppm_parser` | `parse_ppm` | **Corrected**: agent found ppm_parser not ppm_codec |
| qoi | `qoi.qoi_parser` | `parse_qoi` | **Corrected**: agent found qoi_parser not qoi_codec |
| odt | `odt.odt_parser` | `parse_odt` | Confirmed by agent read |
| fodp | `fodp.fodp_codec` | `load` | Confirmed by agent read |
| ndjson | `ndjson.ndjson_codec` | `load` | Verify during MS-004-01 |
| toml | `toml_codec.toml_codec` | `load` | Verify during MS-004-01 |
| tsv | `tsv.tsv_codec` | `load` | Verify during MS-004-01 |
| zst | `zst.zst_codec` | `decompress_zst` | Confirmed by agent read |

**Note:** These module/callable values are extracted from code reading; verify against
actual thin-wrapper function bodies during TC-OIS-004 MS-004-01 before committing.
The `module` field uses Python dotted-path notation relative to `src/python/`.

Example yaml block:
```yaml
executor_config:
  module: zst.zst_codec
  callable: decompress_zst
```

---

## Part 7 — What This Plan Does NOT Address (And Why)

**Not addressed: SAL specification oracle automation.**
17 dormant tools exist (spec_parser.py, spec_normalizer.py, etc.). Wiring them is a
3-6 month project. The honest position: SAL facts are a manual audit trail, not an
automated oracle. Document this clearly. Don't attempt to close this gap now.

**Not addressed: Capability oracle.**
398 capabilities lack fact proof. Building capability proof machinery requires: defining
what "proof" means per capability type, automating test-to-capability linkage, and
creating capability evidence stores. This is a separate major project. Document the gap.
Add a `capability_refs:` tracking coverage in the oracle summary (which oracle cases
reference which capabilities) but don't build a full proof engine now.

**Not addressed: D2 ODF RelaxNG at scale.**
D2 validation exists in code (schema_validator.py + oracle/schemas/odf-1.3-relaxng/).
But current FODS test fixtures fail schema validation because they don't fully conform
to ODF 1.3. D2 requires creating spec-conformant fixtures. Not in scope here.

**Not addressed: LibreOffice version pinning for D3.**
D3 cases are SKIPPED_MISSING_PROVIDER in standard CI. Until LibreOffice is in CI with
a pinned version and reproducible output, D3 is advisory only. Leave it as-is.

---

## Part 8 — Honest Tradeoffs and Limits

| Change | Risk | Mitigation |
|--------|------|-----------|
| Fix D1 depth | dif/fodt/sylk drop to D0 until packages upgraded | Do package upgrades first (same sprint) |
| Remove G2 fallback | New formats without oracle runs will fail G2 visibly | This is CORRECT behavior — visible failure reveals real gap |
| Generic invalid executor | Some formats may have non-exception rejection patterns | Start with exception-only; add format overrides as encountered |
| Source hash advisory | Hash may trigger on non-material source changes (formatting) | Hash only .py source files, not tests or docs |
| Coverage gaps in summary | Shows gaps that were previously silent | Better to know; gaps existed before, now visible |

**Limits of this plan:**
1. D1 is still a weak standard — one non-synthetic property earns D1. The gate system
   needs a future "D1 minimum coverage" gate (e.g., ≥3 non-synthetic properties per valid case).
   This plan doesn't add that; it's scope extension.
2. Invalid case coverage is D0-depth only. Oracle can prove "parser rejects invalid input"
   but not "parser rejects it with the correct error message/type." The `expected_error_type`
   field in oracle-package.yaml (e.g., `"FodsParseError"`) is not evaluated yet.
   Add this in a follow-up sprint.
3. Committed summaries remain the only committed evidence. Individual verdicts remain
   ephemeral. A future improvement: commit exemplar verdict per case type (showing observed
   vs. expected) to `oracle/formats/{format}/evidence/{case_id}-latest.json`. Not in scope.

**Confidence levels:**
- Pillar 1 (D1 fix + generic invalid): HIGH confidence — code is well-understood, fix is precise
- Pillar 2 (G2 fallback removal): HIGH confidence — no format currently uses it, risk is minimal
- Pillar 3 (source hash): MEDIUM confidence — hashing approach is correct; staleness policy TBD
- Pillar 4 (V143 distribution-aware): HIGH confidence — additive change, no blast radius
- Pillar 5 (coverage gaps): MEDIUM confidence — diagnostic only, commits warning list to summary

---

## Part 9 — Machine-State Taskcard Definitions

State machine for every taskcard and micro-step:
`PROPOSED` → `READY` → `IN_PROGRESS` → (`BLOCKED` ↔ `IN_PROGRESS`) → `DONE` → `VERIFIED`

**PROPOSED**: not yet confirmed necessary | **READY**: all deps met, can execute
**IN_PROGRESS**: actively being worked | **BLOCKED**: waiting on dependency
**DONE**: implementation complete, tests passing | **VERIFIED**: ran end-to-end, evidence committed

---

### TC-OIS-001: Scope Verification

| Field | Value |
|-------|-------|
| State | READY |
| Depends-on | NONE |
| Blocks | TC-OIS-002 (verify no conflict before editing oracle packages) |
| Files | `docs/oracle/` (10 files), `plans/oracle/oracle-architecture-implementation-plan.md` |
| Evidence-contract | Annotation in TC-OIS-001 status confirming no plan conflict found; if conflict found, amend affected taskcards before marking DONE |
| Rollback-trigger | N/A — read-only |

#### Micro-steps

**MS-001-01** [OPEN]: Read `plans/oracle/oracle-architecture-implementation-plan.md` and all 10 files in `docs/oracle/`.
- Success: Prior plan's Fix 1–6 taskcards are identified; their scope is checked against this plan's TC-OIS-002 through TC-OIS-008.

**MS-001-02** [OPEN — after MS-001-01]: Confirm compatibility. Record any conflicts as amendments to this plan.
- Success: No unresolved conflicts, or conflicts resolved by plan amendment before proceeding.

#### Validation
| Check | Method | Pass | Fail-action |
|-------|--------|------|-------------|
| No conflicting task IDs | Manual comparison | Prior plan's TC-ORA-NNN vs this plan's TC-OIS-NNN are orthogonal | Amend scope to resolve |
| No duplicate file edits | Check file overlap | Same files edited → merge scope | Merge or exclude duplicate work |

---

### TC-OIS-002: Upgrade Oracle Packages for dif, fodt, sylk

| Field | Value |
|-------|-------|
| State | READY |
| Depends-on | TC-OIS-001 |
| Blocks | TC-OIS-003 (HARD — must complete first) |
| Files | `oracle/formats/dif/oracle-package.yaml`, `oracle/formats/fodt/oracle-package.yaml`, `oracle/formats/sylk/oracle-package.yaml` |
| Evidence-contract | All 3 oracle-package.yaml files have ≥1 `expected_model_properties` entry with `property` ≠ `loaded` and `property` ≠ `result_type`; oracle run for each format returns D1 |
| Rollback-trigger | Oracle run for any of the 3 formats returns FAIL (property name not found in parser output) → revert YAML, investigate actual returned dict, retry |

#### Micro-steps

**MS-002-01** [OPEN]: Run dif parser on sample to discover real output dict:
```bash
cd c:/Users/prora/OneDrive/Documents/GitHub/format-factory
.venv/Scripts/python -c "
from src.python.dif.dif_parser import parse_dif
import json
print(json.dumps(parse_dif('samples/by-format/dif/minimal-spreadsheet.dif'), default=str))
"
```
- Success: Parser returns dict; identify non-synthetic keys (e.g., `row_count`, `column_count`, `vectors`, `records`).

**MS-002-02** [OPEN — after MS-002-01]: Update `oracle/formats/dif/oracle-package.yaml` to replace `{property: loaded, value: true}` with real property entries from parser output. Use `authority_class: ACCEPTED_EMPIRICAL` with comment citing DIF spec section if known, or `SPEC_INFORMATIVE` if available.
- Success: At least 1 entry with property from actual parser output dict.

**MS-002-03** [OPEN]: Run dif parser on sample for fodt:
```bash
.venv/Scripts/python -c "
from src.python.fodt.parser import parse_fodt
import json
print(json.dumps(parse_fodt('samples/by-format/fodt/minimal-document.fodt'), default=str))
"
```
- Success: Parser returns dict; identify properties to use (`format_id`, `paragraph_count`, or other real fields).

**MS-002-04** [OPEN — after MS-002-03]: Update `oracle/formats/fodt/oracle-package.yaml` with real properties from fodt parser output.
- Success: ≥1 non-synthetic property in expected_model_properties.

**MS-002-05** [OPEN]: Run sylk parser on sample (callable is SylkDocument class, not parse_sylk):
```bash
.venv/Scripts/python -c "
from src.python.sylk.sylk_parser import SylkDocument
import json
doc = SylkDocument('samples/by-format/sylk/minimal.sylk')
print(json.dumps(doc.__dict__, default=str))
"
```
- Success: Identify real properties from SylkDocument attributes (`cell_count`, `row_count`, or other non-synthetic fields).

**MS-002-06** [OPEN — after MS-002-05]: Update `oracle/formats/sylk/oracle-package.yaml` with real properties.
- Success: ≥1 non-synthetic property in expected_model_properties.

**MS-002-07** [OPEN — after MS-002-02, MS-002-04, MS-002-06]: Run oracle for all 3 formats and confirm D1 maintained:
```bash
.venv/Scripts/python tools/oracle/execute_oracle.py --format dif --all
.venv/Scripts/python tools/oracle/execute_oracle.py --format fodt --all
.venv/Scripts/python tools/oracle/execute_oracle.py --format sylk --all
```
- Success: All 3 show PASS + D1 in oracle-run-summary.json; oracle reports real property name in deviations-free output.

#### Validation
| Check | Method | Pass | Fail-action |
|-------|--------|------|-------------|
| No synthetic-only properties remain | grep `loaded` in updated yaml files | No `property: loaded` entries remain | Re-edit YAML |
| D1 maintained post-upgrade | Read oracle-run-summary.json for dif/fodt/sylk | `format_depth_score: D1` | Investigate property name mismatch; revert and retry |
| No regressions | Run oracle for all 20 formats | All PASS counts unchanged | Per-format investigation |

---

### TC-OIS-003: Fix D1 Depth — Synthetic Property Exclusion

| Field | Value |
|-------|-------|
| State | BLOCKED (on TC-OIS-002) |
| Depends-on | TC-OIS-002 (HARD — packages must be upgraded before depth fix applied) |
| Blocks | TC-OIS-006 |
| Files | `tools/oracle/execute_oracle.py` (lines 65, 713) |
| Evidence-contract | `SYNTHETIC_PROPERTIES` frozenset present in module; `_compare_model_properties()` returns D0 for `loaded`-only input; all 20 formats show D1+ in oracle-run-summary.json |
| Rollback-trigger | Any format drops to D0 after applying the fix (means TC-OIS-002 package upgrade is incomplete or property is still synthetic) → revert line 713 change, complete TC-OIS-002 for affected format, retry |

#### Micro-steps

**MS-003-01** [OPEN — after TC-OIS-002 DONE]: Add to `tools/oracle/execute_oracle.py` after line 65:
```python
SYNTHETIC_PROPERTIES: frozenset[str] = frozenset({"loaded", "result_type"})
```
- Success: Line present, no syntax error.

**MS-003-02** [OPEN — after MS-003-01]: Replace line 713 in `_compare_model_properties()`:
```python
# OLD:
depth = DEPTH_D1 if expected_props else DEPTH_D0
# NEW:
has_real_comparison = any(
    p.get("property") not in SYNTHETIC_PROPERTIES
    for p in expected_props
    if p.get("property")
)
depth = DEPTH_D1 if has_real_comparison else DEPTH_D0
```
- Success: Function compiles, logic correct.

**MS-003-03** [OPEN — after MS-003-02]: Write unit tests in `tests/oracle/test_depth_scoring.py`:
```python
def test_loaded_property_does_not_earn_d1():
    _, _, depth = _compare_model_properties({"ok": True}, [{"property": "loaded", "value": True}])
    assert depth == "D0"

def test_result_type_does_not_earn_d1():
    _, _, depth = _compare_model_properties({"ok": True}, [{"property": "result_type", "value": "dict"}])
    assert depth == "D0"

def test_real_property_earns_d1():
    _, deviations, depth = _compare_model_properties({"row_count": 5}, [{"property": "row_count", "value": 5}])
    assert depth == "D1"
    assert deviations == []

def test_mixed_synthetic_and_real_earns_d1():
    # loaded + real property → D1 (real property present)
    props = [{"property": "loaded", "value": True}, {"property": "row_count", "value": 5}]
    _, _, depth = _compare_model_properties({"row_count": 5}, props)
    assert depth == "D1"
```
- Success: All 4 tests pass.

**MS-003-04** [OPEN — after MS-003-03]: Run oracle for all 20 formats, verify D1+ maintained:
```bash
for fmt in fods fodt ods odt csv tsv ndjson toml abw dif gnumeric sylk xcf fodp fodg zst qoi pbm pgm ppm; do
    .venv/Scripts/python tools/oracle/execute_oracle.py --format $fmt --all
done
```
- Success: All 20 `oracle-run-summary.json` files show `format_depth_score` ≥ D1; dif/fodt/sylk summaries show D1 (confirmed from TC-OIS-002 packages).

#### Validation
| Check | Method | Pass | Fail-action |
|-------|--------|------|-------------|
| Unit tests pass | `.venv/Scripts/pytest tests/oracle/test_depth_scoring.py` | 4/4 PASS | Fix logic; re-run |
| dif/fodt/sylk at D1 | Read 3 oracle-run-summary.json | `format_depth_score: D1` | TC-OIS-002 incomplete; revert this change, complete TC-OIS-002 |
| No format drops to D0 | Read all 20 oracle-run-summary.json | All D1+ | Per-format investigation; if format had only synthetic properties and TC-OIS-002 didn't cover it, extend TC-OIS-002 scope |

---

### TC-OIS-004: Add executor_config to Oracle Packages

| Field | Value |
|-------|-------|
| State | READY (parallel with TC-OIS-002) |
| Depends-on | TC-OIS-001 |
| Blocks | TC-OIS-005 |
| Files | `oracle/formats/*/oracle-package.yaml` (18 formats: all except csv and fods) |
| Evidence-contract | All 18 oracle-package.yaml files contain `executor_config: {module: ..., callable: ...}`; import check passes for each |
| Rollback-trigger | Import check fails for a format (module path wrong) → fix module path, re-verify; do NOT proceed to TC-OIS-005 until all 18 pass import check |

#### Micro-steps

**MS-004-01** [OPEN]: The Part 6.2 table already contains verified values from agent code reading (lines 774-890 confirmed). Special cases to verify manually:
- `pgm`: execute_pgm_valid_case (lines 819-870) has custom sys.path manipulation before import. Confirm the generic executor can import `pgm.pgm_parser.parse_pgm` without the custom path manipulation (it should work if src/python is on sys.path already).
- `sylk`: callable is `SylkDocument` (class constructor), not a function. The generic invalid executor calls `fn(input_data)` — verify SylkDocument accepts a path string as its first argument.
- `ods`: uses `ods.ods_parser.parse_ods` (not ods_codec); `xcf`: uses `xcf.xcf_parser.XcfImage`; `pbm/ppm/qoi`: use `*_parser.parse_*` pattern.
- Success: All exceptions documented; any format where generic executor cannot work gets a format-specific override note added to TC-OIS-005.

**MS-004-02** [OPEN — after MS-004-01]: Add `executor_config:` block to each of the 18 oracle-package.yaml files using the mapping from MS-004-01. Process formats in alphabetical order (abw, dif, fodg, fodp, fodt, gnumeric, ndjson, ods, odt, pbm, pgm, ppm, qoi, sylk, toml, tsv, xcf, zst).
- Success: All 18 YAML files syntactically valid (no parse error) and contain executor_config block.

**MS-004-03** [OPEN — after MS-004-02]: Run import verification for all 18 formats:
```bash
.venv/Scripts/python -c "
formats = [
    ('abw', 'abw.abw_codec', 'load'),
    ('dif', 'dif.dif_parser', 'parse_dif'),
    # ... all 18
]
for fmt, module, callable_name in formats:
    import importlib
    mod = importlib.import_module(f'src.python.{module}')
    fn = getattr(mod, callable_name)
    print(f'OK: {fmt} -> {module}.{callable_name}')
"
```
- Success: All 18 print `OK:` without ImportError or AttributeError.

#### Validation
| Check | Method | Pass | Fail-action |
|-------|--------|------|-------------|
| YAML validity | `python -c "import yaml; yaml.safe_load(open(f).read())"` per file | No exception | Fix YAML syntax |
| Import check | MS-004-03 script | All 18 OK | Fix module/callable path for failing format |
| No csv/fods modified | `git diff oracle/formats/csv oracle/formats/fods` | No changes | Revert accidental edits |

---

### TC-OIS-005: Implement Generic Invalid Case Executor

| Field | Value |
|-------|-------|
| State | BLOCKED (on TC-OIS-004) |
| Depends-on | TC-OIS-004 (executor_config must exist before generic executor can use it) |
| Blocks | TC-OIS-009 |
| Files | `tools/oracle/execute_oracle.py` (new function + replace lines 1737-1755) |
| Evidence-contract | `execute_generic_invalid_case()` function present; invalid case dispatch loop removes `if format_id in ("csv", "fods"):` guard; zst oracle run shows 4 invalid case verdicts; csv and fods still use their format-specific invalid executors |
| Rollback-trigger | Any format-specific invalid executor breaks after dispatch change → revert dispatch section, investigate routing logic |

#### Micro-steps

**MS-005-01** [OPEN — after TC-OIS-004 DONE]: Add `execute_generic_invalid_case()` to `tools/oracle/execute_oracle.py` immediately after `execute_generic_load_case()`. Full implementation per Part 5, Pillar 1b.
- Success: Function parses, no syntax error; handles sample_ref, input_inline, partial_recovery_allowed, exception/no-exception branches.

**MS-005-02** [OPEN — after MS-005-01]: Replace `if format_id in ("csv", "fods"):` block at line 1737 with universal dispatch:
```python
for case in pkg.get("invalid_cases", []):
    case_id = case["case_id"]
    if case_filter and case_id != case_filter:
        continue
    if format_id == "csv":
        verdict = execute_csv_invalid_case(case, pkg)
    elif format_id == "fods":
        verdict = execute_fods_invalid_case(case, pkg)
    else:
        executor_config = pkg.get("executor_config", {})
        module = executor_config.get("module")
        callable_name = executor_config.get("callable")
        if module and callable_name:
            verdict = execute_generic_invalid_case(case, pkg, format_id, module, callable_name)
        else:
            verdict = make_verdict(
                oracle_id=pkg["oracle_id"], oracle_version=pkg["oracle_version"],
                format_id=format_id, product_id=f"format-factory-{format_id}",
                language="python", case_id=case_id,
                profile="INVALID_INPUT_REJECTION",
                result=RESULT_NOT_APPLICABLE, authority_status="UNKNOWN",
                diagnostics=["No executor_config in oracle-package.yaml for generic invalid case"],
            )
    verdicts.append(verdict)
```
- Success: Dispatch compiles; indentation and loop structure match surrounding code.

**MS-005-03** [OPEN — after MS-005-02]: Add coverage gap warning call at start of `run_oracle_for_format()`:
```python
coverage_gaps = _check_case_coverage(pkg, format_id)
for gap in coverage_gaps:
    print(f"WARNING: {gap}", file=sys.stderr)
```
- Success: Function called; warnings appear in stderr for formats with unexecuted case types.

**MS-005-04** [OPEN — after MS-005-03]: Write unit tests in `tests/oracle/test_generic_invalid_executor.py`:
```python
def test_generic_invalid_raises_returns_pass():
    # Mock callable raises ValueError
    assert verdict["result"] == "PASS"
    assert verdict["depth_level"] == "D0"

def test_generic_invalid_no_raise_returns_fail():
    # Mock callable returns normally
    assert verdict["result"] == "FAIL"
    assert "Expected exception was not raised" in verdict["diagnostics"][0]

def test_generic_invalid_partial_recovery_allowed():
    # callable returns normally, partial_recovery_allowed=True
    assert verdict["result"] == "PASS"
```
- Success: All 3 tests pass.

**MS-005-05** [OPEN — after MS-005-04]: Run oracle for zst to validate live invalid case execution:
```bash
.venv/Scripts/python tools/oracle/execute_oracle.py --format zst --all
```
- Success: oracle-run-summary.json for zst shows 4 additional invalid case verdicts; total cases increases by 4.

**MS-005-06** [OPEN — after MS-005-05]: Confirm csv and fods still use format-specific invalid executors:
```bash
.venv/Scripts/python tools/oracle/execute_oracle.py --format csv --all
.venv/Scripts/python tools/oracle/execute_oracle.py --format fods --all
```
- Success: csv/fods invalid case counts unchanged from pre-TC-OIS-005 baseline.

#### Validation
| Check | Method | Pass | Fail-action |
|-------|--------|------|-------------|
| Unit tests pass | `.venv/Scripts/pytest tests/oracle/test_generic_invalid_executor.py` | 3/3 PASS | Fix executor logic |
| zst invalid cases execute | Read zst oracle-run-summary.json | 4 new verdict entries | Investigate executor_config routing |
| csv/fods unchanged | Compare csv/fods summaries before/after | Same invalid case counts | Revert dispatch section if routing broken |
| No RESULT_NOT_APPLICABLE for formats with executor_config | Check all 18 format summaries | 0 NOT_APPLICABLE from missing executor_config | Fix executor_config or routing |

---

### TC-OIS-006: Remove G2 Test-Suite Fallback

| Field | Value |
|-------|-------|
| State | BLOCKED (on TC-OIS-003) |
| Depends-on | TC-OIS-003 (dif/fodt/sylk must be at D1 before G2 is tightened) |
| Blocks | TC-OIS-009 |
| Files | `tools/supervisor/gate_executor.py` (lines 119-136) |
| Evidence-contract | Lines 119-136 (`using_fallback` block) deleted; `check_g2()` returns FAIL when `passed_cases == 0`; G2 passes for all 20 formats via direct oracle check |
| Rollback-trigger | Any format has `passed_cases == 0` in its oracle-run-summary.json (means oracle didn't run for that format) → DO NOT delete fallback; investigate missing oracle run, re-run oracle, then retry |

#### Micro-steps

**MS-006-01** [OPEN — after TC-OIS-003 DONE]: Pre-check: run gate_executor.py for all 20 formats in dry-run mode and record `passed_cases` from each oracle-run-summary.json:
```bash
for fmt in fods fodt ods odt csv tsv ndjson toml abw dif gnumeric sylk xcf fodp fodg zst qoi pbm pgm ppm; do
    echo "$fmt:"
    python -c "import json; s=json.load(open(f'oracle/formats/$fmt/reports/oracle-run-summary.json')); print(s.get('results',{}).get('PASS',0))"
done
```
- Success: All 20 formats show `PASS > 0`. If any show 0, HALT and run oracle for that format first.

**MS-006-02** [OPEN — after MS-006-01 confirms all >0]: Delete lines 119-136 from `gate_executor.py`:
```python
# DELETE this entire block:
test_dir = REPO_ROOT / "tests" / "python" / format_id
test_count = len(list(test_dir.glob("test_*.py"))) if test_dir.exists() else 0
using_fallback = (passed_cases == 0) and (test_count >= 10)

if using_fallback:
    results.append({...})
    results.append({...})
else:
```
Keep only the direct oracle check path (the `else:` block body, without the `else:`).
- Success: `check_g2()` function has no reference to `using_fallback` or `test_count`.

**MS-006-03** [OPEN — after MS-006-02]: Write unit tests in `tests/supervisor/test_g2_no_fallback.py`:
```python
def test_g2_fails_when_zero_oracle_pass(tmp_path):
    # Create summary with PASS=0
    assert result["passed"] is False
    assert all("fallback" not in c.get("detail", "") for c in result["checks"])

def test_g2_passes_with_real_d1_pass(tmp_path):
    # Create summary with PASS=3, format_depth_score=D1
    assert result["passed"] is True

def test_g2_fails_when_depth_d0(tmp_path):
    # Create summary with PASS=3, format_depth_score=D0
    assert result["passed"] is False
```
- Success: All 3 tests pass.

**MS-006-04** [OPEN — after MS-006-03]: Run gate_executor.py for all 20 formats and confirm G2 PASS:
```bash
for fmt in fods fodt ods odt csv tsv ndjson toml abw dif gnumeric sylk xcf fodp fodg zst qoi pbm pgm ppm; do
    .venv/Scripts/python tools/supervisor/gate_executor.py --format $fmt --gates G2
done
```
- Success: All 20 output `"passed": true` for G2; no format falls back.

#### Validation
| Check | Method | Pass | Fail-action |
|-------|--------|------|-------------|
| No `using_fallback` reference in gate_executor.py | `grep "using_fallback" gate_executor.py` | No output | Re-edit to remove missed references |
| Unit tests pass | `.venv/Scripts/pytest tests/supervisor/test_g2_no_fallback.py` | 3/3 PASS | Fix gate logic |
| All 20 formats pass G2 | MS-006-04 | 20/20 `"passed": true` | Per-format oracle re-run if PASS=0 detected |

---

### TC-OIS-007: Add Source Hash to Oracle Summaries

| Field | Value |
|-------|-------|
| State | READY (independent of depth fix chain) |
| Depends-on | TC-OIS-001 |
| Blocks | TC-OIS-009 |
| Files | `tools/oracle/execute_oracle.py` (new functions + summary dict), `tools/supervisor/gate_executor.py` (advisory check) |
| Evidence-contract | All oracle-run-summary.json files contain `product_source_hash` (sha256:... format) and `oracle_package_hash`; gate_executor G2 output includes `oracle_evidence_fresh` advisory check when hash present |
| Rollback-trigger | Hash computation raises exception for any format (missing src directory) → wrap in try/except, return "sha256:error:{msg}" sentinel; never block oracle run |

#### Micro-steps

**MS-007-01** [OPEN]: Add to `tools/oracle/execute_oracle.py`:
```python
import hashlib  # (add to imports if not present)

def _compute_source_hash(format_id: str) -> str:
    """SHA-256 of all .py files in src/python/{format_id}/, sorted by path."""
    src_dir = REPO_ROOT / "src" / "python" / format_id
    h = hashlib.sha256()
    for py_file in sorted(src_dir.glob("**/*.py")):
        h.update(py_file.read_bytes())
    return f"sha256:{h.hexdigest()}"

def _compute_package_hash(format_id: str) -> str:
    """SHA-256 of the oracle-package.yaml for this format."""
    pkg_path = ORACLE_DIR / "formats" / format_id / "oracle-package.yaml"
    if not pkg_path.exists():
        return "sha256:absent"
    h = hashlib.sha256()
    h.update(pkg_path.read_bytes())
    return f"sha256:{h.hexdigest()}"
```
- Success: Functions present; no import errors.

**MS-007-02** [OPEN — after MS-007-01]: Add fields to summary dict in `run_oracle_for_format()` before `json.dump`:
```python
summary["product_source_hash"] = _compute_source_hash(format_id)
summary["oracle_package_hash"] = _compute_package_hash(format_id)
```
- Success: Summary dict contains both hash fields.

**MS-007-03** [OPEN — after MS-007-02]: Add advisory staleness check to `check_g2()` in `gate_executor.py`:
```python
# After reading summary, before building results:
stored_source_hash = summary.get("product_source_hash", "ABSENT")
if stored_source_hash != "ABSENT":
    # Compute current hash using same logic as execute_oracle.py
    src_dir = REPO_ROOT / "src" / "python" / format_id
    import hashlib
    h = hashlib.sha256()
    for py_file in sorted(src_dir.glob("**/*.py")):
        h.update(py_file.read_bytes())
    current_hash = f"sha256:{h.hexdigest()}"
    if current_hash != stored_source_hash:
        results.append({
            "check": "oracle_evidence_fresh",
            "passed": False,
            "detail": "Source hash changed since last oracle run — re-run recommended (advisory only)",
        })
```
**IMPORTANT**: This advisory check does NOT affect `gate.passed` (do not include in `all(r["passed"] for r in results)` computation). Add to results list AFTER the gate-determining checks.
- Success: Advisory check appears in G2 output when source has changed; does not change `"passed"` field.

**MS-007-04** [OPEN — after MS-007-03]: Write unit test:
```python
def test_source_hash_changes_on_modification(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "codec.py").write_text("def load(): pass")
    h1 = _compute_source_hash_from_dir(src)
    (src / "codec.py").write_text("def load(): return {}")
    h2 = _compute_source_hash_from_dir(src)
    assert h1 != h2

def test_source_hash_stable_on_recompute(tmp_path):
    # Same files, same content → same hash
    assert _compute_source_hash_from_dir(src) == _compute_source_hash_from_dir(src)
```
- Success: Both tests pass.

#### Validation
| Check | Method | Pass | Fail-action |
|-------|--------|------|-------------|
| Hashes present in summaries | Read any oracle-run-summary.json | Contains `product_source_hash` and `oracle_package_hash` | Re-run oracle for that format |
| Hash format correct | Check prefix | Starts with `sha256:` | Fix hash function |
| Advisory doesn't block G2 | Run gate_executor with stale summary | `"all_passed": true` even with advisory `passed: false` | Ensure advisory check excluded from gate determination |

---

### TC-OIS-008: Distribution-Aware V143 Validator

| Field | Value |
|-------|-------|
| State | READY (independent) |
| Depends-on | TC-OIS-001 |
| Blocks | TC-OIS-009 |
| Files | `tools/supervisor/governance_validators_oracle.py` |
| Evidence-contract | `validate_oracle_depth_minimum()` uses D0-majority logic; governance_validator_runner passes with 165 validators; V143 fires WARN for D0-majority format, PASS for D1-majority |
| Rollback-trigger | V143 fires incorrectly for a format that legitimately has many D0 cases (e.g., after TC-OIS-005 adds invalid cases which are all D0) → lower threshold from `>` to `>= 0.7` of total cases |

#### Micro-steps

**MS-008-01** [OPEN]: Replace the all-D0 condition in `validate_oracle_depth_minimum()` with majority-D0:
```python
# Current (fires only when format_depth_score == "D0"):
# if depth_score == "D0": ...

# New:
depth_hist = summary.get("depth_histogram", {})
d0_count = depth_hist.get("D0", 0)
d1_plus_count = sum(v for k, v in depth_hist.items() if k != "D0")
total = d0_count + d1_plus_count
if total > 0 and d0_count > d1_plus_count:
    return {"validator": "V143", "result": "WARN",
            "message": f"D0-majority depth: {d0_count}/{total} cases at D0"}
```
- Success: Logic compiles; fires when D0 > D1+.

**MS-008-02** [OPEN — after MS-008-01]: Write unit tests:
```python
def test_v143_fires_on_d0_majority():
    summary = {"format_id": "fmt", "format_depth_score": "D1",
               "depth_histogram": {"D0": 4, "D1": 2}}
    result = validate_oracle_depth_minimum(summary)
    assert result["result"] == "WARN"

def test_v143_no_fire_on_d1_majority():
    summary = {"format_id": "fmt", "format_depth_score": "D1",
               "depth_histogram": {"D0": 2, "D1": 4}}
    result = validate_oracle_depth_minimum(summary)
    assert result["result"] == "PASS"

def test_v143_fires_on_all_d0():
    summary = {"format_id": "fmt", "format_depth_score": "D0",
               "depth_histogram": {"D0": 5}}
    result = validate_oracle_depth_minimum(summary)
    assert result["result"] == "WARN"
```
- Success: All 3 pass.

**MS-008-03** [OPEN — after MS-008-02]: Run governance_validator_runner.py and confirm count is still 165:
```bash
.venv/Scripts/python tools/supervisor/governance_validator_runner.py
```
- Success: Output shows `Total validators: 165` (or equivalent count check passes in tests).

#### Validation
| Check | Method | Pass | Fail-action |
|-------|--------|------|-------------|
| Unit tests pass | `.venv/Scripts/pytest` tests for V143 | 3/3 PASS | Fix logic |
| Validator count still 165 | governance_validator_runner.py | 165 | If count changed, investigate which validator was added/removed |
| FODS doesn't trigger WARN | Run V143 on FODS summary (6D1+4D0) | PASS | Adjust threshold — 4 D0 with 6 D1 is D1-majority; should PASS |

---

### TC-OIS-009: Full Oracle Execution and Gate Verification

| Field | Value |
|-------|-------|
| State | BLOCKED (on TC-OIS-003, TC-OIS-005, TC-OIS-006, TC-OIS-007, TC-OIS-008) |
| Depends-on | All of TC-OIS-003 through TC-OIS-008 must be DONE |
| Blocks | TC-OIS-010 |
| Files | All oracle-run-summary.json files (20 formats) |
| Evidence-contract | 20 oracle-run-summary.json committed with: format_depth_score≥D1, product_source_hash present, coverage_gaps field present; G2 passes for all 20; 165 governance validators pass |
| Rollback-trigger | Any format fails G2 → per-format investigation; revert relevant taskcard's change if root cause identified |

#### Micro-steps

**MS-009-01** [OPEN]: Run oracle for all 20 formats:
```bash
for fmt in fods fodt ods odt csv tsv ndjson toml abw dif gnumeric sylk xcf fodp fodg zst qoi pbm pgm ppm; do
    .venv/Scripts/python tools/oracle/execute_oracle.py --format $fmt --all
done
```
- Success: All 20 complete without error; oracle-run-summary.json updated for all 20.

**MS-009-02** [OPEN — after MS-009-01]: Verify all 20 formats at D1+:
```bash
for fmt in fods fodt ods odt csv tsv ndjson toml abw dif gnumeric sylk xcf fodp fodg zst qoi pbm pgm ppm; do
    python -c "
import json
s = json.load(open(f'oracle/formats/$fmt/reports/oracle-run-summary.json'))
depth = s.get('format_depth_score', 'D0')
status = 'PASS' if depth in ('D1','D2','D3') else 'FAIL'
print(f'$fmt: {depth} -> {status}')
"
done
```
- Success: All 20 print PASS.

**MS-009-03** [OPEN — after MS-009-01]: Verify dif/fodt/sylk have real property names in summaries (not just `loaded`). Read their oracle-run-summary.json and check that the observed properties recorded include a non-synthetic key.
- Success: dif, fodt, sylk show non-synthetic property in their run summary diagnostics or depth evidence.

**MS-009-04** [OPEN — after MS-009-01]: Verify invalid case verdicts appear for formats with executor_config (spot-check zst):
```bash
python -c "
import json
s = json.load(open('oracle/formats/zst/reports/oracle-run-summary.json'))
print('total:', s['total_cases'], 'pass:', s['results'].get('PASS', 0))
print('coverage_gaps:', s.get('coverage_gaps', []))
"
```
- Success: zst total_cases > pre-TC-OIS-005 count (4 more invalid cases executed).

**MS-009-05** [OPEN — after MS-009-01]: Run G2 gate for all 20 formats:
```bash
for fmt in fods fodt ods odt csv tsv ndjson toml abw dif gnumeric sylk xcf fodp fodg zst qoi pbm pgm ppm; do
    .venv/Scripts/python tools/supervisor/gate_executor.py --format $fmt --gates G2
done
```
- Success: All 20 show `"passed": true`; none use fallback text in detail.

**MS-009-06** [OPEN — after MS-009-01]: Run governance validators:
```bash
.venv/Scripts/python tools/supervisor/governance_validator_runner.py
```
- Success: All 165 validators pass (or known pre-existing exceptions).

**MS-009-07** [OPEN — after MS-009-01]: Idempotency check — re-run oracle for 3 representative formats and compare summaries:
```bash
.venv/Scripts/python tools/oracle/execute_oracle.py --format fods --all
.venv/Scripts/python tools/oracle/execute_oracle.py --format csv --all
.venv/Scripts/python tools/oracle/execute_oracle.py --format zst --all
```
Compare oracle-run-summary.json for each before/after second run. Differences allowed: `executed_at` timestamp and `product_source_hash` (if source is unchanged, hash should be identical). All counts, depths, and coverage_gaps must be identical.
- Success: No functional differences between first and second run summaries.

#### Validation
| Check | Method | Pass | Fail-action |
|-------|--------|------|-------------|
| 20/20 D1+ | MS-009-02 | All PASS | Per-format investigation |
| 20/20 G2 PASS | MS-009-05 | All `"passed": true` | If fallback text appears → TC-OIS-006 incomplete |
| 165 validators pass | MS-009-06 | No new failures | Per-validator investigation |
| Idempotency | MS-009-07 | Only `executed_at` differs | Identify non-deterministic field; make deterministic |

---

### TC-OIS-010: Update Documentation and Idempotency Verification

| Field | Value |
|-------|-------|
| State | BLOCKED (on TC-OIS-009) |
| Depends-on | TC-OIS-009 |
| Blocks | NONE (terminal) |
| Files | `docs/oracle/oracle-investigation-final-report.md`, `oracle/registry/format-oracle-registry.yaml`, `docs/oracle/oracle-readiness-assessment.md` |
| Evidence-contract | All 3 files updated in-place (no new files created); post-implementation section in final-report reflects actual post-fix state |
| Rollback-trigger | N/A — documentation only |

#### Micro-steps

**MS-010-01** [OPEN]: Append post-implementation section to `docs/oracle/oracle-investigation-final-report.md`:
```markdown
## Post-Implementation Update (shiny-percolating-sky, 2026-07-XX)

Root causes RC-1 through RC-7 addressed:
- RC-1/RC-2: SYNTHETIC_PROPERTIES excludes `loaded`/`result_type` from D1 credit
- RC-3: G2 gate fallback removed — oracle evidence now required
- RC-4/RC-7: coverage_gaps field added to committed summaries; case_evidence added (TC-OIS-011)
- RC-5: product_source_hash and oracle_package_hash added to all summaries
- RC-6: SAL facts remain manual audit trail (no change — out of scope)

Post-fix state: All 20 formats at D1+ via real property comparison.
18 formats now execute invalid cases via generic invalid executor.
```
- Success: Section appended; no prior content modified.

**MS-010-02** [OPEN — after MS-010-01]: Update `oracle/registry/format-oracle-registry.yaml` depth_achieved fields for dif, fodt, sylk (change from `D1_SYNTHETIC` to `D1_REAL` or equivalent post-fix value).
- Success: 3 format entries updated; no other entries modified.

**MS-010-03** [OPEN — after MS-010-02]: Update `docs/oracle/oracle-readiness-assessment.md` maturity scores:
- Product Oracle: 3 → 4 (GOVERNED_COMPLETE — false-green paths closed)
- Acquisition Oracle: 2 → 2 (unchanged)
- Success: Maturity scores updated; 12 completion counters updated to reflect new state.

#### Validation
| Check | Method | Pass | Fail-action |
|-------|--------|------|-------------|
| No new files created | `git status` | Only existing files modified | Delete any accidentally created files |
| Post-implementation section present | Read oracle-investigation-final-report.md | Section present at end | Add if missing |
| snoopy-juggling-seal.md untouched | `git diff plans/strategic/snoopy-juggling-seal.md` | No changes | Revert any accidental edits |

---

### TC-OIS-011: Evidence Traceability (NEW)

| Field | Value |
|-------|-------|
| State | PROPOSED (can run in parallel with TC-OIS-003) |
| Depends-on | TC-OIS-001 |
| Blocks | TC-OIS-009 (should complete before full verification) |
| Files | `tools/oracle/execute_oracle.py` (summary generation section) |
| Evidence-contract | oracle-run-summary.json files include `case_evidence` list with one entry per PASS case, each containing `case_id`, `properties_compared` (list of property names), `deviations` count; formats with generic executor show which properties were actually checked |
| Rollback-trigger | case_evidence bloats summary files beyond 50KB → limit to first 10 cases or truncate property list to names-only (no values) |

#### Micro-steps

**MS-011-01** [OPEN]: Define `case_evidence` schema: each entry = `{case_id: str, depth_level: str, properties_compared: [str], deviations: int}`. Values (not just names) are intentionally excluded from committed evidence to avoid secret exposure and file bloat.
- Success: Schema defined in code comment; matches YAML-serializable structure.

**MS-011-02** [OPEN — after MS-011-01]: In `run_oracle_for_format()`, collect per-case evidence during verdict accumulation:
```python
case_evidence = []
for verdict in verdicts:
    if verdict.get("result") == "PASS":
        # Extract property names from observed dict keys that are non-synthetic
        observed = verdict.get("observed", {})
        props = [k for k in observed if k not in ("loaded", "result_type")]
        case_evidence.append({
            "case_id": verdict["case_id"],
            "depth_level": verdict.get("depth_level", "D0"),
            "properties_compared": props,
            "deviations": len(verdict.get("deviations", [])),
        })
```
- Success: case_evidence populated per format; non-empty for formats with real properties.

**MS-011-03** [OPEN — after MS-011-02]: Add to summary dict:
```python
summary["case_evidence"] = case_evidence
```
- Success: oracle-run-summary.json includes case_evidence list.

**MS-011-04** [OPEN — after MS-011-03]: Run oracle for 3 formats (fods, dif after TC-OIS-002, zst) and verify:
- fods case_evidence shows `properties_compared: ["sheet_count", "cell_count", ...]`
- dif case_evidence shows real property names (not empty)
- zst case_evidence shows both valid and invalid case entries appropriately
- Success: case_evidence non-empty and showing real property names.

#### Validation
| Check | Method | Pass | Fail-action |
|-------|--------|------|-------------|
| case_evidence present in summary | Read fods oracle-run-summary.json | `case_evidence` key exists | Re-run oracle |
| No synthetic props in properties_compared | Check case_evidence entries | No `loaded` or `result_type` in any properties_compared list | Fix collection logic |
| File size reasonable | `ls -la oracle/formats/fods/reports/oracle-run-summary.json` | < 50KB | Truncate to first 10 cases |

---

## Part 10 — Dependency DAG

```
TC-OIS-001 (READY)
├── TC-OIS-002 (READY — no code deps, runs immediately after scope check)
│   └── TC-OIS-003 [BLOCKED on 002] (HARD — depth fix AFTER package upgrade)
│       └── TC-OIS-006 [BLOCKED on 003] (HARD — G2 removal AFTER depth fix)
│
├── TC-OIS-004 (READY — parallel with 002, both independent of each other)
│   └── TC-OIS-005 [BLOCKED on 004] (executor_config must exist)
│
├── TC-OIS-007 (READY — fully independent)
├── TC-OIS-008 (READY — fully independent)
└── TC-OIS-011 (PROPOSED — can start after scope check)

After TC-OIS-003 + TC-OIS-005 + TC-OIS-006 + TC-OIS-007 + TC-OIS-008 + TC-OIS-011 all DONE:
    TC-OIS-009 [BLOCKED on all above]
        └── TC-OIS-010 [BLOCKED on 009] (terminal)
```

**Parallel execution opportunities:**
- Wave 1 (simultaneous): TC-OIS-002, TC-OIS-004, TC-OIS-007, TC-OIS-008, TC-OIS-011
- Wave 2 (after Wave 1): TC-OIS-003, TC-OIS-005
- Wave 3 (after Wave 2): TC-OIS-006
- Wave 4 (after Wave 3): TC-OIS-009
- Wave 5 (after Wave 4): TC-OIS-010

---

## Part 11 — Critical Paths and Hard Stops

| Critical path | Risk if violated | Hard stop condition |
|---------------|-----------------|---------------------|
| TC-OIS-002 BEFORE TC-OIS-003 | dif/fodt/sylk drop to D0 → G2 fails | If oracle shows any format at D0 after TC-OIS-003 AND TC-OIS-002 is incomplete → REVERT TC-OIS-003, complete TC-OIS-002, retry |
| TC-OIS-003 BEFORE TC-OIS-006 | G2 removed before D1 restored → pipeline fails | Verify all 20 formats at D1+ (MS-003-04) before deleting G2 fallback |
| TC-OIS-004 BEFORE TC-OIS-005 | Generic invalid executor has no module/callable → all 18 formats return NOT_APPLICABLE | Do not add TC-OIS-005 code until TC-OIS-004 import checks pass |
| MS-006-01 pre-check BEFORE deleting fallback | Unknown format at 0 PASS would lose its only G2 protection | If ANY format shows PASS=0 in pre-check → halt TC-OIS-006, run oracle for that format, retry |

---

## Part 12 — Files Modified

| File | Change | Taskcard |
|------|--------|---------|
| `tools/oracle/execute_oracle.py` | SYNTHETIC_PROPERTIES, depth fix (line 713) | TC-OIS-003 |
| `tools/oracle/execute_oracle.py` | `execute_generic_invalid_case()` function | TC-OIS-005 |
| `tools/oracle/execute_oracle.py` | Invalid case dispatch — remove `if format_id in ("csv", "fods"):` guard | TC-OIS-005 |
| `tools/oracle/execute_oracle.py` | `_check_case_coverage()` function + coverage_gaps in summary | TC-OIS-005 |
| `tools/oracle/execute_oracle.py` | `_compute_source_hash()` + `_compute_package_hash()` + summary fields | TC-OIS-007 |
| `tools/oracle/execute_oracle.py` | case_evidence collection + summary field | TC-OIS-011 |
| `tools/supervisor/gate_executor.py` | Delete using_fallback block (lines 119-136) | TC-OIS-006 |
| `tools/supervisor/gate_executor.py` | Add advisory staleness check to check_g2() | TC-OIS-007 |
| `tools/supervisor/governance_validators_oracle.py` | V143 majority-D0 logic | TC-OIS-008 |
| `oracle/formats/dif/oracle-package.yaml` | Real expected_model_properties + executor_config | TC-OIS-002 + TC-OIS-004 |
| `oracle/formats/fodt/oracle-package.yaml` | Real expected_model_properties + executor_config | TC-OIS-002 + TC-OIS-004 |
| `oracle/formats/sylk/oracle-package.yaml` | Real expected_model_properties + executor_config | TC-OIS-002 + TC-OIS-004 |
| `oracle/formats/*/oracle-package.yaml` (15 other generic formats) | executor_config block | TC-OIS-004 |
| `docs/oracle/oracle-investigation-final-report.md` | Append post-implementation section | TC-OIS-010 |
| `oracle/registry/format-oracle-registry.yaml` | Update depth_achieved for dif/fodt/sylk | TC-OIS-010 |
| `docs/oracle/oracle-readiness-assessment.md` | Update maturity scores | TC-OIS-010 |
| `tests/oracle/test_depth_scoring.py` | New test file (4 tests) | TC-OIS-003 |
| `tests/oracle/test_generic_invalid_executor.py` | New test file (3 tests) | TC-OIS-005 |
| `tests/supervisor/test_g2_no_fallback.py` | New test file (3 tests) | TC-OIS-006 |

---

## Part 13 — Taskcard Status Summary

| Taskcard | State | Blocks | Wave |
|----------|-------|--------|------|
| TC-OIS-001 | READY | TC-OIS-002 (informal) | Pre-work |
| TC-OIS-002 | READY | TC-OIS-003 (HARD) | 1 |
| TC-OIS-003 | BLOCKED on 002 | TC-OIS-006 | 2 |
| TC-OIS-004 | READY | TC-OIS-005 | 1 |
| TC-OIS-005 | BLOCKED on 004 | TC-OIS-009 | 2 |
| TC-OIS-006 | BLOCKED on 003 | TC-OIS-009 | 3 |
| TC-OIS-007 | READY | TC-OIS-009 | 1 |
| TC-OIS-008 | READY | TC-OIS-009 | 1 |
| TC-OIS-009 | BLOCKED on 003,005,006,007,008,011 | TC-OIS-010 | 4 |
| TC-OIS-010 | BLOCKED on 009 | NONE (terminal) | 5 |
| TC-OIS-011 | PROPOSED | TC-OIS-009 | 1 |

# Exhaustive Product-Source Certification & Healing Plan — Revised

```yaml
plan_type: product_certification
mission_id: CERT-EXHAUST-HEAL-20260703
predecessor: plans/.claude/crispy-jingling-snail.md (TERMINAL_CLOSED)
reassessment_date: 2026-07-03
status: IN_PROGRESS
```

## A. Current-State Reassessment (2026-07-03)

The original plan was built from **stale prior-run data**. A thorough re-verification of
the live system shows the following changes since planning:

| Dimension | Plan Assumed | Verified Reality | Status |
|-----------|-------------|-----------------|--------|
| Dashboard | Stale (68 stubs, 27 exceptions) | Current (2026-07-02), 0 stubs, 0 exceptions | OBSOLETE |
| Certification status | 1 CERTIFIED, 19 WITH_KNOWN_GAPS | **All 20 CERTIFIED** | OBSOLETE |
| Weak assertions | 188 across 17 formats | **0 across all formats** | OBSOLETE |
| Roundtrip gaps | ODT=GAP, FODP=GAP | **ODT=PASS, FODP=PASS** | OBSOLETE |
| Security audits | 0 files | **9/20 have audits** (9 XML+ZST PASS) | PARTIAL |
| FODS collection errors | 109 total | **32 FODS-specific** in ledger | STILL NEEDED |
| Cross-language parity | Tool planned | **Tool does not exist** | STILL NEEDED |
| Property-based testing | None | Hypothesis not installed; 1 trivial file | STILL NEEDED |
| Mutation testing | Not started | mutmut installed; CSV/ZST=100%; **FODS=50%** | NEEDS_HARDENING |
| CI certification gate | Planned | **ci_certification_gate.py does not exist** | STILL NEEDED |
| .NET deletions | Not in plan | 88 test files staged (intentional GI-FODS-NET-001) | Tracked by buzzing-wiggling-whistle |

---

## B. Item-by-Item Status of the Previous Plan

### W0: Dashboard Regeneration — OBSOLETE
**Evidence:** `reports/certification/certification-report.md` generated 2026-07-02, shows
all 20 formats CERTIFIED (not CERTIFIED_WITH_KNOWN_GAPS). Per-format `stub-audit.json` files
confirm 0 material stubs. Dashboard "Material stubs: 0, Weak assertions: 0, Uncovered exceptions: 0".
**Nothing remains.**

### W1: Weak Assertion Healing (188 assertions) — OBSOLETE
**Evidence:** `reports/certification/{fods,fodt,abw,gnumeric,ods,fodg,tsv,ndjson}/assertion-quality.json`
all report `weak_assertion_count: 0`. Dashboard "Weak assertions (score 1/5): 0 test functions".
**Nothing remains.**

### W2: Roundtrip Gap Closure (ODT, FODP) — OBSOLETE
**Evidence:**
- `reports/certification/odt/roundtrip-audit.json` → `"status": "PASS"`, test_file: `test_odt_sample_roundtrip.py`
- `reports/certification/fodp/roundtrip-audit.json` → `"status": "PASS"`, 6 roundtrip tests
**Nothing remains.**

### W3: Security Verification — PARTIALLY DONE
**Evidence:** 9 formats have passing security audits (FODS, FODT, FODG, FODP, ODS, ODT, ABW, GNUMERIC, ZST).
Remaining 11 formats (CSV, DIF, PBM, PGM, PPM, QOI, SYLK, TOML, TSV, XCF, NDJSON) have no `security-audit.json`.
Of these, **non-XML formats** (DIF, PBM, PGM, PPM, QOI, SYLK, TOML, TSV, XCF, NDJSON) have no XXE
or entity-expansion attack surface → NOT_APPLICABLE status appropriate. CSV warrants a basic audit
(no XML parsing but stream-size and injection patterns apply).
**Remaining: Write NOT_APPLICABLE JSON for 10 formats + basic CSV audit.**
No `tools/certification/security_test_generator.py` exists.

### W4: FODS Collection Errors — STILL NEEDED (32 files)
**Evidence:** `registry/known-failure-ledger.yaml` documents 32 FODS test files (R258-R286 range) that
import functions not present in `src/python/fods/__init__.py` `__all__`. These cause `ImportError`
at `pytest` collection time, making them invisible to the test runner (neither PASS nor FAIL —
they simply never run). The ledger documents this as TC-HYGIENE-FODS-001-A (2026-06-21, unresolved).
**Root cause:** Tests written against planned gap-ledger capabilities before implementations existed.
**Remaining: Triage each — delete dead tests OR implement missing functions.**

### W5: Cross-Language Behavioral Parity — STILL NEEDED
**Evidence:** `tools/certification/cross_language_parity_checker.py` does not exist.
`reports/certification/cross-product-parity.json` exists for structural API comparison only —
it does not verify behavioral equivalence (same input → same output in both Python and .NET).
**Remaining: Build parity checker, run for 7 dual-track formats.**

### W6: .NET Assertion Quality — RESTRUCTURED
**Evidence:** The 88 deleted `.cs` test files are intentional (GI-FODS-NET-001 incident remediation,
tracked by `buzzing-wiggling-whistle` plan, Phase 5 / Lane 4d). These files supported Category D
constant-return methods that have no ODF basis and are being removed. The deletion is staged but
tracked separately. This plan should NOT duplicate the .NET quality audit since it's actively
being addressed by another plan.
**Status: Defer to buzzing-wiggling-whistle plan. Remove from this plan.**

### W7: Property-Based Testing — STILL NEEDED
**Evidence:** `hypothesis` is not installed (not in pyproject.toml, not importable).
Only 1 trivially named "property" test file exists (`test_r560_xcf_multilayer_property.py`) and
it uses simple parametric testing, not Hypothesis. Pytest marker `property_based` registered but
zero tests use it.
**Remaining: Install hypothesis, write property tests for 3 pilot formats (FODS, CSV, ZST).**

### W8: Mutation Testing — PARTIALLY DONE
**Evidence:**
- `reports/certification/fods/mutation-baseline.json` → kill rate: **50% (15/30), NEEDS_HARDENING** (2026-07-01)
- `reports/certification/csv/mutation-baseline.json` → kill rate: **100% (30/30), STRONG** (2026-07-01)
- `reports/certification/zst/mutation-baseline.json` → kill rate: **100% (30/30), STRONG** (2026-07-01)
**Remaining: Harden FODS `parser.py` tests to kill the 15 surviving mutants (return_none, negate_comparison, off_by_one, swap_bool patterns).**

### W9-W10: Reconciliation and Final Audit — STILL NEEDED
**Evidence:** No `ci_certification_gate.py` exists. No `reports/certification/final-audit-report.md` exists.
**Remaining: CI gate tool + final audit report.**

---

## C. Remaining Problems (Genuine)

### C1 — FODS Parser Mutation Weakness (50% kill rate)
**Root cause:** Tests for `src/python/fods/parser.py` do not distinguish between correct
and mutated return values. Surviving mutation patterns: `return_none` (functions that return
objects are mutated to return None — not caught), `negate_comparison` (comparisons inverted —
not caught), `off_by_one` (index/count expressions off by 1 — not caught), `swap_bool`
(True/False swapped — not caught).
**Impact:** Core parser can have 15 categories of behavioral mutations that pass all current tests.
This is a meaningful correctness gap.
**Fix:** Add assertions that check specific values, lengths, and conditions in FODS parser tests.

### C2 — FODS Test Collection Errors (32 test files)
**Root cause:** 32 tests in `tests/python/fods/` (R258-R286 range) import functions that are
planned in the gap ledger but not yet implemented. They fail at `pytest` collection time with
`ImportError`, meaning they neither pass nor fail — they disappear from all test reporting.
**Impact:** These tests provide zero verification. If the functions DO get implemented in the
future, the tests could silently remain broken forever.
**Fix:** For each file: (a) if the function is permanently removed from `__all__` — delete the test; (b) if the function is planned — implement it with correct behavior.

### C3 — Security Audit Gaps (11 formats missing security-audit.json)
**Root cause:** Security testing was only performed on XML-capable formats in the prior plan.
11 remaining formats (CSV, DIF, PBM, PGM, PPM, QOI, SYLK, TOML, TSV, XCF, NDJSON) have
no security-audit artifact.
**Impact:** Certification matrix shows incomplete coverage. For non-XML formats, the security
risk is minimal, but the artifact gap breaks the dashboard's completeness claim.
**Fix:** Write `NOT_APPLICABLE` security-audit.json for 10 non-XML formats. Write a basic
CSV security audit covering stream-size limits and delimiter injection.

### C4 — No Property-Based Tests (0 Hypothesis tests)
**Root cause:** Hypothesis was never installed or integrated. The `property_based` pytest marker
exists in config but nothing uses it.
**Impact:** No generative testing for parse-invariant properties (e.g., "parse never crashes on
valid inputs," "roundtrip preserves structure").
**Fix:** Install hypothesis. Write ~5 property tests per pilot format (FODS, CSV, ZST).

### C5 — No Cross-Language Behavioral Parity Tests
**Root cause:** `cross-product-parity.json` compares API surface, not behavior. No tool exists
to verify that parsing the same file in Python and .NET produces equivalent models.
**Impact:** Silent behavioral divergence between Python FOSS and .NET commercial readers.
**Fix:** Build minimal parity checker; run on CSV, FODS, TSV (highest-value dual-track formats).

### C6 — No CI Certification Gate
**Root cause:** `ci_certification_gate.py` was never created.
**Impact:** Future changes can silently regress certification dimensions without automatic detection.
**Fix:** Create gate script that reads current certification baselines and fails on regression.

---

## D. Revised Plan (Current Reality Only)

### Priority and Dependencies

```
TC-MUT-001 (FODS mutation hardening)     — no deps, highest impact
TC-COL-001 (FODS collection errors)      — no deps, P2
TC-SEC-001 (Security audit completion)   — no deps, P2 (mostly NOT_APPLICABLE)
TC-PBT-001 (Property-based tests)        — no deps, P3
TC-PAR-001 (Cross-language parity)       — no deps, P3
TC-GATE-001 (CI certification gate)      — depends on all above
TC-AUD-001 (Final audit)                 — depends on TC-GATE-001
```

---

### TC-MUT-001: FODS Parser Mutation Hardening

**Why needed:** FODS mutation kill rate is 50% (15/30 mutations survive). CSV and ZST are at
100%. The 15 surviving mutants indicate tests that don't verify specific return values,
comparisons, or index arithmetic.

**Approach:**
1. Read `reports/certification/fods/mutation-baseline.json` to identify surviving mutation types
2. Read `src/python/fods/parser.py` to understand which functions have surviving mutants
3. Add targeted test cases in `tests/python/fods/` that assert specific values:
   - For `return_none` survivors: add `assert result is not None` + `assert result.attr == expected`
   - For `negate_comparison` survivors: add boundary tests that distinguish True from False results
   - For `off_by_one` survivors: add count assertions (`assert len(sheets) == 3`, not just `> 0`)
   - For `swap_bool` survivors: add both True-case and False-case tests for boolean functions
4. Re-run `mutmut run --paths-to-mutate src/python/fods/parser.py --tests-dir tests/python/fods/`
5. Target: kill rate ≥ 80% (improve from 50% to 80%+)
6. Update `reports/certification/fods/mutation-baseline.json` with new results

**Critical files:**
- `src/python/fods/parser.py`
- `reports/certification/fods/mutation-baseline.json`
- `tests/python/fods/test_parser_basic.py` (extend here)

**Evidence required:** Updated mutation-baseline.json with kill_rate_pct ≥ 80

---

### TC-COL-001: FODS Test Collection Error Triage

**Why needed:** 32 test files import unimplemented functions and fail silently at collection time.
These tests provide zero verification coverage.

**Approach:**
1. Read `registry/known-failure-ledger.yaml` to get the list of 32 FODS test files
2. Read `src/python/fods/__init__.py` to get the current `__all__` list
3. For each test file:
   - Attempt to find the imported function in `__all__` or `src/python/fods/`
   - If function is absent from `__all__` AND has no implementation plan: **delete test file**, remove ledger entry
   - If function IS in `__all__` but implementation is missing: **implement minimal version**, verify test passes
4. Re-run `.venv/Scripts/pytest tests/python/fods/ --continue-on-collection-errors -q`
5. Verify: collection error count = 0
6. Remove resolved entries from `registry/known-failure-ledger.yaml`

**Critical files:**
- `registry/known-failure-ledger.yaml`
- `src/python/fods/__init__.py`
- `tests/python/fods/test_r258_*.py` through `test_r286_*.py` (32 files)

**Evidence required:** pytest output showing 0 collection errors for fods/

---

### TC-SEC-001: Security Audit Completion

**Why needed:** 11 formats lack `security-audit.json`. Dashboard cannot claim complete coverage.

**Approach:**
1. For 10 non-XML formats (DIF, PBM, PGM, PPM, QOI, SYLK, TOML, TSV, XCF, NDJSON):
   Write `reports/certification/{fmt}/security-audit.json` with:
   ```json
   {"format": "{fmt}", "status": "NOT_APPLICABLE", "reason": "Non-XML format: no entity expansion, XXE, or DTD attack surface. Primary risk is file size exhaustion — covered by existing load() size limits."}
   ```
2. For CSV: Write a basic security audit:
   - Check if `csv_parser.py` has file-size or line-count guards
   - Check if delimiter injection is documented/handled
   - Write `reports/certification/csv/security-audit.json` with actual findings
3. Update certification dashboard to include security dimension for all 20 formats

**Critical files:**
- `src/python/csv/csv_parser.py` (check size limits)
- `tools/certification/certification_dashboard.py` (add security dimension for non-XML formats)

**Evidence required:** 20 × security-audit.json files present; dashboard shows security dimension

---

### TC-PBT-001: Property-Based Testing (Pilot Formats)

**Why needed:** The `property_based` pytest marker exists but 0 tests use it. Hypothesis is
not installed. Generative testing would catch parse-invariant violations that targeted tests miss.

**Approach:**
1. Install: `.venv/Scripts/pip install hypothesis`
2. Verify: `.venv/Scripts/python -c "import hypothesis; print(hypothesis.__version__)"`
3. Write `tests/python/fods/test_fods_property.py` (5-8 tests):
   - `@given(st.integers(1, 5))` sheet counts → parse → `len(sheets) == n`
   - `@given(st.text(min_size=1, max_size=100))` cell values → roundtrip → value preserved
   - Parse never raises on valid generated XML structure
4. Write `tests/python/csv_format/test_csv_property.py` (5 tests):
   - `@given(st.lists(st.lists(st.text())))` → write → re-parse → row/col counts match
5. Write `tests/python/zst/test_zst_property.py` (5 tests):
   - `@given(st.binary())` → compress → decompress → equality (use `.venv/Scripts/python`)
6. Run all three files, verify PASS
7. Write `reports/certification/{fods,csv,zst}/property-test-report.json`

**Critical files:**
- `tests/python/fods/test_fods_property.py` (create)
- `tests/python/csv_format/test_csv_property.py` (create)
- `tests/python/zst/test_zst_property.py` (create)

**Evidence required:** 3 test files, all tests PASS; 3 property-test-report.json files

---

### TC-PAR-001: Cross-Language Behavioral Parity (3 Pilot Formats)

**Why needed:** `cross-product-parity.json` compares API surface only. No tool verifies that
Python and .NET parse the same file to equivalent results.

**Approach:**
1. Create `tools/certification/cross_language_parity_checker.py`:
   - Input: format name, sample file path
   - Python path: import format package, call `load()`/`parse_*()`, serialize result to JSON
   - .NET path: run `dotnet run --project tests/net/{fmt}/ -- {sample_path}` to get JSON output
   - Compare: key model fields (e.g., sheet count, row count, cell values for FODS)
2. Implement for CSV (simplest), FODS, TSV (highest-value dual-track formats)
3. If `dotnet` CLI is unavailable: mark as `BLOCKED_EXTERNAL` in result, continue
4. Write `reports/certification/{fmt}/cross-impl-parity.json` per format

**Critical files:**
- `tools/certification/cross_language_parity_checker.py` (create)
- `samples/by-format/fods/valid/` (sample inputs)
- `samples/by-format/csv/valid/` (sample inputs)

**Evidence required:** 3 × cross-impl-parity.json; PASS or documented BLOCKED_EXTERNAL

---

### TC-GATE-001: CI Certification Gate

**Why needed:** No mechanism prevents future changes from silently regressing certification.

**Approach:**
1. Create `tools/certification/ci_certification_gate.py`:
   - Reads `reports/certification/certification-baseline.json` (locked baseline)
   - For each format: runs stub_detector, checks assertion quality from existing JSON
   - Reads mutation baselines and verifies kill rate hasn't regressed below locked threshold
   - Exits 0 if all dimensions pass, exits 1 with specific regression report if any fail
2. Write `reports/certification/certification-baseline.json` locking current values:
   - 20 formats: CERTIFIED
   - Material stubs: 0
   - Uncovered exceptions: 0
   - Weak assertions: 0
   - FODS mutation kill rate: locked at post-TC-MUT-001 value
3. Document CI integration pattern in `docs/certification/ci-integration.md`

**Critical files:**
- `tools/certification/ci_certification_gate.py` (create)
- `reports/certification/certification-baseline.json` (create)

**Evidence required:** Tool runs without error; exits 0 on clean repo; exits 1 with useful message on simulated regression

---

### TC-AUD-001: Final Independent Audit

**Why needed:** Confirm `UNKNOWN_MATERIAL_BEHAVIOR = 0` after all preceding fixes.

**Approach:**
1. Run all certification tools portfolio-wide:
   - `stub_detector.py` for all 20 formats → expect 0 material stubs
   - `exception_coverage_checker.py` → expect 0 uncovered exceptions
   - `assertion_quality_scorer.py` → expect 0 weak assertions
   - `execute_oracle.py` → expect 73/73 PASS
2. Run all property tests → expect PASS
3. Verify mutation baselines → FODS ≥ 80%, CSV/ZST = 100%
4. Verify FODS collection errors = 0
5. Verify 20/20 security-audit.json present
6. Run `certification_dashboard.py` → regenerate final dashboard
7. Write `reports/certification/final-audit-report.md` with:
   - Per-format final disposition (VERIFIED / VALIDLY_OUT_OF_SCOPE / BLOCKED_TRUE_EXTERNAL)
   - UNKNOWN_MATERIAL_BEHAVIOR count (target: 0)
   - Final verdict string

**Evidence required:** `final-audit-report.md` with final verdict

---

## E. Execution Order

```
TC-MUT-001  (FODS mutation hardening)     — Sprint 1
TC-COL-001  (FODS collection triage)      — Sprint 2
TC-SEC-001  (Security audit completion)   — Sprint 3 (fast, mostly NOT_APPLICABLE writes)
TC-PBT-001  (Property-based testing)      — Sprint 4
TC-PAR-001  (Cross-language parity)       — Sprint 5
TC-GATE-001 (CI certification gate)       — Sprint 6
TC-AUD-001  (Final audit)                 — Sprint 7
```

**Total: 7 sprints** (down from 13-18 in original plan, because 8 waves are obsolete)

## F. Out of Scope (Deferred or Tracked Elsewhere)

- **W6 (.NET assertion quality):** Tracked by `buzzing-wiggling-whistle` plan (GI-FODS-NET-001). Category D method deletion and test disposal in progress. Not duplicating here.
- **Performance benchmarks:** No evidence of performance regressions. No blocker for certification. Defer to future sprint.
- **Mutation testing for non-pilot formats:** CSV and ZST already at 100%. FODS is the only format below threshold. Expand mutation testing to other formats only if new code is added.
- **Fuzzing infrastructure:** Existing malformed-input tests (`test_parser_malformed.py`) cover primary adversarial cases. Full fuzzing (AFL, libFuzzer) requires infrastructure not yet present. Defer.

## G. Taskcard Status Summary

| Taskcard | Status |
|----------|--------|
| TC-MUT-001 | CLOSED |
| TC-COL-001 | CLOSED |
| TC-SEC-001 | CLOSED |
| TC-PBT-001 | CLOSED |
| TC-PAR-001 | CLOSED |
| TC-GATE-001 | CLOSED |
| TC-AUD-001 | CLOSED |


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-02T20:45:55.656478+00:00"
  locked_by: "0ce45942c388"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->

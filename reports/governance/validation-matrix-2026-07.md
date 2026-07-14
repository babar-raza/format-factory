# Validation Matrix — Governance and Machinery Healing Sprint
# date: 2026-07-14
# authority: lively-leaping-elephant (TC-GOV-LLE-010)
# plan: plans/.claude/lively-leaping-elephant.md

---

## A. Governance Files Changed

| File | Change Description |
|------|--------------------|
| `docs/code-quality/production-library-best-practices-checklist.md` | CREATED — 75 items, 10 topic areas, [Vnn]/[ADVISORY]/[DEFINED_ONLY]/[UNVALIDATED] markers |
| `reports/governance/src-monolith-register.yaml` | AMENDED — fixed V39→V35/V66 in 32 entries; added root_cause/structural_failure/heal_taskcard to top-4 HIGH entries |
| `reports/governance/src-architecture-gap-register.yaml` | AMENDED — fixed V39→V35/V66 in 32 entries; added detection_tested: false to all entries |
| `reports/governance/root-cause-analysis-2026-07.md` | CREATED — 4 structural failures with line-number evidence; secondary causes; what-works section |
| `registry/source-structure-baseline.json` | AMENDED — added heal_policy section; remediation_status: pending to top-5 HIGH entries |
| `docs/automation/supervisor-worker-contract.md` | AMENDED — added code_quality_delta schema block for PRODUCT_SOURCE items |
| `tools/supervisor/sprint_executor_validate.py` | AMENDED — added Phase 19 (code_quality_delta check for known_violations files) |
| `tools/supervisor/check_continuation.py` | AMENDED — added _compute_violation_pressure() + violation_pressure field in CONTINUE output |
| `docs/code-quality/production-library-standard-v2.md` | AMENDED — fixed remediation_deadline factual error in V72 desc; added V187/V188/V193 to Dimension 14 |
| `tools/supervisor/governance_validators_ext5.py` | CREATED — V187-V193 validators |
| `tools/supervisor/governance_validator_runner.py` | AMENDED — added V187-V193 import block; updated count 216→223 |
| `tests/supervisor/test_governance_validators.py` | AMENDED — added TestValidatorDetectionRealFiles class (8 real-file detection tests) |
| `pyproject.toml` | AMENDED — registered real_src pytest mark |
| `plans/product-healing-taskcards.md` | CREATED — TC-HEAL-SRC-001 through TC-HEAL-SRC-005 |
| `plans/master-plan.md` | AMENDED — §125 added with TC-HEAL-SRC-* table |

---

## B. Validators Added

| ID | Name | blocks_sprint | Introduced Via |
|----|------|--------------|----------------|
| V187 | validate_function_count_per_file | True (new files) | explicit block + shadow mode (threshold=5) |
| V188 | validate_io_in_domain_model | True (new files) | explicit block |
| V189 | validate_analytics_statelessness | False (WARN) | explicit block |
| V190 | validate_test_tier_presence | False (WARN) | explicit block |
| V191 | validate_explicit_all_defined | False (WARN) | explicit block |
| V192 | validate_changed_files_exist | False (WARN) | explicit block |
| V193 | validate_remediation_deadline_expired | False (WARN) | explicit block + shadow mode (threshold=3) |

**Count:** start=216, end=223, delta=+7
**Detection tests:** 8/8 passing (`pytest tests/supervisor/test_governance_validators.py -m real_src -v`)
**Validator invariant test:** PASS (223 registered ≥ 90% threshold of 201)
**Validator count test:** PASS (ran=223 + skipped=0 = expected=223)

**Run results (empty declaration on full repo — captured after TC-PILOT-FIX-002):**
- Ran: 223, Skipped: 0, FAIL: 1 (V102), WARN: 31, PASS: 191
- blocks_sprint: True (V102 blocks)
- V193: PASS — all remediation_deadline values are 2026-09-01 or 2027-01-01 (future); V193 will become active 2026-09-01
- V187-V192: PASS on empty declaration (no changed_files to inspect)

See `reports/governance/validator-run-2026-07.txt` for full run capture.

---

## C. Structural Failures Addressed

### SF-1: Validators tested at registration level, not detection level
**Fix:** Added `TestValidatorDetectionRealFiles` class in `tests/supervisor/test_governance_validators.py`
- `@pytest.mark.real_src` marker registered in pyproject.toml
- 8 tests invoke V187/V188/V192/V193 on real source files
- test_v187_warns_on_xcf_image_metrics: V187 fires on 104-fn file (WARN, in baseline) ✓
- test_v187_warns_on_abw_word_document: V187 fires on 101-fn file (WARN, in baseline) ✓
- test_v187_passes_on_clean_file: V187 PASS on csv/models.py (0 fn) ✓
- test_v188_warns_not_fails_on_baseline_domain_model: V188 WARN not FAIL for baseline csv/models.py ✓
- test_v192_warns_on_nonexistent_path: V192 WARN on declared-but-absent path ✓
- test_v192_passes_on_real_path: V192 PASS on existing path ✓
- test_v193_warns_on_past_deadline: V193 WARN with synthetic expired-deadline entry ✓
- test_v193_passes_when_status_complete: V193 PASS when remediation_status=complete ✓

**Remaining gap:** Existing validators (V35/V66/V40) still tested only with synthetic fixtures.
The new class adds 8 real-file tests for V187-V193 only. A comprehensive migration of all validators
to real-file testing remains out-of-scope for this sprint.

### SF-2: Baseline has deadlines but no status tracking
**Fix:** 
- Added `heal_policy` top-level section to `registry/source-structure-baseline.json` — formalizes removal criteria and remediation_status values
- Added `remediation_status: "pending"` to top-5 HIGH severity entries (xcf_image_metrics.py, abw/word_document.py, qoi/image_document.py, ndjson/json_stream.py, sylk/sylk_analytics.py)
- V193 (`validate_remediation_deadline_expired`) fires when deadline < today AND status != "complete"
- V193 registered in shadow mode (threshold=3) for safe promotion

**Verification:** `grep -c "remediation_status" registry/source-structure-baseline.json` → ≥5

**Remaining gap:** Only top-5 entries have remediation_status. 332 entries still lack the field.
A systematic batch-add of remediation_status to all entries is a separate migration sprint.

### SF-3: Evidence grading inspects existence, not improvement
**Fix:**
- Added `code_quality_delta` block to `docs/automation/supervisor-worker-contract.md`
- Phase 19 in `tools/supervisor/sprint_executor_validate.py` checks for the block in PRODUCT_SOURCE items targeting known_violations files
- Phase 19 is WARN-only (many existing declarations predate this requirement)

**Verification:** `grep -n "Phase 19" tools/supervisor/sprint_executor_validate.py` finds the new phase

**Remaining gap:** Phase 19 is WARN-only; old declarations that don't include code_quality_delta
won't fail. Full enforcement requires a separate migration window.

### SF-4: Sprint selection is violation-blind
**Fix:**
- `_compute_violation_pressure(repo_root)` function added to `check_continuation.py`
- Returns `{total, past_deadline, high_severity, level}` — level CRITICAL/HIGH/MEDIUM/LOW
- Emitted as `violation_pressure` field in the CONTINUE JSON output
- With current baseline (304 src/ entries, 0 past-deadline, 11 high_severity), level=HIGH
  (TC-PILOT-FIX-001 corrected prior bug where total was always 0; actual level=HIGH not CRITICAL)

**Verification:** `python tools/supervisor/check_continuation.py` JSON contains `violation_pressure`

**Remaining gap (Part B):** The next-sprint generator does not yet read `violation_pressure` to
auto-select healing tasks. The field is visible to human operators and the autonomous loop,
but task-ordering is not yet mechanically enforced. This is a known partial fix.

---

## D. Source Architecture Findings

| Metric | Value |
|--------|-------|
| Total entries in `src-monolith-register.yaml` | 32 |
| HIGH severity entries | 4 (xcf_image_metrics, abw/word_document.py, fods_analytics.py, zst_codec.py) |
| Top function-density: xcf_image_metrics.py | 104 fn |
| Top function-density: abw/word_document.py | 101 fn |
| Total `known_violations` in baseline | 337 |
| Entries with `remediation_deadline` | 337 |
| Entries with `remediation_status` | 5 (added this sprint) |
| Entries past deadline | 0 (all deadlines are 2026-09-01 or 2027-01-01 — all future) |
| V193 will begin firing | 2026-09-01 (when 244 entries with 2026-09 deadline first expire) |
| Entries with `remediation_status: complete` | 0 (none healed yet) |

---

## E. Root Causes Summary

4 structural failures + 5 content-level causes per `reports/governance/root-cause-analysis-2026-07.md`:

| ID | Description | Fix | Status |
|----|-------------|-----|--------|
| SF-1 | Validators tested at registration, not detection | Real-file test class (8 tests) | PARTIAL — new validators only |
| SF-2 | Baseline deadlines with no status tracking | heal_policy + remediation_status + V193 | PARTIAL — top-5 only |
| SF-3 | Evidence grading without quality metrics | code_quality_delta schema + Phase 19 | PARTIAL — WARN-only |
| SF-4 | Violation-blind sprint selection | violation_pressure in continuation signal | PARTIAL — field added, task-ordering not yet |
| SC-1 | No function-count validator | V187 (BLOCKING for new, WARN for baseline) | COMPLETE |
| SC-2 | V66 keyword-matching gap | (out of scope — no V66 changes) | NOT ADDRESSED |
| SC-3 | explicit_all: 19/27 formats FAIL | V191 (WARN advisory) | PARTIAL — advisory only |
| SC-4 | Analytics separation: 10/20 formats FAIL | TC-HEAL-SRC-002/003 taskcards created | PLANNED |
| SC-5 | Gap registers cite V39 (nonexistent) | Fixed in both registers | COMPLETE |

---

## F. Machinery Proof

- `governance_validators_ext5.py`: 7 validators, syntactically valid, importable
- `governance_validator_runner.py`: V187-V193 block registered, count 216→223
- `_EXPECTED_VALIDATOR_COUNT = 223`
- `_VALIDATOR_REGISTRY` has ≥202 entries (90%+ threshold met)
- Detection tests: 8/8 pass (`pytest -m real_src -v`)
- V187 in shadow mode (threshold=5): will promote to blocking after 5 confirmed true-positive observations
- V193 in shadow mode (threshold=3): will promote to blocking after 3 confirmed true-positive observations
- Canary shadow registry: `cat .supervisor/validator-shadow-registry.yaml` shows V187 + V193 entries

---

## G. Remaining Gaps (Honest Assessment)

| Gap | Severity | Next Action |
|-----|----------|-------------|
| V66 uses keyword-matching (not AST-based) | MEDIUM | Out of scope — requires AST role detection redesign |
| explicit_all migration: 19/27 formats FAIL | MEDIUM | Separate migration sprint |
| changed_files self-reporting: Phase 14 WARN-only | LOW | Full git verification requires non-trivial refactor |
| Baseline remediation_status: only 5/337 entries | HIGH | Batch migration sprint needed |
| Next-sprint generator: violation_pressure not yet hooked into task ordering | MEDIUM | Part B of TC-GOV-LLE-007 |
| V35/V40/V66 detection tests: still synthetic-only | MEDIUM | Future TestValidatorDetectionRealFiles expansion |
| Automated baseline entry removal on healing | LOW | Manual process only — removal_criteria in heal_policy |

---

## H. Final Verdict

**Verdict:** `MACHINERY_READY_PRODUCT_HEALING_NOT_STARTED`

The 4 structural machinery gaps (SF-1 through SF-4) are addressed with targeted mechanical additions.
Each fix is independently verifiable:
- SF-1 → real-file detection tests exist and pass
- SF-2 → V193 fires on expired deadlines; heal_policy schema added
- SF-3 → Phase 19 WARN on missing code_quality_delta
- SF-4 → violation_pressure in continuation JSON

The product source monoliths (TC-HEAL-SRC-001 through TC-HEAL-SRC-005) are defined as governed
taskcards with V187 validator gates. No product source was changed this sprint (governance-only).

All 5 content-level causes have a clear next action. None of them block product deepening sprints
(they are either addressed by WARN validators or have planned taskcards).

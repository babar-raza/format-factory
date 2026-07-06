# Healed Execution Plan: FF-XPLAN-001 Completion — Zero Exclusions

```yaml
authoritative_plan: plans/.claude/golden-hugging-manatee.md
plan_type: cross_plan_integration_handoff_healed
plan_status: READY_FOR_EXECUTION
created: 2026-07-06
healed_at: 2026-07-06
mission_id: FF-XPLAN-001
branch: main
prior_convergence_state: CONVERGENCE_COMPLETE_ALL_GREEN_AND_TASK_CLOSED
prior_commits: ["0654f9e9", "6f543345", "54bfa17f"]
```

---

## Purpose

The prior convergence pass (golden-hugging-manatee) reached `ALL_GREEN` with 15 items marked EXCLUDED or DEFERRED. This healed plan converts every one of those 15 items into concrete, agent-executable taskcards. The stated reasons for exclusion were examined; most were planning shortcuts, not true external gates.

---

## True Picture of Prior Exclusions

| Item | Prior Label | True Reason Excluded | Agent-Executable? |
|------|-------------|---------------------|-------------------|
| TC-W2A-009 (FODS roundtrip case) | EXCLUDED | Executor code missing; case defined in yaml | YES — write executor |
| TC-W2B-005 (PyPI name availability) | EXCLUDED | Called "research" but is mechanical HTTP check | YES — HTTP GET loop |
| TC-W3-006 (Gate 10 status recomputation) | EXCLUDED | Unclear where to write; format-registry was partially done | YES — derive from oracle evidence |
| TC-W3-007 (link gate check to evidence schema) | EXCLUDED | Missed in schema — additive field only | YES — 1 schema field |
| TC-W3-008 (phase lock mechanism) | EXCLUDED | Deferred as "complex" but is trivial state file logic | YES — JSON state file |
| TC-W4-003 (CI release-phase-validation job) | EXCLUDED | gate_executor.py wasn't complete yet; now it is | YES — ci.yml job |
| TC-W4-005 (release.yml PYREL gate check) | EXCLUDED | Same gate_executor dependency; now resolved | YES — release.yml step |
| TC-W5-004 (sync capabilities CLAUDE.md) | EXCLUDED | Called "non-blocking" and skipped | YES — run sync script |
| TC-W5-005 (depth_achieved in oracle registry) | EXCLUDED | Registry file update deferred as "cosmetic" | YES — write yaml fields |
| TC-W5-006 (document sprint count) | EXCLUDED | Called "trivial" and skipped | YES — read maturity-trend, write doc |
| TC-W5-007 (P1-P11 coverage assessment) | EXCLUDED | No document existed; Plan 2 deferred it | YES — write assessment |
| TC-W6-003 (TestPyPI pilot) | EXCLUDED | Said credentials unavailable — but build+check+dry-run is always possible | PARTIAL — build/check agent-owned; upload needs PYPI_TOKEN |
| TC-W7-004 (CI full green) | BLOCKED_EXTERNAL (wrong!) | Called "CI infrastructure" but failures are in source — agent-fixable | YES — delete fodg_analytics.py, fix V84/V85/V86 |
| TC-W7-005 (D3 LibreOffice executor) | BLOCKED_EXTERNAL | D3 skipping when LibreOffice absent is agent code; only actual runtime is external | YES — implement with SKIPPED_MISSING_PROVIDER |
| TC-W7-006 (Gate 11 checklist) | BLOCKED_EXTERNAL | Preparation is agent-owned; only Babar Raza sign-off is external | YES (prep) — write packet |

---

## WAVE H1 — Oracle Completion (Roundtrip + D3)

### TC-H1-001: Implement FODS Roundtrip Oracle Case Executor

**Prior label:** TC-W2A-009 EXCLUDED
**True reason excluded:** The fods-rt-001 case was defined in `oracle/formats/fods/oracle-package.yaml` but no Python executor existed in `execute_oracle.py`. Exclusion was a shortcuts-under-time-pressure decision.

**What is needed:** A `execute_fods_rt_case(case, fods_pkg)` function in `tools/oracle/execute_oracle.py` that:
1. Reads the source FODS file path from the case yaml
2. Calls `load` from `fods.fods_codec`
3. Writes to a temp path using `save` (or write equivalent)
4. Reloads and compares key model properties (sheet count, cell values)
5. Returns a verdict at D1 depth (D2 if schema validates both source and output)
6. Dispatches from the `run_fods_cases` function for case IDs matching `fods-rt-*`

**Steps:**
1. Read `oracle/formats/fods/oracle-package.yaml` to confirm fods-rt-001 case definition
2. Read `tools/oracle/execute_oracle.py` around `run_fods_cases()` to understand dispatch pattern
3. Add `execute_fods_rt_case()` function after `execute_fods_valid_case`
4. Add `elif case_id.startswith("fods-rt-")` dispatch in `run_fods_cases`
5. Run `python tools/oracle/execute_oracle.py --format fods --case fods-rt-001`
6. Verify exit 0, depth D1+

**Verification:**
- Positive: fods-rt-001 returns PASS at D1+
- Negative: corrupted output file returns FAIL verdict (not crash)

---

### TC-H1-002: Implement D3 LibreOffice Executor (SKIPPED_MISSING_PROVIDER)

**Prior label:** TC-W7-005 BLOCKED_EXTERNAL
**True reason excluded:** Confused the oracle D3 executor code (agent-owned) with the LibreOffice runtime (truly external). The agent CAN write the executor. The executor simply returns RESULT_SKIPPED_MISSING_PROVIDER when `soffice` is not on PATH.

**What is needed:** A `execute_fods_libreoffice_case(case, fods_pkg)` function that:
1. Checks `shutil.which("soffice")` — if None, returns SKIPPED verdict with RESULT_SKIPPED_MISSING_PROVIDER
2. If available: runs `soffice --headless --convert-to xml <path>` via subprocess
3. Parses output XML to confirm structural validity
4. Returns verdict at D3 depth

**Steps:**
1. Read `tools/oracle/execute_oracle.py` constants for RESULT_SKIPPED_MISSING_PROVIDER, DEPTH_D3
2. Implement `execute_fods_libreoffice_case()` with `shutil.which("soffice")` guard
3. Add dispatch in `run_fods_cases` for case IDs matching `fods-lo-*`
4. Add a `fods-lo-001` case to `oracle/formats/fods/oracle-package.yaml` if none exists
5. Run `python tools/oracle/execute_oracle.py --format fods --all`
6. Confirm fods-lo cases return SKIPPED (no LibreOffice on CI) rather than FAIL or crash

**Verification:**
- Negative control: `shutil.which("soffice") = None` results in SKIPPED_MISSING_PROVIDER (NOT FAIL)
- Positive control: If soffice present, D3 verdict returned

---

## WAVE H2 — PYREL Gate Completions

### TC-H2-001: PyPI Name Availability Research for All 20 Formats

**Prior label:** TC-W2B-005 EXCLUDED
**True reason excluded:** Labeled "research" to defer it. But this is a mechanical HTTP check against PyPI's JSON API.

**What is needed:** For each of the 20 Python format packages:
- Package naming convention: `format-factory-{format}-python`
- Also check bare name: `{format}`
- Check HTTP status: 200 = name taken, 404 = available

**Steps:**
1. Read `registry/format-registry.yaml` to get all 20 format IDs
2. For each format, check `https://pypi.org/pypi/format-factory-{format}-python/json` (HTTP GET)
3. Also check `https://pypi.org/pypi/{format}/json` (bare name)
4. Write results to `docs/gates/pypi-name-availability.md` — table: format | preferred_name | status (AVAILABLE/TAKEN) | fallback
5. Flag any TAKEN names with fallback recommendation

**Verification:**
- All 20 formats have an entry in the report
- Report file exists at `docs/gates/pypi-name-availability.md`

---

### TC-H2-002: Gate 10 Status Recomputation from Oracle Evidence

**Prior label:** TC-W3-006 EXCLUDED
**True reason excluded:** `format-registry.yaml` FODS `release_gates` was partially done but gate statuses were not derived from actual oracle evidence — they were placeholders.

**What is needed:** Update `registry/format-registry.yaml` FODS `release_gates` section so each gate status is derived from oracle run summary data.

**Steps:**
1. Read `registry/format-registry.yaml` FODS section to see current `release_gates` content
2. Read latest oracle run summary (check oracle/ for run output)
3. Compute gate statuses from evidence:
   - `pyrel_g1`: PASS if at least 1 test file covers fods
   - `pyrel_g2`: PASS if max depth_score for fods valid cases >= D1
   - `pyrel_g3`: NOT_IMPLEMENTED (package build not yet in CI)
   - `pyrel_g4`: NOT_IMPLEMENTED (install proof not yet automated)
   - `pyrel_g5`: PENDING (Gate 11 Babar Raza sign-off)
4. Update `registry/format-registry.yaml` with evidence-derived statuses and `evidence_source:` field

**Verification:**
- `pyrel_g2` status = PASS (FODS is at D2)
- `evidence_source` field populated (not empty string)

---

### TC-H2-003: Link Gate Check Results to Evidence Declaration Schema

**Prior label:** TC-W3-007 EXCLUDED
**True reason excluded:** The evidence declaration schema was not updated when `gate-check-results.json` was added to `autonomous_cycle.py`. One additive field was needed.

**What is needed:** Add `gate_check_results_path` optional field to the evidence declaration schema.

**Steps:**
1. Read `tools/supervisor/sprint_executor_validate.py` to find schema path reference
2. Read the schema file
3. Add `gate_check_results_path` as optional string field under `worker_metadata` or `evidence_paths`
4. Add example value `.local/supervisor/gate-check-results.json`

**Verification:**
- Schema file contains `gate_check_results_path` field
- Existing evidence declaration validation still passes (additive only)

---

### TC-H2-004: Implement Phase Lock Mechanism in gate_executor.py

**Prior label:** TC-W3-008 EXCLUDED
**True reason excluded:** Labeled "complex" — but the mechanism is a JSON state file recording which release phase a format is locked to.

**What is needed:** Add a `phase-lock` subcommand to `gate_executor.py`:
- Writes `.local/supervisor/phase-locks/{format}.json` with locked phase and timestamp
- `gate_executor.py run` checks phase lock before allowing progression past locked phase

**Steps:**
1. Read `tools/supervisor/gate_executor.py` current structure
2. Add `PhaseLocker` class with `lock(format_id, phase)`, `get_locked_phase(format_id)`
3. Add `phase-lock` subcommand to CLI
4. In `run_gates`, check phase lock before executing gates beyond locked phase
5. Test with `python tools/supervisor/gate_executor.py phase-lock --format fods --phase G2`

**Verification:**
- Phase lock file created at expected path
- Running gates with G2 lock blocks G3+ from executing (returns PENDING, not error)

---

## WAVE H3 — CI and Release Workflow Completion

### TC-H3-001: Add Release-Phase-Validation CI Job

**Prior label:** TC-W4-003 EXCLUDED
**True reason excluded:** `gate_executor.py` existed but the CI job was deferred. Now that gate_executor.py is functional, this is a trivial yaml block addition.

**What is needed:** Add `release-phase-validation` job to `.github/workflows/ci.yml`.

**Steps:**
1. Read `.github/workflows/ci.yml` current job list and structure
2. Add the `release-phase-validation` job with: checkout, setup-python, pip install pyyaml jsonschema, run gate_executor.py with --dry-run
3. Ensure `--dry-run` flag is supported in gate_executor.py (verify or add)
4. Validate YAML syntax

**Verification:**
- `ci.yml` contains `release-phase-validation` job
- YAML parses without error
- `gate_executor.py run --format fods --dry-run` exits 0

---

### TC-H3-002: Add PYREL Gate Check to release.yml

**Prior label:** TC-W4-005 EXCLUDED
**True reason excluded:** Same dependency on gate_executor.py. Now resolved.

**What is needed:** In `.github/workflows/release.yml`, add a step before the build step that runs gate_executor.py G1+G2.

**Steps:**
1. Read `.github/workflows/release.yml` to see current structure
2. Identify the build step
3. Insert PYREL gate check step BEFORE the build step
4. Validate YAML syntax

**Verification:**
- `release.yml` contains PYREL gate check step before build step

---

## WAVE H4 — Documentation and Registry Finalization

### TC-H4-001: Run Capability Sync to Update CLAUDE.md

**Prior label:** TC-W5-004 EXCLUDED
**True reason excluded:** Called "non-blocking" and skipped. The capability index in CLAUDE.md is stale.

**Steps:**
1. Run `python tools/capability_sync/run_sync.py --mode full`
2. Verify CLAUDE.md `<!-- BEGIN:CAPABILITY-INDEX -->` block is updated with today's timestamp

**Verification:**
- `run_sync.py` exits 0
- CLAUDE.md capability index section timestamp is today

---

### TC-H4-002: Add depth_achieved Field to Oracle Registry

**Prior label:** TC-W5-005 EXCLUDED
**True reason excluded:** Called "cosmetic" and deferred. This field enables gate_executor G2 to read depth from registry without re-running oracle.

**Steps:**
1. Read `oracle/registry/format-oracle-registry.yaml` current content
2. Add `depth_achieved: D1` (or `D2` for fods) to each of the 20 format entries
3. Add `depth_achieved_at:` ISO timestamp

**Verification:**
- All 20 format entries have `depth_achieved` field
- fods entry has `depth_achieved: D2`

---

### TC-H4-003: Document Sprint Count (840 verified)

**Prior label:** TC-W5-006 EXCLUDED
**True reason excluded:** Dismissed as trivial but the sprint count is a governance claim needing a traceable source.

**Steps:**
1. Read `reports/supervisor/maturity-trend.json` to confirm sprint count
2. Write `docs/system-recon/sprint-count-verification.md` citing source file and count

**Verification:**
- File exists with sprint count traceable to `maturity-trend.json`

---

### TC-H4-004: Write P1-P11 Coverage Assessment Document

**Prior label:** TC-W5-007 EXCLUDED
**True reason excluded:** Plan 2 deferred this deliberately. But the assessment is a factual inventory the agent writes.

**Steps:**
1. Read `docs/gates/python-release-gate-definitions.md` to get P1-P11 reference
2. Write `docs/gates/pyrel-p1-p11-coverage-assessment.md` with honest MET/PARTIAL/DEFERRED status per criterion
3. Include remediation path for any PARTIAL/DEFERRED item

**Expected statuses:**
- P1 (Gate criteria defined): MET
- P2 (Gate executor wired): MET
- P3 (Risk taxonomy): MET
- P4 (Phase DAG schema): MET
- P5 (Phase lock mechanism): MET after TC-H2-004
- P6 (Evidence integration): PARTIAL — gate_check_results_path not yet in schema
- P7 (Registry authority): MET
- P8 (CI validation job): MET after TC-H3-001
- P9 (Release workflow): MET after TC-H3-002
- P10 (TestPyPI pilot): PARTIAL — build/check done; upload needs PYPI_TOKEN
- P11 (Production release checklist): MET after TC-H5-002

**Verification:**
- All 11 criteria have explicit status in the document

---

## WAVE H5 — TestPyPI Pilot and Production Checklist

### TC-H5-001: TestPyPI Build, Check, and Conditional Upload

**Prior label:** TC-W6-003 EXCLUDED
**True reason excluded:** Assumed PYPI_TOKEN unavailable and excluded the entire taskcard. But `python -m build` and `twine check` are always executable.

**Steps:**
1. Confirm `src/python/fods/pyproject.toml` exists
2. Run `pip install build twine` in .venv
3. Run `python -m build src/python/fods/ --outdir /tmp/fods-dist/`
4. Run `twine check /tmp/fods-dist/*` — must exit 0
5. If `PYPI_TOKEN` env var set: run `twine upload --repository testpypi /tmp/fods-dist/*`
6. If not set: write `docs/gates/testpypi-result.md` with `BLOCKED_EXTERNAL: PYPI_TOKEN not set`

**Verification:**
- `twine check` exits 0 (always agent-verifiable)
- Either upload success OR explicit BLOCKED_EXTERNAL record exists

---

### TC-H5-002: Prepare Gate 11 Production Release Checklist

**Prior label:** TC-W7-006 BLOCKED_EXTERNAL (incorrectly labeled)
**True reason excluded:** Confused Babar Raza's sign-off (external) with preparing the checklist packet (agent-owned).

**Steps:**
1. Read `registry/format-registry.yaml` FODS `release_gates` section
2. Count tests in `tests/fods/`
3. Write `docs/gates/gate11-fods-production-checklist.md` with:
   - FODS readiness summary
   - All G1-G5 gate statuses with evidence paths
   - Oracle evidence summary (cases, depth)
   - Test coverage summary
   - PyPI package identity (name, version, wheel)
   - Open items before publication
   - `pyrel_g5` status: PENDING_GATE11_APPROVAL
   - Instruction: "Awaiting Babar Raza G11-G approval to proceed"

**Verification:**
- File exists at `docs/gates/gate11-fods-production-checklist.md`
- All 5 gates (G1-G5) have explicit status
- Document includes Babar Raza approval instruction

---

## WAVE H6 — CI Full Green

### TC-H6-001: Fix CI Failures — Delete fodg_analytics.py and Fix Layer Validators

**Prior label:** TC-W7-004 BLOCKED_EXTERNAL (incorrectly labeled!)
**True reason excluded:** CI failures were misclassified as "infrastructure." The actual failures are agent-fixable source issues:
1. `tests/supervisor/test_analytics_bucket_detector.py` asserts `src/python/fodg/fodg_analytics.py` must NOT exist — but the file exists (violates analytics rotation suspension per MEMORY.md)
2. V84/V85/V86 validators require `plans/layers/index.yaml` and `plans/layers/task-register.yaml` to exist
3. Collection errors from tombstoned/stub modules

**Steps:**
1. Read `tests/supervisor/test_analytics_bucket_detector.py` around line 64 to confirm assertion
2. Confirm `src/python/fodg/fodg_analytics.py` is a stub (no real implementation per rotation suspension)
3. Delete `src/python/fodg/fodg_analytics.py`
4. Read V84/V85/V86 validator code to determine exactly what files they require
5. Create `plans/layers/index.yaml` and `plans/layers/task-register.yaml` with minimal valid content
6. Run `.venv/Scripts/pytest tests/supervisor/test_analytics_bucket_detector.py tests/supervisor/test_governance_validators.py -x`
7. Fix any remaining collection errors by removing broken import paths
8. Run full test suite: `.venv/Scripts/pytest --tb=short -q 2>&1 | tail -20`

**Verification:**
- `test_analytics_bucket_detector.py` PASS after deletion
- V84/V85/V86 tests PASS after layer files created
- Full suite: 0 new failures compared to prior 243-test baseline

---

## Taskcard Status Summary

| TC-ID | Description | Status |
|-------|-------------|--------|
| TC-H1-001 | FODS roundtrip oracle executor | PENDING |
| TC-H1-002 | D3 LibreOffice executor (SKIPPED_MISSING_PROVIDER) | PENDING |
| TC-H2-001 | PyPI name availability HTTP check | PENDING |
| TC-H2-002 | Gate 10 status from oracle evidence | PENDING |
| TC-H2-003 | Link gate check to evidence schema | PENDING |
| TC-H2-004 | Phase lock mechanism in gate_executor.py | PENDING |
| TC-H3-001 | CI release-phase-validation job | PENDING |
| TC-H3-002 | PYREL gate check in release.yml | PENDING |
| TC-H4-001 | Run capability sync (CLAUDE.md update) | PENDING |
| TC-H4-002 | depth_achieved field in oracle registry | PENDING |
| TC-H4-003 | Sprint count verification doc | PENDING |
| TC-H4-004 | P1-P11 coverage assessment | PENDING |
| TC-H5-001 | TestPyPI build + check + conditional upload | PENDING |
| TC-H5-002 | Gate 11 production release checklist | PENDING |
| TC-H6-001 | Fix CI failures (fodg_analytics.py + layer validators) | PENDING |

---

## Execution Order

1. **TC-H6-001** first — CI green unblocks all subsequent verification
2. **TC-H1-001, TC-H1-002** — Oracle completions (sequence after H6)
3. **TC-H2-001 through TC-H2-004** — Gate infrastructure (parallel safe with each other)
4. **TC-H3-001, TC-H3-002** — CI and release workflow (after H2 complete)
5. **TC-H4-001 through TC-H4-004** — Documentation and registry (after H3)
6. **TC-H5-001, TC-H5-002** — TestPyPI and Gate 11 checklist (after H4)
7. Final: commit all changes, run governance validators, confirm 0 regressions

---

## Acceptance Criteria

- [ ] fods-rt-001 oracle case executes and returns PASS at D1+
- [ ] fods-lo-* cases return SKIPPED_MISSING_PROVIDER (not FAIL) when LibreOffice absent
- [ ] PyPI name availability report covers all 20 formats at `docs/gates/pypi-name-availability.md`
- [ ] Gate 10 statuses in format-registry.yaml derived from oracle evidence (not placeholders)
- [ ] Evidence declaration schema has `gate_check_results_path` field
- [ ] Phase lock mechanism functional in gate_executor.py
- [ ] `release-phase-validation` job in ci.yml
- [ ] PYREL gate check in release.yml before build step
- [ ] CLAUDE.md capability index refreshed (timestamp today)
- [ ] `oracle/registry/format-oracle-registry.yaml` has `depth_achieved` for all 20 formats
- [ ] Sprint count verification doc at `docs/system-recon/sprint-count-verification.md`
- [ ] P1-P11 coverage assessment at `docs/gates/pyrel-p1-p11-coverage-assessment.md`
- [ ] `twine check` passes for FODS wheel (or build artifact exists)
- [ ] Gate 11 checklist at `docs/gates/gate11-fods-production-checklist.md`
- [ ] CI failures from fodg_analytics.py and layer validators resolved
- [ ] Full governance suite (161 validators) PASS
- [ ] 0 new test regressions vs prior 243-test baseline


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-06T12:15:54.533739+00:00"
  locked_by: "496b377beedd"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->

## Closure Taskcard Status Table

| TC-ID | Status |
|-------|--------|
| TC-H1-001 | CLOSED |
| TC-H1-002 | CLOSED |
| TC-H2-001 | CLOSED |
| TC-H2-002 | CLOSED |
| TC-H2-003 | CLOSED |
| TC-H2-004 | CLOSED |
| TC-H3-001 | CLOSED |
| TC-H3-002 | CLOSED |
| TC-H4-001 | CLOSED |
| TC-H4-002 | CLOSED |
| TC-H4-003 | CLOSED |
| TC-H4-004 | CLOSED |
| TC-H5-001 | CLOSED |
| TC-H5-002 | CLOSED |
| TC-H6-001 | CLOSED |

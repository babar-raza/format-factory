# Plan: Found-Issue Ownership Protocol — Gap-Fill, Healing & Verification
## Plan ID: optimized-meandering-giraffe
## Plan Type: machinery_hardening
## Mission ID: FIOP-FULL-001
## Forensic Version: 2 (hardened 2026-07-10 — 14 findings fixed)

---

## Context

The FOUND-ISSUE-MVP-001 initiative (2026-07-04) established the core found-issue infrastructure:
- Policy: `docs/governance/found-issue-ownership-policy.md`
- Registries: `found-issue-register.yaml`, `root-cause-register.yaml`, `fixture-analysis-register.yaml`, `blast-radius-register.yaml`
- Validators V130-V133 (declaration-level) and V139-V142 (register-level)
- Skill `/found-issue-ownership` registered and operational
- Pilots 1, 2, 4 completed (FI-001 to FI-004 = broken fixtures; FI-008 = LOC regressions)
- ⚠ Pilots 3, 5 (flaky), 6, 7 NOT completed — Context v1 falsely claimed pilots 5 completed

**Current state (2026-07-10):**
- 1169 tests from prior sprint summary; next-sprint.md shows 21558 passed after PQ-BUNDLE-FORENSICS-REPAIR-001
- expected_count in governance_validator_runner.py = **167** (line 813, confirmed)
- Five issues in register: FI-008 (taskcarded), FI-010 to FI-013 (in_repair)

**Gaps the 27-section protocol exposes:**
1. FI-008 closed_at=null, disposition=null — never formally verified/closed
2. FI-010 to FI-013 in_repair — but their cap values in FI register (642/604/508/479) do NOT match source-structure-baseline.json actual caps (687/633/511/483 respectively) → these may be stale issues where caps were set at file-creation time
3. Missing artifact types: `governed-exclusion-register.yaml`, `negative-control-register.yaml`, `reports/found-issue/`
4. Section 21 validators not implemented (~6 new validators needed)
5. Pilots 3, 5, 6, 7 missing
6. Unstaged modifications to `tools/review/no_stub_scan.py` and `tools/supervisor/governance_validators_ext4.py`
7. No issue-accounting.yaml
8. No taskcard status summary table (required by lifecycle_audit.py for --terminal --audit-gate)

---

## Forensic Findings Addressed (v1 → v2 healing)

| ID | Severity | Finding | Fix Applied |
|----|----------|---------|-------------|
| F-C1 | CRITICAL | Plan LOC caps for FI-010-013 wrong (642/604/508/479 vs actual 687/633/511/483) | TC-FIOP-004 redesigned as verification-first |
| F-C2 | CRITICAL | `test_no_loc_regression.py` does not exist | TC-FIOP-003 uses `tests/test_source_structure.py` |
| F-C3 | CRITICAL | Python LOC violations (FI-008) — baseline may show cap==loc for all | TC-FIOP-000 pre-flight verification added |
| F-H1 | HIGH | lifecycle_audit.py requires `| TC-ID | STATUS |` table to parse taskcards | Table added at bottom of plan |
| F-H2 | HIGH | Execution order contradiction — Pilot 6 listed after TC-FIOP-003 but "during" it | Pilot 6 embedded within TC-FIOP-003 |
| F-H3 | HIGH | Hardcoded FI-014/FI-015 may collide with TC-FIOP-001 discoveries | Changed to "next available FI-ID" |
| F-H4 | HIGH | "V168-V173" label doesn't exist — validators use string rule_ids | Replaced with canonical rule_id names |
| F-H5 | HIGH | `test_removal_analysis` key doesn't exist in declaration schema — blocking validator would break all sprints | Changed to WARN-only; schema extension noted |
| F-M1 | MEDIUM | Validator invocation missing sys.path — ImportError guaranteed | Added `cd tools/supervisor &&` prefix |
| F-M2 | MEDIUM | TC-FIOP-011 uses `supervisor_loop.py` (120s timeout) | Changed to `autonomous_cycle.py` |
| F-M3 | MEDIUM | No rollback strategy for LOC surgery | Rollback section added to TC-FIOP-003/TC-FIOP-004 |
| F-M4 | MEDIUM | Test count in context stated as 1169 — actual is 21558 | Context updated |
| F-L1 | LOW | TC-FIOP-009 accounting formula incomplete (missing sub-bucket decomposition) | Formula corrected |
| F-L2 | LOW | Pilot 5 misclassified as LOC violations (LOC violations = ALWAYS_REPRODUCIBLE, not flaky) | Context pilot mapping corrected |

---

## Taskcards

### TC-FIOP-000 — Pre-Flight Reality Verification [OPEN]
**Status:** OPEN
**Priority:** P0 — must run before any healing to avoid wasted work
**Prerequisites:** None
**Rollback:** None (read-only)

**Objective:** Verify which LOC violations actually exist right now before writing any healing code.

**Steps:**
1. Run V130 validator to get ground truth on .NET LOC:
   ```
   cd tools/supervisor && .venv/Scripts/python -c "
   import sys; sys.path.insert(0, '.')
   from governance_validators_found_issue import validate_dotnet_loc_cap_static
   r = validate_dotnet_loc_cap_static({})
   print('Result:', r['result'])
   for item in r['items']: print(' -', item)
   "
   ```
   From repo root (use `cd c:\Users\prora\OneDrive\Documents\GitHub\format-factory && cd tools/supervisor`).

2. Run the Python LOC regression check (actual test file):
   ```
   .venv/Scripts/pytest tests/test_source_structure.py -v --tb=short 2>&1 | tail -30
   ```

3. Record actual status for each FI issue:
   - For each FI-010 to FI-013: Does V130 flag it? YES → healing needed. NO → issue is stale.
   - For FI-008: Does `test_source_structure.py` fail for any of the 10 listed files? YES → healing needed. NO → issue is stale.

4. Update `registry/found-issue-register.yaml`:
   - If an issue is now clean (V130 PASS, no test failure): set `disposition: INVALID_FINDING_WITH_PROOF`, `status: closed`, document why in `verification_verdict`
   - If an issue still exists: keep `status: in_repair` or `taskcarded`, continue to TC-FIOP-003/TC-FIOP-004

**Completion criteria:** Every FI entry has a documented current-state assessment before any healing begins.

**Evidence:** Output of V130 run + `test_source_structure.py` run captured in `.local/evidences/fiop-full-001/tc-000-preflight.txt`

---

### TC-FIOP-001 — Investigate Unstaged Modified Files [OPEN]
**Status:** OPEN
**Priority:** P1 — governance tools with unstaged changes must be investigated
**Prerequisites:** None (can run in parallel with TC-FIOP-000)
**Rollback:** N/A (investigation only)

**Steps:**
1. Run (from repo root):
   ```
   git diff tools/review/no_stub_scan.py
   git diff tools/supervisor/governance_validators_ext4.py
   ```
2. For each changed hunk, classify:
   - Bug introduced → register as FI-(next-available) in `registry/found-issue-register.yaml`, taskcard it, then heal
   - Valid improvement uncommitted → stage and commit as part of this sprint's commit
   - Stale/accidental → revert: `git checkout tools/review/no_stub_scan.py`
3. If no defect found: write evidence note: `INVALID_FINDING_WITH_PROOF — changes are valid uncommitted improvements`
4. Register any discovered issues with `stable_semantic_key` before closing this taskcard

**Completion criteria:** Both files have a classified disposition. Any discovered issues are in the register.

**Evidence:** `git diff` output + classification decision in `.local/evidences/fiop-full-001/tc-001-unstaged.txt`

---

### TC-FIOP-002 — Create Missing Registers [OPEN]
**Status:** OPEN
**Priority:** P2 — required artifacts per Section 26
**Prerequisites:** TC-FIOP-000 (issue count needed for accuracy)
**Rollback:** Delete created files

**Create `registry/governed-exclusion-register.yaml`:**
```yaml
version: 1
policy_ref: docs/governance/found-issue-ownership-policy.md
exclusions: []
# Schema per entry:
#   exclusion_id: GE-NNN
#   issue_id: FI-NNN
#   authority: <who authorized>
#   rationale: <proof-backed reason, not "pre-existing">
#   evidence: []
#   affected_scope: <what is excluded>
#   risks: <known risks>
#   future_trigger: <condition that re-opens>
#   reviewer: <approver>
#   status: active | superseded
```

**Create `registry/negative-control-register.yaml`:**
```yaml
version: 1
policy_ref: docs/governance/found-issue-ownership-policy.md
negative_controls: []
# Schema per entry:
#   control_id: NC-NNN
#   issue_id: FI-NNN
#   control_type: restore_malformed_fixture|feed_invalid_input|simulate_stale_output|remove_provenance|recreate_incorrect_state|bypass_skill
#   description: <what is being proven>
#   command: <exact command>
#   expected_result: FAIL
#   actual_result: <filled after execution>
#   verdict: PASSES_NEGATIVE_CONTROL|FAILS_NEGATIVE_CONTROL
#   evidence: <path to output>
```

**Create `reports/found-issue/README.md`:**
```markdown
# Found-Issue Reports
Generated artifacts from FIOP-FULL-001 protocol execution.
Files in this directory are produced by TC-FIOP-009 and TC-FIOP-010.
```

**Verification:**
```
python -c "import yaml; yaml.safe_load(open('registry/governed-exclusion-register.yaml')); yaml.safe_load(open('registry/negative-control-register.yaml')); print('YAML valid')"
```

**Completion criteria:** 3 files exist and load as valid YAML.

---

### TC-FIOP-003 — Heal or Close FI-008: Python LOC Violations [OPEN]
**Status:** OPEN
**Priority:** P2
**Prerequisites:** TC-FIOP-000 must complete first (determines if healing needed)
**Rollback:** `git stash` before modifying any source file; `git stash pop` if tests fail

**Pre-condition:** If TC-FIOP-000 shows all FI-008 files are within cap → skip healing, proceed to "Close as INVALID" sub-step.

**If healing is required (some files actually exceed cap):**
1. `git stash` (create rollback point)
2. For each file still over cap:
   - Read the file fully
   - Identify dead code, over-documented functions, or eligible analytics separation
   - Apply §8.1 Analytics Separation Protocol (from `docs/code-quality/production-library-standard-v2.md`) if analytics extraction is appropriate
   - OR remove genuinely dead/redundant code
   - Do NOT blindly trim docstrings or comments — only remove non-functional code
3. Run verification (see below). If any test fails: `git stash pop` then investigate further.
4. Update FI-008 in `registry/found-issue-register.yaml`:
   - `status: verified`
   - `verification_verdict: "<test command> — N/N PASS"`
   - `disposition: HEALED_AND_VERIFIED`
   - `closed_at: <ISO8601>`

**If all FI-008 files are clean (TC-FIOP-000 shows no violations):**
- Close FI-008 as `INVALID_FINDING_WITH_PROOF`:
  - `status: closed`
  - `disposition: INVALID_FINDING_WITH_PROOF`
  - `verification_verdict: "V130 PASS + test_source_structure.py PASS — baseline caps match current LOC; issue was registered against stale cap values"`
  - `closed_at: <ISO8601>`

**Pilot 6 (unrelated issue discovery) — embedded here:**
While reading each file, immediately register any discovered incidental defect as FI-(next-available) in `found-issue-register.yaml` before closing this taskcard. This proves the protocol's "unrelated issue discovered during work" path.

**Verification:**
```
.venv/Scripts/pytest tests/test_source_structure.py -v --tb=short
```
Expected: 0 failures for any file in FI-008 list.

Also run no_stub_scan:
```
.venv/Scripts/python tools/review/no_stub_scan.py src/python/csv src/python/fods src/python/tsv
```
Expected: No forbidden stub markers introduced.

**Completion criteria:** FI-008 has disposition set (HEALED_AND_VERIFIED or INVALID_FINDING_WITH_PROOF); test_source_structure.py passes.

---

### TC-FIOP-004 — Verify and Close FI-010 to FI-013: .NET LOC Investigation [OPEN]
**Status:** OPEN
**Priority:** P3
**Prerequisites:** TC-FIOP-000 must complete first
**Rollback:** `git stash` before any code changes

**Root cause to investigate:** The found-issue-register.yaml states caps of 642/604/508/479 for these files. But `registry/source-structure-baseline.json` shows caps of 687/633/511/483 (equal to current LOC). This discrepancy means either:
- (A) The FI register was created with stale/incorrect cap values → issues never existed as real violations
- (B) The caps were improperly raised after issue creation (violating write-once policy) → this is itself a new issue

**Steps:**
1. Run V130 to get ground truth (see TC-FIOP-000 step 1 output)
2. For each file (FodsDocumentCellProps.cs, CsvDocumentAnalytics.cs, FodsDocumentDataAnnotations.cs, FodsDocumentSheetFeatures.cs):
   - Count actual LOC: `(Get-Content src/net/fods/FodsDocumentCellProps.cs).Count` (PowerShell) or `wc -l < path`
   - Compare to `baseline_loc_cap` in source-structure-baseline.json
3. **If actual LOC <= cap** (expected outcome per pre-flight):
   - This is scenario (A): issue was never real, or was already healed by decomposition work
   - Close as `INVALID_FINDING_WITH_PROOF` with explanation of baseline discrepancy
   - Register discrepancy as a systemic finding: "FI register was created with incorrect cap values; actual caps at file creation time were cap==loc, not 642/604/508/479"
4. **If actual LOC > cap** (healing needed):
   - `git stash` as rollback
   - Reduce LOC in each file (remove dead code, extract partial class)
   - Re-run V130 to confirm PASS
   - Close as `HEALED_AND_VERIFIED`

**Verification (run after disposition decision):**
```
cd tools/supervisor && .venv/Scripts/python -c "
import sys; sys.path.insert(0, '.')
from governance_validators_found_issue import validate_dotnet_loc_cap_static
r = validate_dotnet_loc_cap_static({})
print('V130 result:', r['result'])
fi_files = ['src/net/fods/FodsDocumentCellProps.cs', 'src/net/csv/CsvDocumentAnalytics.cs',
            'src/net/fods/FodsDocumentDataAnnotations.cs', 'src/net/fods/FodsDocumentSheetFeatures.cs']
remaining = [i for i in r['items'] if any(f in str(i) for f in fi_files)]
print('FI-010-013 violations remaining:', len(remaining))
"
```
Expected: 0 violations for these 4 files.

**Completion criteria:** FI-010 to FI-013 all have `disposition` set; V130 returns PASS for these files.

---

### TC-FIOP-005 — Add Section-21 Validators [OPEN]
**Status:** OPEN
**Priority:** P1 — protocol requires enforcement validators
**Prerequisites:** TC-FIOP-001 (confirm no blocking issues in governance_validators_found_issue.py)
**Rollback:** `git checkout tools/supervisor/governance_validators_found_issue.py` if tests fail

**Pre-check before adding:** Verify governance_validators_found_issue.py LOC will stay under 800:
```
wc -l tools/supervisor/governance_validators_found_issue.py
```
If > 700 lines currently, create `governance_validators_found_issue_ext.py` instead.

**Add 6 new validators to `tools/supervisor/governance_validators_found_issue.py`** (or _ext.py if LOC concern):

**1. `validate_found_issue_task_closure_unaccounted` (rule_id: V_VALIDATE_FI_TASK_CLOSURE_UNACCOUNTED)**
- blocks_sprint=True
- Check: declaration `found_issues` list has entries without `disposition` AND declaration declares some task as complete
- Logic: `[fi for fi in declaration.get('found_issues', []) if not fi.get('disposition')]`
- FAIL if any undisposed issues AND `worker_self_grade in ('PASS', 'PARTIAL')`

**2. `validate_found_issue_no_deleted_test_without_analysis` (rule_id: V_VALIDATE_FI_NO_DELETED_TEST)**
- blocks_sprint=False (WARN — `test_removal_analysis` is a new optional field; blocking would break existing sprints)
- Scan `changed_files` list for paths matching `**/test_*.py` or `**/tests/**` that were removed
- If found and declaration has no `test_removal_analysis` key → WARN (not FAIL)
- Rationale: schema field doesn't exist yet; WARN educates without blocking

**3. `validate_found_issue_downstream_patch_while_upstream_defective` (rule_id: V_VALIDATE_FI_DOWNSTREAM_PATCH)**
- blocks_sprint=False (WARN — advisory)
- Check: `rework_items` has any GOV_BLOCK item AND ALL `changed_files` paths start with `reports/` or `registry/` (no `src/` or `tools/` changes)
- WARN: "Evidence suggests downstream-only changes while upstream GOV_BLOCK remains unresolved"

**4. `validate_found_issue_closure_without_verification` (rule_id: V_VALIDATE_FI_CLOSURE_NO_VERIFY)**
- blocks_sprint=True
- Load `registry/found-issue-register.yaml`
- For each issue with `disposition: HEALED_AND_VERIFIED` or `status: closed`: require non-null `verification_verdict`
- FAIL if closed issue has null/empty `verification_verdict`

**5. `validate_found_issue_untaskcarded_in_final_report` (rule_id: V_VALIDATE_FI_UNTASKCARDED_REPORT)**
- blocks_sprint=False (WARN — false positive risk is high with simple keyword matching)
- Scan `worker_self_verdict` for issue-reporting phrases ("failed", "broken", "error in", "cannot") NOT preceded by "no " or "all "
- Cross-reference: if found, check that declaration.found_issues is non-empty
- WARN if issue-language found without any found_issues entries

**6. `validate_found_issue_no_fixture_edit_without_authority` (rule_id: V_VALIDATE_FI_FIXTURE_EDIT)**
- blocks_sprint=False (WARN — advisory)
- Scan `changed_files` for paths matching `tests/**/*.yaml`, `tests/**/*.json`, `tests/**/fixtures/**`
- If fixture path found AND declaration.found_issues is empty AND declaration does not contain `fixture_authority_ref` → WARN
- Purpose: surface silent fixture edits

**After adding validators:**
1. Update `governance_validator_runner.py` line ~813: `"expected_count": 167` → `"expected_count": 173`
2. Add 6 test methods to `tests/supervisor/test_found_issue_ownership.py`, one per validator
3. Update `.supervisor/skill-registry.yaml` `mandatory_validations` for `found-issue-ownership` skill to include the 6 new rule_ids

**Verification:**
```
.venv/Scripts/pytest tests/supervisor/test_found_issue_ownership.py -v --tb=short
.venv/Scripts/pytest tests/supervisor/test_v130_v133_found_issue.py -v --tb=short
```
Expected: All tests PASS.

Full count verification:
```
cd tools/supervisor && .venv/Scripts/python governance_validator_runner.py 2>&1 | grep -E "expected|ran_count"
```
Expected: `ran_count >= 173`, no count assertion failure.

**Completion criteria:** 6 validators added with passing tests; expected_count updated to 173; count assertion passes.

---

### TC-FIOP-006 — Execute Pilot 3: Test With Invalid Expectation [OPEN]
**Status:** OPEN
**Priority:** P2 — required pilot per Section 23
**Prerequisites:** TC-FIOP-001 complete (ensures governance tools are clean)
**Rollback:** `git checkout` any modified test file if fix is incorrect

**Objective:** Demonstrate a test with an invalid expectation; correct it from authoritative behavior (not from implementation).

**Steps:**
1. Search for candidates — tests that check hardcoded numeric counts that may have drifted:
   ```
   grep -n "assert.*== [0-9]" tests/supervisor/test_governance_validators.py | head -20
   grep -n "assert.*count.*==" tests/supervisor/ -r | head -10
   ```
2. Select a test whose expected value is not derived from an authoritative spec/contract — verify that the assertion is wrong (not just that the value drifted)
3. Document authority (spec, schema, contract) that provides the correct value
4. Fix the test using the authoritative value, NOT the implementation output
5. Register as FI-(next-available) in `found-issue-register.yaml`:
   - `stable_semantic_key: "test_expectation:invalid:pilot_3:<test_file>:<test_name>"`
   - `issue_type: incorrect_implementation` (wrong expectation = implementation defect in test)
   - Root cause: `RC-FIO-004` — test expectation not derived from authoritative source
6. Run the corrected test: `.venv/Scripts/pytest <test_file>::<test_name> -v`
7. Add negative control to `registry/negative-control-register.yaml`:
   - `control_type: feed_invalid_input`
   - `command`: Run with old wrong assertion in an in-memory mock → verify FAIL
   - `expected_result: FAIL`

**Completion criteria:** FI-(next-available) registered and closed as HEALED_AND_VERIFIED; NC-001 added to negative-control-register; test passes.

---

### TC-FIOP-007 — Execute Pilot 7: Invalid "Pre-existing" Dismissal Rejection [OPEN]
**Status:** OPEN
**Priority:** P2 — required pilot per Section 23
**Prerequisites:** TC-FIOP-005 (validators must be present and tested)
**Rollback:** N/A (read-only validator tests)

**Objective:** Simulate an agent attempting to dismiss a failure as "pre-existing" → verify policy blocks it.

**Steps:**
1. Test V142 (ownership disposition validator) with an invalid disposition:
   ```
   cd tools/supervisor && .venv/Scripts/python -c "
   import sys; sys.path.insert(0, '.')
   import tempfile, os, yaml
   from pathlib import Path
   from governance_validators_found_issue import validate_invalid_ownership_disposition
   # Create a temp register with invalid disposition
   tmp = Path(tempfile.mkdtemp()) / 'found-issue-register.yaml'
   tmp.write_text(yaml.dump({'issues': [{'issue_id': 'FI-TEST', 'status': 'closed', 'disposition': 'pre-existing'}]}))
   r = validate_invalid_ownership_disposition({}, repo_root=tmp.parent.parent)
   print('Result:', r['result'])
   print('blocks_sprint:', r['blocks_sprint'])
   print('Items:', r['items'])
   assert r['result'] == 'FAIL', 'V142 must FAIL for invalid disposition'
   assert r['blocks_sprint'] == True, 'V142 must block sprint'
   print('PILOT 7 PASS: V142 correctly rejects pre-existing disposition')
   "
   ```
   Note: Uses a temp directory as repo_root so no actual register is modified.

2. Test V141 (prose dismissal detector):
   ```
   cd tools/supervisor && .venv/Scripts/python -c "
   import sys; sys.path.insert(0, '.')
   from governance_validators_found_issue import validate_no_prose_only_findings
   r = validate_no_prose_only_findings({'worker_self_verdict': 'this is a pre-existing issue, skip it'})
   print('Result:', r['result'])
   assert r['result'] == 'WARN', 'V141 must WARN for prose dismissal'
   print('PILOT 7 PASS: V141 correctly detects prose dismissal')
   "
   ```

3. Capture output to `.local/evidences/fiop-full-001/tc-007-pilot7.txt`
4. Document in `reports/found-issue/pilot-evidence.md` (written in TC-FIOP-010)

**Completion criteria:** Both validators produce expected results; output captured.

---

### TC-FIOP-008 — Execute Pilot 5: Flaky Failure [OPEN]
**Status:** OPEN
**Priority:** P2 — required pilot (not LOC violations — was misclassified in v1)
**Prerequisites:** Full test suite must be accessible
**Rollback:** N/A (investigation pilot)

**Objective:** Demonstrate that intermittent/environment-specific failures are captured and governed.

**Search for flaky candidates:**
1. Check `registry/flaky-test-ledger.yaml` for any registered flaky tests
2. Run the governance validator runner 3 times and compare outputs for any non-deterministic results:
   ```
   cd tools/supervisor && .venv/Scripts/python governance_validator_runner.py > /tmp/run1.json 2>&1
   cd tools/supervisor && .venv/Scripts/python governance_validator_runner.py > /tmp/run2.json 2>&1
   diff /tmp/run1.json /tmp/run2.json
   ```
3. If a flaky test is found: register as FI-(next-available), classify `reproducibility: INTERMITTENT`, document environment conditions
4. If no flaky tests found after 3 runs: register a GOVERNED_EXCLUSION noting "no flaky behavior observed; pilot demonstrated via stability proof"

**Completion criteria:** Pilot 5 documented with either a real flaky issue captured or stability proof recorded.

---

### TC-FIOP-009 — Write Issue Accounting Report [OPEN]
**Status:** OPEN
**Priority:** P1 — required for protocol closure
**Prerequisites:** All healing taskcards (TC-FIOP-003, TC-FIOP-004, TC-FIOP-006) must be complete

**Create `registry/issue-accounting.yaml`:**
```yaml
version: 1
mission_id: FIOP-FULL-001
accounting_date: <ISO8601>
# REQUIRED EQUALITY:
# total_discovered = healed_and_verified + active + duplicate + invalid_with_proof
#                    + governed_exclusion + blocked_true_external + waiting_gate_11
# active = under_investigation + healing + verification_pending
total_discovered: <N>
active: 0         # must be 0 at mission close
under_investigation: 0
healing: 0
verification_pending: 0
healed_and_verified: <count>
duplicate: 0
invalid_with_proof: <count>
governed_exclusion: 0
blocked_true_external: 0
waiting_gate_11: 0
unaccounted: 0    # MUST be 0
counts_reconcile: true
issues:
  - issue_id: FI-001
    bucket: healed_and_verified
    register_status: verified
  - issue_id: FI-002
    bucket: healed_and_verified
    register_status: verified
  - issue_id: FI-003
    bucket: healed_and_verified
    register_status: verified
  - issue_id: FI-004
    bucket: healed_and_verified
    register_status: verified
  - issue_id: FI-008
    bucket: <healed_and_verified OR invalid_with_proof — set after TC-FIOP-003>
    register_status: <from TC-FIOP-003 outcome>
  - issue_id: FI-010
    bucket: <healed_and_verified OR invalid_with_proof — set after TC-FIOP-004>
    register_status: <from TC-FIOP-004 outcome>
  - issue_id: FI-011
    bucket: <from TC-FIOP-004>
    register_status: <from TC-FIOP-004>
  - issue_id: FI-012
    bucket: <from TC-FIOP-004>
    register_status: <from TC-FIOP-004>
  - issue_id: FI-013
    bucket: <from TC-FIOP-004>
    register_status: <from TC-FIOP-004>
  # Add FI-(next-available) for all issues discovered during execution
```

**Also create `reports/found-issue/issue-accounting-report.md`** — human-readable version.

**Verification:**
```python
# Verify equality holds:
import yaml
d = yaml.safe_load(open('registry/issue-accounting.yaml'))
computed_total = (d['healed_and_verified'] + d['active'] + d['duplicate'] +
                  d['invalid_with_proof'] + d['governed_exclusion'] +
                  d['blocked_true_external'] + d['waiting_gate_11'])
assert computed_total == d['total_discovered'], f"{computed_total} != {d['total_discovered']}"
assert d['unaccounted'] == 0
assert len(d['issues']) == d['total_discovered']
print('ACCOUNTING RECONCILES')
```

**Completion criteria:** YAML loads, equality holds, unaccounted=0, entry count matches total.

---

### TC-FIOP-010 — Write Reports: Pilot Evidence, Regression, Enforcement, Idempotency [OPEN]
**Status:** OPEN
**Priority:** P2 — required for Section 26 compliance
**Prerequisites:** TC-FIOP-006, TC-FIOP-007, TC-FIOP-008, TC-FIOP-009 all complete

**Create `reports/found-issue/pilot-evidence.md`:**
Document all 7 pilots with actual command outputs captured:
- Pilot 1: FI-008 — LOC regression investigation (outcome from TC-FIOP-003)
- Pilot 2: FI-001 to FI-004 — broken fixtures (from FOUND-ISSUE-MVP-001, already HEALED)
- Pilot 3: FI-(ID from TC-FIOP-006) — test with wrong expectation (outcome from TC-FIOP-006)
- Pilot 4: RC-FIO-001 — shared fixture generator (from FOUND-ISSUE-MVP-001, already complete)
- Pilot 5: Flaky failure investigation (outcome from TC-FIOP-008)
- Pilot 6: Unrelated issue during work (discovered in TC-FIOP-003)
- Pilot 7: V142/V141 blocking invalid dismissal (from TC-FIOP-007)

**Create `reports/found-issue/regression-report.md`:**
List tests that now pass which previously failed (if any healing was performed).
If all issues closed as INVALID_FINDING_WITH_PROOF: note "no regressions introduced; all baseline tests maintained."
Commands:
```
.venv/Scripts/pytest --tb=short 2>&1 | tail -5
```
Before/after comparison.

**Create `reports/found-issue/prompt-skill-enforcement-report.md`:**
- Confirm `/found-issue-ownership` skill: active, command file path, mandatory_validations list
- Confirm V130-V142 run on every declaration (show validator runner expected_count=173)
- Confirm the 6 new validators from TC-FIOP-005 are registered and passing
- Command: `cd tools/supervisor && .venv/Scripts/python governance_validator_runner.py 2>&1 | grep -c PASS`

**Create `reports/found-issue/idempotency-verdict.md`:**
Prove no spurious state changes on rerun:
1. Run governance validator runner twice, compare:
   ```
   cd tools/supervisor && .venv/Scripts/python governance_validator_runner.py > /tmp/r1.txt 2>&1
   cd tools/supervisor && .venv/Scripts/python governance_validator_runner.py > /tmp/r2.txt 2>&1
   diff /tmp/r1.txt /tmp/r2.txt && echo "IDEMPOTENT" || echo "NOT_IDEMPOTENT"
   ```
2. Verify found-issue-register.yaml is not modified by repeated validator runs
3. **Verdict:** `STABLE_NO_CHANGE_PROOF` (identical outputs) or `IDEMPOTENCY_ISSUE_FOUND` (with details)

**Completion criteria:** All 4 report files exist and contain actual evidence from execution.

---

### TC-FIOP-011 — Sprint Closeout [OPEN]
**Status:** OPEN
**Priority:** P1 — must close mission
**Prerequisites:** ALL other taskcards complete; all FI entries have dispositions; unaccounted=0

**⚠ Pre-step — Plan Migration (MANDATORY per CLAUDE.md Step 0 + MEMORY.md):**
This plan was created externally at `~/.claude/plans/optimized-meandering-giraffe.md`.
Before writing the terminal lock, ensure it has been migrated to the repo:
```
cp "C:/Users/prora/.claude/plans/optimized-meandering-giraffe.md" plans/.claude/optimized-meandering-giraffe.md
.venv/Scripts/python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/optimized-meandering-giraffe.md
```
ALL subsequent lock writes use `plans/.claude/optimized-meandering-giraffe.md` — NOT the external path.

**Steps:**
1. Write evidence declaration:
   ```
   mkdir -p .local/evidences/fiop-full-001
   # Write .local/evidences/fiop-full-001/evidence-declaration.yaml
   ```
   Include: `run_id: fiop-full-001`, all work items, all evidence paths, `found_issues` list

2. Validate declaration:
   ```
   .venv/Scripts/python tools/supervisor/sprint_executor_validate.py .local/evidences/fiop-full-001/evidence-declaration.yaml --repair
   ```

3. Run supervisor pipeline (NOT supervisor_loop.py — 120s timeout):
   ```
   .venv/Scripts/python tools/supervisor/autonomous_cycle.py --declaration .local/evidences/fiop-full-001/evidence-declaration.yaml
   ```

4. Commit all changes (specific files only — no `git add .`):
   ```
   git add registry/governed-exclusion-register.yaml \
           registry/negative-control-register.yaml \
           registry/found-issue-register.yaml \
           registry/issue-accounting.yaml \
           tools/supervisor/governance_validators_found_issue.py \
           tools/supervisor/governance_validator_runner.py \
           tests/supervisor/test_found_issue_ownership.py \
           reports/found-issue/ \
           .supervisor/skill-registry.yaml
   # Add any modified .cs or .py source files if healing was performed
   git commit -m "feat(fiop-full-001): found-issue protocol gap-fill, healing, and verification

   - Add V_VALIDATE_FI_* validators (6 new, expected_count 167→173)
   - Create governed-exclusion-register.yaml and negative-control-register.yaml
   - Close FI-008, FI-010-013 with verified dispositions
   - Complete pilots 3, 5, 6, 7
   - Write issue-accounting.yaml (unaccounted=0)
   - Write pilot-evidence.md, regression-report.md, enforcement-report.md, idempotency-verdict.md

   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
   ```

5. Build review package:
   ```
   .venv/Scripts/python tools/supervisor/build_declaration_review_package.py --declaration .local/evidences/fiop-full-001/evidence-declaration.yaml
   ```
   Print absolute path and SHA-256.

6. Run lifecycle audit:
   ```
   .venv/Scripts/python tools/supervisor/lifecycle_audit.py --mission-id FIOP-FULL-001 --sprint-id TC-FIOP-011
   ```

7. Write terminal lock:
   ```
   .venv/Scripts/python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/optimized-meandering-giraffe.md --terminal --audit-gate
   ```

**Completion criteria:** Terminal lock written as TERMINAL_CLOSED; review package built; commit recorded.

---

## Execution Order (Corrected)

```
Step 0:  TC-FIOP-000 + TC-FIOP-001  (PARALLEL — both read-only investigations)
         ↓ Gate: TC-FIOP-000 output determines if healing needed for FI-008/010-013
Step 1:  TC-FIOP-002  (create missing registers — can start after TC-FIOP-000)
Step 2:  TC-FIOP-003  (heal or close FI-008; Pilot 6 embedded)
         TC-FIOP-004  (verify/close FI-010-013 — can PARALLEL with TC-FIOP-003)
Step 3:  TC-FIOP-005  (add 6 validators — must come after source files are stable)
Step 4:  TC-FIOP-006  (pilot 3 — test expectation)
         TC-FIOP-007  (pilot 7 — dismissal rejection; needs validators from TC-FIOP-005)
         TC-FIOP-008  (pilot 5 — flaky; independent)
Step 5:  TC-FIOP-009  (issue accounting — all prior issues must be disposed)
Step 6:  TC-FIOP-010  (all 4 reports — requires accounting data)
Step 7:  TC-FIOP-011  (sprint closeout + terminal lock)
```

---

## Critical Files

### Read (pre-flight):
- [registry/source-structure-baseline.json](registry/source-structure-baseline.json) — LOC caps (ground truth)
- [registry/found-issue-register.yaml](registry/found-issue-register.yaml) — 9 entries, 5 unresolved
- [tools/supervisor/governance_validators_found_issue.py](tools/supervisor/governance_validators_found_issue.py) — extend with 6 validators (currently 437 LOC)
- [tools/supervisor/governance_validator_runner.py](tools/supervisor/governance_validator_runner.py) — line 813: expected_count=167 → update to 173
- [tests/supervisor/test_found_issue_ownership.py](tests/supervisor/test_found_issue_ownership.py) — add 6 new validator tests
- [tests/test_source_structure.py](tests/test_source_structure.py) — LOC regression test (actual test, not test_no_loc_regression.py)
- [docs/governance/found-issue-ownership-policy.md](docs/governance/found-issue-ownership-policy.md) — authority

### Create:
- `registry/governed-exclusion-register.yaml`
- `registry/negative-control-register.yaml`
- `registry/issue-accounting.yaml`
- `reports/found-issue/README.md`
- `reports/found-issue/pilot-evidence.md`
- `reports/found-issue/issue-accounting-report.md`
- `reports/found-issue/regression-report.md`
- `reports/found-issue/prompt-skill-enforcement-report.md`
- `reports/found-issue/idempotency-verdict.md`

### Modify:
- `tools/supervisor/governance_validators_found_issue.py` — add 6 validators
- `tools/supervisor/governance_validator_runner.py` — update expected_count 167→173
- `registry/found-issue-register.yaml` — close FI-008, FI-010-013; add pilot issue entries
- `.supervisor/skill-registry.yaml` — add new rule_ids to mandatory_validations

---

## Verification Suite

### Pre-flight (TC-FIOP-000):
```
cd tools/supervisor && .venv/Scripts/python -c "import sys; sys.path.insert(0,'.');from governance_validators_found_issue import validate_dotnet_loc_cap_static; r=validate_dotnet_loc_cap_static({}); print(r['result'], len(r['items']), 'items')"
.venv/Scripts/pytest tests/test_source_structure.py -v --tb=short 2>&1 | tail -15
```

### After TC-FIOP-005 (new validators):
```
.venv/Scripts/pytest tests/supervisor/test_found_issue_ownership.py -v --tb=short
cd tools/supervisor && .venv/Scripts/python governance_validator_runner.py 2>&1 | grep expected_count
```
Expected: expected_count assertion passes at 173.

### After TC-FIOP-009 (accounting):
```
.venv/Scripts/python -c "
import yaml
d = yaml.safe_load(open('registry/issue-accounting.yaml'))
total = d['healed_and_verified'] + d['active'] + d['duplicate'] + d['invalid_with_proof'] + d['governed_exclusion'] + d['blocked_true_external'] + d['waiting_gate_11']
assert total == d['total_discovered'] and d['unaccounted'] == 0 and len(d['issues']) == d['total_discovered']
print('ACCOUNTING OK')
"
```

### Full test suite (before commit):
```
.venv/Scripts/pytest -x --tb=short 2>&1 | tail -5
```
Expected: ≥21558 passed, 0 failed (regression baseline from next-sprint.md).

---

## Rollback Strategy

| Taskcard | Risk | Rollback |
|----------|------|----------|
| TC-FIOP-003 | Source code changes | `git stash` before; `git stash pop` if tests fail |
| TC-FIOP-004 | Source code changes | `git stash` before; `git stash pop` if V130 fails |
| TC-FIOP-005 | Validator additions | `git checkout tools/supervisor/governance_validators_found_issue.py` if tests fail |
| TC-FIOP-002 | Register creation | Delete new YAML files |
| TC-FIOP-011 | Commit | `git reset HEAD~1 --soft` if pre-commit hook fails; fix and recommit |

---

## Governance Controls

| Control | Enforcement |
|---------|-------------|
| No issue without FI-ID | V139 (test failures) + V140 (accounting) |
| No "pre-existing" dismissal | V142 (blocks sprint) |
| No prose dismissal | V141 (WARN) |
| No task closure with undisposed issues | V_VALIDATE_FI_TASK_CLOSURE_UNACCOUNTED (blocks sprint) |
| No fixture edit without authority | V_VALIDATE_FI_FIXTURE_EDIT (WARN) |
| No issue closed without verification | V_VALIDATE_FI_CLOSURE_NO_VERIFY (blocks sprint) |
| Accounting must reconcile | V140 + TC-FIOP-009 verification script |

---

## Taskcard Status Summary Table
*(Required for lifecycle_audit.py `parse_plan_taskcards()` — must use exactly this format)*

| TC-ID | STATUS |
|-------|--------|
| TC-FIOP-000 | CLOSED |
| TC-FIOP-001 | CLOSED |
| TC-FIOP-002 | CLOSED |
| TC-FIOP-003 | CLOSED |
| TC-FIOP-004 | CLOSED |
| TC-FIOP-005 | CLOSED |
| TC-FIOP-006 | CLOSED |
| TC-FIOP-007 | CLOSED |
| TC-FIOP-008 | CLOSED |
| TC-FIOP-009 | CLOSED |
| TC-FIOP-010 | CLOSED |
| TC-FIOP-011 | CLOSED |

---

## Issue Accounting Target (end state)

| Bucket | Target | Notes |
|--------|--------|-------|
| healed_and_verified | ≥4 (FI-001 to FI-004 guaranteed) | +FI-008, FI-010-013 if healing needed; +pilots |
| invalid_with_proof | 0 or more | FI-008/FI-010-013 may close here if V130 shows no violation |
| active | 0 | Required at mission close |
| duplicate | 0 | |
| governed_exclusion | 0 or 1 | Pilot 5 may close as governed exclusion |
| blocked_true_external | 0 | |
| waiting_gate_11 | 0 | |
| **unaccounted** | **0** | Hard requirement — mission cannot close if > 0 |
| counts_reconcile | true | Script verified |

## Final Verdict Target
`ALL_DISCOVERED_ISSUES_OWNED_HEALED_AND_VERIFIED`


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-12T17:59:09.851351+00:00"
  locked_by: "93a9fa0ddc5b"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->

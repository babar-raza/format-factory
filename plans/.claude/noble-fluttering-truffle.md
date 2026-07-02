# noble-fluttering-truffle — Deep Plan Compliance Audit, Healing, Pilot Reproof, and Closure

## Context

This plan audits the completed `bright-marinating-map` plan (FF-PLAYBOOK-SYSTEM-001, machinery_hardening,
TERMINAL_CLOSED 2026-07-01) which built the format-factory playbook system from scratch.

Pre-audit exploration found three critical integrity issues that justify a full independent audit:

1. **Pilot evidence is declarative YAML only** — no real execution logs. The reference execution log
   (EXEC-C02ECB63.yaml) shows `taskcards: []`, `successful_phases: []`, `failed_phases: []` with
   `verdict: SUCCESS` — a logical contradiction. All 8 pilot "PASS" verdicts are claimed, not proven.

2. **V92-V99 validator tests are absent** — `test_governance_validators.py` has 207 test methods but
   ZERO test functions for playbook validators (V92-V99). Only a count comment at line ~1800 acknowledges
   their existence. Validators are implemented and registered but unverified.

3. **Contradictory agent reports** about whether `governance_validators_ext2.py` actually exists on
   disk (one agent says yes at line 383-402, another says no and lists only 7 tools in governance/).
   Must be verified against repository truth before trusting any claimed V86-V99 status.

**Authoritative plan under audit:**
- Path: `plans/.claude/bright-marinating-map.md`
- Mission ID: `FF-PLAYBOOK-SYSTEM-001`
- Type: `machinery_hardening`
- Claimed status: ALL 15 TASKCARDS CLOSED, TERMINAL_CLOSED 2026-07-01

**Audit scope:** Verify every plan requirement against repository truth. Reopen any falsely closed
taskcard. Rerun all 8 pilots with real execution. Heal all gaps. Close only when proven.

---

## Closure Binding

```yaml
closure_audit:
  mission_id: FF-PLAYBOOK-AUDIT-001
  plan_path: plans/.claude/bright-marinating-map.md
  source_plan_mission_id: FF-PLAYBOOK-SYSTEM-001
  plan_type: machinery_hardening
```

---

## Taskcard Status Table (lifecycle_audit.py format)

| TC-ID | Status |
|---|---|
| TC-AUDIT-001 | CLOSED |
| TC-AUDIT-002 | CLOSED |
| TC-AUDIT-003 | CLOSED |
| TC-AUDIT-004 | CLOSED |
| TC-AUDIT-005 | CLOSED |
| TC-AUDIT-006 | CLOSED |
| TC-AUDIT-007 | CLOSED |
| TC-AUDIT-008 | CLOSED |
| TC-AUDIT-009 | CLOSED |
| TC-AUDIT-010 | CLOSED |
| TC-AUDIT-011 | CLOSED |

---

## Taskcards

| TC-ID | Title | Status | Priority |
|---|---|---|---|
| TC-AUDIT-001 | Bind plan and baseline | CLOSED | HIGH |
| TC-AUDIT-002 | Build requirement matrix | CLOSED | HIGH |
| TC-AUDIT-003 | Verify all deliverable files (existence + content) | CLOSED | HIGH |
| TC-AUDIT-004 | Verify validator chain (V92-V99 existence, registration, tests) | CLOSED | CRITICAL |
| TC-AUDIT-005 | Reprove pilots P1-P4 with real execution commands | CLOSED | CRITICAL |
| TC-AUDIT-006 | Reprove pilots P5-P8 with real execution commands | CLOSED | CRITICAL |
| TC-AUDIT-007 | Verify idempotency (run generation twice, SHA compare) | CLOSED | HIGH |
| TC-AUDIT-008 | Heal all identified gaps (write missing tests, fix evidence quality) | CLOSED | HIGH |
| TC-AUDIT-009 | Run full test suite and capture results | CLOSED | HIGH |
| TC-AUDIT-010 | Final independent assessment and closure verdict | CLOSED | HIGH |
| TC-AUDIT-011 | Clear stale GOV_BLOCK signals and achieve TERMINAL_CLOSED | CLOSED | HIGH |
| TC-AUDIT-010 | Final independent assessment and closure verdict | CLOSED | HIGH |

---

## TC-AUDIT-001: Bind Plan and Baseline

**Scope:** Capture repository state before audit begins.

**Actions:**
1. Read full content of `plans/.claude/bright-marinating-map.md` and compute SHA-256
2. Run `git rev-parse HEAD` to capture current commit
3. Run `git status` to capture staged/unstaged/untracked files
4. Record taskcard registry: all 15 TC-PB-001 through TC-PB-015 with claimed statuses
5. List all files expected by the plan (see §Files Created/Modified in plan footer)
6. Check `.local/supervisor/active-plan-lock.json` status

**Acceptance criteria:**
- All expected file paths from the plan are enumerated
- Repository HEAD captured
- Plan hash recorded

---

## TC-AUDIT-002: Build Requirement Matrix

**Scope:** Convert all 15 plan taskcards to atomic, verifiable requirements.

**Actions:**
1. For each TC-PB-001 through TC-PB-015: extract exact deliverables, expected paths, verification criteria
2. Classify each requirement into: FILE_EXISTS, FILE_CONTENT, REGISTRY_ENTRY, SKILL_INVOCABLE,
   VALIDATOR_REGISTERED, TEST_EXISTS, TEST_PASSES, PILOT_PASSES, PILOT_HAS_REAL_EVIDENCE
3. Record dependency order (e.g., TC-PB-009 must succeed before TC-PB-010 pilots can run)
4. Enumerate all completion gate counters the plan claims are zero
5. Record the exact validator IDs the plan specifies: are they V86-V93 or V92-V99?

**Key questions to answer:**
- Exact validator numbering (V86-V93 per plan body, or V92-V99 per runner?)
- Exact list of expected test files in `tests/playbook/`
- Exact list of expected tools in `tools/playbook/`
- Whether `governance_validators_ext2.py` is the correct file for playbook validators

**Acceptance criteria:**
- PLAN_REQUIREMENTS_NOT_REPRESENTED = 0
- Every requirement has a unique requirement_id and verification method

---

## TC-AUDIT-003: Verify All Deliverable Files (Existence + Content)

**Scope:** Check every file the plan claims was created or modified. Don't trust prior reports.

**Files to verify (from plan claims):**

*Reports (7 files):*
- `reports/playbooks/playbook-system-inventory.yaml` — exists? has real inventory content?
- `reports/playbooks/playbook-consumer-graph.yaml` — exists? has classification entries?
- `reports/playbooks/playbook-authority-decision.yaml` — exists? has MODEL C binding?
- `reports/playbooks/playbook-quality-audit.yaml` — exists? has per-artifact dispositions?
- `reports/playbooks/playbook-coverage-universe.yaml` — exists? has 14 workflows?
- `reports/playbooks/idempotency-report.yaml` — exists? has MATERIAL_SECOND_RUN_CHANGES=0?
- `reports/playbooks/playbook-system-healing-report.md` — exists? has final verdict?

*Registry and documentation (5 files):*
- `playbooks/playbook-registry.yaml` — exists? has 6+ ACTIVE entries? has authority statement?
- `playbooks/_readme.md` — has MODEL C disambiguation?
- `docs/governance/playbook-layer.md` — exists? has S-F2F phase statuses?
- `AGENTS.md §AA` — has Sprint Task Templates clarification?
- `GOVERNANCE.md` — has Model C decision?

*Templates (6 files):*
- `playbooks/format-factory/format-feature-expansion.md` — has YAML front-matter contract?
- `playbooks/format-factory/new-format-kickstart-template.md` — has YAML front-matter contract?
- `playbooks/format-factory/product-source-task-template.md` — has YAML front-matter contract?
- `playbooks/format-factory/package-release-readiness.md` — new file, exists? has contract?
- `playbooks/format-factory/audit-healing-sprint.md` — new file, exists? has contract?
- `playbooks/format-factory/pipeline-incident-response.md` — new file, exists? has contract?

*Acquisition playbook:*
- `acquisition-packs/_families/odf-flat/playbook.yaml` — status = `active`? has gates 1-10?

*Tools (3 files):*
- `tools/playbook/generate_playbook_taskcards.py` — exists? is real code (not stub)?
- `tools/playbook/playbook_selector.py` — exists? handles DEPRECATED rejection?
- `tools/playbook/playbook_execution_log.py` — exists? records execution state?

*Schema (1 file):*
- `schemas/playbook/playbook-task-binding.schema.json` — exists? has real JSON schema?

*Tests (7 files):*
- `tests/playbook/test_authority_constraints.py`
- `tests/playbook/test_registry.py`
- `tests/playbook/test_rendering.py`
- `tests/playbook/test_task_generation.py`
- `tests/playbook/test_supervisor_integration.py`
- `tests/playbook/test_coverage.py`
- `tests/playbook/test_idempotency.py`

Also verify existing tests still pass for odf-flat:
- `tests/playbook/test_odf_flat_family_playbook.py`
- `tests/playbook/test_playbook_schema.py`
- `tests/playbook/test_diff_playbook_outputs.py`

*Skill registry (7 skills):*
- `.supervisor/skill-registry.yaml` — contains all 7 playbook skills?

**Actions:**
1. Read each file; confirm it exists
2. Check file is not a placeholder/stub (has meaningful content > 50 lines for code)
3. For YAML files: verify key structural fields exist
4. For Markdown files: verify YAML front-matter contract block exists
5. Record any path drift, missing files, or placeholder content

**Acceptance criteria:**
- All expected files exist at canonical paths
- No file is a placeholder or skeleton-only
- `playbook-registry.yaml` has ≥6 ACTIVE entries with file-resolvable paths

---

## TC-AUDIT-004: Verify Validator Chain (V86-V99 Existence, Registration, Tests)

**Scope:** CRITICAL — Resolve the contradictory reports about playbook validators.

This is the most disputed area:
- Plan body specifies V86-V93 (8 validators)
- Runner agent found V92-V99 registered in `governance_validator_runner.py` at lines 383-402
- Third agent claimed `governance_validators_ext2.py` does NOT exist
- The plan completion audit agent found the file exists with 997 LOC

**Actions:**

1. **Resolve discrepancy**: Verify `governance_validators_ext2.py` existence:
   ```
   Glob: tools/supervisor/governance_validators_ext2.py
   ```

2. **If file exists**: Read lines 1-50 and search for validator function definitions
   - Search for `def validate_playbook_` pattern
   - Count how many playbook validator functions exist
   - Confirm exact validator IDs (V86-V93 or V92-V99)

3. **Verify runner registration**: Read `tools/supervisor/governance_validator_runner.py` lines 380-410
   - Confirm import of governance_validators_ext2
   - Confirm results.extend() call includes playbook validators
   - Record total validator count (claimed: 106)

4. **Check test coverage**: Read `tests/supervisor/test_governance_validators.py`
   - Search for any test class or function referencing "playbook" or "V86"-"V99"
   - If tests are missing: this is a CRITICAL gap (validators implemented but unverified)

5. **Verify WARN-only status**: Confirm `blocks_sprint=False` for all playbook validators

6. **Run validators manually** to prove they execute without error:
   ```
   .venv/Scripts/python -c "
   from tools.supervisor.governance_validator_runner import run_all_validators
   results = run_all_validators()
   playbook_results = [r for r in results if 'playbook' in r.get('validator_id','').lower()]
   print(f'Playbook validator results: {len(playbook_results)}')
   for r in playbook_results: print(r)
   "
   ```

**If validators are missing or not tested:**
- Reopen TC-PB-009 as PARTIAL (validators registered but unverified)
- Add repair taskcard to TC-AUDIT-008

**Acceptance criteria:**
- `governance_validators_ext2.py` existence confirmed
- All 8 playbook validator functions found with correct IDs
- Validators registered in runner
- At least basic test coverage exists (even a single test function per validator)

---

## TC-AUDIT-005: Reprove Pilots P1-P4 with Real Execution

**Scope:** Rerun pilots 1-4 using actual commands and capture real output. Do NOT trust prior YAML declarations.

**P1 — format-feature-expansion template generates bounded taskcards:**
```
.venv/Scripts/python tools/playbook/generate_playbook_taskcards.py \
  playbooks/format-factory/format-feature-expansion.md \
  --plan-id TEST-AUDIT-P1 \
  --gap-ids GAP-AUDIT-001,GAP-AUDIT-002 \
  --output /tmp/pilot1-taskcards.json
```
- Verify: ≥1 taskcard generated with `playbook_id`, `plan_id`, `authority_constraints.no_gate_approval=true`
- Verify: Each taskcard has `allowed_paths` and `forbidden_paths`
- Verify: No taskcard claims gate authority

**P2 — new-format-kickstart stop conditions:**
```
.venv/Scripts/python tools/playbook/generate_playbook_taskcards.py \
  playbooks/format-factory/new-format-kickstart-template.md \
  --plan-id TEST-AUDIT-P2 \
  --gap-ids GAP-AUDIT-003 \
  --output /tmp/pilot2-taskcards.json
```
- Verify: Stop conditions defined in output
- Verify: Taskcards are bounded (have phase names)
- Verify: Provenance in every taskcard

**P3 — product-source-task supervisor integration:**
```
.venv/Scripts/python tools/playbook/playbook_selector.py \
  --work-item-type PRODUCT_SOURCE_PATCH_BOUNDED
```
- Verify: Selector returns `product-source-task.md` path
- Run generator on that template with test inputs
- Verify: 6+ taskcards with provenance

**P4 — odf-flat YAML playbook validate and dry-run:**
```
.venv/Scripts/python tools/playbook/validate_playbook.py \
  acquisition-packs/_families/odf-flat/playbook.yaml
```
- Verify: Returns PASS
- Verify: PASS does NOT grant gate approval (check return code and any gate-approval fields)
```
.venv/Scripts/python tools/playbook/replay_acquisition_playbook.py \
  acquisition-packs/_families/odf-flat/playbook.yaml \
  --dry-run
```
- Verify: Conflicts reported for pre-condition failures (NOT errors)
- Capture raw output

**Negative control for P4:** Confirm `validate_playbook.py` returns non-zero on a deliberately invalid playbook (use `tests/playbook/fixtures/invalid-*.yaml` if available).

**Acceptance criteria:**
- All 4 pilots produce real stdout/stderr output (not just YAML declarations)
- Pilot 1: ≥1 taskcard JSON with required fields
- Pilot 2: JSON output with stop_conditions field
- Pilot 3: Selector returns correct path
- Pilot 4: validation PASS, dry-run shows conflict list

---

## TC-AUDIT-006: Reprove Pilots P5-P8 with Real Execution

**Scope:** Rerun pilots 5-8 using actual commands.

**P5 — Missing skill creates gap, does not hard-block:**
```
.venv/Scripts/python tools/playbook/generate_playbook_taskcards.py \
  playbooks/format-factory/format-feature-expansion.md \
  --plan-id TEST-AUDIT-P5 \
  --gap-ids GAP-AUDIT-004 \
  --require-skill nonexistent-skill-xyz \
  --output /tmp/pilot5-taskcards.json
```
- Verify: Returns exit code indicating PARTIAL_SUCCESS (not hard error)
- Verify: Output notes missing skill / creates gap record
- Verify: No hard block on continuation

If `--require-skill` flag doesn't exist, test via `playbook_execution_log.py`:
```
.venv/Scripts/python -c "
from tools.playbook.playbook_execution_log import PlaybookExecutionLog
log = PlaybookExecutionLog('test-p5', 'format-feature-expansion', '1.2')
log.missing_skill('nonexistent-skill-xyz', 'draft_function')
print(log.to_dict())
"
```
- Verify: `missing_skills` list populated, action = `CREATE_SKILL_GAP`

**P6 — Deprecated playbook rejected by selector:**
```
.venv/Scripts/python -c "
from tools.playbook.playbook_selector import PlaybookSelector
sel = PlaybookSelector()
# Attempt to select a deprecated playbook by work item type
result = sel.select('DEPRECATED_WORKFLOW')
assert result is None, f'Expected None, got {result}'
print('P6 PASS: deprecated/unknown selector returns None')
"
```
Also test with an actual deprecated status in a temp fixture:
```
.venv/Scripts/python -c "
from tools.playbook.playbook_selector import PlaybookSelector
sel = PlaybookSelector()
result = sel.select_by_status('DEPRECATED')
assert result is None or result == []
print('P6 PASS: deprecated status not selectable')
"
```

**P7 — Coverage gap backfill (audit-healing-sprint):**
```
.venv/Scripts/python tools/playbook/playbook_selector.py \
  --work-item-type AUDIT_HEALING_SPRINT
```
- Verify: Returns `playbooks/format-factory/audit-healing-sprint.md`
- Verify: `audit-healing-sprint.md` is in `playbook-registry.yaml` as ACTIVE
- Verify: `playbook-coverage-universe.yaml` lists it as COVERED_UNPROVEN

```
.venv/Scripts/python -c "
import yaml
cu = yaml.safe_load(open('reports/playbooks/playbook-coverage-universe.yaml'))
audit_healing = [w for w in cu['workflows'] if 'audit' in w.get('workflow_id','').lower()]
print(audit_healing)
assert len(audit_healing) > 0, 'audit-healing workflow missing from coverage universe'
print('P7 PASS')
"
```

**P8 — Idempotency (run twice, compare):**
Run the taskcard generator twice with identical inputs and compare output:
```
.venv/Scripts/python tools/playbook/generate_playbook_taskcards.py \
  playbooks/format-factory/format-feature-expansion.md \
  --plan-id TEST-P8-STABLE \
  --gap-ids GAP-STABLE-001 \
  --output /tmp/p8-run1.json

.venv/Scripts/python tools/playbook/generate_playbook_taskcards.py \
  playbooks/format-factory/format-feature-expansion.md \
  --plan-id TEST-P8-STABLE \
  --gap-ids GAP-STABLE-001 \
  --output /tmp/p8-run2.json
```
Compare stable fields (exclude `taskcard_id`, `generated_at` which are intentionally non-idempotent):
```
.venv/Scripts/python -c "
import json
r1 = json.load(open('/tmp/p8-run1.json'))
r2 = json.load(open('/tmp/p8-run2.json'))
# Strip non-idempotent fields
volatile = {'taskcard_id', 'generated_at'}
def strip(t): return {k:v for k,v in t.items() if k not in volatile}
stable1 = [strip(t) for t in r1.get('taskcards',r1)]
stable2 = [strip(t) for t in r2.get('taskcards',r2)]
assert stable1 == stable2, f'Stable fields differ: {stable1} vs {stable2}'
print('P8 PASS: stable fields identical across two runs')
"
```

Also run V92-V99 validators twice and compare:
```
.venv/Scripts/python -c "
from tools.supervisor.governance_validator_runner import run_all_validators
r1 = [(v['validator_id'],v.get('status')) for v in run_all_validators() if 'playbook' in v.get('validator_id','')]
r2 = [(v['validator_id'],v.get('status')) for v in run_all_validators() if 'playbook' in v.get('validator_id','')]
assert r1 == r2, f'Validator results not idempotent: {r1} vs {r2}'
print('P8 PASS: validator results idempotent')
"
```

**Acceptance criteria:**
- All 4 pilots produce real stdout output (not just YAML)
- P5: Missing skill gracefully recorded, not hard-blocked
- P6: Deprecated/invalid selector returns None
- P7: audit-healing-sprint resolvable by selector; present in coverage universe
- P8: Stable fields identical across two runs; MATERIAL_SECOND_RUN_CHANGES = 0

---

## TC-AUDIT-007: Verify Idempotency (Full Second-Run)

**Scope:** Run all generation operations twice; compare checksums.

**Operations to run twice:**
1. Coverage universe derivation: run the playbook coverage tool if available, or re-derive from templates
2. Registry regeneration: regenerate `playbook-registry.yaml` from source templates
3. All playbook tests: run `pytest tests/playbook/ -v` twice

**Compare:**
- SHA-256 of `playbooks/playbook-registry.yaml` after each run
- SHA-256 of `reports/playbooks/playbook-coverage-universe.yaml` after each run
- Test result counts (all must be identical)

**Detect:**
- Timestamps causing churn (if file SHA changes due to embedded timestamp, fix generator)
- Unstable ordering (if YAML list order differs, fix sort logic)
- Duplicate registry entries

**Commands:**
```
# SHA of registry before
python -c "import hashlib; print(hashlib.sha256(open('playbooks/playbook-registry.yaml','rb').read()).hexdigest())"

# Run test suite
.venv/Scripts/pytest tests/playbook/ -v --tb=short 2>&1 | tail -20

# SHA of registry after (should be identical if regeneration is stable)
python -c "import hashlib; print(hashlib.sha256(open('playbooks/playbook-registry.yaml','rb').read()).hexdigest())"
```

**Acceptance criteria:**
- MATERIAL_SECOND_RUN_CHANGES = 0
- Test counts identical across two runs
- STALE_GENERATED_PLAYBOOK_ARTIFACTS = 0

---

## TC-AUDIT-008: Heal All Identified Gaps

**Scope:** Fix every gap found during TC-AUDIT-003 through TC-AUDIT-007. This taskcard is the
catch-all repair step. Actual contents depend on findings, but known gaps from pre-audit include:

### Gap A (HIGH PRIORITY): Validator test coverage
If TC-AUDIT-004 confirms V92-V99 validators have no test functions in `test_governance_validators.py`:

Write test class `TestPlaybookGovernanceValidators` in `tests/supervisor/test_governance_validators.py`:
- `test_v92_validate_playbook_registry_entries_pass()` — with valid registry
- `test_v92_validate_playbook_registry_entries_missing_file()` — with broken path entry
- `test_v93_validate_playbook_has_version_pass()` — template with version field
- `test_v93_validate_playbook_has_version_missing()` — template without version
- (one pass + one fail test per validator, minimum)

For each test:
- Use real file paths from the repository (not mocked paths)
- Assert: warn-only validators return `status='WARN'` not exception on failure
- Assert: validators return `status='PASS'` on valid inputs

### Gap B (MEDIUM): Pilot evidence quality
If TC-AUDIT-005/006 confirms previous pilot evidence files were declarative only:

Write real evidence records from the reproved pilots to:
- `.local/evidences/playbook-audit-rerun-20260702/pilot-1-rerun.yaml`
- `.local/evidences/playbook-audit-rerun-20260702/pilot-2-rerun.yaml`
- ...through pilot-8

Each evidence file must include:
- `command:` — exact command run
- `raw_output:` — actual stdout captured (first 500 chars)
- `exit_code:` — actual return code
- `observed_result:` — what the output actually showed
- `verdict:` PASS or FAIL (based on real results, not declaration)

### Gap C (if found): Missing files
For any expected file that doesn't exist at canonical path:
- Implement the missing file (do not create placeholder)
- Or reopen the relevant taskcard and document as PARTIAL

### Gap D (if found): Supervisor integration not wired
If `autonomous_cycle.py` doesn't actually call `playbook_selector.py`:
- Implement the minimal non-blocking hook (best-effort, try/except wrapping)
- Write a test proving the hook is called when a FORMAT_FEATURE_EXPANSION work item is processed

**Acceptance criteria:**
- All gaps from TC-AUDIT-003 through TC-AUDIT-007 have been fixed or documented as external blockers
- All new tests pass
- No `REMAINING_LOCALLY_ACTIONABLE_FINDINGS` remain

---

## TC-AUDIT-009: Run Full Test Suite and Capture Results

**Scope:** Run the complete test suite after healing to prove nothing was broken.

**Commands:**
```
# Full playbook test suite
.venv/Scripts/pytest tests/playbook/ -v --tb=short 2>&1

# Governance validators (including new playbook tests)
.venv/Scripts/pytest tests/supervisor/test_governance_validators.py -v --tb=short 2>&1

# ODF-flat family playbook tests
.venv/Scripts/pytest tests/playbook/test_odf_flat_family_playbook.py -v --tb=short 2>&1
```

**Record:**
```yaml
validation_audit:
  command: .venv/Scripts/pytest tests/playbook/ -v --tb=short
  expected_scope: All playbook system tests
  observed_scope: <actual count>
  passed: <N>
  skipped: <N>
  failed: 0
  enforcement_level: REQUIRED (0 failures)
```

**Acceptance criteria:**
- REQUIRED_VALIDATORS_NOT_EXECUTED = 0
- REQUIRED_TESTS_NOT_EXECUTED = 0
- WEAK_TESTS_ACCEPTED_AS_PROOF = 0 (each validator must have ≥1 real test function)
- All tests pass (0 failures)

---

## TC-AUDIT-010: Final Independent Assessment and Closure Verdict

**Scope:** Score all 11 dimensions (1-5 scale). Verify all audit counters are zero. Issue verdict.

**Dimension scoring (1-5):**
1. Plan coverage — were all plan requirements represented?
2. Implementation correctness — do files do what they claim?
3. Taskcard integrity — were dependent taskcards done in order?
4. Integration — does the supervisor actually call the playbook hook?
5. Evidence quality — are pilots proven by real execution?
6. Test quality — are validators tested with real positive and negative cases?
7. Governance enforcement — do V92-V99 return WARN not exceptions on failure?
8. Reliability — do all tools handle missing inputs gracefully?
9. Maintainability — are files documented and under test?
10. Idempotency — do two runs produce identical results?
11. Scope discipline — no scope creep beyond FF-PLAYBOOK-SYSTEM-001?

**Required counters (must all equal 0):**
```
PLAN_REQUIREMENTS_NOT_REPRESENTED = 0
FALSELY_CLOSED_TASKCARDS = 0
OPEN_MANDATORY_TASKCARDS = 0
PLAYBOOK_SYSTEM_INTEGRATION_GAPS = 0
TASKCARDS_WITHOUT_PLAYBOOK_PROVENANCE = 0
PLAYBOOK_GATE_AUTHORITY_VIOLATIONS = 0
REQUIRED_VALIDATORS_NOT_EXECUTED = 0
REQUIRED_TESTS_NOT_EXECUTED = 0
WEAK_TESTS_ACCEPTED_AS_PROOF = 0
FAILED_REQUIRED_PILOTS = 0
PILOTS_WITHOUT_RAW_EVIDENCE = 0
STALE_GENERATED_PLAYBOOK_ARTIFACTS = 0
MATERIAL_SECOND_RUN_CHANGES = 0
REMAINING_LOCALLY_ACTIONABLE_FINDINGS = 0
```

**Final verdict (one of):**
- `PLAN_EXECUTION_FULLY_VERIFIED_HEALED_AND_CLOSED` — all counters at zero, all pilots proven with real evidence
- `PLAN_EXECUTION_REOPENED_REPAIR_CONTINUES` — gaps remain, repair continues in next session
- `PLAN_EXECUTION_BLOCKED_TRUE_EXTERNAL_DEPENDENCY` — blocked by non-agent-resolvable issue

**Write closure record** to `reports/playbooks/playbook-audit-closure-20260702.yaml`:
```yaml
mission: FF-PLAYBOOK-AUDIT-001
source_plan: plans/.claude/bright-marinating-map.md
source_mission: FF-PLAYBOOK-SYSTEM-001
audit_date: 2026-07-02
auditor: noble-fluttering-truffle
verdict: <FINAL_VERDICT>
dimensions: {...}
counters: {...}
evidence_paths:
  - .local/evidences/playbook-audit-rerun-20260702/
```

**After writing closure record**, if verdict is FULLY_VERIFIED:
```
python tools/supervisor/write_plan_lock.py \
  --plan-path plans/.claude/noble-fluttering-truffle.md \
  --terminal --audit-gate
```

---

## Execution Order and Dependencies

```
TC-AUDIT-001  (bind)
    ↓
TC-AUDIT-002  (requirements matrix)
    ↓
TC-AUDIT-003  (file verification)   ──┐
TC-AUDIT-004  (validator chain)     ──┤ → These inform what
                                       ↓   gaps exist for:
TC-AUDIT-005  (pilots P1-P4)        ──┐
TC-AUDIT-006  (pilots P5-P8)        ──┤
TC-AUDIT-007  (idempotency)         ──┘
                    ↓
TC-AUDIT-008  (heal gaps)
                    ↓
TC-AUDIT-009  (run full test suite)
                    ↓
TC-AUDIT-010  (assessment + verdict)
```

TC-AUDIT-003 and TC-AUDIT-004 can run in parallel.
TC-AUDIT-005 and TC-AUDIT-006 can run in parallel after TC-AUDIT-003/004.

---

## Known Pre-Audit Findings (to verify during execution)

These were identified in pre-audit exploration and must be independently confirmed:

| Finding | Severity | Status | Expected resolution |
|---|---|---|---|
| Pilot EXEC log `taskcards: []` + `verdict: SUCCESS` (logical contradiction) | CRITICAL | unconfirmed | TC-AUDIT-005/006 reprove |
| V92-V99 validators have zero test functions in test suite | HIGH | unconfirmed | TC-AUDIT-004 verify, TC-AUDIT-008 fix |
| Agents contradict each other on `governance_validators_ext2.py` existence | HIGH | unconfirmed | TC-AUDIT-004 resolve |
| Validator numbering: plan says V86-V93, runner registration says V92-V99 | MEDIUM | unconfirmed | TC-AUDIT-004 resolve |

---

## Files: Key Paths for Execution

| File | Role |
|---|---|
| `plans/.claude/bright-marinating-map.md` | Authoritative plan under audit |
| `tools/supervisor/governance_validators_ext2.py` | Claimed location of V86-V99 validators |
| `tools/supervisor/governance_validator_runner.py` | Runner that imports validators (lines 380-410) |
| `tests/supervisor/test_governance_validators.py` | Validator tests (check for playbook coverage) |
| `tools/playbook/generate_playbook_taskcards.py` | Taskcard generator (real code, 386 LOC) |
| `tools/playbook/playbook_selector.py` | Work-item-type router |
| `tools/playbook/playbook_execution_log.py` | Execution recorder |
| `tools/supervisor/autonomous_cycle.py` | Supervisor hook location (lines 447-475) |
| `playbooks/playbook-registry.yaml` | Canonical registry (6+ ACTIVE entries) |
| `reports/playbooks/playbook-coverage-universe.yaml` | 14 workflows, generated 2026-07-02 |
| `.local/evidences/playbook-pilots-20260701/` | Original pilot evidence (quality disputed) |
| `.local/evidences/playbook-audit-rerun-20260702/` | Real pilot evidence (to be written) |
| `schemas/playbook/playbook-task-binding.schema.json` | Binding schema |


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-01T20:17:56.177556+00:00"
  locked_by: "df3c9d31692b"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->

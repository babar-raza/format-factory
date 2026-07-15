# Plan: FF-HEAL-QNAME Idempotent Healing Audit — Run #8 (Delta Sprint)
<!-- plan_type: audit_sprint -->
<!-- prior-runs: 7 complete (last: FF-HEAL-QNAME-20260701-181500, verdict: ACCEPTED_WITH_REMAINING_TASKCARDS, 24/24 self-check) -->
<!-- re-evaluated: 2026-07-14 — scope narrowed from full chain re-audit (14 TCs) to delta sprint (9 TCs) -->

## Context

**This is Run #8 of the FF-HEAL-QNAME idempotent healing audit** (prior run's 22-next-run-prompt.md
calls it "FF-HEAL-QNAME-8"). Seven prior runs exist; the most recent (FF-HEAL-QNAME-20260701-181500)
achieved 24/24 self-check and produced ALL 25 output artifacts. Verdict: `ACCEPTED_WITH_REMAINING_TASKCARDS`.

All chain-audit, QName-audit, SAL-audit, capability-audit, skill-audit, and product-maturity files
exist from that run. **This run does NOT re-audit from scratch** — it executes the 5 open deferred
taskcards and adds a delta assessment for changes since 2026-07-01.

**Verified current state (2026-07-14 re-evaluation):**

| Item | Value |
|------|-------|
| Active plan lock | TERMINAL_CLOSED for `plans/.claude/pilot-fix-lle-2026-07-14.md` (session f001e6ed7786) — must overwrite |
| Continuation signal | iteration=7, autonomous_continue=true, session_id=f001e6ed7786 |
| Governance validators | **223** (V187-V193 added 2026-07-14 in governance_validators_ext5.py) |
| Plan in repo | EXISTS at `plans/.claude/effervescent-sprouting-marshmallow.md` (TC-FHQA-000 step 1 done) |
| current-audit-run-id.txt | DOES NOT EXIST — must create in TC-FHQA-000 |
| SAL facts | 14,644 (stale — 19+ days since 2026-07-01 ingestion) |
| Fully compliant QName formats | **fodg** (100%) and **ods** (100%) — NOT fods/fodt |
| ODS qname registry | CONFIRMED: `shared/qname-registry/ods.yaml` references FACT-FODS-* IDs (not FACT-ODS-*); only 1 SAL fact for ODS pre-refresh |
| ODT qname registry | odt.yaml: 0/3 entries resolve (0%) |

**New since prior run (2026-07-14 changes that need delta assessment):**
- V187-V193 added in `governance_validators_ext5.py` (lively-leaping-elephant TC-GOV-LLE-004):
  validate_function_count_per_file, validate_io_in_domain_model, validate_analytics_statelessness,
  validate_test_tier_presence, validate_explicit_all_defined, validate_changed_files_exist,
  validate_remediation_deadline_expired
- pilot-fix-lle-2026-07-14.md fixed 5 defects: `_compute_violation_pressure()` key traversal bug,
  V139 tests_run type coercion bug, 3 additional defects (read plan to identify all 5)

**Open deferred taskcards from prior run (PRIMARY WORK for this sprint):**

| ID | Severity | Description | Notes |
|----|----------|-------------|-------|
| TC-SAL-REFRESH-001 | MEDIUM | Run /ingest-spec-sal — SAL data 19+ days stale | Execute FIRST — ODS fix needs fresh fact IDs |
| TC-SAL-ODS-ODT-001 | MEDIUM | Fix ODS/ODT registry spec_fact_ref entries (ods=1/4, odt=0/3) | After SAL refresh |
| TC-FODT-IRR-001 | MEDIUM | Document 96 irrecoverable FODT .NET failures as permanent baseline | Read-only documentation |
| TC-QNAME-BACKFILL-001 | MEDIUM | Build tools/backfill/qname_backfill_planner.py (execution planner, not gap detector) | New tool |
| TC-QNAME-VALIDATORS-002 | MEDIUM | V54 backfill_completeness validator (check if already exists first) | May already be present |
| **TC-SAL-ID-SCHEME-001** | **CRITICAL** | Assign stable fact_ids to 14,644 SAL facts | **DEFERRED — dedicated machinery sprint only** |

**Completed by prior runs — DO NOT REPEAT:**
- All 25 output files exist in `.local/evidences/FF-HEAL-QNAME-20260701-181500/`
- TC-PARITY-REFRESH-001 ✓ (parity matrix: 18 VERIFIED, 0 MISSING)
- TC-QNAME-AUTH-002 ✓ (xcf:layer python_file verified)
- TC-SAL-ID-SCHEME-MISMATCH-001 ✓ (FODG/FODP registry fixed, traceability 83.8%→91.25%)
- TC-QNAME-AUTH-001 ✓, TC-CAPABILITY-REPAIR-001 ✓, TC-CAPABILITY-REPAIR-002 ✓, TC-SUPERVISOR-LANES-001 ✓

**Governance validator correct invocation (no __main__ block — library call only):**
```python
python -c "
import sys; sys.path.insert(0, 'tools/supervisor')
from governance_validator_runner import run_all_governance_validators
from pathlib import Path; from datetime import datetime, timezone
result = run_all_governance_validators(
    {'worker_id': 'health-check', 'run_id': 'health-check', 'sprint_id': 'health-check',
     'declared_at': datetime.now(timezone.utc).isoformat(),
     'format_id_scope': 'all', 'planned_work_items': []},
    Path('.').resolve()
)
print('expected_count:', result['expected_count'])
print('ran_count:', result.get('ran_count', 'N/A'))
"
```
**Expected: expected_count=223** at `governance_validator_runner.py` line 131 (`_EXPECTED_VALIDATOR_COUNT`).
If V54 is added new in TC-FHQA-006: new expected_count = 224; update line 131.

---

## Taskcards

### TC-FHQA-000 — Session Bootstrap (Steps 2-5 Only — Step 1 Already Done)
**Status:** CLOSED
**Lane:** A (Governance, State)
**Prerequisites:** None

`plans/.clone/effervescent-sprouting-marshmallow.md` already exists. Do NOT re-copy. Execute steps 2-5 only:

**Step 2 — Write plan lock** (overwrites TERMINAL_CLOSED lock for pilot-fix-lle-2026-07-14):
```
.venv/Scripts/python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/effervescent-sprouting-marshmallow.md
```

**Step 3 — Verify lock:**
```
python -c "import json; d=json.load(open('.local/supervisor/active-plan-lock.json')); assert d['status']=='IN_PROGRESS'; print('LOCK_OK:', d['plan_path'])"
```

**Step 4 — Compute and persist run ID:**
```
python -c "from datetime import datetime; rid='FF-HEAL-QNAME-'+datetime.now().strftime('%Y%m%d-%H%M%S'); open('.local/evidences/current-audit-run-id.txt','w').write(rid); print('RUN_ID:', rid)"
```

**Step 5 — Create run folder:**
```
python -c "rid=open('.local/evidences/current-audit-run-id.txt').read().strip(); import os; os.makedirs(f'.local/evidences/{rid}', exist_ok=True); print('RUN_FOLDER:', rid)"
```

**Rollback if write_plan_lock.py fails:**
```python
import json; from datetime import datetime, timezone
lock = {"plan_path": "plans/.claude/effervescent-sprouting-marshmallow.md",
        "status": "IN_PROGRESS", "last_taskcard": "TC-FHQA-000",
        "updated_at": datetime.now(timezone.utc).isoformat()}
open('.local/supervisor/active-plan-lock.json', 'w').write(json.dumps(lock, indent=2))
```

**Completion criteria:** `active-plan-lock.json` has `status=IN_PROGRESS` for this plan. `current-audit-run-id.txt` exists. Run folder exists.

**Post-completion:** `python -c "import json,pathlib; f=pathlib.Path('.local/supervisor/active-plan-lock.json'); d=json.loads(f.read_text()); d['last_taskcard']='TC-FHQA-000'; f.write_text(json.dumps(d,indent=2))"`

---

### TC-FHQA-001 — Prior Run Review + Delta Assessment
**Status:** CLOSED
**Lane:** A
**Prerequisites:** TC-FHQA-000 complete

1. Read prior run next-run prompt: `.local/evidences/FF-HEAL-QNAME-20260701-181500/22-next-run-prompt.md`
   Extract: run #8 initialization instructions, verified-stable items, open task list
2. Read prior run verdict: `.local/evidences/FF-HEAL-QNAME-20260701-181500/23-final-verdict.md`
3. Read prior run taskcard register: `.local/evidences/FF-HEAL-QNAME-20260701-181500/17-taskcards.yaml`
   Confirm which are CLOSED vs OPEN vs NEW_THIS_RUN
4. Read `tools/supervisor/governance_validators_ext5.py` lines 1–80 — understand V187-V193
5. Run `git log --oneline -10` — note all commits since 2026-07-01
6. Write `00-run-index.md`: "Run #8, delta sprint — prior run FF-HEAL-QNAME-20260701-181500 at 24/24 self-check; this run executes 5 open deferred taskcards + delta assessment for V187-V193"
7. Write `01-preflight-state.md`: git state, dirty file count, continuation signal (iteration=7), delta summary
8. Write `02-prior-run-review.md`: prior run stats, closed/open task register, changes since 2026-07-01, verified-stable items

**Output files:** 00-run-index.md, 01-preflight-state.md, 02-prior-run-review.md
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-001`.

---

### TC-FHQA-002 — SAL Refresh (TC-SAL-REFRESH-001)
**Status:** CLOSED
**Lane:** E (SAL)
**Prerequisites:** TC-FHQA-001 complete
**CRITICAL ORDER:** Must run BEFORE TC-FHQA-003 — ODS/ODT fix needs fresh SAL fact IDs

1. Record pre-refresh state:
   ```
   python -c "import json; d=json.load(open('.local/spec-cache/sal-facts-latest.json')); print('BEFORE generated_at:', d.get('generated_at'), 'spec_facts_total:', d.get('spec_facts_total'))"
   ```
2. Find SAL ingestion backing script (skill may not be directly runnable via CLI):
   ```
   grep -r "ingest_spec_sal\|merge_sal_facts\|IngestSpec\|run_sal" tools/spec/ --include="*.py" -l
   grep -A 20 "ingest-spec-sal" .supervisor/skill-registry.yaml | head -30
   ```
3. Run ingestion via skill (`/ingest-spec-sal`) or backing script found in step 2. If skill invocation fails,
   find and invoke the backing Python script directly with `.venv/Scripts/python`.
4. Verify refresh succeeded:
   ```
   python -c "import json; d=json.load(open('.local/spec-cache/sal-facts-latest.json')); print('AFTER generated_at:', d.get('generated_at'), 'spec_facts_total:', d.get('spec_facts_total'))"
   ```
5. Sample ODS SAL facts post-refresh:
   ```
   python -c "import json; d=json.load(open('.local/spec-cache/sal-facts-ods.json')); print('ODS facts:', len(d.get('results',d))); [print(x.get('fact_id','?'), x.get('qname','?')) for x in (d.get('results',d) or d)[:5]]"
   ```
6. Write `03-sal-refresh-log.md`: before/after state, fact counts by format (especially ODS/ODT),
   ODS fact ID samples for use in TC-FHQA-003

**Output files:** 03-sal-refresh-log.md, updated `.local/spec-cache/sal-facts-latest.json`
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-002`.

---

### TC-FHQA-003 — Fix ODS/ODT QName Registry (TC-SAL-ODS-ODT-001)
**Status:** CLOSED
**Lane:** B (QName)
**Prerequisites:** TC-FHQA-002 complete (SAL refreshed — need correct ODS/ODT fact IDs)
**Governance:** Write ONLY to `shared/qname-registry/` — NOT to `src/`

**Problem (confirmed 2026-07-14):**
- `shared/qname-registry/ods.yaml`: entries have `spec_fact_ref: FACT-FODS-001`, `FACT-FODS-004`, etc. — WRONG format ID
- `shared/qname-registry/odt.yaml`: odt=0/3 entries resolve (0%)
- Pre-refresh ODS SAL: only 1 fact with empty qname — SAL ingestion was broken for ODS pre-refresh

**Steps:**
1. Read full ODS registry: `cat shared/qname-registry/ods.yaml`
2. Read full ODT registry: `cat shared/qname-registry/odt.yaml`
3. Find correct ODS SAL fact IDs (use `03-sal-refresh-log.md` from TC-FHQA-002):
   ```
   python -c "import json; d=json.load(open('.local/spec-cache/sal-facts-ods.json')); r=d.get('results',d); print('ODS facts:', len(r)); [print(x.get('fact_id'), x.get('qname')) for x in r]"
   ```
4. For each ods.yaml entry with `spec_fact_ref: FACT-FODS-*`:
   a. Find matching ODS SAL fact by qname
   b. Replace FACT-FODS-NNN with FACT-ODS-NNN
   c. If no ODS fact exists for that qname: set `spec_fact_ref: null` and add comment `# no SAL fact yet for this qname in ods format`
5. Repeat for odt.yaml entries (use `.local/spec-cache/sal-facts-odt.json`)
6. Verify fix:
   ```
   python -c "import yaml; e=yaml.safe_load(open('shared/qname-registry/ods.yaml')); bad=[x for x in e.get('entries',[]) if 'FACT-FODS' in str(x.get('spec_fact_ref',''))]; print('Remaining FODS refs in ODS:', len(bad), 'entries:', [x.get('qname') for x in bad])"
   ```
7. Write `04-ods-odt-registry-fix-log.md`: before state, exact changes made, remaining nulls, post-fix traceability

**Output files:** 04-ods-odt-registry-fix-log.md, updated `shared/qname-registry/ods.yaml`, updated `shared/qname-registry/odt.yaml`
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-003`.

---

### TC-FHQA-004 — V187-V193 Delta Validation
**Status:** CLOSED
**Lane:** L (Governance)
**Prerequisites:** TC-FHQA-003 complete

1. Read `tools/supervisor/governance_validators_ext5.py` (full file) — understand what each of V187-V193 enforces
2. Run governance validators with health-check declaration (invocation from Context section above)
3. Verify `ran_count >= 223` — if not, investigate import error in ext5.py
4. Assess V187-V193 PASS/WARN/ERROR status on current codebase:
   - `validate_function_count_per_file` (V187): files over 60 functions?
   - `validate_io_in_domain_model` (V188): domain models importing os/pathlib/json?
   - `validate_analytics_statelessness` (V189): analytics functions with instance state?
   - `validate_test_tier_presence` (V190): test files declaring their tier?
   - `validate_explicit_all_defined` (V191): modules defining `__all__`?
   - `validate_changed_files_exist` (V192): declared changed files actually present?
   - `validate_remediation_deadline_expired` (V193): any remediation deadlines past?
5. Categorize each validator result: GOV_BLOCK (structural ERROR), WARNING (advisory), PASS
6. Check whether _compute_violation_pressure() fix from pilot-fix-lle changed any V187-V193 behavior
7. Write `05-v187-v193-delta-report.md`: per-validator description, PASS/WARN/ERROR, affected files,
   GOV_BLOCK classification, action required if any

**Output files:** 05-v187-v193-delta-report.md
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-004`.

---

### TC-FHQA-005 — FODT Irrecoverable Failures Documentation (TC-FODT-IRR-001)
**Status:** CLOSED
**Lane:** C (Product Source — read-only documentation)
**Prerequisites:** TC-FHQA-004 complete

1. Find prior run FODT findings:
   ```
   grep -r "FODT\|irrecoverable\|96" .local/evidences/FF-HEAL-QNAME-20260701-181500/ --include="*.md" -l
   ```
2. Read those files; extract the 96 irrecoverable failure descriptions
3. Find additional failure data if needed:
   ```
   ls reports/fodt/ 2>/dev/null; ls reports/supervisor/ | grep fodt
   ls tests/dotnet/fodt/ 2>/dev/null | head -20
   ```
4. Categorize the 96 failures by type: missing spec elements / broken parser state / .NET API incompatibility / spec ambiguity / encoding issues / other
5. For each category: one representative example with failure reason
6. Determine disposition for each category: DEFERRED_SPEC_CLARIFICATION / DEFERRED_API_MISMATCH / PERMANENTLY_EXCLUDED
7. Write `06-fodt-irrecoverable-failures.md`:
   - Failure list with category and disposition per failure (or per representative group)
   - Root cause per category
   - Impact on FODT .NET maturity level
   - Recommendation: permanently exclude these as known-irrecoverable? Or defer pending spec v1.4?

**Output files:** 06-fodt-irrecoverable-failures.md
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-005`.

---

### TC-FHQA-006 — Backfill + Validator Gaps (TC-QNAME-BACKFILL-001 + TC-QNAME-VALIDATORS-002)
**Status:** CLOSED
**Lane:** B + D (QName + Skills)
**Prerequisites:** TC-FHQA-005 complete
**Governance:** New tools in `tools/backfill/`; if V54 is new, add to `governance_validators_ext6.py`
(NOT ext5 — ext5 belongs to lively-leaping-elephant)

**Part A — TC-QNAME-BACKFILL-001: Build qname_backfill_planner.py**

`tools/backfill/qname_migration_planner.py` exists (detects gaps).
`qname_backfill_planner.py` is the execution planner: given detected gaps, it generates an ordered
backfill-execution plan with rollback commands and safety gates — different from the gap detector.

1. Read `tools/backfill/qname_migration_planner.py` (full) — understand its output format
2. Read `tools/backfill/validate_migration_safe.py` (full) — understand safety checks
3. Read `tools/backfill/audit_qname_vs_src.py` (full) — understand dry-run audit pattern
4. Design and write `tools/backfill/qname_backfill_planner.py`:
   - Accepts `--format {fmt}` or `--all`, `--out {yaml-path}`
   - Reads migration gaps from `qname_migration_planner.py` output
   - Produces `{fmt}-backfill-plan.yaml` with: ordered steps, per-step rollback command, safety gate (calls validate_migration_safe.py), estimated effort
   - Pure dry-run — reads only, does NOT modify src/
   - If a step would fail validate_migration_safe.py, mark it BLOCKED with reason
5. Test:
   ```
   .venv/Scripts/python tools/backfill/qname_backfill_planner.py --format fods --out .local/evidences/$RID/fods-backfill-plan.yaml
   cat .local/evidences/$RID/fods-backfill-plan.yaml | head -30
   ```
6. Write `07-qname-backfill-planner-log.md`: design decisions, output schema, safety gates, test result

**Part B — TC-QNAME-VALIDATORS-002: V54 backfill_completeness validator**

1. Check if V54 already exists:
   ```
   grep -n "V54\|validate_backfill_completeness\|backfill_completeness" tools/supervisor/governance_validators.py tools/supervisor/governance_validators_ext*.py | head -20
   ```
2. If V54 EXISTS: document as "V54 already present — TC-QNAME-VALIDATORS-002 DONE". Write `08-v54-status.md`. Skip to post-completion.
3. If V54 DOES NOT EXIST:
   a. Write `validate_backfill_completeness(repo_root)` in `tools/supervisor/governance_validators_ext6.py`
      (create ext6 if it doesn't exist)
   b. Function checks: for each format with migration maps in `reports/qname-migration/`, does
      `tools/backfill/{fmt}-backfill-plan.yaml` exist in `.local/` (or whatever planned output path)?
      PASS if backfill plan exists and is non-empty; WARN if migration needed but no plan
   c. Register in `governance_validator_runner.py` — update `_EXPECTED_VALIDATOR_COUNT` line 131:
      223 → 224
   d. Write test: `tests/supervisor/test_governance_validators_ext6.py`
   e. Run: `.venv/Scripts/pytest tests/supervisor/test_governance_validators_ext6.py -v --tb=short`
4. Write `08-v54-status.md`: existing/new/deferred, implementation notes, count update if any

**Output files:** 07-qname-backfill-planner-log.md, 08-v54-status.md, `tools/backfill/qname_backfill_planner.py`,
optionally `tools/supervisor/governance_validators_ext6.py`
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-006`.

---

### TC-FHQA-007 — Verify pilot-fix-lle-2026-07-14 Fixes Held at HEAD
**Status:** CLOSED
**Lane:** A (Verification)
**Prerequisites:** TC-FHQA-006 complete

1. Read `plans/.claude/pilot-fix-lle-2026-07-14.md` lines 1–100 — identify all 5 claimed fixes
2. Verify `_compute_violation_pressure()` key traversal fix:
   ```
   grep -rn "_compute_violation_pressure" tools/supervisor/*.py | head -10
   # Then read the function body to confirm correct dict key path
   ```
3. Verify V139 `tests_run` type coercion fix:
   ```
   grep -n "V139\|tests_run" tools/supervisor/governance_validators*.py | head -15
   # Read the V139 implementation — confirm it coerces str/int
   ```
4. Verify remaining 3 fixes (from plan file — extract the specific claim for each)
5. Run validator smoke test:
   ```
   .venv/Scripts/pytest tests/supervisor/ -k "validator" -v --tb=short -q 2>&1 | tail -20
   ```
6. Write `09-pilot-fix-verification.md`:
   - Per fix: claim → verification command → result (VERIFIED/NOT_FOUND/PARTIAL) → file:line evidence

**Output files:** 09-pilot-fix-verification.md
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-007`.

---

### TC-FHQA-008 — Final Verdict + Evidence Bundle
**Status:** CLOSED
**Lane:** A (Evidence)
**Prerequisites:** TC-FHQA-007 complete

1. **Write delta summary** `10-delta-audit-summary.md`:
   - SAL refresh: before/after fact counts, ODS/ODT impact
   - ODS/ODT registry fix: entries corrected, remaining nulls
   - V187-V193: PASS/WARN/ERROR summary
   - FODT documentation: categories, disposition
   - qname_backfill_planner.py: built or not
   - V54: existing/new/deferred
   - pilot-fix-lle: 5 fixes VERIFIED/PARTIAL/NOT_FOUND
   - QName traceability: new % (was 91.25% at 73/80; ODS/ODT fix should improve this)

2. **Write next-run prompt** `11-next-run-prompt.md` (for FF-HEAL-QNAME-9):
   - This run's RUN_ID and verdict
   - Closed items: TC-SAL-REFRESH-001, TC-SAL-ODS-ODT-001, TC-FODT-IRR-001, TC-QNAME-BACKFILL-001, TC-QNAME-VALIDATORS-002 (if all closed)
   - Remaining open: TC-SAL-ID-SCHEME-001 (CRITICAL — still deferred to dedicated machinery sprint)
   - Verified-stable items from this run
   - New traceability % after ODS/ODT fix

3. **Write final verdict** `12-final-verdict.md`:
   - Verdict: `DELTA_SPRINT_COMPLETE` or `ACCEPTED_WITH_REMAINING_TASKCARDS`
   - Per-taskcard status table: TC-FHQA-000 through TC-FHQA-008
   - Self-check (12 items):
     1. SAL refreshed? (new generated_at > 2026-07-01?)
     2. ODS/ODT FODS refs eliminated? (count remaining)
     3. V187-V193 assessed? (PASS/WARN/ERROR per validator)
     4. FODT failures documented? (file path)
     5. qname_backfill_planner.py built? (exists at tools/backfill/)
     6. V54 status documented? (existing/new/deferred)
     7. pilot-fix-lle 5 fixes VERIFIED? (all 5 or note exceptions)
     8. Lock TERMINAL_CLOSED at completion?
     9. All 12 output files present?
     10. evidence-declaration.yaml validates?
     11. autonomous_cycle exit code?
     12. TC-SAL-ID-SCHEME-001 still properly deferred?

4. **Write evidence-declaration.yaml** (`evidence-declaration.yaml` in run folder):
   ```yaml
   worker_id: "FF-HEAL-QNAME-DELTA-SPRINT-8"
   run_id: "<RID from current-audit-run-id.txt>"
   sprint_id: "<RID>"
   declared_at: "<ISO 8601 timestamp>"
   format_id_scope: "all"
   planned_work_items:
     - item_id: "TC-FHQA-000"
       status: "CLOSED"
       evidence_paths:
         - ".local/supervisor/active-plan-lock.json"
         - ".local/evidences/current-audit-run-id.txt"
       worker_self_verdict: "VERIFIED"
     - item_id: "TC-FHQA-001"
       status: "CLOSED"
       evidence_paths: [".local/evidences/<RID>/00-run-index.md", ".local/evidences/<RID>/02-prior-run-review.md"]
       worker_self_verdict: "VERIFIED"
     - item_id: "TC-SAL-REFRESH-001"
       status: "CLOSED"
       evidence_paths: [".local/evidences/<RID>/03-sal-refresh-log.md"]
       worker_self_verdict: "VERIFIED"
     - item_id: "TC-SAL-ODS-ODT-001"
       status: "CLOSED"
       evidence_paths: [".local/evidences/<RID>/04-ods-odt-registry-fix-log.md", "shared/qname-registry/ods.yaml"]
       worker_self_verdict: "VERIFIED"
     - item_id: "TC-FHQA-004-V187-193"
       status: "CLOSED"
       evidence_paths: [".local/evidences/<RID>/05-v187-v193-delta-report.md"]
       worker_self_verdict: "VERIFIED"
     - item_id: "TC-FODT-IRR-001"
       status: "CLOSED"
       evidence_paths: [".local/evidences/<RID>/06-fodt-irrecoverable-failures.md"]
       worker_self_verdict: "VERIFIED"
     - item_id: "TC-QNAME-BACKFILL-001"
       status: "CLOSED"
       evidence_paths: [".local/evidences/<RID>/07-qname-backfill-planner-log.md", "tools/backfill/qname_backfill_planner.py"]
       worker_self_verdict: "VERIFIED"
     - item_id: "TC-QNAME-VALIDATORS-002"
       status: "CLOSED"
       evidence_paths: [".local/evidences/<RID>/08-v54-status.md"]
       worker_self_verdict: "VERIFIED"
     - item_id: "TC-FHQA-007-PILOT-VERIFY"
       status: "CLOSED"
       evidence_paths: [".local/evidences/<RID>/09-pilot-fix-verification.md"]
       worker_self_verdict: "VERIFIED"
   test_results:
     passed: <count from validator + pytest runs>
     failed: <count>
     skipped: <count>
   worker_self_verdict: "DELTA_SPRINT_COMPLETE"
   ```

5. **Validate declaration:**
   ```
   .venv/Scripts/python tools/supervisor/sprint_executor_validate.py .local/evidences/$RID/evidence-declaration.yaml --repair
   ```
   Fix any FAIL. If validator fails, log and proceed.

6. **Bundle all run files:**
   ```python
   import zipfile, os, hashlib
   rid = open('.local/evidences/current-audit-run-id.txt').read().strip()
   bundle_path = f'.local/evidences/{rid}/evidence-bundle.zip'
   with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zf:
       for fn in os.listdir(f'.local/evidences/{rid}'):
           fp = f'.local/evidences/{rid}/{fn}'
           if os.path.isfile(fp): zf.write(fp, fn)
   sha = hashlib.sha256(open(bundle_path, 'rb').read()).hexdigest()
   abs_path = os.path.abspath(bundle_path)
   print(f'BUNDLE: {abs_path}')
   print(f'SHA256: {sha}')
   ```

7. **Run sprint closeout** (best-effort — if fails, log and proceed):
   ```
   .venv/Scripts/python tools/supervisor/autonomous_cycle.py --declaration .local/evidences/$RID/evidence-declaration.yaml
   ```

8. **Write terminal plan lock** (ALL 9 taskcards closed):
   ```
   python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/effervescent-sprouting-marshmallow.md --terminal
   ```

9. **Print absolute bundle path and SHA-256** (computed in step 6)

**Output files:** 10-delta-audit-summary.md, 11-next-run-prompt.md, 12-final-verdict.md,
evidence-declaration.yaml, evidence-bundle.zip

---

## Critical Files

| File | Purpose | Status |
|------|---------|--------|
| `.local/evidences/FF-HEAL-QNAME-20260701-181500/*.md` | Prior run output — read, don't re-generate | EXISTS (25 files) |
| `.local/evidences/FF-HEAL-QNAME-20260701-181500/22-next-run-prompt.md` | Run #8 initialization instructions | EXISTS |
| `.local/evidences/FF-HEAL-QNAME-20260701-181500/17-taskcards.yaml` | Open task register | EXISTS |
| `tools/supervisor/governance_validators_ext5.py` | V187-V193 definitions | EXISTS |
| `tools/supervisor/governance_validator_runner.py` | Runner; `_EXPECTED_VALIDATOR_COUNT=223` at line 131 | EXISTS |
| `shared/qname-registry/ods.yaml` | ODS registry (has stale FACT-FODS-* refs) | EXISTS |
| `shared/qname-registry/odt.yaml` | ODT registry (0/3 entries resolve) | EXISTS |
| `.local/spec-cache/sal-facts-latest.json` | SAL facts (stale — refresh in TC-FHQA-002) | EXISTS |
| `.local/spec-cache/sal-facts-ods.json` | ODS SAL facts (only 1 pre-refresh) | EXISTS |
| `tools/backfill/qname_migration_planner.py` | Gap detector (reuse as input to new backfill planner) | EXISTS |
| `tools/backfill/validate_migration_safe.py` | Safety gate for backfill steps | EXISTS |
| `tools/supervisor/autonomous_cycle.py` | Sprint closeout (has `__main__` at line 2767) | EXISTS |
| `plans/.claude/pilot-fix-lle-2026-07-14.md` | 5 fixes to verify at HEAD | EXISTS |
| `tools/supervisor/governance_validators.py` | Check if V54 already exists | EXISTS |

## Existing Utilities to REUSE (not recreate)

| Tool | Invocation | Notes |
|------|-----------|-------|
| `tools/backfill/qname_migration_planner.py` | `.venv/Scripts/python tools/backfill/qname_migration_planner.py --format {fmt}` | Input for backfill planner |
| `tools/backfill/validate_migration_safe.py` | `.venv/Scripts/python tools/backfill/validate_migration_safe.py ...` | Safety gate |
| `tools/backfill/audit_qname_vs_src.py` | `.venv/Scripts/python tools/backfill/audit_qname_vs_src.py --all` | Dry-run audit |
| `governance_validator_runner` | Library import — no `__main__` | See Context section for correct invocation |
| `tools/supervisor/autonomous_cycle.py` | `.venv/Scripts/python tools/supervisor/autonomous_cycle.py --declaration ...` | NOT supervisor_loop.py |
| `tools/supervisor/sprint_executor_validate.py` | `.venv/Scripts/python tools/supervisor/sprint_executor_validate.py {decl} --repair` | Run before autonomous-cycle |

## Governance Constraints

1. **No ad-hoc `src/` edits** — qname registry in `shared/`, backfill tools in `tools/backfill/`,
   validators in `tools/supervisor/`
2. **Expected validator count = 223** at line 131 of `governance_validator_runner.py`
   If V54 is new: update to 224; also add ext6 registration entry
3. **DO NOT repeat full chain audit** — prior run's 25 files are authoritative; write delta only
   (12 files for this run: 00-12 + evidence-declaration.yaml + evidence-bundle.zip)
4. **TC-SAL-ID-SCHEME-001 is NOT in this plan** — requires dedicated machinery sprint with its own plan
5. **Sprint closeout is best-effort** — autonomous_cycle.py non-zero → log and proceed
6. **SAL refresh BEFORE ODS/ODT fix** — correct fact IDs must exist before registry update
7. **New validators in ext6.py** (not ext5 — that's lively-leaping-elephant's file)

## Execution Order

TC-FHQA-000 → TC-FHQA-001 → **TC-FHQA-002** (SAL refresh) → **TC-FHQA-003** (ODS/ODT fix)
→ TC-FHQA-004 → TC-FHQA-005 → TC-FHQA-006 → TC-FHQA-007 → TC-FHQA-008

TC-FHQA-002 must precede TC-FHQA-003 (correct ODS fact IDs needed first).
All others are sequential. Update plan lock `last_taskcard` after each taskcard.

## Verification Checklist

- [ ] `active-plan-lock.json` → `status: IN_PROGRESS` for `effervescent-sprouting-marshmallow`
- [ ] `current-audit-run-id.txt` exists with `FF-HEAL-QNAME-{timestamp}`
- [ ] SAL refreshed — new `generated_at` timestamp after 2026-07-01
- [ ] ODS/ODT registry: zero remaining `FACT-FODS-*` cross-references in ods.yaml
- [ ] V187-V193 delta report written with PASS/WARN/ERROR per validator
- [ ] FODT irrecoverable failures documented with categories and dispositions
- [ ] `tools/backfill/qname_backfill_planner.py` exists and produces valid output
- [ ] V54 status documented (existing/new/deferred)
- [ ] pilot-fix-lle 5 fixes verified at HEAD with file:line evidence
- [ ] `evidence-declaration.yaml` validated by `sprint_executor_validate.py`
- [ ] `evidence-bundle.zip` exists; absolute path + SHA-256 printed
- [ ] `active-plan-lock.json` → `status: TERMINAL_CLOSED` after TC-FHQA-008
- [ ] `ran_count >= 223` confirmed in governance validator run

---

*Re-evaluated 2026-07-14: 7 prior runs complete, all 25 chain-audit files exist. Scope narrowed
from full re-audit (14 TCs, ~23 output files) to delta sprint (9 TCs, 12 output files) targeting
5 open deferred taskcards + V187-V193 delta + pilot-fix verification. TC-SAL-ID-SCHEME-001 remains
deferred to dedicated machinery sprint. Prior forensic healing log (20 findings, 2026-07-10) is
incorporated in the prior in-repo version of this plan.*


---

## Convergence Closure (Added by Convergence Controller 2026-07-15)

### TC-CLOSE-001 — Commit Sprint Changes + Update Master Plan
**Status:** CLOSED
**Added by:** convergence-loop-effervescent-sprouting-marshmallow (post-sprint audit L1-001, L1-002)
**Source issues:** L1-001 (uncommitted changes), L1-002 (master plan not updated)

**Required actions:**
1. `git add shared/qname-registry/ods.yaml shared/qname-registry/odt.yaml tools/backfill/qname_backfill_planner.py plans/.claude/effervescent-sprouting-marshmallow.md`
2. `git commit` with message describing FF-HEAL-QNAME Run #8 closure
3. Add Section 104 to `plans/master-plan.md` recording sprint results
4. Write convergence closure record

**Completion criteria:**
- `git log --oneline -1` shows commit with sprint-owned files
- `grep "Section 104" plans/master-plan.md` succeeds
- convergence-binding.json updated with close_task_result

**Evidence:**
- commit hash recorded in stage3 files
- master plan diff confirmed
- convergence closure record written

<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-15T05:23:57.066907+00:00"
  locked_by: "7adafdcbf11c"
  session_lock_file: ".local/supervisor/plan-locks/7adafdcbf11c-175e6fbb.json"
  convergence_closure_taskcard: TC-CLOSE-001
  convergence_state: .supervisor/state/convergence-loop-effervescent-sprouting-marshmallow/
-->

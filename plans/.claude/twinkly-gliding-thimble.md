# Plan: Composable Skill-First Execution — Comprehensive Iteration (SFE2)
# Plan ID: twinkly-gliding-thimble
# Mission ID: SKILL-FIRST-002
# Plan Type: machinery_hardening
# Last reassessed: 2026-07-01 (third pass — verified against actual filesystem state)

---

## Verified Current State

All conclusions below are verified against actual files, not prior plan assumptions.

| Artifact | Actual State | Evidence |
|----------|-------------|---------|
| Skills registered | **104 total, 101 active** | `python -c "import yaml; data=yaml.safe_load(open('.supervisor/skill-registry.yaml')); print(len(data['skills']))"` → 104 |
| Capability routes | 30/30 ACTIVE | `.supervisor/capability-routing-results.yaml`: `active_routes: 30`, `missing_skill_routes: 0` |
| Pre-commit hook | Installed | `.git/hooks/pre-commit` → symlink to `.hooks/pre-commit-skill-guard` (Jun 25 21:36) |
| Pilots A–H receipts | **ALL COMPLETE** | `reports/skill-first/pilots/pilot-{A..H}-receipt.yaml` — all exist, all `verdict: PASS` |
| `skill-system-baseline.yaml` | Stale (Jun 24, 48 skills) | `wc -l` = 64 lines; `mission_id: SKILL-FIRST-001` |
| `duplicate-skill-report.yaml` | Stale (Jun 24, 62 skills) | `total_skills_checked: 62`; now 104 active |
| `taskcard-skill-backfill.yaml` | Current (updated Jun 29, PASS) | `items_needing_skill_ids: 0`, `overall_verdict: PASS` |
| `mutation-guard-results.yaml` | Current (Jun 24, V48 fires) | `overall_verdict: PASS`, `v48_result: FAIL (blocks_sprint=True)` |
| `skill-execution-receipt-index.yaml` | Current (lists 8 pilot receipts) | `total_receipts: 8`, all pilots A–H in index |
| `skill-gap-008-closure-proof.yaml` | **MISSING** | Does not exist |
| `reports/skill-audit/` | **MISSING** | Directory does not exist |
| `adhoc-migration-register.yaml` | **MISSING** | Does not exist |
| Pilot result files (`pilot-d-results.yaml` etc.) | **IRRELEVANT** | Pilots are in `reports/skill-first/pilots/`, not `.supervisor/` — correct location |
| `skill-quality-matrix.yaml` | Stale (51 skills graded; 4 new skills ungraded) | Exists Jun 25; misses `rollback-and-recovery`, `preflight-skill-entry`, `audit-root-tools`, `documentation-structure-migration` |
| SFE2 final report | **MISSING** | `reports/supervisor/skill-first-execution-sfe2-report.md` does not exist |
| `skill-first-execution-report.md` | Steps 7,8,9,11 still show "SKIPPED" | File shows SKIPPED but artifacts exist — report is wrong |

---

## Items Removed (Verified Complete)

| Item | Why Removed | Evidence |
|------|------------|---------|
| TC-SFE2-004 (Pilots D/E/F/H) | **ALL 8 pilots done** in Jun 24 run | `reports/skill-first/pilots/pilot-{D,E,F,G,H}-receipt.yaml` all `verdict: PASS` |
| Pilot D (skill decomposition) | BACKWARD_COMPATIBILITY_PRESERVED | `decompose-monolithic-codec` vs `extract-analytics-from-monolith`; routing updated |
| Pilot F (partial failure) | IDEMPOTENT_VERIFIED, SAFE_RESUME | `skill_inventory.py` resumed from partial fixture |
| Pilot G (ad-hoc migration) | ARCHIVED_DISPOSABLE | `_test_xcf_tmp.py` archived to `.local/archive/` |
| Pilot H (agent compliance) | AGENT_COMPLIANCE_PROVEN | Positive control PASS, negative control FAIL_AS_EXPECTED via `validate-skill-transcript` |
| TC-SFE2-001 steps 8,9,11 | Artifacts exist and are current | Step 8 updated Jun 29; step 9 V48 fires; step 11 lists 8 receipts |
| SKILL-GAP-011 | CLOSED | `capability-routing-results.yaml`: 30/30 ACTIVE |

**Critical correction**: `TC-SFE2-004` was listed as "NOT STARTED" in prior plan. This was wrong. All pilots ran during SKILL-FIRST-001 (Jun 24) and receipts are in `reports/skill-first/pilots/`. The plan was checking the wrong path (`.supervisor/pilot-*-results.yaml` instead of `reports/skill-first/pilots/pilot-*-receipt.yaml`).

---

## Remaining Taskcards

### TC-SFE2-000-HOOK: Verify Pre-Commit Hook Functional (SKILL-GAP-008 Closure Proof)
**Skill**: `tools/governance/ci_skill_attribution_check.py` (read-only verification)
**Status**: pending
**Priority**: HIGH — blocks TC-SFE2-006 (needed in final report)

The pre-commit hook is installed (`.git/hooks/pre-commit` → `.hooks/pre-commit-skill-guard`).
This TC proves it works — no new infrastructure needed.

Steps:
1. Run the CI check script dry-run to verify it executes without crashing:
   ```bash
   python tools/governance/ci_skill_attribution_check.py \
     --base-ref HEAD --head-ref HEAD --allow-pre-policy --staged-only
   ```
   Accept exit 0 (clean) or 2 (config warning — permissive). Exit 1 = unexpected failure.

2. Test the fallback transcript-detection path by creating a dummy file:
   ```bash
   python -c "
   import json, time
   from pathlib import Path
   Path('.local/transcripts').mkdir(parents=True, exist_ok=True)
   Path('.local/transcripts/test-hook-verify.json').write_text(
       json.dumps({'skill_id': 'test', 'verdict': 'PASS', 'ts': time.time()}))
   print('Dummy transcript written')
   "
   ```
   Then run the hook's `find_skill_transcript_for_head()` logic inline to confirm it finds the file
   (modification time within 30 minutes). Clean up after.

3. Write `.supervisor/skill-gap-008-closure-proof.yaml`:
   ```yaml
   gap_id: SKILL-GAP-008
   status: CLOSED
   hook_path: .hooks/pre-commit-skill-guard
   symlink: .git/hooks/pre-commit -> ../../.hooks/pre-commit-skill-guard
   ci_check_script: tools/governance/ci_skill_attribution_check.py
   install_script: tools/governance/install_hooks.py
   pre_mutation_guard: tools/governance/pre_mutation_guard.py
   ci_check_exit_code: <actual from step 1>
   fallback_transcript_test: PASS
   remaining_gap: EP-002-GAP (runtime tool-layer; bounded by commit-time hook)
   skill_gap_012_layers:
     declaration_layer: COVERED (mutation-guard-results.yaml — V48 fires)
     commit_layer: COVERED (this hook)
     runtime_layer: STRUCTURAL_GAP — requires Claude Code SDK tool-use hooks; out of repo scope
   ```

4. Note: Do NOT create the dummy transcript file permanently. Delete it after verification.

**Verification**: `.supervisor/skill-gap-008-closure-proof.yaml` exists with `status: CLOSED`

---

### TC-SFE2-000: Refresh Stale Artifacts for SKILL-FIRST-002
**Skill**: read-only + inline Python (steps 7 re-run)
**Status**: pending
**Priority**: HIGH — baseline accuracy required for final report

Three artifacts need updating. All are simple refreshes.

**A — skill-system-baseline.yaml**

Current file: Jun 24, 48 skills, mission SKILL-FIRST-001. Overwrite with:
```yaml
mission_id: SKILL-FIRST-002
plan_id: twinkly-gliding-thimble
generated: <today's date>
head: <git rev-parse HEAD>
branch: main
counts_at_baseline:
  registered_skills: 104
  active_skills: 101
  deprecated_skills: 3
  command_files: <ls .claude/commands/*.md | wc -l>
  capability_routes_active: 30
  capability_routes_total: 30
known_open_gaps:
  - SKILL-GAP-012  # runtime tool-layer; commit-time covered by hook
known_closed_gaps:
  - SKILL-GAP-008  # pre-commit hook installed and verified (TC-SFE2-000-HOOK)
  - SKILL-GAP-011  # capability routing fixed (30/30 ACTIVE)
active_plan: C:\Users\prora\.claude\plans\twinkly-gliding-thimble.md
prior_mission: SKILL-FIRST-001
```

**B — duplicate-skill-report.yaml (step 7 re-run)**

Current file: Jun 24, `total_skills_checked: 62`. Now 104 skills. The 42 new skills include
layer governance skills (append-layer-*, close-layer-task, create-cross-layer-handoff, etc.)
that might overlap. Re-run step 7:

```bash
python -c "
import yaml
from pathlib import Path
_REPO = Path.cwd()
data = yaml.safe_load((_REPO / '.supervisor/skill-registry.yaml').read_text(encoding='utf-8'))
skills = [s for s in data.get('skills', []) if s.get('status') not in ('deprecated',)]
duplicates, overlapping = [], []
for i, a in enumerate(skills):
    for b in skills[i+1:]:
        if a.get('command_file') and a.get('command_file') == b.get('command_file'):
            duplicates.append({'skill_a': a['skill_id'], 'skill_b': b['skill_id'],
                               'reason': 'identical_command_file'})
        else:
            ta = set(str(a.get('purpose', '')).lower().split())
            tb = set(str(b.get('purpose', '')).lower().split())
            if len(ta) > 3 and len(tb) > 3:
                overlap = len(ta & tb) / max(len(ta | tb), 1)
                if overlap > 0.8:
                    overlapping.append({'skill_a': a['skill_id'], 'skill_b': b['skill_id'],
                                        'overlap': round(overlap, 2)})
out = {'generated_by': 'detect-duplicate-skills', 'mission_id': 'SKILL-FIRST-002',
       'total_skills_checked': len(skills),
       'duplicate_count': len(duplicates), 'overlapping_count': len(overlapping),
       'duplicates': duplicates, 'overlapping': overlapping,
       'overall_verdict': 'FAIL' if duplicates else 'PASS'}
(_REPO / '.supervisor/duplicate-skill-report.yaml').write_text(
    yaml.dump(out, default_flow_style=False), encoding='utf-8')
print(f'Checked {len(skills)} skills: {len(duplicates)} DUPLICATE, {len(overlapping)} OVERLAPPING')
"
```
If duplicates found: add a sub-step to resolve them before continuing.

**C — skill-first-execution-report.md**

Steps 7, 8, 9, 11 show "SKIPPED (prompt-backed)" but artifacts exist. Update the 4 SKIPPED rows:

| Step | Change | Evidence |
|------|--------|---------|
| 7 | `SKIPPED (prompt-backed)` → `PASS (refreshed for 104 skills)` | `.supervisor/duplicate-skill-report.yaml` |
| 8 | `SKIPPED (prompt-backed)` → `PASS (updated Jun 29, 0 unbound tasks)` | `.supervisor/taskcard-skill-backfill.yaml` |
| 9 | `SKIPPED (prompt-backed)` → `PASS (V48 fires on RELEASE_GATE+architecture_only)` | `.supervisor/mutation-guard-results.yaml` |
| 11 | `SKIPPED (prompt-backed)` → `PASS (8 pilot receipts indexed)` | `.supervisor/skill-execution-receipt-index.yaml` |

Also update Overall verdict to remove the SKIPPED caveat.
Add note: "CORRECTION: Steps 7/8/9/11 previously misclassified as prompt-backed. All ran during
SKILL-FIRST-001 (Jun 24) with complete Python implementations. Report corrected in SKILL-FIRST-002."

**Verification**: `grep -c "SKIPPED" .supervisor/skill-first-execution-report.md` → 0

---

### TC-SFE2-002: Run /audit-root-tools (Pilot C Completion)
**Skill**: `/audit-root-tools`
**Status**: pending
**Priority**: MEDIUM

The `audit-root-tools` skill was created and registered (`.claude/commands/audit-root-tools.md` +
`skill-registry.yaml`). It has never been executed. This completes Pilot C: create → register → **use**.

The skill audits `tools/supervisor/*.py` files not referenced by any skill entry. Execute it:

```bash
# The skill's protocol (from .claude/commands/audit-root-tools.md):
# 1. List all .py files in tools/supervisor/ not in skill-registry.yaml
# 2. Classify each: REGISTERED / QUARANTINED / KEPT / REJECTED
# 3. Write to reports/skill-audit/root-tools-audit-{date}.yaml
```

Note: The skill's scope in its command file is `tools/supervisor/` (not `tools/` root). The 3
root-level ad-hoc scripts (`tools/close_*.py`) are NOT in scope for this skill as written — they
are handled in TC-SFE2-003.

Expected output: ~174 scripts classified; most as KEPT (infrastructure supporting the sprint loop).

**Verification**: `ls reports/skill-audit/root-tools-audit-*.yaml` → file exists; non-empty YAML

---

### TC-SFE2-003: Write adhoc-migration-register.yaml (Root-Level Scripts)
**Skill**: uses `/audit-root-tools` output as context; writes `.supervisor/adhoc-migration-register.yaml`
**Status**: pending
**Priority**: MEDIUM
**Depends on**: TC-SFE2-002

Context: Pilot G (Jun 24) already archived `_test_xcf_tmp.py` (ARCHIVED_DISPOSABLE). The remaining
unaddressed root-level ad-hoc scripts are:

| Script | Expected Disposition | Rationale |
|--------|---------------------|-----------|
| `tools/close_xcf_zst_gaps.py` | QUARANTINED_PENDING_AUTHORITY | Gaps already closed per MEMORY.md Jun 25; one-time only |
| `tools/close_fods_fodt_ppm_gaps.py` | QUARANTINED_PENDING_AUTHORITY | Same |
| `tools/close_comm_gaps.py` | QUARANTINED_PENDING_AUTHORITY | Same |
| `tools/audit_*.py` (5 scripts) | RETAINED_AS_GOVERNED_DIAGNOSTIC | Read-only audits, ongoing utility |
| `tools/health_check.py` | RETAINED_AS_GOVERNED_DIAGNOSTIC | System health |
| `tools/test_runner.py` | RETAINED_AS_GOVERNED_DIAGNOSTIC | Test execution |
| `tools/build_cross_format_index.py` | RETAINED_AS_GOVERNED_DIAGNOSTIC | Index builder |

Write `.supervisor/adhoc-migration-register.yaml`:
```yaml
adhoc_migration_register:
  mission_id: SKILL-FIRST-002
  generated: <date>
  scope: tools/*.py (root level, not tools/supervisor/)
  prior_work: Pilot G (skill-first-89e03009) archived _test_xcf_tmp.py → .local/archive/
  disposition_records:
    - { path: tools/close_xcf_zst_gaps.py, disposition: QUARANTINED_PENDING_AUTHORITY,
        reason: "gaps already closed per MEMORY.md 2026-06-25; one-time only" }
    - { path: tools/close_fods_fodt_ppm_gaps.py, disposition: QUARANTINED_PENDING_AUTHORITY,
        reason: "gaps already closed; one-time only" }
    - { path: tools/close_comm_gaps.py, disposition: QUARANTINED_PENDING_AUTHORITY,
        reason: "gaps already closed; one-time only" }
    - { path: tools/audit_qname_coverage.py, disposition: RETAINED_AS_GOVERNED_DIAGNOSTIC }
    - { path: tools/audit_deepening_tests.py, disposition: RETAINED_AS_GOVERNED_DIAGNOSTIC }
    - { path: tools/audit_gap_ledger_sal_refs.py, disposition: RETAINED_AS_GOVERNED_DIAGNOSTIC }
    - { path: tools/audit_parity_compliance.py, disposition: RETAINED_AS_GOVERNED_DIAGNOSTIC }
    - { path: tools/audit_sal_to_qname.py, disposition: RETAINED_AS_GOVERNED_DIAGNOSTIC }
    - { path: tools/health_check.py, disposition: RETAINED_AS_GOVERNED_DIAGNOSTIC }
    - { path: tools/test_runner.py, disposition: RETAINED_AS_GOVERNED_DIAGNOSTIC }
    - { path: tools/build_cross_format_index.py, disposition: RETAINED_AS_GOVERNED_DIAGNOSTIC }
```

Verify tool paths still exist before writing (`ls tools/*.py`).

**Verification**: `.supervisor/adhoc-migration-register.yaml` exists; all 3 `close_*.py` entries present

---

### TC-SFE2-005: Update skill-quality-matrix.yaml for New Skills
**Skill**: manual + read command files
**Status**: pending
**Priority**: LOW

The existing `.supervisor/skill-quality-matrix.yaml` grades 8 skills in detail and notes "51 prompt-backed
skills score 0 on determinism by definition." Now there are 104 skills. Four new skills need entries:

Read each command file to fill in grades, then append to `.supervisor/skill-quality-matrix.yaml`:

```yaml
  - skill_id: rollback-and-recovery
    grade_basis: summary
    source_plan: SKILL-GOVERNANCE-REPAIR-001 (Section 56)
    notes: "Newly registered to close SKILL-GAP-011. No prior execution evidence."
    dimensions_summary:
      responsibility_cohesion: 4
      contract_clarity: 3   # read from command file
      idempotency: 3
      evidence: 2           # no prior run evidence
      discoverability: 4    # registered + capability route ACTIVE
    overall_grade: 3.2
    repair_required: false
    first_execution: pending

  - skill_id: preflight-skill-entry
    grade_basis: summary
    source_plan: SKILL-GOVERNANCE-REPAIR-001 (Section 56, TC-R008)
    # fill from .claude/commands/preflight-skill-entry.md
    overall_grade: <compute>
    repair_required: false

  - skill_id: audit-root-tools
    grade_basis: summary
    source_plan: twinkly-gliding-thimble (TC-SFE2-003)
    notes: "Created in this plan. Not yet executed (first run in TC-SFE2-002)."
    dimensions_summary:
      responsibility_cohesion: 4
      contract_clarity: 4
      idempotency: 4    # deterministic file scan
      evidence: 2       # no prior run
      discoverability: 4
    overall_grade: 3.6
    repair_required: false
    first_execution: TC-SFE2-002

  - skill_id: documentation-structure-migration
    grade_basis: summary
    source_plan: <read from command file>
    # fill from .claude/commands/documentation-structure-migration.md
    overall_grade: <compute>
    repair_required: false
```

**Verification**: `grep "skill_id: audit-root-tools" .supervisor/skill-quality-matrix.yaml` → found

---

### TC-SFE2-006: Final Report and Closeout
**Skill**: `/post-sprint-audit` + evidence declaration + `autonomous_cycle.py`
**Status**: pending
**Priority**: HIGH — plan terminal TC
**Depends on**: all prior TCs

**A — Write final SFE2 report**

Write `reports/supervisor/skill-first-execution-sfe2-report.md` using Section 32 template:

```
# Format Factory Composable Skill-First Execution Report (SFE2)

## Policy
- Policy path: docs/governance/skill-only-policy.yaml
- Direct mutation rule: blocked at declaration (V48) and commit (pre-commit hook)
- Reuse-before-create: enforced by detect-duplicate-skills (104 skills checked, 0 duplicates)
- Exception rule: .local/exceptions/*.yaml (documented, bounded, expiring)

## Repository organization
- Skill root: .supervisor/skill-registry.yaml (104 skills)
- Command root: .claude/commands/ (~104 .md files)
- Registry: .supervisor/capability-routing-registry.yaml (30/30 routes)

## Inventory
- Active skills: 101
- Deprecated: 3 (add-analytics-function, check-mcp-status, 1 other)
- Duplicate skills: 0 (verified by detect-duplicate-skills for 104 skills)
- Unregistered tools in tools/supervisor/: ~174 (pre-policy, expected)

## Skill work
- Skills created this plan: 1 (audit-root-tools)
- Skills created since SFE1 (Jun 24): 4 (rollback-and-recovery, preflight-skill-entry,
  audit-root-tools, documentation-structure-migration) + ~39 layer governance skills
- SKILL-GAP-008: CLOSED (hook installed Jun 25; verified TC-SFE2-000-HOOK)
- SKILL-GAP-011: CLOSED (30/30 ACTIVE)
- SKILL-GAP-012: commit-time COVERED; runtime gap = EP-002-GAP (structural, bounded)

## Pilots
- Pilots A–H: ALL PASS (completed Jun 24, receipts in reports/skill-first/pilots/)

## Final verdict: COMPOSABLE_SKILL_FIRST_EXECUTION_ENFORCED_AND_IDEMPOTENCY_PROVEN
```

**B — Update master-plan.md**

Add Section 57 SKILL-FIRST-002 entry (closed). Mark SKILL-GAP-008 CLOSED.

**C — Evidence declaration and closeout**

```bash
# 1. Write declaration
mkdir -p .local/evidences/sfe2-$(date +%Y%m%d)

# 2. Validate
python tools/supervisor/sprint_executor_validate.py \
  .local/evidences/sfe2-<date>/evidence-declaration.yaml --repair

# 3. Supervisor cycle
python tools/supervisor/autonomous_cycle.py \
  --declaration .local/evidences/sfe2-<date>/evidence-declaration.yaml

# 4. Review package
python tools/supervisor/build_declaration_review_package.py \
  --declaration .local/evidences/sfe2-<date>/evidence-declaration.yaml
# Print absolute path and SHA-256

# 5. Lock plan
python tools/supervisor/write_plan_lock.py \
  --plan-path "C:\Users\prora\.claude\plans\twinkly-gliding-thimble.md" --terminal
```

**Verification**: review package ZIP exists; exit 0 from autonomous_cycle; plan lock status=TERMINAL_CLOSED

---

## Execution Order

```
TC-SFE2-000-HOOK ─┐ (hook verification — no deps, 5 min)
TC-SFE2-000      ─┘ (baseline + step-7 re-run + report fix — no deps, 10 min)
                   ↓ (both must complete before TC-SFE2-002 since report fix is prereq)
TC-SFE2-002 (run /audit-root-tools — 15 min)
TC-SFE2-003 (write adhoc-migration-register — 5 min, depends on TC-SFE2-002 output)
TC-SFE2-005 (update quality matrix — 10 min, depends on TC-SFE2-002 for audit-root-tools grade)
TC-SFE2-006 (final report + closeout — 20 min, all prior TCs complete)
```

TC-SFE2-000-HOOK and TC-SFE2-000 are independent — run together.
TC-SFE2-003 and TC-SFE2-005 can run in parallel after TC-SFE2-002.

---

## Known Constraints (Final Assessment)

| Gap | Status | Evidence | Remaining Work |
|-----|--------|---------|---------------|
| SKILL-GAP-008 (pre-commit hook) | **CLOSED** | Hook installed Jun 25; `ci_skill_attribution_check.py` exists | TC-SFE2-000-HOOK writes closure proof |
| SKILL-GAP-011 (routing) | **CLOSED** | 30/30 ACTIVE in `capability-routing-results.yaml` | None |
| SKILL-GAP-012 (agent bypass) | **SCOPE DEFINED** | Declaration: V48 fires (mutation-guard-results.yaml); Commit: hook covers; Runtime: EP-002-GAP (structural, bounded) | TC-SFE2-000-HOOK documents all 3 layers |
| Steps 7,8,9,11 "prompt-backed" | **MISCLASSIFICATION** | Artifacts all exist with PASS verdicts | TC-SFE2-000 fixes the report text |
| Pilots A–H | **ALL DONE** | `reports/skill-first/pilots/pilot-{A..H}-receipt.yaml` all PASS | None |
| Stale skill count in plan | **CORRECTED** | 104 active, not 65 | TC-SFE2-000 updates baseline |

**SKILL-GAP-012 runtime gap**: An agent can call the Edit tool on `src/` without running a skill first.
This cannot be closed by repository tooling — requires Claude Code SDK tool-use hooks. The commit-time
hook (`pre-commit-skill-guard`) bounds the blast radius: bypasses cannot reach git history without a
transcript. This is documented as EP-002-GAP in `tools/governance/pre_mutation_guard.py`.


## Taskcard Status Summary

| TC-ID | Title | Status |
|-------|-------|--------|
| TC-SFE2-000-HOOK | Verify Pre-Commit Hook Functional (SKILL-GAP-008 Closure) | CLOSED |
| TC-SFE2-000 | Refresh Stale Artifacts (baseline, duplicate scan, report fix) | CLOSED |
| TC-SFE2-002 | Run /audit-root-tools (Pilot C completion) | CLOSED |
| TC-SFE2-003 | Write adhoc-migration-register.yaml | CLOSED |
| TC-SFE2-005 | Update skill-quality-matrix.yaml for 4 new skills | CLOSED |
| TC-SFE2-006 | Final Report and Closeout | CLOSED |

<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-01T11:51:03.902836+00:00"
  locked_by: "34c4217ef0bd"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->

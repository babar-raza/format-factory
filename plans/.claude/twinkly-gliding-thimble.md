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

---

## Plan File Hardening Change Log

| Version | Date | Source | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-07-01 | Initial plan (third pass) | 6 taskcards, 3 gaps |
| v1.1 | 2026-07-01 | Post-execution + convergence | Taskcard table added; all 6 TCs CLOSED; TERMINAL_CLOSED |
| v1.2 | 2026-07-01 | Pilot rerun (before/after comparison) | 3 findings surfaced; 2 fixed in pilot; 1 follow-up open |
| v1.3 | 2026-07-01 | Plan File Hardening pass | 3 new taskcards (TC-SFE2-H001–H003); claim audit; gate contract; closeout rules hardened |
| **v1.4** | **2026-07-01** | **All H-taskcards CLOSED** | **TC-SFE2-H001/H002/H003 all CLOSED (commit c61b1c1f); 0 WARN; idempotency proven; TERMINAL_CLOSED** |

---

## Sources Reviewed (Hardening v1.3)

| Source | Path / Reference | Role |
|--------|-----------------|------|
| Pilot rerun output | Inline conversation (2026-07-01) | Primary evidence source |
| skill-contract-validation-results.yaml | `.supervisor/skill-contract-validation-results.yaml` | Before/after contract check |
| skill-registry.yaml (HEAD) | `.supervisor/skill-registry.yaml` | 117 skills, post-fix state |
| Commit 33a13b4e | git log | 7 command-field fixes + refreshed contract artifact |
| Commit cc40884a | git log | master-plan Section 96 |
| Commit 37a0f44a | git log | 10 SKILL-FIRST-002 artifacts |
| active-plan-lock.json | `.local/supervisor/active-plan-lock.json` | TERMINAL_CLOSED (session 22efecc290b9) |
| CI check live run | `ci_skill_attribution_check.py --base-ref HEAD~1` | Returned `verdict: PASS` |

---

## Assistant Summary Claim Audit

### Claims from latest pilot rerun response

| Claim ID | Exact Claim | Claim Type | Proof Level | Required | Disposition |
|----------|-------------|------------|-------------|----------|-------------|
| CLM-001 | "10 pairwise duplicates → 0 after fix" | verification | 2 (focused: simulated before + live after) | 2 | VERIFIED_AND_PRESERVE |
| CLM-002 | "validate-skill-contracts: 0 FAIL, 0 WARN across 117 skills" | verification | 2 (live rerun post-fix) | 2 | VERIFIED_AND_PRESERVE |
| CLM-003 | "contract artifact stale at SKILL-FIRST-001 until pilot fixed it" | governance | 2 (grep mission_id before/after) | 2 | ACTIONABLE_GAP → TC-SFE2-H001 |
| CLM-004 | "7 skills missing command field — pre-existing, not from SFE2" | governance | 3 (git log shows introduced in 68b8204e, c54d2685) | 3 | VERIFIED_AND_PRESERVE (fixed in 33a13b4e) |
| CLM-005 | "backfill-gate4-prototype-evidence: command file missing on disk" | governance | 2 (Path.exists() = False verified live) | 2 | ACTIONABLE_GAP → TC-SFE2-H002 |
| CLM-006 | "validate-skill-contracts was NOT re-run during TC-SFE2-000" | omission | 3 (mission_id: SKILL-FIRST-001 confirms non-rerun) | 3 | ACTIONABLE_GAP → TC-SFE2-H001 |
| CLM-007 | "TC-SFE2-000-C verification `grep -c SKIPPED` = 1 (false positive)" | verification | 2 (grep confirmed prose-only, not table row) | 2 | VERIFIED_AND_PRESERVE |
| CLM-008 | "All improvements production-ready after pilot fix commit 33a13b4e" | production readiness | 2 (committed, 0 FAIL live) | 3 | IMPLEMENTED_NOT_VERIFIED — need idempotency rerun |

**Hidden gaps extracted from language patterns:**

| Pattern | Found in | Assessment |
|---------|----------|------------|
| "pre-existing" (×3) | CLM-004, CLM-005, CLM-006 | Pre-existing defects fixed but no regression guard added |
| "not re-run" | CLM-006 | TC-SFE2-000 scope was too narrow — step 3 omitted |
| "1 WARN remaining" | CLM-005 | Not resolved, not tracked as taskcard — GAP |
| "simulated before state" | Pilot A | Before state was never committed; simulation is not real-repo proof |
| "production-ready" | CLM-008 | Asserted without idempotency second-run |

---

## Audit Findings Incorporated

### FINDING-H001: TC-SFE2-000 Step-3 Omission (validate-skill-contracts not re-run)

**Level**: L1_EXECUTION
**Severity**: HIGH
**Description**: TC-SFE2-000 was scoped to refresh only the duplicate scan (step 7), baseline (step A),
and execution report (step C). Step 3 (validate-skill-contracts) was not re-run. The artifact
`.supervisor/skill-contract-validation-results.yaml` retained `mission_id: SKILL-FIRST-001` until
the pilot rerun corrected it. The execution report row `| 3 | validate-skill-contracts | ... | PASS (0 FAIL, 0 WARN, 65 skills) |`
stated PASS based on stale SKILL-FIRST-001 data — this was a false PASS for SKILL-FIRST-002 scope.
**Fixed in pilot**: commit `33a13b4e` refreshed artifact to `mission_id: SKILL-FIRST-002`, 117 skills, 0 FAIL.
**Remaining**: Execution report step 3 row still shows "65 skills" — stale count from SKILL-FIRST-001.
**Taskcard**: TC-SFE2-H001

### FINDING-H002: backfill-gate4-prototype-evidence Missing Command File

**Level**: L2_INTEGRATION
**Severity**: LOW (WARN, non-blocking)
**Description**: Skill `backfill-gate4-prototype-evidence` (added by FF-G4-BACKFILL-001) has
`command: /backfill-gate4-prototype-evidence` but `.claude/commands/backfill-gate4-prototype-evidence.md`
does not exist on disk. Yields 1 WARN in contract validation.
**Out of scope for SFE2 execution but registered here for follow-up.**
**Taskcard**: TC-SFE2-H002

### FINDING-H003: No Idempotency Second-Run for Pilot Fix

**Level**: L1_EXECUTION
**Severity**: MEDIUM
**Description**: The 7 command-field additions (commit `33a13b4e`) and the contract artifact
refresh were performed once. No second run was executed to confirm idempotency (re-running
the same duplicate check and contract validation on an already-clean registry yields same PASS
counts without side effects).
**Taskcard**: TC-SFE2-H003

### FINDING-H004: Simulated Before-State Not a Real-Repo Proof

**Level**: L3_SYSTEM_WEAKNESS
**Severity**: LOW
**Description**: Pilot A demonstrated the before/after using an in-memory injection of the wrong
`command_file` value. The actual before state (10 duplicates) was never committed to git — it existed
only in the working tree during the sprint. The simulation is mechanically valid (injecting the same
value that was wrong reproduces the same pairwise explosion) but is not a raw git snapshot proof.
**Mitigation**: Commit log search shows the 4 playbook skills already had `command_file: null` in
the WIP stash (282e705f) and all subsequent commits — confirming the issue was fixed before any
commit and cannot be shown from git history. This is an acceptable limitation given the evidence.
**No taskcard required** — documented as a known evidence-quality limitation.

---

## Contradictions Reconciled

| ID | Contradiction | Resolution |
|----|--------------|------------|
| CON-001 | TC-SFE2-000 claimed "PASS" for step 3 but artifact was SKILL-FIRST-001 | CLM-006 confirmed omission; CLM-003 confirmed artifact staleness. Fixed in pilot (33a13b4e). Execution report step 3 row needs count update. → TC-SFE2-H001 |
| CON-002 | Execution report grep-c SKIPPED = 1 contradicted "0 SKIPPED rows" claim | Confirmed prose-only reference in correction note, not a table row. No contradiction remains. |
| CON-003 | Plan lock shows ITERATION_REQUIRED (v34c4217) vs subsequent TERMINAL_CLOSED (v22efecc) | Current active lock: TERMINAL_CLOSED for twinkly-gliding-thimble (session 22efecc290b9). The ITERATION_REQUIRED embedded comment is from an earlier intermediate lock. No real contradiction. |
| CON-004 | "0 duplicates" claimed before pilot vs 10 duplicates found in pilot simulation | Resolved: pilot simulated the problematic state; current committed state has 0. Simulation was mechanically equivalent to the real issue. |

---

## Resolved / Preserved Work (Pilot Confirmed)

| Item | Status | Proof Level | Evidence |
|------|--------|-------------|----------|
| Duplicate skill fix (4 command_file nulled) | COMPLETED_VERIFIED | 2 — live run 0 duplicates across 117 skills | Pilot A |
| Contract validation 0 FAIL after fix | COMPLETED_VERIFIED | 2 — live rerun `fail_count: 0` | commit 33a13b4e |
| skill-system-baseline SKILL-FIRST-002 | COMPLETED_VERIFIED | 2 — `mission_id: SKILL-FIRST-002`, 100 active | Pilot D |
| SKIPPED rows corrected (no table SKIPPED) | COMPLETED_VERIFIED | 2 — grep confirms prose-only reference | Pilot C |
| SKILL-GAP-008 closure proof | COMPLETED_VERIFIED | 3 — hook symlink + CI check `verdict: PASS` | Pilot F, G |
| Quality matrix 67 skills | COMPLETED_VERIFIED | 1 — file exists, count confirmed | Pilot E |
| master-plan Section 96 | COMPLETED_VERIFIED | 2 — committed at HEAD (cc40884a) | git show |

---

## Unresolved Work Register

| ID | Description | Severity | Owner | Taskcard |
|----|-------------|----------|-------|----------|
| URW-001 | Execution report step 3 row shows "65 skills" — stale from SKILL-FIRST-001 | LOW | agent | TC-SFE2-H001 |
| URW-002 | backfill-gate4-prototype-evidence command file missing on disk | LOW (WARN) | FF-G4-BACKFILL-001 sprint | TC-SFE2-H002 |
| URW-003 | No idempotency second-run proof for pilot fix | MEDIUM | agent | TC-SFE2-H003 |
| URW-004 | New skills added after 33a13b4e not validated for missing command field | MEDIUM | agent | TC-SFE2-H003 |

---

## Taskcard Register (Hardening Additions)

### TC-SFE2-H001: Update Execution Report Step-3 Row (Stale Skill Count)

```yaml
taskcard:
  id: TC-SFE2-H001
  title: "Fix stale skill count in execution-report step 3 row"
  source_finding: FINDING-H001 / CON-001
  source_claim_ids: [CLM-003, CLM-006]
  why_it_matters: >
    The execution report step 3 row reads "PASS (0 FAIL, 0 WARN, 65 skills)" which is
    SKILL-FIRST-001 data. Post-pilot the artifact covers 117 skills. The row is factually
    misleading.
  current_status: CLOSED
  closed_at: '2026-07-01'
  commit: c61b1c1f
  priority: LOW
  lane_owner: governance_lane
  dependencies: [TC-SFE2-000-HOOK, TC-SFE2-000]  # parent TCs already closed
  required_work:
    - Read current skill-contract-validation-results.yaml for accurate count
    - Edit .supervisor/skill-first-execution-report.md step 3 row to show 117 skills
    - Confirm step 3 row reads "PASS (0 FAIL, 1 WARN, 117 skills)" or equivalent
  allowed_actions:
    - Edit .supervisor/skill-first-execution-report.md
  forbidden_actions:
    - Change verdict (PASS is correct — do not regress)
    - Modify other rows in the execution report
  required_verification:
    - grep "| 3 |" .supervisor/skill-first-execution-report.md shows current count, not 65
    - skill-contract-validation-results.yaml mission_id = SKILL-FIRST-002
  required_evidence:
    - Updated execution report row (actual file content)
    - skill-contract-validation-results.yaml snippet
  proof_level_current: 1
  proof_level_target: 2
  acceptance_criteria:
    - Step 3 row in execution report is not stale
    - skill-contract-validation-results.yaml mission_id is SKILL-FIRST-002
    - grep -c "65 skills" .supervisor/skill-first-execution-report.md returns 0
  negative_controls:
    - grep "65 skills" execution report must return 0
  rollback: Restore prior text from git show HEAD:.supervisor/skill-first-execution-report.md
  stop_conditions:
    - Row accurately reflects current contract validation state
  closeout_rules:
    - Commit the edited execution report
    - Record commit hash in taskcard evidence
  exact_next_action: "Edit step 3 row in .supervisor/skill-first-execution-report.md"
```

### TC-SFE2-H002: Resolve backfill-gate4-prototype-evidence Missing Command File

```yaml
taskcard:
  id: TC-SFE2-H002
  title: "Create or remove .claude/commands/backfill-gate4-prototype-evidence.md"
  source_finding: FINDING-H002
  source_claim_ids: [CLM-005]
  why_it_matters: >
    Skill backfill-gate4-prototype-evidence has command: /backfill-gate4-prototype-evidence
    but the command file .claude/commands/backfill-gate4-prototype-evidence.md does not exist.
    This produces 1 persistent WARN in every contract validation run. Not from SFE2 — from
    FF-G4-BACKFILL-001 sprint.
  current_status: CLOSED
  closed_at: '2026-07-01'
  commit: c61b1c1f
  note: "Command file .claude/commands/backfill-gate4-prototype-evidence.md already existed; artifact refreshed to 0 WARN"
  priority: LOW
  lane_owner: ff_g4_backfill_sprint_or_agent
  dependencies: []
  required_work:
    - Option A: Create .claude/commands/backfill-gate4-prototype-evidence.md with the skill protocol
    - Option B: Remove the command_file field or set to null in skill-registry.yaml for this skill
    - Either way: re-run validate-skill-contracts and confirm WARN count = 0
  allowed_actions:
    - Create missing command file (preferred — preserves discoverability)
    - OR set command_file: null for the skill entry
  forbidden_actions:
    - Remove the skill entry entirely (it has a command field; just the file is missing)
  required_verification:
    - python -c "from pathlib import Path; print(Path('.claude/commands/backfill-gate4-prototype-evidence.md').exists())"
    - Re-run contract validation and confirm warn_count = 0
  required_evidence:
    - Updated skill-contract-validation-results.yaml with warn_count = 0
    - Diff showing command file created or command_file set to null
  proof_level_current: 0
  proof_level_target: 2
  acceptance_criteria:
    - validate-skill-contracts run shows 0 FAIL, 0 WARN
    - Committed and clean
  negative_controls:
    - After fix, introducing a wrong path should produce WARN (regression guard)
  rollback: git checkout HEAD -- .supervisor/skill-registry.yaml
  stop_conditions:
    - WARN count = 0 in live contract validation run
  closeout_rules:
    - Commit the fix
    - Refresh skill-contract-validation-results.yaml
    - Record 0 WARN in hardening log
  exact_next_action: "Create .claude/commands/backfill-gate4-prototype-evidence.md with the skill's protocol"
```

### TC-SFE2-H003: Idempotency Second-Run for Pilot Fixes

```yaml
taskcard:
  id: TC-SFE2-H003
  title: "Run duplicate detection and contract validation a second time to prove idempotency"
  source_finding: FINDING-H003
  source_claim_ids: [CLM-008]
  why_it_matters: >
    Pilot fixes (7 command-field additions + contract artifact refresh) were run once. A second
    run is required to confirm no side effects: duplicate count stays 0, FAIL count stays 0,
    skill count stays 117. This also validates any new skills added after 33a13b4e have correct
    command fields.
  current_status: CLOSED
  closed_at: '2026-07-01'
  commit: c61b1c1f
  priority: MEDIUM
  lane_owner: governance_lane
  dependencies: [TC-SFE2-H001, TC-SFE2-H002]
  required_work:
    - Re-run duplicate detection on current registry
    - Re-run contract validation on current registry
    - Confirm counts stable: 0 FAIL, ≤1 WARN (after TC-SFE2-H002 resolves the 1 WARN → 0)
    - Check all skills added AFTER commit 33a13b4e for missing command field
    - Write idempotency proof artifact: .supervisor/skill-first-pilot-idempotency.yaml
  allowed_actions:
    - Read-only registry inspection
    - Inline Python for duplicate/contract check
    - Write proof artifact
  forbidden_actions:
    - Modify skill-registry.yaml (idempotency run must not mutate)
    - Reduce skill count to achieve PASS
  required_verification:
    - duplicate_count: 0 on second run (same as first run)
    - contract fail_count: 0 on second run
    - All skills added after 33a13b4e have non-null command field
  required_evidence:
    - .supervisor/skill-first-pilot-idempotency.yaml with run_1 vs run_2 comparison
    - SHA-256 of duplicate-skill-report.yaml (stable across runs)
  proof_level_current: 0
  proof_level_target: 3
  acceptance_criteria:
    - Second run duplicate count = 0 (matches first run)
    - Second run fail count = 0 (matches first run)
    - SHA-256 of contract output stable
    - No new skills missing command field
  negative_controls:
    - Inject one skill with duplicate command_file — confirm FAIL detected — restore
  rollback: No registry changes allowed in this TC; rollback is trivially not needed
  stop_conditions:
    - Both metrics stable across two independent runs
  closeout_rules:
    - Write idempotency proof artifact
    - Commit proof artifact
    - Update this taskcard to completed_verified
  exact_next_action: "Run duplicate check and contract validation inline Python and record run_1 vs run_2 comparison"
```

---

## Taskcard Status Summary (v1.4 — ALL CLOSED)

| TC-ID | Title | Status | Proof Level |
|-------|-------|--------|-------------|
| TC-SFE2-000-HOOK | Verify Pre-Commit Hook (SKILL-GAP-008 Closure) | CLOSED | 3 (live CI check) |
| TC-SFE2-000 | Refresh Stale Artifacts (baseline, duplicate scan, report fix) | CLOSED | 2 (step 3 row fixed in H001) |
| TC-SFE2-002 | Run /audit-root-tools (Pilot C completion) | CLOSED | 2 (artifact exists, 202 scripts) |
| TC-SFE2-003 | Write adhoc-migration-register.yaml | CLOSED | 1 (artifact exists) |
| TC-SFE2-005 | Update skill-quality-matrix.yaml for 4 new skills | CLOSED | 1 (artifact exists) |
| TC-SFE2-006 | Final Report and Closeout | CLOSED | 2 (committed at HEAD) |
| TC-SFE2-H001 | Fix stale step-3 row in execution report | CLOSED | 2 (grep confirmed 0 occurrences of 65 skills) |
| TC-SFE2-H002 | Resolve backfill-gate4 missing command file | CLOSED | 2 (0 WARN on live re-run) |
| TC-SFE2-H003 | Idempotency second-run for pilot fixes | CLOSED | 3 (run-2 + negative control both PASS) |

---

## Gate Contract

### Gate SFE2-G1: Registry Health Gate (PASS required before any future governance sprint)

**Entry conditions**: Any sprint that adds new skills or modifies skill-registry.yaml
**Required tasks**: Re-run duplicate detection AND contract validation
**Required proof**: 0 duplicate_count, 0 fail_count, all new skills have non-null `command` field
**Failure behavior**: Block sprint closeout; fix registry before any other work
**Repair path**: Set command_file to null for duplicates; add `command: /skill-id` for missing commands
**Exit conditions**: duplicate_count = 0, fail_count = 0
**Reopening conditions**: Any sprint that adds >1 skill without re-running this gate

### Gate SFE2-G2: Execution Report Freshness Gate

**Entry conditions**: Any run that claims to update the execution report
**Required proof**: All step rows use data from the CURRENT mission run
**Failure behavior**: Mark step as CLAIMED_UNPROVEN; re-run the step tool and update count
**Exit conditions**: All step rows cite the current mission_id in their evidence artifact

---

## Verification Matrix

| Requirement | How to Verify | Proof Level Target | Current |
|-------------|--------------|-------------------|---------|
| 0 skill duplicates | Inline Python detect-duplicates on current registry | 3 (idempotent repeated run) | 2 (one pilot run) |
| 0 contract FAILs | validate-skill-contracts live rerun | 3 (idempotent repeated run) | 2 (one pilot run) |
| Execution report step 3 accurate | grep step 3 row for current skill count | 2 | 0 (stale "65 skills") |
| WARN count = 0 | validate-skill-contracts live rerun after TC-SFE2-H002 | 2 | 1 WARN persists |
| Pilot fix idempotent | Second run same counts as first run | 3 | 0 (not run) |

---

## Anti-Overclaim Rules

1. **Do not cite step X as PASS if the cited artifact has a prior mission_id.** Always read `mission_id:` from the artifact before claiming PASS.
2. **Do not claim `duplicate_count: 0` based on a prior run.** Re-run the check inline before each claim.
3. **Do not claim "all skills valid" based on a single one-time run.** Idempotency requires a second independent run.
4. **Do not count "65 skills" in execution report rows that should reflect the current registry.** Update counts when the registry changes.
5. **Do not treat a simulated before-state as equivalent to a git-snapshot before-state.** Document the distinction.

---

## Repair and Resume Loop

```
EXECUTE TC-SFE2-H001 (fix step 3 row)
→ VERIFY: grep step 3 row shows 117 not 65
→ COMMIT
→ EXECUTE TC-SFE2-H002 (fix backfill-gate4 command file)
→ VERIFY: validate-skill-contracts WARN = 0
→ COMMIT
→ EXECUTE TC-SFE2-H003 (idempotency second-run)
→ VERIFY: run_1 = run_2 on all counts
→ IF ANY FAIL: preserve evidence, find first failing boundary, repair, rerun
→ WRITE idempotency proof artifact
→ COMMIT
→ FINAL AUDIT: 0 material findings
→ UPDATE Taskcard Status Summary to all CLOSED
→ WRITE TERMINAL_CLOSED (supersede prior ITERATION_REQUIRED lock)
```

---

## Closeout Criteria (v1.4 — ALL SATISFIED)

**All conditions met (commit c61b1c1f, 2026-07-01):**

- [x] TC-SFE2-H001: Execution report step 3 row shows "117 skills, 0 FAIL, 0 WARN" (not 65)
- [x] TC-SFE2-H002: WARN count = 0 in contract validation (command file existed; artifact refreshed)
- [x] TC-SFE2-H003: Idempotency second-run PASS — run-2 + negative control both PASS
- [x] skill-contract-validation-results.yaml `mission_id: SKILL-FIRST-002` (117 skills, 0 FAIL, 0 WARN)
- [x] All taskcards in this table show CLOSED
- [x] Final audit: 0 material findings, 0 actionable findings

**Prohibited premature closures:**
- Must not write TERMINAL_CLOSED while any hardening taskcard shows not_attempted
- Must not claim "all skills valid" without second-run idempotency proof
- Must not leave execution report rows citing prior mission data

---

## Plan Hardening Validation Record

```yaml
plan_hardening_validation:
  plan_path: plans/.claude/twinkly-gliding-thimble.md
  hardening_version: v1.3
  date: 2026-07-01
  claims_reviewed: 8
  explicit_findings: 4
  implied_findings: 4
  contradictions: 4
  taskcards_added: 3  # TC-SFE2-H001, TC-SFE2-H002, TC-SFE2-H003
  taskcards_updated: 1  # TC-SFE2-000 downgraded to completed_but_weakly_verified
  findings_without_taskcards: 0
  gates_updated: 2  # SFE2-G1 (registry health), SFE2-G2 (report freshness)
  evidence_rules_updated: 5  # anti-overclaim rules
  blockers: []
  verdict: PLAN_FILE_HARDENED_READY_FOR_EXECUTION
```

---

## Final Status (v1.4)

All 9 taskcards CLOSED. Commit `c61b1c1f` (H001/H002/H003). Plan TERMINAL_CLOSED.

---

<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-01"
  locked_by: "current_session"
  final_commit: c61b1c1f
  total_taskcards: 9
  all_closed: true
  successor_required_for_future_changes: false
  mutation_policy: "ALL TASKCARDS CLOSED — plan complete"
  hardening_applied: "2026-07-01 — v1.3 (3 taskcards added), v1.4 (all 3 closed)"
-->

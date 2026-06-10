# Required Plan Repairs
# Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-PLAN-REPAIR-FOR-SINGLE-GO-EXECUTION-001
# Run: spec-authority-plan-repair-20260607-e382e5f
# Date: 2026-06-07

---

## REPAIR-001: State Count Fix

**Issue:** Plan narrative says "29 states" but state list contains 32 distinct states.

**Repair action:** Update all markdown references to say "32 states". Generate JSON with exactly 32 state entries. Validate programmatically.

**Files to modify:** repaired-plan.md, authority-healing-state-machine.md, authority-healing-state-machine.json

**Validation command:**
```bash
python -c "import json; sm=json.load(open('authority-healing-state-machine.json')); n=len(sm['states']); print(f'State count: {n}'); assert n==32, f'Expected 32, got {n}'"
```

**Status: APPLIED in this sprint**

---

## REPAIR-002: Dynamic Path Replacement

**Issue:** Prior plan versions contain hardcoded `C:\Users\prora\...` paths. All paths must be computed dynamically from `git rev-parse --show-toplevel`.

**Repair action:** Replace all occurrences of `C:\Users\prora\OneDrive\Documents\GitHub\format-factory` with `${REPO_ROOT}` in repaired-plan.md. Evidence bundle paths use computed RUN_ID.

**Files to modify:** repaired-plan.md, single-go-execution-prompt.md

**Validation command:**
```bash
grep -c "C:\\\\Users" repaired-plan.md  # must return 0
```

**Status: APPLIED in this sprint**

---

## REPAIR-002A: Normalization Output Path Correction (new — from evidence-import-review)

**Issue:** Investigation sprint referenced `.local/spec-normalize/fods/1.3/` but actual normalization output is at `.local/spec-cache/fods/1.3/normalized/`.

**Repair action:** TCA-011 and all healing steps use `.local/spec-cache/fods/1.3/normalized/text.txt` as the actual normalized text path. Update success criteria to check this path.

**Files to modify:** repaired-plan.md, authority-healing-taskcards.json (TCA-011)

**Validation command:**
```bash
test -f .local/spec-cache/fods/1.3/normalized/text.txt && echo PASS || echo FAIL
```

**Status: APPLIED in this sprint**

---

## REPAIR-003: Human Approval Model Fix

**Issue:** Prior plan used `validated_by: human` as default for agent-performable verification. `verified-facts.yaml` has 10 facts set to "verified" by automated tool with no validated_by field at all.

**Repair action:**
- Agent-verifiable facts: `validated_by: independent_agent_verifier`
- Human review only for: git push/commit, Gate 11 approval, package publication, legal/credential decisions
- TCA-010 adds explicit sub-step: downgrade existing auto-verified facts to `verification_status: needs_review` pending proper validation pass
- Never write `validated_by: Babar Raza` unless Babar actually reviewed

**Explicit list of human-approval-required decisions in this repo:**
1. `git push` / `git commit` — requires explicit user authorization
2. Gate 11 (G11-G) commercial readiness — requires Babar Raza
3. Package publication (NuGet, PyPI) — requires explicit user authorization
4. MCP activation changes — requires explicit user authorization

**Files to modify:** repaired-plan.md, authority-healing-taskcards.json (TCA-010)

**Validation command:**
```bash
grep -n "validated_by.*human" repaired-plan.md | grep -v "human_approval_required_reason" | wc -l  # must be 0
```

**Status: APPLIED in this sprint**

---

## REPAIR-004: TCA-000 State Fix

**Issue:** TCA-000 was conceptually pre-marked complete in prior plan context. During this sprint, TCA-000 is IMPLEMENTING — it closes only when validator passes.

**Repair action:** taskcard-state.json initializes TCA-000 as `IMPLEMENTING`. TCA-000 transitions to CLOSED_VERIFIED only after validate_repaired_plan.py exits 0.

**Files to modify:** taskcard-state.json, taskcard-transition-ledger.jsonl

**Validation command:**
```bash
python -c "import json; ts=json.load(open('taskcard-state.json')); assert ts['TCA-000']['state'] in ('IMPLEMENTING','IMPLEMENTED','VALIDATING'), f'Bad: {ts[\"TCA-000\"]}'"
```

**Status: APPLIED in this sprint**

---

## REPAIR-005: Swarm Lane Model

**Issue:** Prior plan had no lane assignments on taskcards, creating potential for conflicting writes.

**Repair action:** Add 9-lane model (see lane-ownership-map.md/json). Every taskcard has owner_lane assigned. Lane ownership map has no conflicting exclusive write claims.

**Files to modify:** repaired-plan.md, authority-healing-taskcards.json (add lane field to every taskcard), lane-ownership-map.md, lane-ownership-map.json

**Validation command:**
```bash
python validate_repaired_plan.py --run-dir . --check lane-ownership
```

**Status: APPLIED in this sprint**

---

## REPAIR-006: Rollback Section

**Issue:** No rollback plan in prior plan.

**Repair action:** Add rollback-recovery-plan.md + .json covering 12 failure modes (see Phase 9 of plan). Every taskcard has rollback_plan field populated.

**Files to modify:** rollback-recovery-plan.md, rollback-recovery-plan.json, authority-healing-taskcards.json (add rollback_plan to each)

**Validation command:**
```bash
python -m json.tool rollback-recovery-plan.json
python -c "import json; rp=json.load(open('rollback-recovery-plan.json')); assert len(rp['failure_modes'])>=12"
```

**Status: APPLIED in this sprint**

---

## REPAIR-007: spec_fact_refs BLOCKING Enforcement

**Issue:** Prior next-healing-sprint-prompt WI-5 said "warn (not error)" for spec_fact_refs. This is insufficient — new product work must be BLOCKED if spec_fact_refs is empty.

**Repair action:**
- spec_fact_refs is BLOCKING for work item types: PRODUCT_SOURCE, TEST, REQUIREMENT, READINESS, RELEASE_GATE
- spec_fact_refs is EXEMPT (with explicit exception_classification) for:
  - investigation_only: pure investigation/audit work
  - sample_only_non_product: sample files with no production code
  - legacy_backfill: pre-existing code being documented retroactively
  - fallback_authority_approved: explicitly approved fallback by governance
  - no_public_spec_available: no publicly accessible spec document exists
- All exceptions require explicit `exception_classification` field — no silent bypass

**Files to modify:** repaired-plan.md (standing constraint with citation to GAP-004), authority-healing-taskcards.json (TCA-002)

**Validation command:**
```bash
grep -c "warning\|warn only\|warn-only" repaired-plan.md  # count near spec_fact_refs must be 0
```

**Status: APPLIED in this sprint**

---

## REPAIR-008: Bypass Pilot Scope

**Issue:** Prior plan focused only on FODS. The bypass/downgrade pilot for formats without spec PDFs (Gnumeric, ABW) was not defined.

**Repair action:**
- TCA-012 (bypass pilot for Gnumeric/ABW) explicitly states: does NOT implement new product code
- TCA-012 non_goals: ["new_product_implementation", "new_test_files", "src_changes"]
- TCA-012 scope: metadata-only — populate exception_classification fields in existing evidence declarations
- If spec cache absent for Gnumeric/ABW: transition to BLOCKED_METADATA_ONLY_SPEC; sprint continues other taskcards

**Files to modify:** repaired-plan.md, authority-healing-taskcards.json (TCA-012)

**Validation command:**
```bash
python -c "import json; tcs=json.load(open('authority-healing-taskcards.json')); tca012=[t for t in tcs['taskcards'] if t['taskcard_id']=='TCA-012'][0]; assert 'new_product_implementation' in tca012['non_goals']"
```

**Status: APPLIED in this sprint**

---

## REPAIR-009: FODS PDF Availability

**Issue:** Plan must handle FODS PDF missing without crashing. PDF expected SHA-256 must be derived from spec-index.yaml, not hardcoded.

**Repair action:**
- TCA-011 checks PDF existence first; transitions to BLOCKED_MISSING_SPEC if absent
- SHA-256 is read from `.local/spec-cache/fods/1.3/spec-index.yaml` at runtime
- Sprint continues with TCA-002, TCA-003, TCA-012 if TCA-011 is blocked

**Live check result:** FODS PDF EXISTS (24270588 bytes). SHA-256 confirmed. TCA-011 will NOT be blocked.

**Files to modify:** authority-healing-taskcards.json (TCA-011 state_transition_rules)

**Validation command:**
```bash
python -c "import json; tcs=json.load(open('authority-healing-taskcards.json')); tca011=[t for t in tcs['taskcards'] if t['taskcard_id']=='TCA-011'][0]; sttr=tca011['state_transition_rules']; print('BLOCKED_MISSING_SPEC' in str(sttr))"
```

**Status: APPLIED in this sprint**

---

## REPAIR-010: CI and Hooks Discovery

**Issue:** No CI/hooks section in prior plan.

**Repair action:**
- Confirmed: no .github/workflows/, no .husky/, no hooks/
- All verification gates marked ci_available=false
- Plan notes: tests runnable locally only; no CI enforcement available

**Files to modify:** verification-gates.json (ci_available=false for all), repaired-plan.md

**Validation command:**
```bash
python -c "import json; vg=json.load(open('verification-gates.json')); assert all(g.get('ci_available')==False for g in vg['gates'])"
```

**Status: APPLIED in this sprint**

---

## All Repairs Summary

| Repair | Issue(s) Addressed | Status |
|--------|---------------------|--------|
| REPAIR-001 | ISSUE-001 (state count 29→32) | APPLIED |
| REPAIR-002 | ISSUE-009 (hardcoded paths) | APPLIED |
| REPAIR-002A | NEW (normalization path correction) | APPLIED |
| REPAIR-003 | ISSUE-005 (validated_by:human) | APPLIED |
| REPAIR-004 | ISSUE-003 (TCA-000 state) | APPLIED |
| REPAIR-005 | ISSUE-006 (no lane model) | APPLIED |
| REPAIR-006 | ISSUE-008 (no rollback plan) | APPLIED |
| REPAIR-007 | ISSUE-004 (spec_fact_refs warn-only) | APPLIED |
| REPAIR-008 | no bypass pilot for non-FODS | APPLIED |
| REPAIR-009 | FODS PDF availability | APPLIED |
| REPAIR-010 | ISSUE-007 (no validator) | APPLIED |

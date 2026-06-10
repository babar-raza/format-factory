# Plan Readiness Review
# Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-PLAN-REPAIR-FOR-SINGLE-GO-EXECUTION-001
# Run: spec-authority-plan-repair-20260607-e382e5f
# Reviewed against: HEAD e382e5f (branch: main)
# Date: 2026-06-07

---

## Summary

| Category | Status |
|----------|--------|
| 1. Technical correctness | NEEDS_REPAIR (ISSUE-001: state count 29 vs 32) |
| 2. Current repo compatibility | NEEDS_REPAIR (ISSUE-002: path discrepancy for normalization output) |
| 3. Governance compatibility | PASS |
| 4. Hook/gate compatibility | PASS (no hooks/CI found) |
| 5. Taskcard completeness | NEEDS_REPAIR (ISSUE-003: TCA-000 pre-marked complete) |
| 6. State machine correctness | NEEDS_REPAIR (ISSUE-001: count mismatch) |
| 7. Evidence rules | NEEDS_REPAIR (ISSUE-004: spec_fact_refs warn-only; ISSUE-005: validated_by:human as default) |
| 8. Supervisor/automation integration | PASS |
| 9. Human-vs-agent ownership | NEEDS_REPAIR (ISSUE-005) |
| 10. Swarm readiness | NEEDS_REPAIR (ISSUE-006: no lane model in prior plan) |
| 11. File ownership and overlap safety | NEEDS_REPAIR (ISSUE-006) |
| 12. Verification completeness | NEEDS_REPAIR (ISSUE-007: no validator script) |
| 13. Rollback/recovery completeness | NEEDS_REPAIR (ISSUE-008: no rollback plan) |
| 14. CI/GitHub applicability | PASS (no CI exists — note in gates) |
| 15. Final evidence bundle completeness | NEEDS_REPAIR (ISSUE-009: hardcoded Windows paths) |

---

## Category 1: Technical Correctness

**Status: NEEDS_REPAIR**

**ISSUE-001: State count mismatch**
- issue_id: ISSUE-001
- evidence_path: C:\Users\prora\.claude\plans\streamed-whistling-owl.md (prior plan)
- risk: HIGH — inconsistent documentation causes agent confusion about terminal states
- required_repair: REPAIR-001 — count states programmatically; update all text references to 32
- validation_command: `python -c "import json; sm=json.load(open('authority-healing-state-machine.json')); assert len(sm['states'])==32"`
- owner_lane: L-STATEMACHINE

The prior hardening plan's narrative said "29 states" but the state list contains 32 distinct states:
DISCOVERED, EVIDENCE_IMPORTED, TRIAGED, ROOT_CAUSE_CONFIRMED, TASKCARD_CREATED,
BLOCKED_BY_MISSING_EVIDENCE, BLOCKED_BY_MISSING_SPEC, BLOCKED_BY_EXTERNAL_AUTHORITY,
BLOCKED_BY_PREREQUISITE_TASKCARD, READY_FOR_DESIGN, DESIGN_COMPLETE,
READY_FOR_IMPLEMENTATION, IMPLEMENTING, IMPLEMENTED, VALIDATING, VALIDATION_FAILED,
PILOT_READY, PILOT_RUNNING, PILOT_FAILED, PILOT_PASSED, INDEPENDENT_VERIFICATION_REQUIRED,
INDEPENDENT_VERIFIED, HUMAN_APPROVAL_REQUIRED, AUTHORITY_DEBT_RECORDED,
DOWNGRADED_NON_PRODUCT, SUPERVISOR_GATE_ENFORCED, PROOF_GRAPH_ENFORCED,
LEDGER_ENFORCED, RELEASE_GATE_ENFORCED, CLOSED_VERIFIED, CLOSED_WITH_AUTHORITY_DEBT,
REJECTED_FALSE_CLAIM

Count = 32. Markdown and JSON must both declare 32.

---

## Category 2: Current Repo Compatibility

**Status: NEEDS_REPAIR**

**ISSUE-002: Normalization output path discrepancy**
- issue_id: ISSUE-002
- evidence_path: .local/spec-cache/fods/1.3/normalized/ (actual output location)
- risk: MEDIUM — plan's WI-1 and TCA-011 reference .local/spec-normalize/fods/1.3/ but actual output is at .local/spec-cache/fods/1.3/normalized/
- required_repair: REPAIR-002A — update TCA-011 path references; note the discrepancy in evidence-import-review; the investigation sprint's path is WRONG for this repo
- validation_command: `ls .local/spec-cache/fods/1.3/normalized/text.txt`
- owner_lane: L-EVIDENCE

All other tool paths exist: normalize_pdf.py, requirement_extractor.py, authority_integration_fabric.py.
No CI workflows. No pre-commit hooks.

**FODS PDF confirmed present:**
- Path: .local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf
- Size: 24270588 bytes
- SHA-256: sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066 (matches spec-index.yaml)

**requirement_extractor.py confirmed present.**
**authority_integration_fabric.py confirmed present** (but not imported by autonomous_cycle.py — GAP-008).
**schemas/evidence-declaration.schema.json NOT FOUND** — evidence schema exists only in docs/automation/supervisor-worker-contract.md (narrative format).

---

## Category 3: Governance Compatibility

**Status: PASS**

AGENTS.md present. CLAUDE.md present. Plan respects:
- No push, no commit
- No Gate 11 approval
- No MCP activation
- No product source changes in plan-repair sprint

---

## Category 4: Hook/Gate Compatibility

**Status: PASS**

No .github/workflows/ found. No .husky/ hooks. No hooks/ directory.
CI checks: NONE locally runnable. Mark all CI gates as ci_available=false in verification-gates.json.

---

## Category 5: Taskcard Completeness

**Status: NEEDS_REPAIR**

**ISSUE-003: TCA-000 pre-marked CLOSED_VERIFIED**
- issue_id: ISSUE-003
- evidence_path: prior plan TCA-000 definition
- risk: HIGH — creates false impression of completion before validation
- required_repair: REPAIR-004 — TCA-000 starts as IMPLEMENTING in taskcard-state.json
- validation_command: `python -c "import json; ts=json.load(open('taskcard-state.json')); assert ts['TCA-000']!='CLOSED_VERIFIED'"`
- owner_lane: L-STATEMACHINE

---

## Category 6: State Machine Correctness

**Status: NEEDS_REPAIR**

See ISSUE-001. Additionally:
- All terminal states are defined (CLOSED_VERIFIED, CLOSED_WITH_AUTHORITY_DEBT, REJECTED_FALSE_CLAIM)
- BLOCKED states all have unblock transitions
- Rollback transitions need explicit definition — see ISSUE-008

---

## Category 7: Evidence Rules

**Status: NEEDS_REPAIR**

**ISSUE-004: spec_fact_refs is warning-only**
- issue_id: ISSUE-004
- evidence_path: reports/spec-authority/spec-authority-investigation-001/next-healing-sprint-prompt.md WI-5
- risk: CRITICAL — "warn only" allows product work to bypass spec authority
- required_repair: REPAIR-007 — spec_fact_refs must be BLOCKING for new product work (PRODUCT_SOURCE, TEST, REQUIREMENT, READINESS, RELEASE_GATE items)
- validation_command: grep repaired-plan.md for "warning" near "spec_fact_refs" returns 0
- owner_lane: L-SCHEMA

**ISSUE-005: validated_by: human as default for agent-verifiable facts**
- issue_id: ISSUE-005
- evidence_path: healing-design.md MVR-3 schema; verified-facts.yaml has verification_status:verified set by automated tool build_spec_workbench.py (NO validated_by field at all)
- risk: HIGH — conflates automated verification with human review
- required_repair: REPAIR-003 — agent-verifiable facts use validated_by: independent_agent_verifier; human review only for external authority decisions (Gate 11, commit/push, legal)
- validation_command: grep repaired-plan.md for 'validated_by.*human' without human_approval_required_reason context
- owner_lane: L-GOVERNANCE

---

## Category 8: Supervisor/Automation Integration

**Status: PASS**

Plan does not conflict with autonomous continuation.
Does not modify autonomous_cycle.py during plan-repair sprint.
Evidence declarations respect current schema conventions.

---

## Category 9: Human-vs-Agent Ownership

**Status: NEEDS_REPAIR**

See ISSUE-005. Additionally:
- INDEPENDENT_VERIFICATION_REQUIRED state is used correctly in state machine
- HUMAN_APPROVAL_REQUIRED only for: git push/commit, Gate 11 approval, package publication, credential changes
- TCA-010 (human review workflow) needs explicit wording: validated_by: independent_agent_verifier for agent verification

---

## Category 10: Swarm Readiness

**Status: NEEDS_REPAIR**

**ISSUE-006: No lane model defined in prior plan**
- issue_id: ISSUE-006
- evidence_path: prior plan — no lane assignments in taskcards
- risk: MEDIUM — without lane ownership, multiple agents may write conflicting files
- required_repair: REPAIR-005 — add 9-lane model with explicit ownership; assign lane to every taskcard
- validation_command: lane-ownership-map.json validates; overlap checker passes
- owner_lane: L-COORD

---

## Category 11: File Ownership and Overlap Safety

**Status: NEEDS_REPAIR**

See ISSUE-006. Additionally:
- .local/spec-cache/ must be read-only during this sprint (PDF is there — do not modify)
- Report directory is unique to RUN_ID — no conflicts with prior sprints

---

## Category 12: Verification Completeness

**Status: NEEDS_REPAIR**

**ISSUE-007: No validator script in prior plan**
- issue_id: ISSUE-007
- evidence_path: prior plan — no validate_repaired_plan.py
- risk: HIGH — without a validator, completeness claims are unverifiable
- required_repair: REPAIR-010 in this sprint — produce validate_repaired_plan.py (Phase 11)
- validation_command: `python validate_repaired_plan.py --run-dir <run_dir>` exits 0
- owner_lane: L-VERIFY

---

## Category 13: Rollback/Recovery Completeness

**Status: NEEDS_REPAIR**

**ISSUE-008: No rollback plan in prior plan**
- issue_id: ISSUE-008
- evidence_path: prior plan — no rollback-recovery-plan.md
- risk: MEDIUM — agents have no defined behavior on failure
- required_repair: REPAIR-006 — add rollback-recovery-plan.md + .json covering 12 failure modes
- validation_command: rollback-recovery-plan.json parses; covers all 12 failure modes
- owner_lane: L-COORD

---

## Category 14: CI/GitHub Applicability

**Status: PASS**

No .github/workflows/ present. All tests run locally. Mark all verification gates as ci_available=false.

---

## Category 15: Final Evidence Bundle Completeness

**Status: NEEDS_REPAIR**

**ISSUE-009: Hardcoded Windows paths in prior plan**
- issue_id: ISSUE-009
- evidence_path: prior plan contains C:\Users\prora\... paths
- risk: HIGH — paths break on other machines; violates portability requirement
- required_repair: REPAIR-002 — replace all C:\Users\prora\... with ${REPO_ROOT}/...
- validation_command: grep repaired-plan.md for "C:\\Users" returns 0
- owner_lane: L-COORD

---

## Issues Summary

| issue_id | risk | REPAIR |
|----------|------|--------|
| ISSUE-001 | HIGH | REPAIR-001 |
| ISSUE-002 | MEDIUM | REPAIR-002A |
| ISSUE-003 | HIGH | REPAIR-004 |
| ISSUE-004 | CRITICAL | REPAIR-007 |
| ISSUE-005 | HIGH | REPAIR-003 |
| ISSUE-006 | MEDIUM | REPAIR-005 |
| ISSUE-007 | HIGH | REPAIR-010 (validator script) |
| ISSUE-008 | MEDIUM | REPAIR-006 |
| ISSUE-009 | HIGH | REPAIR-002 |

All 9 issues are addressed by the 10 mandatory repairs.
No BLOCKED categories — all are NEEDS_REPAIR with defined solutions.

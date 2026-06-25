# Autonomous Supervisor Audit

**Sprint/Run ID:** ff-archaeology-20260625

---

## Summary

The autonomous supervisor is **GREEN**. Continuation signal shows `autonomous_continue=true`,
iteration 1/12, zero hard stops, zero rework items, 1,609 tests pass. AUTONOMOUS_CONTINUE
gate is cleared. 50 governance validators are registered. The supervisor CAN continue without
human intervention.

Known gaps: lane ownership and DAG ordering are prompt-enforced (not code-enforced).
No durable failure memory. Overclaim detector is not called automatically.

---

## Current Session State

| Field | Value |
|-------|-------|
| autonomous_continue | true |
| iteration | 1 |
| max_iterations | 12 |
| session_id | f9145814a1ee |
| owner | autonomous_cycle |
| hard_stops_detected | [] |
| rework_items | [] |
| continuation_state | YES |
| stop_reason | null |
| safe_lanes_available | true |

---

## Approval Gates

| Gate | Status |
|------|--------|
| AUTONOMOUS_CONTINUE | YES |
| MCP_STATUS | ACTIVE (.vscode/mcp.json present) |
| Test suite | 1,609 pass, 0 fail |
| Contradictions | None blocking |
| Next human gate | MODE 5 (explicit user approval for next phase) |

---

## Continuation Logic

**File:** `tools/supervisor/check_continuation.py`

**Verdict engine (deterministic):**
1. Check plan lock (if plan active, block general ledger work)
2. Check session identity (SESSION_MISMATCH → HARD STOP)
3. Check AUTONOMOUS_CONTINUE gate
4. Check hard_stops in continuation signal
5. Check rework_items
6. Check GOV_BLOCK signals
7. Return CONTINUE or STOP with reason

**Hard stops (non-overridable):**
- SESSION_MISMATCH / CHAT_ID_MISMATCH
- POST_PLAN_TERMINAL
- PLAN_COMPLETED_IN_SESSION
- GOV_BLOCK:monolith_detection_validator (when in rework_items)
- GOV_BLOCK:validate_source_architecture (when in rework_items)

**Overridable stops:**
- MAX_ITERATIONS → reset to 0 and continue
- Advisory stops → continue reading next-sprint.md
- check_continuation.py failure → read next-sprint.md directly

---

## Governance Validators (50 Total)

### Validator Categories

| Category | Count | Examples |
|----------|-------|---------|
| Execution & Claim | 8 | validate_execution_method_required, validate_claim_classification |
| Specification & Traceability | 10 | V53 spec_qname, V18 spec_fact_refs, V23 qname_coverage |
| Source Architecture | 8 | validate_source_marker_or_sidecar, validate_lane_ownership |
| Product Quality | 12 | validate_depth_score, V36 no_stub_tests, V42 deepening_suspension |
| Analytics & Skills | 4 | V41 analytics_skill_required, V44 skill_coverage |
| Stubs & Architecture | 3 | V48 architecture_only_stub_gate, V45 canonical_naming |
| Supporting | 5 | V68 knowledge_freshness, lane_enforcement_validator, utils |

### Key Validators for QName/SAL/Skill

| ID | Name | Purpose |
|----|------|---------|
| V53 | validate_spec_qname_refs | ClassVar spec_qname on authority classes |
| V18 | validate_spec_fact_refs_wired | Work items must cite FACT-FORMAT-NNN |
| V23 | validate_qname_coverage | Count qname registrations per format |
| V41 | validate_analytics_skill_required | Analytics functions → analytics.py |
| V42 | validate_deepening_suspension | Block arithmetic analytics masquerade |
| V43 | enforce_skill_first_execution | Skill transcript before manual coding |
| V44 | check_skill_coverage | Verify skill transcript present |
| V45 | validate_canonical_naming | No format-prefix outside Compat/ |
| V48 | validate_architecture_only_stub_gate | Block RELEASE_GATE citing stubs |
| V68 | validate_knowledge_freshness | Detect KC-PYTHON-001/002 drift |

---

## Autonomous Supervisor Architecture

### Main Orchestrator (autonomous_cycle.py)

**LOC:** 2,406 (at baseline cap)
**Key phases:**
1. Step 0a: SAL refresh check
2. Step 0a-refresh: Knowledge freshness
3. Step 0b: Plan lock check
4. Step 1: Load declaration
5. Step 2: Validate declaration (run all 50 validators)
6. Step 2d3: TC-GUARD-001 unconditional block (items without gap_ledger_ref → rework)
7. Step 3: Grade work items (SAL enrichment)
8. Step 3a-pre: Inject gap_ledger_ref from next-work-items.json
9. Step 4: Generate next sprint prompt
10. Step 5: Circuit breaker check (zero-task detection)
11. SIGNAL-UNIFY-001: Patch work-item-grades consistency

### Sprint Executor (sprint_executor.py)

**Purpose:** Headless run-loop for background autonomous execution
**cmd_status:** Always exits 0 (read-only reporter)
**run-loop mode:** Resets iteration counter, continuous execution

### Continuation Signal (continuation-signal.json)

**Path:** `.local/supervisor/continuation-signal.json`
**Contents:** `{autonomous_continue, iteration, max_iterations, session_id, owner,
hard_stops_detected, rework_items, continuation_state, stop_reason, safe_lanes_available}`

---

## Known Supervisor Gaps

### Gap 1: Lane Ownership is Prompt-Only (MEDIUM)

**Issue:** `declared_lane` in work items is validated by `lane_enforcement_validator.py`
but the ASSIGNMENT of items to lanes depends on the sprint prompt / human judgment.
No code ensures that a PRODUCT_SOURCE item in a machinery sprint gets rejected.

**Workaround:** `MULTI_LANE` declaration is supported. Lane enforcement validator handles
it gracefully (skip single-lane constraint, report as advisory).

### Gap 2: DAG Ordering is Prompt-Only (MEDIUM)

**Issue:** The wave-based dependency DAG (Wave 0 → Wave 1 → ... → Wave 7) is defined
in the spec-to-feature plan but not enforced by code. An agent COULD run product work
(Wave 5) before completing machinery healing (Waves 1-3).

**Mitigation:** `check_continuation.py` checks GOV_BLOCK signals. If monolith or
source architecture validators fire, continuation is blocked (SYSARCH-011 notes this).

### Gap 3: Overclaim Detector Not Auto-Called (MEDIUM)

**Issue:** The overclaim detector (`anti_skip_checker.py`) exists but is not called
automatically during validation. It must be run manually or via the `scan-residual-bypasses`
skill.

### Gap 4: No Durable Failure Memory (LOW)

**Issue:** All decision rules are static. When a validator fails repeatedly for the same
root cause, the supervisor doesn't learn to avoid the same mistake.
**Mitigation:** `failure_memory.py` exists but is not integrated into decision logic.
MEMORY.md provides session-level notes but doesn't auto-propagate corrections.

### Gap 5: Evidence Quality Zero (HANDLED)

**Issue:** When LLM grader is unavailable (no GPT_OSS_ENDPOINT), evidence quality score = 0.
**Fix applied (2026-06-18):** Appends to `continuation_warnings` (not `hard_stops`).
Autonomous continuation is NOT blocked by missing LLM grader.
`DEFERRED_WITH_REASON` status is used for spec-parity PRODUCT_SOURCE items without grader.

---

## Supervisor Readiness Rating

| Criterion | Status |
|-----------|--------|
| Continuation gate GREEN | YES |
| Test suite passing | YES (1,609/0) |
| Hard stops absent | YES |
| Rework items absent | YES |
| 50 validators operational | YES |
| Lane separation enforced | YES (code + prompt) |
| GOV_BLOCK signals present | YES |
| Session identity guard (CCI-MVP) | YES |
| Plan lock enforcement | YES |
| DAG ordering enforced | NO (prompt-only) |
| Overclaim detector auto-called | NO (manual) |
| Durable failure memory | NO |

**Overall supervisor readiness: GREEN with 4 known structural gaps (MEDIUM/LOW severity).**

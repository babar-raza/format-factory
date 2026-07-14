# Investigation Plan: Supervisor Machinery Audit — Production-Grade
# Plan: polymorphic-foraging-feather
# Repository: format-factory | Branch: main | HEAD: af879e550ee47f89dd7e805314f9b14923fbf100
# Authority: THIS FILE IS THE SOLE AUTHORITATIVE PLAN
# Artifact role: authoritative_execution_plan
# execution_authority: true

---
# PART I — PLAN AUTHORITY AND PREFLIGHT
---

## Plan Authority Verdict

authoritative_plan: C:\Users\prora\.claude\plans\polymorphic-foraging-feather.md
authority_source: active_plan_mode_session
duplicate_active_plans_found: false
duplicate_risk: NONE — no other plans in plans/.claude/ address this investigation scope
plan_format: markdown with inline YAML blocks
plan_size_lines: ~850 (original) → ~1600 (pass 1) → ~2800 (pass 2: G-001..G-020 added; TC-INV-005..011 expanded)
major_section_count: 7 (Parts I-VII)
existing_taskcard_format: prose TC-INV-NNN (pre-enhancement)
existing_lanes: observability, dead-code-verification, duplication-migration, state-lifecycle, validation-evidence, language-platform, adversarial-verification
existing_waves: Phase 0-11 (TC-INV-000 through TC-INV-011)
existing_gates: per-phase completion criteria
existing_state_vocabulary: TO CREATE / IN_PROGRESS / DONE (informal, pre-enhancement)
existing_validation_model: per-phase "Produce:" lists
existing_evidence_model: investigation files at docs/investigations/supervisor-machinery-audit/
existing_naming_conventions: TC-INV-NNN for phases; VF-NNN for verified facts; RC-NNN for root causes; P-NNN for problems; REDESIGN-NNN for solutions
existing_execution_handoff: none (pre-enhancement)

## Section Inventory (complete plan read confirmation)

Sections analyzed in full:
  S-001  Why This Investigation Exists            ANALYSIS — preserve exactly
  S-002  Operating Rules                           CONSTRAINTS — preserve exactly
  S-003  Pre-Investigation Evidence (VF-001..010)  ANALYSIS — preserve exactly; anchor for all findings
  S-004  Root Cause Analysis (RC-001..005)         ANALYSIS — preserve exactly
  S-005  What Must Be Preserved (PRESERVE-001..007) CONSTRAINTS — preserve exactly
  S-006  What Must Be Redesigned (REDESIGN-001..005) DESIGN — preserve exactly
  S-006b System Guarantees (G-001..G-020)          ANALYSIS — ADDED pass 2; canonical guarantee list
  S-007  Investigation Package Structure           ARTIFACT LIST — preserve; convert to taskcards
  S-008  Phase 0: Setup and Baseline (TC-INV-000)  EXECUTION — decompose into hierarchical TC
  S-009  Phase 1: LOC Classification (TC-INV-001)  EXECUTION — decompose
  S-010  Phase 2: Architecture Reconstruction (TC-INV-002) EXECUTION — decompose
  S-011  Phase 3: Component Register (TC-INV-003)  EXECUTION — decompose
  S-012  Phase 4: Problem Catalog (TC-INV-004)     EXECUTION — decompose
  S-013  Phase 5: Guarantee Matrix (TC-INV-005)    EXECUTION — decompose
  S-014  Phase 6: Risk Register (TC-INV-006)       EXECUTION — decompose
  S-015  Phase 7: Target Architecture (TC-INV-007) EXECUTION — decompose
  S-016  Phase 8: Hardened Execution Plan (TC-INV-008) EXECUTION — decompose (contains sub-stages S0-S7)
  S-017  Phase 9: Adversarial Review (TC-INV-009)  EXECUTION — decompose
  S-018  Phase 10: Executive Decision Brief (TC-INV-010) EXECUTION — decompose
  S-019  Phase 11: Second Pass (TC-INV-011)        EXECUTION — decompose
  S-020  Tradeoffs and Honest Limits               ANALYSIS — preserve exactly
  S-021  Output Summary                            CONSTRAINTS — preserve exactly

All sections analyzed: YES
Actionable items found in execution phases: 60+ discrete actions
Ambiguous items: 3 (VF-007 characterize decision; oracle classification; lifecycle_audit format enforcement scope)
Contradictions: 0
Missing evidence: 5 (MISSING-001..005 in executive brief section)

---
# PART II — PRESERVED ANALYSIS
---

## Why This Investigation Exists

A prior assessment claimed ~81K LOC of supervisor machinery against ~72K LOC of product code.
Both figures are undercounts. More importantly, that framing missed the real story:

  tools/supervisor/  89,165 LOC  (the claimed "81K")
  tests/supervisor/  89,524 LOC  THE SAME SIZE AS THE MACHINERY
  plans/ directory   95,951 LOC  LARGEST TRACKED DIRECTORY
  src/ product       76,170 LOC  (the claimed "72K", Python + .NET)

The size comparison is not the problem. The problem is that the system has five concrete
failure modes that break consistency across reruns — none of which are addressed by counting
lines. This investigation documents them precisely and proposes a production-grade fix for each.

---

## Operating Rules

READ-ONLY throughout. Write only to:
  docs/investigations/supervisor-machinery-audit/  (new investigation files)
  C:\Users\prora\.claude\plans\polymorphic-foraging-feather.md  (this plan)

No edits to: src/, tests/, tools/, registry/, .supervisor/, schemas/, .governance/,
plans/master-plan.md, plans/strategic/, reports/, .local/

Every claim cites: file path, line number, command output, or git evidence.
Classify every claim: VERIFIED_FACT | STRONG_INFERENCE | WEAK_INFERENCE | UNRESOLVED

Supporting artifacts created during investigation:
  authoritative_plan: C:\Users\prora\.claude\plans\polymorphic-foraging-feather.md
  artifact_role: analysis_or_evidence_only
  execution_authority: false

---

## Pre-Investigation Evidence (VERIFIED_FACTs — do not alter)

### VF-001: Precise LOC at HEAD af879e55

  tools/supervisor/                89,165 LOC  (250+ .py files)
  tests/supervisor/                89,524 LOC  (367 .py test files)
  src/python/                      54,226 LOC  (includes nested fods/fods/ duplicates)
  src/net/                         21,944 LOC  (.cs files only)
  docs/                            45,884 LOC  (.md files only)
  plans/                           95,951 LOC  (largest tracked directory)
  .supervisor/                     34,654 LOC
  tools/ (non-supervisor)          36,886 LOC
  registry/                        16,038 LOC
  tests/ total (Python)            84,048 LOC

  Prior "81K machinery" = tools/supervisor/ alone, missing .supervisor/ (35K), tools-non-supervisor (37K)
  Prior "72K product" = missed that src/python/ has nested package duplicates; actual clean Python ~54K

  Prior assessment verdict: PARTIALLY_ACCURATE (correct ratio direction; both figures ~10% undercounts;
  framing missed that test infrastructure equals machinery size and plans exceed product size)

### VF-002: Active State File Inconsistency (present at plan creation)

  .local/supervisor/active-continuation.json   session_id: "6aa05023e6ac"  (stale session)
  .local/supervisor/active-session.json         session_id: "033f6a1ae2f3"  (current session)
  .local/supervisor/active-plan-lock.json       session_id: "033f6a1ae2f3"  (current session)
  .local/supervisor/continuation-signal.json    session_id: null

  Three of four authoritative state files disagree on session identity. No reconciliation
  mechanism runs before check_continuation.py makes its verdict.

### VF-003: check_continuation.py Mutates State During Read (~line 444)

  Check 5 (max iterations): reads continuation-signal.json, then if iteration >= max_iterations,
  WRITES the file (resets iteration to 0) before proceeding. Crash between read and write
  leaves file at old iteration count while in-memory state reflects the reset.

### VF-004: Non-Atomic Lock Collection (~line 195)

  Plan lock collection: glob plan-locks/*.json → sort by updated_at → decide.
  Glob not protected by filesystem lock. New TERMINAL_CLOSED lock written between glob
  and sort will not be seen → false CONTINUE verdict.

### VF-005: Validator Count Is a Fragile Hardcoded Integer

  governance_validator_runner.py line 813: expected_count = 167
  - Updated manually per-sprint (comments cite TC-PFF-R1, 2026-07-09)
  - Validators silently disappear on import failure (bare except: pass at lines 384, 792, 895)
  - Test assertion in test_governance_validators.py line 3376 checks >= 154, NOT exact 167
  - Gap between runner expectation (167) and test threshold (>= 154)

### VF-006: Grade Cache TTL Bypass on Malformed Timestamp

  grade_declared_work.py ~line 86: malformed _cached_at triggers except clause that
  silently skips TTL check and returns stale cached grade. Corrupted field = permanent cache.

### VF-007: Six Autonomous Variants Have No Production Callers

  AutonomousPocController, AutonomousTrainExecutor, AutonomousHostRunner,
  AutonomousHostDaemon, TriLaneIntegration, ReworkOrchestrator
  — zero imports outside their test files (~3,958 LOC total)
  — production loop: sprint_executor.py → check_continuation.py → autonomous_cycle.py
  — classification: TEST HARNESSES (tests exist); disposition: CHARACTERIZE before any action

### VF-008: Three Backends Are Architecturally Blocked by Design

  CogneeMemoryBackend:    can_execute() returns False; error: "COGNEE_RECALL_IS_NOT_EVIDENCE"
  SkillSeekersBackend:    can_execute() returns False; error: "SKILL_SEEKERS_GENERATED_NE_INSTALLED"
  SessionSkillBackend:    can_execute() returns False; error: "SESSION_SKILL_TOOL is not invocable"
  Total LOC: 169. These are NOT dead code — they encode architectural boundaries.

### VF-009: Critical Behavioral Rules Are Prompt-Only

  "Write plan lock IMMEDIATELY at Step 0"  PROMPT ONLY
  "Do NOT resume prior sprints"            PROMPT ONLY
  "STOP after writing --terminal"          PROMPT ONLY (detection exists if called)
  "Per-chat plan precedence"               PROMPT ONLY

### VF-010: lifecycle_audit.py Table Parsing Is Fragile

  Requires: | TC-ID | STATUS | (two-column markdown table)
  Three regex patterns; only table format reliable for plans with many lines between
  headings and status. Single typo (CLSOED vs CLOSED) → silent miss → ITERATION_REQUIRED.

---

## Root Cause Analysis

### Symptoms
  S1. Session resumes wrong sprint or wrong plan
  S2. Plan lock appears to not block continuation
  S3. Governance validation "passes" but product has structural problems
  S4. Stale acceptance verdicts on unchanged work
  S5. lifecycle_audit closes with ITERATION_REQUIRED despite all taskcards done
  S6. check_continuation returns CONTINUE after TERMINAL_CLOSED

### Root Causes

  RC-001: NO STATE INTEGRITY LAYER
    check_continuation.py reads 3-5 files in sequence with no consistency check.
    session_id, autonomous_continue, and plan lock status are never cross-validated
    before the continuation verdict is issued.

  RC-002: ENFORCEMENT MODEL IS PROMPT-FIRST, CODE-SECOND
    Critical rules (plan lock before sprint, stop after terminal) live in CLAUDE.md.
    Code enforcement only fires if the agent cooperates by calling the right functions.

  RC-003: VALIDATOR REGISTRATION IS STATIC AND FRAGILE
    Hardcoded expected_count + silent exception handlers = governance can silently degrade.
    Test threshold (>= 154) and runner expectation (167) have no machine link.

  RC-004: SELF-CERTIFIED EVIDENCE WITH HEURISTIC VERIFICATION
    Same LLM writes work and its evidence-declaration.yaml.
    Anti-skip 19 heuristics check field existence, not semantic correctness.
    Oracle is the only machine-verifiable signal but is not required for acceptance.

  RC-005: MULTI-FILE STATE WITH NO TRANSACTION BOUNDARY
    Atomic writes per-file (atomic_io.py) exist. Cross-file atomicity does not.
    Crash between writes leaves state inconsistent; no automatic recovery.

---

## What Must Be Preserved

  PRESERVE-001: autonomous_cycle.py (2,768 LOC) — declaration-driven architecture correct
  PRESERVE-002: check_continuation.py (796 LOC) — concept correct; implementation needs hardening
  PRESERVE-003: governance_validator_runner.py (821 LOC) + validator ecosystem
  PRESERVE-004: atomic_io.py — per-file atomicity already correct
  PRESERVE-005: Oracle execution infrastructure — 73/73 PASS is the only hard signal
  PRESERVE-006: write_plan_lock.py session-keyed lock mechanism — concept correct
  PRESERVE-007: grade_declared_work.py grading types (12 types) — correct model

---

## What Must Be Redesigned

  REDESIGN-001 (HIGH IMPACT, LOW RISK): Validator Dynamic Registration
    Replace hardcoded expected_count=167 with .supervisor/validator-registry.yaml.
    Runner counts from registry. Test asserts exact registry count.
    Exception handlers emit structured diagnostics.

  REDESIGN-002 (HIGH IMPACT, MEDIUM RISK): State Integrity Pre-Check
    state_integrity_check() at TOP of check_continuation.py before any other check.
    Validates session ID consistency and plan lock / autonomous_continue agreement.
    Deploy in WARN mode first; switch to BLOCK after 5 sessions of clean data.

  REDESIGN-003 (HIGH IMPACT, LOW RISK): Atomic Lock Collection
    Advisory lockfile at plan-locks/.collection.lock acquired before glob.
    Or: replace directory of files with single versioned plan-locks/current.json.

  REDESIGN-004 (MEDIUM IMPACT, LOW RISK): Grade Cache TTL Hardening
    Malformed _cached_at → treat as EXPIRED (not as valid). Emit WARNING log.
    Add cache health check at import time.

  REDESIGN-005 (MEDIUM IMPACT, MEDIUM RISK): Oracle Evidence Gating
    PRODUCT_SOURCE declarations require oracle evidence for ACCEPTED_VERIFIED.
    Without oracle: grade becomes ACCEPTED_WITH_LIMITATIONS.
    Skip for formats with OBLIGATION_CREATED (no oracle exists yet).

---

## System Guarantees (G-001..G-020 — authoritative list for TC-INV-005)

This is the canonical guarantee list. TC-INV-005 maps each guarantee to its enforcing components.
Current-status column uses: ENFORCED | PARTIAL | PROMPT_ONLY | ABSENT

  G-001: SESSION_ISOLATION
    Description: CCI-MVP prevents cross-chat state contamination — a CONTINUE verdict never
    consumes state from a different session_id.
    Enforcing: check_continuation.py Check 0 (session_id match); continuation-signal.json session_id field
    Current status: PARTIAL (Check 0 fires on mismatch but active-continuation.json may carry stale id)
    Failure consequence: Sprint from prior chat resumes in new chat; wrong work executed

  G-002: SPRINT_REPEATABILITY
    Description: Given the same evidence-declaration.yaml and same codebase, grade_declared_work.py
    produces the same grade outcome.
    Enforcing: grade_declared_work.py (deterministic 12 grade types); grade-cache.json TTL
    Current status: PARTIAL (malformed _cached_at bypasses TTL check → stale cached grade returned; VF-006)
    Failure consequence: Changed declaration receives stale grade; wrong CONTINUE/STOP verdict

  G-003: PLAN_LOCK_PRECEDENCE
    Description: When a per-chat plan is loaded, it is the sole work-selection authority; no sprint
    loop item supersedes it until all taskcards are CLOSED.
    Enforcing: write_plan_lock.py (CLAUDE.md Step 0); check_continuation.py Check 1b (plan lock gate)
    Current status: PROMPT_ONLY (write_plan_lock.py call is agent-cooperative; Check 1b fires only if lock was written)
    Failure consequence: Agent ignores plan and resumes ledger work; plan objectives silently abandoned

  G-004: GOVERNANCE_COMPLETENESS
    Description: All registered validators run against every evidence declaration. No validator
    silently absent at runtime.
    Enforcing: governance_validator_runner.py; expected_count=167 (line 813)
    Current status: PARTIAL (bare except: pass at lines 384, 792, 895 silently drops failed-import validators; VF-005)
    Failure consequence: Governance passes with fewer than 167 validators; structural violations missed

  G-005: DECLARATION_SCHEMA_VALIDITY
    Description: Every evidence-declaration.yaml is validated against schema before grading begins.
    Enforcing: sprint_executor_validate.py; autonomous_cycle.py Phase 1 (validate)
    Current status: ENFORCED (validator runs; --repair flag auto-corrects fences and type mismatches)
    Failure consequence: Malformed declaration reaches grader; grade produces wrong result or exception

  G-006: STATE_AUTHORITY_ORDERING
    Description: check_continuation.py derives its verdict from a consistent snapshot where all
    4 state files agree on session identity and continuation intent.
    Enforcing: NONE — check_continuation.py reads files sequentially with no cross-validation
    Current status: ABSENT (RC-001; VF-002 shows 3-of-4 files disagree RIGHT NOW)
    Failure consequence: False CONTINUE in wrong session; wrong sprint executed

  G-007: PER_FILE_WRITE_ATOMICITY
    Description: Individual state file writes are atomic (write-to-temp-then-rename); no partial
    state is visible to readers after a crash mid-write.
    Enforcing: atomic_io.py (all supervised state writes use this)
    Current status: ENFORCED (per-file atomicity correct; PRESERVE-004)
    Failure consequence: n/a per-file; cross-file atomicity NOT guaranteed (separate concern → RC-005)

  G-008: ORACLE_DETERMINISM
    Description: Oracle execution produces deterministic results for the same format sample;
    73/73 PASS at HEAD is the only machine-verifiable correctness signal.
    Enforcing: execute_oracle.py; oracle/formats/*/oracle-package.yaml
    Current status: ENFORCED (73/73 PASS across 20 Python FOSS formats; PRESERVE-005)
    Failure consequence: Oracle results non-deterministic; ACCEPTED_VERIFIED grade loses meaning

  G-009: EVIDENCE_SUFFICIENCY
    Description: ACCEPTED_VERIFIED grade is only reachable when evidence_paths include
    verifiable artifacts (not merely declared).
    Enforcing: anti_skip_checker.py (19 heuristics); autonomous_cycle.py Phase 2 (inspect)
    Current status: PARTIAL (anti-skip checks field existence, not semantic correctness;
    oracle evidence is not required for ACCEPTED_VERIFIED; VF-009 / RC-004)
    Failure consequence: LLM-self-certified work grades as ACCEPTED_VERIFIED without real proof

  G-010: INTERRUPTION_RECOVERY
    Description: After a non-destructive crash mid-sprint, the system can resume from the last
    consistent state without requiring manual repair.
    Enforcing: atomic_io.py (per-file); check_continuation.py Check 0 (session guard)
    Current status: PARTIAL (per-file write atomic; cross-file state may be inconsistent; RC-005)
    Failure consequence: Resumed sprint reads incoherent state; continuation verdict wrong

  G-011: TERMINAL_LOCK_FINALITY
    Description: TERMINAL_CLOSED plan lock prevents any CONTINUE verdict in the same chat session.
    POST_PLAN_TERMINAL stop is non-overridable.
    Enforcing: check_continuation.py Check 1b; write_plan_lock.py --terminal
    Current status: PARTIAL (Check 1b only sees TERMINAL_CLOSED if lock was written; VF-009 shows
    the write is prompt-only; also dependent on non-atomic lock collection; VF-004)
    Failure consequence: Agent continues product deepening after plan close in same session

  G-012: ITERATION_COUNTER_ROLLOVER
    Description: When iteration >= max_iterations, the counter resets to 0 and CONTINUE proceeds;
    max_iterations is NOT a hard stop.
    Enforcing: check_continuation.py Check 5 (resets iteration to 0); sprint_executor.py run-loop
    Current status: PARTIAL (Check 5 resets but also WRITES state during read; VF-003 → crash risk)
    Failure consequence: Crash between read and write leaves iteration at old value; double-reset or skip

  G-013: DECISION_AUDITABILITY
    Description: All continuation verdicts, their reasons, and the state inputs used to derive them
    are logged to a persistent audit trail for post-hoc inspection.
    Enforcing: check_continuation.py (verdict written to continuation-signal.json);
    no dedicated audit log of verdict reasoning exists
    Current status: PARTIAL (verdict + reason logged; state inputs NOT captured; no state-consistency-log)
    Failure consequence: Cannot determine why a wrong verdict was issued without manual state file inspection

  G-014: AUTONOMOUS_CONTINUATION
    Description: CONTINUE verdict from check_continuation.py triggers the next sprint without
    human intervention. The loop never requires a human to press "go."
    Enforcing: sprint_executor.py run-loop; check_continuation.py
    Current status: PARTIAL (CCI-MVP degrades silently when session_id mismatch is not caught;
    active-continuation.json lag produces false STOP on valid sessions)
    Failure consequence: Autonomous loop silently halts; human must manually re-trigger

  G-015: GRADE_CACHE_FRESHNESS
    Description: Cached grades expire after 7 days (168 hours); stale cached grades are never
    returned for declarations with changed content.
    Enforcing: grade_declared_work.py TTL check; _cached_at field; fingerprint threshold (500KB)
    Current status: PARTIAL (malformed _cached_at bypasses TTL; VF-006; permanent cache possible)
    Failure consequence: Stale grade returned indefinitely; rework never re-evaluated

  G-016: HUMAN_APPROVAL_GATE
    Description: Gate 11 execution (commercial release) and switching state-integrity from WARN
    to BLOCK mode require explicit human authorization (Babar Raza).
    Enforcing: format-registry.yaml Gate 11 entry; CLAUDE.md Supreme Directive exceptions
    Current status: ENFORCED for Gate 11 execution; PROMPT_ONLY for plan precedence enforcement
    Failure consequence: Commercial release without business authority; or state integrity deployed
    in BLOCK mode before false-positive rate is known

  G-017: BACKEND_SELECTION_CORRECTNESS
    Description: local_deterministic_backend.py is always available (hardcoded, no try/except);
    higher-priority backends (superpowers_skill, task_master, mcp_superpowers, llm_api) are
    selected when importable and can_execute() is True.
    Enforcing: next_action_runner.py _build_default_backends(); can_execute() on each backend
    Current status: ENFORCED (local_deterministic always loaded; backend priority chain correct)
    Failure consequence: Wrong execution backend selected; sprint action not dispatched correctly

  G-018: GOVERNANCE_ANTI_SKIP_COVERAGE
    Description: anti_skip_checker.py detects 19 categories of heuristic evasion in every
    evidence declaration before it reaches the grader.
    Enforcing: anti_skip_checker.py; called by autonomous_cycle.py Phase 2
    Current status: PARTIAL (19 heuristics check field existence and pattern matching;
    semantic correctness not verified; oracle is the only true anti-skip gate)
    Failure consequence: Agent claims work by inserting expected field values without doing work

  G-019: VALIDATOR_COUNT_INTEGRITY
    Description: The count of validators that actually ran equals the expected registered count.
    No validator silently absent due to import failure or registration gap.
    Enforcing: governance_validator_runner.py expected_count=167 check
    Current status: PARTIAL (expected_count=167 is hardcoded; test asserts >= 154 not exact;
    bare except silently drops failed imports; VF-005 / RC-003)
    Failure consequence: Governance "passes" with 150 validators when 167 are expected; 17 rules unenforced

  G-020: LIFECYCLE_AUDIT_COMPLETENESS
    Description: lifecycle_audit.py correctly identifies all open taskcards in a plan before
    allowing TERMINAL_CLOSED closure; typos or format deviations do not produce false CLOSED.
    Enforcing: lifecycle_audit.py; | TC-ID | STATUS | two-column table format
    Current status: PARTIAL (requires exact two-column markdown table; typo CLSOED → silent miss;
    code-block Status: fields not parsed; VF-010 / RC-002 for enforcement model)
    Failure consequence: Plan closes as TERMINAL_CLOSED with open taskcards; work silently abandoned

Summary of guarantee statuses at HEAD af879e55:
  ENFORCED:      G-005, G-007, G-008, G-016 (Gate 11), G-017  (5 of 20)
  PARTIAL:       G-001, G-002, G-004, G-009, G-010, G-011,
                 G-012, G-013, G-014, G-015, G-018, G-019, G-020  (13 of 20)
  PROMPT_ONLY:   G-003, G-016 (plan precedence aspect)  (1.5 of 20)
  ABSENT:        G-006  (1 of 20)

---

## Investigation Package Structure

Location: docs/investigations/supervisor-machinery-audit/
Status: TO CREATE (no existing package at HEAD af879e55)

Required output files (produced by investigation phases):
  00-investigation-scope-and-baseline.md     Phase 0
  01-loc-and-classification-report.md        Phase 1
  02-current-machinery-architecture.md       Phase 2
  03-workflow-traces.md                      Phase 2
  04-machinery-component-register.md         Phase 3
  05-problem-catalog.md                      Phase 4
  06-guarantee-control-matrix.md             Phase 5
  07-risk-register.md                        Phase 6
  08-target-architecture-options.md          Phase 7
  09-hardened-execution-plan.md              Phase 8
  10-adversarial-review.md                   Phase 9
  11-executive-decision-brief.md             Phase 10
  evidence/metrics.json                      Phase 1
  evidence/file-classification.csv           Phase 1
  evidence/component-register.csv            Phase 3
  evidence/commands-and-results.md           Phase 0 (appended throughout)

---
# PART III — NORMALIZED REQUIREMENTS
---

## Requirements Registry

REQ-INV-000  Create investigation directory and capture reproducible baseline state
REQ-INV-001  Produce reproducible LOC measurements; classify every relevant tracked file
REQ-INV-002  Reconstruct current machinery architecture from source; trace 9 workflows
REQ-INV-003  Classify each significant machinery component with evidence and disposition
REQ-INV-004  Document all structural problems with precise file:line evidence and root cause
REQ-INV-005  Map all 20 system guarantees to their enforcing components
REQ-INV-006  Identify and quantify risks from proposed consolidation changes
REQ-INV-007  Compare 7 architecture strategies with benefits, risks, and suitability
REQ-INV-008  Produce non-executed, dependency-aware rationalization plan (Stages 0-7)
REQ-INV-009  Challenge investigation's own conclusions with 14 adversarial arguments
REQ-INV-010  Answer 9 executive questions with evidence; provide final verdict
REQ-INV-011  Second-pass idempotency verification; confirm all quality gates
REQ-INV-SYS  System-wide: no production files changed; all findings cite evidence

---
# PART IV — EXECUTION CONTROL LAYER (Hierarchical Taskcards)
---

## Taskcard State Vocabulary

Parent states:    PROPOSED → READY → IN_PROGRESS → CHILDREN_IN_PROGRESS →
                  INTEGRATION_PENDING → VERIFIED → SCORED → CLOSED
                  (any non-closed → BLOCKED | BLOCKED_EXTERNAL | DEFERRED_WITH_REASON)

Child states:     TODO → READY → IN_PROGRESS → IMPLEMENTED → VERIFIED → SCORED → CLOSED
                  (REROUTED: back to IN_PROGRESS after quality failure)

Micro-step states: PENDING → READY → ACTIVE → COMPLETE | FAILED | BLOCKED
                   (SKIPPED_NOT_APPLICABLE: with mandatory reason)

Invalid transitions (blocked):
  - Child CLOSED without parent integration checks run
  - Parent CLOSED while any mandatory child not CLOSED
  - Micro-step SKIPPED without reason field
  - REROUTED → CLOSED without rework evidence

Quality threshold: all mandatory dimensions >= 4/5; below 4/5 → REROUTED

---

## TC-INV-000: Setup and Baseline

Parent Taskcard ID: TC-INV-000
Title: Create investigation directory and capture reproducible baseline
Type: PARENT
Status: PROPOSED
Owner: investigator-agent
Supervisor: coordinator-lane
Plan requirement: REQ-INV-000
Source section: S-008

Objective: Establish the investigation directory structure and record all baseline
  state (HEAD commit, tracked file count, git status) so every subsequent claim
  is anchored to a fixed, reproducible repository state.

Scope:
  Allowed folders: docs/investigations/supervisor-machinery-audit/ (CREATE ONLY)
  Forbidden: src/, tests/, tools/, registry/, .supervisor/, .local/, plans/ (except this file)
  Path expansion: create evidence/ subdirectory inside investigation root

Outputs:
  - docs/investigations/supervisor-machinery-audit/ directory exists
  - docs/investigations/supervisor-machinery-audit/evidence/ directory exists
  - evidence/commands-and-results.md contains baseline git commands + outputs
  - 00-investigation-scope-and-baseline.md is written and complete

Dependencies: none (first task)
Child taskcards: TC-INV-000-01, TC-INV-000-02, TC-INV-000-03

Parent acceptance criteria:
  - Directory structure exists
  - commands-and-results.md has all 4 baseline commands with outputs
  - 00-investigation-scope-and-baseline.md covers all 7 required subsections
  - git diff --stat shows zero changes outside docs/investigations/

Rollback: rm -rf docs/investigations/supervisor-machinery-audit/ (trivial, no other files touched)
Stop conditions: working-tree conflict detected; investigation directory already exists with conflicting content
Reroute rule: if any required section is missing from 00-baseline.md, mark REROUTED and add missing section

---

Child Taskcard ID: TC-INV-000-01
Parent: TC-INV-000
Title: Create directory structure
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-000
Source: S-008 action 1

Purpose: Physical prerequisite for all subsequent write operations.

Scope:
  Allowed: mkdir two directories only
  Forbidden: any file writes yet (evidence file comes in TC-INV-000-02)

Expected output: two empty directories exist at correct paths

Micro-steps:
  MS-INV-000-01-01: Create investigation root directory
    Action: mkdir docs/investigations/supervisor-machinery-audit
    Target: filesystem
    Precondition: docs/investigations/ parent exists (verify first)
    Completion check: directory exists at path
    Failure: if docs/investigations/ doesn't exist, create it first
    Next: MS-INV-000-01-02

  MS-INV-000-01-02: Create evidence subdirectory
    Action: mkdir docs/investigations/supervisor-machinery-audit/evidence
    Target: filesystem
    Precondition: MS-INV-000-01-01 COMPLETE
    Completion check: evidence/ subdirectory exists
    Failure: if parent mkdir failed, do not proceed
    Next: TC-INV-000-02

Acceptance checks: both directories exist; ls confirms structure
Evidence: directory listing output in commands-and-results.md
Rollback: rmdir in reverse order

---

Child Taskcard ID: TC-INV-000-02
Parent: TC-INV-000
Title: Capture baseline git state and write evidence/commands-and-results.md
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-000
Source: S-008 action 2

Purpose: Record the exact repository state all findings are anchored to.
  This file is APPENDED throughout the investigation with every command + output.

Scope:
  Allowed: create evidence/commands-and-results.md; run read-only git commands
  Forbidden: git checkout, git stash, git reset, any write to tracked files

Expected output: evidence/commands-and-results.md with 4 command blocks + outputs

Micro-steps:
  MS-INV-000-02-01: Run git rev-parse HEAD; record output
    Action: run `git rev-parse HEAD` (READ-ONLY)
    Expected output: af879e550ee47f89dd7e805314f9b14923fbf100 (or current HEAD)
    Completion check: hash recorded
    Next: MS-INV-000-02-02

  MS-INV-000-02-02: Run git log --oneline -5; record output
    Action: run `git log --oneline -5` (READ-ONLY)
    Expected output: 5 commit lines
    Completion check: output recorded
    Next: MS-INV-000-02-03

  MS-INV-000-02-03: Run git status --short; record output
    Action: run `git status --short` (READ-ONLY)
    Expected output: list of M/? modified/untracked files (expected ~18)
    Completion check: output recorded; count of modified files noted
    Next: MS-INV-000-02-04

  MS-INV-000-02-04: Run git ls-files | wc -l; record output
    Action: run `git ls-files | wc -l` (READ-ONLY)
    Expected output: ~15875 (exact count at current HEAD)
    Completion check: number recorded
    Next: MS-INV-000-02-05

  MS-INV-000-02-05: Write evidence/commands-and-results.md with all 4 outputs
    Action: create file with markdown header + 4 command blocks each labeled with
            command text, timestamp, and exact output
    Target file: docs/investigations/supervisor-machinery-audit/evidence/commands-and-results.md
    Required sections: ## Baseline Git State (4 blocks)
    Completion check: file exists; all 4 blocks present; outputs verbatim
    Failure: if any command fails, record "ERROR: <message>" as output
    Next: TC-INV-000-03

Acceptance checks: file exists; 4 command blocks present; HEAD hash matches expected
Evidence: the file itself is the evidence
Rollback: delete evidence/commands-and-results.md

---

Child Taskcard ID: TC-INV-000-03
Parent: TC-INV-000
Title: Write 00-investigation-scope-and-baseline.md (7 required subsections)
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-000
Source: S-008 action 3

Purpose: The formal baseline document that anchors the investigation.

Scope:
  Allowed: write one file only
  Forbidden: any analysis beyond what's already established in VF-001..010

Expected output: complete 00-investigation-scope-and-baseline.md with all 7 subsections

Required subsections (all mandatory):
  §1  Repository identity (root, branch, HEAD, timestamp)
  §2  Working-tree state (all modified/untracked files from git status)
  §3  Top-level directory inventory (each dir with purpose annotation)
  §4  Language distribution (extension counts from git ls-files)
  §5  Runtime entry points (4 primary: supervisor_loop.py, autonomous_cycle.py,
      check_continuation.py, sprint_executor.py — with file paths)
  §6  Excluded-from-counts catalog (list of excluded dirs: .venv/, build/, .pytest_cache/,
      .mypy_cache/, .local/, .ruff_cache/, *.pyc, __pycache__, .local/evidences/)
  §7  Tracked vs locally-generated file categories summary table

Micro-steps:
  MS-INV-000-03-01: Write §1 repository identity
    Action: write subsection with: repo root = c:\Users\prora\OneDrive\Documents\GitHub\format-factory,
            branch = main, HEAD = af879e55..., date from system
    Completion check: §1 present in file
    Next: MS-INV-000-03-02

  MS-INV-000-03-02: Write §2 working-tree state
    Action: paste git status --short output from MS-INV-000-02-03; annotate each file group
    Completion check: §2 present; all modified files listed
    Next: MS-INV-000-03-03

  MS-INV-000-03-03: Write §3 top-level directory inventory
    Action: list each top-level dir from ls output; annotate purpose:
            src/ (product source), tools/ (automation), tests/ (test suite),
            docs/ (documentation), plans/ (planning artifacts), registry/ (config),
            .supervisor/ (governance config), oracle/ (test infrastructure),
            samples/ (format samples), schemas/ (JSON/YAML schemas),
            .governance/ (capability registry), .local/ (generated state, not tracked),
            .venv/ (virtualenv, excluded), build/ (build artifacts, excluded)
    Completion check: §3 present; at least 12 dirs annotated
    Next: MS-INV-000-03-04

  MS-INV-000-03-04: Write §4 language distribution
    Action: run `git ls-files | grep -oE '\.[^.]+$' | sort | uniq -c | sort -rn | head -20`
            record exact output; write as table with extension, count, primary_role columns
    Completion check: §4 present; table has at least 10 rows
    Next: MS-INV-000-03-05

  MS-INV-000-03-05: Write §5 runtime entry points
    Action: document 4 primary entry points with exact paths and one-line descriptions:
            tools/supervisor/supervisor_loop.py (command dispatch, legacy + declaration)
            tools/supervisor/autonomous_cycle.py (canonical supervisor cycle)
            tools/supervisor/check_continuation.py (continuation gate, CCI-MVP)
            tools/supervisor/sprint_executor.py (headless sprint actuator)
    Completion check: §5 present; all 4 files listed with paths
    Next: MS-INV-000-03-06

  MS-INV-000-03-06: Write §6 excluded-from-counts catalog
    Action: document exclusion rules as a table: path, reason for exclusion, tracked_in_git (Y/N)
    Completion check: §6 present; at least 8 exclusions documented
    Next: MS-INV-000-03-07

  MS-INV-000-03-07: Write §7 tracked vs generated categories summary
    Action: write summary table: category, examples, tracked_in_git, counted_in_LOC
            rows: authored_source, generated_state, planning_artifacts, test_fixtures,
            configuration, generated_evidence, vendored_dependencies
    Completion check: §7 present; at least 6 categories
    Next: TC-INV-000 integration check

Acceptance checks: all 7 subsections present; file is self-contained and readable in isolation
Evidence: file path + checksum in evidence/commands-and-results.md
Rollback: delete file

Parent integration checks (TC-INV-000):
  - Both directories exist
  - evidence/commands-and-results.md contains all 4 baseline commands
  - 00-investigation-scope-and-baseline.md has all 7 subsections
  - git diff --stat shows only new files in docs/investigations/

---

## TC-INV-001: LOC Classification

Parent Taskcard ID: TC-INV-001
Title: Produce reproducible LOC measurements and classify every tracked file
Type: PARENT
Status: PROPOSED
Owner: investigator-agent
Supervisor: coordinator-lane
Plan requirement: REQ-INV-001
Source section: S-009
Dependencies: TC-INV-000 CLOSED

Objective: Reproduce the 81K/72K assessment with exact commands, classify every
  relevant tracked file into one of 16 categories, and conclude whether the
  prior assessment was ACCURATE / PARTIALLY_ACCURATE / MISLEADING / INVALID.

Outputs:
  - 01-loc-and-classification-report.md
  - evidence/metrics.json (structured LOC by category + ratios)
  - evidence/file-classification.csv (per-file classification)

Child taskcards: TC-INV-001-01, TC-INV-001-02, TC-INV-001-03, TC-INV-001-04

Parent acceptance criteria:
  - All 16 categories covered (some may have count=0)
  - Prior assessment verdict stated with evidence
  - evidence/metrics.json is valid JSON with all required fields
  - evidence/file-classification.csv has header row + entries
  - commands-and-results.md appended with all LOC measurement commands + outputs
  - No file in tools/supervisor/ or src/ is unclassified

Rollback: delete 01-loc-and-classification-report.md, evidence/metrics.json, evidence/file-classification.csv
Reroute rule: if any top-level directory produces unexpected LOC (>20% from VF-001), investigate before proceeding

---

Child Taskcard ID: TC-INV-001-01
Parent: TC-INV-001
Title: Run per-category LOC measurements and append to commands-and-results.md
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-001

Purpose: Get precise, reproducible LOC numbers for each tracked directory.
  All commands must be run against git ls-files to exclude untracked files.

Scope:
  Allowed: read-only git commands; write to evidence/commands-and-results.md (append)
  Forbidden: modifying any source file

Commands (run each, record exact output):
  git ls-files tools/supervisor/ | xargs wc -l 2>/dev/null | tail -1
  git ls-files src/python/ | grep '\.py$' | xargs wc -l 2>/dev/null | tail -1
  git ls-files src/net/ | grep '\.cs$' | xargs wc -l 2>/dev/null | tail -1
  git ls-files tests/ | grep '\.py$' | xargs wc -l 2>/dev/null | tail -1
  git ls-files oracle/ | grep '\.py$' | xargs wc -l 2>/dev/null | tail -1
  git ls-files tools/ | grep -v 'tools/supervisor/' | xargs wc -l 2>/dev/null | tail -1
  git ls-files docs/ | grep '\.md$' | xargs wc -l 2>/dev/null | tail -1
  git ls-files plans/ | xargs wc -l 2>/dev/null | tail -1
  git ls-files .supervisor/ | xargs wc -l 2>/dev/null | tail -1
  git ls-files registry/ | xargs wc -l 2>/dev/null | tail -1
  git ls-files | grep -oE '\.[^.]+$' | sort | uniq -c | sort -rn | head -20
  git ls-files tools/supervisor/ | xargs wc -l 2>/dev/null | sort -rn | head -15
  git ls-files src/python/ | xargs wc -l 2>/dev/null | sort -rn | head -15
  git ls-files tests/supervisor/ | xargs wc -l 2>/dev/null | sort -rn | head -15
  git ls-files src/python/ | grep '/[^/]*/[^/]*/' | head -10  # detect nested duplicates

Micro-steps:
  MS-INV-001-01-01: Run tools/supervisor/ LOC; verify vs VF-001 (expect ~89,165)
  MS-INV-001-01-02: Run src/python/ LOC; verify vs VF-001 (expect ~54,226)
  MS-INV-001-01-03: Run src/net/ LOC; verify vs VF-001 (expect ~21,944)
  MS-INV-001-01-04: Run tests/supervisor/ LOC (expect ~89,524)
  MS-INV-001-01-05: Run tests/ total LOC (expect ~84,048)
  MS-INV-001-01-06: Run oracle/ LOC (expect ~25,180 per prior agent; verify with .py filter)
  MS-INV-001-01-07: Run tools/ non-supervisor LOC (expect ~36,886)
  MS-INV-001-01-08: Run docs/ LOC (expect ~45,884)
  MS-INV-001-01-09: Run plans/ LOC (expect ~95,951)
  MS-INV-001-01-10: Run .supervisor/ LOC (expect ~34,654)
  MS-INV-001-01-11: Run registry/ LOC (expect ~16,038)
  MS-INV-001-01-12: Run language breakdown command
  MS-INV-001-01-13: Run top-15 by LOC for tools/supervisor/, src/python/, tests/supervisor/
  MS-INV-001-01-14: Run nested package duplicate detection; record findings
  MS-INV-001-01-15: Append ALL command outputs to evidence/commands-and-results.md under ## LOC Measurements

  For each step: if result diverges >20% from VF-001 expected, record DISCREPANCY note and investigate.

Acceptance checks:
  - All 15 commands run and outputs recorded
  - Divergences from VF-001 documented with explanation
  - commands-and-results.md updated
Evidence: evidence/commands-and-results.md §LOC Measurements
Rollback: delete only the appended section in commands-and-results.md

---

Child Taskcard ID: TC-INV-001-02
Parent: TC-INV-001
Title: Apply 16-category classification rules; document ambiguous cases
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-001
Dependencies: TC-INV-001-01 CLOSED (need actual LOC numbers)

Purpose: Map each directory/file category to exactly one of the 16 classifications
  with documented rationale. Ambiguous cases must be explicitly decided.

16 Categories to apply:
  1  product_runtime:       src/python/**/*.py, src/net/**/*.cs (exclude nested duplicates)
  2  supervisor_orch:       tools/supervisor/ core files (autonomous_cycle, check_continuation, etc.)
  3  governance_valid:      governance_validators*.py, runner, anti_skip_checker.py
  4  spec_acquisition:      tools/spec/**
  5  capability_reasoning:  tools/capability_layer/**, autonomous_task_generator.py,
                            generate_next_worker_prompt.py
  6  source_generation:     (none expected — verify)
  7  shared_infra:          atomic_io.py, path_resolver.py, tools/supervisor/backends/
  8  tests:                 tests/**/*.py + oracle/ (oracle classified here, not as machinery)
  9  fixtures_data:         samples/**, tests/**/fixtures/
  10 schemas_config:        schemas/**, .supervisor/schemas/**, *.schema.json,
                            registry/**, .supervisor/policies.yaml, .supervisor/config.yaml
  11 committed_generated:   (none expected — verify)
  12 examples:              examples/**, drivers/**
  13 migration_compat:      Compat/ in src/net/ — check existence
  14 executable_docs:       playbooks/**, templates/**
  15 archived_deprecated:   files with _old, _legacy, _v1 suffixes — scan
  16 unknown:               everything else

Ambiguous cases requiring explicit decisions (document in 01-report.md):
  DECISION-A: oracle/ → classify as cat 8 (tests), NOT cat 2 (machinery)
    Rationale: execute_oracle.py is a test executor; oracle-package.yaml are test specs;
    oracle infrastructure is not shipped as product
  DECISION-B: plans/ → classify as cat 16 (unknown), excluded from authored-LOC totals
    Rationale: 95,951 LOC of planning STATE, not source code
  DECISION-C: .supervisor/project-memory.md → EXCLUDE entirely (584KB generated state)
  DECISION-D: reports/ → EXCLUDE (generated artifacts)
  DECISION-E: .local/ → EXCLUDE (not tracked in git; generated state)

Micro-steps:
  MS-INV-001-02-01: Classify tools/supervisor/ files into cat 2 (supervisor_orch) vs
                    cat 3 (governance_valid) vs cat 5 (capability_reasoning) vs cat 7 (shared_infra)
    Action: read tools/supervisor/ file listing; assign each file to one category;
            document ambiguous assignments (e.g., autonomous_task_generator.py → cat 5 not cat 2)
    Output: table of filename → category for top 30 tools/supervisor/ files

  MS-INV-001-02-02: Classify src/ files into cat 1 (product_runtime) vs cat 13 (migration_compat)
    Action: check for Compat/ directories in src/net/; classify if present
    Output: determination of whether cat 13 has any entries

  MS-INV-001-02-03: Classify tests/ and oracle/ into cat 8 (tests)
    Action: confirm oracle/ classification decision; record with rationale
    Output: DECISION-A recorded in 01-report.md

  MS-INV-001-02-04: Check for cat 6 (source_generation) and cat 11 (committed_generated)
    Action: grep src/ for # GENERATED, # AUTO-GENERATED, # DO NOT EDIT markers
    Command: git ls-files src/ | xargs grep -l "# GENERATED\|# AUTO-GENERATED\|# DO NOT EDIT" 2>/dev/null
    Output: either file list or "no generated markers found"

  MS-INV-001-02-05: Check for cat 15 (archived_deprecated)
    Action: git ls-files | grep -iE '_old\.|_legacy\.|_v1\.|\.bak$|_deprecated\.'
    Output: file list or "no deprecated files found"

  MS-INV-001-02-06: Classify .supervisor/ into cat 10 (schemas_config) with DECISION-C exclusion
    Action: identify .supervisor/project-memory.md; mark EXCLUDE;
            all other .supervisor/*.yaml/.json → cat 10
    Output: exclusion list documented

  MS-INV-001-02-07: Document all 5 DECISION-A through DECISION-E in 01-report.md §Ambiguous Cases

Acceptance checks: all 16 categories addressed; all 5 decisions documented; no file group uncategorized
Evidence: 01-loc-and-classification-report.md §Classification Rules + §Ambiguous Cases

---

Child Taskcard ID: TC-INV-001-03
Parent: TC-INV-001
Title: Compute ratios and write evidence/metrics.json
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-001
Dependencies: TC-INV-001-01 CLOSED, TC-INV-001-02 CLOSED

Purpose: Produce the structured evidence artifact that anchors all subsequent
  ratio claims.

Required metrics.json structure:
{
  "commit": "af879e550ee47f89dd7e805314f9b14923fbf100",
  "measured_at": "<ISO date>",
  "measurement_command": "git ls-files <path> | xargs wc -l",
  "exclusions": [".venv/", "build/", ".pytest_cache/", ".mypy_cache/", ".local/"],
  "categories": {
    "product_runtime_python_loc": <N>,
    "product_runtime_dotnet_loc": <N>,
    "product_runtime_total_loc": <N>,
    "supervisor_orchestration_loc": <N>,
    "governance_validation_loc": <N>,
    "spec_acquisition_loc": <N>,
    "capability_reasoning_loc": <N>,
    "tests_loc": <N>,
    "oracle_loc": <N>,
    "shared_infrastructure_loc": <N>,
    "schemas_config_loc": <N>,
    "docs_loc": <N>,
    "plans_loc": <N>,
    "supervisor_config_loc": <N>,
    "total_authored_loc": <N>,
    "total_tracked_files": <N>
  },
  "ratios": {
    "runtime_machinery_to_product": <float>,
    "all_machinery_to_product": <float>,
    "tests_to_production": <float>,
    "governance_to_mutation": <float>,
    "plans_to_product": <float>
  },
  "prior_assessment": {
    "machinery_claimed_loc": 81000,
    "product_claimed_loc": 72000,
    "verdict": "PARTIALLY_ACCURATE",
    "verdict_rationale": "<one paragraph>"
  }
}

Micro-steps:
  MS-INV-001-03-01: Compute all category LOC values from TC-INV-001-01 outputs
  MS-INV-001-03-02: Compute total_authored_loc (sum of cats 1-9; exclude plans, docs, config)
  MS-INV-001-03-03: Compute 5 ratios with float precision (2 decimal places)
  MS-INV-001-03-04: Write prior_assessment verdict and one-paragraph rationale
    Expected verdict: PARTIALLY_ACCURATE (direction correct; magnitudes ~10% off;
    framing missed tests=machinery and plans>product)
  MS-INV-001-03-05: Write evidence/metrics.json; validate as parseable JSON

Acceptance checks: valid JSON; all required fields present; ratios computed correctly
Evidence: evidence/metrics.json itself

---

Child Taskcard ID: TC-INV-001-04
Parent: TC-INV-001
Title: Write 01-loc-and-classification-report.md and evidence/file-classification.csv
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-001
Dependencies: TC-INV-001-03 CLOSED

Purpose: Produce the human-readable report and machine-readable CSV.

Required 01-report.md sections:
  §1  Executive Summary (2 paragraphs: what was measured, what the verdict is)
  §2  Measurement Methodology (commands used, exclusions, what git ls-files guarantees)
  §3  LOC by Category table (all 16 categories with file count and LOC)
  §4  Prior Assessment Verdict (PARTIALLY_ACCURATE with evidence)
  §5  Ambiguous Cases (DECISION-A through DECISION-E with rationale)
  §6  Top Files by Category (tables for top-15 in tools/supervisor/ and src/python/)
  §7  Key Ratios (5 ratios with interpretation)
  §8  Reproducibility Note (exact commands to reproduce at any HEAD)

Required file-classification.csv header:
  path,language,loc,category_id,category_name,classification_confidence,notes

Micro-steps:
  MS-INV-001-04-01: Write §1 Executive Summary
  MS-INV-001-04-02: Write §2 Measurement Methodology with exact commands
  MS-INV-001-04-03: Write §3 LOC by Category table (derive from metrics.json)
  MS-INV-001-04-04: Write §4 Prior Assessment Verdict with PARTIALLY_ACCURATE rationale
  MS-INV-001-04-05: Write §5 Ambiguous Cases (5 decisions)
  MS-INV-001-04-06: Write §6 Top Files tables for tools/supervisor/ and src/python/
  MS-INV-001-04-07: Write §7 Key Ratios with interpretation (what each ratio means)
  MS-INV-001-04-08: Write §8 Reproducibility Note
  MS-INV-001-04-09: Write evidence/file-classification.csv with all classified entries
    NOTE: At minimum, classify all files in tools/supervisor/ (top 50 by LOC) and all
    top-level directories. Full per-file classification for 15,875 files is NOT required;
    representative sampling with explicit note on coverage is acceptable.
  MS-INV-001-04-10: Reread 01-report.md completely after writing; fix gaps

Acceptance checks: all 8 sections present; CSV parseable; evidence/metrics.json referenced in §2
Evidence: 01-report.md + CSV paths in commands-and-results.md

---

## TC-INV-002: Machinery Architecture Reconstruction

Parent Taskcard ID: TC-INV-002
Title: Document current machinery architecture and trace 9 required workflows
Type: PARENT
Status: PROPOSED
Owner: investigator-agent
Supervisor: coordinator-lane
Plan requirement: REQ-INV-002
Source section: S-010
Dependencies: TC-INV-001 CLOSED

Objective: Reconstruct current machinery architecture purely from source evidence.
  Produce 3 Mermaid diagrams. Trace all 9 required workflows.

Outputs:
  - 02-current-machinery-architecture.md (3 Mermaid diagrams + component map)
  - 03-workflow-traces.md (9 workflow trace YAML blocks)

Child taskcards: TC-INV-002-01, TC-INV-002-02, TC-INV-002-03

Parent acceptance criteria:
  - 3 Mermaid diagrams present and syntactically valid
  - All 9 workflow traces present with required YAML fields
  - Each trace cites at least one file:line evidence reference
  - WF-006 correctly notes rework_orchestrator.py has no production callers
  - No workflow trace says "UNVERIFIED" without a documented MISSING reference

Rollback: delete 02-current-machinery-architecture.md and 03-workflow-traces.md

---

Child Taskcard ID: TC-INV-002-01
Parent: TC-INV-002
Title: Read targeted source sections and map component boundaries
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-002

Purpose: Read the specific sections of key files needed to produce accurate diagrams.
  Do NOT re-read content already established in VF-001..010.

Files to read (focused ranges):
  tools/supervisor/autonomous_cycle.py: lines 1-120 (overall flow); lines 2700-2768 (closeout)
  tools/supervisor/governance_validators.py: lines 1-80 (structure); lines 3200-3234 (exports)
  tools/supervisor/grade_declared_work.py: lines 36-111 (cache); lines 205-260 (LLM chain)
  tools/supervisor/sprint_executor.py: lines 561-628 (main + run-loop subcommand)
  tools/supervisor/autonomous_task_generator.py: lines 1-60 (purpose and generate function)
  tools/supervisor/next_action_runner.py: lines 32-65 (_build_default_backends) — already read
  tools/supervisor/continuation_selector.py: lines 1-40 (is it called by check_continuation?)
  tools/supervisor/continuation_router.py: lines 1-40 (is it called by check_continuation?)

Micro-steps:
  MS-INV-002-01-01: Read autonomous_cycle.py lines 1-120; record: main function names,
                    order of operations (validate → inspect → grade → plan-next → manifest)
  MS-INV-002-01-02: Read autonomous_cycle.py lines 2700-2768; record: control index sync call,
                    how it's invoked (--sync-index flag, best-effort)
  MS-INV-002-01-03: Read governance_validators.py lines 1-80; record: import structure,
                    is it a dispatch hub or does it contain validator logic?
  MS-INV-002-01-04: Read governance_validators.py lines 3200-3234; record: what's exported
  MS-INV-002-01-05: Read grade_declared_work.py lines 36-111; record: cache key structure,
                    TTL mechanism, fingerprinting threshold (500KB)
  MS-INV-002-01-06: Read grade_declared_work.py lines 205-260; record: LLM tier count,
                    fallback chain order
  MS-INV-002-01-07: Read sprint_executor.py lines 561-628; record: how run-loop works,
                    what command it invokes (claude --print), how it calls autonomous_cycle.py
  MS-INV-002-01-08: Read autonomous_task_generator.py lines 1-60; record purpose and
                    relationship to next-work-items.json
  MS-INV-002-01-09: Read continuation_selector.py lines 1-40 and continuation_router.py
                    lines 1-40; determine if check_continuation.py imports either
  MS-INV-002-01-10: Append all findings to evidence/commands-and-results.md §Architecture Reading

Acceptance checks: all 10 micro-steps COMPLETE; findings documented; no "I assume" statements
Evidence: evidence/commands-and-results.md §Architecture Reading

---

Child Taskcard ID: TC-INV-002-02
Parent: TC-INV-002
Title: Write 02-current-machinery-architecture.md with 3 Mermaid diagrams
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-002
Dependencies: TC-INV-002-01 CLOSED

Purpose: Produce the architecture document with verified Mermaid diagrams.

Required diagrams:
  Diagram 1 — Component Boundaries (flowchart LR):
    Nodes: src/ (product), sprint_executor.py, check_continuation.py, state files,
           next_action_runner.py, backend selector, claude subprocess,
           evidence-declaration.yaml, autonomous_cycle.py, governance_validator_runner.py,
           grade_declared_work.py, grade-cache.json, next-sprint.md
    Edges labeled with the data or call type

  Diagram 2 — State Ownership (flowchart TD):
    For each state file (.local/supervisor/*.json, approval-gates.md):
    Show: WRITER node(s) → FILE → READER node(s)
    Highlight: check_continuation.py reads ALL; no component validates consistency

  Diagram 3 — Execution Lifecycle (sequence diagram):
    sprint_executor → check_continuation → CONTINUE → next_action_runner →
    backend → claude subprocess → produces declaration →
    sprint_executor → autonomous_cycle → validates + grades + writes next-sprint →
    loop

Required additional sections in 02-architecture.md:
  §1  Architecture Overview (1 paragraph summary)
  §2  Component Boundary Map (table: component → responsibility → owned state files)
  §3  Three Mermaid Diagrams (with headers explaining each)
  §4  Critical Architectural Finding: State Consistency Gap (document RC-001 in architectural terms)
  §5  Machinery vs Product Boundary (where is the boundary; what crosses it)
  §6  Known Architectural Weaknesses (cross-reference P-002 through P-006 from problem catalog)

Micro-steps:
  MS-INV-002-02-01: Write §1 Architecture Overview
  MS-INV-002-02-02: Write §2 Component Boundary Map table
  MS-INV-002-02-03: Write Diagram 1 (Component Boundaries) as Mermaid flowchart LR
  MS-INV-002-02-04: Write Diagram 2 (State Ownership) as Mermaid flowchart TD
  MS-INV-002-02-05: Write Diagram 3 (Execution Lifecycle) as Mermaid sequenceDiagram
  MS-INV-002-02-06: Write §4 Critical Architectural Finding
  MS-INV-002-02-07: Write §5 Machinery vs Product Boundary
  MS-INV-002-02-08: Write §6 Known Architectural Weaknesses (forward-reference P-*)
  MS-INV-002-02-09: Reread 02-architecture.md; verify Mermaid syntax; fix gaps

Acceptance checks: 3 diagrams syntactically valid; all 6 sections present; no forward references unresolved
Evidence: file path in commands-and-results.md

---

Child Taskcard ID: TC-INV-002-03
Parent: TC-INV-002
Title: Write 03-workflow-traces.md with all 9 required workflow traces
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-002
Dependencies: TC-INV-002-01 CLOSED

Purpose: Document 9 workflows as structured YAML blocks with evidence.

Required YAML fields per trace:
  workflow_trace:
    trace_id: WF-NNN
    entry_point: <file:function>
    modules: []
    state_read: []
    state_written: []
    decisions: []
    validators: []
    evidence: [<file:line>]
    alternate_paths: []
    bypasses: []
    failure_behavior: <description>
    status: VERIFIED_FACT | STRONG_INFERENCE | WEAK_INFERENCE

9 traces:
  WF-001  spec → facts       (tools/spec/ → SAL → oracle/registry/)
  WF-002  facts → caps       (SAL → capability_layer → product-deepening-ledger.yaml)
  WF-003  caps → work        (ledger → autonomous_task_generator.py → next-work-items.json)
  WF-004  work → mutation    (next-work-items.json → sprint executor → src/ changes)
  WF-005  mutation → evidence (declaration.yaml → autonomous_cycle.py → evidence-review.json)
  WF-006  failure → repair   (rework_items → document that rework_orchestrator.py has NO production callers;
                               actual behavior: check_continuation returns CONTINUE on exit 3)
  WF-007  acceptance → closeout (check_continuation.py → continuation-signal.json)
  WF-008  Python product path (src/python/fods/ → tests/python/fods/ → oracle/formats/fods/)
  WF-009  .NET product path  (src/net/fods/ → tests/net/fods/)

Micro-steps:
  MS-INV-002-03-01: Write WF-001 trace (spec → facts)
  MS-INV-002-03-02: Write WF-002 trace (facts → capabilities)
  MS-INV-002-03-03: Write WF-003 trace (capabilities → work)
  MS-INV-002-03-04: Write WF-004 trace (work → mutation)
  MS-INV-002-03-05: Write WF-005 trace (mutation → evidence) — most important; document
                    all 5 phases of autonomous_cycle.py
  MS-INV-002-03-06: Write WF-006 trace (failure → repair) — CRITICAL: document that
                    rework_orchestrator.py is TEST-ONLY; document actual repair mechanism
  MS-INV-002-03-07: Write WF-007 trace (acceptance → closeout)
  MS-INV-002-03-08: Write WF-008 trace (Python product path through fods example)
  MS-INV-002-03-09: Write WF-009 trace (.NET product path through fods example)
  MS-INV-002-03-10: Reread 03-workflow-traces.md; verify all 9 traces; fix gaps

Acceptance checks: 9 traces present; each has all required YAML fields; no trace missing evidence
Evidence: 03-workflow-traces.md file

---

## TC-INV-003: Component Register

Parent Taskcard ID: TC-INV-003
Title: Classify each significant machinery component with evidence and disposition
Type: PARENT
Status: PROPOSED
Owner: investigator-agent
Supervisor: coordinator-lane
Plan requirement: REQ-INV-003
Source section: S-011
Dependencies: TC-INV-002 CLOSED

Outputs:
  - 04-machinery-component-register.md
  - evidence/component-register.csv

Child taskcards: TC-INV-003-01, TC-INV-003-02, TC-INV-003-03

Parent acceptance criteria:
  - All 50+ identified components classified
  - No component with SUSPECTED_GHOST or CONFIRMED_UNREACHABLE without production-caller evidence
  - No component with DELETE_AFTER_PROOF disposition without proof cited
  - Classification confidence recorded (HIGH/MED/LOW)
  - evidence/component-register.csv is parseable CSV

---

Child Taskcard ID: TC-INV-003-01
Parent: TC-INV-003
Title: Classify core orchestration and continuation components
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-003

Components to classify (with pre-investigation evidence already available):
  autonomous_cycle.py        ESSENTIAL_SAFETY_CRITICAL  confidence: HIGH
  check_continuation.py      ESSENTIAL_SAFETY_CRITICAL  confidence: HIGH (hardening needed)
  governance_validator_runner.py  ESSENTIAL_SAFETY_CRITICAL  confidence: HIGH
  supervisor_loop.py         ESSENTIAL_OVERCOMPLICATED  confidence: MEDIUM (verify legacy path)
  grade_declared_work.py     ESSENTIAL_SAFETY_CRITICAL  confidence: HIGH (cache bug noted)
  write_plan_lock.py         ESSENTIAL_SAFETY_CRITICAL  confidence: HIGH (atomicity gap noted)
  anti_skip_checker.py       USEFUL_SHARED_INFRASTRUCTURE  confidence: HIGH
  autonomous_task_generator.py  ESSENTIAL_OVERCOMPLICATED  confidence: MEDIUM
  generate_next_worker_prompt.py  ESSENTIAL_OVERCOMPLICATED  confidence: MEDIUM

  continuation_state.py      ESSENTIAL_SAFETY_CRITICAL  confidence: HIGH
  continuation_identity.py   ESSENTIAL_SAFETY_CRITICAL  confidence: HIGH
  continuation_ledger.py     USEFUL_SHARED_INFRASTRUCTURE  confidence: HIGH
  continuation_selector.py   USEFUL_SHARED_INFRASTRUCTURE  confidence: MEDIUM (verify callers)
  continuation_router.py     USEFUL_SHARED_INFRASTRUCTURE  confidence: MEDIUM (verify callers)
  evidence_continuation.py   USEFUL_SHARED_INFRASTRUCTURE  confidence: MEDIUM

Additional investigation needed for TC-INV-003-01:
  - Verify supervisor_loop.py still has legacy ZIP path (grep for ZIP or watcher pattern)
  - Verify continuation_selector.py and continuation_router.py callers

Micro-steps:
  MS-INV-003-01-01: Assign classification + confidence to autonomous_cycle.py; cite evidence
  MS-INV-003-01-02: Assign to check_continuation.py; note RC-001 hardening needed
  MS-INV-003-01-03: Assign to governance_validator_runner.py; note RC-003 issue
  MS-INV-003-01-04: Run `grep -n "zip\|ZIP\|watcher\|Watcher" tools/supervisor/supervisor_loop.py | head -10`
                    to verify legacy ZIP path; update classification confidence
  MS-INV-003-01-05: Run `grep -rn "continuation_selector\|ContinuationSelector" tools/supervisor/ | grep -v "^tools/supervisor/continuation_selector.py" | head -5`
                    to find callers of continuation_selector.py
  MS-INV-003-01-06: Same grep for continuation_router.py
  MS-INV-003-01-07: Assign classifications to remaining continuation files based on MS findings
  MS-INV-003-01-08: Record all classifications in component-register.csv rows

Acceptance checks: 15 core components classified; all have evidence cited; CSV rows created

---

Child Taskcard ID: TC-INV-003-02
Parent: TC-INV-003
Title: Classify backends, autonomous variants, governance validators, and infrastructure
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-003
Dependencies: TC-INV-003-01 CLOSED

Components to classify:

8 BACKENDS (pre-investigation evidence):
  local_deterministic_backend.py   ESSENTIAL_SAFETY_CRITICAL  [always loaded]
  llm_api_backend.py               USEFUL_SHARED_INFRASTRUCTURE [CONDITIONAL_ACTIVE]
  task_master_backend.py           COMPATIBILITY_ONLY [CONDITIONAL_ACTIVE, MCP mode]
  mcp_superpowers_backend.py       COMPATIBILITY_ONLY [CONDITIONAL_ACTIVE, MCP mode]
  superpowers_skill_backend.py     COMPATIBILITY_ONLY [CONDITIONAL_ACTIVE, priority 0]
  cognee_memory_backend.py         DOCUMENTED_NEGATIVE_SPACE [BLOCKED_BY_DESIGN, 53 LOC]
  skill_seekers_backend.py         DOCUMENTED_NEGATIVE_SPACE [BLOCKED_BY_DESIGN, 48 LOC]
  session_skill_backend.py         DOCUMENTED_NEGATIVE_SPACE [BLOCKED_BY_DESIGN, 68 LOC]

6 AUTONOMOUS VARIANTS (pre-investigation evidence):
  autonomous_poc_controller.py     SUSPECTED_GHOST [no prod callers; tests exist; CHARACTERIZE]
  autonomous_train_executor.py     SUSPECTED_GHOST [no prod callers; tests exist]
  autonomous_host_runner.py        SUSPECTED_GHOST [no prod callers; tests exist]
  autonomous_host_daemon.py        SUSPECTED_GHOST [no prod callers; tests exist]
  tri_lane_integration.py          SUSPECTED_GHOST [no prod callers; tests exist]
  rework_orchestrator.py           SUSPECTED_GHOST [no prod callers; tests exist]

GOVERNANCE VALIDATORS (20 files):
  governance_validators.py (3,234 LOC)   ESSENTIAL_OVERCOMPLICATED
  governance_validators_ext*.py (4 files) ESSENTIAL_SAFETY_CRITICAL
  governance_validators_contract.py       USEFUL_SHARED_INFRASTRUCTURE
  governance_validators_dotnet*.py        USEFUL_SHARED_INFRASTRUCTURE
  governance_validators_spec.py           ESSENTIAL_SAFETY_CRITICAL
  governance_validators_sal.py            ESSENTIAL_SAFETY_CRITICAL
  governance_validators_*signal/path/release/oracle (6 files) USEFUL_SHARED_INFRASTRUCTURE

INFRASTRUCTURE (control index 26 files, concurrency 4 files):
  All → USEFUL_SHARED_INFRASTRUCTURE (verify specific callers of concurrency subsystem)

Micro-steps:
  MS-INV-003-02-01: Assign classifications + disposition to all 8 backends; note BLOCKED_BY_DESIGN
                    for 3 blocked backends; document LOC (169 total safe to retire if behavior
                    documented in ADR)
  MS-INV-003-02-02: Assign SUSPECTED_GHOST to 6 autonomous variants; note CHARACTERIZE required;
                    record test file LOC alongside source LOC
  MS-INV-003-02-03: Assign classifications to 20 governance validator files
  MS-INV-003-02-04: Verify concurrency subsystem callers:
                    `grep -rn "from.*concurrency\|import.*checkpoint\|import.*mission_lock" tools/supervisor/ | grep -v concurrency/ | head -10`
  MS-INV-003-02-05: Classify control index 26 files as USEFUL_SHARED_INFRASTRUCTURE
  MS-INV-003-02-06: Create all CSV rows for above components

Acceptance checks: all 50+ components have CSV rows; no SUSPECTED_GHOST without caller-search evidence

---

Child Taskcard ID: TC-INV-003-03
Parent: TC-INV-003
Title: Write 04-machinery-component-register.md
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-003
Dependencies: TC-INV-003-02 CLOSED

Purpose: Produce the human-readable register with summaries by classification.

Required sections:
  §1  Component Register Summary table (classification → count → total LOC → example files)
  §2  ESSENTIAL_SAFETY_CRITICAL components (full detail for each)
  §3  ESSENTIAL_OVERCOMPLICATED components (full detail + what makes them overcomplicated)
  §4  SUSPECTED_GHOST components (with evidence that no production callers exist)
  §5  DOCUMENTED_NEGATIVE_SPACE components (3 blocked backends; why they encode rules)
  §6  USEFUL_SHARED_INFRASTRUCTURE summary
  §7  COMPATIBILITY_ONLY summary (4 conditional backends)
  §8  Key Findings (3-5 most important findings from component classification)
  §9  Disposition Summary (RETAIN / CHARACTERIZE / INVESTIGATE / RETIRE counts)

Micro-steps:
  MS-INV-003-03-01: Write §1 Summary table from CSV data
  MS-INV-003-03-02: Write §2 ESSENTIAL_SAFETY_CRITICAL components (9 core + 5 continuation + spec validators)
  MS-INV-003-03-03: Write §3 ESSENTIAL_OVERCOMPLICATED (5 files; explain complexity source)
  MS-INV-003-03-04: Write §4 SUSPECTED_GHOST (6 variants; evidence of no callers; CHARACTERIZE note)
  MS-INV-003-03-05: Write §5 DOCUMENTED_NEGATIVE_SPACE (3 blocked backends; document why they exist)
  MS-INV-003-03-06: Write §6 and §7 summaries
  MS-INV-003-03-07: Write §8 Key Findings
  MS-INV-003-03-08: Write §9 Disposition Summary
  MS-INV-003-03-09: Reread 04-register.md; verify all cited file paths exist; fix gaps

Acceptance checks: all 9 sections; disposition summary totals match CSV row count; file self-contained

---

## TC-INV-004: Problem Catalog

Parent Taskcard ID: TC-INV-004
Title: Document all structural problems with precise evidence and root causes
Type: PARENT
Status: PROPOSED
Owner: investigator-agent
Supervisor: coordinator-lane
Plan requirement: REQ-INV-004
Source section: S-012
Dependencies: TC-INV-003 CLOSED

Outputs: 05-problem-catalog.md

12 problems to document (P-001 through P-012):
  P-001  LOC Assessment Undercount (severity: LOW; root: measurement_error)
  P-002  State Authority Fragmentation (severity: HIGH; root: RC-001)
  P-003  Non-Atomic Lock Collection (severity: HIGH; root: RC-005)
  P-004  State Mutation During Read — Check 5 (severity: MEDIUM; root: RC-005)
  P-005  Prompt-Only Enforcement of Critical Rules (severity: HIGH; root: RC-002)
  P-006  Validator Count Fragile Invariant (severity: HIGH; root: RC-003)
  P-007  Grade Cache TTL Bypass (severity: MEDIUM; root: RC-004)
  P-008  Self-Certified Evidence with Heuristic Verification (severity: MEDIUM; root: RC-004)
  P-009  Six Autonomous Variants Without Production Callers (severity: LOW-MED; root: additive growth)
  P-010  governance_validators.py Monolithic Size (severity: MEDIUM; root: incremental addition)
  P-011  lifecycle_audit.py Taskcard Parsing Fragility (severity: MEDIUM; root: organic format growth)
  P-012  Missing Observability — Validator Invocation per Declaration (severity: MEDIUM; root: aggregate-only logging)

Child taskcards: TC-INV-004-01, TC-INV-004-02

---

Child Taskcard ID: TC-INV-004-01
Parent: TC-INV-004
Title: Write P-001 through P-006 in 05-problem-catalog.md
Type: CHILD
Status: TODO

Required YAML format for each problem:
  problem_id: P-NNN
  title: <short title>
  category: <category>
  severity: CRITICAL|HIGH|MEDIUM|LOW|INFORMATIONAL
  confidence: HIGH|MEDIUM|LOW
  affected_paths: [<file:line>, ...]
  evidence: [<VF-reference>, <file:line>]
  root_cause: <RC-reference + 1-2 sentences>
  impact: <what breaks in production>
  affected_qualities: [<quality>]
  related_problems: [<P-reference>]
  strategy: <REDESIGN-reference>
  change_risk: HIGH|MEDIUM|LOW
  prerequisites: []
  proof_required: <if confidence < HIGH>

Micro-steps:
  MS-INV-004-01-01: Write P-001 (LOC undercount; severity LOW; strategy: none needed)
  MS-INV-004-01-02: Write P-002 (state fragmentation; severity HIGH; evidence: VF-002, VF-003;
                    strategy: REDESIGN-002 state integrity pre-check)
  MS-INV-004-01-03: Write P-003 (non-atomic lock; severity HIGH; evidence: VF-004;
                    strategy: REDESIGN-003)
  MS-INV-004-01-04: Write P-004 (Check 5 state mutation; severity MEDIUM; evidence: VF-003;
                    strategy: REDESIGN-003 related)
  MS-INV-004-01-05: Write P-005 (prompt-only enforcement; severity HIGH; evidence: VF-009;
                    strategy: REDESIGN-002 partially; NOTE: not fully solvable without
                    restructuring how CLAUDE.md and code interact)
  MS-INV-004-01-06: Write P-006 (validator count fragile; severity HIGH; evidence: VF-005;
                    strategy: REDESIGN-001)

Acceptance checks: 6 problems documented with all required fields; evidence references valid

---

Child Taskcard ID: TC-INV-004-02
Parent: TC-INV-004
Title: Write P-007 through P-012 in 05-problem-catalog.md; add catalog header
Type: CHILD
Status: TODO
Dependencies: TC-INV-004-01 CLOSED

Micro-steps:
  MS-INV-004-02-01: Write P-007 (cache TTL bypass; evidence: VF-006; strategy: REDESIGN-004)
  MS-INV-004-02-02: Write P-008 (self-certified evidence; evidence: anti_skip_checker.py heuristics;
                    strategy: REDESIGN-005)
  MS-INV-004-02-03: Write P-009 (6 autonomous variants; evidence: VF-007; strategy: INVESTIGATE;
                    proof_required: "Read each variant's test file to determine if behavioral
                    specs are unique to those tests")
  MS-INV-004-02-04: Write P-010 (governance_validators.py monolithic; evidence: 3,234 LOC;
                    strategy: REDESIGN-001 partially)
  MS-INV-004-02-05: Write P-011 (lifecycle_audit parsing; evidence: VF-010;
                    strategy: TC-EXP-S7-004 from hardened plan)
  MS-INV-004-02-06: Write P-012 (missing observability; evidence: governance_validator_runner.py
                    returns aggregate only; strategy: TC-EXP-S1-002)
  MS-INV-004-02-07: Write catalog §Introduction (problem count by severity; worst-5 summary)
  MS-INV-004-02-08: Write catalog §Severity Matrix table (problem × quality × root-cause grid)
  MS-INV-004-02-09: Reread 05-problem-catalog.md; verify all 12 problems; fix gaps

Acceptance checks: 12 problems; all have evidence, root_cause, strategy; severity matrix present

---

## TC-INV-005: Guarantee Control Matrix

Parent Taskcard ID: TC-INV-005
Title: Map all 20 system guarantees to enforcing components with current status
Type: PARENT
Status: PROPOSED
Owner: investigator-agent
Supervisor: coordinator-lane
Plan requirement: REQ-INV-005
Source section: S-013
Dependencies: TC-INV-004 CLOSED
Output: 06-guarantee-control-matrix.md

Objective: Produce a complete mapping of G-001..G-020 to enforcing components, current enforcement
  status, and failure consequence. Pre-established statuses from Part II analysis must be cited.
  Any status that differs from Part II analysis requires new source evidence.

Required YAML format per guarantee:
  guarantee_id: G-NNN
  title: <guarantee title>
  description: <what the system promises>
  enforcing_components: [<file:function or component name>]
  status: ENFORCED | PARTIAL | PROMPT_ONLY | ABSENT
  status_evidence: [<VF-reference or file:line>]
  failure_consequence: <what breaks when this guarantee is violated>
  redesign_reference: <REDESIGN-NNN or "none">
  related_problems: [<P-NNN>]

Parent acceptance criteria:
  - All 20 guarantees documented with all required YAML fields
  - Status for G-001, G-006, G-011 matches Part II analysis (PARTIAL, ABSENT, PARTIAL)
  - ENFORCED guarantees cite at least one file:function reference
  - PARTIAL/ABSENT guarantees reference at least one VF-NNN or P-NNN
  - §Summary table shows breakdown by status (count per status category)
  - §Critical Gaps section lists ABSENT and most-consequential PARTIAL guarantees

Rollback: delete 06-guarantee-control-matrix.md

---

Child Taskcard ID: TC-INV-005-01
Parent: TC-INV-005
Title: Write G-001 through G-010 in 06-guarantee-control-matrix.md
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-005

Purpose: Document first 10 guarantees with enforcing_components, status, and failure_consequence.
  Source all statuses from Part II §System Guarantees unless new evidence contradicts.

Scope:
  Allowed: write to 06-guarantee-control-matrix.md only; append to commands-and-results.md
  Forbidden: modify any source file; modify any other investigation file

Micro-steps:
  MS-INV-005-01-01: Write file header and §Introduction
    Action: create 06-guarantee-control-matrix.md; write header (authoritative_plan reference,
            REQ-INV-005, TC-INV-005); write §Introduction explaining the 20 guarantees scope
            and the 4 status categories (ENFORCED/PARTIAL/PROMPT_ONLY/ABSENT)
    Completion check: file exists; header and §Introduction present
    Next: MS-INV-005-01-02

  MS-INV-005-01-02: Write G-001 (SESSION_ISOLATION)
    Action: write YAML block for G-001; enforcing_components from Part II; status: PARTIAL;
            cite VF-002 (active-continuation.json stale) and check_continuation.py Check 0;
            failure_consequence: wrong-session sprint execution
    Completion check: G-001 block complete with all required fields
    Next: MS-INV-005-01-03

  MS-INV-005-01-03: Write G-002 (SPRINT_REPEATABILITY)
    Action: write YAML block; status: PARTIAL; cite VF-006 (grade cache TTL bypass);
            redesign_reference: REDESIGN-004; related_problems: [P-007]
    Completion check: G-002 complete
    Next: MS-INV-005-01-04

  MS-INV-005-01-04: Write G-003 (PLAN_LOCK_PRECEDENCE)
    Action: write YAML block; status: PROMPT_ONLY; cite VF-009 (write_plan_lock.py call
            is agent-cooperative); cite check_continuation.py Check 1b as partial enforcement;
            redesign_reference: REDESIGN-003 (atomicity) and REDESIGN-002 (integrity)
            related_problems: [P-003, P-005]
    Completion check: G-003 complete
    Next: MS-INV-005-01-05

  MS-INV-005-01-05: Write G-004 (GOVERNANCE_COMPLETENESS)
    Action: write YAML block; status: PARTIAL; cite VF-005 (bare except at lines 384, 792, 895);
            cite governance_validator_runner.py line 813 (expected_count=167);
            redesign_reference: REDESIGN-001; related_problems: [P-006]
    Completion check: G-004 complete
    Next: MS-INV-005-01-06

  MS-INV-005-01-06: Write G-005 (DECLARATION_SCHEMA_VALIDITY)
    Action: write YAML block; status: ENFORCED; cite sprint_executor_validate.py;
            cite autonomous_cycle.py Phase 1 validate step
    Completion check: G-005 complete
    Next: MS-INV-005-01-07

  MS-INV-005-01-07: Write G-006 (STATE_AUTHORITY_ORDERING)
    Action: write YAML block; status: ABSENT; cite RC-001 and VF-002;
            note: no cross-validation exists before continuation verdict;
            redesign_reference: REDESIGN-002; related_problems: [P-002]
    Completion check: G-006 complete — this is the ONLY ABSENT guarantee; flag prominently
    Next: MS-INV-005-01-08

  MS-INV-005-01-08: Write G-007 (PER_FILE_WRITE_ATOMICITY)
    Action: write YAML block; status: ENFORCED; cite atomic_io.py;
            note: per-file only; cross-file atomicity is a separate concern (G-010)
    Completion check: G-007 complete
    Next: MS-INV-005-01-09

  MS-INV-005-01-09: Write G-008 (ORACLE_DETERMINISM)
    Action: write YAML block; status: ENFORCED; cite execute_oracle.py and 73/73 PASS;
            cite oracle/formats/*/oracle-package.yaml
    Completion check: G-008 complete
    Next: MS-INV-005-01-10

  MS-INV-005-01-10: Write G-009 (EVIDENCE_SUFFICIENCY)
    Action: write YAML block; status: PARTIAL; cite anti_skip_checker.py (19 heuristics,
            field-existence only); cite RC-004; note oracle is only true anti-skip gate;
            redesign_reference: REDESIGN-005; related_problems: [P-008]
    Completion check: G-009 complete
    Next: MS-INV-005-01-11

  MS-INV-005-01-11: Write G-010 (INTERRUPTION_RECOVERY)
    Action: write YAML block; status: PARTIAL; cite atomic_io.py (per-file OK);
            cite RC-005 (cross-file NOT atomic); related_problems: [P-002, P-003, P-004]
    Completion check: G-010 complete
    Next: TC-INV-005-02

Acceptance checks: G-001..G-010 all present; all have required YAML fields;
  G-006 flagged as ABSENT; G-007/G-008 flagged as ENFORCED with evidence cited
Evidence: 06-guarantee-control-matrix.md §G-001 through §G-010

---

Child Taskcard ID: TC-INV-005-02
Parent: TC-INV-005
Title: Write G-011 through G-020; write summary sections; reread and verify
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-005
Dependencies: TC-INV-005-01 CLOSED

Micro-steps:
  MS-INV-005-02-01: Write G-011 (TERMINAL_LOCK_FINALITY)
    Action: write YAML block; status: PARTIAL; cite VF-004 (non-atomic lock collection);
            cite VF-009 (write_plan_lock.py is prompt-cooperative); cite check_continuation.py Check 1b;
            related_problems: [P-003, P-005]
    Next: MS-INV-005-02-02

  MS-INV-005-02-02: Write G-012 (ITERATION_COUNTER_ROLLOVER)
    Action: write YAML block; status: PARTIAL; cite VF-003 (Check 5 writes state during read);
            note: reset succeeds if no crash; crash leaves iteration at old value;
            related_problems: [P-004]
    Next: MS-INV-005-02-03

  MS-INV-005-02-03: Write G-013 (DECISION_AUDITABILITY)
    Action: write YAML block; status: PARTIAL; note: verdict+reason logged to continuation-signal.json
            but state inputs NOT captured; no state-consistency-log exists yet (TC-EXP-S1-001 would add it)
    Next: MS-INV-005-02-04

  MS-INV-005-02-04: Write G-014 (AUTONOMOUS_CONTINUATION)
    Action: write YAML block; status: PARTIAL; cite CCI-MVP degradation on session lag;
            cite active-continuation.json lag (VF-002); related_problems: [P-002]
    Next: MS-INV-005-02-05

  MS-INV-005-02-05: Write G-015 (GRADE_CACHE_FRESHNESS)
    Action: write YAML block; status: PARTIAL; cite VF-006 (malformed _cached_at bypass);
            redesign_reference: REDESIGN-004; related_problems: [P-007]
    Next: MS-INV-005-02-06

  MS-INV-005-02-06: Write G-016 (HUMAN_APPROVAL_GATE)
    Action: write YAML block; status: ENFORCED (Gate 11) / PROMPT_ONLY (plan precedence aspect);
            note dual nature — Gate 11 execution is properly gated; plan precedence is VF-009;
            related_problems: [P-005]
    Next: MS-INV-005-02-07

  MS-INV-005-02-07: Write G-017 (BACKEND_SELECTION_CORRECTNESS)
    Action: write YAML block; status: ENFORCED; cite next_action_runner.py _build_default_backends();
            cite local_deterministic_backend.py always-loaded pattern
    Next: MS-INV-005-02-08

  MS-INV-005-02-08: Write G-018 (GOVERNANCE_ANTI_SKIP_COVERAGE)
    Action: write YAML block; status: PARTIAL; cite anti_skip_checker.py 19 heuristics;
            note field-existence vs semantic correctness gap; cite RC-004; related_problems: [P-008]
    Next: MS-INV-005-02-09

  MS-INV-005-02-09: Write G-019 (VALIDATOR_COUNT_INTEGRITY)
    Action: write YAML block; status: PARTIAL; cite VF-005 (expected_count=167 vs test >= 154);
            cite bare except lines 384, 792, 895; redesign_reference: REDESIGN-001;
            related_problems: [P-006]
    Next: MS-INV-005-02-10

  MS-INV-005-02-10: Write G-020 (LIFECYCLE_AUDIT_COMPLETENESS)
    Action: write YAML block; status: PARTIAL; cite VF-010 (two-column table required;
            typo → silent miss); related_problems: [P-011]
    Next: MS-INV-005-02-11

  MS-INV-005-02-11: Write §Summary table
    Action: write table: status category | count | guarantee IDs
            ENFORCED: 5 (G-005, G-007, G-008, G-016-Gate11, G-017)
            PARTIAL: 13 (G-001, G-002, G-004, G-009..G-015, G-018..G-020)
            PROMPT_ONLY: 1 (G-003; G-016 plan-precedence aspect)
            ABSENT: 1 (G-006)
    Next: MS-INV-005-02-12

  MS-INV-005-02-12: Write §Critical Gaps section
    Action: write prose: G-006 is the only ABSENT guarantee; its absence is the root of RC-001;
            highest-priority PARTIAL guarantees for fixing: G-003 (prompt-only; risk of plan drift),
            G-004 (silent validator loss), G-011 (terminal lock can be bypassed)
    Next: MS-INV-005-02-13

  MS-INV-005-02-13: Reread 06-guarantee-control-matrix.md completely; verify all 20 guarantees; fix gaps
    Action: read entire file; check every G-NNN block has all required fields;
            verify status counts in §Summary match actual block statuses; fix any gap
    Completion check: 20 blocks present; summary counts verified; no UNRESOLVED fields

Acceptance checks: all 20 guarantees with all required YAML fields; §Summary counts correct;
  §Critical Gaps identifies G-006 and top 3 PARTIAL priorities
Evidence: 06-guarantee-control-matrix.md

---

## TC-INV-006: Risk Register

Parent Taskcard ID: TC-INV-006
Title: Document risks introduced by each proposed consolidation change
Type: PARENT
Status: PROPOSED
Owner: investigator-agent
Supervisor: coordinator-lane
Plan requirement: REQ-INV-006
Source section: S-014
Dependencies: TC-INV-005 CLOSED
Output: 07-risk-register.md

Objective: For each of the 5 REDESIGN-NNN proposals, document the risk introduced by the change
  itself — separate from the problem it solves. Every risk needs: likelihood, impact, mitigation,
  and residual risk after mitigation.

Required YAML format per risk:
  risk_id: R-NNN
  title: <risk title>
  triggered_by: <REDESIGN-NNN>
  problem_addressed: <P-NNN>
  risk_description: <what can go wrong during or after the change>
  likelihood: 1-5 (1=rare, 5=almost certain)
  impact: 1-5 (1=cosmetic, 5=data loss or system halt)
  risk_score: likelihood * impact
  mitigation: <how to reduce likelihood or impact>
  residual_risk: <what remains after mitigation>
  detection: <how to detect if the risk materializes>
  rollback: <how to recover if it does>

Parent acceptance criteria:
  - R-001 through R-005 all documented with all required YAML fields
  - Risk scores computed (likelihood × impact)
  - R-003 (false positive rate) is rated highest risk score (most consequential)
  - §Risk Matrix table present (risk_id × likelihood × impact × score × priority)
  - §Residual Risk summary present
  - All R-NNN reference their REDESIGN-NNN and P-NNN

Rollback: delete 07-risk-register.md

---

Child Taskcard ID: TC-INV-006-01
Parent: TC-INV-006
Title: Write R-001 through R-005 in 07-risk-register.md
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-006

Micro-steps:
  MS-INV-006-01-01: Write file header and §Introduction
    Action: create 07-risk-register.md; write header (authoritative_plan, REQ-INV-006, TC-INV-006);
            write §Introduction explaining these are migration-introduced risks, not existing problems
    Completion check: file created with header and §Introduction
    Next: MS-INV-006-01-02

  MS-INV-006-01-02: Write R-001 (validator registry → silent skip if importable but not registered)
    Action: write YAML block; triggered_by: REDESIGN-001; problem_addressed: P-006;
            risk: new validator added to codebase but not added to .supervisor/validator-registry.yaml →
            validator runs but expected_count unchanged → no detection;
            likelihood: 3 (engineers forget registry update); impact: 3 (governance gap)
            mitigation: pre-commit hook that counts validator functions vs registry count;
            detection: registry count drift in CI; rollback: revert registry file
    Next: MS-INV-006-01-03

  MS-INV-006-01-03: Write R-002 (CI breaks if validator added without registry update)
    Action: write YAML block; triggered_by: REDESIGN-001; problem_addressed: P-006;
            risk: test assertion changes from >= 154 to exact registry count → any count drift fails CI;
            likelihood: 4 (frequent validator additions per sprint); impact: 2 (CI noise, not silent failure)
            mitigation: dual_execution period (2 sprints running old + new count in parallel before switching)
            detection: CI red on count mismatch; rollback: revert test assertion to >= count
    Next: MS-INV-006-01-04

  MS-INV-006-01-04: Write R-003 (state integrity pre-check false-positive rate blocks continuation)
    Action: write YAML block; triggered_by: REDESIGN-002; problem_addressed: P-002;
            risk: state_integrity_check() in BLOCK mode fires on legitimate state transitions
            (e.g., active-continuation.json lags after session boundary) → autonomous loop halts;
            likelihood: 3 (lag is known to occur; see VF-002); impact: 4 (loop halt requires human restart)
            mitigation: deploy in WARN mode first for 10+ sessions; only switch to BLOCK after
            false-positive rate measured; require human authorization for mode switch (G-016);
            detection: WARN log entries without corresponding actual incoherence;
            rollback: remove state_integrity_check() call (one line); return to prior behavior
            NOTE: this is rated highest priority risk — deploy must follow observability-first (S1-001)
    Next: MS-INV-006-01-05

  MS-INV-006-01-05: Write R-004 (atomic lock on Windows NTFS — lockfile advisory not exclusive)
    Action: write YAML block; triggered_by: REDESIGN-003; problem_addressed: P-003;
            risk: on Windows NTFS, advisory lockfiles (.collection.lock) are not enforced by OS;
            two processes can write plan-locks/current.json simultaneously; version field helps
            detect but not prevent collision;
            likelihood: 2 (sprint_executor and agent rarely write simultaneously);
            impact: 3 (write collision corrupts current.json → lock state unreadable)
            mitigation: prefer single-versioned current.json (one atomic read/write) over advisory
            lockfile; atomic_io.py temp-then-rename provides Windows-safe atomicity per-write;
            detection: version field out-of-sequence; current.json parse failure;
            rollback: revert to glob-based collection (no lockfile dependency)
    Next: MS-INV-006-01-06

  MS-INV-006-01-06: Write R-005 (oracle gating blocks acceptance for formats without oracle)
    Action: write YAML block; triggered_by: REDESIGN-005; problem_addressed: P-008;
            risk: OBLIGATION_CREATED formats (ora/pam/xpm/zpaq) cannot reach ACCEPTED_VERIFIED
            even when work is structurally correct because no oracle exists yet;
            likelihood: 5 (4 formats at OBLIGATION_CREATED); impact: 2 (downgrade to
            ACCEPTED_WITH_LIMITATIONS, not rejection); mitigation: OBLIGATION_CREATED exception
            already designed into REDESIGN-005; must verify oracle_status field before gating;
            detection: ACCEPTED_WITH_LIMITATIONS rate spike for known OBLIGATION_CREATED formats;
            rollback: revert oracle_evidence_present field and grade outcome branch

Acceptance checks: R-001 through R-005 all complete; all have likelihood, impact, mitigation,
  residual_risk, detection, rollback; R-003 notes WARN-mode-first requirement
Evidence: 07-risk-register.md §R-001 through §R-005

---

Child Taskcard ID: TC-INV-006-02
Parent: TC-INV-006
Title: Write §Risk Matrix, §Residual Risk Summary, §Introduction; reread and verify
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-006
Dependencies: TC-INV-006-01 CLOSED

Micro-steps:
  MS-INV-006-02-01: Write §Risk Matrix table
    Action: write table with columns: risk_id | triggered_by | likelihood | impact | score | priority
            R-001: 3×3=9  MEDIUM
            R-002: 4×2=8  MEDIUM
            R-003: 3×4=12 HIGH (highest score)
            R-004: 2×3=6  LOW-MEDIUM
            R-005: 5×2=10 MEDIUM-HIGH
    Completion check: table present; scores computed; R-003 ranked highest

  MS-INV-006-02-02: Write §Residual Risk Summary
    Action: write prose: after mitigations, R-003 residual (false-positive in WARN mode) is
            acceptable; R-005 residual (OBLIGATION_CREATED downgrade) is expected by design;
            R-004 residual (NTFS advisory) mitigated by single-file approach + atomic_io.py;
            net residual risk across R-001..R-005 is LOW if WARN-mode-first sequence followed

  MS-INV-006-02-03: Write §Introduction (reorder to appear before risk entries)
    Action: prepend §Introduction to file (before R-001): explain these are risks introduced
            by the changes, not existing risks; reference REDESIGN-001 through REDESIGN-005

  MS-INV-006-02-04: Reread 07-risk-register.md completely; verify all 5 risks; fix gaps
    Action: read entire file; check R-001..R-005 all have required YAML fields;
            check matrix scores are correct; fix any field gap
    Completion check: 5 risk blocks present; matrix present; residual summary present

Acceptance checks: all 5 risks present; §Risk Matrix with scores; §Residual Risk Summary;
  R-003 identified as highest-priority; rollback defined for all 5
Evidence: 07-risk-register.md

---

## TC-INV-007: Architecture Options

Parent Taskcard ID: TC-INV-007
Title: Compare 7 architecture strategies and produce recommendation
Type: PARENT
Status: PROPOSED
Owner: investigator-agent
Supervisor: coordinator-lane
Plan requirement: REQ-INV-007
Source section: S-015
Dependencies: TC-INV-006 CLOSED
Output: 08-target-architecture-options.md

Objective: For each of 7 architecture strategies, document benefits, risks, migration cost,
  verification difficulty, rollback, complexity reduction, governance impact, and suitability.
  Conclude with a recommendation: S2+S3 primary, limited S6 for blocked backends only.

Required section format per strategy:
  ## Strategy SN: <title>
  Suitability: RECOMMENDED | VIABLE | NOT_RECOMMENDED_NOW | NOT_RECOMMENDED
  Benefits: []
  Risks: []
  Migration cost: LOW | MEDIUM | HIGH (with rationale)
  Verification difficulty: LOW | MEDIUM | HIGH
  Rollback: <how to revert>
  Complexity reduction: <quantitative estimate where possible>
  Governance impact: <positive or negative effect on governance guarantees>
  Problems addressed: [P-NNN, ...]
  Prerequisite strategies: [SN, ...]

Parent acceptance criteria:
  - All 7 strategies present with all required fields
  - S1 explicitly rated NOT_SUFFICIENT (not just NOT_RECOMMENDED)
  - S7 (rewrite) explicitly argues against with 89,524 LOC test replication rationale
  - §Recommendation section present: states S2+S3 as primary; S6 limited scope
  - §Strategy Comparison Matrix table present (7 strategies × 5 dimensions)
  - Suitability verdict justified with evidence for each strategy

Rollback: delete 08-target-architecture-options.md

---

Child Taskcard ID: TC-INV-007-01
Parent: TC-INV-007
Title: Write strategies S1 through S4 in 08-target-architecture-options.md
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-007

Micro-steps:
  MS-INV-007-01-01: Write file header and §Introduction
    Action: create 08-target-architecture-options.md; write header; write §Introduction explaining
            these are forward-looking strategies — none are authorized for execution from this document
    Completion check: file created with header and §Introduction
    Next: MS-INV-007-01-02

  MS-INV-007-01-02: Write S1 (Retain and Document)
    Action: write §Strategy S1 with all required fields;
            Suitability: NOT_SUFFICIENT (addresses none of P-002..P-006);
            Benefits: zero migration risk; zero disruption; documents current state;
            Risks: problems persist; G-006 remains ABSENT; false CONTINUE risk unchanged;
            Migration cost: LOW (documentation only); Verification: trivial;
            Governance impact: NEGATIVE (G-004/G-019 fragility persists);
            Complexity reduction: NONE; Problems addressed: P-001 only (documentation)
    Next: MS-INV-007-01-03

  MS-INV-007-01-03: Write S2 (Incremental Consolidation — REDESIGN-001 + REDESIGN-003 + REDESIGN-004)
    Action: write §Strategy S2; Suitability: RECOMMENDED (primary);
            Benefits: addresses P-003 (atomic lock), P-006 (validator registry), P-007 (cache TTL);
            each change independently reversible; LOW-MEDIUM migration risk; no behavioral change
            for valid inputs; LOC reduction: 169 confirmed (blocked backends) + structural improvements;
            Risks: R-001 (registry drift), R-002 (CI friction), R-004 (NTFS advisory);
            Migration cost: MEDIUM (3 separate changes with tests); Verification: MEDIUM (needs
            concurrent-write test for lock, malformed-timestamp test for cache);
            Rollback: revert each change independently; Problems addressed: P-003, P-006, P-007
    Next: MS-INV-007-01-04

  MS-INV-007-01-04: Write S3 (Strangler Replacement for State Integrity — REDESIGN-002 warn-first)
    Action: write §Strategy S3; Suitability: RECOMMENDED (secondary, after S2 stable);
            Benefits: addresses root cause of G-006 (ABSENT) and P-002;
            WARN mode first prevents false-positive disruption; provides 10+ sessions of data
            before BLOCK mode decision;
            Risks: R-003 (false-positive rate unknown until measured);
            Migration cost: MEDIUM (state_integrity_check() function + logging + 2-mode flag);
            Prerequisite: TC-EXP-S1-001 (logging) must run for 10+ sessions first;
            Rollback: remove state_integrity_check() call from check_continuation.py top;
            Governance impact: STRONGLY POSITIVE (addresses G-006 ABSENT, the only absent guarantee);
            Problems addressed: P-002, P-004 (partially), P-005 (partially)
    Next: MS-INV-007-01-05

  MS-INV-007-01-05: Write S4 (Extract Independent Libraries)
    Action: write §Strategy S4; Suitability: NOT_RECOMMENDED_NOW;
            rationale: requires S2+S3 stable as prerequisite; extracting orchestration logic
            while state bugs exist would extract the bugs too; LOC benefit is real (~12K ESSENTIAL_OVERCOMPLICATED)
            but payable only after integrity guarantees are restored;
            Migration cost: HIGH (package boundaries, import rewiring, CI changes);
            Prerequisite strategies: [S2, S3]; Problems addressed: P-010 (partially)
    Next: TC-INV-007-02

Acceptance checks: S1..S4 all present; all have required fields; S1 rated NOT_SUFFICIENT;
  S2 and S3 marked RECOMMENDED; S4 explicitly deferred
Evidence: 08-target-architecture-options.md §Strategy S1 through §Strategy S4

---

Child Taskcard ID: TC-INV-007-02
Parent: TC-INV-007
Title: Write strategies S5-S7; write §Recommendation and §Comparison Matrix; reread and verify
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-007
Dependencies: TC-INV-007-01 CLOSED

Micro-steps:
  MS-INV-007-02-01: Write S5 (Generate Repeated Code — 16 control index ingestors)
    Action: write §Strategy S5; Suitability: VIABLE;
            rationale: 16 control index ingestors follow highly similar pattern; code generation
            would reduce ~5,000 LOC to ~300 LOC template + generator; medium priority;
            Migration cost: MEDIUM; not dependent on S2/S3; standalone; Verification: MEDIUM;
            Risks: generated code harder to debug; generator itself becomes critical path;
            Problems addressed: None of P-001..P-012 directly (structural maintenance concern)
    Next: MS-INV-007-02-02

  MS-INV-007-02-02: Write S6 (Retire Superseded Paths — limited scope)
    Action: write §Strategy S6; Suitability: VIABLE with limited scope;
            CONFIRMED scope: 3 blocked backends (169 LOC, HIGH confidence, after ADR documentation);
            CONDITIONAL scope: 6 autonomous variants (3,958 LOC) — only after full test file audit;
            DO NOT retire supervisor_loop.py legacy ZIP path without MISSING-003 resolution;
            Migration cost: LOW (blocked backends) to MEDIUM (variants pending audit);
            Rollback: git revert per file; Verification: grep confirms no production callers;
            Governance impact: NEUTRAL (blocked backends encode architecture rules; ADR preserves intent);
            Problems addressed: P-009 (variants, conditional); reduces noise in component register
    Next: MS-INV-007-02-03

  MS-INV-007-02-03: Write S7 (Redesign/Rewrite)
    Action: write §Strategy S7; Suitability: NOT_RECOMMENDED;
            primary argument: 89,524 LOC of tests/supervisor/ exist; a rewrite must replicate
            all behavioral contracts encoded in those tests; replication risk exceeds benefit;
            existing declaration-driven architecture (PRESERVE-001) is correct in concept;
            problems are in specific implementation details, not architecture;
            secondary argument: 5 root causes are surgical fixes, not architectural overhauls;
            Migration cost: EXTREME (replication of 89,524 LOC tests minimum);
            Rollback: impossible without test suite equivalence; Problems addressed: ALL (at cost of certainty)
    Next: MS-INV-007-02-04

  MS-INV-007-02-04: Write §Recommendation section
    Action: write recommendation:
            PRIMARY: S2 (incremental consolidation) in sequence S2-001, S2-002 (parallel-safe)
                     then S3-001 → S3-002 (after S2 stable)
            SECONDARY: S3 (state integrity) after 10+ sessions of S1-001 observability data
            LIMITED: S6 (retirement) for 3 confirmed blocked backends only;
                     conditional S6 for 6 variants pending audit
            DEFERRED: S4 (library extraction) until S2+S3 stable
            VIABLE: S5 (code generation) as standalone; no dependency on S2/S3
            NOT_RECOMMENDED: S7 (rewrite) at any point without test equivalence proof
    Next: MS-INV-007-02-05

  MS-INV-007-02-05: Write §Strategy Comparison Matrix table
    Action: write table: strategy | suitability | problems_addressed | migration_cost |
            verification_difficulty | rollback_safety | recommended_timing
            Fill all 7 rows from the prior micro-step analyses
    Next: MS-INV-007-02-06

  MS-INV-007-02-06: Reread 08-target-architecture-options.md completely; verify all 7 strategies; fix gaps
    Action: read entire file; check all 7 strategies have all required fields;
            verify §Recommendation states S2+S3 as primary; verify §Matrix has all 7 rows;
            fix any missing field
    Completion check: 7 strategies present; §Recommendation and §Matrix present; no UNRESOLVED fields

Acceptance checks: S5..S7 present; §Recommendation names S2+S3 as primary; §Matrix complete;
  S7 argued against with test-replication rationale
Evidence: 08-target-architecture-options.md

---

## TC-INV-008: Hardened Execution Plan

Parent Taskcard ID: TC-INV-008
Title: Write non-executed, dependency-aware rationalization plan (Stages 0-7)
Type: PARENT
Status: PROPOSED
Owner: investigator-agent
Supervisor: coordinator-lane
Plan requirement: REQ-INV-008
Source section: S-016
Dependencies: TC-INV-007 CLOSED
Output: 09-hardened-execution-plan.md

Note: This produces the INVESTIGATION OUTPUT PLAN (not to be confused with this
polymorphic-foraging-feather.md which is the investigation control plan).
The output 09-hardened-execution-plan.md proposes future code changes; it must
NOT be executed during this investigation.

Child taskcards: TC-INV-008-01 through TC-INV-008-05

---

Child Taskcard ID: TC-INV-008-01
Parent: TC-INV-008
Title: Write Stage 0 (Baseline Freeze) and Stage 1 (Observability) taskcards in 09-plan.md
Type: CHILD
Status: TODO
Dependencies: TC-INV-007 CLOSED

Stage 0 taskcards to write:
  TC-EXP-S0-001: Document current passing test counts
    affected: tests/ (READ ONLY — no test changes during investigation)
    evidence: 1,169 tests passing per session-resume.md; current count via test discovery
    acceptance: test count documented at HEAD with commit reference

  TC-EXP-S0-002: Capture current state file snapshot
    files: .local/supervisor/*.json state files (4 files)
    acceptance: session IDs documented; status values recorded

Stage 1 taskcards to write:
  TC-EXP-S1-001: State integrity logging (add to check_continuation.py top)
    action: add log_state_consistency() call logging session IDs and agreement verdict
    output: .local/supervisor/state-consistency-log.jsonl (append)
    rollback: remove 15-line logging block
    guarantee: G-013 (auditability) preserved; no behavior change

  TC-EXP-S1-002: Validator invocation logging (add to governance_validator_runner.py)
    action: per-declaration log in .local/supervisor/validator-invocation-log.jsonl
    rollback: remove logging lines

Micro-steps:
  MS-INV-008-01-01: Write TC-EXP-S0-001 with full taskcard format
  MS-INV-008-01-02: Write TC-EXP-S0-002 with full taskcard format
  MS-INV-008-01-03: Write TC-EXP-S1-001 with full taskcard format (stage 1 observability)
  MS-INV-008-01-04: Write TC-EXP-S1-002 with full taskcard format
  MS-INV-008-01-05: Write 09-plan.md §Overview (purpose, scope, lanes, what is NOT executed)

Acceptance checks: 4 taskcards with all required fields; §Overview explains non-execution

---

Child Taskcard ID: TC-INV-008-02
Parent: TC-INV-008
Title: Write Stage 2 (Low-Risk Cleanup) taskcards in 09-plan.md
Type: CHILD
Status: TODO

Stage 2 taskcards:
  TC-EXP-S2-001: Remove 3 architecturally blocked backends (169 LOC)
    prerequisites: TC-EXP-S0-001, TC-EXP-S1-001
    affected: tools/supervisor/backends/cognee_memory_backend.py (53),
              tools/supervisor/backends/skill_seekers_backend.py (48),
              tools/supervisor/backends/session_skill_backend.py (68)
    proof_required: grep confirms no production imports (VF-008 supports this)
    forbidden: do NOT remove local_deterministic_backend.py
    action before delete: extract error messages as ADR at docs/decisions/ADR-001..ADR-003
    rollback: git revert
    risk: LOW

  TC-EXP-S2-002: Grade Cache TTL Hardening (REDESIGN-004)
    affected: tools/supervisor/grade_declared_work.py ~line 86
    change: replace `except Exception: pass` with explicit malformed-timestamp handling
    forbidden: do NOT change cache key, 7-day TTL, or fingerprinting threshold
    test: verify malformed _cached_at treated as cache miss
    rollback: git revert (2-line change)
    risk: LOW

Micro-steps:
  MS-INV-008-02-01: Write TC-EXP-S2-001 with full taskcard format including ADR prerequisite
  MS-INV-008-02-02: Write TC-EXP-S2-002 with full taskcard format
  MS-INV-008-02-03: Write Stage 2 §Overview (scope: confirmed-unreachable or buggy-trivial only)

---

Child Taskcard ID: TC-INV-008-03
Parent: TC-INV-008
Title: Write Stage 3 (Consolidation Pilots) taskcards in 09-plan.md
Type: CHILD
Status: TODO

Stage 3 taskcards:
  TC-EXP-S3-001: Validator Dynamic Registration (REDESIGN-001)
    prerequisites: TC-EXP-S0-001, TC-EXP-S1-002
    problem: P-006
    action sequence: (A) create .supervisor/validator-registry.yaml; (B) modify runner to load
                     expected_count from registry; (C) replace bare except with structured log;
                     (D) update test assertion to exact count from registry; (E) add pre-commit hook
    dual_execution: run both old count AND registry count for 2 sprints before removing old
    forbidden: do NOT change validator function signatures; do NOT remove validators
    rollback: revert runner; delete registry file
    risk: MEDIUM (modifies governance test assertion)

  TC-EXP-S3-002: Atomic Lock Collection (REDESIGN-003)
    prerequisites: TC-EXP-S3-001 stable
    problem: P-003
    recommended implementation: single versioned plan-locks/current.json
      (replaces directory of session-keyed files)
      schema: {"sessions": [{session_id, plan_path, status, updated_at}], "version": int}
      read: one atomic read (no glob)
      write: read current.json, append/update session, atomic write back
    shadow_run: write both old format AND new format for 2 sprints
    forbidden: do NOT change lock status states (IN_PROGRESS, TERMINAL_CLOSED, etc.)
    test: add concurrent-write test for write_plan_lock.py
    rollback: revert to glob-based collection
    risk: MEDIUM

Micro-steps:
  MS-INV-008-03-01: Write TC-EXP-S3-001 with full implementation sequence (A)-(E)
  MS-INV-008-03-02: Write TC-EXP-S3-002 with implementation options and shadow-run requirement
  MS-INV-008-03-03: Write Stage 3 §Overview and dependency on Stage 2 stability

---

Child Taskcard ID: TC-INV-008-04
Parent: TC-INV-008
Title: Write Stages 4-6 taskcards in 09-plan.md
Type: CHILD
Status: TODO

Stage 4 — State Integrity Unification:
  TC-EXP-S4-001: State Integrity Pre-Check (REDESIGN-002)
    prerequisites: TC-EXP-S1-001 active for 10+ sessions
    problem: P-002
    action: add state_integrity_check() function at TOP of check_continuation.py
    two-mode deployment:
      WARN mode: log but don't block (deploy first)
      BLOCK mode: STOP(STATE_INCOHERENT) for critical disagreements (require human auth to switch)
    incoherence cases:
      CRITICAL: active-plan-lock.status==TERMINAL_CLOSED AND signal.autonomous_continue==true
      WARN: active-continuation.session_id disagrees with active-session.session_id
      SKIP: signal.session_id==null (common between sessions, expected)
    forbidden: do NOT change existing 10 checks (Check 0 through Check 10)
    rollback: remove state_integrity_check() call from top of function
    human_approval: YES for switching from WARN to BLOCK mode
    risk: MEDIUM (false positives would block autonomous continuation)

Stage 5 — Oracle Evidence Gating:
  TC-EXP-S5-001: Oracle Evidence Gate for Product Declarations (REDESIGN-005)
    prerequisites: TC-EXP-S4-001 complete
    problem: P-008
    change: for items with type==PRODUCT_SOURCE: require oracle evidence path in evidence_paths
    grade outcome without oracle: ACCEPTED_WITH_LIMITATIONS (not ACCEPTED_VERIFIED)
    add field: oracle_evidence_present: true/false to grade result
    edge case: formats with OBLIGATION_CREATED oracle status → skip oracle gating
    forbidden: do NOT require oracle for GOVERNANCE, INFRASTRUCTURE, DOCUMENTATION, ARCHITECTURE
    human_approval: YES (grading policy change)
    risk: MEDIUM

Stage 6 — Retirement:
  TC-EXP-S6-001: Audit and Retire 6 Autonomous Variants (conditional on audit findings)
    prerequisites: TC-EXP-S0-001 + deep audit of 6 test files (separate investigation task)
    proof_required_before_retirement: read each variant's full test file;
      if tests encode unique behavioral specs → extract as ADR before retiring code;
      if no unique specs → confirm via grep that no CLAUDE.md/AGENTS.md references them
    forbidden: do NOT retire if tests reveal unique governance contracts
    rollback: git revert
    human_approval: YES if uncertain about behavioral spec loss

Stage 7 — Regrowth Prevention (4 taskcards):
  TC-EXP-S7-001: Add validator registration policy to .supervisor/policies.yaml
  TC-EXP-S7-002: Add backend lifecycle ADR to docs/decisions/
  TC-EXP-S7-003: Add .supervisor/state-authority-map.yaml documenting state file ownership
  TC-EXP-S7-004: Add lifecycle_audit.py format pre-write validator (WARN mode)

Micro-steps:
  MS-INV-008-04-01: Write TC-EXP-S4-001 with two-mode deployment detail
  MS-INV-008-04-02: Write TC-EXP-S5-001 with oracle edge cases
  MS-INV-008-04-03: Write TC-EXP-S6-001 with conditional gating on audit
  MS-INV-008-04-04: Write TC-EXP-S7-001 through TC-EXP-S7-004
  MS-INV-008-04-05: Write Stages 4-7 §Overview with dependency chains

---

Child Taskcard ID: TC-INV-008-05
Parent: TC-INV-008
Title: Write 09-plan.md §Tradeoffs, §Quantitative Estimates, §Dependency DAG summary
Type: CHILD
Status: TODO
Dependencies: TC-INV-008-04 CLOSED

Required 09-plan.md §Tradeoffs:
  TRADEOFF-001: Observability first = 3-5 sprints of no-LOC-reduction work (justified)
  TRADEOFF-002: Validator registry = extra maintenance friction for engineers
  TRADEOFF-003: Oracle gating = product sprint velocity impact for formats without oracle

Required 09-plan.md §Quantitative Estimates:
  Confirmed removable: 169 LOC (3 blocked backends) HIGH confidence
  Potentially removable: 3,958 LOC (6 variants) MEDIUM confidence pending audit
  Legacy ZIP path: UNKNOWN confidence (MISSING-003: needs grep confirmation)
  Essential machinery: ~45,000 LOC (cannot be reduced)
  Overcomplicated but functioning: ~12,000 LOC (safe to address in Stage 3+)

Required 09-plan.md §Dependency DAG:
  S0 → S1 → S2 (parallel: S2-001 and S2-002 parallel-safe)
  S2 → S3-001 → S3-002
  S3-001, S3-002 → S4-001
  S4-001 → S5-001 (requires human auth)
  S0 → S6-001 (after variant audit; parallel with S2-S5)
  All → S7-001..004 (parallel-safe; no code changes)

Micro-steps:
  MS-INV-008-05-01: Write §Tradeoffs (3 tradeoffs)
  MS-INV-008-05-02: Write §Quantitative Estimates with confidence levels
  MS-INV-008-05-03: Write §Dependency DAG as Mermaid flowchart
  MS-INV-008-05-04: Reread 09-plan.md completely; verify all stages and taskcards; fix gaps

---

## TC-INV-009: Adversarial Review

Parent Taskcard ID: TC-INV-009
Title: Challenge investigation conclusions with 14 adversarial arguments
Type: PARENT
Status: PROPOSED
Owner: investigator-agent
Supervisor: coordinator-lane
Plan requirement: REQ-INV-009
Source section: S-017
Dependencies: TC-INV-008 CLOSED
Output: 10-adversarial-review.md

Objective: Steel-man 14 objections to the investigation's conclusions. For each challenge,
  present the strongest version of the objection, then refute or qualify it with investigation
  evidence. Identify any genuine plan gaps revealed by the challenges.

Required YAML format per challenge:
  challenge_id: C-NNN
  objection: <strongest version of the challenge>
  evidence_for: <what genuinely supports the challenge>
  evidence_against: <what the investigation found that refutes or complicates it>
  response: <verdict after considering both sides>
  plan_amendment: <specific plan gap identified, or "none required">

Key pre-established verdicts (cite these; do not contradict without new source evidence):
  C-001: NOT CORRECT AS STATED — size is symptom; 5 specific failure modes are the problem
  C-002: NOT SUFFICIENT — blocked backends encode rules; 6 variants have tests; characterize first
  C-003: PARTIALLY CORRECT — defence in depth legitimate; problem is prompt-layer degradation
  C-005: CHALLENGE IS REAL — consolidation migration introduces risk; plan acknowledges this (R-001..R-005)
  C-008: NOT RECOMMENDED — 89,524 LOC of tests must be replicated; incremental is proven
  C-011: HONEST CONCESSION — 3-5 sprints of machinery work before product velocity improves

Parent acceptance criteria:
  - All 14 challenges documented with all required YAML fields
  - Verdicts for C-001/C-002/C-003/C-005/C-008/C-011 match pre-established positions
  - §Review Summary present: top 3 challenges that revealed genuine plan gaps
  - plan_amendment is "none required" or specific plan gap with taskcard reference
  - No challenge left at UNRESOLVED status

Rollback: delete 10-adversarial-review.md

---

Child Taskcard ID: TC-INV-009-01
Parent: TC-INV-009
Title: Write C-001 through C-007 in 10-adversarial-review.md
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-009

Micro-steps:
  MS-INV-009-01-01: Write file header and §Introduction
    Action: create 10-adversarial-review.md; write header; write §Introduction explaining
            purpose: to find plan gaps and weak arguments before external review
    Completion check: file created with header and §Introduction
    Next: MS-INV-009-01-02

  MS-INV-009-01-02: Write C-001 ("Large machinery is inherently bad")
    Action: objection: 89,165 LOC of supervisor machinery cannot be justified for a product
            with 76,170 LOC of product code; evidence_for: size ratio ~1.17:1;
            evidence_against: machinery includes governance (G-004), oracle infrastructure (G-008),
            evidence verification (G-009), state management (G-007) — all required for production-grade
            autonomous operation; size alone cannot justify reduction; the 5 concrete failure modes
            (RC-001..RC-005) are the real problems, not total LOC;
            response: NOT CORRECT AS STATED; verdict: size is symptom; problems are specific;
            plan_amendment: none required
    Next: MS-INV-009-01-03

  MS-INV-009-01-03: Write C-002 ("Low-reference code is dead")
    Action: objection: 3 backends with can_execute()=False and 6 autonomous variants with
            zero production callers should be deleted;
            evidence_for: no production call path; ~4,127 LOC total;
            evidence_against: 3 blocked backends encode architectural rules via error messages
            (VF-008 / DOCUMENTED_NEGATIVE_SPACE); 6 variants have substantial test files
            that may encode unique behavioral contracts (VF-007); deletion without ADR or test audit
            risks losing documented rules; response: NOT SUFFICIENT — must characterize before
            any retirement; blocked backends → ADR first; variants → full test file read required;
            plan_amendment: TC-EXP-S6-001 already conditions retirement on audit (confirmed)
    Next: MS-INV-009-01-04

  MS-INV-009-01-04: Write C-003 ("Duplicated validation is unnecessary")
    Action: objection: having 167 validators AND anti_skip_checker AND oracle is over-engineered;
            evidence_for: three layers of validation for same declaration;
            evidence_against: three layers serve different purposes: validators check structural
            rules, anti-skip detects heuristic evasion, oracle provides machine-verifiable
            correctness; PROBLEM is not the layers but the degradation of the prompt-only layer
            (RC-002 / G-003); response: PARTIALLY CORRECT — the layers are appropriate;
            the prompt-only enforcement of the outer layer is the weakness, not the layer itself;
            plan_amendment: none required; REDESIGN-002 (S3) addresses enforcement gap
    Next: MS-INV-009-01-05

  MS-INV-009-01-05: Write C-004 ("Shared abstractions are always better")
    Action: objection: continuation_selector.py, continuation_router.py, and continuation_state.py
            should be merged into one module; evidence_for: separate files with related functions;
            evidence_against: separation enables independent testing and clear ownership;
            continuation_selector and continuation_router have MEDIUM confidence classification
            (callers unverified); merging before caller verification risks incorrect scope decisions;
            response: NEEDS INVESTIGATION — verify callers first (MS-INV-003-01-05/06) before
            concluding these are candidates for consolidation;
            plan_amendment: TC-INV-003-01 already includes caller verification (confirmed)
    Next: MS-INV-009-01-06

  MS-INV-009-01-06: Write C-005 ("Consolidation lowers risk")
    Action: objection: proposed REDESIGN-001..REDESIGN-005 will reduce risk once implemented;
            evidence_for: each redesign addresses a real root cause;
            evidence_against: the migration itself introduces new risks R-001..R-005; REDESIGN-002
            in BLOCK mode without observability data has false-positive risk R-003 (score 12, highest);
            REDESIGN-003 on Windows NTFS introduces R-004 (advisory lock not enforced by OS);
            response: CHALLENGE IS REAL — plan acknowledges this in R-001..R-005; mitigation is
            observability-first sequence (TC-EXP-S1-001 before TC-EXP-S4-001);
            plan_amendment: R-003 must explicitly precede S4 in dependency DAG (already in 09-plan DAG)
    Next: MS-INV-009-01-07

  MS-INV-009-01-07: Write C-006 ("One state machine is always preferable")
    Action: objection: having 4 separate state files that must agree is the root cause; merge them;
            evidence_for: RC-001 (no state integrity layer) is directly caused by multi-file state;
            evidence_against: REDESIGN-002 adds a consistency check without merging files;
            merging would require rewriting check_continuation.py (796 LOC), write_plan_lock.py,
            autonomous_cycle.py, and sprint_executor.py simultaneously — massive blast radius;
            REDESIGN-003 (single plan-locks/current.json) already merges the lock directory without
            requiring full state unification; response: PARTIALLY CORRECT — the plan should not merge
            all state files (too high blast radius); it should add consistency checking and atomically
            collect locks (REDESIGN-002 + REDESIGN-003); that achieves the same safety property
            with surgical scope; plan_amendment: none required
    Next: TC-INV-009-02

Acceptance checks: C-001..C-007 all present with all required YAML fields;
  C-001 rated NOT CORRECT AS STATED; C-005 rated CHALLENGE IS REAL;
  plan_amendment fields either "none required" or specific confirmed reference
Evidence: 10-adversarial-review.md §C-001 through §C-007

---

Child Taskcard ID: TC-INV-009-02
Parent: TC-INV-009
Title: Write C-008 through C-014; write §Review Summary; reread and verify
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-009
Dependencies: TC-INV-009-01 CLOSED

Micro-steps:
  MS-INV-009-02-01: Write C-007 ("Generated code should not be committed")
    Action: objection: 16 control index ingestors follow the same pattern and should be generated;
            evidence_for: S5 (generate repeated code) is listed as VIABLE strategy;
            evidence_against: committed generated code is harder to debug; generator becomes
            critical path; ingestors currently serve as documentation of each entity type;
            response: VIABLE but not urgent — S5 is a standalone strategy, no dependency on
            S2/S3, but adds maintenance complexity for the generator; defer until S2/S3 stable;
            plan_amendment: none required (S5 already rated VIABLE with appropriate caveats)
    Next: MS-INV-009-02-02

  MS-INV-009-02-02: Write C-008 ("A rewrite is cleaner")
    Action: objection: starting from scratch with proper state management would be faster than
            surgical fixes to 796-line check_continuation.py;
            evidence_for: S7 (redesign/rewrite) would resolve all 5 root causes simultaneously;
            evidence_against: 89,524 LOC of tests/supervisor/ encode behavioral contracts that must be
            replicated; replication risk exceeds benefit; the investigation found that autonomous_cycle.py
            declaration-driven architecture IS correct (PRESERVE-001) — only specific implementation
            details need fixing; response: NOT RECOMMENDED — RC-001..RC-005 are surgical fixes,
            not architectural overhauls; 89,524 LOC test replication is not feasible without
            test equivalence proof; plan_amendment: none required
    Next: MS-INV-009-02-03

  MS-INV-009-02-03: Write C-009 ("Tests capture actual behavior")
    Action: objection: 89,524 LOC of tests/supervisor/ prove the system works correctly;
            if tests pass, the problems don't exist;
            evidence_for: 1,169 tests passing at HEAD per session-resume.md;
            evidence_against: VF-002 shows 3-of-4 state files disagree RIGHT NOW at HEAD —
            this is a live observation, not a hypothetical; tests validate code paths but not
            cross-file state consistency at runtime; race conditions (VF-004) require concurrent
            execution to trigger and are unlikely to appear in sequential test runs;
            response: INSUFFICIENT — tests prove code correctness; they do not prevent state
            incoherence that arises from inter-file timing; VF-002 is observed state, not tested;
            plan_amendment: TC-EXP-S0-002 (state file snapshot) documents observed state
    Next: MS-INV-009-02-04

  MS-INV-009-02-04: Write C-010 ("The target preserves autonomy")
    Action: objection: REDESIGN-002 BLOCK mode will halt the autonomous loop more than the current
            system does;
            evidence_for: state_integrity_check() in BLOCK mode returns STOP on incoherence;
            evidence_against: WARN mode is the required first deployment (TC-EXP-S4-001);
            BLOCK mode requires human authorization (G-016); false-positive rate is measured
            before switching; the SKIP case (session_id==null) is explicitly handled to avoid
            blocking normal between-session state;
            response: VALID CONCERN — addressed by WARN-first sequence; BLOCK mode gated
            behind human authorization; plan_amendment: already explicit in TC-EXP-S4-001;
            flag in §Review Summary as requiring careful observability measurement
    Next: MS-INV-009-02-05

  MS-INV-009-02-05: Write C-011 ("The plan will not slow product progress")
    Action: objection: machinery hardening should have zero product velocity impact;
            evidence_for: Stages 0-2 are documentation + 2-line fixes;
            evidence_against: Stage 3 (validator registry, atomic lock collection) requires
            1-2 machinery sprints; Stage 4 (state integrity) requires 10+ sessions of observability
            data before deployment; Stage 5 (oracle gating) requires Babar Raza authorization;
            total estimate: 3-5 sprints of machinery focus before full product velocity resumes;
            response: HONEST CONCESSION — Stages 0-2 are genuinely low-impact; Stages 3-5 require
            dedicated machinery sprints; product deepening continues in parallel during Stages 0-2
            but must pause for Stage 3 governance test assertion changes;
            plan_amendment: §Tradeoffs in 09-plan.md must state this explicitly (TRADEOFF-001)
    Next: MS-INV-009-02-06

  MS-INV-009-02-06: Write C-012 ("Execution requires no undocumented knowledge")
    Action: objection: the 09-hardened-execution-plan.md is sufficient for a new engineer to execute;
            evidence_for: plan has rollback, acceptance criteria, and dependency DAG;
            evidence_against: MISSING-001..MISSING-005 are unresolved items that affect execution
            safety; MISSING-003 (legacy ZIP path) must be resolved before TC-EXP-S6-001;
            MISSING-002 (variant test audit) must be completed before retirement;
            response: NOT FULLY TRUE — execution is safe for Stages 0-2 without resolving
            missing items; Stages 3-6 have explicit prerequisites in the plan; missing items
            are documented, not hidden; plan_amendment: none required (MISSING-001..005 already
            documented in TC-INV-010 Q7)
    Next: MS-INV-009-02-07

  MS-INV-009-02-07: Write C-013 ("Oracle layer is machinery")
    Action: objection: execute_oracle.py (1,428 LOC) should be counted as supervisor machinery,
            not as tests; this increases the machinery:product ratio;
            evidence_for: execute_oracle.py lives in oracle/ directory; it's automation, not test assertions;
            evidence_against: DECISION-A in TC-INV-001-02 classifies oracle/ as tests (cat 8)
            with documented rationale: execute_oracle.py is a test executor; oracle-package.yaml
            are test specifications; oracle output is a test signal; oracle is not shipped as product;
            response: REASONABLE ALTERNATIVE CLASSIFICATION but investigation decision stands;
            even if oracle were reclassified as machinery, it would not change any P-NNN finding;
            plan_amendment: document DECISION-A explicitly in 01-loc-report.md §Ambiguous Cases
            (already planned in TC-INV-001-02)
    Next: MS-INV-009-02-08

  MS-INV-009-02-08: Write C-014 ("governance_validators.py should be split")
    Action: objection: 3,234 LOC in one file (governance_validators.py) is a monolith that should
            be split into domain-specific modules;
            evidence_for: P-010 rates this MEDIUM severity; already split: ext1-ext4 files exist;
            evidence_against: splitting governance_validators.py changes import chains; runner imports
            this file by name; test file imports by name; REDESIGN-001 already plans dynamic registration
            which reduces the need for the file to be comprehensive; splitting without registry first
            risks validator loss during transition; response: VALID LONG-TERM GOAL but premature now;
            REDESIGN-001 (dynamic registry) must complete first to make validator locations configurable;
            then splitting is low-risk; plan_amendment: add sequencing note that P-010 resolution
            depends on REDESIGN-001 completion (already implicit in strategy S2 → S4 ordering)
    Next: MS-INV-009-02-09

  MS-INV-009-02-09: Write §Review Summary
    Action: write §Review Summary identifying top 3 challenges that revealed genuine plan gaps:
            1. C-005 (consolidation risk) → confirmed need for WARN-first sequence (already in plan)
            2. C-010 (autonomy preservation) → confirmed need for BLOCK mode human authorization gate
            3. C-011 (velocity impact) → confirmed need for §Tradeoffs in 09-plan.md
            Also list: challenges that found no plan gaps (C-001, C-002, C-003, C-007, C-008,
            C-009, C-012, C-013, C-014); challenges that confirmed existing plan coverage
    Next: MS-INV-009-02-10

  MS-INV-009-02-10: Reread 10-adversarial-review.md completely; verify all 14 challenges; fix gaps
    Action: read entire file; verify C-001..C-014 all present; all have required YAML fields;
            §Review Summary identifies top 3 challenges; no UNRESOLVED response fields;
            all plan_amendment fields are concrete or "none required"
    Completion check: 14 challenges present; §Review Summary complete; no UNRESOLVED fields

Acceptance checks: all 14 challenges present; §Review Summary; verdicts match pre-established positions;
  no plan_amendment is vague (all are "none required" or cite specific taskcard/section)
Evidence: 10-adversarial-review.md

---

## TC-INV-010: Executive Decision Brief

Parent Taskcard ID: TC-INV-010
Title: Answer 9 executive questions; issue final verdict
Type: PARENT
Status: PROPOSED
Owner: investigator-agent
Supervisor: coordinator-lane
Plan requirement: REQ-INV-010
Source section: S-018
Dependencies: TC-INV-009 CLOSED
Output: 11-executive-decision-brief.md

Objective: Synthesize the entire investigation into 9 executive answers and a final verdict.
  All answers must cite investigation artifacts (metrics.json, component-register.csv,
  problem-catalog.md, guarantee-control-matrix.md, risk-register.md). No new analysis in this phase —
  only synthesis and citation.

Pre-established answers (cite these; do not contradict without evidence from prior phases):
  Q1: PARTIALLY_ACCURATE (direction correct; magnitudes ~10% off; framing missed tests=machinery)
  Q2: Justified breakdown by classification category with LOC estimates
  Q3: Confirmed 169 LOC removable; 3,958 LOC conditional; 0 genuinely duplicative
  Q4: Five ranked problems: P-002, P-005, P-003, P-006, P-008
  Q5: PRESERVE-001..007 + oracle + CCI-MVP + atomic_io + 12 grade types
  Q6: TC-EXP-S2-002 (cache TTL) first; TC-EXP-S2-001 (blocked backends) second
  Q7: MISSING-001..MISSING-005
  Q8: PARTIAL YES (immediate: S1+S2; NOT YET: S3-S6 pending observability data)
  Q9: Stage 5 requires Babar Raza authorization; Stage 4 BLOCK mode requires calibration first

Parent acceptance criteria:
  - All 9 questions answered with evidence citations to investigation artifacts
  - §Final Verdict section present with INVESTIGATION_COMPLETE_PLAN_READY_FOR_EXTERNAL_REVIEW
  - §Missing Evidence section lists MISSING-001..MISSING-005
  - §External Review Required section lists Stage 5 and Stage 4 BLOCK mode requirements
  - Final verdict dated with HEAD commit and branch

Rollback: delete 11-executive-decision-brief.md

---

Child Taskcard ID: TC-INV-010-01
Parent: TC-INV-010
Title: Write Q1 through Q5 answers with evidence citations in 11-executive-decision-brief.md
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-010

Micro-steps:
  MS-INV-010-01-01: Write file header and §Introduction
    Action: create 11-executive-decision-brief.md; write header (authoritative_plan, REQ-INV-010,
            TC-INV-010); write §Introduction: this brief synthesizes the complete investigation;
            all findings cite prior investigation artifacts
    Completion check: file created with header
    Next: MS-INV-010-01-02

  MS-INV-010-01-02: Write Q1 answer (Was the 81K vs 72K assessment correct?)
    Action: write §Q1 with verdict PARTIALLY_ACCURATE; cite evidence/metrics.json for exact figures;
            cite 01-loc-and-classification-report.md §Prior Assessment Verdict;
            key finding: prior assessment correct in direction but missed tests/supervisor/ (89,524 LOC)
            equaling machinery and plans/ (95,951 LOC) exceeding product
    Next: MS-INV-010-01-03

  MS-INV-010-01-03: Write Q2 answer (How much machinery is justified?)
    Action: write §Q2 with classification breakdown table:
            ESSENTIAL_SAFETY_CRITICAL: ~45K LOC — justified (orchestration + continuation + governance)
            ESSENTIAL_OVERCOMPLICATED: ~12K LOC — justified but complexity reduction target
            USEFUL_SHARED_INFRASTRUCTURE: ~28K LOC — justified (backends, control index, atomic_io)
            SUSPECTED_GHOST: ~4K LOC — requires audit before verdict
            DOCUMENTED_NEGATIVE_SPACE: <200 LOC — justified (architectural rule documentation)
            COMPATIBILITY_ONLY: ~3K LOC — justified while MCP and superpowers paths active
            cite 04-machinery-component-register.md §Summary table
    Next: MS-INV-010-01-04

  MS-INV-010-01-04: Write Q3 answer (How much is removable?)
    Action: write §Q3 with confidence-tiered table:
            HIGH confidence: 169 LOC (3 blocked backends) — after ADR documentation
            MEDIUM confidence: 3,958 LOC (6 autonomous variants) — after full test file audit
            UNRESOLVED: legacy ZIP path in supervisor_loop.py (MISSING-003)
            LOW genuinely duplicative: validator split ext1-ext4 is functional separation
            cite 04-machinery-component-register.md §DOCUMENTED_NEGATIVE_SPACE and §SUSPECTED_GHOST
    Next: MS-INV-010-01-05

  MS-INV-010-01-05: Write Q4 answer (Five most serious structural problems)
    Action: write §Q4 ranked list with rationale for each ranking:
            1. P-002 (state authority fragmentation): OBSERVABLE RIGHT NOW (VF-002)
            2. P-005 (prompt-only enforcement): enables bypass of plan lock and terminal stop
            3. P-003 (non-atomic lock collection): race condition → false CONTINUE on concurrent write
            4. P-006 (validator count fragile): governance can silently degrade to 154 validators
            5. P-008 (self-certified evidence): ACCEPTED_VERIFIED without oracle is heuristic-only
            cite 05-problem-catalog.md; note G-006 is ABSENT (no other guarantee is fully absent)
    Next: MS-INV-010-01-06

  MS-INV-010-01-06: Write Q5 answer (What must not be changed?)
    Action: write §Q5 preserve list:
            - PRESERVE-001..007 (cite Part II §What Must Be Preserved)
            - oracle execution infrastructure (73/73 PASS — only machine-verifiable signal)
            - CCI-MVP session isolation logic in check_continuation.py Check 0/0b
            - atomic_io.py per-file atomicity (G-007 is ENFORCED)
            - 12 grade types in grade_declared_work.py (PRESERVE-007)
            - lock status vocabulary (IN_PROGRESS/TERMINAL_CLOSED/COMPLETE/SUPERSEDED/ITERATION_REQUIRED)
    Next: TC-INV-010-02

Acceptance checks: Q1..Q5 all present; each cites at least one investigation artifact;
  Q4 ranked list matches pre-established ordering; Q5 preserve list matches Part II analysis
Evidence: 11-executive-decision-brief.md §Q1 through §Q5

---

Child Taskcard ID: TC-INV-010-02
Parent: TC-INV-010
Title: Write Q6 through Q9; §Final Verdict; §Missing Evidence; §External Review Required
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-010
Dependencies: TC-INV-010-01 CLOSED

Micro-steps:
  MS-INV-010-02-01: Write Q6 answer (Safest first pilot?)
    Action: write §Q6:
            FIRST: TC-EXP-S2-002 (grade cache TTL hardening) — 2-line change; independently testable;
            zero behavioral impact for valid cache entries; HIGH confidence; cite VF-006 and P-007
            SECOND: TC-EXP-S2-001 (remove 3 blocked backends) — 169 LOC; requires grep confirmation
            of no production imports first; cite VF-008 and P-009
            NOT FIRST: TC-EXP-S3-001 (validator registry) — modifies governance test assertion; requires
            S1-002 observability first
    Next: MS-INV-010-02-02

  MS-INV-010-02-02: Write Q7 answer (What evidence is missing?)
    Action: write §Q7 with §Missing Evidence subsection listing all 5 gaps:
            MISSING-001: Has VF-004 race condition ever been triggered? — search git log for TERMINAL_CLOSED fix
            MISSING-002: Do 6 autonomous variant tests encode unique behavioral specs? — requires full read
            MISSING-003: Is legacy ZIP path in supervisor_loop.py called by any external script? — grep needed
            MISSING-004: How often does active-continuation.json lag? — needs TC-EXP-S1-001 running first
            MISSING-005: Does PLAN_COMPLETED_IN_SESSION safety net distinguish stale-but-closed correctly?
            Note how each missing item maps to a deferred execution decision
    Next: MS-INV-010-02-03

  MS-INV-010-02-03: Write Q8 answer (Is rationalization advisable now?)
    Action: write §Q8 as two-column table: SAFE_NOW vs NOT_YET_SAFE;
            SAFE_NOW: TC-EXP-S2-002 (cache TTL), TC-EXP-S2-001 (blocked backends after grep),
                      TC-EXP-S1-001 (logging, non-blocking), TC-EXP-S1-002 (validator logging)
            NOT_YET_SAFE: TC-EXP-S3-002 (need MISSING-001), TC-EXP-S4-001 (need 10+ sessions S1-001),
                          TC-EXP-S5-001 (need Babar Raza authorization), TC-EXP-S6-001 (need test audit)
            cite 07-risk-register.md for R-003 (highest risk: S4 false positive)
    Next: MS-INV-010-02-04

  MS-INV-010-02-04: Write Q9 answer (What requires external review?)
    Action: write §Q9 §External Review Required:
            Stage 5 TC-EXP-S5-001: oracle gating changes grading policy; ACCEPTED_VERIFIED
            no longer reachable without oracle evidence; requires Babar Raza authorization
            (same gate as Gate 11 grading policy decisions)
            Stage 4 TC-EXP-S4-001 BLOCK mode: must be calibrated against state-consistency-log data;
            false-positive rate must be measured in WARN mode first; human authorization required
            for mode switch (G-016); premature BLOCK mode = worst-case outcome of R-003
    Next: MS-INV-010-02-05

  MS-INV-010-02-05: Write §Final Verdict
    Action: write §Final Verdict section:
            verdict: INVESTIGATION_COMPLETE_PLAN_READY_FOR_EXTERNAL_REVIEW
            branch: main
            head_commit: af879e550ee47f89dd7e805314f9b14923fbf100 (verify against actual HEAD at time of writing)
            production_files_changed: 0 (confirm via git diff --stat)
            investigation_files_created: 16
            top_5_problems: P-002, P-005, P-003, P-006, P-008
            safest_first_pilot: TC-EXP-S2-002
            unresolved_risks: MISSING-001..005 (documented; not blocking investigation)
            external_review_required: TC-EXP-S5-001 (Babar Raza); TC-EXP-S4-001 BLOCK mode
            authorized_plan_for_execution: 09-hardened-execution-plan.md (after external review)
    Next: MS-INV-010-02-06

  MS-INV-010-02-06: Reread 11-executive-decision-brief.md completely; verify all 9 Q sections; fix gaps
    Action: read entire file; check Q1..Q9 present; §Final Verdict present with all required fields;
            §Missing Evidence lists MISSING-001..005; §External Review Required covers Stage 5 and S4 BLOCK;
            all Q answers cite investigation artifact (by filename);
            fix any missing citation or gap
    Completion check: 9 Q sections; §Final Verdict with INVESTIGATION_COMPLETE verdict; no UNRESOLVED fields

Acceptance checks: all 9 Q answers; §Final Verdict with verdict string and commit;
  §Missing Evidence; §External Review Required; every Q cites at least one investigation artifact
Evidence: 11-executive-decision-brief.md

---

## TC-INV-011: Second Pass and Quality Gates

Parent Taskcard ID: TC-INV-011
Title: Verify idempotency; confirm all quality gates; run final diff check
Type: PARENT
Status: PROPOSED
Owner: investigator-agent
Supervisor: coordinator-lane
Plan requirement: REQ-INV-011
Source section: S-019
Dependencies: TC-INV-010 CLOSED

Purpose: Ensure no material changes occur on a second read of each file.
  Confirm all 12 quality gate counters are at target values.
  Produce final git diff confirmation that zero production files changed.

Parent acceptance criteria:
  - All 16 output files exist at correct paths
  - git diff --stat shows ONLY additions in docs/investigations/supervisor-machinery-audit/
  - All 12 quality gate counters at target (specified in TC-INV-011-02)
  - Second-pass produced no material changes (MATERIAL_SECOND_PASS_CHANGES = 0)

Rollback: delete any incorrectly created files; investigation directory is always removable

---

Child Taskcard ID: TC-INV-011-01
Parent: TC-INV-011
Title: Reread all 16 investigation files; record any gaps found; fix gaps immediately
Type: CHILD
Status: TODO
Plan requirement: REQ-INV-011

Scope:
  Allowed: reread + append to evidence/commands-and-results.md; edit investigation files to fix gaps
  Forbidden: modify any source file outside docs/investigations/

Micro-steps:
  MS-INV-011-01-01: Reread 00-investigation-scope-and-baseline.md; record REREAD_COMPLETE or gap
  MS-INV-011-01-02: Reread 01-loc-and-classification-report.md; verify 8 sections present
  MS-INV-011-01-03: Reread 02-current-machinery-architecture.md; verify 3 Mermaid blocks present
  MS-INV-011-01-04: Reread 03-workflow-traces.md; verify all 9 WF-NNN traces present
  MS-INV-011-01-05: Reread 04-machinery-component-register.md; verify all 4 classification groups
  MS-INV-011-01-06: Reread 05-problem-catalog.md; verify P-001..P-012 all present
  MS-INV-011-01-07: Reread 06-guarantee-control-matrix.md; verify G-001..G-020 all present
  MS-INV-011-01-08: Reread 07-risk-register.md; verify R-001..R-005 all present
  MS-INV-011-01-09: Reread 08-target-architecture-options.md; verify 7 strategies + §Recommendation
  MS-INV-011-01-10: Reread 09-hardened-execution-plan.md; verify >= 12 TC-EXP-* taskcards;
                    verify each has P-NNN reference and rollback field
  MS-INV-011-01-11: Reread 10-adversarial-review.md; verify C-001..C-014 all present
  MS-INV-011-01-12: Reread 11-executive-decision-brief.md; verify Q1..Q9 + §Final Verdict
  MS-INV-011-01-13: Reread evidence/commands-and-results.md; verify baseline section + LOC section
                    + architecture section + second-pass section
  MS-INV-011-01-14: Reread evidence/metrics.json; verify valid JSON; parse with python -m json.tool
  MS-INV-011-01-15: Reread evidence/file-classification.csv; verify header row + entries
  MS-INV-011-01-16: Reread evidence/component-register.csv; verify header row + entries

  For each micro-step: if gap found → fix immediately before moving to next file.
  Record each file as REREAD_COMPLETE or REREAD_GAP_FIXED in evidence/commands-and-results.md.

Acceptance checks: 16 files reread; all gaps fixed; commands-and-results.md updated with reread log
Evidence: evidence/commands-and-results.md §Second Pass Log

---

Child Taskcard ID: TC-INV-011-02
Parent: TC-INV-011
Title: Run quality gate checks and produce final diff verification
  Micro-steps:
    MS-INV-011-02-01: Verify UNCLASSIFIED_RELEVANT_FILES = 0
      (check that file-classification.csv covers all tools/supervisor/ and src/ files)
    MS-INV-011-02-02: Verify MATERIAL_COMPONENTS_WITHOUT_CLASSIFICATION = 0
      (check component-register.csv row count vs identified components)
    MS-INV-011-02-03: Verify MATERIAL_FINDINGS_WITHOUT_EVIDENCE = 0
      (check each P-NNN in 05-problem-catalog.md has at least one file:line citation)
    MS-INV-011-02-04: Verify GUARANTEES_WITHOUT_CONTROL_MAPPING = 0
      (check G-001 through G-020 all have enforcing_components)
    MS-INV-011-02-05: Verify TASKS_WITHOUT_PROBLEM_IDS = 0
      (check all TC-EXP-* in 09-plan.md reference at least one P-NNN)
    MS-INV-011-02-06: Verify TASKS_WITHOUT_ROLLBACK = 0
      (check all TC-EXP-* have rollback field)
    MS-INV-011-02-07: Verify TASKS_WITHOUT_ACCEPTANCE_CRITERIA = 0
      (check all TC-EXP-* have acceptance_criteria)
    MS-INV-011-02-08: Run git diff --stat; verify output shows ONLY new files in
                      docs/investigations/supervisor-machinery-audit/
    MS-INV-011-02-09: Verify PRODUCTION_FILES_CHANGED = 0
      (confirm git diff touches no file in src/, tests/, tools/, registry/, .supervisor/)
    MS-INV-011-02-10: Append second-pass summary to evidence/commands-and-results.md
    MS-INV-011-02-11: Write INVESTIGATION_COMPLETE_PLAN_READY_FOR_EXTERNAL_REVIEW verdict
                      in 11-executive-decision-brief.md §Final Status

Parent integration checks (TC-INV-011):
  All 16 output files exist
  git diff --stat shows 0 production files changed
  All 12 quality gate counters at target
  Second-pass produced no material changes (MATERIAL_SECOND_PASS_CHANGES = 0)

Rollback: delete any incorrectly created files; the investigation directory can always be removed

---
# PART V — DEPENDENCY DAG
---

## Execution DAG

Mandatory sequence:
  TC-INV-000 (baseline) →
  TC-INV-001 (LOC) →
  TC-INV-002 (architecture) →
  TC-INV-003 (components) →
  TC-INV-004 (problems) →
  TC-INV-005 (guarantees) →
  TC-INV-006 (risks) →
  TC-INV-007 (options) →
  TC-INV-008 (hardened plan) →
  TC-INV-009 (adversarial) →
  TC-INV-010 (brief) →
  TC-INV-011 (second pass)

Within each parent, child ordering:
  TC-INV-000: 000-01 → 000-02 → 000-03
  TC-INV-001: 001-01 → 001-02 → 001-03 → 001-04
  TC-INV-002: 002-01 → 002-02 (parallel-safe with 002-03) → 002-03
  TC-INV-003: 003-01 → 003-02 → 003-03
  TC-INV-004: 004-01 → 004-02
  TC-INV-005: 005-01 → 005-02
  TC-INV-006: 006-01 → 006-02
  TC-INV-007: 007-01 → 007-02
  TC-INV-008: 008-01 → 008-02 → 008-03 → 008-04 → 008-05
  TC-INV-009: 009-01 → 009-02
  TC-INV-010: 010-01 → 010-02
  TC-INV-011: 011-01 → 011-02

Parallel-safe pairs:
  TC-INV-002-02 and TC-INV-002-03 (separate output files; no shared state)
  TC-INV-008-04 Stage 6 taskcards (variant audit) parallel with Stages 4-5
  TC-INV-008-04 Stage 7 taskcards (policy docs) parallel with any Stage

File ownership (one file → one owner at a time):
  00-investigation-scope-and-baseline.md  → TC-INV-000-03
  01-loc-and-classification-report.md     → TC-INV-001-04
  02-current-machinery-architecture.md    → TC-INV-002-02
  03-workflow-traces.md                   → TC-INV-002-03
  04-machinery-component-register.md      → TC-INV-003-03
  05-problem-catalog.md                   → TC-INV-004-01, TC-INV-004-02 (sequential)
  06-guarantee-control-matrix.md          → TC-INV-005-01, TC-INV-005-02 (sequential)
  07-risk-register.md                     → TC-INV-006-01, TC-INV-006-02 (sequential)
  08-target-architecture-options.md       → TC-INV-007-01, TC-INV-007-02 (sequential)
  09-hardened-execution-plan.md           → TC-INV-008-01 through 008-05 (sequential)
  10-adversarial-review.md               → TC-INV-009-01, TC-INV-009-02 (sequential)
  11-executive-decision-brief.md         → TC-INV-010-01, TC-INV-010-02 (sequential)
  evidence/commands-and-results.md       → ALL (append-only; multiple owners; order safe)
  evidence/metrics.json                  → TC-INV-001-03 (one writer)
  evidence/file-classification.csv       → TC-INV-001-04 (one writer)
  evidence/component-register.csv        → TC-INV-003-01, TC-INV-003-02 (sequential)

---
# PART VI — VALIDATION MATRIX
---

## Validation Commands per Output File

00-investigation-scope-and-baseline.md:
  - grep -c "^##" 00-investigation-scope-and-baseline.md | grep -c "7" (7 sections)
  - head -5 confirms repository identity section present
  MANDATORY: all 7 subsections present

01-loc-and-classification-report.md:
  - grep -c "^##" 01-loc-and-classification-report.md (expect >= 8 sections)
  - cat evidence/metrics.json | python -m json.tool (valid JSON)
  MANDATORY: metrics.json valid JSON; PARTIALLY_ACCURATE verdict present

02-current-machinery-architecture.md:
  - grep -c "mermaid" 02-current-machinery-architecture.md (expect 3)
  MANDATORY: 3 mermaid blocks present

03-workflow-traces.md:
  - grep -c "trace_id: WF-" 03-workflow-traces.md (expect 9)
  MANDATORY: all 9 WF-NNN traces present

04-machinery-component-register.md:
  - grep -c "ESSENTIAL_SAFETY_CRITICAL\|ESSENTIAL_OVERCOMPLICATED\|SUSPECTED_GHOST\|DOCUMENTED_NEGATIVE_SPACE" (expect >= 8 lines)
  MANDATORY: all 4 main classification groups present

05-problem-catalog.md:
  - grep -c "^P-0" 05-problem-catalog.md (expect 12)
  MANDATORY: P-001 through P-012 present

06-guarantee-control-matrix.md:
  - grep -c "^G-0" 06-guarantee-control-matrix.md (expect 20)
  MANDATORY: G-001 through G-020 present

07-risk-register.md:
  - grep -c "^R-00" 07-risk-register.md (expect 5)
  MANDATORY: R-001 through R-005 present

08-target-architecture-options.md:
  - grep -c "^## Strategy" 08-target-architecture-options.md (expect 7)
  MANDATORY: all 7 strategies present + recommendation section

09-hardened-execution-plan.md:
  - grep -c "^TC-EXP-" 09-hardened-execution-plan.md (expect >= 12 taskcards)
  - grep "problem_id\|problem_ref\|P-00" (every taskcard references a P-NNN)
  - grep "rollback" (every taskcard has rollback)
  MANDATORY: >= 12 TC-EXP-* taskcards; all reference P-NNN; all have rollback

10-adversarial-review.md:
  - grep -c "^## C-0" 10-adversarial-review.md (expect 14)
  MANDATORY: C-001 through C-014 present

11-executive-decision-brief.md:
  - grep -c "^## Q" (expect 9 Q sections)
  - grep "INVESTIGATION_COMPLETE" (final verdict present)
  MANDATORY: 9 Q answers + final verdict

Final diff check (TC-INV-011):
  git diff --stat
  Expected: only additions in docs/investigations/supervisor-machinery-audit/
  Forbidden: any modified line in src/, tests/, tools/, registry/, .supervisor/, .local/

---
# PART VII — EXECUTION HANDOFF
---

## Evidence Contract

Every output file must reference:
  - authoritative_plan: C:\Users\prora\.claude\plans\polymorphic-foraging-feather.md
  - relevant REQ-INV-NNN (in file header or first paragraph)
  - relevant TC-INV-NNN (in file footer or change log)

Evidence root (investigation directory):
  docs/investigations/supervisor-machinery-audit/
    run-record.yaml           (create at TC-INV-000; update status at each phase close)
    evidence/commands-and-results.md  (append throughout ALL phases)
    evidence/metrics.json
    evidence/file-classification.csv
    evidence/component-register.csv
    00-investigation-scope-and-baseline.md
    01-loc-and-classification-report.md
    ... (all 12 investigation files)

run-record.yaml structure:
  authoritative_plan: C:\Users\prora\.claude\plans\polymorphic-foraging-feather.md
  artifact_role: investigation_run_record
  execution_authority: false
  started_at: <ISO>
  head_commit: af879e550ee47f89dd7e805314f9b14923fbf100
  phases:
    TC-INV-000: PENDING
    TC-INV-001: PENDING
    ... (all 12)
  overall_status: IN_PROGRESS

## Execution Handoff Instructions (for the executing agent)

STEP 1: READ THIS PLAN COMPLETELY before executing any task.
STEP 2: Read the authoritative plan at C:\Users\prora\.claude\plans\polymorphic-foraging-feather.md
STEP 3: Identify the first PROPOSED parent taskcard (start with TC-INV-000).
STEP 4: Read TC-INV-000 completely (parent + all children + all micro-steps).
STEP 5: Confirm prerequisites (for TC-INV-000: none).
STEP 6: Confirm allowed paths (docs/investigations/ only for writes).
STEP 7: Execute exactly ONE micro-step at a time.
STEP 8: After each micro-step: capture evidence immediately and update micro-step status.
STEP 9: After all micro-steps in a child: run child acceptance checks; update child status.
STEP 10: If any acceptance check fails: mark child REROUTED; fix the deficiency; re-run checks.
STEP 11: After all children of a parent CLOSED: run parent integration checks.
STEP 12: Score parent across required quality dimensions; if any < 4/5, mark REROUTED.
STEP 13: Close parent only after integration checks pass and all scores >= 4/5.
STEP 14: Move to the next parent in the DAG order (TC-INV-001, etc.).
STEP 15: At TC-INV-011: run git diff --stat before declaring second pass complete.
STEP 16: Report INVESTIGATION_COMPLETE_PLAN_READY_FOR_EXTERNAL_REVIEW with:
         branch + commit; confirmation production files unchanged; paths to 09 and 11;
         corrected measurements; top 5 problems; safest first pilot; unresolved risks.

The executing agent MUST NOT:
  - choose unrelated work outside docs/investigations/
  - modify src/, tests/, tools/, registry/, .supervisor/, or .local/
  - execute any TC-EXP-* taskcard from 09-hardened-execution-plan.md
  - skip micro-steps without marking SKIPPED_NOT_APPLICABLE with a reason
  - close a parent before all mandatory children are CLOSED
  - treat code or file existence as validation without checking content
  - claim "complete" without running git diff --stat to confirm no production changes

## Quality Scoring Dimensions

Child taskcards (scale 1-5; threshold 4 for all mandatory):
  requirement_correctness: does the output answer the requirement?
  implementation_correctness: are the claimed findings accurate to source evidence?
  scope_discipline: did the task stay within allowed paths/files?
  validation_strength: were the acceptance checks run and passed?
  evidence_completeness: are all required evidence files created with required content?
  regression_safety: can this be reverted without affecting other investigation files?

Parent taskcards (scale 1-5; threshold 4):
  root_cause_coverage: does the output address the root cause it was designed for?
  child_completeness: are all mandatory children CLOSED?
  integration_completeness: do integration checks pass?
  dependency_correctness: were all prerequisites met before starting?
  preserved_behavior: no production files changed?
  evidence_completeness: evidence/commands-and-results.md updated?
  rerun_consistency: would re-executing this phase produce the same output?
  production_readiness: is the output format correct for its audience?

---
# FINAL CONSTRAINTS
---

CANONICAL_INVESTIGATION_PACKAGE_BOUND = true
BLIND_OVERWRITES = 0
UNNECESSARY_NEW_FILES = 0
PRODUCTION_FILES_CHANGED = 0 (absolute)
MATERIAL_SECOND_PASS_CHANGES = 0 (target)
DO_NOT_EXECUTE_09_PLAN = true (09-hardened-execution-plan.md is output, not authorization)

Duplicate plan risk: NONE
  - This file is the only authoritative plan for this investigation scope
  - No competing plan exists in plans/.claude/ for this topic
  - All supporting artifacts reference this file as authoritative_plan
  - Supporting artifacts have execution_authority: false

Final expected verdict: INVESTIGATION_COMPLETE_PLAN_READY_FOR_EXTERNAL_REVIEW

# Format Factory Multi-Plan Intake — Per-Plan Summaries
**Manifest ID:** multi-plan-intake-20260625
**Date:** 2026-06-25
**Session:** 5c16c5c46b6f
**Full-Read Gate:** ALL 11 PLANS FULLY READ — PASS

---

## Plan 1: sunny-crunching-galaxy
**Type:** machinery_hardening | **Mission:** product-deepening-ledger-healing-20260625
**Taskcards:** 9 (TC-PDL-001 through TC-PDL-009) | **Priority:** P1

**Primary Intent:** Repair three critical integrity failures blocking product deepening:
1. Stale plan lock (lovely-seeking-dongarra.md) puts next-work-items.json in PLAN_LOCKED mode suppressing all 1,132 gaps
2. `continuation_allowed: true` incorrectly set for 17/20 formats (should be false — mixed_model src_layout)
3. No governance validator (V54) reads ledger before allowing product deepening items

**Key Actions Required:**
- TC-PDL-001: SUPERSEDE lovely-seeking-dongarra lock, regenerate next-work-items.json
- TC-PDL-002: Fix 17 formats from `continuation_allowed: true` → `false` in ledger
- TC-PDL-003: Add 8 missing schema fields to all 20 ledger entries
- TC-PDL-004: Backfill sal_fact_count (currently 0 for all formats)
- TC-PDL-005: Add V54 governance validator (ledger compliance gate) — ~60 LOC
- TC-PDL-006: Add repair taskcards for 17 blocked formats
- TC-PDL-007: Dry-run compliance matrix → reports/forensic-audit-20260625/
- TC-PDL-008: Verification tests
- TC-PDL-009: Evidence declaration and sprint closeout

**Stale Assumptions:** None — investigation was current as of plan creation.
**Unique Value:** Fixes gate enforcement gap that allows blocked formats to bypass the ledger.
**Recommended Disposition:** EXECUTE (all 9 taskcards)

---

## Plan 2: reflective-exploring-kurzweil
**Type:** machinery_hardening | **Mission:** terminal-closure-forensics
**Taskcards:** 10 (TC-TCF-001 through TC-TCF-010) | **Priority:** P1

**Primary Intent:** Fix premature terminal closure — 4 confirmed premature closures in reopening-register.json.
Root causes: (RC-1) `--terminal` writes TERMINAL_CLOSED without lifecycle audit (RC-2) queue exhaustion misread as completion (RC-3) closeout sprint used as basis for closure (RC-4) no `--completion-candidate` flag in write_plan_lock.py.

**Key Actions Required:**
- TC-TCF-001: Create `generate_closure_artifacts.py` + 5 investigation YAML files
- TC-TCF-002: Add `--completion-candidate` flag to write_plan_lock.py (+25 LOC)
- TC-TCF-003: Mandatory lifecycle audit gate in write_plan_lock.py + 4 guards in lifecycle_audit.py
- TC-TCF-004: Write `terminal_closure_record.json` on every TERMINAL_CLOSED
- TC-TCF-005: Strengthen autonomous reopening in autonomous_cycle_extensions.py
- TC-TCF-006: Successor plan policy (classify IN_SCOPE vs OUT_OF_SCOPE) in reopen_plan_lock.py
- TC-TCF-007: Three new validators V-TCF-001/002/003 in new terminal_closure_validators.py
- TC-TCF-008: 12-pilot test suite in test_terminal_closure_pilots.py
- TC-TCF-009: Idempotency artifacts
- TC-TCF-010: All 21 gates (TC-0 through TC-20) verified + final report

**LOC Constraints:** write_plan_lock.py: 458→573 (cap 800). lifecycle_audit.py: 540→620 (cap 800). autonomous_cycle.py at cap — use extensions only.
**Recommended Disposition:** EXECUTE (all 10 taskcards)

---

## Plan 3: woolly-yawning-stream
**Type:** investigation | **Mission:** spec-auth-inv-20260625-001
**Taskcards:** 5 phases (A-F) | **Priority:** P2

**Primary Intent:** Comprehensive SAL (Spec Authority Layer) audit. No source changes — produces 9 report artifacts.

**Key Findings from Pre-flight:**
- ODF formats have rich workbench facts (FODS: 4991 with real provenance)
- Non-ODF formats have only 3 generic template facts (no real spec parsing)
- V13 governance validator degrades to non-blocking on import error
- SAL format advisory not wired into autonomous_cycle.py (LOC cap blocks it)
- Evidence schema lacks provenance fields (no chunk_id, section_ref, page_ref)

**Outputs Required:** 9 files in `reports/spec-authority/spec-auth-inv-20260625-001/`:
inventory.md, architecture-map.md, integration-matrix.md, ai-embeddings-audit.md,
root-cause-gap-matrix.md/.json, healing-design.md, verification-plan.md, pilot-rerun-plan.md, next-healing-sprint-prompt.md

**Expected Verdict:** SPEC_AUTHORITY_INVESTIGATION_COMPLETE_CRITICAL_GAPS_FOUND
**Recommended Disposition:** EXECUTE (investigation only — no source mutations)

---

## Plan 4: tidy-dreaming-lollipop
**Type:** audit_and_repair | **Mission:** FF-HEAL-QNAME-run6 (run #6)
**Taskcards:** 15 phases (TC-SETUP-001 through TC-CLOSEOUT-001) | **Priority:** P1

**Primary Intent:** Comprehensive idempotent QNAME/SAL/capability healing audit. Three safe repairs:
1. Gap severity classification — 1,120 gaps have no `severity` field (triage is blind)
2. Architecture doc addendum — `docs/architecture.md` stale (says "3/20 qname verified" when actual is 20/20)
3. Parity matrix refresh for 18 formats without spec_parity_status

**Current System State:** 1,609 tests passing, 0 failures; 20/20 Python formats; 14,309 SAL facts; 21 qname registries; 181 Python files with spec_qname; 1,132 capability gaps (1,120 missing severity field).

**Key Outputs:** 23+ files in `.local/evidences/FF-HEAL-QNAME-{RUN_ID}/`
**Safe Repair:** gap-ledger.json severity classification (idempotent — only adds missing fields)
**Stale Assumption:** Prior run was 2026-06-23; system state has progressed since
**Recommended Disposition:** EXECUTE (3 safe repairs + full audit artifacts)

---

## Plan 5: serialized-tickling-bentley
**Type:** machinery_hardening | **Mission:** FF-MREAD-20260625
**Taskcards:** 13 (TC-MREAD-001 through TC-MREAD-013) | **Priority:** P2

**Primary Intent:** Comprehensive machinery readiness audit before next product deepening wave.
Prove: QName → SAL → RCAL → Feature → Source chain is end-to-end functional, not ghost infrastructure.
Lane isolation proof, representative pilots (FODS .NET, NDJSON Python, CSV cross-language, FODS→CSV export).
Add Section 30 to master-plan.md. Emit execution handoff.

**Scope:** All 29 products (20 Python + 9 .NET), 13 audit phases, 4 pilots, 20+ output files.
**Non-Goals:** Broad backfill, PyPI/NuGet publish, Gate 11 commercial approval.
**Key Dependencies:** TC-MREAD-001 → all others sequential.
**Stale Assumptions:** Claims check_continuation returns POST_PLAN_TERMINAL — RECON shows it returns CONTINUE now.
**Recommended Disposition:** EXECUTE (comprehensive audit, all 13 taskcards)

---

## Plan 6: rustling-jumping-otter
**Type:** machinery_hardening | **Mission:** MACH-LIF-FORENSICS-20260623 (continuation)
**Taskcards:** 7 (TC-RJO-001 through TC-RJO-007) | **Priority:** P1

**Primary Intent:** Continue agile-munching-quasar mission. Prove real AUDIT_REQUIRES_ITERATION → work → AUDIT_PASS lifecycle cycle.

**Critical Gap:** `lifecycle_audit.py` returns vacuous AUDIT_PASS with `mission_complete: true` when called without `--plan-path` (0 taskcards parsed). This masks real open work.

**Already Done (prior sessions):** TC-LIF-000 through TC-LIF-011 (lifecycle_audit.py created, --audit-gate wired, encoding bug fixed, tests committed).

**What Remains:**
- TC-RJO-001: Reconcile agile-munching-quasar.md (mark TC-LIF-009/010/011 CLOSED)
- TC-RJO-002: Execute TC-LIF-012 — real iteration cycle proof (3-step AUDIT_REQUIRES_ITERATION → AUDIT_PASS)
- TC-RJO-003: Investigate TC-LIF-013 (post-TERMINAL_CLOSED lock overwrite)
- TC-RJO-004: Add vacuous-call guard to lifecycle_audit.py + 2 tests (19 total)
- TC-RJO-005: Commit write_plan_lock.py simplification
- TC-RJO-006: Close agile-munching-quasar with --terminal --audit-gate
- TC-RJO-007: Evidence declaration

**Unique Value:** Closes the lifecycle iteration gap that caused 4 confirmed premature closures.
**Recommended Disposition:** EXECUTE (all 7 taskcards)

---

## Plan 7: eager-launching-phoenix
**Type:** forensic_audit_and_healing | **Mission:** FORENSIC-AUDIT-EAGER-PHOENIX-20260625
**Taskcards:** 16 (TC-FA-001 through TC-FA-016) | **Priority:** P2

**Primary Intent:** Comprehensive spec-to-code forensic audit for all 20 formats. Traces each through:
SPEC SOURCE → SAL FACTS → QNAMES → CAPABILITIES → FEATURES → CODE → TESTS → PACKAGES → CONSUMER PROOF.

**Batch Structure:**
- Batch 0 (TC-FA-001–008): Baseline capture + loss analysis + root causes + taskcard register
- Batch 1 (TC-FA-009): SAL chain repair pilot — CSV/RFC4180
- Batch 2 (TC-FA-010): QName gap closure (11 gaps)
- Batch 3 (TC-FA-011): Capability compiler spec-fact wiring
- Batch 4 (TC-FA-012): Analytics masquerade pilot — GNUMERIC separation
- Batch 5 (TC-FA-013): Domain model backfill (8 missing Python formats)
- Batch 6 (TC-FA-014): Writer/exporter backfill
- Batch 7 (TC-FA-015): Package & consumer proof completion (all 20 at PROOF_LEVEL_4+)
- Batch 8 (TC-FA-016): Reaudit + idempotency

**Known root causes:**
- RC-SAL-001: SAL chain broken for 10 non-ODF formats
- RC-CAP-001: Capability extraction goal-based, not spec-fact-driven
- RC-CODE-001: Analytics masquerade (16 files)
- RC-CODE-002: Missing domain models (10 Python formats)
- RC-CODE-003: Missing writers (8 formats)

**Recommended Disposition:** EXECUTE (start with Batch 0, then sequential batches)

---

## Plan 8: twinkly-gliding-thimble
**Type:** machinery_hardening | **Mission:** SKILL-FIRST-002
**Taskcards:** 8 (TC-SFE2-000 through TC-SFE2-007) | **Priority:** P1

**Primary Intent:** Close delta between SKILL-FIRST-001 (63 skills, PRODUCTION-READY) and full protocol requirements:
- 4 enforce steps were SKIPPED (steps 7, 8, 9, 11 are "prompt-backed")
- SKILL-GAP-011: rollback-and-recovery has no route (29/30 ACTIVE)
- Pilots C-H not done (only A and B done)
- skill_system_baseline.yaml, skill-quality matrix, execution receipts not produced
- adhoc migration register for 3 root tools unaddressed

**Key Actions:**
- TC-SFE2-000: Continuity gate + write skill-system-baseline.yaml
- TC-SFE2-001: Full enforce-skill-first-execution (no SKIPPED steps)
- TC-SFE2-002: Fix SKILL-GAP-011 routing → 30/30 ACTIVE
- TC-SFE2-003: Pilot C — create `audit-root-tools` skill (~40 LOC)
- TC-SFE2-004: Pilot G — ad-hoc script migration (3 close_*.py scripts)
- TC-SFE2-005: Pilots D, E, F, H
- TC-SFE2-006: Execution receipts + quality matrix
- TC-SFE2-007: Final report + master-plan update + closeout

**Recommended Disposition:** EXECUTE (all 8 taskcards)

---

## Plan 9: vast-weaving-lampson
**Type:** machinery_hardening | **Mission:** VAST-WEAVING-LAMPSON-001
**Taskcards:** 15 (TC-VWL-001 through TC-VWL-015) | **Priority:** P1

**Primary Intent:** Fix blocking plan lock (eager-wishing-bear.md IN_PROGRESS), produce forensic proof
two historical violations are repaired, add production sprint system design to master-plan.md,
execute pilot program (historical reconstruction, governance repair, SYLK/TOML/.NET/binary format deepening, idempotency).

**Current State Check:** check_continuation.py already returns CONTINUE (lock likely fixed).
TC-VWL-001 may already be complete. Recon needed before executing.

**Unique Value:** 8 pilots covering diverse format types + production sprint system design.
**Stale Assumption:** TC-VWL-001 may already be resolved (current continuation returns CONTINUE).
**Recommended Disposition:** EXECUTE with recon first (verify TC-VWL-001 state before proceeding)

---

## Plan 10: humble-meandering-bachman
**Type:** machinery_hardening | **Mission:** system-healing-product-acquisition-unblock-20260625
**Taskcards:** 6 (TC-SHR-000 through TC-SHR-005) + 1 optional | **Priority:** P2

**Primary Intent:** Formally close Wave 3 system-healing gate. The gate was last checked 2026-06-22 with
5 PASS / 3 PARTIAL. Since then, Lane 14 (lane_enforcement_validator.py) and Lane 15 (healing modules)
have been fixed. Only Condition 2 (action_queue advisory_only) remains uncertain.

**Key Actions:**
- TC-SHR-000: Run check_system_healing_gate.py live, capture lane-by-lane verdict
- TC-SHR-001: Fix Lane 2 (action_queue advisory_only) if still PARTIAL
- TC-SHR-002: Produce formal system-healing-gate-verdict-20260625.md
- TC-SHR-003: Update sprint-safety-lock to post-repair verdict
- TC-SHR-004: Run full validation suite (0 test failures required)
- TC-SHR-005: Evidence declaration + supervisor pipeline

**Expected Verdict:** PASSED or CONDITIONAL (Conditions 7+8 now resolved by code)
**Recommended Disposition:** EXECUTE (run gate first, then fix Condition 2 if needed)

---

## Plan 11: zany-riding-goblet
**Type:** execution_mission | **Mission:** FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-001
**Taskcards:** ~35 (TC-PQ-PRE, TC-PQ-000 through TC-PQ-083) | **Priority:** P3

**Primary Intent:** Execute the healing mission from a 57-file product quality review bundle.
The prior analysis plan (FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001) is TERMINAL_CLOSED.

**Lock Status:** SUPERSEDED in plan-locks (from both session 5c16c5c46b6f and f9145814a1ee).
This means the plan was started and then superseded in prior sessions — recon required to determine actual progress.

**28 forensic findings (F-CRIT-001 through F-LOW-004)** were corrected in v2/v2.1 before execution.

**Key Waves:**
- WAVE0 (TC-PQ-000/001): Bundle completeness gate + stale finding reverification
- WAVE1 (TC-PQ-010/011): P0 release blockers — Gate 11 false claims + ZST .NET writer
- [Additional waves for Python API improvements, .NET fixes, documentation, etc.]

**Master plan target:** §57 (new section to add after current last section)
**Recommended Disposition:** REVALIDATE_THEN_EXECUTE (check what was done in prior sessions first)

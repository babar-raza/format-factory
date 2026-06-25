# Machinery Repair Plan
# Sprint: ff-machinery-readiness-audit-20260625

## Purpose

This plan describes the sequence and dependencies for repairing the 4 BLOCKER gaps
identified in the system gap matrix (artifact 15). After all 4 blockers are resolved,
the system will be ready for repeatably-correct spec-backed product deepening.

---

## Ordered Repair Sequence

### Step 1: Authority Repair — SAL Pipeline (SAL-REPAIR-001)

**Gap:** GAP-MACH-001 — 17/20 SAL pipeline tools dormant
**Sprint type:** Machinery Lane 1 (Wave 1A)
**Prerequisite:** None (can start immediately)

**What to do:**
1. Read RFC 4180 spec text (public: https://datatracker.ietf.org/doc/html/rfc4180)
2. Extract 3-5 key facts manually (e.g., delimiter, quoting, CRLF linebreak)
3. Write these as FACT-CSV-001 through FACT-CSV-005 in `.local/spec-cache/sal-facts-csv.json`
4. Wire a minimal `sal_csv_runner.py` that reads the RFC and can regenerate these facts
5. Prove the chain: spec text → sal-facts-csv.json → spec_fact_refs in a work item

**Shortcut path (acceptable for proof):**
- Manual extraction is acceptable IF the runner is architecturally wired
- Full automation of spec_parser tool can come later
- The proof only needs to show the chain CAN work — not that it's fully automated

**Success criteria:**
- sal-facts-csv.json has ≥3 FACT-CSV-NNN entries
- At least 1 work item in next-work-items.json cites one of these FACT-CSV-NNN IDs
- V43 validator for CSV finds at least 1 spec_fact_ref in the declaration

**Unlocks:** Wave B product deepening for CSV; proves pattern for 9 remaining formats

---

### Step 2: Translation Repair — Replace _EXPANSION_GOALS (CAPABILITY-REPAIR-001)

**Gap:** GAP-MACH-002 — task generator uses hardcoded list
**Sprint type:** Machinery Lane 3 (Wave 1B)
**Prerequisite:** GAP-MACH-001 must be closed (so gap-ledger has at least 1 format with spec facts)

**What to do:**
1. Read tools/supervisor/autonomous_task_generator.py to understand _EXPANSION_GOALS structure
2. Read reports/capability-layer/gap-ledger.json to understand gap entry structure
3. Replace _EXPANSION_GOALS with a `load_top_gaps(format_filter, limit)` function
4. Top-N selection by priority score (P0=highest) × format filter
5. Ensure output work items include gap_ledger_ref + any spec_fact_refs from SAL cache

**Acceptance criteria:**
- Running autonomous_task_generator.py produces work items citing gap_ledger_ref values
- No _EXPANSION_GOALS list remains in the file
- Work items with no spec facts cite at least the gap entry's capability_type

**Unlocks:** Task generator output is now traceable to spec authority (not hardcoded)

---

### Step 3: Generation Repair — Feature Compiler Phase 1 (FEATURE-COMPILER-001)

**Gap:** GAP-MACH-005 — gap cannot drive taskcard skeleton with spec_fact_refs
**Sprint type:** Machinery Lane 3 (Wave 1B)
**Prerequisite:** SAL-REPAIR-001 (need real spec facts); CAPABILITY-REPAIR-001 (gap-ledger is source)

**What to do:**
1. Read docs/capability-feature-compiler-spec.md (design exists)
2. Implement the Phase 1 compiler function: `compile_gap_to_work_item(gap: dict) -> dict`
3. Input: gap entry from gap-ledger.json (has gap_id, format, capability_type, spec_fact_refs)
4. Output: work item skeleton in next-work-items.json format with all required fields:
   - item_id: derived from gap_id
   - gap_ledger_ref: gap_id
   - spec_fact_refs: from gap's spec_fact_refs field
   - capability_ref: gap's capability_type
   - item_type: PRODUCT_SOURCE
   - format_name: gap's format

**Acceptance criteria:**
- Given CSV gap entry with FACT-CSV-001 ref → compiler produces work item with spec_fact_ref=FACT-CSV-001
- TC-GUARD-001 does NOT trigger rework for compiler-produced items (they have required fields)
- 3+ unit tests in tests/supervisor/test_feature_compiler_phase1.py

**Unlocks:** Product deepening sprint tasks come from spec-backed source, not hardcoded list

---

### Step 4: Supervision Repair — Wave Gate + Overclaim Detector

#### Step 4a: Overclaim Detector Wiring (SUPERVISOR-CONTINUATION-001)
**Gap:** GAP-MACH-003
**Sprint type:** Machinery Lane 14 (Wave 0)
**Prerequisite:** None

**What to do:**
1. Find the overclaim detector in autonomous_cycle.py or a related module
2. Wire it into Step 2d: for each declaration item, run patterns
3. Items with overclaim pattern → add to rework_items with reason=overclaim_detected
4. Add 3 tests: (a) clean item passes, (b) overclaim pattern caught, (c) rework output correct

#### Step 4b: Wave Gate Pre-Check (SUPERVISOR-LANES-001)
**Gap:** GAP-MACH-004 + GAP-MACH-011
**Sprint type:** Machinery Lane 14 (Wave 0)
**Prerequisite:** SAL-REPAIR-001 complete (wave gate checks SAL facts exist)

**What to do:**
1. Create tools/supervisor/wave_gate_check.py
2. Implement `check_wave_gate(target_lane: int, target_format: str) -> WaveGateResult`
3. For product lanes (7-13): check SAL facts exist OR CHAIN_BROKEN_ACKNOWLEDGED in registry
4. Wire as Step 0c in autonomous_cycle.py (before Step 1)
5. On failure: `continuation_state = NO_BROKEN_BASELINE`

---

### Step 5: Backfill Repair — Automated Scanner (QNAME-BACKFILL-SYSTEM-001)

**Gap:** GAP-MACH-007 — 19 formats without symbol inventory
**Sprint type:** Machinery Lane 2 (Wave 1A)
**Prerequisite:** None (pure tooling, no product source changes)

**Scope:** Build 5-module system (see artifact 12 for full design)
**Effort:** 1 sprint to build system; 1 sprint per 3-format batch to run it

---

### Repair Sprint Sequence

| Sprint | Type | Taskcards | Goal |
|---|---|---|---|
| REPAIR-01 | Machinery Wave 0 | SUPERVISOR-CONTINUATION-001 | Overclaim detector wired |
| REPAIR-02 | Machinery Wave 1A | SAL-REPAIR-001, QNAME-BACKFILL-SYSTEM-001, EVIDENCE-LEDGER-001 | SAL chain proven for CSV; backfill tooling built |
| REPAIR-03 | Machinery Wave 1B | CAPABILITY-REPAIR-001, FEATURE-COMPILER-001, SKILL-HARDENING-001 | Task generator driven by gap-ledger; compiler Phase 1 complete |
| REPAIR-04 | Machinery Wave 1B | SUPERVISOR-LANES-001 | Wave gate code-enforced (depends on SAL-REPAIR-001) |
| REPAIR-05 | Machinery Wave 1B | QNAME-BACKFILL-PILOT-001, SAL-REPAIR-002, QNAME-VALIDATORS-001 | Backfill pilot for NDJSON/TSV/SYLK; V43 upgraded to FAIL |
| REPAIR-06 | Product Wave B | PRODUCT-PILOT-001 (ODS pilot first) | First spec-backed product deepening proof |

---

## Repairs That Run in Machinery Lane (No Product Source Changes)

| Taskcard | Lane | Changes machinery source? | Changes product source? |
|---|---|---|---|
| SAL-REPAIR-001 | 1 | YES (sal_csv_runner.py) | NO |
| CAPABILITY-REPAIR-001 | 3 | YES (autonomous_task_generator.py) | NO |
| FEATURE-COMPILER-001 | 3 | YES (capability_feature_compiler.py) | NO |
| SUPERVISOR-LANES-001 | 14 | YES (autonomous_cycle.py) | NO |
| SUPERVISOR-CONTINUATION-001 | 14 | YES (autonomous_cycle.py) | NO |
| EVIDENCE-LEDGER-001 | 1 | YES (gap-ledger.json) | NO |
| QNAME-BACKFILL-SYSTEM-001 | 2 | YES (backfill_*.py tools) | NO |

**All 7 critical repairs are machinery-only.** No product source changes needed to fix blockers.

## Repairs That Touch Product Source (Governed by Skill-First Policy)

| Taskcard | Lane | Changes product source? | Skill required |
|---|---|---|---|
| SRC-STANDARDIZATION-001 | 7 | YES (dif_analytics.py, etc.) | /decompose-monolithic-codec |
| SRC-MASQUERADE-001 | 7 | YES (rename 2 files + imports) | /add-python-api (for import updates) |
| QNAME-BACKFILL-PILOT-001 | 2 | YES (inventory + migration changes) | /qname-backfill |
| PRODUCT-PILOT-001 | 9 | YES (consumer roundtrip examples) | /add-python-api or /add-installed-package-example |

---

## Completion Criteria

The machinery is considered READY_FOR_PRODUCT_DEEPENING when:

1. **SAL-REPAIR-001 CLOSED** — at least 1 non-ODF format has spec facts extracted
2. **CAPABILITY-REPAIR-001 CLOSED** — _EXPANSION_GOALS removed; gap-ledger drives tasks
3. **FEATURE-COMPILER-001 CLOSED** — gap entry → work item with spec_fact_refs works
4. **SUPERVISOR-CONTINUATION-001 CLOSED** — overclaim detector is wired
5. **SUPERVISOR-LANES-001 CLOSED** — wave gate is code-enforced

When all 5 are CLOSED, the system moves from READY_AFTER_TARGETED_MACHINERY_REPAIRS
to READY_FOR_PRODUCT_DEEPENING.

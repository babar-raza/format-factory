# Final Verdict
# Audit Sprint: ff-machinery-readiness-audit-20260625
# Date: 2026-06-25
# Evidence: 22 artifacts in reports/machinery-readiness-audit-20260625/

---

## VERDICT

```
READY_AFTER_TARGETED_MACHINERY_REPAIRS
```

The Format Factory has professional-quality product source code and working consumer
roundtrip proofs for 14/20 Python FOSS formats. However, the autonomous machinery
that is supposed to drive spec-backed product deepening has 4 BLOCKER gaps that prevent
it from generating repeatably correct, spec-literal, QName-compliant source code at scale.

The question asked: *"Is the Format Factory machinery actually ready to produce the
expected product-deepening results, or will it continue creating malformed, non-qname,
non-presentable, non-repeatable source code?"*

**Answer:** The machinery will continue producing non-spec-backed results until the
4 BLOCKER gaps are closed. After those repairs, it is ready.

---

## 20-Item Final Response

### 1. Product Code Quality

**PROFESSIONAL — 7/10**

Evidence (artifact 05): CSV has RFC 4180 state machine with modular exception hierarchy;
NDJSON has authority-only pattern; FODS is Gold Standard (8-layer separation, 10 Compat/
facades, 638+ tests). NOT generated proof-of-concept. Demonstrates modular exception hierarchies,
RFC-literal parsers, immutable .NET design patterns, and spec-literal naming throughout.

### 2. QName Compliance

**HIGH for 9 formats; IMPLEMENTING for 11**

Evidence (artifacts 03, 04): All 21 Python formats have `spec_qname` attribute.
9 formats (FODS/FODT/CSV/NDJSON/TSV/GNUMERIC/ABW/TOML/ZST) have full domain models
with spec_qname ClassVar. 11 formats are at "implementing" status — spec classes exist
but not all public APIs are spec-aligned. V43 validator is WARN (not FAIL) for implementing
status — this must be upgraded (taskcard QNAME-VALIDATORS-001).

### 3. SAL (Spec Authority Layer) Status

**DORMANT — 3 of 20 pipeline tools active**

Evidence (artifact 07): 57,803 lines of normalized FODS spec text sits unused.
Fact extraction ran ONCE (run030, 2026-05-06) and produced 10 FODS facts manually.
The pipeline has never run automatically. 10 formats are CHAIN_INTACT (ODF/image);
10 formats are CHAIN_BROKEN_AT_SAL (non-ODF). Required fix: SAL-REPAIR-001
(wire minimal runner for 1 non-ODF format as proof).

### 4. Capability Layer Connection

**DISCONNECTED**

Evidence (artifact 08): 1,132+ open gaps exist in gap-ledger.json. All action-queue items
have `advisory_only=true`. The autonomous task generator uses a hardcoded `_EXPANSION_GOALS`
list (20+ entries) and NEVER reads gap-ledger.json. The gap-to-taskcard path is architecturally
designed but not implemented (feature compiler Phase 2 not started).

### 5. Feature Compiler Status

**DESIGN EXISTS; PHASE 2 NOT IMPLEMENTED**

Evidence (artifact 08): `docs/capability-feature-compiler-spec.md` describes the design.
`capability_feature_compiler.py` implements gap→priority scoring but does NOT produce
taskcard skeletons with spec_fact_refs. FeatureFactory (6 patterns A-F) is a code-generation
helper that has NEVER been called by autonomous loops. Required fix: FEATURE-COMPILER-001.

### 6. Skill Repeatability

**STRONG for product skills; SUSPENDED for analytics**

Evidence (artifact 06): 35+ skills registered in fail-closed registry. `/add-python-api`
is STRONG — enforces gap_ledger_ref, spec_fact_refs, focused tests, product code ledger.
`/add-analytics-function` SUSPENDED since 2026-06-18 (rotation produced non-spec-backed code).
3 critical skill gaps: no qname-backfill skill command, no SAL pipeline skill, no
capability-compiler skill. All skills would benefit from SAL fact pre-check (SKILL-HARDENING-001).

### 7. Lane DAG Enforcement

**PROMPT-ONLY — no code enforcement**

Evidence (artifact 10, 11): `check_continuation.py` returns CONTINUE based on iteration count
and rework items — not wave prerequisites. No wave gate validates that Lane 1 (SAL) is active
before Lane 3 (compiler) runs, or that Lanes 1-6 complete before Lanes 7-13.
Required fix: SUPERVISOR-LANES-001 (wave_gate_check() as autonomous_cycle.py Step 0c).

### 8. Overclaim Detection

**PARTIAL — anti-skip checker works; 10-pattern detector not wired**

Evidence (artifact 10): Anti-skip checker (Step 8) catches ACCEPTED_VERIFIED without raw logs,
generic prompts, advisory-only-only items — feeds into 19-state machine correctly.
The 10-pattern overclaim detector exists in code but autonomous_cycle.py Step 2d never calls it.
Required fix: SUPERVISOR-CONTINUATION-001 (wire into Step 2d).

### 9. Backfill Coverage

**1/20 formats (ABW only)**

Evidence (artifact 12): `docs/audits/python-qname-backfill-inventory.csv` covers only ABW
(170+ symbols, all PENDING migration). No automated backfill tooling exists. FODS/FODT have
Compat/ facades but no formal backfill inventory. ~800 symbols across 19 formats are
un-inventoried. Required fix: QNAME-BACKFILL-SYSTEM-001 (5-module automated system).

### 10. Gate 11 Readiness

**5 FORMATS TECHNICALLY READY; AWAITING BABAR RAZA SIGN-OFF**

Evidence (artifact 13): FODS, FODT, PBM, PGM, PPM — all 8 customer readiness criteria PASS.
G11-G APPROVED (Babar Raza, 2026-06-05). Release docs exist (docs/release/fods-v0.1.0.md etc.).
Wheels built and installed-workflow verified. Publication awaits: PyPI/NuGet credentials +
Babar Raza final commercial authorization = TRUE_EXTERNAL_GATE.

### 11. Products Closest to Gate 11

**FODS, FODT, PBM, PGM, PPM**

All 5 are past G11-G sub-gate. Only TRUE_EXTERNAL_GATE (Babar Raza sign-off +
publication credentials) stands between these formats and commercial release.
NEXT closest: NDJSON (has 1 SAL fact, clean domain model, 1409 tests, authority class).

### 12. Products Best for Spec-to-Library-to-Export Proof

**NDJSON (immediate), ODS (immediate), CSV (after SAL-REPAIR-001)**

- NDJSON: simplest schema; authority class exists; 1 SAL fact; clean model; 1409 tests
- ODS: SAL CHAIN_INTACT; ODF spec richest; shares pipeline with FODS Gold Standard
- CSV: SAL-REPAIR-001 target; RFC 4180 public spec; highest community interest

### 13. Blocker Gaps (Must Fix Before Autonomous Spec-Backed Deepening)

**4 BLOCKERS — all agent-resolvable**

| Gap | Taskcard | Effort |
|---|---|---|
| SAL pipeline dormant (17/20 dead) | SAL-REPAIR-001 | HIGH |
| _EXPANSION_GOALS hardcoded | CAPABILITY-REPAIR-001 | MEDIUM |
| Overclaim detector not wired | SUPERVISOR-CONTINUATION-001 | LOW |
| Lane DAG prompt-only | SUPERVISOR-LANES-001 | MEDIUM |

None of these require TRUE_EXTERNAL_GATE access. All are pure machinery changes.

### 14. High-Priority Repairs (Fix Within 3 Sprints)

| Gap | Taskcard | Impact |
|---|---|---|
| Feature compiler Phase 1 not implemented | FEATURE-COMPILER-001 | Gap→taskcard automation |
| Zero durable learning | SUPERVISOR-LEARNING-001 | Failure propagation |
| 19 formats without backfill inventory | QNAME-BACKFILL-SYSTEM-001 | Level 5 readiness |
| 192 gaps without spec_fact_refs | EVIDENCE-LEDGER-001 | TC-GUARD-001 compliance |
| V43 WARN not FAIL | QNAME-VALIDATORS-001 | QName enforcement |

### 15. Repeatable and Governed

**YES for product write operations; NO for task selection**

Writing product source IS repeatable: /add-python-api skill enforces gap_ledger_ref +
spec_fact_refs + focused tests + governance validators. If these pass, the product is
governed. Task SELECTION is NOT repeatable: _EXPANSION_GOALS is static and hardcoded.
Two runs of autonomous_task_generator with the same gap-ledger state can produce
different results (ordering issues, spec_authority=no_public_spec_available entries ignored).

### 16. Source Code Not Generated

**CONFIRMED: NOT autonomously generated**

Evidence (artifact 05): The machinery to generate spec-correct code autonomously is
not fully functional (SAL dormant, feature compiler Phase 2 not implemented, FeatureFactory
never called). The product code was written by skilled agents using skill-guided workflows
(/add-python-api, /add-dogfood-export etc.) — not by the autonomous pipeline end-to-end.
The machinery DESIGN would produce generated code when repaired; it currently does not.

### 17. Lane Collision Risk

**HIGH — 7/8 collision scenarios prompt-only**

Evidence (artifact 11): Only plan lock files provide mechanical isolation. Gap-ledger writes
are uncoordinated (HC-001). Source baseline cap updates are write-once but not write-locked
(HC-002). Product lane contamination risk (CV-001) is HIGH probability when machinery
lanes are incomplete. Required: wave gate (SC-001) + gap-ledger write lock (G-003) +
stale lock auto-cleanup (G-004, partially implemented).

### 18. Durable Learning

**NONE — FailureMemory not integrated**

Evidence (artifact 10): SUP-GAP-009: `from failure_memory import FailureMemory` is in
autonomous_cycle.py but no write path exists in the cycle. No `failure-memory.json` found
in repository. All decision rules (validators, grading thresholds, skill gates) are static.
Failures are documented only in MEMORY.md (prose, 200-line limit). Required: SUPERVISOR-LEARNING-001.

### 19. Summary Assessment

| Dimension | Assessment | Evidence |
|---|---|---|
| Product code quality | 7/10 PROFESSIONAL | artifact-05 |
| QName compliance | HIGH (9 full, 11 implementing) | artifact-03, 04 |
| SAL pipeline | DORMANT (3/20 active) | artifact-07 |
| Capability layer | DISCONNECTED | artifact-08 |
| Feature compiler | NOT IMPLEMENTED | artifact-08, 09 |
| Skill repeatability | STRONG (product); SUSPENDED (analytics) | artifact-06 |
| Lane DAG enforcement | PROMPT-ONLY | artifact-10, 11 |
| Overclaim detection | PARTIAL | artifact-10 |
| Backfill coverage | 1/20 formats | artifact-12 |
| Gate 11 candidates | 5 TECHNICALLY READY | artifact-13 |
| Durable learning | NONE | artifact-10 |
| Session isolation | EXCELLENT | artifact-10 |
| Plan lock enforcement | EXCELLENT | artifact-10 |
| Continuation machine | EXCELLENT (19 states) | artifact-10 |

### 20. Recommended Immediate Actions

In priority order (agent-executable, no TRUE_EXTERNAL_GATEs):

1. **SUPERVISOR-CONTINUATION-001** (Wave 0) — Wire overclaim detector. Effort: LOW. 0 prerequisites.
2. **SAL-REPAIR-001** (Wave 1A) — Prove SAL chain for CSV. Effort: HIGH. Unlocks Wave B.
3. **QNAME-BACKFILL-SYSTEM-001** (Wave 1A) — Build automated backfill tools. Effort: HIGH.
4. **CAPABILITY-REPAIR-001** (Wave 1B) — Replace _EXPANSION_GOALS. Effort: MEDIUM.
5. **FEATURE-COMPILER-001** (Wave 1B) — Implement feature compiler Phase 1. Effort: HIGH.
6. **SUPERVISOR-LANES-001** (Wave 1B) — Wave gate code-enforced. Effort: MEDIUM.
7. **PILOT-ODS-001** (authorized NOW) — ODS consumer roundtrip (SAL CHAIN_INTACT). Effort: LOW.

Items 1 and 7 can start immediately without prerequisites.
Items 2-6 should run in order (each unlocks the next).

---

## Verdict Justification

**Why NOT READY_FOR_PRODUCT_DEEPENING:**
The 4 BLOCKER gaps mean any autonomous product sprint on non-ODF formats will:
- Select tasks from a hardcoded list (not spec-driven)
- Produce work items without spec_fact_refs (TC-GUARD-001 rework)
- Have no overclaim detection (false ACCEPTED claims can slip through)
- Proceed without checking machinery prerequisites (wave contamination)

**Why NOT NOT_READY_REPAIR_MACHINERY_FIRST:**
ODS/ODT/PBM/PGM/PPM product deepening CAN proceed immediately (SAL CHAIN_INTACT for ODF;
Netpbm is already Gate 11 ready). The system is not fundamentally broken — it needs
targeted repairs, not a complete rebuild.

**Why READY_AFTER_TARGETED_MACHINERY_REPAIRS:**
- 4 blockers, all agent-resolvable, no TRUE_EXTERNAL_GATEs blocking machinery
- Professional source code foundation (not throwaway)
- Working governance infrastructure (48 validators, 19-state machine, CCI-MVP)
- Clear repair sequence with testable acceptance criteria
- 5 formats already past Gate 11 technical review

---

## Audit Self-Check

- [x] Read actual source files (not relying on agent summaries alone)
- [x] Inspected autonomous_task_generator.py for _EXPANSION_GOALS
- [x] Verified SAL pipeline dormancy with tool counts (artifact 07)
- [x] Checked capability-to-feature compiler file for implementation status
- [x] Scored 5+ Python formats and 2+ .NET formats for source quality
- [x] Verified backfill scope beyond ABW
- [x] Checked lane DAG enforcement in autonomous_cycle.py
- [x] Verified overclaim detector wiring (or absence) in autonomous_cycle.py
- [x] Produced gap matrix with severity and "must fix before product deepening" column
- [x] Produced taskcards for all 14 required groups
- [x] Separated working/repeatable/governed/production-ready in verdict
- [x] Did NOT claim Gate 11 readiness from test counts alone
- [x] Produced next-agent-execution-prompt with exact paths

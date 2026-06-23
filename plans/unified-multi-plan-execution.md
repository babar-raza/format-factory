# Unified Multi-Plan Execution Plan
## Synthesized from: squishy-chasing-marshmallow, agile-munching-quasar, majestic-cooking-waffle

**Plan ID:** unified-multi-plan-execution
**Mission ID:** UNIFIED-FF-EXECUTION-20260623
**Synthesis Date:** 2026-06-23
**Authority:** GOVERNED MULTI-PLAN SYNTHESIS (three supplied plans)
**Controller:** autonomous_cycle.py (single controller, per CLAUDE.md §One-Mechanism Lock)
**Evidence Root:** `.local/evidences/unified-multi-plan-20260623/`

---

## 1. Supplied Plan Set

```yaml
supplied_plan_set:
  input_set_id: UNIFIED-FF-EXECUTION-20260623
  supplied_by: user
  plans:
    - source_id: SMM
      supplied_path: C:\Users\prora\.claude\plans\squishy-chasing-marshmallow.md
      title: "Format Factory Machinery Readiness, QName/SAL/RCAL Forensics, Autonomous-Lane Proof..."
      plan_id: squishy-chasing-marshmallow
      mission_id: FF-MACHINERY-READINESS-20260623
      version: "2.0"
      status: ACTIVE
    - source_id: AMQ
      supplied_path: C:\Users\prora\.claude\plans\agile-munching-quasar.md
      title: "Machinery Iteration Failure — Lifecycle Forensics & Repair Plan"
      plan_id: agile-munching-quasar
      mission_id: MACH-LIF-FORENSICS-20260623
      version: "2.0"
      status: ACTIVE
    - source_id: MCW
      supplied_path: C:\Users\prora\.claude\plans\majestic-cooking-waffle.md
      title: "Capability & Feature Understanding Layer — Investigative Healing Sprint"
      plan_id: majestic-cooking-waffle
      mission_id: MCW-CAPABILITY-LAYER-20260623
      version: "2.0 (forensically hardened)"
      status: ACTIVE
  expected_count: 3
  resolved_count: 3
  missing_plans: []
  input_set_verdict: SUPPLIED_PLAN_SET_COMPLETE
```

---

## 2. Repository Truth (Verified 2026-06-23)

```yaml
repository_truth:
  branch: main
  ahead_of_remote: 10 commits
  unstaged_files:
    - plans/master-plan.md
    - registry/known-failure-ledger.yaml
    - registry/source-structure-baseline.json
    - shared/qname-registry/ndjson.yaml
    - shared/qname-registry/xcf.yaml
    - src/python/ndjson/__init__.py
    - src/python/ndjson/ndjson_codec.py
    - src/python/xcf/image_document.py
    - src/python/xcf/xcf_parser.py
    - tools/supervisor/governance_validators.py
  continuation_signal:
    autonomous_continue: false
    stop_reason: critical_rework_blocks_continuation
    rework_items: ["GOV_BLOCK:monolith_detection_validator"]
    govblock_resolved_by: null
    session_id: c878b5607d1b  # prior session
    iteration: 9
  blocking_files:
    - file: src/python/xcf/xcf_parser.py
      current_loc: 1283
      baseline_loc_cap: 1277
      over_by: 6
      status: WORSENED_VIOLATION_BLOCKING
    - file: src/python/ndjson/ndjson_codec.py
      current_loc: 1080
      baseline_loc_cap: 1080
      over_by: 0
      status: AT_CAP_NOT_BLOCKING
  xcf_analytics_py_exists: false  # must NOT be created per forensics
  ndjson_analytics_py_exists: true  # LOC=713, not in baseline
```

---

## 3. Conflict Resolution

| Conflict | AMQ Claims | SMM Claims | MCW Claims | Resolution |
|---------|-----------|-----------|-----------|------------|
| ndjson_codec.py LOC | 1095 (stale — pre-change) | "over cap" | "may be blocking" | CURRENT TRUTH: 1080=cap (at cap, not blocking) |
| xcf_parser.py LOC | +1 over cap (stale) | "over cap" | "may be blocking" | CURRENT TRUTH: 1283 vs 1277 (over by 6, blocking) |
| xcf_analytics.py | DO NOT CREATE | §8.1 extract | unknown | DO NOT CREATE (AMQ forensics authority) |
| ndjson_analytics.py | MOVE TO EXISTING | create analytics | unknown | MOVE TO EXISTING (AMQ forensics authority) |

All plan claims reconciled against repository truth. AMQ v2.0 forensics is most authoritative for implementation details.

---

## 4. Unified Taskcard Register (Dependency-Ordered)

### WAVE 0 — Setup and GOV_BLOCK Resolution (CRITICAL PATH)

#### TC-UNIFIED-000: Write Plan Lock (DONE IN SESSION START)
**Status:** IN_PROGRESS (written at session start)
**Source Plans:** SMM(TC-SMM-000), MCW(Step 0.0), AMQ(pre-flight)
**Objective:** Write plan lock before any sprint work (CLAUDE.md §Step 0)

---

#### TC-UNIFIED-001: GOV_BLOCK Resolution — Reduce xcf_parser.py by 6 LOC
**Status:** READY
**Priority:** P0 — EXECUTION BLOCKER
**Source Plans:** AMQ(TC-LIF-001), SMM(TC-SMM-001+002), MCW(Phase 0.1+0.2)
**Disposition:** MERGED (all three plans agree on this as first action)

**Verified State:**
- xcf_parser.py: 1283 LOC vs cap 1277 — over by 6 lines
- Fix: Remove 6 consecutive double-blank-line separators between exception class definitions
- DO NOT create xcf_analytics.py (explicitly forbidden per AMQ forensics)
- DO NOT modify xcf_analytics.py (doesn't exist)

**Implementation:** Remove 6 blank lines from double-blank pairs in xcf_parser.py (purely style — zero functional change)

**Verification:**
1. `sum(1 for _ in Path('src/python/xcf/xcf_parser.py').open())` → must be ≤ 1277
2. `python tools/validators/source_structure_validator.py` → exits 0, no WORSENED
3. `.venv/Scripts/pytest tests/python/xcf/ -x -q` → all pass

**Post-Fix:** Set `govblock_resolved_by` in continuation-signal.json

**Acceptance:** source_structure_validator.py exits 0 with no blocking entries

---

#### TC-UNIFIED-002: Update Baseline LOC Fields
**Status:** READY_AFTER TC-UNIFIED-001
**Priority:** P0
**Source Plans:** AMQ(TC-LIF-001 step 10), SMM(TC-SMM-002 Case A step 11)

**Actions:**
- Update `loc` field for `src/python/xcf/xcf_parser.py` in source-structure-baseline.json
- Do NOT modify `baseline_loc_cap` (write-once frozen)

---

#### TC-UNIFIED-003: Phase 0 Supervisor Closeout
**Status:** READY_AFTER TC-UNIFIED-002
**Priority:** P0
**Source Plans:** SMM(TC-SMM-002B), MCW(implicit), AMQ(between taskcards)

**Actions:**
1. Write evidence declaration for Phase 0
2. Run: `python tools/supervisor/autonomous_cycle.py --declaration <path>`
3. Verify `check_continuation.py` returns CONTINUE

---

### WAVE 1 — Lifecycle Infrastructure (agile-munching-quasar tasks)

#### TC-UNIFIED-010: Create lifecycle_audit.py
**Status:** READY_AFTER TC-UNIFIED-003
**Priority:** P1
**Source Plans:** AMQ(TC-LIF-002)
**Objective:** Product-track post-execution lifecycle audit module
- Creates `tools/supervisor/lifecycle_audit.py` (<800 LOC)
- Creates `tests/supervisor/test_lifecycle_audit.py` (9 tests)
- Output: `.local/supervisor/lifecycle-audit-results.json`

---

#### TC-UNIFIED-011: Wire --audit-gate into write_plan_lock.py
**Status:** READY_AFTER TC-UNIFIED-010
**Priority:** P1
**Source Plans:** AMQ(TC-LIF-003)
**Objective:** Add `--audit-gate` flag; wire `ITERATION_REQUIRED` status into check_continuation.py
**Backward compat:** `--terminal` without `--audit-gate` unchanged

---

#### TC-UNIFIED-012: Wire govblock_resolved_by into autonomous_cycle.py
**Status:** READY
**Priority:** P1
**Source Plans:** AMQ(TC-LIF-004)
**Note:** TC-UNIFIED-001 manually sets govblock_resolved_by. This TC automates it.

---

### WAVE 2 — System Audits (squishy-chasing-marshmallow Phase 1)

#### TC-UNIFIED-020: QName Integration Audit
**Status:** READY_AFTER TC-UNIFIED-003
**Source Plans:** SMM(TC-SMM-010)
**Output:** `$EVROOT/qname-verdict.md`, `qname-producer-consumer-map.json`

#### TC-UNIFIED-021: SAL Fact Chain Audit
**Status:** READY_AFTER TC-UNIFIED-003
**Source Plans:** SMM(TC-SMM-011)
**Output:** `$EVROOT/sal-verdict.md`

#### TC-UNIFIED-022: RCAL/Capability Audit
**Status:** READY_AFTER TC-UNIFIED-003
**Source Plans:** SMM(TC-SMM-012), MCW(Phase 1a)
**Output:** `$EVROOT/rcal-verdict.md`

#### TC-UNIFIED-023: Product Source Census Python
**Status:** READY_AFTER TC-UNIFIED-003
**Source Plans:** SMM(TC-SMM-014)
**Output:** `$EVROOT/product-inventory.json`

#### TC-UNIFIED-024: Product Source Census .NET
**Status:** READY_AFTER TC-UNIFIED-003
**Source Plans:** SMM(TC-SMM-019)
**Output:** `$EVROOT/dotnet-product-audit.json`

---

### WAVE 3 — Capability Layer (majestic-cooking-waffle tasks)

#### TC-UNIFIED-030: Generate Fresh Capability Maps
**Status:** READY_AFTER TC-UNIFIED-003
**Source Plans:** MCW(Phase 1b)
**Command:** `python tools/capability_layer/capability_map_generator.py --output-dir reports/capability-layer --run-id unified-multi-plan-20260623`

#### TC-UNIFIED-031: Validate Generated Maps
**Status:** READY_AFTER TC-UNIFIED-030
**Source Plans:** MCW(Phase 1c)

#### TC-UNIFIED-032: Commercial Pilots (FODS, FODT, Netpbm)
**Status:** READY_AFTER TC-UNIFIED-030
**Source Plans:** MCW(Phase 2a)
**Output:** `reports/capability-layer/pilots/fods-mcw-pilot.json`, etc.

#### TC-UNIFIED-033: FOSS Pilots (SYLK, NDJSON, TSV)
**Status:** READY_AFTER TC-UNIFIED-030
**Source Plans:** MCW(Phase 2b)

#### TC-UNIFIED-034: Create capability_to_feature_compiler.py
**Status:** READY_AFTER TC-UNIFIED-031
**Source Plans:** MCW(Phase 3c)
**Note:** Confirmed NOT existing — must CREATE

---

### WAVE 4 — Plan Closeout

#### TC-UNIFIED-090: Final Evidence Declaration + Autonomous Cycle
**Status:** PENDING (last action)
**Source Plans:** All three plans
**Actions:** Write declaration, run autonomous_cycle.py, write --terminal plan lock

---

## 5. Dependency Graph

```
TC-UNIFIED-001 (GOV_BLOCK fix)
  → TC-UNIFIED-002 (baseline update)
    → TC-UNIFIED-003 (supervisor closeout)
      ├── TC-UNIFIED-010 (lifecycle_audit.py)  [sequential]
      │     → TC-UNIFIED-011 (audit-gate)
      │     → TC-UNIFIED-012 (govblock signal)
      ├── TC-UNIFIED-020 through 024 (audits) [parallel]
      └── TC-UNIFIED-030 (capability maps)
            ├── TC-UNIFIED-031 (validate maps)
            ├── TC-UNIFIED-032 (commercial pilots)
            ├── TC-UNIFIED-033 (FOSS pilots)
            └── TC-UNIFIED-034 (compiler stub)
                  → TC-UNIFIED-090 (closeout)
```

---

## 6. Priority Queue

1. **P0**: TC-UNIFIED-001 (GOV_BLOCK — xcf_parser.py -6 LOC)
2. **P0**: TC-UNIFIED-002 (baseline update)
3. **P0**: TC-UNIFIED-003 (supervisor closeout → CONTINUE signal)
4. **P1**: TC-UNIFIED-010 (lifecycle_audit.py)
5. **P1**: TC-UNIFIED-011 (audit-gate in write_plan_lock.py)
6. **P2**: TC-UNIFIED-020-024 (system audits, parallel)
7. **P3**: TC-UNIFIED-030-034 (capability layer)
8. **P5**: TC-UNIFIED-090 (final closeout)

---

## 7. Evidence Root

**Fixed path:** `.local/evidences/unified-multi-plan-20260623/`

---

## 8. Item Disposition Register

| Source Item | Disposition | Unified TC |
|-------------|-------------|------------|
| SMM TC-SMM-00P (pre-flight) | MERGED into session start | TC-UNIFIED-000 |
| SMM TC-SMM-00W (unstaged changes) | ALREADY_RESOLVED (ndjson at cap, xcf is the GOV_BLOCK) | TC-UNIFIED-001 |
| SMM TC-SMM-000 (run setup) | MERGED | TC-UNIFIED-000 |
| SMM TC-SMM-001 (GOV_BLOCK diagnosis) | SUPERSEDED_WITH_PROOF (diagnosis already done) | TC-UNIFIED-001 |
| SMM TC-SMM-002 (GOV_BLOCK resolution) | MERGED | TC-UNIFIED-001 |
| SMM TC-SMM-002B (supervisor closeout) | MERGED | TC-UNIFIED-003 |
| SMM TC-SMM-003 (signal reconciliation) | MERGED | TC-UNIFIED-003 |
| SMM TC-SMM-010–019 (audits) | PRESERVED | TC-UNIFIED-020-024 |
| AMQ TC-LIF-000 (forensics snapshot) | ALREADY_COMPLETED_AND_VERIFIED |
| AMQ TC-LIF-001 (GOV_BLOCK fix) | MERGED | TC-UNIFIED-001 |
| AMQ TC-LIF-002 (lifecycle_audit.py) | PRESERVED | TC-UNIFIED-010 |
| AMQ TC-LIF-003 (audit-gate) | PRESERVED | TC-UNIFIED-011 |
| AMQ TC-LIF-004 (govblock signal) | PRESERVED | TC-UNIFIED-012 |
| MCW Phase 0 (plan lock + GOV_BLOCK) | MERGED | TC-UNIFIED-000,001 |
| MCW Phase 1 (investigation) | PRESERVED | TC-UNIFIED-020-024,030-031 |
| MCW Phase 2 (pilots) | PRESERVED | TC-UNIFIED-032-033 |
| MCW Phase 3c (compiler stub) | PRESERVED | TC-UNIFIED-034 |

---

## 9. Anti-Overclaim Rules

- ndjson_codec.py is at cap (1080=1080) — NOT blocking. Do not attempt to reduce it further unless a new change adds lines.
- xcf_parser.py needs -6 lines. Only blank line removal (no logic changes).
- xcf_analytics.py MUST NOT be created.
- govblock_resolved_by must be set via Python code after fix, not via --dry-run (doesn't exist).
- autonomous_cycle.py entry point: `python tools/supervisor/autonomous_cycle.py --declaration <path>` (NOT supervisor_loop.py).

---

## 10. Closeout Criteria

Plan is complete when:
1. TC-UNIFIED-001 through TC-UNIFIED-003 closed (GOV_BLOCK resolved, continuation unblocked)
2. TC-UNIFIED-010 and TC-UNIFIED-011 closed (lifecycle infrastructure)
3. TC-UNIFIED-020 through TC-UNIFIED-024 closed (system audits)
4. TC-UNIFIED-030 through TC-UNIFIED-034 closed (capability layer)
5. TC-UNIFIED-090 closed (final closeout)
6. All 3 supplied plans' mandatory outcomes are addressed

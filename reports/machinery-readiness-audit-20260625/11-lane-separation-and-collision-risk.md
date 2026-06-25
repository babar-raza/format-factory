# Lane H (continued): Lane Separation and Collision Risk
# Sprint: ff-machinery-readiness-audit-20260625

## Lane Boundary Map

The spec-to-feature-radical-correction-plan.md defines a strict wave sequence:

```
Wave 0:  Lane 14 (supervisor hardening), Lane 15 (durable learning)
Wave 1A: Lane 1 (SAL pipeline), Lane 2 (QName registry)
Wave 1B: Lane 3 (capability-to-feature compiler), Lane 4 (skill contracts)
Wave 2:  Lane 5 (governance validator hardening)
Wave 3:  Lane 6 (integration/dogfood proof)
Wave 4:  Lane 7 (FODS deepening), Lane 8 (FODT deepening)
Wave 5:  Lanes 9-11 (CSV/NDJSON/TSV deepening)
Wave 6:  Lane 12 (Netpbm/PBM/PGM/PPM deepening)
Wave 7:  Lane 13 (remaining formats)
```

### Lane Categories

| Category | Lanes | Purpose | Current Status |
|---|---|---|---|
| Machinery | 1, 2, 3, 4, 5, 6 | Infrastructure repair | WAVE 1A IN PROGRESS (minimal) |
| Lifecycle | 14, 15 | Supervisor/learning | PARTIAL |
| Product | 7, 8, 9, 10, 11, 12, 13 | Format deepening | UNAUTHORIZED (machinery not complete) |

---

## Shared-File Risk Map

### Files Modified by Both Machinery and Product Lanes

The following files are modified in BOTH machinery and product work, creating contamination risk:

| Shared File | Machinery Lanes | Product Lanes | Collision Type |
|---|---|---|---|
| `registry/source-structure-baseline.json` | All (baseline cap updates) | 7-13 (new format LOC) | Concurrent write, wrong cap values |
| `reports/capability-layer/gap-ledger.json` | 1, 3 (SAL gaps, compiler gaps) | 7-13 (format gap closures) | Concurrent writes, duplicate/conflicting gap IDs |
| `.supervisor/skill-registry.yaml` | 4 (skill contracts) | 7-13 (skill invocations) | Registration conflicts |
| `tools/supervisor/governance_validators.py` | 5, 14 | — | Cap violations from product-lane-triggered edits |
| `tools/supervisor/autonomous_cycle.py` | 14, 15 | — | Accidental breakage from product PRs |
| `registry/product-deepening-ledger.yaml` | — | 7-13 | Concurrent product status updates |
| `docs/architecture.md` | 14, 15 | 7-13 | Both update architecture diagrams |
| `.supervisor/knowledge/contracts/python-domain-model.yaml` | 4 (contract spec) | 7-13 (contract enforcement) | Contract mismatch during product work |

### High-Collision Zones

**Zone HC-001: gap-ledger.json**
- Lane 1 (SAL) writes new gap entries for CHAIN_BROKEN formats
- Lane 3 (compiler) writes capability-to-gap cross-references
- Lanes 7-13 (product) CLOSE gaps with closure evidence
- **Risk:** If product lanes run while machinery lanes 1+3 are writing gaps, closures may target stale gap IDs or ghost gaps may persist in the ledger

**Zone HC-002: source-structure-baseline.json**
- Lane 5 (governance validator hardening) may update caps for validator tools
- Lanes 7-13 (product) must not raise caps — only update `loc` field for healed files
- **Risk:** Product worker sets `baseline_loc_cap` when adding new format source files; machinery validator sees wrong cap; GOV_BLOCK fires incorrectly

**Zone HC-003: autonomous_cycle.py**
- Lane 14 wires SUP-GAP-001 (lane ownership check), SUP-GAP-003 (overclaim detector)
- Product lanes do NOT touch autonomous_cycle.py
- **Risk:** If a product lane introduces a declaration syntax that autonomous_cycle.py's upgraded validators reject, the next machinery lane cannot close cleanly

---

## Contamination Vectors

### CV-001: Product Lane Proceeds Without Machinery Prerequisites

**Evidence:** Current `check_continuation.py` has NO wave gate validation.
The 19-state machine returns YES based on:
- `hard_stops_detected == []`
- `rework_items == []`
- `iteration < max_iterations`

It does NOT check:
- Whether Lane 1 (SAL) has active fact extraction for the target format
- Whether Lane 3 (compiler) can generate a gap→taskcard skeleton for the sprint
- Whether Lane 5 (governance validators) has FAIL mode for the target format's V43

**Impact:** Product deepening sprint runs for (e.g.) CSV while:
- SAL has no live fact extraction (CHAIN_BROKEN_AT_SAL)
- _EXPANSION_GOALS drives task selection (not gap-ledger)
- V43 is WARN not FAIL for CSV (not enforced)
- No gap_ledger_ref in work items → TC-GUARD-001 rework

The product sprint produces non-spec-backed code that must be reworked.

### CV-002: Analytics Masquerade Contaminates Domain Model Layer

**Evidence:** gnumeric/workbook_document.py is analytics (not a domain model) but is named as a model file.
If a product lane agent reads directory structure, sees `workbook_document.py`, assumes it's the domain model, and adds behavioral methods to it, that file is now a GOV_BLOCK risk (LOC exceeds cap after additions).

**Current formats at risk:**
- gnumeric/workbook_document.py (analytics masquerade, incorrect name)
- toml/config_document.py (analytics masquerade)
- These will cause confusion for any product lane working on Gnumeric or TOML

### CV-003: Skill Invocation During Skill-Registry Modification

**Evidence:** Lane 4 (skill contracts) is the current machinery wave.
If a product lane agent invokes `/add-python-api` while Lane 4 is mid-modification of the skill's contract file, the invoked skill may execute with stale or inconsistent contract requirements.

The skill registry is fail-closed (`active_fail_closed: true`) but the contract YAML can be in a partially-written state during Lane 4 editing.

### CV-004: Plan Lock File Collision

**Evidence:** Plan locks use session-keyed paths in `.local/supervisor/plan-locks/`.
If machinery sprint and product sprint run in separate chat sessions simultaneously:
- Both may write `IN_PROGRESS` plan locks
- `generate_next_work_items` may see PLAN_LOCKED state and return empty queue
- `check_continuation.py` may return `ACTIVE_PLAN_INCOMPLETE` (false positive)

This was observed 2026-06-25 with foreign session locks causing ACTIVE_PLAN_INCOMPLETE.
**Fix in place:** `cleanup_stale_locks()` resolves IN_PROGRESS locks from foreign sessions via SUPERSEDED status.

### CV-005: QName Registry Race — Two Formats Updated Simultaneously

**Evidence:** `shared/qname-registry/` contains 20 YAML files, one per format.
If two product lane agents update (e.g.) `csv.yaml` and `ndjson.yaml` simultaneously,
and both run V53 validation that reads all registry files, a partial-write YAML may
cause V53 to fail with a parse error rather than a compliance error.

**Probability:** LOW (single-threaded session execution), but POSSIBLE in headless mode.

---

## Lane Collision Risk Matrix

| Risk | Severity | Probability | Enforced by Code? | Current Mitigation |
|---|---|---|---|---|
| CV-001: Product without SAL prerequisites | CRITICAL | HIGH | NO | Prompt-only |
| CV-002: Analytics masquerade model confusion | HIGH | MEDIUM | NO | Manual documentation only |
| CV-003: Skill contract mid-modification | MEDIUM | LOW | NO | Fail-closed registry (partial) |
| CV-004: Plan lock file collision | MEDIUM | MEDIUM | PARTIAL | cleanup_stale_locks() |
| CV-005: QName registry YAML race | LOW | LOW | NO | Single-threaded normal ops |
| HC-001: gap-ledger concurrent write | HIGH | MEDIUM | NO | None |
| HC-002: baseline.json cap collision | HIGH | LOW | NO | Write-once policy (prompt-only) |
| HC-003: autonomous_cycle.py breakage | MEDIUM | LOW | NO | Code review (manual) |

**Total enforced risks: 1/8 (12.5%)**
**Total prompt-only: 7/8 (87.5%)**

---

## Required Guardrails

### G-001: Wave Gate Validator (addresses CV-001)

A new autonomous_cycle.py pre-step BEFORE Step 1 (declaration validation):

```python
def wave_gate_check(target_lane: int) -> tuple[bool, str]:
    """Check that prerequisite waves are complete before lane N runs."""
    if target_lane >= 7:  # Product lanes
        # Require: Lane 1 (SAL) has active extraction OR explicit CHAIN_BROKEN acknowledgment
        # Require: Lane 3 (compiler) has gap→workitem pipeline working for target format
        # Require: Lane 5 (governance) V43 in FAIL mode for target format
        pass
    return True, "OK"
```

**Implementation:** SUPERVISOR-LANES-001 (cross-reference to SUP-GAP-001)
**Severity if not built:** Blocker — product sprints will continue producing non-spec-backed code

### G-002: Analytics Masquerade Detector (addresses CV-002)

A new governance validator (V54) that scans `src/python/*/` for files with:
- Name containing "document" or "model" in the filename
- File body that has NO `spec_qname` class attribute
- File body that has >10 arithmetic functions

Files matching this pattern should be flagged as analytics masquerades.

**Required action:** V54 added as WARN (path to FAIL after 60-day notice period).

### G-003: Gap Ledger Write Coordinator (addresses HC-001)

Shared gap-ledger.json file is currently write-directly (no coordinator).
Recommendation: add a gap-ledger write lock using a `.local/supervisor/gap-ledger.lock` file.
Any script that writes to gap-ledger.json must acquire this lock.

**Severity:** HIGH — race writes corrupt the ledger

### G-004: Stale Plan Lock Auto-Cleanup (addresses CV-004, partially implemented)

`cleanup_stale_locks()` in write_plan_lock.py is available but NOT called automatically.
It requires manual invocation: `python tools/supervisor/write_plan_lock.py --cleanup-stale-locks`.

**Required:** Wire `cleanup_stale_locks()` into `check_continuation.py` Step 0 (pre-check).
This eliminates false ACTIVE_PLAN_INCOMPLETE stops from foreign session locks.

---

## Required Supervisor Changes

### SC-001: Wave Gate Pre-Check in autonomous_cycle.py

```
New Step 0c (between plan-lock check and SAL refresh):
  wave_gate_result = check_wave_gate(declaration_lane)
  if wave_gate_result.blocked:
    write_continuation_signal(NO_BROKEN_BASELINE, wave_gate_result.reason)
    sys.exit(3)
```

**Files changed:** `tools/supervisor/autonomous_cycle.py` (add step 0c), `tools/supervisor/wave_gate_check.py` (new module)
**Taskcard:** SUPERVISOR-LANES-001

### SC-002: Automatic Stale Lock Cleanup

```
New Step 0b-cleanup (in check_continuation.py, before plan lock check):
  cleanup_stale_locks()
```

**Files changed:** `tools/supervisor/check_continuation.py` (one import + one call)
**Taskcard:** Extend SUPERVISOR-CONTINUATION-001

### SC-003: MULTI_LANE Declaration Support (DONE)

**Evidence from MEMORY.md (2026-06-25):** TC-S55-003 FIXED.
When `declared_lane == "MULTI_LANE"`, single-lane constraint check is skipped.
Lanes_touched reported as advisory evidence.
**Status: RESOLVED**

### SC-004: Overclaim Detector Wiring (NOT DONE)

10-pattern overclaim detector exists in code but is NEVER called.
Must be wired into Step 2d of autonomous_cycle.py.
See SUP-GAP-003 in artifact 10-autonomous-supervisor-audit.md.

---

## Lane Collision Verdict

**Current lane separation enforced by CODE: MINIMAL**

The only mechanical lane enforcement is:
1. Plan lock files (block concurrent plan execution in same session)
2. TC-GUARD-001 (BLOCK mode for items without gap_ledger_ref/spec_fact_refs)
3. V43 WARN mode (partial: not FAIL for implementing-status formats)

Everything else — wave ordering, SAL prerequisites, feature compiler availability,
analytics masquerade detection, gap-ledger write coordination — is PROMPT-ONLY.

An agent following the prompt correctly produces correct lane ordering.
An agent ignoring the prompt (or working from stale context) will contaminate lanes.

**Risk summary:** HIGH collision risk in Wave 1B→2→product pipeline.
**Required fix:** SC-001 (wave gate), G-003 (gap-ledger lock), V54 (masquerade detector).

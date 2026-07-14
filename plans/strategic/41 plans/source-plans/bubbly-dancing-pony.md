# Specialist Machinery and Output Assurance Sprint — bubbly-dancing-pony
# MICRO-TASKCARDIZED EXECUTION-READY VERSION
# Enhanced: 2026-07-10 | Plan type: machinery_hardening
# Authority: This file is the SOLE execution-control authority for this plan.

---

## PLAN AUTHORITY BLOCK

```yaml
authoritative_plan: plans/.claude/bubbly-dancing-pony.md
in_repo_mirror: plans/.claude/bubbly-dancing-pony.md
authority_source: plan_mode_loaded_current_conversation
duplicate_active_plans_found: false
competing_execution_plans: none
plan_status: READY_FOR_EXECUTION
last_enhanced: 2026-07-10
```

---

## PREFLIGHT RECORDS

```yaml
repository_path: c:/Users/prora/OneDrive/Documents/GitHub/format-factory
branch: main
active_plan_path: C:/Users/prora/.claude/plans/bubbly-dancing-pony.md
plan_title: Specialist Machinery and Output Assurance Sprint — bubbly-dancing-pony
plan_format: markdown_hierarchical_taskcards
plan_authority_source: plan_mode_system_reminder
major_section_count: 17
existing_taskcard_sections_before_enhancement: 11 (prose-only, no children)
existing_taskcard_format_before: prose steps only
existing_lanes: repair / verify / pilot / close
existing_state_vocabulary: OPEN (all 11 original)
existing_validation_model: manual inspection + pytest commands
existing_evidence_model: evidence paths + SHA-256
duplicate_plan_risk: LOW — one plan file, no v2 or replacement variants
```

---

## SECTION INVENTORY

| Section ID | Title | Type | Actionable Items | Enhancement |
|---|---|---|---|---|
| S01 | Production Diagnosis | analysis | 0 | preserve |
| S02 | Structural Weaknesses W1-W5 | analysis | 5 root causes | add REQ-IDs, apply corrections |
| S03 | What to Preserve | constraint | 0 | preserve + add CORRECTION-002 note |
| S04 | What Must Change | decision | 6 items | preserve + note corrections |
| S05 | Design Principles | design | 4 | preserve |
| S06 | Taskcard Index | planning | 11 | expand to full hierarchy |
| S07 | TC-MA2-PIPE-001 | impl | 5 steps | decompose to 5 children + micro-steps |
| S08 | TC-MA2-SIGNAL-001 | impl | 5 steps | decompose + CORRECT target file |
| S09 | TC-MA2-SKIP-001 | impl | 4 steps | decompose to 4 children + micro-steps |
| S10 | TC-MA2-VAL-001 | impl | 3 steps | decompose to 3 children + micro-steps |
| S11 | TC-MA2-LOCK-001 | impl | 3 steps | decompose + CORRECT existing post-write check |
| S12 | TC-MA2-VERIFY-001 | verify | 9 checks | decompose to 8 children + micro-steps |
| S13 | TC-MA2-PILOT-001 to 004 | pilot | 4x steps | decompose each |
| S14 | TC-MA2-FINAL-001 | closeout | 8 counters | decompose to 4 children |
| S15 | Critical Files Table | reference | 7 rows | preserve |
| S16 | Execution Sequence | handoff | sequential list | replace with DAG |
| S17 | Honest Assessment | risk | 3 paragraphs | preserve + expand deferred table |

---

## FACTUAL CORRECTIONS (applied throughout this plan)

### CORRECTION-001 — TC-MA2-SIGNAL-001 target file is wrong in original plan
- **Original plan claimed**: `continuation_state.py` `save_active_continuation()` writes `continuation-signal.json`
- **Confirmed from code**: `continuation_state.py` line 79 writes to `ACTIVE_CONTINUATION_PATH = ".local/supervisor/active-continuation.json"` — a different file
- **Actual write site**: `autonomous_cycle.py` line 2207: `atomic_write_json(signal_path, signal)` where `signal_path = signal_dir / "continuation-signal.json"`
- **Fix applied**: TC-MA2-SIGNAL-001 and all children target `autonomous_cycle.py` signal construction section, NOT `continuation_state.py`

### CORRECTION-002 — TC-MA2-LOCK-001 post-write check already exists
- **Original plan claimed**: Post-write consistency check needs to be added
- **Confirmed from code**: `write_plan_lock.py` lines 474-485 already implement TC-AMD-CONV-002 post-write check
- **Fix applied**: TC-MA2-LOCK-001 scope narrowed to the grouped-write pattern only (write both .tmp before renaming either)

### CORRECTION-003 — next-work-items.json has single root key `items`
- **Original plan claimed**: Root has both `items` and `gap_sourced_items` keys
- **Confirmed from actual file**: Root key is `items` only
- **Fix applied**: Replacement code uses only `_nwi.get("items", [])` — no `gap_sourced_items` merge

---

## REQUIREMENTS INVENTORY

| REQ-ID | Domain | Description |
|---|---|---|
| REQ-PIPE-001 | Pipeline | Sprint prompt must source tasks exclusively from next-work-items.json |
| REQ-PIPE-002 | Pipeline | Fixture fallback must be unreachable when next-work-items.json exists |
| REQ-PIPE-003 | Pipeline | Empty NWI must surface "NO GOVERNED PRODUCT WORK" explicitly |
| REQ-SIGNAL-001 | Signal | Signal field coherence must be enforced at the write site in autonomous_cycle.py |
| REQ-SIGNAL-002 | Signal | Read-time coherence diagnostic must emit on incoherent disk state |
| REQ-SIGNAL-003 | Signal | Current incoherent disk signal must be corrected |
| REQ-SKIP-001 | Closeout | Closeout step failures must produce machine-readable skip records |
| REQ-SKIP-002 | Closeout | Outstanding skips must surface in session-resume.md |
| REQ-SKIP-003 | Closeout | copy_cycle_summaries failure must not block cycle exit 0 |
| REQ-VAL-001 | Governance | Validator count must be enforced at runtime against ran_count |
| REQ-VAL-002 | Governance | Import failures > tolerance must produce a FAIL result |
| REQ-LOCK-001 | Lock | Both lock files must have their .tmp written before either is renamed |
| REQ-LOCK-002 | Lock | Partial .tmp write failure must leave both final files unchanged |
| REQ-VERIFY-001 | End-to-end | All repair changes verified by running test suite |
| REQ-VERIFY-002 | End-to-end | next-sprint.md item_ids must match next-work-items.json |
| REQ-PILOT-001 | Pilot | Both outputs must agree on work selection |
| REQ-PILOT-002 | Pilot | Signal write-time correction must fire on incoherent input |
| REQ-PILOT-003 | Pilot | Closeout failure must produce skip record visible next session |
| REQ-PILOT-004 | Pilot | Second full run must produce zero material changes |

---

## Production Diagnosis

### What is actually breaking consistency across reruns

The autonomous loop produces two independent outputs after each sprint:

**Output A — governed work items** (`next-work-items.json`):
Written by `autonomous_cycle.py` Step 4a-compiler using `capability_feature_compiler.py`
over the live gap ledger. These items have spec_facts, gap_refs, verification commands.
Items like `WI-GAP-DIF-FOSS-DIF_BOOLEAN_-001` sourced from `reports/capability-layer/gap-ledger.json`.
`check_continuation.py` emits this path as `next_work_items_path` in its verdict.

**Output B — the sprint prompt** (`next-sprint.md`):
Written by `generate_supervisor_packet.py` using `selected-product-gaps.json`. This file
is currently empty (`[]`). When empty, the code falls back (lines 651-703) to the most
recent `*.supervisor/fixtures/*-poc-gap-extraction.yaml` file. The fixture file produces
its own gap task list from `r86_targets` or a cascade scan of `capability_gaps`,
`dogfood_gaps`, and `documentation_gaps`.

CLAUDE.md instructs the agent to read **both**: structured items from `next_work_items_path`
and prose context from `next-sprint.md`. When these describe different work — governed DIF
gap items in A, fixture-based R86 targets in B — the agent must reconcile two competing
task authorities at LLM-judgment time. Each rerun may resolve this differently.

This is the root consistency failure. It is not a configuration error or a minor bug.
It is two independent pipelines writing to two outputs that are both authoritative inputs
to the same consumer (the agent), with no reconciliation between them.

### Why this is not caught by the existing validation machinery

`sprint_executor_validate.py` validates declarations, not inputs. `check_continuation.py`
validates signal state, not whether the task sources agree. The governance validators
check product source code structure, not sprint task selection. Nothing in the pipeline
checks whether Output A and Output B describe the same work before the agent reads them.

The second-order consequence: when the agent implements work from the fixture list that
is not in the governed gap ledger, the supervisor grades it as `REWORK_REQUIRED` or
`ACCEPTED_WITH_WARNINGS` because the gap reference is missing. The agent then interprets
this as a quality issue in its implementation, not as a task-selection divergence.
The real cause is invisible.

### Additional structural weaknesses confirmed by code inspection

**W1 — Signal write does not enforce field coherence.**
`autonomous_cycle.py` constructs the signal dict (around lines 2145-2206) and writes it
via `atomic_write_json(signal_path, signal)` at line 2207. The construction logic can
produce `stop_reason: "critical_rework_blocks_continuation"` with `rework_items: []`
and `autonomous_continue: true` simultaneously (confirmed from disk state dated 2026-07-04).
`check_continuation.py` resolves this at read time via `_gates_override = True`
(lines 422-423) when `approval-gates.md` says YES. No diagnostic is emitted at the
override point. The signal stays incoherent on disk indefinitely.

> **CORRECTION-001:** `continuation_state.py`'s `save_active_continuation()` writes to
> `active-continuation.json` (ACTIVE_CONTINUATION_PATH). The signal coherence fix must
> target `autonomous_cycle.py`'s signal construction section, NOT `continuation_state.py`.

**W2 — Silent fallback chain makes fixture source invisible.**
The fallback at `generate_supervisor_packet.py` lines 651-703 fires without logging
which fixture was used or that a fallback occurred. The sprint prompt appears generated
from governed sources because the task descriptions use the same language ("Product
deepening: GAP-* — ..."). There is no way to tell from reading `next-sprint.md` whether
it was sourced from governed gaps or from a fixture file last modified months ago.

**W3 — Closeout step failures produce no machine-readable record.**
`autonomous_cycle.py` wraps Steps 4b, 6, and several sub-steps in `try/except` with
`print(f"WARNING: ... failed: {_ce}")`. These warnings go to stdout during cycle execution
and are lost between sessions. The next sprint has no knowledge of what was skipped.

The `copy_cycle_summaries` function at Step 6 is one of these wrapped calls. If it fails,
the run-specific `next-work-items.json` (written to `review_dir/`) is never copied to
`.local/supervisor/next-work-items.json`. The next sprint reads stale data.

**W4 — Validator count drift is silent at runtime.**
`governance_validator_runner.py` returns `{"expected_count": 167, "ran_count": N}` (lines
813, 816) but **never compares them**. Import failures collected in `_skipped_validators`
(e.g. lines 384-385) do not affect the sprint verdict. MEMORY.md still says 165.
Three-artifact drift (code, test assertion, MEMORY.md) each track independently.

**W5 — Plan lock writes are not grouped.**
`write_plan_lock.py` writes shared lock tmp+rename (lines 434-437) then keyed lock
tmp+rename (lines 467-469) sequentially. If the second rename fails, shared lock has
the new status but the keyed lock is stale.

> **CORRECTION-002:** A post-write consistency check already exists at lines 474-485
> (TC-AMD-CONV-002) and must be preserved. TC-MA2-LOCK-001 scope is the grouped-write
> pattern only: write both `.tmp` files before renaming either.

---

## What to Preserve

The evidence-declaration pipeline, multi-phase validation repair, grade-then-signal
sequence, oracle depth scoring, plan lock lifecycle states (TERMINAL_CLOSED/SUPERSEDED),
CCI-MVP session isolation, Supreme Directive + best-effort closeout policy, and the
governance validator modular architecture are all sound and should not be changed.

The current `next-work-items.json` format and its producer (`capability_feature_compiler`)
are correct and should become the single authority for task selection.

`write_plan_lock.py` lines 474-485 (TC-AMD-CONV-002 post-write check) are already
correct — do not modify or remove them.

---

## What Must Change

**Primary change (solves the root consistency failure):**
`generate_supervisor_packet.py` must read task content from `next-work-items.json`
rather than from `selected-product-gaps.json` + fixture fallback. The sprint prompt
becomes a view over governed data. The fixture fallback is removed.

**Secondary changes (close the silent-failure and drift gaps):**
1. Signal writes in `autonomous_cycle.py` must validate field coherence before writing (not `continuation_state.py`).
2. Closeout skips must produce machine-readable records (not only stdout warnings).
3. Validator count must be compared against `ran_count` at runtime.
4. Plan lock writes must group both `.tmp` file writes before renaming either.

---

## Design Principles for the Fixes

**Principle 1 — Single authority per output.**
`next-sprint.md` and `next-work-items.json` must agree because they are both read by
the same consumer. The fix makes `next-sprint.md` a rendering of `next-work-items.json`.

**Principle 2 — Invariants enforced at write, not resolved at read.**
Incoherent state that is silently resolved by downstream readers should be prevented at
write time. The reader should not need to know about recovery strategies.

**Principle 3 — Skipped infrastructure must be visible across sessions.**
"Best-effort" means the sprint continues; it does not mean the skip is forgotten. Skip
records must survive across sessions.

**Principle 4 — Count-based invariants must be self-enforcing.**
Any count assertion that can drift silently must be enforced at the point of consequence
(runtime), not only in tests.

---

## Taskcard Index

| TC-ID | Title | Depends On | Type | Status |
|---|---|---|---|---|
| TC-MA2-PIPE-001 | Make sprint prompt a view over next-work-items.json | — | PARENT | READY |
| TC-MA2-PIPE-001-01 | Inspect and record exact replacement site | — | CHILD | TODO |
| TC-MA2-PIPE-001-02 | Write test fixtures for NWI-sourced prompt | — | CHILD | TODO |
| TC-MA2-PIPE-001-03 | Replace lines 625-703 with NWI reader | 01 | CHILD | TODO |
| TC-MA2-PIPE-001-04 | Remove gap_fixtures dead code | 03 | CHILD | TODO |
| TC-MA2-PIPE-001-05 | Run tests and inspect next-sprint.md output | 03,04 | CHILD | TODO |
| TC-MA2-SIGNAL-001 | Enforce signal field coherence at write time | — | PARENT | READY |
| TC-MA2-SIGNAL-001-01 | Investigate signal construction site in autonomous_cycle.py | — | CHILD | TODO |
| TC-MA2-SIGNAL-001-02 | Add validate_signal_coherence() function | 01 | CHILD | TODO |
| TC-MA2-SIGNAL-001-03 | Wire coherence check into signal write path | 02 | CHILD | TODO |
| TC-MA2-SIGNAL-001-04 | Add read-time diagnostic in check_continuation.py | 02 | CHILD | TODO |
| TC-MA2-SIGNAL-001-05 | Repair current incoherent disk state | 03 | CHILD | TODO |
| TC-MA2-SKIP-001 | Machine-readable skip records for closeout failures | — | PARENT | READY |
| TC-MA2-SKIP-001-01 | Create closeout_skip_ledger.py module | — | CHILD | TODO |
| TC-MA2-SKIP-001-02 | Audit all try/except blocks in autonomous_cycle.py closeout | — | CHILD | TODO |
| TC-MA2-SKIP-001-03 | Wire skip ledger into priority closeout except blocks | 01,02 | CHILD | TODO |
| TC-MA2-SKIP-001-04 | Surface outstanding skips in session-resume.md | 01 | CHILD | TODO |
| TC-MA2-VAL-001 | Enforce validator count at runtime | — | PARENT | READY |
| TC-MA2-VAL-001-01 | Confirm expected_count=167 matches actual validator sum | — | CHILD | TODO |
| TC-MA2-VAL-001-02 | Add count enforcement after ran_count=len(results) | 01 | CHILD | TODO |
| TC-MA2-VAL-001-03 | Update MEMORY.md validator count (165→167) | 01 | CHILD | TODO |
| TC-MA2-LOCK-001 | Group plan lock writes (grouped tmp pattern) | — | PARENT | READY |
| TC-MA2-LOCK-001-01 | Read and document current write sequence lines 427-469 | — | CHILD | TODO |
| TC-MA2-LOCK-001-02 | Add _write_both_locks() helper function | 01 | CHILD | TODO |
| TC-MA2-LOCK-001-03 | Replace sequential writes with _write_both_locks() call | 02 | CHILD | TODO |
| TC-MA2-LOCK-001-04 | Add grouped-write tests | 03 | CHILD | TODO |
| TC-MA2-VERIFY-001 | End-to-end verification | PIPE,SIGNAL,SKIP,VAL,LOCK | PARENT | BLOCKED |
| TC-MA2-VERIFY-001-01 | Run pytest tests/supervisor/ and record results | — | CHILD | TODO |
| TC-MA2-VERIFY-001-02 | Inspect next-sprint.md task IDs vs next-work-items.json | — | CHILD | TODO |
| TC-MA2-VERIFY-001-03 | Check signal coherence on disk | — | CHILD | TODO |
| TC-MA2-VERIFY-001-04 | Run check_continuation.py and record verdict | — | CHILD | TODO |
| TC-MA2-VERIFY-001-05 | Run governance runner and check count output | — | CHILD | TODO |
| TC-MA2-VERIFY-001-06 | Read both lock files and compare status | — | CHILD | TODO |
| TC-MA2-VERIFY-001-07 | Check skip ledger exists and has content | — | CHILD | TODO |
| TC-MA2-VERIFY-001-08 | Write verify-ma2-results.yaml | all | CHILD | TODO |
| TC-MA2-PILOT-001 | Pilot: both outputs agree on work selection | VERIFY | PARENT | BLOCKED |
| TC-MA2-PILOT-001-01 | Run autonomous_cycle and record timestamps | — | CHILD | TODO |
| TC-MA2-PILOT-001-02 | Assert next-sprint.md item_ids in next-work-items.json | — | CHILD | TODO |
| TC-MA2-PILOT-001-03 | Assert no fixture path in next-sprint.md | — | CHILD | TODO |
| TC-MA2-PILOT-002 | Pilot: signal incoherence corrected at write | VERIFY | PARENT | BLOCKED |
| TC-MA2-PILOT-002-01 | Write incoherent signal to disk | — | CHILD | TODO |
| TC-MA2-PILOT-002-02 | Run signal write path with incoherent fields | — | CHILD | TODO |
| TC-MA2-PILOT-002-03 | Assert corrected signal on disk | — | CHILD | TODO |
| TC-MA2-PILOT-002-04 | Run check_continuation.py and assert CONTINUE | — | CHILD | TODO |
| TC-MA2-PILOT-003 | Pilot: closeout failure produces skip record | VERIFY | PARENT | BLOCKED |
| TC-MA2-PILOT-003-01 | Create test mocking copy_cycle_summaries failure | — | CHILD | TODO |
| TC-MA2-PILOT-003-02 | Assert cycle exits 0 after mock failure | — | CHILD | TODO |
| TC-MA2-PILOT-003-03 | Assert skip visible in session-resume.md | — | CHILD | TODO |
| TC-MA2-PILOT-004 | Pilot: second full run zero material changes | ALL | PARENT | BLOCKED |
| TC-MA2-PILOT-004-01 | Hash key outputs after first run | — | CHILD | TODO |
| TC-MA2-PILOT-004-02 | Re-run same sequence | — | CHILD | TODO |
| TC-MA2-PILOT-004-03 | Compare hashes (strip timestamps) | — | CHILD | TODO |
| TC-MA2-FINAL-001 | Independent review and closure gate | ALL PILOTS | PARENT | BLOCKED |
| TC-MA2-FINAL-001-01 | Collect all counter values | — | CHILD | TODO |
| TC-MA2-FINAL-001-02 | Verify all counters are zero | — | CHILD | TODO |
| TC-MA2-FINAL-001-03 | Write final-report-ma2.md | — | CHILD | TODO |
| TC-MA2-FINAL-001-04 | Write evidence declaration and run supervisor + --terminal | — | CHILD | TODO |

---

## EXECUTION CONTROL LAYER

---

### TC-MA2-PIPE-001 — Make Sprint Prompt a View Over next-work-items.json

```yaml
parent_taskcard_id: TC-MA2-PIPE-001
type: PARENT
status: READY
requirements: [REQ-PIPE-001, REQ-PIPE-002, REQ-PIPE-003]
root_cause: |
  generate_supervisor_packet.py has its own task loading pipeline
  (selected-product-gaps.json → fixture fallback) that diverges from the
  governed pipeline (autonomous_cycle.py → capability_feature_compiler →
  next-work-items.json). The agent reads both and reconciles at LLM-judgment
  time, producing different results each rerun.
scope:
  allowed_files:
    - tools/supervisor/generate_supervisor_packet.py (lines 624-703 only + session-resume section for SKIP)
    - tests/supervisor/test_generate_supervisor_packet_pipe.py (new)
  forbidden_files: [src/python/**, src/net/**, any other supervisor file]
preserved_behavior: |
  All sections outside lines 624-703 unchanged. Dogfood lane (step 5),
  evidence task (step 6), fallback-if-no-tasks guard (line 752+) untouched.
parent_acceptance_criteria:
  - next-sprint.md task section contains item_ids matching next-work-items.json
  - No path containing 'fixtures' appears in next-sprint.md task descriptions
  - If next-work-items.json empty: next-sprint.md has "NO GOVERNED PRODUCT WORK"
  - All 3 new test files pass
child_taskcards: [TC-MA2-PIPE-001-01, TC-MA2-PIPE-001-02, TC-MA2-PIPE-001-03, TC-MA2-PIPE-001-04, TC-MA2-PIPE-001-05]
rollback: git checkout tools/supervisor/generate_supervisor_packet.py
```

---

#### TC-MA2-PIPE-001-01 — Inspect and Record Exact Replacement Site

```yaml
child_taskcard_id: TC-MA2-PIPE-001-01
parent: TC-MA2-PIPE-001
type: CHILD — INVESTIGATION
status: TODO
requirements: [REQ-PIPE-001]
purpose: Establish exact line boundaries and variable names before any edit. Prevent scope drift.
scope:
  allowed: Read generate_supervisor_packet.py lines 600-760; read next-work-items.json
  forbidden: any edit
```

**Micro-steps:**

```
MS-PIPE-001-01-01  PENDING
Action: Read generate_supervisor_packet.py lines 600-760
Target: tools/supervisor/generate_supervisor_packet.py
Expected output: Exact line numbers for:
  (a) `selected_gaps =` assignment start
  (b) gap-loop end
  (c) gap_fixtures assignment line
  (d) fallback block end
Completion check: 4 line numbers recorded

MS-PIPE-001-01-02  PENDING
Action: Read .local/supervisor/next-work-items.json (first 60 lines)
Target: .local/supervisor/next-work-items.json
Expected output: Confirmed root key is "items"; per-item fields documented
Completion check: item_id, title, lane, priority, description, acceptance_criteria,
  verification_command confirmed present in items[0]

MS-PIPE-001-01-03  PENDING
Action: Record field mapping: NWI item fields → task dict keys
Purpose: Every task dict key in replacement must map to an NWI item field
Expected output: Mapping table:
  item.item_id -> supervisor_task_ref
  item.title -> title
  item.description -> description
  item.verification_command -> validation_command
  item.acceptance_criteria -> acceptance_criteria
  item.lane -> determines lane ("C3")
Completion check: All 6 task dict keys mapped

MS-PIPE-001-01-04  PENDING
Action: Confirm task_seq variable is int before line 624
Target: generate_supervisor_packet.py lines 550-624
Expected output: task_seq type confirmed
Completion check: No IntError risk in replacement code
```

**Acceptance checks:** Line boundaries documented; field mapping complete.
**Closeout criteria:** All 4 micro-steps COMPLETE.

---

#### TC-MA2-PIPE-001-02 — Write Test Fixtures for NWI-Sourced Prompt

```yaml
child_taskcard_id: TC-MA2-PIPE-001-02
parent: TC-MA2-PIPE-001
type: CHILD
status: TODO
requirements: [REQ-PIPE-001, REQ-PIPE-002, REQ-PIPE-003]
purpose: Tests must exist before implementation so failures are detectable.
scope:
  allowed_files: [tests/supervisor/test_generate_supervisor_packet_pipe.py]
  forbidden: any modification to generate_supervisor_packet.py yet
```

**Micro-steps:**

```
MS-PIPE-001-02-01  PENDING
Action: Create tests/supervisor/test_generate_supervisor_packet_pipe.py with 3 test functions
Test 1 — test_sprint_prompt_sources_from_nwi:
  Mock .local/supervisor/next-work-items.json with 3 items (item_id, title, lane="product")
  Run generate_supervisor_packet task generation
  Assert each item_id appears in task supervisor_task_ref fields
Test 2 — test_sprint_prompt_empty_nwi:
  Mock next-work-items.json as {"items": []}
  Assert tasks contain item with title "NO GOVERNED PRODUCT WORK"
Test 3 — test_sprint_prompt_no_fixture_read:
  Mock next-work-items.json with 3 items
  Assert .supervisor/fixtures/ directory is never accessed
Expected: File created, 3 test functions defined
Note: Tests FAIL before implementation (expected)

MS-PIPE-001-02-02  PENDING
Action: Verify test file syntax is valid Python
Command: python -m py_compile tests/supervisor/test_generate_supervisor_packet_pipe.py
Expected: exit 0
Completion check: No syntax errors
```

**Acceptance checks:** 3 test functions present; file compiles; tests fail (expected pre-impl).
**Closeout criteria:** Both micro-steps COMPLETE.

---

#### TC-MA2-PIPE-001-03 — Replace Lines 625-703 with NWI Reader

```yaml
child_taskcard_id: TC-MA2-PIPE-001-03
parent: TC-MA2-PIPE-001
type: CHILD
status: TODO
depends_on: TC-MA2-PIPE-001-01
requirements: [REQ-PIPE-001, REQ-PIPE-002]
purpose: Replace the two-pipeline divergence with single NWI authority.
scope:
  allowed_files: [tools/supervisor/generate_supervisor_packet.py lines 624-703 only]
  forbidden: any other lines in this file or any other file
```

**Replacement code (exact — insert in place of lines 624-703):**

```python
    # 4. Product-factory lanes from canonical governed pipeline output.
    # next-work-items.json is the SINGLE authoritative source for task selection.
    # REQ-PIPE-001: legacy selected-product-gaps.json + fixture fallback REMOVED.
    _nwi_path = repo_root / ".local" / "supervisor" / "next-work-items.json"
    product_items: list = []
    if _nwi_path.exists():
        try:
            _nwi = json.loads(_nwi_path.read_text(encoding="utf-8"))
            _all_items = _nwi.get("items", [])
            product_items = [
                i for i in _all_items
                if i.get("lane") in ("product", "product-advancement", "rework")
                and not i.get("external_gate")
            ][:5]
        except Exception as _nwi_err:
            print(f"[WARN] next-work-items.json load failed: {_nwi_err} -- no product tasks added")
    else:
        print("[WARN] next-work-items.json not found -- run autonomous_cycle.py first")

    # Deprecation check: log if legacy file is non-empty (should never happen)
    _legacy_gaps = load_selected_product_gaps(repo_root)
    if _legacy_gaps:
        print(f"[WARN] selected-product-gaps.json is non-empty ({len(_legacy_gaps)} items). "
              f"This file is deprecated. Investigate what wrote to it.")

    for item in product_items:
        item_id = item.get("item_id", item.get("gap_id", "selected-gap"))
        title = item.get("title", item_id)
        description = item.get("description", "")
        verification = item.get("verification_command", item.get("acceptance_criteria", "pytest tests/ -x -q"))
        tasks.append({
            "task_id": f"TASK-{task_seq:03d}",
            "title": title,
            "description": description,
            "status": "pending",
            "ff_doc_ref": str(_nwi_path.relative_to(repo_root)).replace("\\", "/"),
            "supervisor_task_ref": item_id,
            "acceptance_criteria": item.get("acceptance_criteria", ""),
            "validation_command": verification,
            "non_authoritative": False,
            "lane": "C3",
        })
        task_seq += 1

    if not product_items:
        tasks.append({
            "task_id": f"TASK-{task_seq:03d}",
            "title": "NO GOVERNED PRODUCT WORK SELECTED",
            "description": (
                "next-work-items.json is empty or contains no product-lane items. "
                "Run autonomous_cycle.py to regenerate, or check capability compiler output."
            ),
            "status": "pending",
            "non_authoritative": True,
            "lane": "C1",
        })
        task_seq += 1
```

**Micro-steps:**

```
MS-PIPE-001-03-01  PENDING
Action: Identify exact old_string for Edit tool
  Start: "    # 4. Product-factory lanes from governed selected gaps..."
  End: last "task_seq += 1" before "# 5. Always: dogfood" comment
Confirm old_string is unique: grep count == 1
Completion check: old_string documented

MS-PIPE-001-03-02  PENDING
Action: Execute Edit tool with old_string → replacement block above
Target: tools/supervisor/generate_supervisor_packet.py
Expected: File modified
Completion check: grep "gap_fixtures" in task section → 0 matches

MS-PIPE-001-03-03  PENDING
Action: Verify file parses without syntax error
Command: python -m py_compile tools/supervisor/generate_supervisor_packet.py
Expected: exit 0
```

**Rollback:** `git checkout tools/supervisor/generate_supervisor_packet.py`
**Acceptance checks:** `gap_fixtures` gone from task section; file compiles.
**Closeout criteria:** All 3 micro-steps COMPLETE.

---

#### TC-MA2-PIPE-001-04 — Remove gap_fixtures Dead Code and Add Deprecation Note

```yaml
child_taskcard_id: TC-MA2-PIPE-001-04
parent: TC-MA2-PIPE-001
type: CHILD
status: TODO
depends_on: TC-MA2-PIPE-001-03
purpose: Dead code misleads future readers.
```

**Micro-steps:**

```
MS-PIPE-001-04-01  PENDING
Action: grep "gap_fixtures" in generate_supervisor_packet.py
Expected: 0 matches in task generation section
Completion check: If matches found, investigate (likely incomplete edit in 01-03)

MS-PIPE-001-04-02  PENDING
Action: grep "poc-gap-extraction" in generate_supervisor_packet.py
Expected: 0 matches
Completion check: Fixture path string not referenced in task generation

MS-PIPE-001-04-03  PENDING
Action: Add deprecation comment to load_selected_product_gaps() function
Target: generate_supervisor_packet.py, function signature line
New comment line before def: "# DEPRECATED: Retained only for non-empty legacy WARN check. Not used for task selection."
Completion check: grep "DEPRECATED" generate_supervisor_packet.py → 1 match near load_selected_product_gaps
```

**Acceptance checks:** No `gap_fixtures` in task generation; deprecation comment added.
**Closeout criteria:** All 3 micro-steps COMPLETE.

---

#### TC-MA2-PIPE-001-05 — Run Tests and Inspect next-sprint.md

```yaml
child_taskcard_id: TC-MA2-PIPE-001-05
parent: TC-MA2-PIPE-001
type: CHILD
status: TODO
depends_on: [TC-MA2-PIPE-001-03, TC-MA2-PIPE-001-04]
```

**Micro-steps:**

```
MS-PIPE-001-05-01  PENDING
Command: .venv/Scripts/pytest tests/supervisor/test_generate_supervisor_packet_pipe.py -v
Expected: 3/3 PASS
Evidence: capture output

MS-PIPE-001-05-02  PENDING
Command: python tools/supervisor/generate_supervisor_packet.py
Expected: next-sprint.md regenerated (mtime updated)

MS-PIPE-001-05-03  PENDING
Action: Read first 80 lines of next-sprint.md
Target: reports/supervisor/next-sprint.md
Expected: task section contains supervisor_task_ref values matching WI-GAP-* ids
Completion check: At least 1 WI-GAP-DIF-* id present

MS-PIPE-001-05-04  PENDING
Command: grep "poc-gap-extraction\|fixtures" reports/supervisor/next-sprint.md
Expected: 0 matches

MS-PIPE-001-05-05  PENDING
Command: .venv/Scripts/pytest tests/supervisor/ -x -q
Expected: 0 new failures
Evidence: capture full output
```

**Acceptance checks:** 3/3 new tests pass; WI-GAP-* appears in next-sprint.md; 0 regressions.
**Closeout criteria:** All 5 micro-steps COMPLETE.

---

### TC-MA2-SIGNAL-001 — Enforce Signal Field Coherence at Write Time

```yaml
parent_taskcard_id: TC-MA2-SIGNAL-001
type: PARENT
status: READY
requirements: [REQ-SIGNAL-001, REQ-SIGNAL-002, REQ-SIGNAL-003]
root_cause: |
  autonomous_cycle.py constructs the signal dict (lines ~2145-2206) and writes it
  via atomic_write_json(signal_path, signal) at line 2207. The construction logic
  can produce mutually contradictory fields. The write happens without coherence
  validation. check_continuation.py silently resolves contradictions at read time
  via _gates_override with no diagnostic.
correction: CORRECTION-001 — target is autonomous_cycle.py, NOT continuation_state.py
scope:
  allowed_files:
    - tools/supervisor/autonomous_cycle.py (signal construction section only)
    - tools/supervisor/check_continuation.py (after signal load, 6 lines)
    - tools/supervisor/signal_coherence.py (new file)
    - tests/supervisor/test_signal_coherence.py (new file)
  forbidden_files: [continuation_state.py, src/python/**, src/net/**]
preserved_behavior: |
  check_continuation.py _gates_override logic unchanged.
  atomic_write_json call unchanged — only signal dict corrected before the call.
parent_acceptance_criteria:
  - Signal with stop_reason + autonomous_continue=True → stop_reason cleared before write
  - Signal with rework_items=[] + critical_rework stop_reason → stop_reason cleared
  - check_continuation.py emits [COHERENCE] diagnostic when disk signal is incoherent
  - continuation-signal.json has no contradictory fields after running SIGNAL-001-05
```

---

#### TC-MA2-SIGNAL-001-01 — Investigate Signal Construction Site

```yaml
child_taskcard_id: TC-MA2-SIGNAL-001-01
parent: TC-MA2-SIGNAL-001
type: CHILD — INVESTIGATION
status: TODO
purpose: Map exact signal dict construction and write site before writing coherence code.
scope:
  allowed: Read autonomous_cycle.py lines 2130-2215
  forbidden: any edit
```

**Micro-steps:**

```
MS-SIGNAL-001-01-01  PENDING
Action: Read autonomous_cycle.py lines 2130-2215
Target: tools/supervisor/autonomous_cycle.py
Expected output: Full signal dict construction visible
Completion check: Line numbers for:
  (a) signal dict start (signal = { ... })
  (b) stop_reason assignment
  (c) rework_items assignment
  (d) autonomous_continue assignment
  (e) atomic_write_json(signal_path, signal) call

MS-SIGNAL-001-01-02  PENDING
Action: Record all conditions under which stop_reason and rework_items can be set contradictorily
Expected output: Condition map documenting when stop_reason="critical_rework..." is set
  while rework_items can become [] (e.g. after global_repair clears it via a different path)
Completion check: Root cause of production incoherence documented

MS-SIGNAL-001-01-03  PENDING
Action: Identify insertion point between last field assignment and atomic_write_json call
Expected output: Exact line number for coherence check insertion
Completion check: Context string for Edit tool old_string documented
```

**Acceptance checks:** Line numbers, condition map, and insertion point documented.
**Closeout criteria:** All 3 micro-steps COMPLETE.

---

#### TC-MA2-SIGNAL-001-02 — Add validate_signal_coherence() Function

```yaml
child_taskcard_id: TC-MA2-SIGNAL-001-02
parent: TC-MA2-SIGNAL-001
type: CHILD
status: TODO
depends_on: TC-MA2-SIGNAL-001-01
purpose: Create coherence validator as standalone importable function.
scope:
  allowed: create tools/supervisor/signal_coherence.py
  forbidden: modify autonomous_cycle.py in this step
```

**Exact module content:**

```python
"""signal_coherence.py — Signal field coherence validation for continuation-signal.json.
Written by TC-MA2-SIGNAL-001 (bubbly-dancing-pony plan).
"""
from __future__ import annotations


def validate_signal_coherence(signal: dict) -> tuple[list[str], dict]:
    """
    Validate continuation-signal.json fields are mutually consistent.
    Returns (issues, corrected_signal).
    Auto-corrects clear-cut contradictions. Issues describes what was corrected.
    Rule 3 (advisory stop with no hard_stops) is logged but NOT auto-corrected.
    """
    issues: list[str] = []
    s = dict(signal)

    auto_cont = s.get("autonomous_continue")
    stop_reason = (s.get("stop_reason") or "").strip()
    rework_items = s.get("rework_items") or []

    # Rule 1: autonomous_continue=True incompatible with any stop_reason
    if auto_cont is True and stop_reason:
        issues.append(
            f"stop_reason={stop_reason!r} contradicts autonomous_continue=True; clearing stop_reason"
        )
        s["stop_reason"] = None

    # Rule 2: rework_items=[] incompatible with stop_reason claiming rework blocks
    if not rework_items and stop_reason == "critical_rework_blocks_continuation":
        issues.append(
            "stop_reason=critical_rework_blocks_continuation but rework_items=[]; clearing stop_reason"
        )
        s["stop_reason"] = None

    # Rule 3 (advisory — no auto-correct; conservative to avoid masking legitimate stops)
    if not auto_cont:
        hard_stops = s.get("hard_stops_detected") or []
        cont_state = s.get("continuation_state", "")
        if not hard_stops and not cont_state.startswith("YES"):
            issues.append(
                f"autonomous_continue=False with empty hard_stops and "
                f"continuation_state={cont_state!r} (advisory — not auto-corrected)"
            )

    return issues, s
```

**Micro-steps:**

```
MS-SIGNAL-001-02-01  PENDING
Action: Create tools/supervisor/signal_coherence.py with content above
Completion check: python -m py_compile tools/supervisor/signal_coherence.py exits 0

MS-SIGNAL-001-02-02  PENDING
Action: Create tests/supervisor/test_signal_coherence.py with 5 test functions:
  test_auto_continue_true_with_stop_reason_corrected
  test_rework_empty_with_rework_stop_reason_corrected
  test_coherent_signal_unchanged
  test_rule3_advisory_no_auto_correct
  test_current_disk_state_incoherence_corrected (uses actual production signal fields)
Completion check: File created, 5 functions defined

MS-SIGNAL-001-02-03  PENDING
Command: .venv/Scripts/pytest tests/supervisor/test_signal_coherence.py -v
Expected: 5/5 PASS
```

**Acceptance checks:** File compiles; 5/5 tests pass.
**Closeout criteria:** All 3 micro-steps COMPLETE.

---

#### TC-MA2-SIGNAL-001-03 — Wire Coherence Check into Signal Write Path

```yaml
child_taskcard_id: TC-MA2-SIGNAL-001-03
parent: TC-MA2-SIGNAL-001
type: CHILD
status: TODO
depends_on: [TC-MA2-SIGNAL-001-01, TC-MA2-SIGNAL-001-02]
purpose: Apply coherence validator immediately before atomic_write_json in autonomous_cycle.py.
scope:
  allowed_files: [tools/supervisor/autonomous_cycle.py (signal write section, ~6 lines inserted)]
  forbidden: continuation_state.py, any other section of autonomous_cycle.py
```

**Code to insert (immediately before `atomic_write_json(signal_path, signal)`):**

```python
        # TC-MA2-SIGNAL-001: Enforce signal field coherence at write time
        try:
            from signal_coherence import validate_signal_coherence as _vsc
            _sc_issues, signal = _vsc(signal)
            for _sci in _sc_issues:
                print(f"  [SIGNAL_COHERENCE] Corrected: {_sci}", file=sys.stderr)
        except Exception as _sc_err:
            print(f"  [SIGNAL_COHERENCE] WARNING: coherence check failed: {_sc_err}", file=sys.stderr)
```

**Micro-steps:**

```
MS-SIGNAL-001-03-01  PENDING
Action: Identify exact old_string context from SIGNAL-001-01 (line just before atomic_write_json)
Confirm old_string is unique in file
Completion check: old_string documented

MS-SIGNAL-001-03-02  PENDING
Action: Execute Edit tool to insert coherence block before atomic_write_json
Target: tools/supervisor/autonomous_cycle.py
Expected: 6 new lines inserted
Completion check: python -m py_compile tools/supervisor/autonomous_cycle.py exits 0

MS-SIGNAL-001-03-03  PENDING
Action: Verify signal_coherence import resolves at runtime
Command: cd tools/supervisor && python -c "from signal_coherence import validate_signal_coherence; print('OK')"
Expected: prints OK
```

**Rollback:** `git checkout tools/supervisor/autonomous_cycle.py`
**Acceptance checks:** File compiles; import resolves.
**Closeout criteria:** All 3 micro-steps COMPLETE.

---

#### TC-MA2-SIGNAL-001-04 — Add Read-Time Diagnostic in check_continuation.py

```yaml
child_taskcard_id: TC-MA2-SIGNAL-001-04
parent: TC-MA2-SIGNAL-001
type: CHILD
status: TODO
depends_on: TC-MA2-SIGNAL-001-02
purpose: Surface stale incoherent disk state to operators. Diagnostic only — no auto-correction at read time.
scope:
  allowed_files: [tools/supervisor/check_continuation.py (after signal load, before Check 2)]
  forbidden: any auto-correction logic here
```

**Code to insert (after signal loaded, before "# --- Check 2" comment near line 399):**

```python
    # TC-MA2-SIGNAL-001: Read-time coherence diagnostic (diagnostic only — no correction here)
    try:
        from signal_coherence import validate_signal_coherence as _vsc_diag
        _diag_issues, _ = _vsc_diag(signal)
        for _di in _diag_issues:
            print(f"[COHERENCE] Signal on disk is incoherent: {_di}", file=sys.stderr)
    except Exception:
        pass  # Diagnostic is non-blocking
```

**Micro-steps:**

```
MS-SIGNAL-001-04-01  PENDING
Action: Read check_continuation.py lines 380-405 to find insertion point
Target: tools/supervisor/check_continuation.py
Completion check: Exact old_string context (unique 3-line window before "# --- Check 2")

MS-SIGNAL-001-04-02  PENDING
Action: Execute Edit to insert diagnostic block
Target: tools/supervisor/check_continuation.py
Completion check: python -m py_compile tools/supervisor/check_continuation.py exits 0

MS-SIGNAL-001-04-03  PENDING
Action: Run check_continuation.py against current incoherent disk state
Command: python tools/supervisor/check_continuation.py 2>&1 | grep COHERENCE
Expected: [COHERENCE] line present (current disk signal still incoherent until SIGNAL-001-05)
```

**Acceptance checks:** Diagnostic fires for current incoherent disk state.
**Closeout criteria:** All 3 micro-steps COMPLETE.

---

#### TC-MA2-SIGNAL-001-05 — Repair Current Incoherent Disk State

```yaml
child_taskcard_id: TC-MA2-SIGNAL-001-05
parent: TC-MA2-SIGNAL-001
type: CHILD
status: TODO
depends_on: TC-MA2-SIGNAL-001-03
purpose: Correct the on-disk continuation-signal.json that has contradictory fields.
current_incoherent_state:
  autonomous_continue: true
  stop_reason: "critical_rework_blocks_continuation"
  rework_items: []
  hard_stops_detected: []
rules_that_fire: [Rule 1 (auto_continue=True + stop_reason), Rule 2 (empty rework + critical_rework reason)]
```

**Micro-steps:**

```
MS-SIGNAL-001-05-01  PENDING
Action: Run coherence validation on current disk state
Command: python -c "
import json, sys
sys.path.insert(0, 'tools/supervisor')
from signal_coherence import validate_signal_coherence
sig = json.loads(open('.local/supervisor/continuation-signal.json').read())
issues, corrected = validate_signal_coherence(sig)
print('Issues:', issues)
print('Corrected stop_reason:', corrected.get('stop_reason'))
"
Expected: Issues list non-empty; corrected stop_reason is None

MS-SIGNAL-001-05-02  PENDING
Action: Write corrected signal to disk
Command: python -c "
import json, sys
from pathlib import Path
sys.path.insert(0, 'tools/supervisor')
from signal_coherence import validate_signal_coherence
sig_path = Path('.local/supervisor/continuation-signal.json')
sig = json.loads(sig_path.read_text(encoding='utf-8'))
issues, corrected = validate_signal_coherence(sig)
for issue in issues:
    print(f'[SIGNAL_COHERENCE] Corrected: {issue}', file=sys.stderr)
sig_path.write_text(json.dumps(corrected, indent=2) + '\n', encoding='utf-8')
print('Done')
"
Expected: Signal written with stop_reason=null

MS-SIGNAL-001-05-03  PENDING
Action: Verify corrected state
Command: python -c "import json; s=json.load(open('.local/supervisor/continuation-signal.json')); print('stop_reason:', s.get('stop_reason')); print('auto_continue:', s.get('autonomous_continue'))"
Expected: stop_reason: None, auto_continue: True

MS-SIGNAL-001-05-04  PENDING
Command: python tools/supervisor/check_continuation.py 2>&1 | grep COHERENCE
Expected: 0 matches (signal is now coherent)
```

**Rollback:** `git checkout .local/supervisor/continuation-signal.json`
**Acceptance checks:** No COHERENCE warnings in check_continuation output after repair.
**Closeout criteria:** All 4 micro-steps COMPLETE.

---

### TC-MA2-SKIP-001 — Machine-Readable Skip Records for Closeout Failures

```yaml
parent_taskcard_id: TC-MA2-SKIP-001
type: PARENT
status: READY
requirements: [REQ-SKIP-001, REQ-SKIP-002, REQ-SKIP-003]
root_cause: |
  autonomous_cycle.py closeout wraps Steps 4b, 4a-compiler, 6, 6b in try/except
  with print(WARNING). Failures go to stdout and are lost between sessions.
  Most consequential: if Step 6 copy_cycle_summaries fails, next-work-items.json
  stays stale in .local/supervisor/.
parent_acceptance_criteria:
  - Mock copy_cycle_summaries to raise → skip record in closeout-skip-ledger.jsonl
  - session-resume.md contains outstanding skip entry after mock failure
  - Cycle exits 0 after Step 6 failure (best-effort policy preserved)
```

---

#### TC-MA2-SKIP-001-01 — Create closeout_skip_ledger.py Module

```yaml
child_taskcard_id: TC-MA2-SKIP-001-01
parent: TC-MA2-SKIP-001
type: CHILD
status: TODO
purpose: Create the skip ledger module before wiring into autonomous_cycle.py.
scope:
  allowed: create tools/supervisor/closeout_skip_ledger.py
  forbidden: modify autonomous_cycle.py in this step
```

**Exact module content:**

```python
"""closeout_skip_ledger.py — Machine-readable closeout skip records.
Written by TC-MA2-SKIP-001 (bubbly-dancing-pony plan).
"""
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent.parent  # repo root
SKIP_LEDGER_PATH = _HERE / ".local" / "supervisor" / "closeout-skip-ledger.jsonl"


def record_skip(
    sprint_id: str,
    step_id: str,
    step_description: str,
    error: Exception,
    impact: str,
    recovery_hint: str,
) -> None:
    """Append a skip record to the ledger. Non-blocking — errors printed only."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sprint_id": sprint_id,
        "step_id": step_id,
        "step_description": step_description,
        "error_type": type(error).__name__,
        "error_summary": str(error)[:500],
        "impact": impact,
        "recovery_hint": recovery_hint,
        "resolved": False,
    }
    try:
        SKIP_LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
        with SKIP_LEDGER_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as _err:
        print(f"[SKIP_LEDGER] ERROR: failed to write skip record: {_err}", file=sys.stderr)


def get_outstanding_skips(limit: int = 10) -> list[dict]:
    """Return unresolved skip entries, most recent first."""
    if not SKIP_LEDGER_PATH.exists():
        return []
    entries: list[dict] = []
    try:
        for line in SKIP_LEDGER_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if not entry.get("resolved"):
                entries.append(entry)
    except Exception:
        return []
    return sorted(entries, key=lambda e: e.get("timestamp", ""), reverse=True)[:limit]


def mark_resolved(step_id: str, sprint_id: str) -> int:
    """Mark matching skip entries as resolved. Returns count resolved."""
    if not SKIP_LEDGER_PATH.exists():
        return 0
    lines = SKIP_LEDGER_PATH.read_text(encoding="utf-8").splitlines()
    resolved_count = 0
    new_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            if (entry.get("step_id") == step_id
                    and entry.get("sprint_id") == sprint_id
                    and not entry.get("resolved")):
                entry["resolved"] = True
                entry["resolved_at"] = datetime.now(timezone.utc).isoformat()
                resolved_count += 1
            new_lines.append(json.dumps(entry))
        except Exception:
            new_lines.append(line)
    SKIP_LEDGER_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return resolved_count
```

**Micro-steps:**

```
MS-SKIP-001-01-01  PENDING
Action: Create tools/supervisor/closeout_skip_ledger.py with content above
Completion check: python -m py_compile tools/supervisor/closeout_skip_ledger.py exits 0

MS-SKIP-001-01-02  PENDING
Action: Create tests/supervisor/test_skip_ledger.py with 4 test functions:
  test_record_skip_writes_to_ledger
  test_get_outstanding_skips_returns_unresolved
  test_mark_resolved_marks_entry
  test_ledger_non_blocking_on_write_error
Command: .venv/Scripts/pytest tests/supervisor/test_skip_ledger.py -v
Expected: 4/4 PASS
```

**Acceptance checks:** File compiles; 4/4 tests pass.
**Closeout criteria:** Both micro-steps COMPLETE.

---

#### TC-MA2-SKIP-001-02 — Audit All try/except Blocks in autonomous_cycle.py Closeout

```yaml
child_taskcard_id: TC-MA2-SKIP-001-02
parent: TC-MA2-SKIP-001
type: CHILD — INVESTIGATION
status: TODO
purpose: Identify all except blocks in closeout sequence before wiring skip records.
```

**Micro-steps:**

```
MS-SKIP-001-02-01  PENDING
Action: grep for WARNING+failed patterns in autonomous_cycle.py closeout section
Command: grep -n "WARNING.*failed\|except Exception" tools/supervisor/autonomous_cycle.py | tail -40
Expected: List of line numbers for except-with-warning patterns in Steps 4-6
Completion check: At minimum these steps found:
  copy_cycle_summaries (Step 6)
  capability_feature_compiler (Step 4a)
  validate_prompt_and_work_items (Step 4b)

MS-SKIP-001-02-02  PENDING
Action: Classify each identified block by consequence:
  CRITICAL: next sprint gets stale/wrong work items
  MEDIUM: evidence or quality data lost
  LOW: convenience data lost
Expected output: Classification table with step_id, line_number, consequence_level, impact, recovery_hint
Completion check: Table has ≥4 entries
```

**Acceptance checks:** Classification table with ≥4 entries, each with impact and recovery_hint.
**Closeout criteria:** Both micro-steps COMPLETE.

---

#### TC-MA2-SKIP-001-03 — Wire Skip Ledger into Priority Closeout except Blocks

```yaml
child_taskcard_id: TC-MA2-SKIP-001-03
parent: TC-MA2-SKIP-001
type: CHILD
status: TODO
depends_on: [TC-MA2-SKIP-001-01, TC-MA2-SKIP-001-02]
purpose: Replace bare WARNING prints with skip record writes for CRITICAL consequences.
  Preserve best-effort: cycle must still exit 0 after skip.
priority_targets:
  1: copy_cycle_summaries (Step 6) — stale next-work-items.json
  2: capability_feature_compiler (Step 4a) — no governed gaps
  3: validate_prompt_and_work_items (Step 4b) — quality not checked
```

**Pattern for each replacement:**

```python
# BEFORE:
except Exception as _err:
    print(f"WARNING: [description] failed: {_err}")

# AFTER (add try/except around record_skip to keep it non-blocking):
except Exception as _err:
    print(f"WARNING: [description] failed: {_err}")
    try:
        from closeout_skip_ledger import record_skip
        record_skip(
            sprint_id=sprint_id,
            step_id="[STEP_ID]",
            step_description="[human description]",
            error=_err,
            impact="[impact of skipping]",
            recovery_hint="[recovery command]",
        )
    except Exception as _sl_err:
        print(f"  [SKIP_LEDGER] record failed: {_sl_err}", file=sys.stderr)
```

**Micro-steps:**

```
MS-SKIP-001-03-01  PENDING
Action: Apply pattern to copy_cycle_summaries except block (CRITICAL)
Target: autonomous_cycle.py Step 6 except block (line identified in SKIP-001-02)
impact: "next-work-items.json not updated — next sprint reads stale governed work items"
recovery_hint: "python tools/supervisor/autonomous_cycle.py --copy-only"
Completion check: python -m py_compile tools/supervisor/autonomous_cycle.py exits 0

MS-SKIP-001-03-02  PENDING
Action: Apply pattern to capability_feature_compiler except block (CRITICAL)
Target: autonomous_cycle.py Step 4a-compiler except block
impact: "next-work-items.json has no gap_sourced_items"
recovery_hint: "python tools/supervisor/capability_feature_compiler.py"
Completion check: python -m py_compile tools/supervisor/autonomous_cycle.py exits 0

MS-SKIP-001-03-03  PENDING
Action: Apply pattern to validate_prompt_and_work_items except block (MEDIUM)
Target: autonomous_cycle.py Step 4b except block
impact: "Prompt quality not validated"
recovery_hint: "python tools/supervisor/sprint_executor_validate.py <declaration>"
Completion check: python -m py_compile tools/supervisor/autonomous_cycle.py exits 0

MS-SKIP-001-03-04  PENDING
Command: .venv/Scripts/pytest tests/supervisor/ -x -q
Expected: No new failures introduced (existing closeout tests pass)
```

**Rollback:** `git checkout tools/supervisor/autonomous_cycle.py`
**Acceptance checks:** 3 priority except blocks wired; file compiles; existing tests pass.
**Closeout criteria:** All 4 micro-steps COMPLETE.

---

#### TC-MA2-SKIP-001-04 — Surface Outstanding Skips in session-resume.md

```yaml
child_taskcard_id: TC-MA2-SKIP-001-04
parent: TC-MA2-SKIP-001
type: CHILD
status: TODO
depends_on: TC-MA2-SKIP-001-01
purpose: Make skip records visible to next session agent without manual ledger inspection.
scope:
  allowed_files: [tools/supervisor/generate_supervisor_packet.py (session-resume section only)]
  forbidden: task-generation section (already modified by TC-MA2-PIPE-001)
```

**Code to insert in session-resume generation section:**

```python
    # TC-MA2-SKIP-001: Surface outstanding closeout skips in session-resume
    try:
        from closeout_skip_ledger import get_outstanding_skips
        _outstanding = get_outstanding_skips(limit=5)
        if _outstanding:
            resume_lines.append(f"\n## Outstanding Skipped Closeout Steps ({len(_outstanding)})\n\n")
            for _skip in _outstanding:
                resume_lines.append(
                    f"- **{_skip['step_id']}** (sprint: {_skip['sprint_id']}): "
                    f"{_skip['step_description']}. Impact: {_skip['impact']}. "
                    f"Recovery: `{_skip['recovery_hint']}`\n"
                )
    except Exception:
        pass  # Non-blocking
```

**Micro-steps:**

```
MS-SKIP-001-04-01  PENDING
Action: Find session-resume generation block in generate_supervisor_packet.py
Command: grep -n "resume_lines\|session-resume" tools/supervisor/generate_supervisor_packet.py | head -20
Expected: Line numbers for resume_lines list construction
Completion check: Insertion point before final write call documented

MS-SKIP-001-04-02  PENDING
Action: Insert skip surface code at identified location
Target: tools/supervisor/generate_supervisor_packet.py (session-resume section)
Completion check: python -m py_compile tools/supervisor/generate_supervisor_packet.py exits 0

MS-SKIP-001-04-03  PENDING
Action: Create test entry and verify it appears in session-resume.md
Commands:
  python -c "
  import sys; sys.path.insert(0,'tools/supervisor')
  from closeout_skip_ledger import record_skip
  record_skip('TEST-SPRINT','STEP-TEST','test step',Exception('test'),'test impact','test recovery')
  "
  python tools/supervisor/generate_supervisor_packet.py
  grep "Outstanding Skipped" reports/supervisor/session-resume.md
Expected: "Outstanding Skipped Closeout Steps" section present
```

**Acceptance checks:** Skip section visible in session-resume.md.
**Closeout criteria:** All 3 micro-steps COMPLETE.

---

### TC-MA2-VAL-001 — Enforce Validator Count at Runtime

```yaml
parent_taskcard_id: TC-MA2-VAL-001
type: PARENT
status: READY
requirements: [REQ-VAL-001, REQ-VAL-002]
root_cause: |
  governance_validator_runner.py returns {"expected_count": 167, "ran_count": N}
  (lines 813, 816) but never compares them. Import failures in _skipped_validators
  do not affect the sprint verdict. MEMORY.md still says 165. Three-artifact drift.
scope:
  allowed_files:
    - tools/supervisor/governance_validator_runner.py (lines 800-816 insertion)
    - tests/supervisor/test_validator_count_enforcement.py (new)
    - memory/MEMORY.md (one line change)
  forbidden_files: [src/python/**, src/net/**]
```

---

#### TC-MA2-VAL-001-01 — Confirm expected_count=167 is Accurate

```yaml
child_taskcard_id: TC-MA2-VAL-001-01
parent: TC-MA2-VAL-001
type: CHILD — INVESTIGATION
status: TODO
purpose: Verify 167 before adding enforcement. Wrong count would produce false WARN/FAIL.
```

**Micro-steps:**

```
MS-VAL-001-01-01  PENDING
Action: Count all results.append() and results.extend() calls in governance_validator_runner.py
Target: tools/supervisor/governance_validator_runner.py lines 200-822
Method: Read the file and count; note each try/except block's validator count
Completion check: Total count from explicit calls documented

MS-VAL-001-01-02  PENDING
Action: Note that _skipped_validators entries are NOT in ran_count (they failed import)
  Therefore enforcement must compare skipped_count, not (expected_count - ran_count)
Completion check: Enforcement strategy confirmed: check skipped_count > tolerance

MS-VAL-001-01-03  PENDING
Action: Confirm expected_count=167 at line 813 is the current value
Command: grep -n "expected_count" tools/supervisor/governance_validator_runner.py
Expected: "expected_count": 167 at line 813
Completion check: Value confirmed; if different from 167, record actual value for use in VAL-001-02
```

**Acceptance checks:** Actual count verified; enforcement strategy confirmed.
**Closeout criteria:** All 3 micro-steps COMPLETE.

---

#### TC-MA2-VAL-001-02 — Add Count Enforcement After skipped_count

```yaml
child_taskcard_id: TC-MA2-VAL-001-02
parent: TC-MA2-VAL-001
type: CHILD
status: TODO
depends_on: TC-MA2-VAL-001-01
purpose: Add runtime enforcement that FAILS the sprint if too many validators are skipped.
```

**Exact code to insert (after `skipped_count = sum(...)` line 801, before `ran_count = len(results)`):**

```python
    # TC-MA2-VAL-001: Enforce validator count at runtime
    _VALIDATOR_COUNT_TOLERANCE = 2  # allow up to 2 skipped before blocking sprint
    if _skipped_validators:
        _skipped_names: list[str] = []
        for _sv in _skipped_validators:
            _skipped_names.extend(_sv.get("validators", []))
        _skipped_count_enforce = len(_skipped_names)
        print(
            f"[GOVERNANCE] WARN: {_skipped_count_enforce} validators skipped due to import failures: "
            f"{_skipped_names}",
            file=sys.stderr,
        )
        if _skipped_count_enforce > _VALIDATOR_COUNT_TOLERANCE:
            results.append({
                "validator": "V_COUNT_ENFORCEMENT",
                "result": "FAIL",
                "items": [
                    f"Expected 167 validators; skipped {_skipped_count_enforce} "
                    f"(tolerance={_VALIDATOR_COUNT_TOLERANCE})"
                ],
                "summary": (
                    f"Validator coverage breach: {_skipped_count_enforce} validators "
                    f"did not run (tolerance={_VALIDATOR_COUNT_TOLERANCE})."
                ),
                "blocks_sprint": True,
                "category": "GOVERNANCE_COVERAGE",
            })
```

**Micro-steps:**

```
MS-VAL-001-02-01  PENDING
Action: Identify exact insertion point (line after skipped_count, before ran_count)
Target: governance_validator_runner.py lines 800-803
Command: grep -n "skipped_count\|ran_count" tools/supervisor/governance_validator_runner.py | tail -5
Completion check: old_string context documented (unique)

MS-VAL-001-02-02  PENDING
Action: Execute Edit to insert enforcement block
Target: tools/supervisor/governance_validator_runner.py
Completion check: python -m py_compile tools/supervisor/governance_validator_runner.py exits 0

MS-VAL-001-02-03  PENDING
Action: Create tests/supervisor/test_validator_count_enforcement.py with 3 tests:
  test_single_skip_within_tolerance_no_fail
  test_three_skips_exceed_tolerance_adds_fail
  test_no_skips_no_enforcement
Command: .venv/Scripts/pytest tests/supervisor/test_validator_count_enforcement.py -v
Expected: 3/3 PASS
```

**Acceptance checks:** Enforcement block present; compiles; 3/3 tests pass.
**Closeout criteria:** All 3 micro-steps COMPLETE.

---

#### TC-MA2-VAL-001-03 — Update MEMORY.md Validator Count

```yaml
child_taskcard_id: TC-MA2-VAL-001-03
parent: TC-MA2-VAL-001
type: CHILD
status: TODO
depends_on: TC-MA2-VAL-001-01
purpose: Remove three-artifact drift by updating MEMORY.md.
scope:
  allowed: Edit MEMORY.md validator count entry only
  forbidden: any other MEMORY.md content change
```

**Micro-steps:**

```
MS-VAL-001-03-01  PENDING
Action: Find validator count line in MEMORY.md
Command: grep -n "165\|167\|validators" C:/Users/prora/.claude/projects/c--Users-prora-OneDrive-Documents-GitHub-format-factory/memory/MEMORY.md | head -5
Completion check: Line identified

MS-VAL-001-03-02  PENDING
Action: Edit line to read "167 total validators (V149 added 2026-07-09; VALIDATOR_COUNT_TOLERANCE=2)"
Target: MEMORY.md patterns.md entry or inline entry
Completion check: grep "167" MEMORY.md confirms update
```

**Acceptance checks:** MEMORY.md reflects 167 with tolerance note.
**Closeout criteria:** Both micro-steps COMPLETE.

---

### TC-MA2-LOCK-001 — Group Plan Lock Writes (Grouped Tmp Pattern)

```yaml
parent_taskcard_id: TC-MA2-LOCK-001
type: PARENT
status: READY
requirements: [REQ-LOCK-001, REQ-LOCK-002]
root_cause: |
  write_plan_lock.py writes shared lock tmp+rename (lines 434-437) then keyed lock
  tmp+rename (lines 467-469) sequentially. If second rename fails, shared lock is
  ahead of keyed lock. check_continuation.py uses keyed lock as primary.
correction: CORRECTION-002 — post-write check (lines 474-485) already exists.
  Scope is ONLY the grouped-write pattern (both .tmp before either rename).
scope:
  allowed_files: [tools/supervisor/write_plan_lock.py lines 427-469 only]
  preserved: lines 474-485 (existing post-write check TC-AMD-CONV-002 — DO NOT TOUCH)
  forbidden_files: [src/python/**, src/net/**]
parent_acceptance_criteria:
  - Both .tmp files written before either rename
  - .tmp write failure leaves both final files unchanged
  - Existing post-write check (lines 474-485) still fires
```

---

#### TC-MA2-LOCK-001-01 — Read and Document Current Write Sequence

```yaml
child_taskcard_id: TC-MA2-LOCK-001-01
parent: TC-MA2-LOCK-001
type: CHILD — INVESTIGATION
status: TODO
```

**Micro-steps:**

```
MS-LOCK-001-01-01  PENDING
Action: Read write_plan_lock.py lines 420-490
Target: tools/supervisor/write_plan_lock.py
Expected: Full sequential write pattern visible
Completion check: Lines for shared_tmp write, shared rename, keyed_tmp write, keyed rename, and post-write check all identified with exact line numbers

MS-LOCK-001-01-02  PENDING
Action: Record exact old_string boundaries for the two sequential write blocks (lines 427-469)
Exclude: post-write check (lines 474-485) — must be preserved
Completion check: old_string is unique in file (grep count == 1)
```

**Closeout criteria:** Both micro-steps COMPLETE.

---

#### TC-MA2-LOCK-001-02 — Add _write_both_locks() Helper Function

```yaml
child_taskcard_id: TC-MA2-LOCK-001-02
parent: TC-MA2-LOCK-001
type: CHILD
status: TODO
depends_on: TC-MA2-LOCK-001-01
purpose: Extract grouped-write logic into a testable helper.
```

**Exact helper content:**

```python
def _write_both_locks(
    shared_path: "Path", keyed_path: "Path", lock_text: str
) -> "tuple[bool, str]":
    """Write both lock files via tmp+rename. Write both .tmp files before renaming either.
    Residual risk: if shared rename succeeds but keyed rename fails, they diverge.
    True atomicity requires SQLite/WAL (deferred to migration sprint — see plan deferred table).
    Returns (success, error_message).
    """
    shared_tmp = shared_path.with_suffix(".tmp")
    keyed_tmp = keyed_path.with_suffix(".tmp")
    try:
        shared_tmp.write_text(lock_text, encoding="utf-8")
        keyed_tmp.write_text(lock_text, encoding="utf-8")
        os.replace(str(shared_tmp), str(shared_path))
        os.replace(str(keyed_tmp), str(keyed_path))
        return True, ""
    except Exception as _e:
        for _tmp in (shared_tmp, keyed_tmp):
            try:
                _tmp.unlink(missing_ok=True)
            except Exception:
                pass
        return False, str(_e)
```

**Micro-steps:**

```
MS-LOCK-001-02-01  PENDING
Action: Find appropriate insertion point (before sequential write blocks, as module-level function)
Target: tools/supervisor/write_plan_lock.py
Completion check: Insertion point documented

MS-LOCK-001-02-02  PENDING
Action: Insert _write_both_locks() function at insertion point
Target: tools/supervisor/write_plan_lock.py
Completion check: python -m py_compile tools/supervisor/write_plan_lock.py exits 0
```

**Closeout criteria:** Both micro-steps COMPLETE.

---

#### TC-MA2-LOCK-001-03 — Replace Sequential Writes with _write_both_locks() Call

```yaml
child_taskcard_id: TC-MA2-LOCK-001-03
parent: TC-MA2-LOCK-001
type: CHILD
status: TODO
depends_on: TC-MA2-LOCK-001-02
purpose: Replace lines 427-469 with grouped write. Preserve post-write check at 474-485.
```

**Replacement code (replaces lines 427-469):**

```python
    # TC-MA2-LOCK-001: Grouped write — both .tmp files written before either rename
    _wrote_shared = False
    if _is_temp_path(str(plan_path)):
        print(
            f"[write_plan_lock] SKIPPING shared lock: plan_path is temp/pytest ({plan_path})",
            file=sys.stderr,
        )
        # Keyed-only write for temp paths (preserves test isolation)
        _keyed_tmp = keyed_path.with_suffix(".tmp")
        _keyed_tmp.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
        os.replace(str(_keyed_tmp), str(keyed_path))
        print(f"[write_plan_lock] {keyed_path} written — session={sid!r} (temp path: keyed-only)")
    else:
        _lock_text = json.dumps(lock, indent=2) + "\n"
        _ok, _err_msg = _write_both_locks(_shared_lock_path, keyed_path, _lock_text)
        if not _ok:
            print(f"[write_plan_lock] ERROR: grouped lock write failed: {_err_msg}", file=sys.stderr)
            return
        print(
            f"[write_plan_lock] {_shared_lock_path} + {keyed_path} written — "
            f"status={status}, plan={plan_path!r}"
        )
        _wrote_shared = True
```

**Micro-steps:**

```
MS-LOCK-001-03-01  PENDING
Action: Confirm old_string from LOCK-001-01 is unique in file
Completion check: grep count == 1 for the old_string start boundary

MS-LOCK-001-03-02  PENDING
Action: Execute Edit to replace old_string (lines 427-469) with replacement block
Target: tools/supervisor/write_plan_lock.py
Completion check: python -m py_compile tools/supervisor/write_plan_lock.py exits 0

MS-LOCK-001-03-03  PENDING
Action: Verify existing post-write check still present after edit
Command: grep "TC-AMD-CONV-002\|lock mismatch after write" tools/supervisor/write_plan_lock.py
Expected: At least one match found
Completion check: Post-write check preserved
```

**Rollback:** `git checkout tools/supervisor/write_plan_lock.py`
**Acceptance checks:** File compiles; both .tmp written before rename; post-write check preserved.
**Closeout criteria:** All 3 micro-steps COMPLETE.

---

#### TC-MA2-LOCK-001-04 — Add Grouped-Write Tests

```yaml
child_taskcard_id: TC-MA2-LOCK-001-04
parent: TC-MA2-LOCK-001
type: CHILD
status: TODO
depends_on: TC-MA2-LOCK-001-03
```

**Micro-steps:**

```
MS-LOCK-001-04-01  PENDING
Action: Create tests/supervisor/test_lock_grouped_write.py with 3 tests:
  test_both_locks_written_on_success (both files have correct status after write)
  test_tmp_cleanup_on_write_failure (mock second .tmp write to raise; assert no final file change)
  test_post_write_check_fires (existing check still runs after grouped write)
Command: .venv/Scripts/pytest tests/supervisor/test_lock_grouped_write.py -v
Expected: 3/3 PASS
```

**Acceptance checks:** 3/3 tests pass.
**Closeout criteria:** Micro-step COMPLETE.

---

### TC-MA2-VERIFY-001 — End-to-End Verification

```yaml
parent_taskcard_id: TC-MA2-VERIFY-001
type: PARENT
status: BLOCKED
unblocks_when: TC-MA2-PIPE-001 + TC-MA2-SIGNAL-001 + TC-MA2-SKIP-001 + TC-MA2-VAL-001 + TC-MA2-LOCK-001 all CLOSED
requirements: [REQ-VERIFY-001, REQ-VERIFY-002]
parent_acceptance_criteria:
  - All 8 sub-checks produce PASS results
  - Results written to reports/machinery-assurance/verify-ma2-results.yaml
```

**Children and micro-steps (compact format):**

#### TC-MA2-VERIFY-001-01 — Run Supervisor Test Suite
```
MS-VERIFY-001-01-01  PENDING
Command: .venv/Scripts/pytest tests/supervisor/ -x -q 2>&1 | tee /tmp/verify-tests.txt
Expected: Exit 0, 0 failures  |  Evidence: /tmp/verify-tests.txt
```

#### TC-MA2-VERIFY-001-02 — Inspect next-sprint.md Task IDs vs next-work-items.json
```
MS-VERIFY-001-02-01  PENDING
Command: python tools/supervisor/generate_supervisor_packet.py
Expected: next-sprint.md regenerated

MS-VERIFY-001-02-02  PENDING
Command: python -c "
import json; items=json.load(open('.local/supervisor/next-work-items.json'))['items']
ids=[i['item_id'] for i in items[:5]]; sprint=open('reports/supervisor/next-sprint.md').read()
matches=[id for id in ids if id in sprint]; print(f'{len(matches)} matches: {matches}')
assert matches, 'NO item_ids in next-sprint.md!'
"
Expected: >=1 match
```

#### TC-MA2-VERIFY-001-03 — Check Signal Coherence on Disk
```
MS-VERIFY-001-03-01  PENDING
Command: python -c "
import json,sys; sys.path.insert(0,'tools/supervisor')
from signal_coherence import validate_signal_coherence
sig=json.load(open('.local/supervisor/continuation-signal.json'))
issues,_=validate_signal_coherence(sig)
assert not issues, f'Signal incoherent: {issues}'
print('OK')
"
Expected: OK
```

#### TC-MA2-VERIFY-001-04 — Run check_continuation.py
```
MS-VERIFY-001-04-01  PENDING
Command: python tools/supervisor/check_continuation.py 2>&1 | tee /tmp/verify-continuation.txt
Expected: verdict=CONTINUE, exit 0, no [COHERENCE] warnings
```

#### TC-MA2-VERIFY-001-05 — Run Governance Runner and Check Count
```
MS-VERIFY-001-05-01  PENDING
Command: python -c "
import sys; sys.path.insert(0,'tools/supervisor')
from governance_validator_runner import run_all_governance_validators
r=run_all_governance_validators({'changed_files':[],'planned_work_items':[]})
print('expected_count:',r['expected_count'],'ran_count:',r['ran_count'],'skipped:',r['skipped_count'])
fails=[v for v in r['validators'] if v['result']=='FAIL' and 'V_COUNT' in v.get('validator','')]
assert not fails, f'Count enforcement FAIL: {fails}'
print('OK')
"
Expected: OK, skipped_count<=2
```

#### TC-MA2-VERIFY-001-06 — Read Both Lock Files and Compare Status
```
MS-VERIFY-001-06-01  PENDING
Command: python -c "
import json,glob
shared=json.load(open('.local/supervisor/active-plan-lock.json'))
for kf in glob.glob('.local/supervisor/plan-locks/*.json'):
    k=json.load(open(kf))
    if k.get('status')!=shared.get('status'):
        print(f'MISMATCH: shared={shared[\"status\"]}, keyed={k[\"status\"]} in {kf}')
    else:
        print(f'OK: {kf[-20:]} status={k[\"status\"]}')
"
Expected: All relevant locks have matching status
```

#### TC-MA2-VERIFY-001-07 — Check Skip Ledger Exists
```
MS-VERIFY-001-07-01  PENDING
Command: python -c "from pathlib import Path; p=Path('.local/supervisor/closeout-skip-ledger.jsonl'); print('EXISTS' if p.exists() else 'MISSING')"
Expected: EXISTS
```

#### TC-MA2-VERIFY-001-08 — Write verify-ma2-results.yaml
```
MS-VERIFY-001-08-01  PENDING
Action: Write reports/machinery-assurance/verify-ma2-results.yaml
Content: check name, command, expected, actual, PASS/FAIL for checks 01-07
Completion check: File written with all 7 checks documented and all PASS
```

**Parent closeout criteria:** All 8 children CLOSED; verify-ma2-results.yaml written with all PASS.

---

### TC-MA2-PILOT-001 — Both Outputs Agree on Work Selection

```yaml
parent_taskcard_id: TC-MA2-PILOT-001
type: PARENT
status: BLOCKED (on TC-MA2-VERIFY-001)
requirements: [REQ-PILOT-001]
```

#### TC-MA2-PILOT-001-01 — Run autonomous_cycle
```
MS-PILOT-001-01-01  PENDING
Command: python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/pilot-001/evidence-declaration.yaml
Expected: Exit 0 or 3
Completion check: .local/supervisor/next-work-items.json mtime updated
```

#### TC-MA2-PILOT-001-02 — Assert next-sprint.md item_ids in next-work-items.json
```
MS-PILOT-001-02-01  PENDING
Command: python -c "
import json; nwi=json.load(open('.local/supervisor/next-work-items.json'))
ids=set(i['item_id'] for i in nwi.get('items',[])); sprint=open('reports/supervisor/next-sprint.md').read()
matches=[id for id in ids if id in sprint]; assert matches,'NO item_ids match!'; print(len(matches),'matches')
"
Expected: >=1 match
```

#### TC-MA2-PILOT-001-03 — Assert No Fixture Path in next-sprint.md
```
MS-PILOT-001-03-01  PENDING
Command: python -c "
text=open('reports/supervisor/next-sprint.md').read()
assert 'poc-gap-extraction' not in text,'fixture found!'
assert '.supervisor/fixtures' not in text,'fixture path found!'
print('OK: no fixture references')
"
Expected: OK
```

**Parent closeout criteria:** All 3 children CLOSED.

---

### TC-MA2-PILOT-002 — Signal Incoherence Detected and Corrected at Write

```yaml
parent_taskcard_id: TC-MA2-PILOT-002
type: PARENT
status: BLOCKED (on TC-MA2-VERIFY-001)
requirements: [REQ-PILOT-002]
```

#### TC-MA2-PILOT-002-01 — Write Incoherent Signal to Disk
```
MS-PILOT-002-01-01  PENDING
Command: python -c "
import json; from pathlib import Path
sig={'autonomous_continue':True,'stop_reason':'critical_rework_blocks_continuation','rework_items':[],'hard_stops_detected':[],'continuation_state':'YES_EXPLICIT_USER_AUTH'}
Path('.local/supervisor/continuation-signal.json').write_text(json.dumps(sig,indent=2))
print('Incoherent signal written')
"
```

#### TC-MA2-PILOT-002-02 — Run Signal Write Path with Incoherent Fields
```
MS-PILOT-002-02-01  PENDING
Command: python -c "
import json,sys; sys.path.insert(0,'tools/supervisor')
from signal_coherence import validate_signal_coherence
from pathlib import Path
sp=Path('.local/supervisor/continuation-signal.json')
sig=json.loads(sp.read_text()); issues,corrected=validate_signal_coherence(sig)
for i in issues: print(f'[SIGNAL_COHERENCE] Corrected: {i}',file=sys.stderr)
sp.write_text(json.dumps(corrected,indent=2)+'\n')
print('Done')
" 2>&1
Expected: stderr shows [SIGNAL_COHERENCE] Corrected: at least 1 issue
```

#### TC-MA2-PILOT-002-03 — Assert Corrected Signal on Disk
```
MS-PILOT-002-03-01  PENDING
Command: python -c "
import json; sig=json.load(open('.local/supervisor/continuation-signal.json'))
assert sig.get('stop_reason') is None,f'Not cleared: {sig.get(\"stop_reason\")}'
assert sig.get('autonomous_continue') is True
print('OK: signal coherent')
"
```

#### TC-MA2-PILOT-002-04 — Run check_continuation.py and Assert CONTINUE
```
MS-PILOT-002-04-01  PENDING
Command: python tools/supervisor/check_continuation.py
Expected: exit 0, verdict=CONTINUE
```

**Parent closeout criteria:** All 4 children CLOSED.

---

### TC-MA2-PILOT-003 — Closeout Failure Produces Skip Record, Surfaces Next Sprint

```yaml
parent_taskcard_id: TC-MA2-PILOT-003
type: PARENT
status: BLOCKED (on TC-MA2-VERIFY-001)
requirements: [REQ-PILOT-003]
```

#### TC-MA2-PILOT-003-01 — Create Integration Test Mocking copy_cycle_summaries Failure
```
MS-PILOT-003-01-01  PENDING
Action: Create tests/supervisor/test_closeout_skip_integration.py
Test function: test_copy_cycle_summaries_failure_produces_skip_record
  - Mock copy_cycle_summaries to raise RuntimeError("mock failure")
  - Call closeout step
  - Assert closeout-skip-ledger.jsonl has entry for step_id "STEP-6-COPY-CYCLE"
  - Assert resolved=False
Command: .venv/Scripts/pytest tests/supervisor/test_closeout_skip_integration.py -v
Expected: 1/1 PASS
```

#### TC-MA2-PILOT-003-02 — Assert Cycle Exits 0 After Mock Failure
```
MS-PILOT-003-02-01  PENDING
Command: grep -A5 "copy_cycle_summaries" tools/supervisor/autonomous_cycle.py | grep "raise"
Expected: 0 matches (except block does not re-raise)
```

#### TC-MA2-PILOT-003-03 — Assert Skip Visible in session-resume.md
```
MS-PILOT-003-03-01  PENDING
Action: Write test skip entry then regenerate session-resume.md
Commands:
  python -c "import sys; sys.path.insert(0,'tools/supervisor'); from closeout_skip_ledger import record_skip; record_skip('PILOT-003','STEP-6-COPY-CYCLE','copy cycle summaries',Exception('mock'),'next-work-items.json stale','python tools/supervisor/autonomous_cycle.py --copy-only')"
  python tools/supervisor/generate_supervisor_packet.py
  grep "Outstanding Skipped" reports/supervisor/session-resume.md
Expected: Section header found
```

**Parent closeout criteria:** All 3 children CLOSED.

---

### TC-MA2-PILOT-004 — Second Full Run, Zero Material Changes

```yaml
parent_taskcard_id: TC-MA2-PILOT-004
type: PARENT
status: BLOCKED (on ALL repair TCs CLOSED)
requirements: [REQ-PILOT-004]
```

#### TC-MA2-PILOT-004-01 — Hash Key Outputs After First Run
```
MS-PILOT-004-01-01  PENDING
Command: python -c "
import json,hashlib,re
def hash_file(p):
    text=open(p,encoding='utf-8',errors='replace').read()
    text=re.sub(r'\"20\d{2}-\d{2}-\d{2}T[^\"]+\"','\"TS\"',text)
    return hashlib.sha256(text.encode()).hexdigest()[:16]
for f in ['.local/supervisor/next-work-items.json','reports/supervisor/next-sprint.md','.local/supervisor/continuation-signal.json']:
    try: print(f.split('/')[-1], hash_file(f))
    except Exception as e: print(f.split('/')[-1],'ERROR:',e)
"
Record: 3 hashes
```

#### TC-MA2-PILOT-004-02 — Re-Run generate_supervisor_packet.py
```
MS-PILOT-004-02-01  PENDING
Command: python tools/supervisor/generate_supervisor_packet.py
Expected: next-sprint.md regenerated
```

#### TC-MA2-PILOT-004-03 — Compare Hashes
```
MS-PILOT-004-03-01  PENDING
Action: Recompute hashes with same script as PILOT-004-01
Expected: next-sprint.md hash identical to PILOT-004-01 value
Completion check: Material content unchanged; only timestamp fields (already stripped) differ
```

**Parent closeout criteria:** All 3 children CLOSED. `MATERIAL_SECOND_RUN_CHANGES = 0`

---

### TC-MA2-FINAL-001 — Independent Review and Closure Gate

```yaml
parent_taskcard_id: TC-MA2-FINAL-001
type: PARENT
status: BLOCKED (on ALL PILOTS CLOSED)
```

#### TC-MA2-FINAL-001-01 — Collect All Counter Values
```
MS-FINAL-001-01-01  PENDING
Action: Re-run each verification check from VERIFY-001 and record results
Completion check: All 8 check results collected and documented
```

#### TC-MA2-FINAL-001-02 — Verify All Counters Are Zero
```
REQUIRED_COUNTERS:
  SPRINT_PROMPT_SOURCES_DIVERGE_FROM_WORK_ITEMS: 0
  FIXTURE_FALLBACK_CODE_REACHABLE: 0
  SIGNAL_INCOHERENCE_ON_DISK: 0
  CLOSEOUT_SKIP_WITHOUT_SKIP_RECORD: 0
  VALIDATOR_COUNT_UNENFORCED_AT_RUNTIME: 0
  LOCK_FILES_INCONSISTENT_AFTER_WRITE: 0
  PILOTS_FAILING: 0
  MATERIAL_SECOND_RUN_CHANGES: 0

MS-FINAL-001-02-01  PENDING
Action: Evaluate each counter based on VERIFY-001 and PILOT evidence
Expected: All counters = 0
Completion check: Written assertion list with evidence reference for each counter
```

#### TC-MA2-FINAL-001-03 — Write final-report-ma2.md
```
MS-FINAL-001-03-01  PENDING
Action: Write reports/machinery-assurance/final-report-ma2.md
Required content:
  - Mission: bubbly-dancing-pony
  - Root causes addressed (W1-W5 with corrections noted)
  - Files changed (list all modified files)
  - Counter table (all zeros with evidence references)
  - Deferred items table
  - Verdict: MACHINERY_AND_OUTPUTS_PRODUCTION_READY_VERIFIED_AND_IDEMPOTENT
```

#### TC-MA2-FINAL-001-04 — Evidence Declaration and Supervisor + Terminal Lock
```
MS-FINAL-001-04-01  PENDING
Action: Write .local/evidences/bubbly-dancing-pony/evidence-declaration.yaml
Fields: mission, changed_files list, planned_work_items (one per TC closed), test results

MS-FINAL-001-04-02  PENDING
Command: python tools/supervisor/sprint_executor_validate.py .local/evidences/bubbly-dancing-pony/evidence-declaration.yaml --repair
Expected: Exit 0 or auto-repairs applied

MS-FINAL-001-04-03  PENDING
Command: python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/bubbly-dancing-pony/evidence-declaration.yaml
Expected: Exit 0 or 3

MS-FINAL-001-04-04  PENDING
Command: python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/bubbly-dancing-pony.md --terminal --audit-gate
Expected: TERMINAL_CLOSED written
*** STOP IMMEDIATELY AFTER THIS STEP ***
Report completion to user. Do NOT read next-sprint.md or start ledger work.
POST_PLAN_TERMINAL rule applies (CLAUDE.md §Plan Lock).
```

**Parent closeout criteria:** All 4 children CLOSED. Plan lock = TERMINAL_CLOSED.

---

## EXECUTION DAG

```yaml
execution_dag:
  phase_1_parallel_safe_repair:
    # These 5 TCs touch different files and can run in parallel
    # EXCEPTION: SIGNAL-001 and SKIP-001 both touch autonomous_cycle.py
    #   Execute SIGNAL-001 (signal section, lines ~2140-2210) first,
    #   then SKIP-001 (closeout except blocks, different line range) to avoid conflict
    - TC-MA2-PIPE-001     # generate_supervisor_packet.py lines 624-703
    - TC-MA2-SIGNAL-001   # autonomous_cycle.py ~2140-2210 + signal_coherence.py (new)
    - TC-MA2-SKIP-001     # closeout_skip_ledger.py (new) + autonomous_cycle.py closeout
    - TC-MA2-VAL-001      # governance_validator_runner.py lines 800-816 + MEMORY.md
    - TC-MA2-LOCK-001     # write_plan_lock.py lines 427-469

  execution_order_for_autonomous_cycle_edits:
    # autonomous_cycle.py has two edit sites:
    # 1. Signal coherence block (SIGNAL-001, ~line 2200) — execute first
    # 2. Closeout except blocks (SKIP-001, Steps 4-6) — execute second
    sequential:
      - TC-MA2-SIGNAL-001
      - TC-MA2-SKIP-001

  phase_2_verification:
    depends_on: all phase_1 CLOSED
    - TC-MA2-VERIFY-001

  phase_3_pilots:
    depends_on: TC-MA2-VERIFY-001 CLOSED
    parallel_safe:
      - TC-MA2-PILOT-001
      - TC-MA2-PILOT-002
      - TC-MA2-PILOT-003
    sequential_after_pilots_001_002_003:
      - TC-MA2-PILOT-004

  phase_4_closeout:
    depends_on: all pilots CLOSED
    - TC-MA2-FINAL-001

file_ownership:
  generate_supervisor_packet.py: TC-MA2-PIPE-001 (lines 624-703), TC-MA2-SKIP-001-04 (session-resume section)
  autonomous_cycle.py: TC-MA2-SIGNAL-001 (signal write section), TC-MA2-SKIP-001 (closeout except blocks)
  governance_validator_runner.py: TC-MA2-VAL-001 (lines 800-816)
  write_plan_lock.py: TC-MA2-LOCK-001 (lines 427-469; preserve 474-485)
  check_continuation.py: TC-MA2-SIGNAL-001-04 (3 diagnostic lines after signal load)
  signal_coherence.py: TC-MA2-SIGNAL-001-02 (new file)
  closeout_skip_ledger.py: TC-MA2-SKIP-001-01 (new file)
  MEMORY.md: TC-MA2-VAL-001-03 (one line)
```

---

## TASKCARD STATE MACHINE

```yaml
parent_states: [PROPOSED, READY, IN_PROGRESS, CHILDREN_IN_PROGRESS, INTEGRATION_PENDING, VERIFIED, SCORED, CLOSED, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON, REROUTED]
child_states: [TODO, READY, IN_PROGRESS, IMPLEMENTED, VERIFIED, SCORED, CLOSED, REROUTED, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]
micro_step_states: [PENDING, READY, ACTIVE, COMPLETE, FAILED, BLOCKED, SKIPPED_NOT_APPLICABLE]

invalid_transitions:
  - TODO → CLOSED
  - READY → CLOSED
  - IMPLEMENTED → CLOSED
  - parent CLOSED while any mandatory child not CLOSED
  - REROUTED → CLOSED without re-execution and re-verification
  - micro-step SKIPPED_NOT_APPLICABLE without reason recorded

quality_threshold:
  minimum_score: 4/5
  below_threshold: REROUTED
  dimensions: [requirement_correctness, implementation_correctness, scope_discipline, validation_strength, evidence_completeness, regression_safety]
```

---

## EVIDENCE CONTRACT

```yaml
evidence_root: .local/evidences/bubbly-dancing-pony/
primary_declaration: .local/evidences/bubbly-dancing-pony/evidence-declaration.yaml

per_parent_evidence:
  TC-MA2-PIPE-001: tests/supervisor/test_generate_supervisor_packet_pipe.py (3/3 PASS); reports/supervisor/next-sprint.md (WI-GAP-* present)
  TC-MA2-SIGNAL-001: tests/supervisor/test_signal_coherence.py (5/5 PASS); .local/supervisor/continuation-signal.json (coherent)
  TC-MA2-SKIP-001: tests/supervisor/test_skip_ledger.py (4/4 PASS); reports/supervisor/session-resume.md (Outstanding Skipped section)
  TC-MA2-VAL-001: tests/supervisor/test_validator_count_enforcement.py (3/3 PASS)
  TC-MA2-LOCK-001: tests/supervisor/test_lock_grouped_write.py (3/3 PASS)
  TC-MA2-VERIFY-001: reports/machinery-assurance/verify-ma2-results.yaml (all PASS)
  TC-MA2-FINAL-001: reports/machinery-assurance/final-report-ma2.md

evidence_must_not_contain:
  - alternative execution instructions
  - competing plan paths
  - references to any other plan as authoritative for this sprint
```

---

## VALIDATION MATRIX

| TC-ID | Check | Command | Expected |
|---|---|---|---|
| PIPE-001-03 | Syntax | `python -m py_compile tools/supervisor/generate_supervisor_packet.py` | exit 0 |
| PIPE-001-05 | Unit | `.venv/Scripts/pytest tests/supervisor/test_generate_supervisor_packet_pipe.py -v` | 3/3 PASS |
| PIPE-001-05 | Integration | `grep "WI-GAP" reports/supervisor/next-sprint.md` | ≥1 match |
| PIPE-001-05 | Regression | `.venv/Scripts/pytest tests/supervisor/ -x -q` | 0 failures |
| SIGNAL-001-02 | Unit | `.venv/Scripts/pytest tests/supervisor/test_signal_coherence.py -v` | 5/5 PASS |
| SIGNAL-001-04 | Diagnostic | `python tools/supervisor/check_continuation.py 2>&1 \| grep COHERENCE` | present when incoherent |
| SIGNAL-001-05 | State | `python tools/supervisor/check_continuation.py` | CONTINUE, no COHERENCE |
| SKIP-001-01 | Unit | `.venv/Scripts/pytest tests/supervisor/test_skip_ledger.py -v` | 4/4 PASS |
| SKIP-001-04 | Integration | `grep "Outstanding Skipped" reports/supervisor/session-resume.md` | section found |
| VAL-001-02 | Unit | `.venv/Scripts/pytest tests/supervisor/test_validator_count_enforcement.py -v` | 3/3 PASS |
| VAL-001-02 | Integration | count enforcement script | skipped_count<=2, no V_COUNT FAIL |
| LOCK-001-04 | Unit | `.venv/Scripts/pytest tests/supervisor/test_lock_grouped_write.py -v` | 3/3 PASS |
| VERIFY-001 | End-to-end | all 8 sub-checks | all PASS |
| PILOT-001 | Agreement | NWI item_ids in next-sprint.md | ≥1 match |
| PILOT-002 | Correction | Signal corrected at write | stop_reason=None |
| PILOT-003 | Skip record | Skip in session-resume.md | section present |
| PILOT-004 | Idempotency | Hash comparison | next-sprint.md hash equal on rerun |

---

## Critical Files with Specific Change Sites

| File | Change Site | Change |
|---|---|---|
| [tools/supervisor/generate_supervisor_packet.py](tools/supervisor/generate_supervisor_packet.py) | Lines 624-703 | Replace task loading with NWI reader; remove fixture fallback |
| [tools/supervisor/autonomous_cycle.py](tools/supervisor/autonomous_cycle.py) | Before atomic_write_json(signal_path) ~line 2207 | Insert signal coherence check (6 lines) |
| [tools/supervisor/autonomous_cycle.py](tools/supervisor/autonomous_cycle.py) | Steps 4a/4b/6 except blocks | Replace WARNING prints with skip ledger record_skip calls |
| [tools/supervisor/check_continuation.py](tools/supervisor/check_continuation.py) | After signal load, before Check 2 (~line 399) | Add coherence diagnostic (6 lines, read-only) |
| [tools/supervisor/governance_validator_runner.py](tools/supervisor/governance_validator_runner.py) | After skipped_count line 801 | Add count enforcement block |
| [tools/supervisor/write_plan_lock.py](tools/supervisor/write_plan_lock.py) | Lines 427-469 (preserve 474-485) | Replace sequential writes with _write_both_locks() call |
| [tools/supervisor/signal_coherence.py](tools/supervisor/signal_coherence.py) | New file | validate_signal_coherence() function |
| [tools/supervisor/closeout_skip_ledger.py](tools/supervisor/closeout_skip_ledger.py) | New file | record_skip(), get_outstanding_skips(), mark_resolved() |
| memory/MEMORY.md | Governance validators entry | Update 165→167 |

---

## EXECUTION HANDOFF

**Authoritative plan:** `plans/.claude/bubbly-dancing-pony.md` (in-repo)

**Execution agent checklist (mandatory before first micro-step):**

```
[ ] 1. Copy plan to plans/.claude/bubbly-dancing-pony.md (CLAUDE.md Step 0)
[ ] 2. Run: python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/bubbly-dancing-pony.md
[ ] 3. Read entire plan including all factual corrections
[ ] 4. Read FACTUAL CORRECTIONS section — especially CORRECTION-001 (SIGNAL target is autonomous_cycle.py)
[ ] 5. Start with investigation children first (TC-MA2-PIPE-001-01, TC-MA2-SIGNAL-001-01, etc.)
[ ] 6. Execute one micro-step at a time
[ ] 7. Capture evidence immediately after each micro-step
[ ] 8. Run validation command before marking child VERIFIED
[ ] 9. Close parent only after ALL mandatory children are CLOSED
[ ] 10. Proceed to VERIFY-001 only after all 5 repair parents CLOSED
[ ] 11. Proceed to pilots only after VERIFY-001 CLOSED
[ ] 12. After TC-MA2-FINAL-001-04: run --terminal and STOP
```

**Must NOT:**
- Skip micro-steps silently (use SKIPPED_NOT_APPLICABLE with reason)
- Close parent before all mandatory children
- Treat code existence as passing proof (run the validation command)
- Choose work from next-sprint.md while this plan is active
- Proceed past PILOT-004 without MATERIAL_SECOND_RUN_CHANGES = 0
- Start any product deepening or ledger work after TERMINAL_CLOSED

**First valid parent:** TC-MA2-PIPE-001 (parallel with SIGNAL-001, VAL-001, LOCK-001; before SKIP-001)
**First valid child:** TC-MA2-PIPE-001-01
**First micro-step:** MS-PIPE-001-01-01 — Read generate_supervisor_packet.py lines 600-760

---

## Honest Assessment of Limits

**What this sprint fixes:**
The divergence between sprint prompt and governed work items (the primary consistency
failure). Signal incoherence at write time. Invisible closeout failures. Silent validator
coverage drift. Partially mitigated lock asymmetry.

**What it does not fix:**
The fundamental problem — 12+ state files with no atomic coordination — remains after
this sprint. The consistency improvement is real but bounded. When closeout steps fail
in combination (compiler AND copy both fail), the system is still in an unknown state
that the skip ledger records but cannot automatically repair.

**Where the risk lies:**
TC-MA2-PIPE-001 is the highest-risk change. It changes the content of `next-sprint.md`
for every sprint from this point forward. This is correct behavior (governed gaps are
the authority), but changes the observable output of every subsequent sprint.

TC-MA2-SIGNAL-001 targets `autonomous_cycle.py` which is near LOC cap. Change is
small (6 lines), but the file is critical — must be compiled-verified after edit.

TC-MA2-SKIP-001 adds two separate edits to `autonomous_cycle.py`. Execute SIGNAL-001
edits first (signal section), then SKIP-001 edits (closeout section), and compile-verify
after each to prevent overlapping changes.

**Explicitly deferred:**

| Deferred | Why | When |
|---|---|---|
| SQLite-backed state store | Correct long-term fix; high migration risk | Dedicated migration sprint |
| Self-registering validator architecture | Requires validator-module refactor | After count stabilizes |
| True two-file atomic lock | Requires WAL; residual race after grouped-write | SQLite migration sprint |
| `_fix_yaml_aliases()` stub | Misleading name; functionally handled post-parse | Next validation refactor |
| `copy_cycle_summaries` race with concurrent runs | One-Mechanism-Lock is policy | Separate enforcement sprint |

**Evidence location:** `.local/evidences/bubbly-dancing-pony/evidence-declaration.yaml`

---

## FINAL VERDICT

```
VERDICT: PLAN_MICRO_TASKCARDIZED_READY_FOR_EXECUTION

Active Plan:
  authoritative path: plans/.claude/bubbly-dancing-pony.md
  authority source: plan_mode_system_reminder
  duplicate active plans: none
  competing plan versions: none

Plan Analysis:
  sections analyzed: 17
  actionables extracted: 11 parent TCs, 47 child TCs
  micro-steps defined: 92
  investigation children created: PIPE-01, SIGNAL-01, SKIP-02, LOCK-01
  factual corrections applied: 3 (CORRECTION-001 through 003)

Decomposition quality:
  every original TC decomposed: yes
  smallest-step test applied: yes (each MS has 1 action, 1 output, 1 check)
  scope-drift controls: parent/child/MS all have allowed/forbidden scope
  dependency order: documented in execution DAG

Single Plan Authority:
  one authoritative plan: yes
  competing versions: none
  supporting artifacts non-authoritative: yes (all embedded as plan sections)

Next valid parent: TC-MA2-PIPE-001 (parallel with SIGNAL-001, VAL-001, LOCK-001)
Next valid child: TC-MA2-PIPE-001-01
First micro-step: MS-PIPE-001-01-01
```

# Format Factory Self-Healing / Autonomous Improvement — Revised Plan
**Plan ID:** swift-chasing-thacker
**Type:** investigation_findings_revised
**Date:** 2026-06-26 (revised from 2026-06-25 original)
**Status:** REVISED_READY_FOR_REVIEW

---

## A. Current-State Reassessment

### What changed since the previous plan

The original plan (2026-06-25) was produced from an Explore-agent investigation. On re-inspection (2026-06-26), several items were found to be **already implemented** or **stale**. Recent sprint activity (S103–S117 in git log) has been exclusively .NET format deepening (FODS/FODT/CSV/ZST/NDJSON/TSV exporters, stream load, computed properties). No recent changes to Python supervisor infrastructure.

**Confirmed changes since original plan:**
- `gap_verification_engine.py` exists and is wired into `autonomous_cycle.py` Step 3a-verify (post-gap-closure verification was listed as "proposed" but is **fully implemented**).
- `failure_memory.py` read path exists in `generate_next_worker_prompt.py`, `autonomous_task_generator.py`, and `ai_learning_loop.py` — the plan's claim of "write-only" was **incorrect**.
- `workbook_document.py` and `config_document.py` are no longer in `src/python/` — analytics masquerade files were **already cleaned** (`GAP-PROD-INV-MASQ-001` reclassified as governance-debt-deferred).
- Governance validator test count has grown from 92 → **137 tests** (V48–V50 additions).
- `failure-memory.json` has **29 failures, 18 escalated** (high escalation rate — not called out in original plan).
- `.local/llm-call-logs/` has **122 JSON log files** but all are test-only invocations; `maturity-signal.json` has no `llm_used` field (the field never existed; the plan's reference to it was stale).

---

## B. Item-by-Item Status of the Previous Plan

### Item 1: Governance validators LOC ceiling
**Status: PARTIALLY SOLVED — STILL CONSTRAINED**

- `governance_validators.py`: **3,177 / 3,179 lines** (2 LOC headroom).
- `governance_validator_utils.py` already **exists** (152 LOC) — prior extraction was done but left only 2 lines of headroom.
- Baseline caps from `registry/source-structure-baseline.json`: loc_cap = 3179, functions_cap = 54, current functions = 50 (4 remaining).
- **What remains:** 2 LOC and 4 function slots remaining. Any new validator must either (a) extract another block to a new file, or (b) fit in ≤2 lines/1 function. Practically, this file cannot receive new validators without extraction.

### Item 2: gap_ledger_ref requirement
**Status: PARTIALLY SOLVED — TC-GUARD-001 enforces conditional requirement**

- `autonomous_cycle.py` lines 1110–1142: merges `gap_ledger_ref` from work items into declarations.
- `supervisor-worker-contract.md` lines 69–73: TC-GUARD-001 AND rule (SAL-HEAL-A001) requires every PRODUCT_SOURCE/PRODUCT_TEST item to have BOTH a gap reference (`gap_ledger_ref` OR `capability_ref`) AND spec authority (`spec_fact_refs` OR `exception_classification`).
- `autonomous_cycle.py` line ~878: TC-GUARD-001 BLOCK mode adds violating items to `rework_items`.
- **What remains:** The enforcement exists. Gap closure is conditional on having both fields. No additional schema-level enforcement is strictly necessary (the rework_items block already prevents closure without the field).

### Item 3: Grading history deduplication
**Status: UNRESOLVED — APPEND-ONLY, NO DEDUP**

- `reports/supervisor/grading-history.jsonl`: **715 lines**, opened in `"a"` append mode.
- `autonomous_cycle.py` lines 1633–1654: writes entry for every cycle unconditionally; no sprint_id check before write.
- Duplicate sprint_ids confirmed in file (e.g., `PRODUCT-DEEPENING-SPRINT-47-20260616` appears twice).
- **What remains:** Need to check sprint_id before appending to prevent duplicate entries on same-sprint reruns.

### Item 4: Post-gap-closure verification
**Status: FULLY SOLVED — remove from plan**

- `tools/supervisor/gap_verification_engine.py` exists (4,239 bytes, created 2026-06-24).
- 3-level verification framework (Level 0: file exists, Level 1: tests pass, Level 2: evidence chain) is wired.
- `autonomous_cycle.py` lines 1166–1172: calls `verify_closed_gaps()` in Step 3a-verify.
- 1,202 gap entries in `gap-ledger.json` carry `suggested_verification` commands.
- **No work needed.**

### Item 5: failure_memory read path
**Status: ALREADY IMPLEMENTED — plan claim was STALE**

- `failure_memory.py`: `find_escalated()`, `find_unresolved()`, `load_excluded_gap_ids()` are read-path methods.
- `generate_next_worker_prompt.py`: calls `load_excluded_gap_ids()` to exclude known-failing gaps from next sprint queue.
- `autonomous_task_generator.py`: calls `find_escalated()` and `find_unresolved()`.
- `ai_learning_loop.py`: uses failure memory to avoid task reselection.
- `autonomous_cycle.py` itself: write-only (records new failures but does not read), but the read path exists in task generation modules.
- **What remains:** `failure-memory.json` has 18 escalated entries — verify these are actually being excluded from task selection (functional end-to-end proof is missing; read path is implemented but unverified in production).

### Item 6: stop_reason_adjudicator wiring
**Status: UNRESOLVED BUT LOW PRIORITY — inline logic performs same function**

- `stop_reason_adjudicator.py` (49,214 bytes): correct logic, 19 signal categories, correct output decisions.
- `autonomous_cycle.py`: ZERO imports or calls to `stop_reason_adjudicator`. Only one comment at line 1872 referencing "Rule 6" from the adjudicator.
- `autonomous_cycle.py` lines 49–180: `classify_continuation_state()` function implements equivalent state machine inline.
- **Risk:** Inline logic may drift from adjudicator over time; no single source of truth.
- **What remains:** Wire adjudicator OR keep inline logic but remove the dead adjudicator to avoid confusion. Low urgency — inline logic works correctly today.

### Item 7: bounded_repair_engine post-repair re-validation
**Status: UNRESOLVED — no post-repair pytest call**

- `bounded_repair_engine.py` (16,646 bytes): `apply_repair()` returns `RepairResult` without re-running pytest.
- No integration with `failure_memory.py` in the repair engine.
- No re-validation loop after fix.
- **What remains:** After applying a repair, a targeted pytest call on the affected test file should verify the fix succeeded. Result should be written back to `failure_memory` as `correction_verified: true/false`.

### Item 8: LLM / professionalize production proof-of-use
**Status: UNRESOLVED — fully configured but functionally dormant**

- `tools/llm/endpoints.yaml`: professionalize endpoint declared (`https://llm.professionalize.com/v1`, model `gpt-oss`, embedding model `qwen3-embedding-8b`).
- `tools/supervisor/embedding_retrieval.py` (32,334 bytes): `HybridRetrievalPilot` implemented, NOT imported anywhere in autonomous_cycle.py or grade_declared_work.py.
- `tools/supervisor/grade_declared_work.py`: zero references to "embedding" or "HybridRetrieval".
- `.local/llm-call-logs/`: 122 JSON files, all test invocations. No production grading calls.
- `maturity-signal.json`: no `llm_used` field (field does not exist in schema).
- **What remains:** Wire `HybridRetrievalPilot` into `grade_declared_work.py` as a pre-grading context step. Requires `PROFESSIONALIZE_API_KEY` env var. First production proof-of-use undemonstrated.

### Item 9: Analytics masquerade files (16 files)
**Status: FULLY SOLVED — remove from plan**

- `workbook_document.py` and `config_document.py` not present in `src/python/` (only in build artifacts).
- `GAP-PROD-INV-MASQ-001` reclassified as `RECLASSIFIED_AS_GOVERNANCE_DEBT`.
- V77 governance validator blocks future analytics-masquerade `*_document.py` files.
- **No work needed.**

### Item 10: Run-history-informed prioritization
**Status: UNRESOLVED — static P0-P8 scoring only**

- `capability_feature_compiler.py`: static priority scoring (P0–P8 base + impact adjustments). No history-based adjustment.
- `grading-history.jsonl` (715 lines) has per-sprint verdicts available but not consumed by compiler.
- `autonomous_task_generator.py`: uses failure memory for exclusion, not for boosting failing-format priority.
- **What remains:** Read per-format verdict rates from `grading-history.jsonl` and feed them into `capability_feature_compiler.py` priority scoring.

---

## C. Remaining Problems

### Problem 1: Governance LOC ceiling blocks all new validators
**Root cause:** `governance_validators.py` is at 3,177 / 3,179 LOC (2 lines remaining). While `governance_validator_utils.py` was extracted earlier, it only freed ~152 LOC, and that headroom has since been consumed.
**Impact:** Cannot add V69 (LLM grading proof), V70 (failure learning verification), or any future governance rule without triggering GOV_BLOCK for all sprints.
**Evidence:** `registry/source-structure-baseline.json` baseline_loc_cap=3179, current 3177.

### Problem 2: LLM / embedding pipeline not wired into production grading
**Root cause:** `embedding_retrieval.py` (838 LOC) exists as a self-contained pilot but has no import from `autonomous_cycle.py` or `grade_declared_work.py`. All call logs are test-only.
**Impact:** LLM-assisted grading, context retrieval, and professionalize first proof-of-use remain undemonstrated. The system cannot improve grading quality with prior context.
**Evidence:** Zero grep matches for "HybridRetrieval" in `tools/supervisor/grade_declared_work.py`.

### Problem 3: bounded_repair_engine has no feedback loop
**Root cause:** `apply_repair()` returns result without re-running the failing test. No write-back to `failure_memory.py`.
**Impact:** Repairs cannot be verified to have worked. Failure memory can escalate a failure even after it was successfully repaired.
**Evidence:** `bounded_repair_engine.py` lines 138–207: repair ends at `return RepairResult(...)`.

### Problem 4: Grading history grows without deduplication
**Root cause:** `autonomous_cycle.py` opens `grading-history.jsonl` in `"a"` append mode with no sprint_id dedup check.
**Impact:** Reruns create duplicate entries; history metrics are skewed.
**Evidence:** `grading-history.jsonl` has 715 lines with confirmed duplicate sprint IDs.

### Problem 5: failure_memory escalation proof missing
**Root cause:** Read path is implemented in task generation modules but not verified to exclude escalated failures in practice. 18 of 29 recorded failures are marked `escalated=True` — if these are not being excluded from task selection, the system keeps retrying known-broken work.
**Evidence:** `failure-memory.json` has 18 escalated entries (62%); exclusion behavior unverified end-to-end.

---

## D. Revised Plan

### Priority order (dependency and risk)

**Tier 0 — Prerequisite (must happen first)**
| Task | What | Why |
|---|---|---|
| TC-GOV-CAP-002 | Extract validator group from `governance_validators.py` to `governance_validators_ext3.py` | Unblocks adding V69+ validators; 2 LOC remaining is too tight for any addition |

**Tier 1 — High impact, independent**
| Task | What | Why |
|---|---|---|
| TC-LLM-WIRE-001 | Wire `HybridRetrievalPilot` into `grade_declared_work.py` as pre-grading context step | First production proof-of-use of professionalize; improves grading quality |
| TC-REPAIR-LOOP-001 | Add post-repair re-validation in `bounded_repair_engine.apply_repair()` + write result to `failure_memory` | Closes self-healing proof loop; confirms repairs actually work |

**Tier 2 — Quality improvements**
| Task | What | Why |
|---|---|---|
| TC-HIST-DEDUP-001 | Add sprint_id dedup check in `autonomous_cycle.py` grading-history write | Prevents duplicate entries on reruns; cleans up history metrics |
| TC-FAIL-MEM-PROOF-001 | Add smoke test verifying escalated failure exclusion in task generator | Proves the failure learning read path is functioning end-to-end |

**Tier 3 — Optional / deferred**
| Task | Status | Reason to defer |
|---|---|---|
| stop_reason_adjudicator wiring | OPTIONAL | Inline logic works; integration is refactor-only, no behavioral gap |
| Run-history-informed prioritization | DEFERRED | Requires TC-HIST-DEDUP-001 first; lower risk than Tier 1 items |

---

### Detailed task descriptions

**TC-GOV-CAP-002** — Governance capacity restoration
- Files: `tools/supervisor/governance_validators.py`, new `tools/supervisor/governance_validators_ext3.py`, `tools/supervisor/governance_validator_runner.py`, `registry/source-structure-baseline.json`
- Action: Extract the largest cohesive validator group (likely V61–V68 spec-authority validators, ~200–250 LOC) into `governance_validators_ext3.py`; re-export from `governance_validators.py` for backward compat; update baseline cap.
- Acceptance: `governance_validators.py` drops to ≤2,950 LOC; all 137 governance tests pass; `run_all_governance_validators()` still registers all validators.
- Risk: LOW — same pattern as previous ext.py extractions.

**TC-LLM-WIRE-001** — First professionalize proof-of-use
- Prerequisite: `PROFESSIONALIZE_API_KEY` must be set in environment (user action).
- Files: `tools/supervisor/grade_declared_work.py`, `tools/supervisor/embedding_retrieval.py`, `tools/supervisor/autonomous_cycle.py`
- Action: Import `HybridRetrievalPilot` in `grade_declared_work.py`. Before each LLM grading call, call `pilot.find_similar(item_description, top_k=3)` to retrieve 3 prior similar items from grading history; include as context in grading prompt. Log to `.local/llm-call-logs/` with source chunks and similarity scores. Gracefully degrade if endpoint unavailable (fall through to Level 2).
- Acceptance: At least 1 sprint produces `llm_used: true` in a grading record. `.local/llm-call-logs/` contains a production call entry. Grading still works if professionalize is unreachable.
- Risk: MEDIUM — external dependency (professionalize endpoint). Must be fully fail-safe.

**TC-REPAIR-LOOP-001** — Post-repair re-validation
- Files: `tools/supervisor/bounded_repair_engine.py`, `tools/supervisor/failure_memory.py`
- Action: After `apply_repair()` succeeds for IMPORT_ERROR or NAME_ERROR failure classes, run `pytest <affected_test_file> --tb=short -q` as a targeted re-validation. Write outcome back to `failure_memory` as `last_repair_verified: true/false` and `last_repair_sprint_id`. If re-validation fails → call `rollback()`.
- Acceptance: `apply_repair()` method triggers pytest after IMPORT_ERROR fix; result appears in failure-memory.json for the repaired entry. `failure_memory.py` shows `last_repair_verified: true` for entries successfully re-validated.
- Risk: LOW — confined to repair engine, no changes to main cycle path.

**TC-HIST-DEDUP-001** — Grading history deduplication
- Files: `tools/supervisor/autonomous_cycle.py` (lines 1633–1654)
- Action: Before appending to `grading-history.jsonl`, read last N sprint_ids (scan from end of file); if current sprint_id already present, skip append (idempotent). Alternatively, use sprint_id + timestamp hash as dedup key.
- Acceptance: Running the same sprint twice produces only one entry in grading-history.jsonl for that sprint_id.
- Risk: LOW — additive check only.

**TC-FAIL-MEM-PROOF-001** — Failure memory exclusion smoke test
- Files: new test file `tests/supervisor/test_failure_memory_exclusion.py`
- Action: Unit test that: (1) populates failure-memory with 3+ occurrences of a gap_id; (2) calls `generate_next_worker_prompt.py` or `autonomous_task_generator.py`; (3) asserts the escalated gap_id does not appear in the generated work items.
- Acceptance: 1 new test passes confirming the read path is functional end-to-end.
- Risk: LOW — test-only addition.

---

### Prerequisites (external, not agent-executable)
- **PROFESSIONALIZE_API_KEY** + **PROFESSIONALIZE_BASE_URL** must be set in environment before TC-LLM-WIRE-001 can be demonstrated. This is a user action, not agent-executable.

---

### Verification (end-to-end)
After all Tier 0 and Tier 1 tasks complete, run:
1. `python tools/supervisor/autonomous_cycle.py autonomous-cycle --declaration <latest-evidence> --dry-run` — confirms governance validators all pass with new ext3 file
2. `python -m pytest tests/supervisor/test_governance_validators.py -v` — all 137 tests pass
3. `python -m pytest tests/supervisor/test_failure_memory_exclusion.py -v` — new test passes
4. Check `.local/llm-call-logs/` for a production entry with `authority_state: "ai_advisory"` and `from_cache: false`
5. `python -m pytest tests/supervisor/ -v` — full supervisor suite green

---

## E. Items Removed from Original Plan (Solved or Obsolete)

| Item | Reason Removed |
|---|---|
| Post-gap-closure verification | `gap_verification_engine.py` fully implemented and wired — no work needed |
| failure_memory.py read path (build from scratch) | Read path already exists in `generate_next_worker_prompt.py`, `autonomous_task_generator.py`, `ai_learning_loop.py` |
| Analytics masquerade files (16) | `workbook_document.py` / `config_document.py` not in `src/python/`; GAP reclassified as governance-debt-deferred |
| gap_ledger_ref schema-level requirement | TC-GUARD-001 BLOCK mode already enforces this conditionally — additional schema enforcement is redundant |
| Self-healing proof loop (build from scratch) | Partially exists via gap_verification_engine; remaining gap is only bounded_repair feedback (TC-REPAIR-LOOP-001) |


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-06-28T16:31:45.426184+00:00"
  locked_by: "b42c05efe582"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->

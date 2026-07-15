# Format Factory — Deep First-Principles Production Assessment

**Assessment date:** 2026-07-14
**Assessor:** Independent analysis with mechanical code tracing
**Evidence base:** Direct code path tracing, agent-assisted investigation across grading pipeline, state write mechanics, and sprint consistency patterns
**Method:** Every root cause is traced to specific code lines. Symptoms are distinguished from causes. No finding relies on prompt text alone.

---

## 1. Scope

- **System:** Format Factory — file format acquisition/conversion platform with autonomous AI agent supervision
- **Operational history:** 840 graded sprints, 3,287 evidence runs, 434 plan locks
- **Product surface:** 26 Python format packages (76,653 LOC), 9 .NET format directories (22,150 LOC)
- **Supervision surface:** 98,240 LOC supervisor infrastructure, 223 governance validators, 44,277 tests
- **Primary question:** What causes inconsistent results across reruns of the autonomous sprint system, and what would a production-grade fix look like?

---

## 2. Behavior Reconstruction: What the System Actually Does

The autonomous sprint loop executes this sequence:

```
check_continuation.py → evaluate 13+ stop conditions
    ↓ (CONTINUE)
Agent reads next-sprint.md → executes product/governance work
    ↓
Agent writes evidence-declaration.yaml (free-form, schema-optional)
    ↓
autonomous_cycle.py runs ~30 steps:
    Step 0-pre: validate declaration schema
    Step 1-3:   inspect evidence, materialize paths, run overclaim detector
    Step 4:     grade_declared_work.grade_all() — per-item grading
    Step 5-6:   write cycle manifest, copy summaries
    Step 7:     bridge to legacy format (evidence-review.json, contradictions.json)
    Step 7b:    generate_supervisor_packet → writes session-resume.md, approval-gates.md, next-sprint.md
    Step 8:     write continuation-signal.json (PRIMARY state write)
    Step 8+:    evidence_continuation.py repairs signal (NON-ATOMIC re-write)
    Post-8:     plan lock cleanup
    ↓
check_continuation.py → re-evaluate → loop or stop
```

The critical observation: **the system works** — 840 sprints ran, real product was produced, real tests pass, real governance is enforced. But the *consistency* of results across reruns is degraded by five mechanical failure modes detailed below.

---

## 3. Problem Separation

### Symptoms (visible effects, not root causes)

| # | Symptom | Evidence |
|---|---------|----------|
| S1 | 47% rework rate (394/840 sprints) | grading-history.jsonl |
| S2 | approval-gates.md says `AUTONOMOUS_CONTINUE: NO` while continuation-signal.json says `autonomous_continue: true` | Direct file inspection |
| S3 | continuation-signal.json contains `hard_stops_detected: ["critical_rework_blocks_continuation"]` with `rework_items: []` (empty) | Direct file inspection |
| S4 | 79% of last 100 sprints grade zero work items, each scored 0.85 quality | maturity-trend.json analysis |
| S5 | 178 uncommitted files in working tree | git status |
| S6 | 6.5:1 infrastructure-to-product LOC ratio | LOC counts |
| S7 | Evidence declarations vary wildly in schema (some have `evidence_artifacts`, some don't; mixed absolute/relative paths) | Three-declaration comparison |

### Root Causes (mechanical failures traced to code)

**RC-1: LLM availability is the primary nondeterminism source**

The grading pipeline produces different grades for the same evidence depending on whether the LLM is available:

- **With LLM available:** `semantic_verify_item()` ([grade_declared_work.py:442](tools/supervisor/grade_declared_work.py#L442)) calls the LLM, gets adequate/inadequate + confidence. If inadequate with confidence > 0.85, the grade is downgraded ([line 975](tools/supervisor/grade_declared_work.py#L975)). If adequate, the grade stands.

- **With LLM unavailable:** The function falls through to `grade_intermediate_verify.py` (AST-based, deterministic) or to the `fallback_llm_unavailable` path ([line 578](tools/supervisor/grade_declared_work.py#L578)), which returns `adequate=False, confidence=0.0`. The grade is then capped at ACCEPTED_WITH_LIMITATIONS ([line 962-964](tools/supervisor/grade_declared_work.py#L962)) but NOT downgraded.

- **Net effect:** Same evidence → ACCEPTED_VERIFIED (with LLM, adequate) OR ACCEPTED_WITH_LIMITATIONS (without LLM) OR ACCEPTED_WITH_LIMITATIONS→REWORK_REQUIRED (with LLM, inadequate + high confidence). Three possible outcomes for one input depending on LLM availability.

**RC-2: Confidence override dead band (0.80–0.85)**

When the LLM says "inadequate" with confidence between 0.80 and 0.85, nothing happens:

- [Line 553](tools/supervisor/grade_declared_work.py#L553): `if not result.get("adequate") and result.get("confidence", 0) < 0.80:` → override fires only below 0.80, flips adequate to True
- [Line 975](tools/supervisor/grade_declared_work.py#L975): `elif not sv.get("adequate") and sv.get("confidence", 0) > 0.85:` → downgrade fires only above 0.85

Between 0.80 and 0.85: the override at line 553 does NOT fire (confidence is ≥ 0.80), so adequate stays False. But the downgrade at line 975 does NOT fire either (confidence is ≤ 0.85). The LLM said "this evidence is inadequate" and the system... does nothing with that information.

This dead band is not an edge case — LLM confidence often clusters in the 0.75-0.90 range, putting a meaningful fraction of verdicts into the silent zone.

**RC-3: Three independent computations of `autonomous_continue`**

The state contradiction between approval-gates.md and continuation-signal.json (symptom S2) is not a bug — it's a design: the two files compute `autonomous_continue` from different inputs using different logic.

- **continuation-signal.json:** Computed by `autonomous_cycle.py` [lines 2338-2343](tools/supervisor/autonomous_cycle.py#L2338). Logic: `autonomous_continue = False` if hard_stops or overclaimed items exist; `"true_with_rework"` if rework items exist without overclaimed; otherwise, uses `manifest.autonomous_continue`.

- **approval-gates.md:** Computed by `generate_supervisor_packet.py` [line 1185](tools/supervisor/generate_supervisor_packet.py#L1185). Logic: reads `contradictions.get("autonomous_continue", True)` from contradictions.json. This is a separate computation from a separate data source.

- **check_continuation.py:** Has a cross-check at [line 489-495](tools/supervisor/check_continuation.py#L489) that attempts to reconcile the two, using approval-gates.md as authority for non-TRUE_EXTERNAL_GATE reasons. But this cross-check only covers the boolean value, not `iteration`, `session_id`, or `rework_items`.

**Result:** The signal says "continue with hard stops" (S3) because the `_sync_hard_stops_after_repair` function ([autonomous_cycle_utils.py:189](tools/supervisor/autonomous_cycle_utils.py#L189)) can clear the rework_items list after GOV_BLOCK rescan, but `continuation_reason_codes` still contains the pre-repair `HARD_STOP:critical_rework_blocks_continuation` and `hard_stops_detected` is not cleared. The signal captures pre-repair and post-repair state simultaneously.

**RC-4: 124 broad `except Exception` catches in autonomous_cycle.py mask failures**

Counted mechanically: autonomous_cycle.py contains 137 `except` clauses. Of these, 124 catch `Exception` broadly. 23 of those 124 silently `pass`. The remaining ~100 log a warning and continue.

This pattern means: any step in the 30-step pipeline can fail silently, producing partial outputs that become inputs to later steps. A grading step failure that returns an empty list looks identical to "zero work items" — both result in an ACCEPTED verdict (see RC-5).

**RC-5: Empty sprints score ACCEPTED with 0.85 quality**

[grade_declared_work.py:1052-1058](tools/supervisor/grade_declared_work.py#L1052): When `grades` is empty (no work items), the verdict computation falls through:
- `rejected` is empty → not REJECTED
- `overclaimed` is empty and `any(... REWORK_REQUIRED)` on empty list is False → not ACCEPTED_WITH_REWORK
- `all(... for g in grades)` on an empty list returns **True** in Python → verdict = ACCEPTED

Then [maturity_trend.py:25-37](tools/supervisor/maturity_trend.py#L25): `_verdict_score("ACCEPTED")` returns 0.85.

**Net effect:** 79% of the last 100 sprints grade zero items. Each gets 0.85 quality. The maturity trend score for the last 100 sprints is 0.828, which looks healthy but is almost entirely composed of empty sprints. The quality signal is meaningless.

### Structural Weaknesses (not directly causing inconsistency, but amplifying it)

**SW-1: Grade cache couples sprints across time**

The grade cache at `.local/supervisor/grade-cache.json` persists LLM verdicts for 7 days by evidence hash ([line 114](tools/supervisor/grade_declared_work.py#L114)). If the same evidence is submitted in sprint N and sprint N+5, the cached LLM result from sprint N is used. This is correct behavior IF the evidence is truly identical — but the hash includes file contents ([lines 94-101](tools/supervisor/grade_declared_work.py#L94)), so even a whitespace change invalidates the cache and produces a fresh LLM call, which may return a different verdict.

The LLM-unavailable fallback also caches, but with a `random.randint(0, 5)` minute jitter on the TTL ([line 576](tools/supervisor/grade_declared_work.py#L576)). This creates timing-dependent rerun behavior: two identical runs started 3 minutes apart may get different cache hits.

**SW-2: grading-history.jsonl is broken**

The `append_grading_history` function referenced at [autonomous_cycle.py:1977](tools/supervisor/autonomous_cycle.py#L1977) does not exist in `autonomous_cycle_extensions.py`. The import fails, caught by `except Exception` at line 1979, and silently skipped. Grading history has not been appended since this function was extracted. The existing 840 entries are historical; new sprints are not recorded. The maturity trend is stale.

**SW-3: Non-atomic re-write of continuation signal**

After the primary atomic write of continuation-signal.json at [line 2526](tools/supervisor/autonomous_cycle.py#L2526), `evidence_continuation.py` reads-modifies-writes the same file at [line 251](tools/supervisor/evidence_continuation.py#L251) using plain `Path.write_text()` — not atomic. A crash during this write can corrupt the signal file. Similarly, `check_continuation.py`'s auto-rollover at [line 514](tools/supervisor/check_continuation.py#L514) uses plain `write_text()`.

**SW-4: Broken zero-task circuit breaker**

The circuit breaker at [autonomous_cycle.py:1900-1925](tools/supervisor/autonomous_cycle.py#L1900) only fires on 3+ *consecutive* zero-task cycles. The actual pattern is non-consecutive: dotnet-deepening sprints produce zero items, then an interleaved LAYER-AUDIT sprint produces items and resets the counter. The counter never reaches 3. Additionally, the breaker only adds a warning — it never stops execution. Current counter state: `{"count": 0, "sprints": []}`.

**SW-5: Dual work selection paths**

`generate_next_worker_prompt.py` and `autonomous_task_generator.py` are parallel work selection authorities. The task generator contains `_EXPANSION_GOALS` — 114 hardcoded entries ([autonomous_task_generator.py](tools/supervisor/autonomous_task_generator.py)) — a separate task source from the gap-ledger-based items in `generate_next_worker_prompt.py`. Which path runs depends on which entry point was used.

**SW-6: Evidence declaration schema is not enforced**

The schema validator in [evidence_declaration.py:25-35](tools/supervisor/evidence_declaration.py#L25) declares 17 required fields, but declarations in practice omit many (evidence_root, evidence_artifacts, test_results, reports_created). The YAML loader returns None for missing keys. Path references mix absolute Windows paths and relative paths. Three recent declarations compared: field presence varies 40-60% between them.

---

## 4. What Breaks Consistency Across Reruns

Summarizing the five mechanisms that cause the same work to produce different outcomes on different runs:

| # | Mechanism | Code Location | Trigger | Effect |
|---|-----------|--------------|---------|--------|
| M1 | LLM availability | [grade_declared_work.py:442-585](tools/supervisor/grade_declared_work.py#L442) | LLM up vs. down | Same evidence → ACCEPTED_VERIFIED or ACCEPTED_WITH_LIMITATIONS or REWORK_REQUIRED |
| M2 | Confidence dead band | [grade_declared_work.py:553, 975](tools/supervisor/grade_declared_work.py#L553) | LLM confidence 0.80-0.85 | "Inadequate" verdict silently ignored |
| M3 | State write ordering | [autonomous_cycle.py:2060, 2526](tools/supervisor/autonomous_cycle.py#L2060) | Crash between Step 7b and Step 8 | approval-gates.md and continuation-signal.json disagree |
| M4 | Grade cache timing | [grade_declared_work.py:114, 576](tools/supervisor/grade_declared_work.py#L114) | 7-day TTL + random jitter | Cached vs. fresh LLM verdict for same evidence |
| M5 | Empty sprint acceptance | [grade_declared_work.py:1057](tools/supervisor/grade_declared_work.py#L1057) | `all()` on empty list | Zero-item sprints → ACCEPTED with 0.85 quality |

These mechanisms are **independent and multiplicative**. A single rerun can be affected by any combination.

---

## 5. What Should Be Preserved

### P-1: Product Source Code — PROVEN, PRESERVE

26 Python format packages with real parsing logic. FODS uses streaming iterparse with ODF namespace handling and defusedxml for XXE protection. SYLK parses record-type syntax. ZST validates RFC 8878. Near-zero stubs (1 intentional `NotImplementedError` across 76K LOC). 1,772 FODS tests pass in 11.4s. This is genuine production code.

### P-2: Oracle System — PROVEN, PRESERVE

26 oracle packages with real conformance checks. Anti-self-approval mechanism blocks `IMPLEMENTATION_OBSERVED` authority class. `execute_oracle.py` (2,240 LOC) is the most trustworthy verification layer in the system. Negative control tests validate oracle integrity.

### P-3: Governance Validators — PROVEN, PRESERVE

223 validators performing AST analysis, LOC cap enforcement, spec_qname verification, import direction checks. These catch real structural violations (337 tracked in source-structure-baseline.json, 15.5% GOV_BLOCK rate).

### P-4: check_continuation.py Safety Logic — PROVEN, PRESERVE

13+ carefully differentiated stop conditions with real defensive depth. Session isolation, plan lock management, structural GOV_BLOCK detection, collect-then-decide lock evaluation. This is well-designed safety logic that prevents real failure modes.

### P-5: Test Suite — PROVEN, PRESERVE

44,277 tests collected. Property-based tests, mutation hardening, security tests, malformed input tests. 3.5:1 test-to-source LOC ratio.

### P-6: Evidence Declaration Concept — PRESERVE, HARDEN

The structured evidence-declaration.yaml format with per-item grading is a genuine audit trail. The concept is sound; the schema enforcement needs hardening (see R-4).

---

## 6. What Must Be Redesigned

### R-1: Eliminate the confidence dead band

**Problem:** [grade_declared_work.py:553, 975](tools/supervisor/grade_declared_work.py#L553) — LLM "inadequate" verdicts with confidence 0.80-0.85 are silently dropped.

**Fix:** Unify the two thresholds. Either:
- (A) Lower the downgrade threshold at line 975 from 0.85 to 0.80 (closes the gap from the top), OR
- (B) Remove the confidence floor override at line 553 entirely — when the LLM says "inadequate," respect it regardless of confidence, and let the downstream logic at line 975 decide whether to act

Option (B) is more correct: the override at line 553 flips `adequate` from False to True, which means downstream code never sees the LLM's actual verdict. Removing line 553-555 preserves the LLM signal while the downgrade threshold at 975 still protects against very-low-confidence noise.

**Verification:** Re-grade the last 10 evidence declarations. Count how many items currently in the dead band would flip. Expect a modest increase in REWORK_REQUIRED verdicts — this is the correct behavior.

### R-2: Make LLM-absent grading deterministic and honest

**Problem:** When the LLM is unavailable, the fallback produces `adequate=False, confidence=0.0` ([line 578](tools/supervisor/grade_declared_work.py#L578)). This triggers grade capping (ACCEPTED_VERIFIED → ACCEPTED_WITH_LIMITATIONS) but doesn't downgrade other grades. The maturity trend treats this as normal ACCEPTED.

**Fix:**
1. Add a grade level: `UNVERIFIED` (between ACCEPTED and ACCEPTED_WITH_LIMITATIONS). Meaning: "deterministic checks passed, but LLM semantic verification was not available."
2. Map `UNVERIFIED` to a distinct quality score (e.g., 0.70) in maturity_trend.py — below ACCEPTED (0.85) but above ACCEPTED_WITH_REWORK (0.65).
3. Remove the `random.randint(0, 5)` jitter at [line 576](tools/supervisor/grade_declared_work.py#L576) — use a fixed TTL for failure cache entries.

**Verification:** Run grade_all with LLM disabled, then with LLM enabled, on the same evidence. UNVERIFIED vs. ACCEPTED_VERIFIED makes the difference visible rather than hidden.

### R-3: Fix empty sprint inflation

**Problem:** `all(condition for g in [])` returns True at [line 1057](tools/supervisor/grade_declared_work.py#L1057), causing zero-item sprints to be graded ACCEPTED.

**Fix:** Add an explicit empty-list guard before the verdict computation:

```python
if not grades:
    overall_verdict = "NO_ITEMS_DECLARED"
    autonomous_continue = True  # empty sprint is not a stop, but it's not ACCEPTED either
```

Map `NO_ITEMS_DECLARED` to quality score 0.0 in maturity_trend.py. This immediately deflates the trend and makes the 79% empty-sprint pattern visible.

**Verification:** The maturity trend's last-100 average will drop from 0.828 to approximately 0.18 (21 real sprints × 0.85 ÷ 100). This accurately reflects reality.

### R-4: Enforce evidence declaration schema

**Problem:** Declarations vary wildly in structure ([evidence_declaration.py:25-35](tools/supervisor/evidence_declaration.py#L25)). Missing fields return None. Path formats are inconsistent.

**Fix:**
1. Make the existing schema validator return errors for missing required fields (it currently doesn't block)
2. Normalize paths: all evidence paths must be relative to repo root. Reject absolute paths.
3. Add `sprint_executor_validate.py --strict` mode that rejects declarations with missing required fields (currently `--repair` auto-fixes, masking the problem)

**Verification:** Run `--strict` validation on the last 5 declarations. Expect failures. Fix the declaration-generating code to produce conformant output.

### R-5: Consolidate state writes into a single authoritative update

**Problem:** approval-gates.md (Step 7b) and continuation-signal.json (Step 8) are written at different pipeline stages by different functions from different inputs. Crash between them causes inconsistency. The signal is then non-atomically re-written by evidence_continuation.py.

**Fix:**
1. Compute the continuation verdict ONCE using a single function that takes all inputs (grades, contradictions, hard_stops, plan_lock state)
2. Write all state files from this single computed result, in the same step
3. Use `atomic_write_json` for ALL continuation signal writes (replace the `Path.write_text()` calls at [evidence_continuation.py:251](tools/supervisor/evidence_continuation.py#L251) and [check_continuation.py:514](tools/supervisor/check_continuation.py#L514))

This does NOT require replacing all state files with a single file (that's premature). It requires that the files agree because they're derived from the same computation, not independently derived.

**Verification:** After the change, `autonomous_continue` in continuation-signal.json and `AUTONOMOUS_CONTINUE` in approval-gates.md should always agree. Add an assertion to check_continuation.py that flags disagreement as a bug (not a cross-check to silently reconcile).

### R-6: Fix grading history append

**Problem:** `append_grading_history` does not exist in `autonomous_cycle_extensions.py`. The import fails silently at [autonomous_cycle.py:1977](tools/supervisor/autonomous_cycle.py#L1977). Grading history is not being recorded.

**Fix:** Implement `append_grading_history` in `autonomous_cycle_extensions.py` with sprint_id dedup (the original TC-HIST-DEDUP-001 intention). Check if `sprint_id` already exists in the JSONL before appending.

**Verification:** Run an autonomous cycle, check that grading-history.jsonl has a new entry. Run the same cycle again, check that no duplicate entry is added.

### R-7: Fix the zero-task circuit breaker

**Problem:** The breaker at [autonomous_cycle.py:1900](tools/supervisor/autonomous_cycle.py#L1900) only counts consecutive zeros. The actual pattern is non-consecutive. The breaker only warns, never stops.

**Fix:**
1. Track a rolling window (e.g., last 10 sprints) instead of consecutive count
2. If 7+ of last 10 are zero-item, emit a `CIRCUIT_BREAKER` hard stop (not a warning)
3. The hard stop should be overridable by check_continuation.py (not a TRUE_EXTERNAL_GATE) but should appear in the signal and be visible

**Verification:** After implementing, the current state (79% zero-item in last 100) would trigger the breaker within the first 10 sprints. The system would stop and report "7 of last 10 sprints produced zero items — work selection may be broken."

---

## 7. Production-Grade Solution Design

### Principle: Fix the grading pipeline's determinism first, then fix state management, then fix observability

The five nondeterminism mechanisms (M1-M5) are in the grading pipeline. Fixing them requires surgical changes to `grade_declared_work.py` and `autonomous_cycle.py`, not a rewrite.

### Phase 1: Grading Pipeline Determinism (R-1, R-2, R-3)

**Target files:**
- `tools/supervisor/grade_declared_work.py` — 3 changes (dead band, LLM-absent grade, empty-sprint guard)
- `tools/supervisor/maturity_trend.py` — add score mappings for UNVERIFIED and NO_ITEMS_DECLARED

**Changes:**
1. Remove lines 553-555 (confidence floor override) — 3 lines deleted
2. At line 962, when LLM unavailable and grade is ACCEPTED_VERIFIED, set grade to `UNVERIFIED` instead of ACCEPTED_WITH_LIMITATIONS
3. Before line 1052, add empty-grades guard returning `NO_ITEMS_DECLARED`
4. In maturity_trend.py, add `UNVERIFIED: 0.70` and `NO_ITEMS_DECLARED: 0.0` to `_verdict_score()`
5. Remove the `random.randint(0, 5)` jitter at line 576 — use fixed 30-minute TTL

**Risk:** Low. These are value changes in a grading function, not structural refactoring. The test suite covers grading behavior. The expected change: quality scores become lower but more honest.

**Safeguard:** Before deploying, re-grade the last 10 evidence declarations under both old and new logic. Document every grade that changes and verify the new grade is more correct.

### Phase 2: State Write Consolidation (R-5, R-6)

**Target files:**
- `tools/supervisor/autonomous_cycle.py` — consolidate Steps 7b and 8 into a single state-write function
- `tools/supervisor/evidence_continuation.py` — replace `Path.write_text()` with `atomic_write_json()`
- `tools/supervisor/check_continuation.py` — replace `Path.write_text()` with `atomic_write_json()`
- `tools/supervisor/autonomous_cycle_extensions.py` — implement `append_grading_history`

**Changes:**
1. Extract a `compute_continuation_verdict(grades, contradictions, hard_stops, plan_lock)` function that returns a single dict
2. Both approval-gates.md and continuation-signal.json derive from this dict
3. Write all state files in one function call (still separate files, but same input)
4. Fix all non-atomic writes to use `atomic_write_json()`
5. Implement `append_grading_history` with sprint_id dedup

**Risk:** Medium. This touches the critical path of the autonomous cycle. The state write ordering is load-bearing — changing it could introduce new inconsistencies.

**Safeguard:** Dual-write for 10 sprints: compute the new way, write the new way, also write the old way, diff the outputs. If they diverge, investigate before removing the old path.

### Phase 3: Circuit Breaker and Schema Enforcement (R-4, R-7)

**Target files:**
- `tools/supervisor/autonomous_cycle.py` — rolling-window zero-task detection
- `tools/supervisor/evidence_declaration.py` — strict validation mode
- `tools/supervisor/sprint_executor_validate.py` — `--strict` mode

**Changes:**
1. Replace consecutive counter with rolling-window tracker (last 10 sprints)
2. Add hard stop when 7+ of last 10 are zero-item
3. Make evidence declaration validation reject missing required fields in strict mode
4. Add relative-path enforcement for evidence paths

**Risk:** Low-medium. The circuit breaker change is a policy change (new stop condition). Schema enforcement may break existing declaration-generating code.

**Safeguard:** Run `--strict` validation against the last 20 declarations first. Identify which generating code paths produce non-conformant output. Fix them before enabling strict mode.

---

## 8. Verification Strategy

### Determinism Test

Run the grading pipeline 3 times on the same evidence declaration with LLM disabled:
- All 3 runs must produce identical grades, identical continuation signals, identical approval-gates.md
- If any differ, the nondeterminism has not been eliminated

### Boundary Tests for RC-1 and RC-2

For the confidence dead band fix:
- Test with `adequate=False, confidence=0.79` → should override to True (below threshold)
- Test with `adequate=False, confidence=0.80` → should NOT override (at/above threshold)
- Test with `adequate=False, confidence=0.85` → should downgrade (above threshold)
- Test with `adequate=False, confidence=0.84` → was the dead band, now should downgrade

For the LLM-absent grading:
- Test grade_all with LLM unavailable → UNVERIFIED, not ACCEPTED
- Test maturity trend score → 0.70, not 0.85

### Empty Sprint Test

- Submit an evidence declaration with zero work items
- Grade should be NO_ITEMS_DECLARED
- Quality score should be 0.0
- Continuation should be TRUE (empty sprint is not a stop condition)
- Maturity trend should reflect 0.0, not 0.85

### State Coherence Test

After the state write consolidation:
- Kill the process at random points during the pipeline
- Check that continuation-signal.json and approval-gates.md agree on `autonomous_continue`
- Check that grading-history.jsonl has exactly one entry per sprint_id

### Regression Test

- Re-grade the last 10 evidence declarations under the new logic
- Compare old vs. new grades for every item
- Document every change and verify correctness
- Run the full test suite (44,277 tests) — no regressions allowed

---

## 9. Tradeoffs and Risks

### What improves
- **Rerun consistency:** Eliminating the dead band and LLM-absent ambiguity means the same evidence produces the same grade regardless of LLM state. The grade may be different (UNVERIFIED vs. ACCEPTED_VERIFIED) but it's deterministically different.
- **Quality signal honesty:** Empty sprints at 0.0 instead of 0.85 makes the maturity trend meaningful.
- **State coherence:** Single-source continuation verdict eliminates the approval-gates/continuation-signal disagreement.
- **Operational visibility:** The zero-task circuit breaker with rolling window catches the 79%-empty pattern that the consecutive counter misses.

### What gets worse (temporarily)
- **Quality scores drop:** The maturity trend's last-100 average will drop from 0.828 to ~0.18. This is correct — it was inflated by empty sprints. But it will look like a regression to anyone watching the number.
- **More REWORK verdicts:** Closing the dead band means some items that were silently ACCEPTED will now be REWORK_REQUIRED. This is correct behavior but increases short-term rework volume.
- **Migration period complexity:** Dual-writing state files for 10 sprints adds operational overhead.

### What stays the same
- Product source code is untouched.
- Oracle system is untouched.
- Governance validators are untouched.
- Test suite is untouched.
- check_continuation.py safety logic is preserved.

### Limits of this solution
- **LLM nondeterminism is inherent.** Even with the dead band fixed, two LLM calls on the same evidence can return different confidence values. The fix makes the system's *response* to the LLM more consistent, but doesn't make the LLM itself deterministic.
- **Governance-to-product ratio (6.5:1) is structural.** These fixes don't reduce governance LOC. The ratio is a consequence of the system's architecture (autonomous supervision is expensive in code), not a bug.
- **SAL pipeline is still partially wired.** 14,844 facts were extracted once and never regenerated. Fixing the grading pipeline doesn't fix specification authority staleness.
- **178 uncommitted files remain.** The EXTERNAL_BLOCKER for git commits (VSCode extension permission system) is outside scope.

---

## 10. Evidence-Driven Conclusions

### Conclusion 1: The product is real and functional
**Evidence:** 26 format packages with streaming parsers, real test suites (1,772 FODS tests in 11.4s), near-zero stubs, oracle conformance with anti-self-approval.
**Confidence:** HIGH — verified by direct code inspection and test execution.

### Conclusion 2: The grading pipeline has five mechanical nondeterminism sources
**Evidence:** Code paths at [grade_declared_work.py:442-585, 553, 975, 1057](tools/supervisor/grade_declared_work.py#L442) and [autonomous_cycle.py:2060, 2526](tools/supervisor/autonomous_cycle.py#L2060), each independently verified.
**Confidence:** HIGH — these are code-level facts, not behavioral observations.

### Conclusion 3: The quality signal is currently meaningless
**Evidence:** 79% of last 100 sprints are zero-item, each scored 0.85. The trend (0.828) is dominated by empty-sprint inflation.
**Confidence:** HIGH — grading-history.jsonl analysis with maturity_trend.py score mapping.

### Conclusion 4: The state management is incoherent but not catastrophically broken
**Evidence:** approval-gates.md and continuation-signal.json disagree, but check_continuation.py has cross-checking logic that partially reconciles them. The system continues to run despite the contradiction.
**Confidence:** HIGH — state file inspection + code path tracing.

### Conclusion 5: The proposed fixes are targeted, low-risk, and independently verifiable
**Evidence:** Phase 1 changes 3 lines + adds 2 grade mappings. Phase 2 consolidates existing logic without changing behavior. Phase 3 replaces a broken circuit breaker.
**Confidence:** MEDIUM — the changes are well-scoped, but the dual-write migration period (Phase 2) introduces temporary complexity that could surface new issues.

### Conclusion 6: The governance infrastructure is overdeveloped relative to product but not wrong
**Evidence:** 6.5:1 infrastructure-to-product ratio. 223 validators for 26 formats. 174 commands. 262 plan files. This is expensive but functional — the validators catch real violations, the evidence trail is genuine, the safety logic prevents real failure modes.
**Confidence:** HIGH — LOC counts and validator behavior verified directly. The question of whether this ratio is optimal is a business decision, not a technical one.

---

## Execution Taskcards

### TC-SSC-001: Eliminate confidence dead band (R-1)
- **File:** `tools/supervisor/grade_declared_work.py`
- **Change:** Remove lines 553-555 (confidence floor override). Lower downgrade threshold at line 975 from `> 0.85` to `>= 0.80`.
- **Rationale:** Closes the 0.80-0.85 dead band where LLM "inadequate" verdicts are silently ignored.
- **Verification:** Unit test with confidence values 0.79, 0.80, 0.84, 0.85, 0.86 — each must produce the correct behavior.
- **Status:** CLOSED

### TC-SSC-002: Fix empty sprint inflation (R-3)
- **File:** `tools/supervisor/grade_declared_work.py`
- **Change:** Before line 1052, add empty-grades guard: `if not grades: overall_verdict = "NO_ITEMS_DECLARED"`. Add `NO_ITEMS_DECLARED` mapping to `maturity_trend.py` `_verdict_score()` → 0.0.
- **Rationale:** `all()` on empty list returns True in Python, causing zero-item sprints to be graded ACCEPTED with 0.85 quality.
- **Verification:** Test grade_all with empty items list → NO_ITEMS_DECLARED. Test maturity_trend score → 0.0.
- **Status:** CLOSED

### TC-SSC-003: Remove random jitter from grade cache TTL (R-2 partial)
- **File:** `tools/supervisor/grade_declared_work.py`
- **Change:** Remove `import random` and `_jitter = _random.randint(0, 5)` at lines 574-577. Use fixed `_effective_ttl = _FAILURE_TTL_MINUTES`.
- **Rationale:** Random jitter creates timing-dependent rerun behavior.
- **Verification:** Two identical runs started at different times must produce identical cache TTLs.
- **Status:** CLOSED

### TC-SSC-004: Fix non-atomic continuation signal writes (R-5 partial)
- **Files:** `tools/supervisor/evidence_continuation.py` (line 251), `tools/supervisor/check_continuation.py` (line 514)
- **Change:** Replace `Path.write_text()` with `atomic_write_json()` from `tools/supervisor/atomic_io.py`.
- **Rationale:** Non-atomic writes can corrupt continuation-signal.json on crash.
- **Verification:** Confirm both files import and use `atomic_write_json` instead of `write_text` for signal writes.
- **Status:** CLOSED

### TC-SSC-005: Implement append_grading_history (R-6)
- **File:** `tools/supervisor/autonomous_cycle_extensions.py`
- **Change:** Implement `append_grading_history(repo_root, sprint_id, run_id, timestamp, review, manifest)` with sprint_id dedup. Place after `append_maturity_trend` (line 186).
- **Rationale:** Function is imported at autonomous_cycle.py:1977 but doesn't exist. Grading history is not being recorded.
- **Verification:** Run autonomous cycle → grading-history.jsonl has new entry. Run again with same sprint_id → no duplicate.
- **Status:** CLOSED

### TC-SSC-006: Fix zero-task circuit breaker (R-7)
- **File:** `tools/supervisor/autonomous_cycle.py` (lines 1900-1925)
- **Change:** Replace consecutive counter with rolling-window tracker (last 10 sprints). Fire hard stop when 7+ of last 10 are zero-item. The hard stop adds to `hard_stops_detected` (not just a warning).
- **Rationale:** Consecutive counting misses the actual non-consecutive zero-task pattern. Warning-only breaker never stops execution.
- **Verification:** Test with 7 zero-item and 3 non-zero sprints in alternating order → breaker fires. Test with 6 zero and 4 non-zero → breaker does not fire.
- **Status:** CLOSED

### TC-SSC-007: Add UNVERIFIED grade level (R-2)
- **Files:** `tools/supervisor/grade_declared_work.py`, `tools/supervisor/maturity_trend.py`
- **Change:** When LLM is unavailable, cap ACCEPTED_VERIFIED to `UNVERIFIED` (not ACCEPTED_WITH_LIMITATIONS). Add `UNVERIFIED: 0.70` to `_verdict_score()`.
- **Rationale:** Makes the LLM-absent vs. LLM-present difference visible in grade output rather than hidden.
- **Verification:** Grade with LLM disabled → UNVERIFIED (not ACCEPTED_WITH_LIMITATIONS). Maturity trend score → 0.70.
- **Status:** CLOSED

### Convergence Amendment: Additional test fixes
- **Files:** `tests/supervisor/test_grade_timeout_spec_parity.py` — added `UNVERIFIED` to accepted grade set
- **Discovered during:** Post-sprint audit (convergence iteration 1)
- **Status:** CLOSED (413 tests pass, 0 fail)

<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-15T05:19:42.946233+00:00"
  locked_by: "7adafdcbf11c"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->

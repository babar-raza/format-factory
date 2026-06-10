# FORMAT-FACTORY-RNEXT-MEGA-TRAIN-001
# Generated: 2026-06-10T13:42:46.039857
# Source: Supervisor autonomous-cycle review of FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-10-001
# Stream: acceleration
# ADVISORY ONLY -- not a Format Factory authority document

---

## Sprint Context

The previous sprint (FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-10-001) was **ACCEPTED_WITH_REWORK** due to several critical evidence and verification gaps:

| Issue | Symptom | Root Cause |
|-------|---------|------------|
| Continuation signal mismatch | `continuation-signal.json` reported `"autonomous_continue": false` while `approval-gates.md` claimed `AUTONOMOUS_CONTINUE: YES` | Inconsistent generation logic and no test asserting alignment |
| Scope drift | Evidence showed iteration **10** instead of the required **9/12** | Wrong iteration parameter supplied to generation scripts |
| Missing execution proof | No test logs or runtime output demonstrating that the continuation signal or approval gates were actually evaluated | Absence of integration‑test harness |
| Incomplete task regeneration | `product-task-candidates.json` contained only **6** candidates, with many fields missing and no sprint metadata | Generation script truncated output and omitted required fields |
| Insufficient clear_page testing | No tests for `TypeError` on non‑dict input, no verification of `shapes_total` update, and negative‑index handling not covered | Test suite focused only on happy path |
| Evidence thinness | Static JSON/markdown without timestamps, version stamps, or commit references | No systematic evidence‑declaration workflow |

**Priorities for this sprint**

1. **Align continuation signal with approval‑gate declaration** and provide a concrete test that asserts the match.
2. **Regenerate `product-task-candidates.json`** with **exactly 10 fully‑populated tasks** (including `action_id`, `done_criteria`, `status`, `completion_timestamp`, `sprint_id`, etc.) and prove the regeneration with version/timestamp evidence.
3. **Add comprehensive tests for `clear_page()`** covering type validation, shape updates, negative indices, and preservation of unrelated fields.
4. **Produce verifiable execution logs** for all new/updated functionality and reference them in the evidence declaration.
5. **Ensure all evidence files are declared** in `.local/evidences/<run_id>/evidence-declaration.yaml` with correct status and paths.

---

## Preflight (read before any code change)

Read these files before writing any code:

1. `AGENTS.md`
2. `GOVERNANCE.md`
3. `plans/master-plan.md`
4. `registry/format-registry.yaml`
5. `reports/supervisor/session-resume.md`
6. `reports/supervisor/latest-review.md`
7. `.supervisor/policies.yaml`
8. `.supervisor/skill-registry.yaml`
9. `.local/supervisor/selected-product-gaps.json`
10. `product-capability-matrix/poc-targets.yaml`
11. `CLAUDE.md`

---

## Sprint Identity

- Sprint ID: FORMAT-FACTORY-RNEXT-MEGA-TRAIN-001
- Prior sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-10-001
- Prior verdict: ACCEPTED_WITH_REWORK
- Prior tests: 0 passed, 0 failed, 0 skipped
- Autonomous continue: True

---

## Sprint Goal

**Goal:** Repair 2 item(s) flagged by supervisor review. Advance Acceleration tooling: Expand anti‑skip detectors or severity mapping; Improve grading engine or evidence quality scoring; Harden hard gates and continuation policy. Build evidence declaration and run supervisor autonomous‑cycle.

---

## Mandatory Evidence Rules

1. Worker MUST write `.local/evidences/<run_id>/evidence-declaration.yaml` at sprint end.
2. Last instruction MUST be:
   ```bash
   python tools/supervisor/supervisor_loop.py autonomous-cycle \
     --declaration .local/evidences/<run_id>/evidence-declaration.yaml
   ```
3. The declaration must list ALL work items with status, evidence paths, and test references.
4. Do NOT use the legacy `run-on-latest --bundle` command. It is deprecated.
5. Evidence is support infrastructure -- the goal is product POC progress.

---

## Governed Product Acceleration Rules

1. Load `.local/supervisor/selected-product-gaps.json` before choosing product work.
2. Resolve each selected product gap through `.supervisor/skill-registry.yaml`.
3. No direct ad‑hoc `src/` edits are permitted. Use a governed skill or generated execution handoff.
4. Every `src/` edit MUST be recorded in `reports/r90/product-code-change-ledger.json`.
5. Run `python tools/supervisor/validate_product_code_ledger.py --ledger reports/r90/product-code-change-ledger.json` after product‑code changes.
6. Include at least one dogfood export lane and one package/install proof lane.

---

## Train Manifest

| Train | Group | Title |
|-------|-------|-------|
| A | G1 | Governance Preflight |
| B | G2 | Rework: Verify continuation signal and approval-gates (iter 9/12) |
| C | G2 | Rework: TC-CANDIDATES: Regenerate product-task-candidates.json with 10 Sprint 10 tasks |
| D | G2 | Expand anti-skip detectors or severity mapping |
| E | G2 | Improve grading engine or evidence quality scoring |
| F | G2 | Harden hard gates and continuation policy |
| G | G7 | State + Memory + POC Matrix Sync |
| H | G8 | Evidence Declaration + Supervisor Autonomous-Cycle |

---

## Group G1: Governance + Preflight

### Train A: Governance Preflight

Read all governance files. Verify no policy violations from prior sprint. Confirm MCP status, supervisor mode, and gate states. Load `.local/supervisor/selected-product-gaps.json` and `.supervisor/skill-registry.yaml` before selecting product work.

**Acceptance Criteria:**
- All preflight files are read without error.
- No policy violations are detected; any findings are documented.
- Current gate states are captured in `reports/<run_id>/00-preflight.md`.

**Files:**
- `reports/<run_id>/00-preflight.md`

## Group G2: Rework / Repair

### Train B: Rework: Verify continuation signal and approval-gates (iter 9/12)

**Acceptance Criteria:**
1. `continuation-signal.json` contains `"autonomous_continue": true` **and** the same boolean value appears in `approval-gates.md` under `AUTONOMOUS_CONTINUE`.
2. A unit test `tests/supervisor/test_continuation_signal.py` asserts the equality of the two sources.
3. Execution logs (`logs/continuation-eval.log`) show the signal being read and the gate decision applied.
4. The evidence declaration references the JSON, the markdown, the test file, and the log.

**Files:**
- `.local/supervisor/continuation-signal.json`
- `reports/supervisor/approval-gates.md`
- `tests/supervisor/test_continuation_signal.py`
- `logs/continuation-eval.log`

### Train C: Rework: TC-CANDIDATES: Regenerate product-task-candidates.json with 10 Sprint 10 tasks

**Acceptance Criteria:**
1. `product-task-candidates.json` contains **exactly 10** top‑level task objects.
2. Each task includes the fields: `task_id`, `action_id`, `done_criteria`, `status` (set to `completed`), `completion_timestamp` (ISO‑8601), `sprint_id` = 10, and any other required metadata.
3. The file includes a `generated_at` timestamp and a version bump (`"version": "10.0.0"` or similar) different from the prior sprint.
4. A regeneration script test `tests/product/test_task_candidates_regeneration.py` validates the count, required fields, and timestamp freshness.
5. Evidence includes the git diff (`git diff --stat product-task-candidates.json`) and the generation log (`logs/task-candidates-regeneration.log`).

**Files:**
- `product-task-candidates.json`
- `tests/product/test_task_candidates_regeneration.py`
- `logs/task-candidates-regeneration.log`

### Train D: Expand anti-skip detectors or severity mapping

Add new detectors, refine severity levels, or improve detection accuracy.

**Acceptance Criteria:**
- New detector modules are covered by unit tests in `tests/supervisor/`.
- Severity mapping changes are reflected in `tools/supervisor/severity_map.yaml`.
- Evidence of test pass and updated mapping is declared.

**Files:**
- `tools/supervisor/`
- `tests/supervisor/`

### Train E: Improve grading engine or evidence quality scoring

Enhance `grade_declared_work.py` or evidence quality heuristics.

**Acceptance Criteria:**
- Updated grading logic is exercised by tests in `tests/supervisor/`.
- Evidence of improved scoring (e.g., before/after score CSV) is included.

**Files:**
- `tools/supervisor/`
- `tests/supervisor/`

### Train F: Harden hard gates and continuation policy

Strengthen autonomous‑cycle enforcement and stop conditions.

**Acceptance Criteria:**
- Gate‑evaluation code is covered by tests.
- Evidence shows gate decisions for at least three distinct scenarios (continue, pause, abort).

**Files:**
- `tools/supervisor/`
- `tests/supervisor/`

## Group G7: State / Memory / POC Matrix

### Train G: State + Memory + POC Matrix Sync

Update `state/current-state.md`, `.supervisor/project-memory.md`, and `product-capability-matrix/poc-targets.yaml` with sprint results.

**Acceptance Criteria:**
- `poc-targets.yaml` reflects the actual status of each POC (no over‑claiming).
- `state/current-state.md` includes a summary table with the new sprint ID.
- `.supervisor/project-memory.md` has a new entry dated with the sprint end timestamp.

**Files:**
- `state/current-state.md`
- `.supervisor/project-memory.md`
- `product-capability-matrix/poc-targets.yaml`

## Group G8: Evidence + Supervisor Loop

### Train H: Evidence Declaration + Supervisor Autonomous-Cycle

Write `evidence-declaration.yaml` listing ALL work items. Run autonomous‑cycle. Verify `session-resume.md` is regenerated. Validate `reports/r90/product-code-change-ledger.json` for any governed product source edit.

**Acceptance Criteria:**
- `evidence-declaration.yaml` enumerates every train (A‑H) with status `completed`, paths to evidence files, and test references.
- Autonomous‑cycle exits with code **0** (success) or **3** (graceful stop) and logs are captured (`logs/autonomous-cycle.log`).
- `reports/supervisor/session-resume.md` contains the latest run metadata.
- `approval-gates.md` shows `AUTONOMOUS_CONTINUE: YES` matching the continuation signal.
- Ledger validation passes with no unauthorized edits.

**Files:**
- `.local/evidences/<run_id>/evidence-declaration.yaml`
- `reports/supervisor/session-resume.md`
- `reports/supervisor/approval-gates.md`
- `logs/autonomous-cycle.log`

**Verification:**
```bash
python tools/supervisor/supervisor_loop.py autonomous-cycle \
  --declaration .local/evidences/<run_id>/evidence-declaration.yaml
```

---

## Hard Prohibitions

- No `git push` without explicit user authorization.
- No `git commit` without explicit user authorization.
- No Gate 8 or Gate 11 approval (requires Babar Raza).
- No `commercial_product_ready: true` in any file.
- No PyPI / NuGet / GitHub release publication.
- No paid external AI API or web automation.
- No MCP activation unless MODE 4 already authorized.
- No destructive git operations (`git reset --hard`, `git clean -fd`, force-push).
- No deletion of existing test files.
- No PENDING markers in final state files.
- No overclaiming: if evidence is missing, declare status honestly.
- No direct ad‑hoc `src/` edits outside the governed skill registry or generated handoff.
- No product-code change without a product-code ledger entry.

---

## Final Validation Sequence

After all trains complete, run this exact sequence:

```bash
# 1. Python tests
.local/venv/Scripts/python -m pytest tests/ -x -q --tb=short

# 2. Compile check on supervisor tools
.local/venv/Scripts/python -m py_compile tools/supervisor/autonomous_cycle.py
.local/venv/Scripts/python -m py_compile tools/supervisor/supervisor_loop.py
.local/venv/Scripts/python -m py_compile tools/supervisor/generate_supervisor_packet.py

# 3. .NET tests (if .NET work was done)
# (no .NET work this sprint)

# 4. Write evidence declaration
# (create .local/evidences/<run_id>/evidence-declaration.yaml)

# 5. Run supervisor autonomous-cycle
.local/venv/Scripts/python tools/supervisor/supervisor_loop.py autonomous-cycle \
  --declaration .local/evidences/<run_id>/evidence-declaration.yaml
```
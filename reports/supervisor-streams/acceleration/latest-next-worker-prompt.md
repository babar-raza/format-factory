# FORMAT-FACTORY-RNEXT-MEGA-TRAIN-001
# Generated: 2026-06-11T21:41:40.894460
# Source: Supervisor autonomous-cycle review of FORMAT-FACTORY-SAL-ENFORCEMENT-CLOSEOUT-AND-PRODUCT-ACCELERATION-RNEXT-001
# Stream: acceleration
# ADVISORY ONLY -- not a Format Factory authority document

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
- Prior sprint: FORMAT-FACTORY-SAL-ENFORCEMENT-CLOSEOUT-AND-PRODUCT-ACCELERATION-RNEXT-001
- Prior verdict: ACCEPTED_WITH_REWORK
- Prior tests: 0 passed, 0 failed, 0 skipped
- Autonomous continue: True

---

## Sprint Goal

**Goal:** Repair 4 item(s) flagged by supervisor review. Advance Acceleration tooling: Expand anti-skip detectors or severity mapping; Improve grading engine or evidence quality scoring; Harden hard gates and continuation policy. Build evidence declaration and run supervisor autonomous-cycle.

---

## Mandatory Evidence Rules

1. Worker MUST write `.local/evidences/<run_id>/evidence-declaration.yaml` at sprint end.
2. Last instruction MUST be:
   ```
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
3. No direct ad-hoc `src/` edits are permitted. Use a governed skill or generated execution handoff.
4. Every `src/` edit MUST be recorded in `reports/r90/product-code-change-ledger.json`.
5. Run `python tools/supervisor/validate_product_code_ledger.py --ledger reports/r90/product-code-change-ledger.json` after product-code changes.
6. Include at least one dogfood export lane and one package/install proof lane.

---

## Train Manifest

| Train | Group | Title |
|-------|-------|-------|
| A | G1 | Governance Preflight |
| B | G2 | Rework: Lane C — Raw log index |
| C | G2 | Rework: Lane G — Product advancement: add get_frame_size_stats() to zst_codec.py |
| D | G2 | Rework: Lane H — Backfill dry-run: capability map generator |
| E | G2 | Rework: Lane I — Doc state sync verification |
| F | G2 | Expand anti-skip detectors or severity mapping |
| G | G2 | Improve grading engine or evidence quality scoring |
| H | G2 | Harden hard gates and continuation policy |
| I | G7 | State + Memory + POC Matrix Sync |
| J | G8 | Evidence Declaration + Supervisor Autonomous-Cycle |

---

## Group G1: Governance + Preflight

### Train A: Governance Preflight

Read all governance files. Verify no policy violations from prior sprint. Confirm MCP status, supervisor mode, and gate states. Load `.local/supervisor/selected-product-gaps.json` and `.supervisor/skill-registry.yaml` before selecting product work.

**Acceptance Criteria:**
- All preflight files read
- No policy violations detected
- Gate states documented

**Files:**
- `reports/<run_id>/00-preflight.md`

## Group G2: Rework / Repair

### Train B: Rework: Lane C — Raw log index



**Acceptance Criteria:**
- Evidence for RNEXT-LC passes supervisor inspection
- Tests pass for affected code

**Files:**
- `.local/evidences/sal-enforcement-closeout-product-accel-rnext-20260611-8e45224/raw-log-index.json`

### Train C: Rework: Lane G — Product advancement: add get_frame_size_stats() to zst_codec.py

Stub evidence detected (was ACCEPTED_VERIFIED): ['The provided diff does not contain the implementation of get_frame_size_stats; the function is missing from the changed file.', 'No test file content is included, so we cannot verify that the claimed 11 tests actually exercise the new function or contain meaningful assertions.', 'The added code focuses on unrelated helper functions (compress_string, decompress_to_string, etc.), indicating a scope mismatch with the work item.', 'Without seeing the test code, there is a risk that the tests are stubs (e.g., only assert True or pass) rather than validating the returned statistics.']

**Acceptance Criteria:**
- Evidence for RNEXT-LG passes supervisor inspection
- Tests pass for affected code

**Files:**
- `.local/evidences/sal-enforcement-closeout-product-accel-rnext-20260611-8e45224/product-advancement-ledger.json`
- `.local/evidences/sal-enforcement-closeout-product-accel-rnext-20260611-8e45224/diff-zst-codec.patch`

### Train D: Rework: Lane H — Backfill dry-run: capability map generator



**Acceptance Criteria:**
- Evidence for RNEXT-LH passes supervisor inspection
- Tests pass for affected code

**Files:**
- `.local/evidences/sal-enforcement-closeout-product-accel-rnext-20260611-8e45224/backfill-proof.json`

### Train E: Rework: Lane I — Doc state sync verification



**Acceptance Criteria:**
- Evidence for RNEXT-LI passes supervisor inspection
- Tests pass for affected code

**Files:**
- `.local/evidences/sal-enforcement-closeout-product-accel-rnext-20260611-8e45224/source-diff-index.json`

### Train F: Expand anti-skip detectors or severity mapping

Add new detectors, refine severity levels, or improve detection accuracy.

**Acceptance Criteria:**
- Tests pass for affected tools
- Evidence declared

**Files:**
- `tools/supervisor/`
- `tests/supervisor/`

### Train G: Improve grading engine or evidence quality scoring

Enhance grade_declared_work.py or evidence quality heuristics.

**Acceptance Criteria:**
- Tests pass for affected tools
- Evidence declared

**Files:**
- `tools/supervisor/`
- `tests/supervisor/`

### Train H: Harden hard gates and continuation policy

Strengthen autonomous-cycle enforcement and stop conditions.

**Acceptance Criteria:**
- Tests pass for affected tools
- Evidence declared

**Files:**
- `tools/supervisor/`
- `tests/supervisor/`

## Group G7: State / Memory / POC Matrix

### Train I: State + Memory + POC Matrix Sync

Update state/current-state.md, .supervisor/project-memory.md, and product-capability-matrix/poc-targets.yaml with sprint results.

**Acceptance Criteria:**
- poc-targets.yaml reflects actual status (no overclaiming)
- state/current-state.md updated
- project-memory.md entry appended

**Files:**
- `state/current-state.md`
- `.supervisor/project-memory.md`
- `product-capability-matrix/poc-targets.yaml`

## Group G8: Evidence + Supervisor Loop

### Train J: Evidence Declaration + Supervisor Autonomous-Cycle

Write evidence-declaration.yaml listing ALL work items. Run autonomous-cycle. Verify session-resume.md is regenerated. Validate `reports/r90/product-code-change-ledger.json` for any governed product source edit.

**Acceptance Criteria:**
- evidence-declaration.yaml written with all work items
- autonomous-cycle exits 0 or 3
- session-resume.md regenerated with current data
- approval-gates.md shows correct AUTONOMOUS_CONTINUE

**Files:**
- `.local/evidences/<run_id>/evidence-declaration.yaml`
- `reports/supervisor/session-resume.md`

**Verification:**
```bash
python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/<run_id>/evidence-declaration.yaml
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
- No direct ad-hoc `src/` edits outside the governed skill registry or generated handoff.
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

---

## Allowed Verdicts

The sprint MUST end with one of these verdicts in the evidence declaration:

| Verdict | Meaning |
|---------|---------|
| ALL_TRAINS_COMPLETE | All trains passed acceptance criteria |
| PARTIAL_TRAINS_COMPLETE_PUBLICATION_BLOCKED | Some trains done, publication gate blocks remaining |
| REWORK_REQUIRED | Supervisor review found issues requiring repair |
| BLOCKED_EXTERNAL_GATE | Cannot proceed without external gate approval |

---

## Final Artifact Specification

At sprint end, these files MUST exist:

- `.local/evidences/<run_id>/evidence-declaration.yaml` -- declaration of all work items
- `reports/supervisor/session-resume.md` -- regenerated by autonomous-cycle
- `reports/supervisor/approval-gates.md` -- regenerated by autonomous-cycle
- `product-capability-matrix/poc-targets.yaml` -- updated if any product status changed
- `state/current-state.md` -- updated with sprint outcome

---

END OF SUPERVISOR-GENERATED MEGA-TRAIN EXECUTION PROMPT

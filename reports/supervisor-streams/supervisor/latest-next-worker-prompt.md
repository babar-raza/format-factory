# FORMAT-FACTORY-RNEXT-MEGA-TRAIN-001
# Generated: 2026-06-14T12:54:25.709616
# Source: Supervisor autonomous-cycle review of SYSTEM-HARDENING-AND-CONTROLLED-PRODUCT-HEALING-20260614
# Stream: supervisor
# ADVISORY ONLY -- not a Format Factory authority document

---

## Sprint Context

**What went wrong in the prior sprint**  
- All six rework lanes were accepted only after a *re‑work* verdict because the submitted evidence consisted of **stub artifacts** (design markdown, file listings, or high‑level test descriptions) with **no executable test code, diff snippets, or execution logs**.  
- Critical verification steps were missing:  
  - No pytest files or `pytest` output showing that the intended tests actually ran.  
  - No logs demonstrating that `critical_rework_count` was incremented and that the process exited with code 3 for the blocks‑sprint enforcement case.  
  - No code diffs proving that validators were wired into `run_all_governance_validators()`.  
  - The evidence‑schema hardening lane added **16 optional fields** while the acceptance criteria required **13**, and no schema‑validation script was provided.  
  - For the durable‑healing and task‑generation lanes, the required test files were absent, making it impossible to confirm edge‑case handling.  

**Priorities for this sprint**  
1. **Deliver concrete, runnable test artifacts** for every lane (pytest files, `pytest -q` output, coverage reports ≥ 80 %).  
2. **Include verifiable execution evidence**: logs, exit‑code checks, and diff snippets that show the exact code changes.  
3. **Align schema changes** with the specified 13 optional fields and provide an automated validation script that proves the fields are truly optional.  
4. **Document all evidence** in the required declaration file and ensure every work item is referenced with concrete paths.  

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
- Prior sprint: SYSTEM-HARDENING-AND-CONTROLLED-PRODUCT-HEALING-20260614
- Prior verdict: ACCEPTED_WITH_REWORK
- Prior tests: 0 passed, 0 failed, 0 skipped
- Autonomous continue: True

---

## Sprint Goal

**Goal:** Repair 6 item(s) flagged by supervisor review. Advance Supervisor tooling: Improve supervisor pipeline components; Strengthen evidence model or declaration schema. Build evidence declaration and run supervisor autonomous‑cycle.

---

## Mandatory Evidence Rules

1. Worker MUST write `.local/evidences/<run_id>/evidence-declaration.yaml` at sprint end.  
2. Last instruction MUST be:
   ```bash
   python tools/supervisor/supervisor_loop.py autonomous-cycle \
     --declaration .local/evidences/<run_id>/evidence-declaration.yaml
   ```
3. The declaration must list **ALL** work items with status, evidence paths, and test references.  
4. Do NOT use the legacy `run-on-latest --bundle` command. It is deprecated.  
5. Evidence is support infrastructure – the goal is product POC progress.

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
| B | G2 | Rework: Lane 1: Governance closeout defect repair — blocks_sprint enforcement + claim classification regression tests |
| C | G2 | Rework: Lane 2: Spec-parity validator implementation — 4 validators wired into governance pipeline |
| D | G2 | Rework: Lane 3: Depth validator implementation — 3 validators for shallow code detection |
| E | G2 | Rework: Lane 4: Evidence schema hardening — 13 optional fields for spec-parity and depth validation |
| F | G2 | Rework: Lane 6: Task generation repair — gap-ledger primary, advisory-only guard, hardcoded goals demoted |
| G | G2 | Rework: Lane 7: CI gate hardening — || true removed from .NET build, continue-on-error for experimental only |
| H | G2 | Improve supervisor pipeline components |
| I | G2 | Strengthen evidence model or declaration schema |
| J | G7 | State + Memory + POC Matrix Sync |
| K | G8 | Evidence Declaration + Supervisor Autonomous-Cycle |

---

## Group G1: Governance + Preflight

### Train A: Governance Preflight

Read all governance files. Verify no policy violations from prior sprint. Confirm MCP status, supervisor mode, and gate states. Load `.local/supervisor/selected-product-gaps.json` and `.supervisor/skill-registry.yaml` before selecting product work.

**Acceptance Criteria**
- All preflight files are read and their SHA‑256 hashes recorded in `reports/<run_id>/00-preflight.md`.  
- No policy violations are detected; any findings are logged with line numbers.  
- Gate states (e.g., `blocks_sprint`, `claim_classification`) are captured in the preflight report.  
- The preflight report is referenced in the final evidence declaration.

**Files**
- `reports/<run_id>/00-preflight.md`

---

## Group G2: Rework / Repair

### Train B: Rework: Lane 1: Governance closeout defect repair — blocks_sprint enforcement + claim classification regression tests

**Acceptance Criteria**
1. **Implementation** – Code changes that enforce `blocks_sprint` and correct claim‑classification logic are present in `src/governance/closeout.py`.  
2. **Diff Evidence** – A unified diff (`git diff`) showing the exact modifications is included in the evidence folder.  
3. **Test Suite** – A pytest file `tests/governance/test_closeout_enforcement.py` containing **≥ 10** concrete test cases (including success, failure, and edge cases).  
4. **Execution Proof** – `pytest -q` output showing **10 passed** and the process exit code **3** when `critical_rework_count` is incremented. The log file `logs/closeout_enforcement.log` must contain the line `critical_rework_count incremented to X`.  
5. **Coverage** – Coverage report (`coverage xml`) indicating **≥ 80 %** line coverage for the modified module.  
6. All artifacts are listed in the evidence declaration under the identifier `SHCPH-L1-GOV-REPAIR`.

**Files**
- `.local/evidences/<run_id>/claim-classification-repair.md` (includes diff, test file, pytest output, coverage report, log)
- `.local/evidences/<run_id>/governance-closeout-contradiction-repair.md` (summary and verification checklist)

### Train C: Rework: Lane 2: Spec-parity validator implementation — 4 validators wired into governance pipeline

**Acceptance Criteria**
1. **Validator Code** – Four validator classes (`SpecParityValidatorA‑D`) are implemented in `src/validators/spec_parity.py`.  
2. **Wiring Evidence** – A diff snippet showing the addition of these validators to `run_all_governance_validators()` in `src/governance/runner.py`.  
3. **Test Suite** – `tests/validators/test_spec_parity_validators.py` with **≥ 8** tests covering PASS, WARN, and FAIL outcomes for each validator.  
4. **Execution Proof** – Pytest output confirming all tests pass and showing the exact exit code (0).  
5. **Coverage** – Coverage report with **≥ 85 %** coverage of `spec_parity.py`.  
6. All items are referenced in the declaration under `SHCPH-L2-SPEC-PARITY`.

**Files**
- `.local/evidences/<run_id>/spec-parity-validator-design.md` (contains diff, test file, pytest output, coverage)

### Train D: Rework: Lane 3: Depth validator implementation — 3 validators for shallow code detection

**Acceptance Criteria**
1. **Implementation** – Three depth‑validator functions (`detect_shallow_imports`, `detect_shallow_calls`, `detect_shallow_definitions`) are added to `src/validators/depth.py`.  
2. **Diff Evidence** – Unified diff of `depth.py` and the updated `run_all_governance_validators()` call.  
3. **Test Suite** – `tests/validators/test_depth_validators.py` with **≥ 6** concrete test cases, including edge‑case files that should trigger each validator.  
4. **Execution Proof** – Pytest output showing all tests pass; log `logs/depth_validator.log` must contain at least one detection message for each validator.  
5. **Coverage** – Coverage report with **≥ 80 %** line coverage for `depth.py`.  
6. Referenced in the declaration as `SHCPH-L3-DEPTH`.

**Files**
- `.local/evidences/<run_id>/depth-validator-design.md` (diff, test file, pytest output, coverage, logs)

### Train E: Rework: Lane 4: Evidence schema hardening — 13 optional fields for spec-parity and depth validation

**Acceptance Criteria**
1. **Schema Update** – `schema/evidence_schema.yaml` now includes **exactly 13** new optional fields (`spec_parity_*` and `depth_*`). No extra fields are present.  
2. **Diff Evidence** – Diff showing the schema change.  
3. **Validation Script** – A Python script `tools/validate_evidence_schema.py` that runs against the current evidence declarations and exits with code 0 when all required fields are present and optional fields are omitted.  
4. **Optional‑Field Tests** – A pytest file `tests/schema/test_optional_fields.py` that iterates over each of the 13 fields, removes it from a sample declaration, runs the validator, and asserts success.  
5. **Execution Proof** – Pytest output confirming **13 passing** optional‑field tests and a final run of `validate_evidence_schema.py` with exit code 0.  
6. All artifacts are listed under `SHCPH-L4-SCHEMA`.

**Files**
- `.local/evidences/<run_id>/schema-hardening-design.md` (diff, validation script, test file, pytest output)

### Train F: Rework: Lane 6: Task generation repair — gap‑ledger primary, advisory‑only guard, hardcoded goals demoted

**Acceptance Criteria**
1. **Code Changes** – Modifications to `src/task_generation/gap_ledger.py` and `src/task_generation/guard.py` that implement the primary gap‑ledger, advisory‑only guard, and removal of hard‑coded goals. Diff included.  
2. **Test Suite** – `tests/task_generation/test_task_generation_repair.py` with **≥ 9** tests covering:  
   - Priority inversion detection,  
   - Advisory‑only guard behavior,  
   - Queue tracking correctness,  
   - Correct handling when hard‑coded goals are absent.  
3. **Execution Proof** – Pytest output showing all tests pass; logs `logs/task_generation_repair.log` must contain entries confirming each scenario was exercised.  
4. **Coverage** – Coverage report with **≥ 80 %** coverage of the modified modules.  
5. All evidence referenced under `SHCPH-L6-TASKGEN`.

**Files**
- `.local/evidences/<run_id>/task-generation-repair.md` (diff, test file, pytest output, coverage, logs)

--- 

## Hard Prohibitions
*(Preserved unchanged as required)*

## Final Validation Sequence
*(Preserved unchanged as required)*
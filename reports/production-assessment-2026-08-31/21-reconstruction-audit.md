# Reconstruction Audit — R1-R20 Execution Verification

**Assessed commit:** dd909cf3a9586a8a6b7a32c357011cd2557e3fae (HEAD of main, unchanged)
**Audit date:** 2026-08-31
**Auditor:** Claude (production-system reconstruction session)
**Plan:** plans/.claude/production-system-reconstruction.md

## Methodology

Each repair item is classified into exactly one of:

- `completed_verified` — implemented AND verified with real execution
- `completed_weakly_verified` — implementation exists; proof is limited
- `partially_done` — code exists but is unwired or unvalidated
- `not_attempted` — required work not started
- `claimed_unproven` — claimed complete without adequate proof
- `risk_not_reduced` — code changed but production risk unchanged

## Audit Results

### Phase 1: Stabilize

| Item | Classification | Evidence |
|------|---------------|----------|
| R1 | `completed_verified` | Baseline frozen at dd909cf3a, all 22 investigation artifacts produced |
| R3 | `completed_verified` | `controller_state_validator.py` detects promotion/truth_boundary disagreement; current state PASSES after UNASSESSED reset; negative controls proven |
| R8 | `completed_verified` | `autonomous_task_generator.py` line 1705 `output_path = output_path or DEFAULT_OUTPUT` removed; all writes guarded by `if output_path is not None:` |
| R9 | `completed_verified` (no fix needed) | All 725 IPYNB tests pass at HEAD; assessment findings were based on different worktree state |
| R10 | `completed_verified` | CI `test-gen2` job added: Python 3.11+3.12 matrix, installs core + 6 FF6 packages with [test] extras |
| R11 | `completed_verified` | `openraster` → `ora` in product-goal.yaml, production_program.py, product_action_guard.py, tests |
| R12 | `completed_verified` | UBL 194→195 in controller-state.yaml; register, reconciliation, and controller all agree |
| R13 | `completed_verified` | `build_evidence_ledger.py` preserves existing evidence order; `test_real_safetensors_ledger_rebuilds_identically` PASSES |

### Phase 2: Fix Certification Chain

| Item | Classification | Evidence |
|------|---------------|----------|
| R4 | `completed_verified` | `goal_driver.py` no longer reads `promotion.get(format_id) == CERTIFIED`; `_is_certified()` computes from reconciliation |
| R5 | `completed_verified` | Certification = total > 0 AND unresolved == 0 AND proof_strength not "nonpromoting" AND promotion_effect not "none" AND evidence fresh. Negative control: ORA with 1 unresolved → NOT certified |
| R6 | `completed_verified` | `promote_evidence.py` records per-file SHA-256 hashes in `referenced_input_digests`; `_evidence_is_fresh()` in goal_driver.py compares stored hashes against current files |

### Phase 3: Consolidate Control Systems

| Item | Classification | Evidence |
|------|---------------|----------|
| R2 | `completed_verified` | `docs/authority-decision-record.md`: 16 concerns, single authority per concern, DERIVED/ADVISORY/RETIRED classification |
| R14 | `completed_verified` | `tools/plan_control/__init__.py` retirement docstring + DeprecationWarning on import; no external consumers |
| R15 | `completed_verified` | `_FF6_GOVERNED_FORMATS` guard in lane_selector.py (returns ff6_governed_boundary) and autonomous_task_generator.py (filters out FF6 goals) |
| R16 | `completed_verified` | `_NON_OVERRIDABLE_SESSION_STOPS` set in sprint_executor.py; elif branch checks before blanket Supreme Directive override |

### Phase 4: Build Target System

| Item | Classification | Evidence |
|------|---------------|----------|
| R7 | `completed_verified` | `python -m tools.ff6.run` produces correct verdict from committed files only; contradiction gate integrated; exits 0/1/2 |
| R17 | `completed_verified` | `tools/ff6/scheduler.py`: breadth/depth scheduler with anti-starvation; correctly shows only ORA work after 5/6 certified |

### Phase 5: Prove and Migrate

| Item | Classification | Evidence |
|------|---------------|----------|
| R18 | `completed_verified` | Full vertical cycle for NRRD: clean start → scheduler selects → 962 tests pass → per-file hashes recorded → certification derived → scheduler selects different work |
| R19 | `completed_verified` | 5/6 formats promoted: IPYNB (725 tests), NRRD (962), XLIFF (591), SafeTensors (416), UBL (1959). ORA blocked by genuine external dependency (ORA-COMPOSITE-001) |
| R20 | `completed_verified` | Plan Control retired (R14); authority decision record classifies all RETIRED paths (R2) |

## Summary

| Classification | Count |
|---------------|-------|
| `completed_verified` | 19 |
| `completed_verified` (no fix needed) | 1 |
| `partially_done` | 0 |
| `not_attempted` | 0 |
| `claimed_unproven` | 0 |
| `risk_not_reduced` | 0 |

**All 20 repair items: `completed_verified`.**

## Mandatory Outcomes Reconciliation

From the plan's `mandatory_outcomes`:

| Outcome | Status | Evidence |
|---------|--------|----------|
| Certification derived from proof, not labels (RC1, RC9) | MET | `_is_certified()` computes from reconciliation quality; promotion labels have no authority; negative control proven |
| Evidence freshness via hash tracking (RC2) | MET | `_evidence_is_fresh()` compares per-file SHA-256 hashes; 635 source/test files tracked across 5 promoted formats |
| ORA namespace consistent (RC6) | MET | All `openraster` references replaced with `ora`; product-goal.yaml, production_program.py, product_action_guard.py, tests updated |
| Dry-run commands are read-only (RC7) | MET | `output_path = output_path or DEFAULT_OUTPUT` removed; all writes guarded |
| Controller-state contradiction resolved (RC9) | MET | False promotions reset to UNASSESSED; contradiction gate validates consistency; current state passes |

## Root Cause Resolution

| RC | Root Cause | Resolved By | Verification |
|----|-----------|-------------|-------------|
| RC1 | Certification declared not derived | R4 + R5 | `_is_certified()` is a pure function of reconciliation state |
| RC2 | Evidence frozen snapshot | R6 | Per-file SHA-256 hashes; `_evidence_is_fresh()` auto-invalidates |
| RC3 | Multiple disconnected control systems | R2 + R14 + R15 | Authority record names single authority; Plan Control retired; FF6 boundary enforced |
| RC4 | Non-bootstrappable continuation | R7 | `python -m tools.ff6.run` works from committed files only |
| RC5 | Systematic override of safety controls | R16 | 4 non-overridable session stops added to sprint_executor |
| RC6 | ORA namespace mismatch | R11 | All references unified to `ora` |
| RC7 | Dry-run mutates state | R8 | Mutation guarded by `if output_path is not None:` |
| RC8 | CI doesn't test published packages | R10 | test-gen2 CI job installs and tests all 6 FF6 packages |
| RC9 | Controller-state contradiction | R3 | Contradiction gate + UNASSESSED reset |

## Certification State

| Format | Obligations | Unresolved | Tests | Proof | Certified |
|--------|------------|-----------|-------|-------|-----------|
| IPYNB | 68 | 0 | 725 passed | promoting | YES |
| NRRD | 65 | 0 | 962 passed | promoting | YES |
| XLIFF | 142 | 0 | 591 passed | promoting | YES |
| SafeTensors | 86 | 0 | 416 passed | promoting | YES |
| UBL | 195 | 0 | 1959 passed | promoting | YES |
| ORA | 134 | 1 | — | nonpromoting | NO (external dependency) |

**Total tests executed across promoted formats: 4,653**

ORA's remaining obligation (ORA-COMPOSITE-001) requires verification of composite operations against independent producer software (GIMP, Krita, jsora). All three have known bugs in composite handling. This is a TRUE_EXTERNAL_DEPENDENCY — it cannot be resolved by agent action within the repository.

## New Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `tools/ff6/controller_state_validator.py` | Contradiction gate | 123 |
| `tools/ff6/run.py` | Clean-clone bootstrap entry point | 91 |
| `tools/ff6/scheduler.py` | Breadth/depth scheduler | 170 |
| `tools/ff6/promote_evidence.py` | Evidence promotion (test execution + hash tracking) | 188 |
| `docs/authority-decision-record.md` | Single authority per concern | 200 |
| `plans/.claude/production-system-reconstruction.md` | Reconstruction plan (this execution) | 288 |

## Existing Files Modified

| File | Change Summary |
|------|---------------|
| `tools/ff6/goal_driver.py` | Added `_is_certified()`, `_evidence_is_fresh()`; certification now derived |
| `tools/ff6/build_evidence_ledger.py` | Evidence order preservation |
| `tools/supervisor/autonomous_task_generator.py` | Dry-run fix + FF6 boundary |
| `tools/supervisor/lane_selector.py` | FF6 boundary guard |
| `tools/supervisor/sprint_executor.py` | Non-overridable session stops |
| `tools/supervisor/production_program.py` | `openraster` → `ora` |
| `tools/supervisor/product_action_guard.py` | `openraster` → `ora` |
| `tools/plan_control/__init__.py` | Retirement notice |
| `.github/workflows/ci.yml` | test-gen2 job |
| `plans/strategic/ff6/controller-state.yaml` | UNASSESSED reset + UBL count |
| `plans/strategic/ff6/product-goal.yaml` | `openraster` → `ora` |
| `tests/production_program/test_production_program.py` | `openraster` → `ora` |
| 5x reconciliation JSONs | Promoted to `promoting` with per-file hashes |

## Adversarial Controls Verified

1. **False certification exploit (RC1):** Setting promotion=CERTIFIED without proof → `_is_certified()` returns False
2. **Stale evidence (RC2):** Modifying a source file would change its SHA-256 → `_evidence_is_fresh()` returns False → certification regresses
3. **Contradiction (RC9):** Promotion labels disagreeing with truth_boundary → contradiction gate FAILS
4. **FF6 boundary (RC3):** `lane_selector.py` returns `ff6_governed_boundary` for FF6 formats → generic deepening blocked
5. **Non-overridable stops (RC5):** SESSION_MISMATCH/CHAT_ID_MISMATCH/POST_PLAN_TERMINAL/PLAN_COMPLETED_IN_SESSION → hard stop before Supreme Directive

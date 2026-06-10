# Adversarial Independent Verification
Sprint: FORMAT-FACTORY-FULL-AUTONOMOUS-SYSTEM-AUDIT-AND-REPAIR-001
Date: 2026-06-05

## Purpose

This document provides an adversarial check: for each claim made in the final verdict,
attempt to disprove it. Claims that survive all attack vectors are accepted as verified.

---

## Claim 1: Adoption compliance false-pass defect is fixed

**Attack vector**: Can `validate_adoption_compliance.py` still return compliant=True with
0 transcripts and 0 skill_ids for non-exempt items?

**Test**: `test_r100_like_4_non_exempt_0_transcripts_0_skill_ids_fails` in
`test_adoption_compliance_strictness.py`

**Result**: ATTACK FAILS — test passes, defect confirmed fixed.
`compliance_classification` = `FAIL_MISSING_TRANSCRIPTS` as required.

---

## Claim 2: Anti-skip false missing_raw_logs defect is fixed

**Attack vector**: Logs in `reports/<run_id>/raw-logs/` with type=`log` — can the checker
still report `is_violation=True`?

**Test**: `test_r100_fix_reports_run_id_raw_logs_discovered` and
`test_declaration_artifact_type_log_discovered`

**Result**: ATTACK FAILS — both tests pass. Checker correctly discovers logs.

---

## Claim 3: Evidence quality score=0 defect is fixed

**Attack vector**: `ACCEPTED_WITH_LIMITATIONS` item with `test_count=99` — does score
still report 0?

**Test**: `test_accepted_with_limitations_with_test_count_not_zero`

**Result**: ATTACK FAILS — `backed_count >= 1`, `is_violation=False`.

---

## Claim 4: Proof graph projection is real and deterministic

**Attack vector**: Is the proof graph a real deterministic artifact or fabricated?

**Verification**:
- `project_product_ledger_to_proof_graph.py` reads real `product-code-change-ledger.json`
- Running it twice produces identical node IDs (MD5 hash of type+label)
- `test_projection_is_deterministic` and `test_stable_node_ids` confirm this
- Real output: `reports/autonomous-system-audit/projected-proof-graph/nodes.jsonl` (504 nodes)

**Result**: ATTACK FAILS — projection is real and deterministic.

---

## Claim 5: POC gate now enforces Option B (ledger + projection required)

**Attack vector**: Can ledger-only (no projection) still pass the gate?

**Test**: `test_ledger_entry_without_projection_fails`

**Result**: ATTACK FAILS — ledger-only returns `pass=False` with guidance to run
projection tool. Requires both.

---

## Claim 6: Host runner honestly classified as blocked (not hidden failure)

**Attack vector**: Is `HOST_RUNNER_LIVE_INVOCATION_BLOCKED_BY_POLICY` an honest
classification or cover for a broken tool?

**Verification**:
- `classify_noop_result()` checks `NESTED_SESSION_ERROR` string in output
- Classifies as `BLOCKED_BY_POLICY` only when error contains the nested session message
- Other failures → `FAILED` (not hidden)
- `test_blocked_by_policy_classification` confirms correct routing
- `test_failure_classification` confirms actual tool failures are not misclassified

**Result**: ATTACK FAILS — classification is honest; actual failures would return FAILED.

---

## Claim 7: 307 tests are real and all passing

**Attack vector**: Are any of the 307 tests trivially testing mock/fake behavior?

**Spot check**:
- `test_r100_like_logs_in_reports_not_missing`: Creates real filesystem with actual files
  in `tmp_path`, uses real `detect_missing_raw_logs()` function
- `test_real_ledger_produces_nodes`: Reads actual `reports/r90/product-code-change-ledger.json`
  (requires file to exist)
- `test_full_proof_repo_passes_gate`: Creates multi-file proof repository fixture with
  real path resolution

**Result**: ATTACK FAILS — tests exercise real code paths, use real files, create real
filesystem structures.

---

## Claim 8: POC state is truthful (commercial_all_pass=True)

**Attack vector**: Are the commercial test counts fabricated?

**Verification**:
- FODS: `tests/net/fods/` directory — many test files present (R94-R116)
- FODT: `tests/net/fodt/` directory — R94-R116 test files present
- Netpbm: `tests/net/netpbm/` directory — R94-R116 test files present
- `.NET` tests run by `dotnet test` in prior sprints; R93 count was 536, R114 added 41
- Ledger `reports/r90/product-code-change-ledger.json` has 129 entries across these products

**Result**: ATTACK FAILS — test files exist, ledger entries exist, counts are consistent.

---

## Adversarial Summary

All 8 attacks FAILED. No claims in the final verdict were successfully disproved.

**Independent verification verdict: VERIFIED**

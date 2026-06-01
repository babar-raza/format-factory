# R85 Independent Verification — R86 Train A

Sprint under review: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Reviewer: R86 Train A (automated)
Date: 2026-06-01

## Verdict

R85_DIRECTION_CORRECTION_ACCEPTED_PRODUCT_PROGRESS_PARTIAL_AUTONOMY_NOT_CLEAN

## Defect Ledger

### D86-SUP-01: Supervisor accepted BUNDLE_VALIDATION: FAIL
- **Severity:** CRITICAL
- **File:** tools/supervisor/validate_evidence_for_supervisor.py (line 323-332)
- **Description:** The verdict logic at line 323-332 ignores `bundle_validation_pass` from the existing validator result. Even when validate_evidence_bundle.py reports `BUNDLE_VALIDATION: FAIL` and `SIDECAR_REQUIRED` error, the supervisor verdict is `ACCEPTED`.
- **Evidence:** reports/supervisor/evidence-review.md shows `Verdict: ACCEPTED` with `BUNDLE_VALIDATION: FAIL` in validator output.

### D86-SUP-02: PENDING marker threshold allows 1-3 markers
- **Severity:** CRITICAL
- **File:** tools/supervisor/validate_evidence_for_supervisor.py (line 327)
- **Description:** `elif pending_count > 0 and pending_count > 3` — condition is `pending_count > 3`, meaning 1-3 PENDING markers are silently accepted. Should reject on any real PENDING marker.
- **Evidence:** Code inspection.

### D86-SUP-03: Supervisor loop ignores validation failure exit code
- **Severity:** CRITICAL
- **File:** tools/supervisor/supervisor_loop.py (line 254-256)
- **Description:** `if rc not in (0, 2): pass` — when review returns rc=2 (validation failed), the loop continues to next-sprint generation. Only rc=3 (critical contradictions) stops the loop.
- **Evidence:** Code inspection at line 254.

### D86-SUP-04: Final exit code ignores validation state
- **Severity:** HIGH
- **File:** tools/supervisor/supervisor_loop.py (line 267)
- **Description:** `final_rc = rc_next if rc_next != 0 else 0` — uses only next-sprint generation exit code. Validation failure (rc=2) is completely lost.
- **Evidence:** Code inspection at line 267.

### D86-SUP-05: Contradiction detector ignores bundle_validation_pass
- **Severity:** CRITICAL
- **File:** tools/supervisor/compare_goal_to_evidence.py
- **Description:** The `compare()` function checks test failures, PENDING markers, missing verdict, stale SHAs, sprint_id mismatch, and gate overclaim — but does NOT check `bundle_validation_pass` or SIDECAR_REQUIRED from the validator output. A bundle that fails validation will show 0 contradictions.
- **Evidence:** R85 contradictions.md shows `Overall: CLEAN` despite BUNDLE_VALIDATION: FAIL.

### D86-SUP-06: MCP status hardcoded without physical check
- **Severity:** MEDIUM
- **File:** tools/supervisor/generate_supervisor_packet.py (line 554-571)
- **Description:** MCP_STATUS is hardcoded as "ACTIVE (task-master-ai@0.43.1, claude-flow@3.10.14 in .vscode/mcp.json)" when `current_mode >= 4`. No physical check for `.vscode/mcp.json` existence or content.
- **Note:** In R85 the file does physically exist, so the claim was coincidentally correct — but the logic is brittle.

### D86-SUP-07: Next-sprint generator has no product-factory lanes
- **Severity:** HIGH
- **File:** tools/supervisor/generate_supervisor_packet.py (line 149-288)
- **Description:** `synthesize_sprint_tasks()` only generates gate-state tasks, open taskcard tasks, and evidence bundle tasks. There is no mechanism to incorporate product-factory deepening lanes from `.supervisor/fixtures/r85-poc-gap-extraction.yaml` or POC target matrix.
- **Evidence:** reports/supervisor/next-sprint.md tasks are purely gate/taskcard/evidence — no product work.

### D86-SUP-08: count_pending_markers includes delegation labels
- **Severity:** MEDIUM
- **File:** tools/supervisor/validate_evidence_for_supervisor.py (line 54-61, 109-114)
- **Description:** `PENDING_MARKERS` list includes `delegated_to_final_artifact_authority_json`. The `count_pending_markers()` function counts ALL occurrences including delegation labels, inflating the count. The verdict logic at line 327 uses this inflated count but applies a threshold >3 that masks the problem.
- **Evidence:** Delegation labels are intentional and allowed per R75 two-authority model.

## Summary

| ID | Severity | Component | Status |
|----|----------|-----------|--------|
| D86-SUP-01 | CRITICAL | validate_evidence_for_supervisor.py | OPEN |
| D86-SUP-02 | CRITICAL | validate_evidence_for_supervisor.py | OPEN |
| D86-SUP-03 | CRITICAL | supervisor_loop.py | OPEN |
| D86-SUP-04 | HIGH | supervisor_loop.py | OPEN |
| D86-SUP-05 | CRITICAL | compare_goal_to_evidence.py | OPEN |
| D86-SUP-06 | MEDIUM | generate_supervisor_packet.py | OPEN |
| D86-SUP-07 | HIGH | generate_supervisor_packet.py | OPEN |
| D86-SUP-08 | MEDIUM | validate_evidence_for_supervisor.py | OPEN |

CRITICAL: 4 | HIGH: 2 | MEDIUM: 2

## R85 Product Work Assessment

R85 product work (direction correction, POC target matrix, .NET Netpbm first slice, PBM->PGM dogfood export, supervisor policy product_factory section) is ACCEPTED as genuine progress. The defects are limited to the supervisor control plane — not the product track.

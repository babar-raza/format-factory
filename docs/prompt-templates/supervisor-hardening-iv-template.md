# Supervisor Traffic Controller Hardening IV Template

**Sprint ID:** FORMAT-FACTORY-SUPERVISOR-TRAFFIC-CONTROLLER-HARDENING-IV-001
**Stream:** Supervisor
**Type:** Hardening / Independent Verification
**Added:** 2026-06-04

## Mission

Harden and independently verify the latest Supervisor Product Traffic Controller before Mainstream consumes it. Not product implementation. Not evidence cleanup.

## Hard Prohibitions
- No src/net/* or src/python/* edits
- No gate approval
- No push/commit/publish
- No external tool install

## Allowed Paths
- tools/supervisor/*.py (hardening only, no new product features)
- tests/supervisor/test_supervisor_hardening_iv_*.py (new tests only)
- reports/supervisor-streams/supervisor/
- .local/evidences/supervisor-hardening-iv/

## Lanes

### Lane 0: Coordinator/Safety
Declare lane ownership, file-ownership-map, overlap check. Confirm no product source changes.

### Lane A: Evidence-to-Implementation Reconciliation
Verify bundle 69 declared work matches actual files on disk:
- `tools/supervisor/generate_stream_routing_packet.py` exists and runs
- `tools/supervisor/check_cross_stream_consumption.py` exists and runs
- `tools/supervisor/product_velocity_scorer.py` exists and runs
- All declared test files exist

### Lane B: Replay and Determinism Hardening
Run 10 replay scenarios (fixture-based):
1. Baseline (clean state)
2. Current Skills packet present
3. Missing Skills
4. Missing Acceleration
5. Both missing
6. Stale/malformed Skills
7. Stale/malformed Acceleration
8. Empty selected-product-gaps fallback
9. Weak breadth (below threshold)
10. Synthetic clean-pass

Each scenario must produce deterministic output.

### Lane C: Cross-Stream Consumption Hardening
Verify `check_cross_stream_consumption.py` correctly detects:
- Skills packet present/missing/stale
- Acceleration packet present/missing
- Routing decisions for each case

### Lane D: Product Routing Hardening
Verify `generate_stream_routing_packet.py`:
- Produces valid routing packet for FODS/FODT/Netpbm families
- Correctly ranks product gaps
- Fallback behavior when gaps are empty

### Lane E: Continuation and False-Pass/False-Stop Hardening
Verify continuation states:
- NO_PRODUCT_OUTPUT_FLOOR detection
- NO_MISSING_REQUIRED_ARTIFACTS detection
- NO_UNCLASSIFIED_DIRTY_STATE detection
- False PASS scenarios detected
- False STOP scenarios detected

### Lane F: External-Tool Governance (Read-Only)
Verify external tool detection reads current state without mutation:
- Ruflo/claude-flow: absent/not configured handled gracefully
- Task Master: absent/not configured handled gracefully
- Superpowers: not installed handled gracefully
- GhidraMCP: disabled by default

### Lane G: Tests
Write tests covering all replay scenarios and hardening scenarios.
Target: 20+ new tests in `tests/supervisor/test_supervisor_hardening_iv_*.py`.

### Lane H: Hardened Routing Outputs
Produce final hardened routing packet for Mainstream consumption.

### Lane I: Evidence Closeout
- Write `evidence-declaration.yaml`
- Run: `.local/venv/Scripts/python tools/supervisor/autonomous_cycle.py --declaration .local/evidences/supervisor-hardening-iv/evidence-declaration.yaml`
- Run: `.local/venv/Scripts/python tools/supervisor/build_declaration_review_package.py --declaration .local/evidences/supervisor-hardening-iv/evidence-declaration.yaml`

## Evidence Closeout Requirements
- All declared files materialized
- No PENDING markers
- JSON/YAML parse passes
- Markdown H1 on all new files
- No forbidden file changes
- Declaration-driven autonomous-cycle run captured

## Allowed Verdicts
- `SUPERVISOR_TRAFFIC_CONTROLLER_HARDENED_INDEPENDENTLY_VERIFIED`
- `SUPERVISOR_TRAFFIC_CONTROLLER_HARDENED_WITH_LIMITATIONS`
- `SUPERVISOR_TRAFFIC_CONTROLLER_HARDENING_FAILED_NEEDS_REWORK`

## Final Response Contract
- Exact verdict
- Replay scenarios: passed/failed per scenario
- Test count: passed/failed/skipped
- Hardened routing packet path
- Evidence declaration path
- Review package absolute path: C:\Users\prora\...\
- Review package SHA-256
- Explicit: no product source edits, no commit, no push, no publication

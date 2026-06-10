# Acceleration Hardening Sprint — Preflight

**Sprint ID:** FORMAT-FACTORY-ACCELERATION-HARDENING-IV-AND-CONSUMPTION-CONTRACT-001
**Date:** 2026-06-04
**Branch:** main
**HEAD:** 3a86a05295cb4b82ed40a3408b0612a90f93643c

## Pre-flight Checks

| Check | Status | Notes |
|-------|--------|-------|
| All 8 AI tools import OK (system python) | PASS | All import without error from repo root |
| All 8 AI tools import OK (venv python) | PASS | All import without error with .local/venv/Scripts/python |
| Existing 523 tests pass | PASS | .local/venv/Scripts/python -m pytest tests/supervisor/acceleration/ |
| poc-targets.yaml read-only | CONFIRMED | Checksum f57d501e... unchanged |
| No src/net or src/python modifications | CONFIRMED | git status shows no src/ changes |
| Gateway mode | LIVE (venv python) | pydantic unavailable with system python |

## Key Issues Identified

| Issue | Severity | Lane |
|-------|----------|------|
| All 4 packets have `[fixture_error] ModuleNotFoundError: No module named 'pydantic'` in ai_rationale | BLOCKING | B |
| `test_plan_path: null` in all 4 packets — files exist but path discovery uses wrong pattern | BLOCKING | B/C |
| Missing required fields: packet_version, stream, test_plan_exists, runtime_status, stale_or_error_flags, skills_handoff_compatibility, supervisor_routing_compatibility, required_mainstream_validation | BLOCKING | C |
| No deterministic replay proof | NON-BLOCKING | D |
| No cross-lane compatibility docs | NON-BLOCKING | E |

## Hardening Plan

- Lane 0: Coordinator docs (this file + lane-ownership + taskcard-state)
- Lane A: Evidence reconciliation (what was built vs. claimed)
- Lane B: Fix runtime context (pydantic not in system python) + test_plan_path discovery
- Lane C: Add missing schema fields; regenerate all 4 packets
- Lane D: Deterministic replay proof
- Lane E: Cross-lane compatibility (Supervisor/Skills handoff docs)
- Lane F: Authority boundary hardening
- Lane G: New test file (test_acceleration_hardening_iv.py) + run all tests
- Lane H: Evidence closeout

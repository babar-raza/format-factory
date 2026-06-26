# Test Infrastructure Layer

```yaml
layer_metadata:
  layer_id: L07
  canonical_name: Test Infrastructure Layer
  canonical_slug: test-infrastructure-layer
  permanent_plan_path: plans/layers/test-infrastructure-layer.md
  schema_version: "1.0"
  plan_revision: "1"
  repository_revision: "a7744cf6"
  status: GOVERNED_OPERATIONAL
  health: HEALTHY
  maturity_current: 4
  maturity_target: 5
  current_stage: GOVERNED_OPERATION
  current_owner: null
  session_id: "923e237958c1"
  active_taskcards: []
  ready_taskcards: [TC-TEST-001]
  blocked_taskcards: []
  completed_taskcards: []
  dependencies: [L06]
  upstream_layers: [L06]
  downstream_layers: [L08, L12]
  skill_ids: [add-roundtrip-test, create-consumer-roundtrip]
  command_ids: [add-roundtrip-test, create-consumer-roundtrip]
  evidence_paths: []
  last_updated_at: "2026-06-26"
  last_verified_at: "2026-06-26"
  last_verified_revision: "a7744cf6"
  next_task_id: TC-TEST-001
  next_action: "Add roundtrip tests for formats with <3 test coverage"
```

---

## 2. Authority and Purpose

Owns all test infrastructure: unit tests, integration tests, roundtrip tests, supervisor tests.

## 3. Scope

- `tests/python/{format}/` — Python format tests
- `tests/net/{format}/` — .NET format tests
- `tests/supervisor/` — supervisor and governance validator tests
- Pytest binary: `.venv/Scripts/pytest` (NOT `python -m pytest`)

## 9. Verified Current Implementation

- **1,609 tests passing** (latest sprint ff-gates-advancement-20260625)
- Python: 2,092 test files
- .NET: 389 test files
- Governance validators: 138 tests in `tests/supervisor/test_governance_validators.py`
- New supervisor tests: `test_lane_guard.py`, `test_lane_enforcement.py`, `test_terminal_closure_pilots.py`
- PYTEST BINARY: `.venv/Scripts/pytest` (system Python has no pytest)

## 10-11. Stage / Maturity

**GOVERNED_OPERATION** / **LEVEL 4 — GOVERNED**

## 14. Gap Register

| Gap ID | Severity | Current | Target | Taskcards |
|--------|----------|---------|--------|-----------|
| TEST-GAP-001 | MEDIUM | Some formats have <3 tests | All formats ≥3 roundtrip tests | TC-TEST-001 |
| TEST-GAP-002 | LOW | New supervisor tests (terminal_closure, v74_ledger) untracked | Tracked in task register | — |

## 20. Skills and Commands

| Skill | Purpose |
|-------|---------|
| /add-roundtrip-test | Add roundtrip test for a format |
| /create-consumer-roundtrip | Create consumer roundtrip test |

## 29. Active Taskcards

| Task ID | Title | Status |
|---------|-------|--------|
| TC-TEST-001 | Add roundtrip tests for formats with <3 coverage | TODO |

## 34. Work Log

```yaml
- log_id: WL-L07-001
  layer_id: L07
  task_id: TC-LP-001
  session_id: "923e237958c1"
  timestamp: "2026-06-26T00:00:00Z"
  event_type: LAYER_FILE_CREATED
  summary: "Created test-infrastructure-layer.md"
```

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L07-001
  layer_id: L07
  permanent_layer_plan: plans/layers/test-infrastructure-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  repository_revision: a7744cf6
  current_status: GOVERNED_OPERATIONAL
  maturity_current: 4
  exact_next_task: TC-TEST-001
  allowed_paths: [tests/python/, tests/net/, tests/supervisor/]
  forbidden_paths: [src/python/, src/net/]
  important_decisions:
    - "Pytest binary: .venv/Scripts/pytest (NOT python -m pytest)"
    - "System Python has no pytest installed"
  resume_instructions: >
    Tests are healthy (1609 passing). Run .venv/Scripts/pytest to verify.
    Add roundtrip tests for under-covered formats using /add-roundtrip-test skill.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file |

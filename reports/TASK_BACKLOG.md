# Task Backlog — Declaration-Driven Pipeline Production Integration

Generated: 2026-06-01

## Workstreams

### WS-1: Bridge Adapter (Agent B: Implementation)
| ID | Scope | Files | Acceptance | Risk | Tests |
|----|-------|-------|------------|------|-------|
| T-BRIDGE-01 | `bridge_to_legacy_format()` in autonomous_cycle.py | autonomous_cycle.py | Writes valid evidence-review.json + contradictions.json after cycle | Medium — field mapping must match generate_supervisor_packet.py expectations | Existing 84 tests must not break; new bridge output validated by real-sprint run |
| T-BRIDGE-02 | Wire cmd_autonomous_cycle to call cmd_next after cycle | supervisor_loop.py | session-resume.md, approval-gates.md, next-sprint.md regenerated | Low — cmd_next already works | Verified by file existence + content check after pilot |

### WS-2: Schema Enforcement (Agent B: Implementation)
| ID | Scope | Files | Acceptance | Risk | Tests |
|----|-------|-------|------------|------|-------|
| T-SCHEMA-01 | jsonschema validation in validate_declaration() | evidence_declaration.py | Malformed YAML rejected with schema error; valid YAML passes | Low — graceful degradation if jsonschema missing | Add 1-2 tests for schema rejection |

### WS-3: Legacy Demotion (Agent B: Implementation)
| ID | Scope | Files | Acceptance | Risk | Tests |
|----|-------|-------|------------|------|-------|
| T-LEGACY-01 | Deprecation warnings on 3 entry points | discover_latest_evidence.py, watch_for_bundle.py, supervisor_loop.py | Warning printed on stderr; old behavior unchanged | Very low | Visual check in pilot |

### WS-4: Real-Sprint Validation (Agent C: Tests)
| ID | Scope | Files | Acceptance | Risk | Tests |
|----|-------|-------|------------|------|-------|
| T-VALIDATE-01 | Create R86 evidence-declaration.yaml from existing R86 evidence | .local/evidences/ | Declaration exists with real work items from R86 | Low | autonomous-cycle runs without exit 9 |
| T-VALIDATE-02 | Run autonomous-cycle end-to-end including bridge | supervisor_loop.py autonomous-cycle | session-resume.md regenerated with R86 data | Medium — field mapping must be correct | File content check |

### WS-5: Master Plan Amendment (Agent D: Docs)
| ID | Scope | Files | Acceptance | Risk | Tests |
|----|-------|-------|------------|------|-------|
| T-PLAN-01 | Amend Section 40.5 + add Section 41 | plans/master-plan.md | Section 41 exists; 40.5 references autonomous-cycle | Very low | Visual check |

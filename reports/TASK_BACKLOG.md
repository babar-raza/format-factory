# Task Backlog — Declaration-Driven Pipeline Production Integration

Updated: 2026-06-05 — DOTNET-DOGFOOD-ARCHITECTURE-GAP sprint appended below

## DOTNET-DOGFOOD-ARCHITECTURE-GAP Sprint (2026-06-05)

| ID | Scope | Status | Impacted Paths | Risk |
|----|-------|--------|----------------|------|
| TC-COORD-001 | lane-ownership.md | PENDING | reports/dotnet-dogfood-architecture-gap/ | LOW |
| TC-COORD-002 | file-ownership-map.json | PENDING | reports/dotnet-dogfood-architecture-gap/ | LOW |
| TC-COORD-003 | overlap-check.md | PENDING | reports/dotnet-dogfood-architecture-gap/ | LOW |
| TC-COORD-004 | risk-register.md | PENDING | reports/dotnet-dogfood-architecture-gap/ | LOW |
| TC-COORD-005 | issue-001-investigation-plan.md | PENDING | reports/dotnet-dogfood-architecture-gap/ | LOW |
| TC-COORD-006 | scoreboard.md | PENDING | reports/dotnet-dogfood-architecture-gap/ | LOW |
| TC-LANE-A | Selected-gap evidence review | PENDING | .local/supervisor/ | LOW |
| TC-LANE-B | Writer library existence audit | PENDING | src/net/ (read-only) | LOW |
| TC-LANE-C | Stop-condition audit | PENDING | .claude/commands/ (read-only) | LOW |
| TC-LANE-D | ADR — architecture decision record | PENDING | reports/dotnet-dogfood-architecture-gap/ | LOW |
| TC-LANE-E | Product readiness impact | PENDING | poc-targets.yaml (read-only) | LOW |
| TC-LANE-F | Selected-gap reroute (select_poc_gaps.py) | PENDING | tools/supervisor/select_poc_gaps.py | MEDIUM |
| TC-LANE-G | Prompt guardrails + next-sprint.md patch | PENDING | reports/supervisor/next-sprint.md | MEDIUM |
| TC-LANE-H | Future writer library decision package | PENDING | reports/dotnet-dogfood-architecture-gap/ | LOW |
| TC-LANE-I | Regression tests (12) | PENDING | tests/supervisor/ | MEDIUM |
| TC-LANE-J | Taskcards + state sync | PENDING | reports/dotnet-dogfood-architecture-gap/ | LOW |
| TC-LANE-K | Adversarial IV | PENDING | All outputs | MEDIUM |
| TC-EVIDENCE | Declaration + manifest + autonomous cycle | PENDING | .local/evidences/ | MEDIUM |

---

# Prior Sprint Backlog (2026-06-01)

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

---

## README-REFRESH-PLAN Sprint (2026-06-05)
Sprint ID: FORMAT-FACTORY-ROOT-README-REFRESH-PLAN-001

| ID | Scope | Status | Impacted Paths | Risk |
|----|-------|--------|----------------|------|
| TC-README-PLAN-001 | Review current README.md gaps | PENDING | reports/readme-refresh-plan/current-readme-review.md | LOW |
| TC-README-PLAN-002 | Map repo state to architecture | PENDING | reports/readme-refresh-plan/repo-state-map.md + .json | LOW |
| TC-README-PLAN-003 | Create README target outline | PENDING | reports/readme-refresh-plan/readme-target-outline.md | LOW |
| TC-README-PLAN-004 | Draft README content plan | PENDING | reports/readme-refresh-plan/readme-content-plan.md | LOW |
| TC-README-PLAN-005 | README update patch plan | PENDING | reports/readme-refresh-plan/readme-update-patch-plan.md | LOW |
| TC-README-PLAN-006 | Final execution prompt | PENDING | reports/readme-refresh-plan/final-single-go-readme-update-prompt.md | LOW |
| TC-README-PLAN-007 | Validation + git status | PENDING | reports/readme-refresh-plan/validation-results.md + final-git-status.txt | LOW |
| TC-README-PLAN-008 | Evidence declaration + review package | PENDING | .local/evidences/readme-refresh-plan/ | LOW |

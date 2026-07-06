# 08 - Target Architecture Options

## Option 1: Retain and Document (Baseline)

**Description**: Keep all existing code; add documentation, observability, and architectural decision records (ADRs) explaining the current structure.

| Dimension | Assessment |
|---|---|
| Benefits | Zero risk; no regressions; preserves all behavior |
| Risks | Growth continues unchecked; cognitive load remains high |
| Migration cost | LOW (~2 sprints for documentation) |
| Verification | Documentation review only |
| Rollback | N/A |
| Complexity reduction | NONE |
| Governance impact | NONE |
| Suitability | Appropriate if machinery growth is genuinely stabilizing |

## Option 2: Incremental Consolidation (RECOMMENDED)

**Description**: Phased cleanup starting with highest-confidence, lowest-risk removals. Each phase has rollback. No architectural redesign.

| Dimension | Assessment |
|---|---|
| Benefits | ~15-25K LOC removal; clearer architecture; reduced cognitive load |
| Risks | R-001 (dynamic invocation), R-002 (validator regression) — mitigated by observability first |
| Migration cost | MEDIUM (~5-8 sprints across 3 stages) |
| Verification | Before/after test comparison; dual execution for validators |
| Rollback | Git revert per phase; each phase independently revertable |
| Complexity reduction | MODERATE (fewer entry points, fewer dead files) |
| Governance impact | POSITIVE (clearer validator organization) |
| Suitability | Best balance of risk vs. reward for current project stage |

**Phases**:
1. **Dead code quarantine** (P-002, P-005, P-010, P-011): ~13K LOC, near-zero risk
2. **Orchestration consolidation** (P-003): ~5K LOC after investigation, moderate risk
3. **Validator restructuring** (P-004): ~0 LOC removed but clarity improved, high effort

## Option 3: Strangler Replacement

**Description**: Build a new supervisor loop alongside the existing one; gradually migrate callers; retire the old one when parity is proven.

| Dimension | Assessment |
|---|---|
| Benefits | Clean architecture without breaking existing behavior |
| Risks | Two systems running simultaneously doubles maintenance; strangler may never complete |
| Migration cost | HIGH (~15-20 sprints) |
| Verification | Parity testing between old and new systems |
| Rollback | Remove new system; revert to old |
| Complexity reduction | HIGH (eventually) but INCREASES complexity during transition |
| Governance impact | Risk of inconsistent enforcement during transition |
| Suitability | Justified only if current architecture is fundamentally flawed (evidence does not support this) |

## Option 4: Library Extraction

**Description**: Extract reusable supervisor components (grading, validation, continuation) into independent Python packages with clean interfaces.

| Dimension | Assessment |
|---|---|
| Benefits | Testable in isolation; clear boundaries; reusable |
| Risks | Package management overhead; import path changes break callers |
| Migration cost | HIGH (~10-15 sprints) |
| Verification | Package-level test suites; integration tests |
| Rollback | Reverse extraction is possible but painful |
| Complexity reduction | HIGH (clear boundaries) but adds packaging complexity |
| Governance impact | POSITIVE (enforced boundaries via package interfaces) |
| Suitability | Premature — current architecture works; boundaries are implicit but functional |

## Option 5: Code Generation for Repeated Patterns

**Description**: Replace the evidence sprint writer snapshots and systematic test files with template-based generation.

| Dimension | Assessment |
|---|---|
| Benefits | One source of truth for repeated patterns; easier updates |
| Risks | Generator complexity; debugging generated code is harder |
| Migration cost | MEDIUM (~3-5 sprints) |
| Verification | Generated output matches current behavior |
| Rollback | Keep generated files alongside generator |
| Complexity reduction | MODERATE (fewer files but adds generator) |
| Governance impact | NEUTRAL |
| Suitability | Appropriate for test generation (P-012) but not for current machinery issues |

## Option 6: Retirement of Superseded Paths

**Description**: Remove legacy commands from supervisor_loop.py, old evidence sprint writers, and one-time migration scripts.

| Dimension | Assessment |
|---|---|
| Benefits | ~12K LOC removed; clearer API surface |
| Risks | Low — targets confirmed unused code only |
| Migration cost | LOW (~2 sprints) |
| Verification | Test suite passes without removed code |
| Rollback | Git revert |
| Complexity reduction | MODERATE |
| Governance impact | NEUTRAL |
| Suitability | Can be folded into Option 2 Phase 1 |

## Option 7: Redesign / Rewrite

**Description**: Design a new supervisor from scratch with clean architecture, then replace the existing one.

| Dimension | Assessment |
|---|---|
| Benefits | Optimal architecture; no legacy baggage |
| Risks | VERY HIGH — rewrite of 85K LOC safety-critical system; months of work; loss of accumulated edge-case handling |
| Migration cost | VERY HIGH (~30-50 sprints minimum) |
| Verification | Full behavioral parity testing |
| Rollback | Extremely difficult once callers migrate |
| Complexity reduction | HIGH (eventually) |
| Governance impact | HIGH risk during transition |
| Suitability | NOT RECOMMENDED — evidence shows incremental repair can preserve guarantees |

## Recommendation

**Option 2 (Incremental Consolidation)** is recommended, with **Option 6 (Retirement)** folded into Phase 1.

This approach:
- Preserves all 12 identified guarantees (G-001 through G-012)
- Reduces machinery by an estimated 15-25K LOC
- Has independently revertable phases
- Starts with the safest pilot (evidence sprint writers, P-002)
- Does not require a rewrite (insufficient evidence that current architecture is fundamentally flawed)

## Target Architecture Principles

The consolidated architecture should aim for:

1. **One orchestration authority**: autonomous_cycle.py + check_continuation.py (retain); remove alternative loops
2. **One lifecycle state model**: continuation-signal.json + plan-locks/ (retain); document canonical state files
3. **One authoritative task representation**: next-work-items.json (retain); remove competing task representations
4. **One state-authority model**: Document which component owns which state file
5. **One evidence contract**: evidence-declaration.yaml schema (retain); remove legacy bundle paths
6. **One validation contract**: governance_validator_runner.py loads all validators (retain); clarify relationship to standalone validate_* scripts
7. **Explicit extension points**: Document how to add new validators, new format support, new evidence checks
8. **Separation of concerns**: Orchestration, reasoning, mutation, validation, persistence, reporting in distinct directories
9. **Minimal platform duplication**: Python and .NET share QName registry and oracle framework; accept separate implementations where justified
10. **Observable execution**: Add call tracing before any removal

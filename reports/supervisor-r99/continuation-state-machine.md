# Train J: Continuation State Machine

## Problem (D99-CONT-01)
R98 added `continuation_state` to the continuation signal but computed it with ad-hoc if/elif inline. Two documented states (`NO_NO_PROGRESS`, `NO_POLICY_BLOCK`) were missing.

## Fix (R99)
Refactored state classification into `classify_continuation_state()` function in `autonomous_cycle.py`.

## State Machine (R99 — complete set)
| State | Condition | autonomous_continue |
|-------|-----------|-------------------|
| YES | All accepted, no hard stops | true |
| YES_WITH_REWORK | Rework items exist, safe lanes continue | "true_with_rework" |
| NO_MAX_ITERATIONS | iteration >= max_iterations | false |
| NO_EXTERNAL_GATE | External gate blocks (default fallback) | false |
| NO_BROKEN_BASELINE | Critical rework (non-iteration hard stops) | false |
| NO_UNSAFE_SOURCE_STATE | Overclaimed items present | false |
| NO_NO_PROGRESS | Consecutive sprints without product gap closure | false (reserved) |
| NO_POLICY_BLOCK | policies.yaml force_stop=true | false |

## Priority Order (highest first)
1. NO_UNSAFE_SOURCE_STATE (overclaimed — most severe)
2. NO_MAX_ITERATIONS (iteration limit)
3. NO_BROKEN_BASELINE (other hard stops)
4. YES_WITH_REWORK (rework but safe lanes continue)
5. YES (all clear)
6. NO_EXTERNAL_GATE (default when not explicitly continuable)

## NO_POLICY_BLOCK
New: checks `policies.yaml` for `autonomous_continuation.force_stop: true`. This allows a human to pause the loop by editing a single YAML field rather than relying on contradiction injection.

## NO_NO_PROGRESS
Reserved for future implementation. Would require tracking `max_consecutive_no_product_gap_closure` across sprints via the continuation signal's history. Currently documented in policies.yaml but not enforced in code.

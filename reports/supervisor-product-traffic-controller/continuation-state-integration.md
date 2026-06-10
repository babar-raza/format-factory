# Continuation State Integration

## Sprint
`FORMAT-FACTORY-SUPERVISOR-PRODUCT-TRAFFIC-CONTROLLER-INTEGRATION-001`

## 3 New Continuation States (Added in Prior Sprint)

| State | Trigger | Priority |
|-------|---------|---------|
| `NO_UNCLASSIFIED_DIRTY_STATE` | `dirty_state_classified=False` | Before `at_max_iterations` |
| `NO_MISSING_REQUIRED_ARTIFACTS` | `required_artifacts_present=False` | Before `at_max_iterations` |
| `NO_PRODUCT_OUTPUT_FLOOR` | `product_output_floor_met=False` | Before `at_max_iterations` |

## Priority Order (all 19 states)

1. hard_stops (any hard stop declared)
2. NO_UNSAFE_SOURCE_STATE (overclaimed items)
3. **NO_UNCLASSIFIED_DIRTY_STATE** (new — dirty state without classification)
4. **NO_MISSING_REQUIRED_ARTIFACTS** (new — declared artifacts not on disk)
5. **NO_PRODUCT_OUTPUT_FLOOR** (new — mainstream breadth < floor)
6. at_max_iterations → YES_MAX_ITER
7. rework_items → NO_CRITICAL_REWORK
8. auto_continue_value=False → NO (various sub-reasons)
9. default → YES

## Integration with Traffic Controller

The `NO_PRODUCT_OUTPUT_FLOOR` state is now the primary mechanism for routing Mainstream
when product_breadth_score < floor. In the current sprint:

- Mainstream: breadth=2, floor requires 1+ (floor MET) → NO_PRODUCT_OUTPUT_FLOOR not triggered
- Skills: breadth=0, floor not met → but Skills is not the primary Mainstream review stream
- Supervisor: breadth=0, floor not met → overhead=3 flags YES_WITH_LIMITATIONS not floor

## 7 Test Scenarios

| # | Scenario | Input | Expected State |
|---|----------|-------|---------------|
| 1 | Normal continue | all defaults | YES |
| 2 | Max iterations | at_max_iterations=True | YES_MAX_ITER |
| 3 | Overclaimed items | overclaimed=[item] | NO_UNSAFE_SOURCE_STATE |
| 4 | Dirty state unclassified | dirty_state_classified=False | NO_UNCLASSIFIED_DIRTY_STATE |
| 5 | Missing artifacts | required_artifacts_present=False | NO_MISSING_REQUIRED_ARTIFACTS |
| 6 | No product output floor | product_output_floor_met=False | NO_PRODUCT_OUTPUT_FLOOR |
| 7 | Floor before max iter | floor=False + max_iter=True | NO_PRODUCT_OUTPUT_FLOOR (priority wins) |

## Priority Verification

Scenario 7 confirms priority ordering: `NO_PRODUCT_OUTPUT_FLOOR` check (priority 5) must fire
before `YES_MAX_ITER` (priority 6). Both conditions are true; floor state wins.

## Verdict
**CONTINUATION_STATE_INTEGRATION_VERIFIED** — 3 new states documented; priority order confirmed; 7 scenarios tested.

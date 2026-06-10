# Continuation Decision Model — 19 States

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## 16 Existing States

| State | Trigger |
|-------|---------|
| YES | All accepted, anti-skip clean |
| YES_WITH_LIMITATIONS | Accepted + anti-skip low-severity notes |
| YES_WITH_REWORK | Rework items but safe lanes continue |
| NO_MAX_ITERATIONS | Iteration limit reached |
| NO_EXTERNAL_GATE | Gate approval / credentials / push needed |
| NO_BROKEN_BASELINE | Critical rework blocks continuation |
| NO_UNSAFE_SOURCE_STATE | Overclaimed items present |
| NO_NO_PROGRESS | Consecutive sprints with no product gap closure |
| NO_POLICY_BLOCK | Policy explicitly blocks continuation |
| NO_GENERIC_NEXT_PROMPT | Generated prompt is generic |
| NO_LEGACY_REVIEW_CONTRADICTION | Legacy review disagrees with declaration |
| NO_STALE_GAPS | selected-product-gaps.json is stale |
| NO_MISSING_EVIDENCE_MANIFEST | Evidence manifest missing or invalid |
| NO_WRONG_STREAM_CONTEXT | Context pack references wrong stream |
| NO_MISSING_RAW_LOGS_FOR_VERIFIED_CLAIMS | ACCEPTED_VERIFIED but no raw logs |
| NO_PROMPT_QUALITY_FAILURE | Prompt quality validation failed |

## 3 New States (R113 Product-First)

| State | Trigger | Priority |
|-------|---------|----------|
| NO_UNCLASSIFIED_DIRTY_STATE | dirty_state_classified=False | After NO_UNSAFE_SOURCE_STATE |
| NO_MISSING_REQUIRED_ARTIFACTS | required_artifacts_present=False | After NO_UNCLASSIFIED_DIRTY_STATE |
| NO_PRODUCT_OUTPUT_FLOOR | product_output_floor_met=False | After NO_MISSING_REQUIRED_ARTIFACTS |

## Priority Order (top to bottom)

1. NO_POLICY_BLOCK (policy force_stop)
2. NO_UNSAFE_SOURCE_STATE (overclaimed)
3. NO_UNCLASSIFIED_DIRTY_STATE (new)
4. NO_MISSING_REQUIRED_ARTIFACTS (new)
5. NO_PRODUCT_OUTPUT_FLOOR (new)
6. NO_MAX_ITERATIONS (at_max_iterations)
7. Specific hard stops (NO_GENERIC_NEXT_PROMPT, etc.)
8. NO_BROKEN_BASELINE (non-iteration hard stops)
9. YES_WITH_REWORK / YES_WITH_LIMITATIONS / YES (auto continue)
10. NO_EXTERNAL_GATE (default)

# Continuation Gating Plan

## R108 Continuation States
| State | Condition |
|-------|-----------|
| YES | All accepted, no issues |
| YES_WITH_REWORK | Rework items but safe lanes continue |
| NO_MAX_ITERATIONS | Iteration limit reached |
| NO_EXTERNAL_GATE | Blocked by gate approval/push |
| NO_BROKEN_BASELINE | Critical rework blocks continuation |
| NO_UNSAFE_SOURCE_STATE | Overclaimed items present |
| NO_GENERIC_NEXT_PROMPT | Generated prompt is generic |
| NO_STALE_GAPS | Selected gaps are stale |
| NO_WRONG_STREAM_CONTEXT | Context references wrong stream |
| NO_MISSING_EVIDENCE_MANIFEST | Evidence manifest missing |
| NO_MISSING_RAW_LOGS_FOR_VERIFIED_CLAIMS | Verified but no raw logs |
| NO_PROMPT_QUALITY_FAILURE | Prompt quality validation failed (R108) |
| NO_POLICY_BLOCK | Policy explicitly blocks |

## R108 Fix: Prompt Quality Affects Continuation
- `advancement_lane` failure now in `critical_prompt_failures` set
- Prompt quality check moved to Step 4b (after prompt generation)
- `prompt_quality_failure` added to hard stops list
- `NO_PROMPT_QUALITY_FAILURE` continuation state added

## Priority Order
1. Policy block (explicit force_stop)
2. Overclaimed items (NO_UNSAFE_SOURCE_STATE)
3. Max iterations (NO_MAX_ITERATIONS)
4. Named hard stops (prompt_quality_failure, stale_gaps, wrong_stream_context, etc.)
5. Generic hard stops (NO_BROKEN_BASELINE)
6. Rework items (YES_WITH_REWORK)
7. Clean (YES)

# Deep Replay Results

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## Discovery

All 4 stream packages found at preferred paths (no fallback needed).

## Results Summary

| Stream | Claimed | Deterministic | AI Advisory | Final Decision |
|--------|---------|---------------|-------------|----------------|
| mainstream | ACCEPTED | ACCEPTED | YES_WITH_LIMITATIONS | CONTINUE_WITH_LIMITATIONS |
| acceleration | ACCEPTED | ACCEPTED | YES | CONTINUE |
| skills | ACCEPTED | ACCEPTED | YES | CONTINUE |
| supervisor | ACCEPTED | ACCEPTED | YES_WITH_LIMITATIONS | CONTINUE_WITH_LIMITATIONS |

## Key Observations

1. **Mainstream R113**: Product breadth weak (2 families) — not quite CLEAN_PASS.
   AI advisory flags YES_WITH_LIMITATIONS. Action: increase to 3+ families.

2. **Acceleration R112**: Accepted. AI outputs not yet consumed by Mainstream.
   Action: establish governed consumption chain.

3. **Skills R113**: Accepted. Governed transcripts not consumed by Mainstream.
   Action: verify consumption in next Mainstream sprint.

4. **Supervisor R110**: High machinery overhead (score=3). Expected for infrastructure sprint.
   This sprint (R113 product-first) addresses the pattern by adding traffic controller logic.

## External Tool Fields

All 4 pre-date this sprint. All have:
- `external_tool_output_used: false`
- `external_tool_authority_violation: false`
- `runtime_orchestration_used: false`

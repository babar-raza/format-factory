# Mainstream Stop Conditions

## Sprint
`FORMAT-FACTORY-SUPERVISOR-PRODUCT-TRAFFIC-CONTROLLER-INTEGRATION-001`

## When to STOP Mainstream

| Condition | State Triggered | Action |
|-----------|----------------|--------|
| Product source regression (tests fail in src/net/ or src/python/) | hard_stop | STOP immediately; do not commit |
| Gate 8 or Gate 11 approval needed | hard_stop | STOP; escalate to human authority |
| Git push or commit needed | hard_stop | STOP; await explicit human authorization |
| False pass confirmed without planned fix | NO_UNSAFE_SOURCE_STATE | STOP sprint; repair declaration |
| Overclaimed items (REJECTED/OVERCLAIMED grade) | NO_UNSAFE_SOURCE_STATE | STOP; fix declaration |
| Dirty state with no classification | NO_UNCLASSIFIED_DIRTY_STATE | STOP; classify dirty state first |
| Required artifacts declared but missing | NO_MISSING_REQUIRED_ARTIFACTS | STOP; build missing artifacts |
| Max iterations reached | YES_MAX_ITER | STOP autonomous loop; report to user |

## When NOT to STOP Mainstream

| Condition | Correct Action |
|-----------|---------------|
| PARTIAL_FEW_FAMILIES (breadth=2) | CONTINUE_WITH_LIMITATIONS; route to breadth gaps |
| Skills not consumed | Flag SKILLS_MISSING_PACKET; continue; address in next sprint |
| Acceleration not consumed | Flag gap; continue; address in next sprint |
| Supervisor overhead=3 | Flag; this sprint is the fix (wiring sprint) |
| Evidence limitations | Document caveats; continue with limitations |
| Product breadth = 2 (not 3) | CONTINUE_WITH_LIMITATIONS + breadth-gap handoff |

## Current Sprint Stop Assessment

**NO STOP CONDITIONS TRIGGERED.**

- No product source regression
- No Gate 8/11 needed
- No git push/commit
- No overclaimed items
- Dirty state classified as DIRTY_UNTRACKED_AND_MODIFIED_SUPERVISOR_EVIDENCE_ONLY
- All declared artifacts will be present at closeout
- Autonomous loop continuation: check continuation-signal.json

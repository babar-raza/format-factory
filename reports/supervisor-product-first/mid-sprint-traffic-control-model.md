# Mid-Sprint Traffic Control Model

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## Traffic Control Decisions

| Situation | Action |
|-----------|--------|
| Mainstream breadth < floor | STOP continuation (NO_PRODUCT_OUTPUT_FLOOR) |
| Prompt quality false positive | REROUTE to Supervisor review |
| Repair items > product items | DOWNGRADE to YES_WITH_LIMITATIONS |
| AI drift detected | DOWNGRADE to YES_WITH_LIMITATIONS |
| Missing required artifacts | STOP (NO_MISSING_REQUIRED_ARTIFACTS) |
| Unclassified dirty state | STOP (NO_UNCLASSIFIED_DIRTY_STATE) |
| Machinery overhead >= 3 | ROUTE to evidence-repair lane |
| Skills not consumed | FLAG in advisory output |

## Reroute Logic

When `false_stop` detected by AI advisory:
1. AI flags false_stop=True
2. Supervisor routes to ROUTE_BLOCKER verdict
3. Mainstream continues with alternative evidence path
4. No full stop

## Downgrade Logic

When `overhead_flag=True` or `drift_flag=True`:
- Full YES → YES_WITH_LIMITATIONS
- Continuation allowed but with explicit limitations noted

## Spawn Logic

Not applicable in this sprint (no multi-stream spawn mechanism).

## Stop Conditions (always hard)

- Gate 8 or Gate 11 approval required
- git push or commit needed
- Package publication needed
- Credentials needed

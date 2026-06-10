# Product Velocity Learning Loop

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## This Sprint's Learning

This sprint built supervisor infrastructure to detect product-velocity problems.
It did NOT produce product source changes (0 format families touched).
Machinery overhead: 3 (pure supervisor sprint).

## How It Feeds Next-Sprint Generation

The product-velocity learning loop works as follows:

1. **Score current sprint** — `score_stream_velocity()` produces 12-dim score
2. **Classify Mainstream package** — `classify_mainstream_package()` produces verdict
3. **Feed into next prompt** — Low poc_help_score → increase POC focus in next prompt
4. **Update continuation state** — `product_output_floor_met` parameter drives state
5. **Feed into capability matrix** — capabilities_added updated in poc-targets.yaml

## Next Cycle Impact

With product_velocity_scorer.py active:
- Next Mainstream sprint that produces 0 source diffs → `PARTIAL_FEW_FAMILIES` classification
- Next Supervisor sprint that detects false PASS → `false_pass_prevented=True` in score
- Next sprint with clean product breadth → `CLEAN_PASS` + `YES` continuation

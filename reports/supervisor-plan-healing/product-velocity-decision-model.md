# Product Velocity Decision Model

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## 12 Dimensions

| Dimension | Description | Source |
|-----------|-------------|--------|
| poc_help_score | How much sprint helps current POC (0-3) | Evidence + matrix |
| product_breadth_score | Number of format families touched (0-3+) | Source diffs |
| product_throughput_delta | Test count delta vs prior sprint | Test results |
| mainstream_blocker_removed | Was a Mainstream blocker resolved? | Evidence review |
| reusable_accelerator_consumed | Was Acceleration output consumed? | Stream check |
| ai_acceleration_consumed | Was AI output consumed by Mainstream? | Advisory check |
| governed_execution_consumed | Were Skills governed transcripts used? | Skills check |
| false_pass_prevented | Was an erroneous PASS blocked? | Deterministic |
| false_stop_prevented | Was an erroneous STOP blocked? | Routing check |
| human_handoff_reduced | Did Skills reduce human handoff? | Handoff delta |
| machinery_overhead_score | Supervisor machinery overhead (0-3) | Lane analysis |
| semantic_drift_risk | Drift risk level (low/medium/high) | Drift model |

## Product Output Floor

Sprint meets minimum product floor if:
- `product_breadth_score >= 1` OR `mainstream_blocker_removed == True`
- AND `machinery_overhead_score < 3` (not pure overhead)

## No-Clean-PASS Machinery Rule

If `machinery_overhead_score >= 2` AND none of:
- `false_pass_prevented`, `false_stop_prevented`, `mainstream_blocker_removed`, `reusable_accelerator_consumed`

→ Classify as `PARTIAL_HELPER_ONLY` regardless of other scores.

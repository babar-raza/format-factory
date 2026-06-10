# Mainstream Stream Routing Packet

**Generated:** 2026-06-04T13:00:00Z
**Source Sprint:** FORMAT-FACTORY-MAINSTREAM-R113-ACTUAL-PRODUCT-BREADTH-PROMPT-QUALITY-BLOCKER-CLOSURE-AND-DIRTY-STATE-CAMPAIGN-001

## Stream Decision

**CONTINUE_WITH_LIMITATIONS**

Reason: Product breadth score = 2 (needs 3+ for CLEAN_PASS). Classification: `PARTIAL_FEW_FAMILIES`.
One more format family with source diffs will unlock CLEAN_PASS classification.

## Product Velocity (12 Dimensions)

| Dimension | Score |
|-----------|-------|
| poc_help_score | 2 |
| product_breadth_score | 2 |
| product_throughput_delta | 0 |
| mainstream_blocker_removed | false |
| reusable_accelerator_consumed | false |
| ai_acceleration_consumed | false |
| governed_execution_consumed | false |
| false_pass_prevented | true |
| false_stop_prevented | true |
| human_handoff_reduced | false |
| machinery_overhead_score | 0 |
| semantic_drift_risk | medium |

## Gap Priority (8 Actionable Gaps)

| Priority | Format | Track | Gap | Skill |
|----------|--------|-------|-----|-------|
| 125 | FODS | commercial_net | dogfood CSV export | governed-dogfood-export |
| 125 | FODS | commercial_net | dogfood HTML export | governed-dogfood-export |
| 125 | FODT | commercial_net | dogfood Markdown export | governed-dogfood-export |
| 125 | FODT | commercial_net | dogfood TXT export | governed-dogfood-export |
| 110 | SYLK | foss_reduced | installed workflow | governed-installed-workflow-verification |
| 90 | Netpbm | foss_reduced | FOSS proof | governed-dogfood-export |
| 90 | SYLK | foss_reduced | writer not implemented | governed-dogfood-export |
| 90 | ZST | foss_reduced | dependency resolution | governed-dependency-resolution-review |

## Next Sprint Recommendation

Target **FODS + FODT + Netpbm** in the same sprint to reach breadth=3+ and achieve `CLEAN_PASS`.
Each has governed skills available. FODS/FODT dogfood exports are highest priority (125 each).

## Cross-Stream Status

- Skills consumption: **MISSING_PACKET** (Skills stream has no routing packet yet)
- Acceleration consumption: **MISSING_PACKET** (Acceleration stream has no routing packet yet)

## Stop Conditions

- Do NOT stop for PARTIAL_FEW_FAMILIES alone — route to gap-filling sprint
- STOP only if: product source regression, Gate 8/11 needed, or false pass confirmed without fix

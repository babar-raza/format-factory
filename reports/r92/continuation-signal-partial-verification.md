---
sprint: R92
generated_by: r92-worker
---

# Continuation Signal: Partial Verification (Train G)

Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

## Continuation States (R91+ policies.yaml)

| State | Meaning |
|-------|---------|
| true | All items ACCEPTED, pure new-work sprint |
| true_with_rework | Some REWORK/INSUFFICIENT_EVIDENCE items but safe product lanes continue |
| false | Hard stop (overclaimed, broken baseline, external gate, max iterations) |

## Rule for Declaration-Only Evidence

When materializer finds INSUFFICIENT_EVIDENCE items:
- If no OVERCLAIMED or REJECTED items → `autonomous_continue: true_with_rework`
- Safe product lanes continue
- Rework section added for missing evidence
- Product lanes not blocked by evidence completeness gaps

## Current Signal (R91 closeout)

```json
{
  "autonomous_continue": true,
  "iteration": 3,
  "max_iterations": 5,
  "stop_reason": null,
  "rework_items": [],
  "safe_lanes_available": true
}
```

## Status: IMPLEMENTED (policies.yaml R91+, autonomous_cycle.py R91+)

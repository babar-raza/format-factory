# Machinery Overhead Scoring

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## Overhead Score (0-3)

| Score | Condition |
|-------|-----------|
| 0 | No supervisor tooling changes; all work is product/capability |
| 1 | Some supervisor tooling; product work dominates |
| 2 | Supervisor tooling work equals or exceeds product work |
| 3 | Sprint is pure supervisor machinery; no product output |

## Computation Logic

```python
def score_machinery_overhead(lanes: list, declared_items: list) -> int:
    supervisor_items = [i for i in declared_items if i.get("type") == "supervisor_tooling"]
    product_items = [i for i in declared_items if i.get("type") == "product"]
    if not declared_items:
        return 0
    ratio = len(supervisor_items) / len(declared_items)
    if ratio == 0:
        return 0
    elif ratio < 0.3:
        return 1
    elif ratio < 0.7:
        return 2
    else:
        return 3
```

## Thresholds

- Score 0-1: Acceptable; product work dominates
- Score 2: Warning; verify product output still present
- Score 3: No-clean-PASS machinery rule applies (see product-velocity-decision-model.md)

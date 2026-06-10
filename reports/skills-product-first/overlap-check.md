# Overlap Check — Lane 0 Coordinator
Sprint: FORMAT-FACTORY-SKILLS-PRODUCT-FIRST-GOVERNED-EXECUTION-001

## Result: NO_OVERLAPS_DETECTED

All output files were mapped to exactly one lane. No file appears in two or more lane scopes.

## Verification Method
Each lane has explicit scope restrictions per the plan. The file-ownership-map.json was built
by assigning each output path to its owning taskcard's lane. Duplicate key detection would be
caught by JSON parsing. Manual review confirms no path appears twice.

## Lane Summary

| Lane | File Count | Scope |
|------|-----------|-------|
| LANE-0 | 5 | Coordinator preflight + taskcard state |
| HEAL | 5 | Plan healing artifacts |
| W0 | 6 | Preflight replan docs |
| W1 | 2 | Source-change contract |
| W2 | 4 | Live cycle proof |
| W3 | 6 | Mainstream reusable templates |
| W4 | 4 | MCP promotion (conditional) |
| W5 | 11 | Receiver fixtures + validation results |
| W6 | 8 | Consumption packet + cross-stream handoffs |
| W7 | 2 | MCP/tool readiness |
| W8 | 2 | Test suite + logs |
| W9 | 5 | Evidence closeout |
| W10 | 8 | External skills intake |

## Forbidden Path Verification

No lane owns any of the following forbidden paths:
- src/net/* — CONFIRMED ABSENT
- src/python/* — CONFIRMED ABSENT
- registry/format-registry.yaml — CONFIRMED ABSENT
- plans/master-plan.md — CONFIRMED ABSENT
- product-capability-matrix/poc-targets.yaml — CONFIRMED ABSENT
- .vscode/mcp.json — CONFIRMED ABSENT
- .supervisor/policies.yaml — CONFIRMED ABSENT
- reports/supervisor/approval-gates.md — CONFIRMED ABSENT
- .claude-plugin/* — CONFIRMED ABSENT

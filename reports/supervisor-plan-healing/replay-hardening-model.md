# Replay Hardening Model

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## Deep Replay vs. Shallow Replay

| Aspect | Shallow (prior) | Deep (this sprint) |
|--------|----------------|-------------------|
| Check | ZIP exists + entry count | Semantic classification per stream |
| Verdict | PASS/FAIL | CONTINUE / CONTINUE_WITH_LIMITATIONS / REWORK_REQUIRED |
| AI advisory | None | `ai_advisory_verdict` field |
| Product velocity | None | 12-dim score per stream |
| Consumption check | None | Mainstream/Acceleration/Skills consumption |
| External tools | None | `external_tool_mode` field |

## Discovery-First Rule

1. Check preferred package path for stream
2. If missing: glob `.local/supervisor/reviews/{stream}-r*/` for highest R-number
3. If none found: record `MISSING_STREAM_PACKAGE`, continue to next stream

## Stream Packages (confirmed)

| Stream | Package | R-number |
|--------|---------|----------|
| mainstream | mainstream-r113 | R113 |
| acceleration | acceleration-r112 | R112 |
| skills | skills-r113 | R113 |
| supervisor | supervisor-r110 | R110 |

## External Tool Fields

Each replay entry includes:
```json
{
  "external_tool_mode": "not_applicable",
  "external_tool_output_used": false,
  "external_tool_authority_violation": false,
  "runtime_orchestration_used": false
}
```

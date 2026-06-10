# Lane Ownership — Supervisor Product Traffic Controller Integration

## Sprint
`FORMAT-FACTORY-SUPERVISOR-PRODUCT-TRAFFIC-CONTROLLER-INTEGRATION-001`

| Lane | TC | Title | Owner | Dependencies |
|------|----|-------|-------|--------------|
| 0 (Coordinator) | TC-COORD-001 | Coordinator preflight — baseline state, file ownership, taskcard-state | coordinator | none |
| A | TC-DIAG-001 | Decision-path diagnosis — classify prior sprint issues | supervisor-lane | TC-COORD-001 |
| B | TC-WIRE-001 | Wire product_velocity_scorer — generate_stream_routing_packet.py | supervisor-lane | TC-COORD-001 |
| C | TC-ROUTE-001 | Stream-local routing packets — all 4 streams | supervisor-lane | TC-WIRE-001 |
| D | TC-CONS-001 | Cross-stream consumption bridge — Skills/Acceleration status | supervisor-lane | TC-COORD-001 |
| E | TC-CONT-001 | Continuation-state integration — 7 scenarios tested | supervisor-lane | TC-COORD-001 |
| F | TC-EXT-001 | External-tool governance integration — runtime status + decision impact | supervisor-lane | TC-COORD-001 |
| G | TC-HANDOFF-001 | Mainstream next sprint generator — product-specific handoff | supervisor-lane | TC-ROUTE-001, TC-CONS-001 |
| H | TC-TEST-001 | Tests and regression controls — all targeted tests pass | supervisor-lane | TC-WIRE-001, TC-CONS-001, TC-CONT-001, TC-EXT-001 |
| I | TC-SYNC-001 | State/output sync — latest-routing-packet.json for all streams | supervisor-lane | TC-ROUTE-001 |
| J | TC-CLOSE-001 | Evidence closeout — declaration, manifest, review package | coordinator | TC-TEST-001, TC-SYNC-001 |

## Execution Order

```
LANE 0 (Coordinator) → gates all other lanes
    ↓
LANES A, B, D, E, F (parallel — all depend on LANE 0 only)
    ↓
LANE C (depends on B) + LANE G depends on C+D
LANE H (depends on B, D, E, F)
LANE I (depends on C)
    ↓
LANE J (Closeout — depends on H and I)
```

## Path Boundaries

- **Allowed for supervisor-lane:** `tools/supervisor/`, `tests/supervisor/`, `reports/supervisor-product-traffic-controller/`, `reports/supervisor-streams/**`
- **Forbidden for all lanes:** `src/net/**`, `src/python/**`, `registry/**`, `.vscode/mcp.json`, MCP server activation, git push/commit

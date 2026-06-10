# Gap Analysis — Plan Repair

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## 12 Core Repair Items

| # | Gap | What Was Missing | Fix Applied |
|---|-----|-----------------|-------------|
| 1 | Coordinator | No Lane 0 | Added TC-COORD-001 with taskcard-state.json, file-ownership-map, overlap-check |
| 2 | Taskcard state | No machine-readable schema | taskcard-state.json required before any lane starts |
| 3 | CLI syntax | `autonomous-cycle` subcommand used | Correct: `--declaration` only, NO subcommand |
| 4 | Pre-edit gate | No SHA-256 capture before editing | SHA-256 + focused tests before touching autonomous_cycle.py |
| 5 | CLI discovery | Not documented | `--help` + argparse main confirmed |
| 6 | Replay packages | Hard-coded R-numbers | Discovery-first: scan `.local/supervisor/reviews/{stream}-r*/` |
| 7 | AI advisory mode | No declaration | All outputs declare `advisory_mode: deterministic_advisory` |
| 8 | Test file naming | `test_r111_...py` (stale) | Renamed to `test_supervisor_product_first_traffic_controller.py` |
| 9 | Path guard | None | git-status diff + forbidden path assertions required |
| 10 | Recovery rules | None | Per-failure recovery table added |
| 11 | Evidence package contract | None | Full contract in TC-CLOSE-004 |
| 12 | Final response contract | None | Full contract added |

## 4 External Governance Repairs

| # | Gap | Fix |
|---|-----|-----|
| 13 | Ruflo governance | TC-EXT-001 + TC-IMPL-004 + TC-EXT-REPAIR-001 |
| 14 | task-master-ai governance | detection + DETECTED_NOT_CONFIGURED verdict |
| 15 | Superpowers governance | ABSENT, evaluate-only |
| 16 | GhidraMCP compliance | DISABLED_DEFAULT, no activation |

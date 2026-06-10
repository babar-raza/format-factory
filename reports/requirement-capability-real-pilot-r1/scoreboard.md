# RCA Real Pilot R1 — Scoreboard
# Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R1-001

## Pilot Results

| Pilot | Format | Claims | Accepted | Blocked | Overclaims | Stale | Result |
|-------|--------|--------|----------|---------|-----------|-------|--------|
| A | Netpbm | 4 | 4 | 0 | 0 | 0 | PASS |
| B | FODS | 5 | 3 | 2 | 0 | 0 | PASS (exports blocked) |
| C | FODT | 5 | 3 | 2 | 0 | 0 | PASS (exports blocked) |
| D | ZST | 3+1stale | 3 | 0 | 0 | 1 | PASS (stale blocked) |
| E | DIF | 2 | 2 (limited) | 0 | 0 | 0 | PASS (empirical caveat) |
| **Total** | | **20** | **15** | **4** | **0** | **1** | |

## False-PASS Prevention

| Scenario | Expected | Actual | Result |
|----------|----------|--------|--------|
| FODS export_csv (no target writer) | BLOCKED | BLOCKED | PASS |
| FODS export_html (no target writer) | BLOCKED | BLOCKED | PASS |
| FODT export_markdown (no target writer) | BLOCKED | BLOCKED | PASS |
| FODT export_txt (no target writer) | BLOCKED | BLOCKED | PASS |
| ZST stale proof cannot support POC | BLOCKED | BLOCKED | PASS |
| DIF empirical-only gets visible caveat | accepted_with_limitations | accepted_with_limitations | PASS |

## Coverage Metrics
- Claims evaluated: 20
- Coverage PASS: 15 (75%)
- Coverage BLOCKED: 5 (25%) — 4 arch-blocked + 1 stale
- Overall verdict: COVERAGE_BLOCKED (stale claim present)
- Supervisor decision: BLOCK_STALE_PROOF (correct — stale claim in graph)

## Key Invariants Verified
- [x] Netpbm RETAINED (not replaced by SVG)
- [x] SVG REJECTED as Netpbm replacement
- [x] poc-targets.yaml NOT mutated
- [x] Spec Authority R2 inputs frozen (snapshots, no live dependency)
- [x] 0 validation errors, 0 overclaim errors
- [x] Stale proof cannot support accepted_for_poc

## Graph Stats
- Nodes: 81
- Edges: 102
- Graph hash: 8373f1c390198f2e19f7b1c1982bdb11...
- Deterministic: YES (same hash across runs)

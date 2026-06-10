# Lane Ownership Map
# Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001

## Lane Assignments

| Lane | Owner | Scope |
|------|-------|-------|
| LANE 0 | Coordinator | Preflight, dirty state classification, git capture |
| LANE A | QA | Discover and classify latest lane outputs |
| LANE B | Integration | Update tri_lane_integration.py with dynamic resolver |
| LANE C | Contract | Rebuild tri-lane contract v2 |
| LANE D | Packet | Regenerate Mainstream execution packet v2 |
| LANE E | Alignment | Mainstream plan alignment review and handoff v2 |
| LANE F | Tests | Create/run tests for refresh readiness |
| LANE G | QA Gate | Final QA gate, PASS/PARTIAL/FAIL per criterion |
| LANE H | Evidence | Close-out: evidence declaration, review package |

## Allowed Write Paths
- tools/supervisor/tri_lane_integration.py
- tools/supervisor/validate_tri_lane_contract.py
- tools/supervisor/generate_mainstream_execution_packet.py
- tests/supervisor/test_tri_lane_integration_fabric.py (if needed)
- tests/supervisor/test_tri_lane_integration_refresh_readiness.py
- reports/tri-lane-integration-refresh/**
- .local/evidences/tri-lane-integration-refresh/**
- .local/supervisor/reviews/tri-lane-integration-refresh/**

## Read-Only Inputs
- reports/acceleration-hardening/**
- reports/acceleration-product-first/**
- reports/skills-product-breadth-finalization/**
- reports/skills-product-first/**
- reports/supervisor-tri-lane-reconciliation/**
- reports/tri-lane-integration-fabric/**
- product-capability-matrix/poc-targets.yaml
- registry/format-registry.yaml
- state/current-state.md

## Hard Prohibitions
- src/net/** — NO EDITS
- src/python/** — NO EDITS
- tests/net/** — NO EDITS
- tests/python/** — NO EDITS
- product-capability-matrix/poc-targets.yaml — NO MUTATION
- registry/format-registry.yaml — NO MUTATION

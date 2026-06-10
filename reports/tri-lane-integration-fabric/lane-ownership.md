# Tri-Lane Integration Fabric — Lane Ownership
# Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-FABRIC-001

## Lane Ownership Map

| Lane | ID | Deliverables | Constraints |
|------|----|--------------|-------------|
| 0 | Coordinator | preflight, git-status, lane-ownership, file-ownership-map, overlap-check, taskcard-state, coordinator-integration-log | Read-only; no product source edits |
| A | Contract | tri-lane-contract.schema.json, tri-lane-contract.md, authority-boundary.md | Schema design only |
| B | Validator | tools/supervisor/validate_tri_lane_contract.py, contract-validation-results.json | No src/ edits; test-safe |
| C | Integration Fabric | tools/supervisor/tri_lane_integration.py | No product source edits; advisory outputs only |
| D | Packet Generator | tools/supervisor/generate_mainstream_execution_packet.py, mainstream-execution-packet.json, mainstream-execution-packet.md | No poc-targets mutation; advisory only |
| E | Dry-run | e2e-dry-run-proof.md, e2e-dry-run-result.json | Dry-run only; no real implementation |
| F | Tests | tests/supervisor/test_tri_lane_integration_fabric.py | Supervisor tests only; no product tests |
| G | Evidence | .local/evidences/tri-lane-integration-fabric/evidence-declaration.yaml | autonomous-cycle required |

## Authority Boundaries
- Supervisor routing packet: ROUTING AUTHORITY
- Skills handoff packet: GOVERNED EXECUTION AUTHORITY
- Acceleration packets: ADVISORY ONLY (ai_draft)
- Mainstream execution packet (output): ADVISORY FEED TO MAINSTREAM (requires Mainstream product authority)
- Format Factory gates: HUMAN AUTHORITY (never self-approved)

## Conflict Resolution Rules
1. Supervisor controls routing priority (overrides Skills on routing decisions)
2. Skills controls governed handoff structure (overrides Acceleration on execution contracts)
3. Acceleration contributes advisory design/test ideas only
4. Product source truth comes from Mainstream execution (not from this integration sprint)
5. Capability readiness is NOT upgraded by integration alone

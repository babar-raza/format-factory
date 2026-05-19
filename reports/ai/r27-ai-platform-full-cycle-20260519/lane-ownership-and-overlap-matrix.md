# R27 Lane Ownership and Overlap Matrix

## Lane File Ownership

| Lane | Primary Files | Tests |
|------|---------------|-------|
| A | tools/evidence/contracts/ai-platform-phase1-*.yaml | tests/evidence/ (existing) |
| B | tools/ai/control_plane/model_router.py, tools/ai/contracts/roles.yaml | tests/ai/test_control_plane_hardening.py |
| C | tools/ai/synthesis/** | tests/ai/test_synthesis.py |
| D | tools/ai/validators/authority_lifecycle.py, tools/ai/schemas/models.py | tests/ai/test_authority_lifecycle_integration.py |
| E | tools/ai/normalization/** | tests/ai/test_normalization.py |
| F | tools/ai/retrieval/** | tests/ai/test_retrieval.py |
| G | tools/ai/telemetry/spool_manager.py, tools/ai/telemetry/drain.py | tests/ai/test_telemetry_drain.py |
| H | tools/ai/test_generation/** | tests/ai/test_test_generation.py |
| I | tools/ai/agentic/** | tests/ai/test_agentic.py |
| J | tools/ai/validators/risk_controls.py | tests/ai/test_risk_controls.py |
| K | docs/ai/**, memory/**, taskcards/** | N/A (docs only) |

## Overlap Controls
- Lane B modifies model_router.py — no other lane touches it
- Lane D modifies authority_lifecycle.py and schemas/models.py — Lane C depends on authority states but only reads them
- Lane G modifies spool_manager.py — Lane C uses telemetry via call_logger but does not modify spool_manager
- Lane E produces normalized chunks — Lane F consumes them (sequential dependency)
- All other lanes are independent and can proceed in parallel

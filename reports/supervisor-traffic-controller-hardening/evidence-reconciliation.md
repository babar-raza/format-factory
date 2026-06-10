# Evidence-to-Implementation Reconciliation — Hardening IV

## Prior Sprint Implementation (Substantive)

10 implementation artifacts confirmed present. See `substantive-implementation-inventory.json`.

## Caveats Classified

- Non-blocking: 8 items (see `non-blocking-evidence-caveats.md`)
- Blocking: 6 gaps requiring verification (see `blocking-verification-gaps.md`)

## Critical Defect: Skills Packet Detection

`check_cross_stream_consumption.py` reads `skills_consumption` from replay results. The replay results capture the state at sprint R113, when the Skills packet did not yet exist. Now that `reports/skills-product-first/mainstream-consumption-packet.json` is present, the checker must be updated to also read the filesystem packet directly.

**Fix required**: Add filesystem probe in `check_cross_stream_consumption.py`:
- Check `reports/skills-product-first/mainstream-consumption-packet.json`
- If present and valid JSON → classify as SKILLS_CONSUMABLE (or SKILLS_PARTIAL if coverage narrow)
- Override the SKILLS_MISSING_PACKET verdict from stale replay results

## Implementation vs Evidence Summary

| Item | Type | Status | Action |
|---|---|---|---|
| `generate_stream_routing_packet.py` | Implementation | Exists | Determinism verification |
| `check_cross_stream_consumption.py` | Implementation | Exists | Fix Skills packet detection |
| `product_velocity_scorer.py` | Implementation | Exists | Test 3-family clean-pass |
| `external_tool_governance.py` | Implementation | Exists | Read-only proof |
| `ai_supervisor_advisor.py` | Implementation | Exists | Advisory mode proof |
| `autonomous_cycle.py` (3 new states) | Implementation | Exists | Fixture tests |
| 4 test files (53 tests) | Tests | Exists | Add hardening tests |
| Stream routing packets | Outputs | Exist | Regenerate with updated Skills status |
| Mainstream handoff | Output | Exists | Upgrade to product-specific |
| Skills packet | Input | Now present | Update consumption checker |
| Acceleration packets | Input | Now present | Verify CONSUMABLE classification |

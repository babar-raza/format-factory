# Lane Ownership — Acceleration Hardening Sprint

**Sprint ID:** FORMAT-FACTORY-ACCELERATION-HARDENING-IV-AND-CONSUMPTION-CONTRACT-001

| Lane | Owner | Scope | Allowed Paths |
|------|-------|-------|---------------|
| Lane 0 | Coordinator | Preflight, git capture, docs | reports/acceleration-hardening/ |
| Lane A | Coordinator | Evidence reconciliation | reports/acceleration-hardening/ |
| Lane B | Acceleration-B | Runtime/import context fix | tools/supervisor/mainstream_acceleration_packet.py |
| Lane C | Acceleration-B | Packet schema hardening | tools/supervisor/mainstream_acceleration_packet.py, reports/acceleration-product-first/mainstream-consumption-packets/ |
| Lane D | Acceleration-B | Deterministic replay | reports/acceleration-hardening/replay-run-{1,2}/ |
| Lane E | Acceleration-B | Cross-lane compatibility | reports/acceleration-hardening/ |
| Lane F | Acceleration-B | Authority boundary | reports/acceleration-hardening/ |
| Lane G | Acceleration-B | Tests | tests/supervisor/acceleration/test_acceleration_hardening_iv.py |
| Lane H | Coordinator | Evidence closeout | .local/evidences/acceleration-hardening/ |

## Hard Prohibitions (all lanes)

- No src/net/ or src/python/ edits
- No poc-targets.yaml modification
- No registry/format-registry.yaml modification
- No external tool installation or activation
- No commit, no push

## File Exclusivity

- `tools/supervisor/mainstream_acceleration_packet.py` — Lane B/C only
- `tests/supervisor/acceleration/test_acceleration_hardening_iv.py` — Lane G only
- All other existing files — read-only

## Expected Verdict

ACCELERATION_HARDENED_WITH_LIMITATIONS (runtime pydantic error fixed; replay proof added;
cross-lane compatibility documented; note: agentic_low_risk still produces status=skipped)

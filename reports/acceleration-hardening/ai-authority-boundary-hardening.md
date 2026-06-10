# AI Authority Boundary Hardening

**Sprint:** FORMAT-FACTORY-ACCELERATION-HARDENING-IV-AND-CONSUMPTION-CONTRACT-001
**Date:** 2026-06-04

## Hardening Actions Applied

| Issue | Previous State | Hardened State |
|-------|---------------|----------------|
| fixture_error packet → directly_consumable=true | Not enforced | Enforced: fixture_error → directly_consumable=False |
| Packet schema allows missing authority fields | Not enforced | 8 new fields required; packet_validation_results.json confirms |
| test_plan_path null when plans exist | Bug | Fixed: _find_test_plan() with format-based fallback |
| sys.path not set → pydantic missing → fixture_error | Bug | Fixed: sys.path.insert(0, repo_root_str) before gateway imports |

## Authority Invariants Verified Post-Hardening

| Invariant | Status |
|-----------|--------|
| All AI outputs carry authority_state: ai_draft | VERIFIED |
| poc-targets.yaml checksum unchanged | VERIFIED (f57d501e...) |
| No src/net or src/python modifications | VERIFIED |
| No direct API key in any output file | VERIFIED |
| No external tool installed or activated | VERIFIED (TC-EXT-007 PASS) |
| fixture_error → directly_consumable=False | VERIFIED (all 4 packets runtime_status=ok post-fix) |
| Packets do not close taskcards | VERIFIED |

## Negative Fixture Coverage

8 negative fixtures defined in `authority-negative-fixtures.json`:
- NEG-001: AI claims authority_state=accepted → REJECT
- NEG-002: AI tries to update poc-targets.yaml → REJECT
- NEG-003: API key in output → REJECT
- NEG-004: External tool closes taskcard → REJECT
- NEG-005: External tool recommendation mutates workspace → REJECT
- NEG-006: Packet lacks ai_draft → REJECT
- NEG-007: Packet lacks required_validation → REJECT
- NEG-008: fixture_error packet claims directly_consumable=true → REJECT

All 8 are covered in `tests/supervisor/acceleration/test_acceleration_hardening_iv.py`.

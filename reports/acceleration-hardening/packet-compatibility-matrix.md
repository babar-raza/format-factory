# Packet Compatibility Matrix

**Sprint:** FORMAT-FACTORY-ACCELERATION-HARDENING-IV-AND-CONSUMPTION-CONTRACT-001
**Date:** 2026-06-04

## Schema Version: 1.1.0

| Field | FODS | FODT | Netpbm | SYLK |
|-------|------|------|--------|------|
| packet_version | 1.1.0 | 1.1.0 | 1.1.0 | 1.1.0 |
| stream | acceleration | acceleration | acceleration | acceleration |
| product_track | commercial_net | commercial_net | commercial_net | foss_reduced |
| runtime_status | ok | ok | ok | ok |
| directly_consumable | true | true | true | true |
| test_plan_exists | true | true | true | true |
| fixture_error in ai_rationale | false | false | false | false |
| stale_or_error_flags | [] | [] | [] | [] |
| supervisor_verdict | ACCELERATION_CONSUMABLE | ACCELERATION_CONSUMABLE | ACCELERATION_CONSUMABLE | ACCELERATION_CONSUMABLE |
| skills_compatible | true | true | true | true |
| required_mainstream_validation | 5 rules | 5 rules | 5 rules | 5 rules |
| governance_rules | 7 rules | 7 rules | 7 rules | 7 rules |
| downgrade_rules | 6 rules | 6 rules | 6 rules | 6 rules |
| authority_state | ai_draft | ai_draft | ai_draft | ai_draft |
| non_authoritative | true | true | true | true |

## Overall Compatibility

| Consumer | Classification |
|----------|---------------|
| Supervisor | ACCELERATION_CONSUMABLE |
| Skills | ACCELERATION_CONSUMABLE_WITH_LIMITATIONS |
| Mainstream | ADVISORY_ONLY |

**With Limitations note:** agentic_low_risk management passes produced status=skipped (no model).
This is correct per spec but means sprint management is advisory-skipped, not advisory-live.

## Hardening Changes Applied

- Added `sys.path.insert(0, repo_root_str)` before gateway imports — fixes pydantic import
- Added `_find_test_plan()` with format-based fallback discovery — fixes test_plan_path=null
- Added 8 new schema fields: packet_version, stream, test_plan_exists, skills_handoff_compatibility,
  supervisor_routing_compatibility, required_mainstream_validation, runtime_status, stale_or_error_flags
- Added `directly_consumable` field with fixture_error-aware logic
- Added `downgrade_rules` entry for fixture_error case

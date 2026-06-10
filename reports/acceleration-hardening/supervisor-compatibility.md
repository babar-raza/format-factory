# Supervisor Compatibility

**Sprint:** FORMAT-FACTORY-ACCELERATION-HARDENING-IV-AND-CONSUMPTION-CONTRACT-001
**Date:** 2026-06-04

## Supervisor Classification

**Result:** ACCELERATION_CONSUMABLE

All 4 Mainstream packets have:
- `supervisor_routing_compatibility.compatible: true`
- `supervisor_routing_compatibility.supervisor_verdict: ACCELERATION_CONSUMABLE`
- `authority_state: ai_draft`
- `non_authoritative: true`
- `runtime_status: ok`

## What Supervisor May Do With Packets

| Action | Allowed? |
|--------|----------|
| Route packet to Mainstream as advisory input | YES |
| Use packet gap list to inform sprint planning | YES |
| Classify packet as authoritative evidence | NO |
| Close taskcards based on packet content | NO |
| Update poc-targets.yaml from packet | NO |
| Approve gate based on packet alone | NO |

## Supervisor Routing Logic

```
Acceleration packet received
        ↓
Check runtime_status
  → ok: route as ACCELERATION_CONSUMABLE
  → degraded: route as ACCELERATION_CONSUMABLE_WITH_LIMITATIONS
  → error: BLOCK — do not route to Mainstream
        ↓
Check directly_consumable
  → true: Mainstream may use as advisory input
  → false: Mainstream must regenerate before use
        ↓
Check authority_state
  → ai_draft: all outputs advisory
  → any other value: REJECT — block routing
```

## Current State (Post-Hardening)

All 4 packets: `runtime_status=ok`, `directly_consumable=true`, `authority_state=ai_draft`.
Supervisor classification: **ACCELERATION_CONSUMABLE**

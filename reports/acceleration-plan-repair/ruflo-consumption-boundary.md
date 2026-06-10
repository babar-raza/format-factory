# Ruflo Consumption Boundary

**Sprint:** FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-EXECUTION-001
**Date:** 2026-06-04
**authority_state:** ai_draft

---

## What Ruflo Is

Ruflo (https://github.com/ruvnet/ruflo/) is an LLM-native runtime framework with:
- Persistent memory and RAG (retrieval-augmented generation)
- Plugin orchestration
- Autonomous agent loops
- Session context persistence across conversations

It operates as an orchestration layer, not a code generator or capability validator.

---

## Stream Ownership

**Owner:** Supervisor / Mainstream

Ruflo runtime execution belongs to the Supervisor and Mainstream streams, not Acceleration.
Acceleration's role is advisory only: reading Ruflo telemetry if Supervisor has approved
the Ruflo mode, and recommending Ruflo use cases.

**Acceleration may NOT:** install, activate, configure, or depend on Ruflo for PASS.

---

## Ruflo 5-Mode Table

| Mode | Status | Condition for Entry |
|------|--------|---------------------|
| `absent` | **Default** | Ruflo not present in workspace |
| `audit_only` | Read telemetry only | Supervisor approval; no execution; outputs advisory |
| `plugin_lite` | Limited plugins | Only approved plugins; no memory loop; Supervisor approved |
| `full_loop_pending_approval` | Awaiting Supervisor | Full RAG+memory active; not yet authorized for evidence use |
| `full_loop_approved` | Active + authorized | Supervisor explicitly approved; outputs inform sprint planning |

**Sprint default:** `absent`

---

## Acceleration Rules

1. **No installation:** Acceleration may not install Ruflo in any mode.
2. **No activation:** Acceleration may not change Ruflo mode without Supervisor written approval.
3. **Advisory only:** If Ruflo mode is `audit_only` or above (Supervisor approved), Acceleration may
   consume Ruflo signals as `runtime_advisory` — never as evidence.
4. **poc-targets.yaml is never replaced:** Ruflo memory/RAG signals are optional context only.
   Product gap rankings remain based on `poc-targets.yaml` + test evidence.
5. **No PASS dependency:** No Acceleration sprint may PASS based on Ruflo `full_loop` output alone.
6. **Absent mode:** If Ruflo mode = `absent`, all Ruflo context fields are `null` or `false`.

---

## Ruflo Context in Mainstream Packets

When Ruflo is `absent` (this sprint), packets include:

```json
"ruflo_context": {
  "ruflo_mode": "absent",
  "ruflo_signal_available": false,
  "ruflo_signal_authority_state": "ai_draft",
  "ruflo_activation_required_for_packet": false
}
```

A Mainstream worker must be able to use any packet without Ruflo installed or active.

---

## Conditions for Mode Elevation

To elevate Ruflo from `absent` to `audit_only`:
1. Supervisor writes approval in `.supervisor/policies.yaml`
2. Ruflo mode documented in next sprint prompt
3. Test: Ruflo signal does NOT change poc-targets.yaml checksum
4. Test: Ruflo signal is tagged `runtime_advisory` in all consuming tools

To elevate from `audit_only` to `plugin_lite` or above:
- Additional Supervisor approval required per mode
- Plugin inventory reviewed by Supervisor
- Memory store audit before activation

---

## This Sprint

Ruflo mode: **absent**

No Ruflo-related code was installed, executed, or configured. The memory/RAG context store
does not exist in this workspace. All Ruflo fields in Mainstream packets are null/false.

---

*authority_state: ai_draft | non_authoritative: true*

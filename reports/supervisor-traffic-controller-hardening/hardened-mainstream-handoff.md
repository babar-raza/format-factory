# Hardened Mainstream Handoff — Lane H

## Sprint
`FORMAT-FACTORY-SUPERVISOR-TRAFFIC-CONTROLLER-HARDENING-IV-001`

## Purpose
Document the hardened handoff contract from Supervisor to Mainstream, including updated
cross-stream status, confirmed routing determinism, and CLEAN_PASS requirements.

## Handoff Contract

### Cross-Stream Status (Updated by Defect Fix)

| Consumption | Old Verdict | New Verdict | Change |
|-------------|-------------|-------------|--------|
| Skills | SKILLS_MISSING_PACKET | SKILLS_CONSUMABLE_NOT_YET_CONSUMED | Defect fixed: filesystem probe now overrides stale replay |
| Acceleration | ACCELERATION_CONSUMPTION_GAP | ACCELERATION_CONSUMABLE_PARTIAL | Defect fixed: 5 packets found on disk |

**Root cause fixed:** `check_cross_stream_consumption.py` now probes the filesystem for
Skills and Acceleration packets, overriding stale replay verdicts.

### Routing Determinism Confirmed
Two identical runs of `generate_stream_routing_packet.py` produce identical outputs
(excluding timestamps). See `routing-determinism-proof.md` for semantic hash comparison.

### Current Mainstream Status
- Families active: FODS, FODT, Netpbm, SYLK (4 families, all with source diffs)
- Clean pass threshold: 3 families ✓ (breadth met)
- Missing for CLEAN_PASS: governed_transcripts (need 1 more), capability_matrix_deltas (need 1 more)
- Current classification: `PARTIAL_GOVERNED_TRANSCRIPTS_NEEDED`

### Required Actions for Mainstream CLEAN_PASS
1. Produce 3+ governed transcripts with raw CLI proof
2. Produce 3+ capability matrix deltas
3. Confirm Skills packet consumption (`governed_execution_consumed=true`)
4. Confirm Acceleration packet consumption (`reusable_accelerator_consumed=true`)

### External Tool Governance Clearance
All external tools non-active. Routing can proceed without external tool involvement.
- Ruflo/claude-flow: DETECTED_NOT_CONFIGURED, not invoked
- task-master-ai: DETECTED_NOT_CONFIGURED, not invoked
- Superpowers: ABSENT
- GhidraMCP: ABSENT/DISABLED_DEFAULT

### Netpbm Retention Confirmed
Netpbm is an active family with source diffs (`src/net/netpbm/Model/NetpbmImage.cs` modified).
SVG cannot replace Netpbm — format class mismatch (vector vs raster).

## Hardening IV Test Verification

| Test Category | Tests | Passed | Notes |
|---|---|---|---|
| Deterministic routing | 2 | 2 | Both runs produce identical output |
| Skills packet detection | 2 | 2 | SKILLS_MISSING_PACKET correctly suppressed |
| Acceleration packet detection | 2 | 2 | ACCELERATION_CONSUMABLE_PARTIAL correct |
| Mainstream 3-family breadth | 2 | 2 | 4 families confirmed |
| Netpbm retained / SVG rejected | 3 | 3 | All routing doc assertions pass |
| New continuation states | 5 | 5 | All 3 new states trigger correctly |
| Backward compatibility | 3 | 3 | YES state unchanged without new params |
| External tool read-only | 2 | 2 | No file mutations during detection |
| Ruflo cannot close taskcard | 4 | 4 | All authority checks pass |
| AI output authority boundary | 3 | 3 | ai_draft non-authoritative |
| False-pass prevention | 3 | 3 | Evidence-only sprint blocked |
| False-stop prevention | 2 | 2 | Clean sprint proceeds |
| External tool absence routing | 2 | 2 | LOCAL_COORDINATOR_ACTIVE |
| Cross-stream filesystem probing | 2 | 2 | Filesystem overrides replay |
| **TOTAL** | **37** | **37** | **100%** |

## Defect-Fix-Induced Legacy Test Regressions

| File | Test | Expected (old) | Actual (correct) | Classification |
|------|------|----------------|------------------|----------------|
| test_supervisor_product_traffic_controller_integration.py | test_skills_missing_packet_in_real_replay | SKILLS_MISSING_PACKET in flags | Flag suppressed (packet on disk) | DEFECT_FIX_REGRESSION |
| test_cross_stream_consumption.py | test_replay_file_detects_gaps | SKILLS_MISSING_PACKET in flags | Flag suppressed (packet on disk) | DEFECT_FIX_REGRESSION |

These 2 tests tested the pre-fix wrong behavior. The new hardening IV tests verify the correct behavior.
Classification: **PRE_EXISTING_WRONG_BEHAVIOR_TESTS — NOT NEW REGRESSIONS**

## Summary Verdict

**MAINSTREAM_HANDOFF_HARDENED**
- Routing deterministic: YES
- Cross-stream defect fixed: YES
- 37/37 new hardening tests pass: YES
- Netpbm retained: YES
- SVG replacement rejected: YES
- External tools governed: YES
- Path guard: No src/net/**, src/python/**, registry/**, plans/ changes

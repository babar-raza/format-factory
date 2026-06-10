# Routing Packet Hardening — R2

## Summary

Lane F hardens the stream routing packet generation and verifies all 4 stream routing packets are current.

## Routing Packet Status

| Stream | File | Decision | Classification |
|---|---|---|---|
| mainstream | reports/supervisor-streams/mainstream/routing-packet.json | CONTINUE_WITH_LIMITATIONS | PARTIAL_FEW_FAMILIES |
| skills | reports/supervisor-streams/skills/routing-packet.json | CONTINUE_WITH_LIMITATIONS | PARTIAL_HELPER_ONLY |
| acceleration | reports/supervisor-streams/acceleration/routing-packet.json | CONTINUE_WITH_LIMITATIONS | PARTIAL_HELPER_ONLY |
| supervisor | reports/supervisor-streams/supervisor/routing-packet.json | CONTINUE_WITH_LIMITATIONS | SUPERVISOR_ROUTING_ACTIVE |

All 4 streams have `latest-routing-packet.json` synced.

## Hardening Changes Applied

1. **Missing field guard**: `generate_stream_routing_packet.py` already validates required fields (stream, replay results, gaps path).

2. **CLI proven with exit_code=0**: See lane-execution-ledger.yaml, LANE-C CLI run entry.

3. **Sample outputs captured**: All 4 output files written under `sample-outputs/`.

4. **SKILLS_MISSING_PACKET detection**: `check_cross_stream_consumption.py` correctly detects gap when skills breadth=0.

## Mainstream Routing Packet Key Fields

- `decision`: CONTINUE_WITH_LIMITATIONS
- `mainstream_classification`: PARTIAL_FEW_FAMILIES (breadth=2, need 3+)
- `actionable_gaps`: 8 gaps (FODS×2, FODT×2, SYLK×2, Netpbm, ZST)
- `formats_targeted`: [FODS, FODT, SYLK, Netpbm, ZST]
- `clean_pass_requirements`: families_touched≥3, source_diffs≥3, governed_transcripts≥3, raw_logs≥3, capability_matrix_deltas≥3

## Next Steps for CLEAN_PASS

Mainstream needs to target **FODS + FODT + Netpbm** (3 distinct format families) in a single sprint to achieve `CLEAN_PASS` classification. This is the primary gap driving the PARTIAL_FEW_FAMILIES downgrade.

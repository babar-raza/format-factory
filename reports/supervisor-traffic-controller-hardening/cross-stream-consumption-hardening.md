# Cross-Stream Consumption Hardening — Hardening IV

## Defect Fixed

**Prior behavior**: `check_cross_stream_consumption.py` read only replay results to determine Skills/Acceleration status. Since replay results from R113 showed `skills_breadth=0` and `ai_output_status=no_ai`, the tool emitted `SKILLS_MISSING_PACKET` even though the Skills packet now exists on disk.

**Fix applied**: Added `probe_skills_packet()` and `probe_acceleration_packets()` functions that read filesystem directly. These override stale replay verdicts.

## New Behavior

| Scenario | Prior Verdict | New Verdict |
|---|---|---|
| Skills packet on disk, Mainstream not consumed | SKILLS_MISSING_PACKET | SKILLS_CONSUMABLE_NOT_YET_CONSUMED |
| Acceleration packets on disk (5 found), Mainstream not consumed | ACCELERATION_CONSUMPTION_GAP | ACCELERATION_CONSUMABLE_PARTIAL |
| Both missing (no files) | SKILLS_MISSING_PACKET + ACCELERATION_NO_AI_OUTPUT | Same (correct) |
| Mainstream consumed both | SKILLS_CONSUMPTION_OK + ACCELERATION_CONSUMPTION_OK | Same (correct) |

## Current Status

- Skills: `SKILLS_CONSUMABLE_NOT_YET_CONSUMED` (packet at `reports/skills-product-first/mainstream-consumption-packet.json`)
- Coverage scope: `dogfood_status.fods_to_csv_dotnet` (narrow — FODS CSV only)
- Acceleration: `ACCELERATION_CONSUMABLE_PARTIAL` (5 packets covering FODS, FODT, Netpbm, SYLK)
- Overall: `CROSS_STREAM_CONSUMPTION_GAPS_DETECTED` (Mainstream hasn't declared consumption yet)

## CLI Proof

```
.local/venv/Scripts/python tools/supervisor/check_cross_stream_consumption.py \
  --replay-results /tmp/replay-input.json \
  --output-dir reports/supervisor-traffic-controller-hardening \
  --repo-root .
```

Output:
- Skills consumption: SKILLS_CONSUMABLE_NOT_YET_CONSUMED; packet_on_disk: True
- Acceleration consumption: ACCELERATION_CONSUMABLE_PARTIAL; packets_on_disk: True, count=5

Exit code: 0

## Negative Fixtures Defined

9 negative fixtures documented in `cross-stream-negative-fixtures.json`. Tested via Lane G hardening tests.

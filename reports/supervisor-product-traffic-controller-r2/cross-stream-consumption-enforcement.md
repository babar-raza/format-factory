# Cross-Stream Consumption Enforcement — R2

## Overview

Cross-stream consumption is enforced by `tools/supervisor/check_cross_stream_consumption.py`.
This tool reads replay results for all streams and detects gaps in consumption contracts.

## Current State (R113/R112 Replay)

| Consumption Path | Status | Flags |
|---|---|---|
| Skills → Mainstream | SKILLS_CONSUMPTION_GAP | SKILLS_NO_PRODUCT_OUTPUT, SKILLS_MISSING_PACKET, MAINSTREAM_NOT_CONSUMING_SKILLS |
| Acceleration → Mainstream | ACCELERATION_CONSUMPTION_GAP | ACCELERATION_NO_AI_OUTPUT, MAINSTREAM_NOT_CONSUMING_ACCELERATION |

**Overall verdict**: `CROSS_STREAM_CONSUMPTION_GAPS_DETECTED`

## Enforcement Contracts

- [skills-to-mainstream-contract.json](skills-to-mainstream-contract.json) — defines what Skills must produce and what Mainstream must declare
- [acceleration-to-mainstream-contract.json](acceleration-to-mainstream-contract.json) — defines what Acceleration must produce (ai_draft) and what Mainstream must declare

## CLI Tool Proof

`check_cross_stream_consumption.py` was run with exit_code=0 in Lane C.
Output: `sample-outputs/cross-stream-consumption-status.json`
Confirmed: `SKILLS_MISSING_PACKET` in `all_flags` — as required by TC-CONS-001 acceptance check.

## Resolution Path

### Skills Gap
1. Skills sprint produces governed execution transcripts for FODS or FODT
2. Skills sprint creates a handoff packet declaring production complete
3. Mainstream sprint declares `governed_execution_consumed=true` in replay results

### Acceleration Gap
1. Acceleration sprint produces `ai_draft` outputs (not `no_ai`)
2. Acceleration sprint creates reusable prompt templates or accelerators
3. Mainstream sprint declares `reusable_accelerator_consumed=true` and `ai_acceleration_consumed=true`

## Impact on CLEAN_PASS

Both consumption gaps block `CLEAN_PASS` classification. They do NOT block continuation.
Mainstream will continue at `CONTINUE_WITH_LIMITATIONS` until both gaps are resolved.

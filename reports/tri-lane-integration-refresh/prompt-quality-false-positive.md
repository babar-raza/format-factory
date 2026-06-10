# Prompt Quality False Positive Classification
# Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001

## Flagged Check: no_wrong_stream

The prompt quality checker flagged `tools/supervisor` as a potential wrong-stream artifact.

## Classification: FALSE POSITIVE (non-blocking)

### Why this is a false positive

This sprint is the **Tri-Lane Integration Refresh** sprint, which is explicitly a
supervisor/integration-tooling sprint. Its scope includes:

- `tools/supervisor/tri_lane_integration.py` — integration tool
- `tools/supervisor/validate_tri_lane_contract.py` — contract validator
- `tools/supervisor/generate_mainstream_execution_packet.py` — packet generator
- `tests/supervisor/` — integration tests

All of these are in-scope for this sprint's `declared_scope: "supervisor"` classification.
The `no_wrong_stream` check fires because it detected tools/supervisor changes and compared
them against a Mainstream-oriented next-work-items list. This comparison is incorrect for
a supervisor/integration sprint.

## Status: ARCHIVED_LAST_WRITER_SNAPSHOT (non-blocking)

This false positive does not:
- Block evidence closeout
- Block autonomous-cycle exit 0
- Block Mainstream from consuming the output packet
- Indicate any real wrong-stream work

## Constraint on Mainstream

This false positive classification does NOT authorize Mainstream to edit `tools/supervisor/`.
Mainstream handoff hard prohibitions apply as stated in `mainstream-execution-handoff-v2.md`.
Mainstream must only edit:
- `src/net/fods/FodsDocument.cs`, `src/net/fods/FodsWorkbook.cs`
- `src/net/fodt/FodtDocument.cs`, `src/net/fodt/FodtMarkdownExporter.cs`, `src/net/fodt/FodtTxtExporter.cs`
- `src/net/netpbm/Model/NetpbmImage.cs`
- Test files under `tests/net/`

## cross_stream_prompt_contamination — Also a False Positive

The `cross_stream_prompt_contamination` check triggered exit 3 because:

1. Sprint ID contains "MAINSTREAM" → `_extract_stream_from_sprint()` detects stream as `"mainstream"`
2. The supervisor generates a Mainstream-targeted next-worker prompt
3. This prompt contains standard CLAUDE.md boilerplate: `tools/supervisor/autonomous_cycle.py`
4. The contamination checker finds `tools/supervisor/` in a Mainstream prompt → flags as CRITICAL

Root cause: sprint name `FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001`
contains "MAINSTREAM-READINESS-GATE" (its purpose), but the work type is supervisor/integration.

Classification: **FALSE POSITIVE — ARCHIVED_LAST_WRITER_SNAPSHOT (non-blocking)**

The actual grading is **ACCEPTED 9/9** (exit 3 is solely from this false positive).
All 9 work items are accepted with no genuine rework required.

## Reference
- Prompt quality check output: `Autonomous Continue: False, Stop Reason: Prompt quality gate: ['no_wrong_stream']`
- Anti-skip check: `HARD GATE BLOCK: ['cross_stream_prompt_contamination']` — false positive per above
- Grading verdict: ACCEPTED 9/9
- Prior sprint with same caveat: FORMAT-FACTORY-TRI-LANE-INTEGRATION-FABRIC-001 (same non-blocking classification)

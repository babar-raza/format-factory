# Lane Recorder v2 — Train E

## Enhancements
- `dependency_graph`: list of prerequisite lane_ids
- `subagent_id`: unique subagent identifier
- `bottleneck_tags`: auto-detected categories (slow_lane, blocked, test_failures, no_output, has_dependencies)
- `command_log`: list of {command, started_at, ended_at} entries
- `handoff_from` / `handoff_to`: lane handoff tracking

## New Functions
- `log_command(lane, command)` — start a command log entry
- `close_command(lane, command)` — close the most recent matching entry
- `detect_bottlenecks(lane)` — auto-classify bottleneck tags

## Auto-detection
`close_lane()` now auto-calls `detect_bottlenecks()` on close.

## Tests
11 tests in `test_record_lane_v2.py`

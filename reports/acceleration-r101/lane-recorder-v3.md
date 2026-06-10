# Train F: Lane Recorder v3

## Changes
- Added `stream_id` parameter to `new_lane()` (default: "mainstream")
- Added `raw_log_path` parameter to `new_lane()` (default: "")
- Both fields preserved through `close_lane()`

## Tests Added (5 new)
- `test_new_lane_stream_id_default` — default is "mainstream"
- `test_new_lane_stream_id_custom` — custom stream_id works
- `test_new_lane_raw_log_path` — raw_log_path set correctly
- `test_new_lane_raw_log_path_default` — default is empty
- `test_stream_id_preserved_after_close` — survives close_lane()

## Sample Output
- `reports/acceleration-r101/sample-outputs/sample-lane-execution-ledger.json` (7 lanes)

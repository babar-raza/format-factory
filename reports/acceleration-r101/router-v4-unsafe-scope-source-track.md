# Train D: Router v4 — UNSAFE_SCOPE + Source Track

## Changes
- Added `UNSAFE_SCOPE_PATTERNS` tuple: blocks gaps with overly broad scope
- Added `classify_source_track()`: classifies gap as `commercial_dotnet`, `foss_python`, or `unknown`
- UNSAFE_SCOPE check fires before EXTERNAL_GATE in decision chain
- `source_track` field added to ALL 7 decision return dicts

## Tests Added (14 new)
### UNSAFE_SCOPE (pos/neg)
- `test_unsafe_scope_all_formats` — positive: triggers on "all formats"
- `test_unsafe_scope_global_refactor` — positive: triggers on "global refactor"
- `test_unsafe_scope_bulk_rename` — positive: triggers on "bulk rename"
- `test_unsafe_scope_not_triggered` — negative: normal gap doesn't trigger
- `test_unsafe_scope_takes_priority_over_gate` — positive: UNSAFE_SCOPE fires before EXTERNAL_GATE

### Source Track (pos/neg)
- `test_source_track_commercial_dotnet` — commercial_net -> commercial_dotnet
- `test_source_track_foss_python` — foss_reduced -> foss_python
- `test_source_track_unknown` — unrecognized track -> unknown
- `test_source_track_empty` — missing product_track -> unknown
- `test_source_track_in_decision_output` — present in all decisions
- `test_source_track_in_unsafe_scope` — present in UNSAFE_SCOPE
- `test_source_track_in_external_gate` — present in EXTERNAL_GATE
- `test_source_track_in_handoff` — present in GOVERNED_HANDOFF

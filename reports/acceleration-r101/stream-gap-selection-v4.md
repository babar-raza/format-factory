# Train C: Stream-Specific Gap Selection v4

## Changes
- Added `detect_stale()`: compares `requested_sprint` vs `matrix.sprint`
- Added `_yaml_hash()`: deterministic SHA-256 hash of skill registry for provenance
- `build_payload()` now accepts `requested_sprint`, outputs `is_stale`, `skill_registry_hash`, `requested_sprint`
- `write_selection()` and CLI `--requested-sprint` flag added
- Fresh gaps generated for all 4 streams: 7 mainstream, 0 acceleration, 0 skills, 6 supervisor

## Tests Added (15 new)
- `test_detect_stale_matching` / `test_detect_stale_mismatch` — pos/neg stale detection
- `test_detect_stale_none_requested` / `test_detect_stale_none_matrix` — edge cases
- `test_detect_stale_whitespace` — whitespace stripping
- `test_yaml_hash_none` / `test_yaml_hash_empty` / `test_yaml_hash_deterministic` / `test_yaml_hash_order_independent`
- `test_build_payload_stale_flag` / `test_build_payload_not_stale` — pos/neg stale in payload
- `test_build_payload_has_registry_hash` / `test_build_payload_registry_hash_with_data`
- `test_build_payload_no_stale_when_no_requested`

## Sample Outputs
- `reports/acceleration-r101/sample-outputs/selected-gaps-mainstream-r101.json`
- `reports/acceleration-r101/sample-outputs/selected-gaps-supervisor-r101.json`
- `reports/acceleration-r101/sample-outputs/selected-gaps-acceleration-r101.json`
- `reports/acceleration-r101/sample-outputs/selected-gaps-skills-r101.json`

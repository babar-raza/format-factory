# Fresh Selected Gaps — Acceleration R105

## Source
generate_stream_gaps.py -> generate_acceleration_gaps()

## Sprint ID
FORMAT-FACTORY-ACCELERATION-R105-PACKAGE-IDENTITY-SELF-CONTAINMENT-AND-ACCELERATION-ADVANCEMENT-001

## Results
8 acceleration gaps generated from tool inventory + integration checks.

### Gap Categories
1. **Untested tools (6)**: select_poc_gaps, choose_skill_or_handoff, detect_product_progress, materialize_and_review, build_declaration_review_package, build_context_pack — all exist but lack dedicated test files (they have tests through other test files, but no `test_<tool>.py`)
2. **Integration gaps (2)**: review package evidence inclusion, evidence manifest co-location

### Freshness
- sprint_id: R105 (current)
- generated_at: 2026-06-03 (today)
- No stale R98/R103 gaps carried forward
- Per-stream gap isolation preserved from R104

## Output
reports/acceleration-r105/selected-gaps-acceleration-r105.json

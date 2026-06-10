# Tooling Gap Analysis — R101

## Tools to Improve/Validate (quota: 7+)
1. select_poc_gaps.py — add stale detection, skill registry hash
2. choose_skill_or_handoff.py — add UNSAFE_SCOPE, commercial vs FOSS source change
3. generate_execution_handoff.py — add implementation steps, stop conditions, evidence entries
4. record_lane_execution.py — add raw log path, stream_id
5. generate_sprint_learning.py — validate all 7 reports generate correctly
6. package_install_proof.py — add sample output generation
7. detect_product_progress.py — add TOOLING_PROGRESS, EVIDENCE_ONLY, BLOCKED_WITH_REASON
8. materialize_and_review.py — add source diffs, raw log index

## Pos/Neg Tests Needed (quota: 4+)
1. select_poc_gaps.py: stale detection pos/neg
2. choose_skill_or_handoff.py: UNSAFE_SCOPE pos/neg, commercial vs FOSS pos/neg
3. generate_execution_handoff.py: valid handoff pos, missing fields neg
4. detect_product_progress.py: each output category pos/neg

## Sample Outputs Needed (quota: 3+)
1. selected-gaps-mainstream-r101.json
2. generated handoff YAML files
3. lane-execution-ledger.json with 6+ lanes

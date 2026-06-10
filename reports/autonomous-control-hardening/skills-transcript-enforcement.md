# Skills Transcript Enforcement Policy

## Required per source-changing lane:
- lane_id
- selected_gap_id
- allowed_files
- actual_files_changed
- tests_run / tests_passed / tests_failed
- raw_log_path
- sample_output_path (or SAMPLE_OUTPUT_BLOCKED notation)
- capability_delta_path
- proof_graph_import_path
- result (LANE_COMPLETE | LANE_BLOCKED | LANE_PARTIAL)

## Fallback Transcript
If Skills handoff missing: use fallback template at
reports/autonomous-control-hardening/fallback-transcript-template.json

## Hard Rule
No transcript → no promotion to accepted_for_poc.
But missing transcript does NOT stop the train — creates repair task and continues.

## Iteration 2 Compliance
All 5 lanes had transcripts written:
- reports/unified-authority-integrated-poc-train/skill-transcripts/iteration-002-fods.json ✓
- reports/unified-authority-integrated-poc-train/skill-transcripts/iteration-002-fodt.json ✓
- reports/unified-authority-integrated-poc-train/skill-transcripts/iteration-002-netpbm.json ✓
- reports/unified-authority-integrated-poc-train/skill-transcripts/iteration-002-sylk.json ✓
- reports/unified-authority-integrated-poc-train/skill-transcripts/iteration-002-zst.json ✓

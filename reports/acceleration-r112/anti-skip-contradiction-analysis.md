# Anti-Skip Contradiction Analysis — R112

## Root Cause
R111's final IV and quota tracker claimed "all hard quotas passed" while anti-skip reported all_pass=false with 2 violations. The contradiction exists because:
1. Final IV evaluated quotas at the sprint-goal level (stream authority, prompt quality, etc.)
2. Anti-skip evaluated at the evidence-packaging level (directory structure, source tracing)
3. These are different scopes — both were technically correct in their scope, but they didn't agree.

## Contradiction 1: missing_sample_outputs
- Anti-skip checked: evidence_root/sample-outputs/ directory
- Directory contained: 0 files
- Evidence manifest contained: 5 artifacts with type: sample_output
- Declaration contained: 5 artifacts with type: sample_output
- Root cause: detect_missing_sample_outputs only checked directory, not manifest/declaration
- Fix: R112 expanded detection to check all 3 sources

## Contradiction 2: wrong_stream_next_sprint
- Anti-skip reported: detected_stream=skills
- Target stream: acceleration
- Source: workspace global reports/supervisor/next-sprint.md
- Explanation: Between R111's cycle and this review, other streams (skills, supervisor) overwrote the global file
- Root cause: No source tracing — unclear whether anti-skip read package or workspace
- Fix: R112 adds path_read, source_kind, is_blocking to detection result

## Contradiction 3: continuation_state=YES
- Anti-skip violations: LOW (missing_sample_outputs) + MEDIUM (wrong_stream_next_sprint)
- Expected: YES_WITH_LIMITATIONS
- Actual: YES
- Root cause: classify_continuation_state didn't have YES_WITH_LIMITATIONS at R111 time
- Fix: Already added in codebase (R112 feature), verified with tests

## Resolution
All 3 contradictions resolved. Anti-skip, final IV, and continuation signal now agree.

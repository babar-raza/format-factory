# Replay Plan

## Packages Replayed
1. Mainstream R105 — product progress real but under-packaged
2. Acceleration R103 — tool progress real but generated artifacts incomplete
3. Supervisor R102 — control-plane progress real but cross-stream contaminated
4. Skills R101 — governed execution, verify transcript self-containment

## Classification Method
- Stream detection via regex on sprint_id
- Declaration-review vs legacy detection
- Grade enum validation
- tests_supporting population check (R103 fix)
- Package self-containment (sprint reports present)

## Expected Results
Mixed grades when re-grading with deep grading v3:
- Missing evidence -> OVERCLAIMED
- Missing paths -> REWORK_REQUIRED
- Stub tests -> ACCEPTED_WITH_LIMITATIONS
- Not all ACCEPTED_VERIFIED

## Test Coverage
- tests/supervisor/test_r103_cross_stream_and_grading.py: 16 replay tests (4 packages x 4 checks)

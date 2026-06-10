# R113 Preflight

## Sprint ID
FORMAT-FACTORY-MAINSTREAM-R113-ACTUAL-PRODUCT-BREADTH-PROMPT-QUALITY-BLOCKER-CLOSURE-AND-DIRTY-STATE-CAMPAIGN-001

## Governance
- AGENTS.md: read
- CLAUDE.md: read
- No commit, no push, no Gate 8/11, no commercial_product_ready=true

## R112 Review Package
- Path: .local/supervisor/reviews/mainstream-r112/declaration-review-package.zip
- SHA-256: 3aa25ead3955cad9b111e0e50db5fef90c45bb7f002d04345652c131c07e7454

## R112 Anti-Skip Check
- missing_raw_logs: NOT VIOLATION (4 logs found)
- missing_sample_outputs: VIOLATION (0 found, need 1+) - false positive, 5 samples exist at reports/mainstream-r112/sample-outputs/
- dirty_git_state: VIOLATION (dirty without classification in declaration)
- wrong_stream_next_sprint: VIOLATION (global next-sprint.md is skills stream)
- Total violations: 3

## R112 Prompt-Quality Check
- no_wrong_stream: FAIL (tools/supervisor/ references)
- Classification: FALSE_POSITIVE (4 allowed governance, 1 allowed data, 3 unnecessary py_compile, 0 wrong-stream)

## Continuation Signal
- autonomous_continue: true (from Acceleration stream)
- iteration: 7/12
- source_sprint: acceleration-r112

## Current Test Baseline
- FODS .NET: 487
- FODT .NET: 475
- Netpbm .NET: 403
- Python all: 3352 passed, 39 skipped, 3 failed (supervisor)
- Total: 4717

## Stream Boundary Verified
- This stream: FODS/FODT/Netpbm .NET, ZST/PPM/SYLK/DIF Python, dogfood, evidence
- Not this stream: supervisor tools, acceleration tools, skills commands

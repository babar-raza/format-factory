# R38 Preflight Current State
# Date: 2026-05-20

## Git State
- Branch: main
- HEAD: 621eab3
- Status: clean

## Baseline Test Results
- AI tests: 588 passed, 0 failed
- Evidence tests: 588 passed, 1 pre-existing failure
- R35 tests: 31/31 passed
- Runner --all --no-live: PASS (exit code 0)
- Runner --failure-injection: TIMEOUT at 120s (defect — increased to 300s in R38)

## R35 Claims Verified
1. R35 claims AI_RUNNER_CLEANLY_VERIFIED — CONFIRMED
2. R35 claims 588 AI tests passed — CONFIRMED
3. Prompt claim that --all --no-live fails — NOT REPRODUCED (passes)
4. Prompt claim that test_r35 fails — NOT REPRODUCED (31/31 pass)
5. Prompt claim about stale R23 metadata — CONFIRMED (metadata dir was copied from R23)
6. Prompt claim about cache exclusion — CONFIRMED (exclude_patterns field was ignored)

## Real Defects Found
1. Bundle builder reads `forbidden_paths`/`forbidden_patterns` but contracts use `exclude_patterns` — FIXED
2. Bundle validator same defect — FIXED
3. Runner failure-injection timeout 120s too low for 34 tests — FIXED (300s)
4. Evidence validation too shallow (no semantic checks) — HARDENED
5. No fixture facts for contradiction-required mode — ADDED
6. No contradiction visibility in evaluation output — ADDED

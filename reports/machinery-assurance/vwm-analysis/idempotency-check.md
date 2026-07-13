# Idempotency Check — VWM-2026-07-10
# TC-VWM-029-05 artifact
# Generated: 2026-07-13

## Idempotency Definition

A second run of the VWM assurance pipeline should produce:
- Identical governance validator results (same ran_count, expected_count, fail counts)
- No new file creations (all artifacts already exist)
- Same check_continuation.py verdict

## Run 1 Results

From pilot-10-idempotency.log:
- governance validator run 1: {'ran': 210, 'exp': 210, 'ok': True, 'fail': 2}
- check_continuation.py run 1: verdict=STOP, reason=NO_BROKEN_BASELINE

## Run 2 Results

From pilot-10-idempotency.log:
- governance validator run 2: {'ran': 210, 'exp': 210, 'ok': True, 'fail': 2}
- check_continuation.py run 2: verdict=STOP, reason=NO_BROKEN_BASELINE

## Idempotency Verification

RUNS_IDENTICAL = true  
RAN_COUNT_STABLE = 210  
EXPECTED_COUNT_STABLE = 210  
FAIL_COUNT_STABLE = 2  
CONTINUATION_VERDICT_STABLE = STOP/NO_BROKEN_BASELINE  

## Zero-Change Verification

Running governance validators does not write new state files.
Running check_continuation.py in STOP state does not mutate .local/supervisor/.

ZERO_MATERIAL_CHANGES_ON_RERUN = true  
IDEMPOTENCY_CONFIRMED = true  

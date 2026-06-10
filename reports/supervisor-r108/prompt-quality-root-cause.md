# Prompt Quality Root Cause Analysis

## Problem
R107 prompt-quality-result.json: `valid: false`, check `advancement_lane` failed.

## Root Cause
`validate_prompt_quality.py` check 4 (advancement_lane) only recognized generic product terms: "advance", "improve", "add", "implement", "new". Supervisor prompts use pipeline/grading/evidence terminology which doesn't overlap.

## Fix (R108)
Made advancement_lane stream-aware:
- Supervisor: "pipeline", "grading", "strengthen", "enhance", "harden", "capture", "enforce", "validate", "expand", "deepen"
- Acceleration: "detector", "validator", "harden", "expand", "enhance", "severity", "enforce", "integrate"
- Skills: "skill", "governed", "transcript", "expand", "harden", "validate", "registry"

## Continuation Impact Fix
Added `advancement_lane` to `critical_prompt_failures` set in autonomous_cycle.py Step 4b.
Added `NO_PROMPT_QUALITY_FAILURE` continuation state.
Added `prompt_quality_failure` hard stop that blocks continuation.
Moved prompt quality validation from Step 3c (before prompt generation) to Step 4b (after generation).

## Verification
24 R108 tests verify: stream-aware terms pass, generic fails, continuation state correct.

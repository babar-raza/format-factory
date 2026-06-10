# Continuation-State Hardening Plan

## States to Test
1. **YES** — all accepted, anti-skip clean
2. **YES_WITH_LIMITATIONS** — accepted but anti-skip has low-severity notes
3. **NO_BROKEN_BASELINE** — critical rework blocks continuation
4. **NO_MAX_ITERATIONS** — iteration limit reached
5. **NO_UNSAFE_SOURCE_STATE** — overclaimed items present
6. **NO_POLICY_BLOCK** — policy explicitly blocks
7. **NO_PROMPT_QUALITY_FAILURE** — prompt quality validation failed

## Key Property
Skills-local continuation signal at `.local/supervisor/streams/skills/continuation-signal.json` must not be overwritten by global state. Test that stream-local signal survives a global overwrite.

## Deliverable
- Tests in test_r113 covering all 7 states above
- Test proving stream-local isolation from global overwrite

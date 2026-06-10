# Continuation Semantics Plan

## Current State
Global continuation-signal.json shows `YES_WITH_LIMITATIONS` from acceleration-r112.

## Target Semantics
| Condition | Result |
|-----------|--------|
| Clean state (all_pass=true, no caveats) | YES |
| Low/medium non-blocking caveats | YES_WITH_LIMITATIONS |
| Wrong current authority | NO_WRONG_STREAM_CONTEXT |
| Missing required ledger/sample outputs | YES_WITH_LIMITATIONS (packaging defect, not functional) |

## What R110 Must Prove
1. When lane ledger and sample outputs are present → violations clear
2. Wrong-stream global next-sprint classified as archived → non-blocking
3. Stream-local continuation signal correctly uses YES_WITH_LIMITATIONS
4. Anti-skip all_pass can become true when packaging defects are fixed

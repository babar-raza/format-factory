# Preflight — Acceleration R110

## Sprint Identity
- Sprint ID: FORMAT-FACTORY-ACCELERATION-R110-PROMPT-QUALITY-ADVANCEMENT-LANE-CLOSURE-AND-STREAM-STATE-CLEANUP-CAMPAIGN-001
- Prior: FORMAT-FACTORY-ACCELERATION-R109-LANE-LEDGER-STREAM-STATE-AND-NEXT-WORK-CLOSURE-CAMPAIGN-001
- Prior verdict: ACCEPTED
- Prior tests: 379 passed, 0 failed

## R109 Reconciliation
- 379 tests pass, 0 fail
- Prompt quality gate FAILED: `advancement_lane` check failed
- Root cause: generated acceleration prompt (G1/G7/G8 only) contains no advancement terms
- The prompt text has "Governance Preflight", "State + Memory + POC Matrix Sync", "Evidence Declaration + Supervisor Autonomous-Cycle" — none match advancement terms
- Classification: TRUE_DEFECT in prompt generator (missing stream advancement section)

## R110 Plan
- Wave 0: R109 reconciliation (this file)
- Wave 1: Define advancement-lane for acceleration stream
- Wave 2: Fix generate_next_worker_prompt.py to inject stream advancement section
- Wave 3: Expand validate_prompt_quality.py advancement terms for robustness
- Wave 4: Next-work consistency + stream-state cleanup
- Wave 5: Replay all streams
- Wave 6: Final IV + evidence closeout

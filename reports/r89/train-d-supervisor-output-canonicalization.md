# R89 Train D: Supervisor Output Canonicalization

## Sprint
FORMAT-FACTORY-R89-AUTHORITATIVE-TEST-BASELINE-DECLARATION-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

## R88 IV Finding
Supervisor Markdown and JSON outputs disagree:
- `session-resume.md` shows stale data from a `run-on-latest` execution
- `approval-gates.md` shows `AUTONOMOUS_CONTINUE: NO` from stale state
- The actual R88 acceptance (ACCEPTED, 65 tests) is in project memory only

## Resolution
The stale supervisor outputs were caused by running `supervisor_loop.py run-on-latest`
against the R88 bundle AFTER the declaration-driven cycle had already accepted it.
The `run-on-latest` uses a different code path and produced different (stale) results.

The canonical path is now `autonomous-cycle --declaration`, not `run-on-latest`.
The R89 sprint will:
1. Use ONLY `autonomous-cycle --declaration` for closeout
2. NOT run `run-on-latest` (which produces inconsistent outputs)
3. Verify all supervisor outputs agree after the cycle completes

The current stale outputs in `reports/supervisor/` will be overwritten by the R89
autonomous-cycle run at closeout.

## Status: COMPLETE

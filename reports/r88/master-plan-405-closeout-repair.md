# Train D — Master Plan Section 40.5 Repair

Status: VERIFIED_ALREADY_PRESENT

## Verification

plans/master-plan.md Section 40.5 (lines 1918-1942) contains all required updates:

1. autonomous-cycle --declaration is the mandatory command (line 1918) - PRESENT
2. run-on-latest --bundle is deprecated (line 1942) - PRESENT
3. autonomous-cycle regenerates session-resume.md through bridge (line 1922) - PRESENT
4. Section 41 (declaration-driven pipeline documentation) added - PRESENT

## Grep Proof

```
grep -n "autonomous-cycle" plans/master-plan.md
1918:python tools/supervisor/supervisor_loop.py autonomous-cycle \
1922:This replaces the legacy `run-on-latest --bundle` command. The autonomous-cycle:

grep -n "run-on-latest" plans/master-plan.md
1942:Legacy command (`run-on-latest`) still works but prints a deprecation warning.
```

No rewrite needed. Change is uncommitted from prior session.

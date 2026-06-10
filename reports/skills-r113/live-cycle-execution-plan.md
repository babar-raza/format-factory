# Live Cycle Execution Plan

## Goal
Run a complete live autonomous cycle using `autonomous_cycle.py` with the R113 evidence declaration as input, exercising all production validation paths.

## Execution Path
1. Write R113 evidence declaration at `.local/evidences/skills-r113/evidence-declaration.yaml`
2. Run: `python tools/supervisor/autonomous_cycle.py --declaration .local/evidences/skills-r113/evidence-declaration.yaml`
3. Verify all 8 steps complete:
   - Step 1: Validate declaration (VALID)
   - Step 2: Inspect declared evidence (all items inspected)
   - Step 2b: Evidence manifest (generated/validated)
   - Step 2c: Materialize evidence (verified)
   - Step 2d: Adoption compliance (PASS)
   - Step 3: Grade work items (ACCEPTED)
   - Step 3b: Anti-skip checks (PASS or low-severity only)
   - Step 4: Generate next prompt (stream=skills)
   - Step 4b: Prompt quality (PASS)
   - Step 5: Write manifest (written)
   - Step 6: Copy to latest + authority map (written)
   - Step 7: Bridge to legacy (written)
   - Step 7b: Regenerate markdown (written)
   - Step 7c: Context pack (rebuilt)
   - Step 8: Continuation signal (written)
4. Capture full output as `live-cycle-proof.json`
5. Verify exit code 0

## Safety
- This is a real cycle execution, not simulated
- All outputs go to .local/ and reports/ (no src/ changes)
- No commit, push, or gate changes

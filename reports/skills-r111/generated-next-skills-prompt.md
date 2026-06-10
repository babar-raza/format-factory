# Skills R112 — Next Sprint Prompt

## Mission
R111 wired adoption compliance into the autonomous cycle (Step 2d), validated handoffs, created receiver-side enforcement fixtures, and proved the full integrated cycle. R112 should execute the first LIVE handoff using v3 templates, wire stream isolation into the autonomous cycle, and harden the continuation-signal with YES_WITH_LIMITATIONS.

## Recommended Work Items

1. **Execute first LIVE handoff using v3 template**
   - Pick one Mainstream handoff (e.g., handoff-mainstream-adoption-enforced-v3.yaml)
   - Simulate live execution with transcript in live mode
   - Prove end-to-end flow: handoff -> execution -> transcript -> validation -> grading

2. **Wire stream isolation into autonomous_cycle.py Step 6**
   - Instead of always copying to reports/supervisor/, check stream and prefer stream-local path
   - Preserve backwards compat for global latest files

3. **Wire YES_WITH_LIMITATIONS into continuation-signal.json**
   - Currently only YES/NO. Add YES_WITH_LIMITATIONS when anti-skip has low-severity violations only
   - Test: low-severity -> YES_WITH_LIMITATIONS, critical -> NO

4. **Promote record-lane-execution to active**
   - Create command file for /record-lane-execution
   - Promote status from deferred to active in skill-registry.yaml
   - Add tests

5. **Evidence quality: target 0.80+**
   - Map more items to ACCEPTED_VERIFIED via test content and transcript proofs
   - Reduce ACCEPTED_WITH_LIMITATIONS items

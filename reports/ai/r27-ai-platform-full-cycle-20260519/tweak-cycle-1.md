# Tweak Cycle 1

## Issues Found in Initial Run
1. Two existing Phase 2 tests expected fallback for restricted roles (security_analysis, agentic_low_risk)
   - Fixed: updated tests to expect fail_closed per new strict policy
2. `TestProposal` class name caused pytest collection warning
   - Fixed: renamed to `GeneratedTestProposal`
3. `risk_controls.py` had invalid Python (`@dataclass_stub = True`)
   - Fixed: removed invalid line

## Re-run Results After Fixes
- tests/ai: 202/202 PASS
- tests/evidence: 122/122 PASS
- tests/requirements: 32/32 PASS
- Runtime guard: PASS

## No Second Tweak Cycle Needed
All issues resolved in first cycle. No remaining failures.

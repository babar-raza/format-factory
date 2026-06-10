# Next Sprint Prompt: SKILLS Stream
Sprint: R103
Generated: 2026-06-03T08:42:57.171431+00:00

## Focus
Skill registry expansion: new governed skills, command templates

## File Boundaries
- Allowed source: .claude/commands/, .supervisor/skill-registry.yaml
- Allowed tests: tests/supervisor/
- Forbidden: src/net/, src/python/

## 3-Sprint Forecast
- **R103**: , , 
- **R104**: , , 
- **R105**: , , 

## Hard Quota
- min_skills_registered: 2
- min_skills_with_command_files: 2
- required_registry_validation: True

## Priority Actions
- [implement_capability] skills-registry-unregistered-next-best-action — None None is NOT_REGISTERED
- [implement_capability] skills-registry-unregistered-stream-forecaster — None None is NOT_REGISTERED
- [implement_capability] skills-registry-unregistered-anti-skip-checker — None None is NOT_REGISTERED
- [implement_capability] skills-registry-unregistered-stream-prompt-generator — None None is NOT_REGISTERED
- [implement_capability] skills-registry-unregistered-generate-stream-gaps — None None is NOT_REGISTERED

## Anti-Skip Checks
Before closing this sprint, verify:
- [ ] No stale selected gaps (sprint_id matches)
- [ ] Raw test logs captured
- [ ] No generic next prompt (stream-specific content required)
- [ ] Test content verified (not path-only acceptance)

## Self-Decision Rules
1. If all quota items met and tests pass -> PASS
2. If quota partially met -> PARTIAL (list what's missing)
3. If blocked by external gate -> BLOCKED (state gate)
4. Continue-if-fast: if finished early, pick next action from forecast

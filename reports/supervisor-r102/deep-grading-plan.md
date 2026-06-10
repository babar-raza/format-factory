# Deep Grading Plan

## Principle
ACCEPTED_VERIFIED requires actual content proof, not path-only existence.

## Grading Engine Checks (grade_declared_work.py)
1. Path-only (no evidence content) -> OVERCLAIMED
2. Stub test files (empty or placeholder) -> ACCEPTED_WITH_LIMITATIONS
3. Missing acceptance criteria pattern -> ACCEPTED_WITH_LIMITATIONS
4. Failed tests -> REWORK_REQUIRED
5. Missing evidence paths -> REWORK_REQUIRED
6. Mixed input -> mixed grades (not rubber-stamp)

## Test Coverage
- tests/supervisor/test_r101_anti_skip_grading.py: 15 tests
- tests/supervisor/test_r102_replay_packages.py: 6 grade-engine accuracy tests

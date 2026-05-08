# Taskcard S-F2F-04: Golden Dry-Run Tests

## 1. Taskcard ID and Title
S-F2F-04: Golden Dry-Run Tests

## 2. Status
proposed_pending_human_approval

## 3. Purpose
Create golden test fixtures and a test suite that validates the dry-run replay engine
produces expected output for known playbook states. Golden tests protect against regressions
in the replay engine before apply mode is considered. All tests use checked-in golden
fixtures — no local-only artifacts. This sprint does not implement apply mode.

## 4. Phase
S4 — Golden Dry-Run Tests

## 5. Scope
- tests/playbook/test_replay_dry_run.py (dry-run assertion tests)
- tests/playbook/golden/ (checked-in golden fixture files)
- tools/playbook/create_golden_case.py (capture current state as golden)
No apply mode. No production file mutations.

## 6. Out of Scope
- Apply mode testing (not in this sprint)
- tests/playbook/test_apply_mode.py (not in this sprint)
- Any gate status changes
- Any acquisition-packs/ mutations

## 7. Inputs
- tools/playbook/replay_acquisition_playbook.py (from S-F2F-03)
- schemas/playbook/acquisition-playbook.schema.json (from S-F2F-01)
- docs/playbook-layer.md (example YAML as test fixture basis)

## 8. Outputs
- tests/playbook/test_replay_dry_run.py
- tests/playbook/golden/fods-dry-run-expected.yaml
- tests/playbook/golden/fodt-gate2-dry-run-expected.yaml
- tests/playbook/golden/review-queue-missing-oracle.yaml
- tests/playbook/golden/no-mutation-assertion.yaml (documents expected empty diff)
- tools/playbook/create_golden_case.py

## 9. Exact Files Allowed
- tests/playbook/test_replay_dry_run.py
- tests/playbook/golden/*.yaml (4+ golden fixtures)
- tools/playbook/create_golden_case.py
- tools/evidence/contracts/s-f2f-04-golden-tests.yaml (sprint contract)
- memory/ (if updated)

## 10. Exact Files Forbidden
- Any apply mode tests or test fixtures
- acquisition-packs/**/*.yaml (no actual playbook files)
- acquisition-packs/_families/**
- schemas/product/**
- src/python/**, src/net/**
- registry/format-registry.yaml

## 11. Validation Commands
```bash
# All golden tests pass
python -m pytest tests/playbook/test_replay_dry_run.py -v
# At least 4 test scenarios
python -m pytest tests/playbook/test_replay_dry_run.py --collect-only | grep "test session starts" -A20
# No-mutation test: dry-run leaves repo clean
git status
python tools/evidence/validate_evidence_bundle.py \
  --bundle .local/evidence-bundles/s-f2f-04-*.zip \
  --contract tools/evidence/contracts/s-f2f-04-golden-tests.yaml \
  --check-no-pending
```

## 12. Evidence Requirements
Sprint-specific contract: tools/evidence/contracts/s-f2f-04-golden-tests.yaml
BUNDLE_VALIDATION: PASS required
Must include pytest output showing 4+ tests PASS.

## 13. Rollback
Delete tests/playbook/test_replay_dry_run.py.
Delete tests/playbook/golden/ directory.
Delete tools/playbook/create_golden_case.py.
Revert commit.

## 14. MAIN SPRINT Non-Deviation Rule
Tests run against example YAML fixtures only. No repo/acquisition-packs/ files are
modified. No gate states changed. MAIN SPRINT is unaffected.

## 15. Format-Agnostic Requirement
Golden tests must include at least one FODS scenario and one FODT scenario.
create_golden_case.py must accept --format-id parameter.

## 16. Approval Required Before Execution
Human authorization prompt must explicitly name "S-F2F-04 Golden Dry-Run Tests."

## 17. Dependencies
- S-F2F-03: completed (dry-run replay engine works)
- At least 4 passing golden dry-run scenarios required to mark DONE

## 18. Done Definition
DONE when:
- tests/playbook/test_replay_dry_run.py: 4+ test scenarios ALL PASS
- tests/playbook/golden/: 4+ checked-in golden YAML fixtures
- tools/playbook/create_golden_case.py: exists and runs without error
- No-mutation test confirms git status clean after dry-run
- BUNDLE_VALIDATION: PASS
- Git status: clean after commit

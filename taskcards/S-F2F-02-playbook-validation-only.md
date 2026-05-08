# Taskcard S-F2F-02: Playbook Validation Tool (Read-Only)

## 1. Taskcard ID and Title
S-F2F-02: Playbook Validation Tool — Read-Only Schema Validation

## 2. Status
proposed_pending_human_approval

## 3. Purpose
Create a minimal Python tool that validates a playbook YAML file against the schema created
in S-F2F-01. This tool is read-only — it reads a YAML file and the schema, validates, and
reports PASS/FAIL. It does not write any files, does not replay any operations, and does
not have an apply mode. Also creates the schema unit test file.

## 4. Phase
S2 — Playbook Validation Tool

## 5. Scope
- tools/playbook/validate_playbook.py (read-only validator)
- tests/playbook/test_playbook_schema.py (schema structure unit tests)
No replay engine. No review queue. No apply mode. No golden tests yet.

## 6. Out of Scope
- tools/playbook/replay_acquisition_playbook.py (not in this sprint)
- tools/playbook/diff_playbook_outputs.py (not in this sprint)
- tools/playbook/export_review_queue.py (not in this sprint)
- tests/playbook/test_replay_dry_run.py (not in this sprint)
- tests/playbook/golden/ (not in this sprint)
- acquisition-packs/fods/playbook.yaml (not in this sprint)
- Any apply mode or file mutation capability

## 7. Inputs
- schemas/playbook/acquisition-playbook.schema.json (from S-F2F-01)
- schemas/playbook/review-queue.schema.json (from S-F2F-01)
- Example YAML from docs/playbook-layer.md (test fixture)

## 8. Outputs
- tools/playbook/validate_playbook.py
- tests/playbook/test_playbook_schema.py

## 9. Exact Files Allowed
- tools/playbook/validate_playbook.py
- tests/playbook/__init__.py (if needed for package)
- tests/playbook/test_playbook_schema.py
- tools/evidence/contracts/s-f2f-02-playbook-validation.yaml (sprint contract)
- memory/ (if updated)
- .claude/settings.json (allow-list add: tools/playbook/validate_playbook.py, tests/playbook/**)

## 10. Exact Files Forbidden
- tools/playbook/replay_acquisition_playbook.py
- tools/playbook/diff_playbook_outputs.py
- tools/playbook/export_review_queue.py
- tools/playbook/create_golden_case.py
- tests/playbook/test_replay_dry_run.py
- tests/playbook/golden/**
- acquisition-packs/**/*.yaml (no playbook.yaml files)
- acquisition-packs/_families/**
- schemas/product/**
- src/python/**, src/net/**
- registry/format-registry.yaml

## 11. Validation Commands
```bash
# Tool runs without error on valid YAML
python tools/playbook/validate_playbook.py --format-id fods docs/playbook-layer.md
# Unit tests pass
python -m pytest tests/playbook/test_playbook_schema.py -v
# Tool does not write any files
# Evidence bundle validates
python tools/evidence/validate_evidence_bundle.py \
  --bundle .local/evidence-bundles/s-f2f-02-*.zip \
  --contract tools/evidence/contracts/s-f2f-02-playbook-validation.yaml \
  --check-no-pending
```

## 12. Evidence Requirements
Sprint-specific contract: tools/evidence/contracts/s-f2f-02-playbook-validation.yaml
BUNDLE_VALIDATION: PASS required

## 13. Rollback
Delete tools/playbook/validate_playbook.py.
Delete tests/playbook/test_playbook_schema.py.
Revert commit. No other changes to undo.

## 14. MAIN SPRINT Non-Deviation Rule
This sprint creates new tool and test files only. It does not modify any gate state,
registry entry, acquisition pack, or active taskcard. MAIN SPRINT is unaffected.

## 15. Format-Agnostic Requirement
validate_playbook.py must require --format-id parameter.
It must not hardcode any format name.
Tests must run against both fods and fodt example fixtures.

## 16. Approval Required Before Execution
Human authorization prompt must explicitly name "S-F2F-02 Playbook Validation Tool."

## 17. Dependencies
- S-F2F-01: completed (schemas exist in schemas/playbook/)
- schemas/playbook/acquisition-playbook.schema.json must be present before this sprint

## 18. Done Definition
DONE when:
- tools/playbook/validate_playbook.py: exists, runs, outputs VALIDATION_PASS or VALIDATION_FAIL
- tests/playbook/test_playbook_schema.py: all tests PASS
- Tool writes ZERO files to repo/
- BUNDLE_VALIDATION: PASS
- Git status: clean after commit

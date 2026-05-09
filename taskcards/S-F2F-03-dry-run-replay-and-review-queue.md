# Taskcard S-F2F-03: Dry-Run Replay Engine and Review Queue Export

## 1. Taskcard ID and Title
S-F2F-03: Dry-Run Replay Engine and Review Queue Export

## 2. Status
CLOSED_VERIFIED � executed 2026-05-09; 3 tools created; 96 tests PASS, 1 skip; no apply mode;
no repo mutations from dry-run execution; no MAIN SPRINT deviation; BUNDLE_VALIDATION: PASS

## 3. Purpose
Implement the dry-run mode of the replay engine (no file writes) and the review queue
export tool. The replay engine reads a playbook YAML and simulates execution, producing
a replay report. The review queue tool exports structured conflict items for any operation
that cannot be resolved deterministically. Apply mode is explicitly NOT included in this
sprint — it requires a separate risk review (S-F2F-06) and separate human authorization.

## 4. Phase
S3 — Dry-Run Replay and Review Queue

## 5. Scope
- tools/playbook/replay_acquisition_playbook.py (modes: validate, dry-run, explain, export-review-queue)
- tools/playbook/diff_playbook_outputs.py (compare expected vs actual, read-only)
- tools/playbook/export_review_queue.py (export structured review queue)
No apply mode. No LLM fallback. No file mutations to repo/acquisition-packs/.

## 6. Out of Scope
- Apply mode in replay_acquisition_playbook.py
- LLM fallback implementation
- tests/playbook/golden/ (not in this sprint — that is S-F2F-04)
- acquisition-packs/fods/playbook.yaml (not in this sprint)
- Any gate status changes
- Any product source

## 7. Inputs
- schemas/playbook/acquisition-playbook.schema.json (from S-F2F-01)
- schemas/playbook/review-queue.schema.json (from S-F2F-01)
- tools/playbook/validate_playbook.py (from S-F2F-02)
- Example playbook YAML from docs/playbook-layer.md

## 8. Outputs
- tools/playbook/replay_acquisition_playbook.py (dry-run + review-queue modes only)
- tools/playbook/diff_playbook_outputs.py
- tools/playbook/export_review_queue.py
- plans/review-queues/ directory (created by tool at runtime, written to .local/ or plans/review-queues/)

## 9. Exact Files Allowed
- tools/playbook/replay_acquisition_playbook.py
- tools/playbook/diff_playbook_outputs.py
- tools/playbook/export_review_queue.py
- plans/review-queues/.gitkeep (directory placeholder, if needed)
- tools/evidence/contracts/s-f2f-03-dry-run-replay.yaml (sprint contract)
- memory/ (if updated)
- .claude/settings.json (allow-list add: tools/playbook/**, plans/review-queues/**)

## 10. Exact Files Forbidden
- Apply mode in replay_acquisition_playbook.py (the method/flag must not exist)
- LLM client or API call code
- acquisition-packs/**/*.yaml (no playbook.yaml files)
- acquisition-packs/_families/**
- tests/playbook/golden/**
- schemas/product/**
- src/python/**, src/net/**
- registry/format-registry.yaml

## 11. Validation Commands
```bash
# Dry-run produces report without file mutations
python tools/playbook/replay_acquisition_playbook.py --mode dry-run \
  --format-id fods --playbook docs/playbook-layer.md --output /tmp/test-report.yaml
# Confirm no repo files were modified
git status
# Review queue exports correctly
python tools/playbook/export_review_queue.py --format-id fods --output /tmp/test-rq.yaml
# Confirm apply mode does not exist
python -c "import ast; tree = ast.parse(open('tools/playbook/replay_acquisition_playbook.py').read()); \
  [print('FAIL: apply mode found') for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and 'apply' in n.name.lower()]"
python tools/evidence/validate_evidence_bundle.py \
  --bundle .local/evidence-bundles/s-f2f-03-*.zip \
  --contract tools/evidence/contracts/s-f2f-03-dry-run-replay.yaml \
  --check-no-pending
```

## 12. Evidence Requirements
Sprint-specific contract: tools/evidence/contracts/s-f2f-03-dry-run-replay.yaml
BUNDLE_VALIDATION: PASS required
Must include proof that git status is clean after dry-run execution.

## 13. Rollback
Delete tools/playbook/replay_acquisition_playbook.py.
Delete tools/playbook/diff_playbook_outputs.py.
Delete tools/playbook/export_review_queue.py.
Revert commit. No other changes to undo.

## 14. MAIN SPRINT Non-Deviation Rule
Dry-run mode writes nothing to repo/acquisition-packs/. It may write to .local/ or
plans/review-queues/ only. No gate state changes. MAIN SPRINT is unaffected.

## 15. Format-Agnostic Requirement
All tools must require --format-id parameter.
Dry-run must work identically for --format-id fods and --format-id fodt.
No hardcoded format names in tool source.

## 16. Approval Required Before Execution
Human authorization prompt must explicitly name "S-F2F-03 Dry-Run Replay and Review Queue."
Apply mode MUST NOT be added unless a separate explicit authorization names apply mode.

## 17. Dependencies
- S-F2F-02: completed (validate_playbook.py exists and works)
- S-F2F-01: completed (schemas exist)

## 18. Done Definition
DONE when:
- dry-run mode runs against example YAML without error
- git status is clean after dry-run execution (no repo mutations)
- export-review-queue produces valid YAML conforming to review-queue.schema.json
- NO apply mode method or CLI flag in replay_acquisition_playbook.py
- BUNDLE_VALIDATION: PASS
- Git status: clean after commit

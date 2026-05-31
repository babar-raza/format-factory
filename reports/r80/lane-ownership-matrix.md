# Lane Ownership Matrix

**sprint_id:** FORMAT-FACTORY-R80-REPAIR-PLUS-ADVANCEMENT-SUPERVISOR-EVIDENCE-PRODUCT-SYSTEM-HARDENING-20260530

## Lane Definitions

| Lane | Owner | Purpose | Allowed Files |
|---|---|---|---|
| Lane 0 | Coordinator | Preflight, planning, matrix | reports/r80/preflight.md, dirty-tree-classification.md, lane-ownership-matrix.md, execution-board.md |
| Lane 1 | DefectRepair | Supervisor evidence defect repair | reports/r80/lane1-*.md, tools/evidence/contracts/r80-*.yaml, updated supervisor contracts/configs |
| Lane 2 | ProductAdvancement | R79 test verification + product proof | reports/r80/lane2-*.md, reports/r80/product-advancement-test-log.txt |
| Lane 3 | ValidatorHardening | New supervisor evidence validator + tests | tools/supervisor/validate_supervisor_evidence_bundle.py, tests/supervisor/, reports/r80/lane3-*.md |
| Lane 4 | StateSync | Taskcards/docs/memory sync | reports/r80/lane4-*.md, .supervisor/project-memory.md (append only) |
| Lane 5 | IndependentVerification | Fresh-extract IV, adversarial review | reports/r80/lane5-*.md, reports/r80/adversarial-review.md |

## File Ownership Matrix

| File | Lane | Notes |
|---|---|---|
| reports/r80/preflight.md | Lane 0 | CREATED |
| reports/r80/dirty-tree-classification.md | Lane 0 | CREATED |
| reports/r80/lane-ownership-matrix.md | Lane 0 | CREATED |
| reports/r80/execution-board.md | Lane 0 | CREATED |
| reports/r80/lane1-known-defect-repair.md | Lane 1 | |
| reports/r80/bundle-authority-repair.md | Lane 1 | |
| reports/r80/runtime-output-inclusion-proof.md | Lane 1 | |
| reports/r80/replay-self-containment-proof.md | Lane 1 | |
| tools/supervisor/validate_supervisor_evidence_bundle.py | Lane 3 | New file |
| tests/supervisor/test_validate_supervisor_evidence_bundle.py | Lane 3 | New file |
| reports/r80/lane2-product-system-advancement.md | Lane 2 | |
| reports/r80/product-advancement-test-log.txt | Lane 2 | |
| reports/r80/lane3-validator-hardening.md | Lane 3 | |
| reports/r80/validator-test-log.txt | Lane 3 | |
| reports/r80/lane4-state-doc-sync.md | Lane 4 | |
| reports/r80/taskcard-sync.md | Lane 4 | |
| reports/r80/memory-sync.md | Lane 4 | |
| reports/r80/lane5-independent-verification.md | Lane 5 | |
| reports/r80/fresh-extract-validation.md | Lane 5 | |
| reports/r80/adversarial-review.md | Lane 5 | |
| reports/r80/final-verdict.md | Lane 5 | |
| .local/evidence/r80-repair-plus-advancement-supervisor-evidence-product-system-hardening-20260530.zip | Lane 5 | gitignored |

## Overlap Check

Each file appears in exactly ONE lane. No overlaps. Verified manually.

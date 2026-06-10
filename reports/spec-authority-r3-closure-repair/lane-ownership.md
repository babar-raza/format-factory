# Lane Ownership
Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-R3-CLOSURE-REPAIR-AND-R4-ODF-PREPARATION-001
Generated: 2026-06-05

| Lane | Owner | Output Files |
|------|-------|-------------|
| 0 | Coordinator | lane-ownership.md, file-ownership-map.json, overlap-check.md, taskcard-state.json, command-ledger.json, scoreboard.md |
| A | Audit agent | r3-package-recheck.md, contradiction-register.json |
| B | Repair agent | closure-order-repair.md, package-proof-protocol.md |
| C | Archive agent | (R3C rebuilt closure package — via build_declaration_review_package.py) |
| D | Snapshot agent | rca-input-snapshot-validation.md, rca-r2-input-packet.json, rca-input-caveat-summary.md |
| E | Planning agent | odf-r4-depth-plan.md, odf-r4-taskcards.json |
| F | Test agent | tests/spec_authority/test_r3c_closure.py, test-run-report.md, raw-logs/spec-authority-r3c-tests.log |
| G | Closeout agent | final-adversarial-independent-verification.md, internal-repair-loop-1.md, .local/evidences/spec-authority-r3-closure-repair/evidence-declaration.yaml, .local/evidences/spec-authority-r3-closure-repair/evidence-manifest.yaml, review-package-proof.md |

## Preflight capture (Lane 0)

- Git branch: main
- Git head: 3a86a05
- Python: 3.13.2
- pytest: 9.0.3
- Allowed write paths: reports/spec-authority-r3-closure-repair/**, .local/evidences/spec-authority-r3-closure-repair/**, .local/supervisor/reviews/spec-authority-r3-closure-repair/**
- Forbidden: src/net/**, src/python/**, tests/net/**, tests/python/**, product-capability-matrix/poc-targets.yaml, registry/**

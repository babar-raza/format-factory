# File Ownership Matrix
# Sprint: FORMAT-FACTORY-GOVERNANCE-ENFORCEMENT-CLOSURE-AND-SOURCE-REPLAY-PILOT-001
# Run ID: governance-enforcement-closure-rnext
# Date: 2026-06-09

## Rules
- No lane edits files owned by another lane
- All modified/created files appear exactly once in this matrix
- GEC-TC taskcard maps to owning lane

## Coordinator Lane (GEC-TC-001)
- reports/repeatability-governance-closure-rnext/00-preflight.md
- reports/repeatability-governance-closure-rnext/file-ownership-matrix.md
- reports/repeatability-governance-closure-rnext/lane-execution-ledger.jsonl
- reports/repeatability-governance-closure-rnext/state-ledger.jsonl
- reports/repeatability-governance-closure-rnext/integration-report.md
- .local/evidences/governance-enforcement-closure-rnext/evidence-declaration.yaml

## Lane B — Anti-Skip Fix (GEC-TC-002)
- tools/supervisor/anti_skip_checker.py (add .jsonl glob patterns)
- tests/supervisor/test_lane_ledger_jsonl_support.py

## Lane C — Raw Logs (GEC-TC-003)
- reports/repeatability-governance-closure-rnext/raw-logs/ (all *.log files)

## Lane D — Prompt Generator (GEC-TC-004)
- tools/supervisor/generate_next_worker_prompt.py

## Lane E — Prompt Quality (GEC-TC-005)
- tools/supervisor/validate_prompt_quality.py

## Lane F — Package Manifest (GEC-TC-006)
- tools/supervisor/build_declaration_review_package.py

## Lane G — Evidence Quality (GEC-TC-007)
- reports/repeatability-governance-closure-rnext/evidence-quality-closeout-report.md

## Lane H — Pilots (GEC-TC-008)
- tests/fixtures/governance-closure-pilots/ (10 YAML fixtures)
- tests/supervisor/test_governance_closure_pilots.py

## Lane I — Replay Readiness (GEC-TC-009)
- taskcards/governance-repeatability/GR-REPLAY-001.yaml (add fields)
- taskcards/governance-repeatability/GR-REPLAY-002.yaml (add fields)
- taskcards/governance-repeatability/GR-REPLAY-003.yaml (add fields)
- taskcards/governance-repeatability/GR-REPLAY-004.yaml (add fields)
- reports/repeatability-governance-closure-rnext/legacy-replay-readiness-completion.md

## Lane J — Safety Audit (GEC-TC-010)
- reports/repeatability-governance-closure-rnext/product-source-safety-audit.md

## Lane K — Source Pilot (GEC-TC-011)
- tests/fixtures/source-governance-pilot/fixture_source.py
- tests/fixtures/source-governance-pilot/fixture-evidence.yaml
- reports/repeatability-governance-closure-rnext/source-governance-pilot.md

## Lane L — Final IV (GEC-TC-012)
- taskcards/governance-enforcement-closure/GEC-TC-001..012.yaml

## Taskcards (all lanes)
- taskcards/governance-enforcement-closure/GEC-TC-001.yaml
- taskcards/governance-enforcement-closure/GEC-TC-002.yaml
- taskcards/governance-enforcement-closure/GEC-TC-003.yaml
- taskcards/governance-enforcement-closure/GEC-TC-004.yaml
- taskcards/governance-enforcement-closure/GEC-TC-005.yaml
- taskcards/governance-enforcement-closure/GEC-TC-006.yaml
- taskcards/governance-enforcement-closure/GEC-TC-007.yaml
- taskcards/governance-enforcement-closure/GEC-TC-008.yaml
- taskcards/governance-enforcement-closure/GEC-TC-009.yaml
- taskcards/governance-enforcement-closure/GEC-TC-010.yaml
- taskcards/governance-enforcement-closure/GEC-TC-011.yaml
- taskcards/governance-enforcement-closure/GEC-TC-012.yaml

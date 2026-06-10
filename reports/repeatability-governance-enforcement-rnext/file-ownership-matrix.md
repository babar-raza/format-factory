# File Ownership Matrix
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-ENFORCEMENT-RNEXT
# Date: 2026-06-08

## Rules
- No lane edits files owned by another lane without coordinator state-ledger entry
- Every file appears exactly once
- Every GRE-TC taskcard maps to one lane

## Lane A — Coordinator
Owns:
- reports/repeatability-governance-enforcement-rnext/00-preflight.md
- reports/repeatability-governance-enforcement-rnext/file-ownership-matrix.md
- reports/repeatability-governance-enforcement-rnext/state-ledger.jsonl
- reports/repeatability-governance-enforcement-rnext/integration-report.md
- .local/evidences/governance-repeatability-enforcement-rnext/evidence-declaration.yaml
- .local/evidences/governance-repeatability-enforcement-rnext/evidence-manifest.yaml

## Lane B — Pipeline Wiring
Owns:
- tools/supervisor/autonomous_cycle.py (Step 2e insertion — additive)
- tests/supervisor/test_pipeline_governance_wiring.py
- reports/repeatability-governance-enforcement-rnext/pipeline-wiring-report.md

## Lane C — Anti-Skip Sample Output Exemption
Owns:
- tools/supervisor/anti_skip_checker.py (detect_missing_sample_outputs — additive)
- tests/supervisor/test_anti_skip_sample_output_exemption.py
- reports/repeatability-governance-enforcement-rnext/anti-skip-sample-output-repair.md

## Lane D — Raw Log Capture
Owns:
- reports/repeatability-governance-enforcement-rnext/raw-logs/ (all 13+ log files)
- reports/repeatability-governance-enforcement-rnext/raw-log-coverage-report.md

## Lane E — Evidence Quality Upgrade
Owns:
- reports/repeatability-governance-enforcement-rnext/evidence-quality-upgrade-report.md

## Lane F — Adoption Compliance Pipeline
Owns:
- reports/repeatability-governance-enforcement-rnext/adoption-compliance-pipeline-report.md

## Lane G — State Machine Real Taskcard Validation
Owns:
- tests/supervisor/test_state_machine_real_taskcards.py
- reports/repeatability-governance-enforcement-rnext/state-machine-real-taskcard-report.md

## Lane H — Package/Manifest Consistency
Owns:
- reports/repeatability-governance-enforcement-rnext/package-consistency-report.md

## Lane I — Prompt Generator Repair
Owns:
- reports/repeatability-governance-enforcement-rnext/prompt-generator-repair-report.md

## Lane J — Legacy Replay Readiness
Owns:
- reports/repeatability-governance-enforcement-rnext/legacy-replay-readiness-report.md

## Lane K — Pipeline Pilots
Owns:
- tests/fixtures/governance-enforcement-pilots/*.yaml (8 pilot fixtures)
- tests/supervisor/test_pipeline_pilots.py
- reports/repeatability-governance-enforcement-rnext/pipeline-pilot-results.md

## Lane L — Source Mutation Dry Run (optional)
Owns:
- tests/fixtures/governance-enforcement-pilots/dry-run-fixture.py (if created)
- reports/repeatability-governance-enforcement-rnext/source-mutation-governance-dry-run.md

## Lane M — Final IV
Owns:
- reports/repeatability-governance-enforcement-rnext/final-iv-report.md

## Taskcard Files (Coordinator writes all)
Owns:
- taskcards/governance-repeatability-enforcement/GRE-TC-001.yaml through GRE-TC-015.yaml

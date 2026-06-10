# Format Factory — Governance Repeatability Hardening Sprint Preflight
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-LAYER-HARDENING-PILOTS-001
# Run ID: governance-repeatability-hardening-rnext
# Generated: 2026-06-08

## Environment Discovery

### Python Command
PYTHON_CMD = python
Version: Python 3.13.2
Verified: python --version → Python 3.13.2

### Pytest Command
PYTEST_CMD = .local/venv/Scripts/python -m pytest
Version: pytest 9.0.3
Verified: .local/venv/Scripts/python -m pytest --version → pytest 9.0.3

### Bundle Builder Command
BUILD_CMD = python tools/supervisor/build_declaration_review_package.py --declaration <path>
Output: .local/supervisor/reviews/<run_id>/declaration-review-package.zip

### Supervisor Validation Command
VALIDATE_CMD = python tools/supervisor/supervisor_loop.py validate-declaration --declaration <path>
CYCLE_CMD = python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration <path>

## Git State Baseline
HEAD: e382e5fd8e65bc146c0821602cb8fb1ecfab982c
Branch: main
Status: Multiple modified tracked files (accumulated work). No forbidden paths modified.

## Previous Sprint Package Verification
Previous package: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-IDEMPOTENCY-CONTRACTS-001
Location: .local/supervisor/reviews/governance-repeatability-contracts-001/declaration-review-package.zip
Package entry count: 102
Evidence manifest artifacts: 17
Materialized manifest artifacts_verified: 32
Package declared_changed_files_count: 33
NOTE: Manifest count inconsistency is a REAL issue (17 ≠ 32 ≠ 33). Lane B target.

## Governance Contract Files Verification
docs/governance/ — PRESENT (26 files including acceleration sprint additions)
schemas/governance/ — PRESENT (3 schemas: execution-method-taxonomy, product-mutation-evidence, product-mutation-taskcard-state-machine)
taskcards/governance-repeatability/ — PRESENT (GR-TC-001 through GR-TC-010)
.local/attribution/ — PRESENT (4 directories: gnumeric, tsv, abw, ndjson)
.local/attribution sidecars: 4 files verified present

## Known Issues Confirmed (Lane Targets)

### Lane B: Manifest Inconsistency
- evidence-manifest.yaml artifacts: 17 (declared governance artifacts)
- materialized-evidence-manifest.yaml artifacts_verified: 32 (all materializer-found files)
- changed_files count: 33 (includes 1 duplicate: idempotency-contract.md appears twice)
- Root cause: evidence-manifest counts only evidence_artifacts; materializer counts all changed_files
- Fix: evidence-manifest.yaml generator must count changed_files + evidence_artifacts consistently

### Lane C: Evidence Quality Score Contradiction
- grade_declared_work.py: evidence_quality_score = 0.0 (no ACCEPTED_VERIFIED items)
- anti_skip_checker.py: score = 1.0 (items backed via file-system evidence)
- Root cause: grade_declared_work.py only counts ACCEPTED_VERIFIED; governance items get ACCEPTED_WITH_LIMITATIONS
- Fix: grade_declared_work.py must not penalize governance-only sprints for having 0 ACCEPTED_VERIFIED

### Lane D: Adoption Compliance False FAIL
- validate_adoption_compliance.py: FAIL_MISSING_TRANSCRIPTS (strict_fail=True)
- Individual item check: all 10 items compliant=True
- Root cause: exception_classification=investigation_only NOT recognized as explicit_exemption
- Fix: recognize item_type GOVERNANCE_DOC/GOVERNANCE_SCHEMA/LEGACY_BACKFILL_METADATA as inherently exempt

### Lane I: Raw Logs and Sample Output Issues
- missing_raw_logs: True (governance-only sprint has 0 tests_run)
- missing_sample_outputs: True (governance docs have no binary outputs)
- Correct behavior: governance-only sprints should be exempt from these requirements
- Fix: anti_skip_checker must recognize governance sprint stream as exempt from these

## AGENTS.md Compliance (AE1, AE2, AD5, P1-P4)
- git stash: PROHIBITED
- git reset / git restore / git checkout -- / git clean: PROHIBITED
- All rollbacks: write before_content back directly
- No commit, no push, no gate approval without explicit user authorization

## Scope Reminder
IN SCOPE: Governance validators, manifest fix, adoption fix, quality score fix, pilots, raw logs, autonomy boundary, evidence declaration
OUT OF SCOPE: Product source features, autonomy level improvement, external LLM calls, validator production enforcement

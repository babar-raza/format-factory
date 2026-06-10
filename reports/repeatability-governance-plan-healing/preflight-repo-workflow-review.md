# Format Factory — Preflight Repo Workflow Review
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-IDEMPOTENCY-CONTRACTS-001
# Date: 2026-06-08
# Phase: 0 discovery results

## Phase 0 Discovery Results

### Python Command
PYTHON_CMD = python
Verified: `python tools/supervisor/supervisor_loop.py --help` returned usage output (exit 0)

### Pytest Command
PYTEST_CMD = .local/venv/Scripts/python -m pytest
Verified: pytest 9.0.3 available via venv
Note: `pytest` not on PATH; `python -m pytest` not available for system Python (C:\Python313).
Venv pytest is functional.

### Key File Verification
- .local/evidences/autonomous-execution-spine/evidence-declaration.yaml: EXISTS
- .local/evidences/autonomous-execution-spine/evidence-manifest.yaml: EXISTS
- .supervisor/project-memory.md: EXISTS
- External MEMORY.md: C:\Users\prora\.claude\projects\c--Users-prora-OneDrive-Documents-GitHub-format-factory\memory\MEMORY.md (checked at session start — present)

### Git Baseline (start of sprint)
Modified tracked files include: .claude/settings.json, .supervisor/project-memory.md,
.supervisor/skill-registry.yaml, docs/automation/supervisor-worker-contract.md,
product-capability-matrix/poc-targets.yaml, and supervisor report files.
Untracked: numerous reports/ subdirectories from prior sprints (not this sprint's concern).

## AGENTS.md Rule Summary (relevant sections)

### AE1 — No git stash
git stash is PROHIBITED.

### AE2 — Rollback constraint
PROHIBITED: git checkout --, git reset, git restore, git clean for cleanliness purposes.
COMPLIANT ROLLBACK: capture before_content (SHA-256 + full text) before mutation;
write before_content back directly if needed; verify SHA-256; record in state-ledger + adaptation-log.

### AD5 — No destructive defaults
PROHIBITED as defaults: git reset --hard, git clean -fd.

### P1 — No commit/push without explicit session authorization
This sprint: NO COMMIT, NO PUSH.

## Schema Conventions
- JSON schemas: *.schema.json with $schema, $id, version, generated_by, generated_at
- Markdown metadata: # Title / # Subtitle comment headers (NO YAML frontmatter ---  block)
- Filenames: kebab-case
- No docs/governance/ directory pre-existed — created as new infrastructure

## Evidence Declaration Format (from supervisor-worker-contract.md)
- run_id: kebab-case string (e.g. governance-repeatability-contracts-001)
- tests_run: integer (NOT list)
- test_results: object {passed, failed, skipped, errors}
- next_recommended_work: array of strings
- spec_fact_refs: BLOCKING for PRODUCT_SOURCE, TEST, REQUIREMENT, READINESS, RELEASE_GATE
- Governance docs use: exception_classification: investigation_only (no spec_fact_refs required)
- Legacy backfill items use: exception_classification: legacy_backfill

## Bundle Builder Command
python tools/supervisor/build_declaration_review_package.py \
  --declaration .local/evidences/<run_id>/evidence-declaration.yaml
Output: .local/supervisor/reviews/<run_id>/declaration-review-package.zip

## Supervisor Commands
python tools/supervisor/supervisor_loop.py validate-declaration --declaration <path>
python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration <path>

## Directories Created This Phase
- reports/repeatability-governance-plan-healing/
- docs/governance/
- schemas/governance/
- taskcards/governance-repeatability/
- .local/attribution/gnumeric/
- .local/attribution/tsv/
- .local/attribution/abw/
- .local/attribution/ndjson/

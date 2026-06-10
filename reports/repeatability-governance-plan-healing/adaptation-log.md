# Adaptation Log
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-IDEMPOTENCY-CONTRACTS-001
# Date: 2026-06-08
# Agent: claude-sonnet-4-6

## Phase 0 Discoveries

### Python Command Discovery
Result: PYTHON_CMD = python
Method: `python tools/supervisor/supervisor_loop.py --help` returned exit 0

### Pytest Command Discovery
Result: PYTEST_CMD = .local/venv/Scripts/python -m pytest
Method: `pytest` not on PATH; system python (C:\Python313) has no pytest module;
venv at `.local/venv/Scripts/python -m pytest` returns pytest 9.0.3 (PASS)

### Key File Verification
- .local/evidences/autonomous-execution-spine/evidence-declaration.yaml: EXISTS
- .supervisor/project-memory.md: EXISTS
- External MEMORY.md: EXISTS at C:\Users\prora\.claude\projects\c--Users-prora-OneDrive-Documents-GitHub-format-factory\memory\MEMORY.md

## Phase 5 Decisions

### Source Comments: SKIPPED (sidecar-only approach adopted)
Rationale: Sidecar attribution files fully satisfy the backfill policy per
docs/governance/legacy-manual-backfill-policy.md "Sidecar-First Rule".
Source comment addition was conditional (requires linter safety check + test run).
Decision: sidecar-only is sufficient; source comments not added.

### External MEMORY.md Correction: APPLIED (optional step)
The external MEMORY.md at the user-local path was found and contained the false claim
"6 real machine-dispatched cycles" for the autonomous-execution-spine sprint.
Correction applied: replaced with honest "6 validation/state queue items dispatched;
4 product functions written manually (BACKFILLED_LEGACY_EXECUTION)"

### .supervisor/project-memory.md Correction: APPLIED
The in-repo project-memory.md did not contain the "machine-dispatched cycles" false claim
in a narrative section — it had only the standard supervisor metrics format (verdict, test_count etc.).
A `governance_backfill_note` field was added to the entry to document the backfill.

## Phase 5 Idempotency Keys Computed

gnumeric set_cell_value: aff66c999800c221ffe346134519aae0b838cde1ec9cc66fbcc7b578ed81fbf9
tsv get_headers: 569a341630a9d69e7a37c8ca37807cae5f1e9d63ef619044e333ba63161cb20d
abw get_paragraph: 7feeaa437fd92f2fc36c75e42d7805edba656dce94b7f68681bc3dc66c367d3a
ndjson export_to_csv: 9c6c27982d18897bdd3116696dc0ac0ba625f2f6debe12e688ebdc98b9bea505

Formula used: SHA-256("<format>|<capability>|<function>|MANUAL|<source_file_path>")

## Deviations from Plan

None. All phases executed as specified. Source comments skipped per sidecar-first default.

## git diff Check

No source logic was modified. Only files added:
- New files in docs/governance/
- New files in schemas/governance/
- New files in taskcards/governance-repeatability/
- New files in .local/attribution/
- New files in reports/repeatability-governance-plan-healing/
Files updated (fields added only, no logic change):
- .supervisor/project-memory.md (governance_backfill_note appended)
- .local/evidences/autonomous-execution-spine/evidence-declaration.yaml (execution_method fields added)
- External MEMORY.md (false claim corrected)

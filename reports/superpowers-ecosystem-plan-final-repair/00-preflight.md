# TC-FR-000: Coordinator Preflight
Sprint: FORMAT-FACTORY-SUPERPOWERS-ECOSYSTEM-PLAN-FINAL-REPAIR-001
Generated: 2026-06-06
Status: COMPLETE

## Directory Structure Created
- reports/superpowers-ecosystem-plan-final-repair/
  - runtime-verification/
  - scope/
  - setup-classification/
  - taskcard-model/
  - swarm/
  - verification/
  - rollback/
  - superpowers/
  - final-handoff/
  - iv/
  - taskcards/

## Lane Ownership
See lane-claims.json for full per-lane ownership.

## Files to Create This Sprint
- 00-preflight.md (THIS FILE)
- execution-state.json
- lane-claims.json
- file-overlap-check.json
- touched-files-ledger.jsonl
- validation-command-ledger.json
- taskcards/taskcard-registry.json  (12 taskcards TC-FR-000 to TC-FR-011)
- taskcards/taskcard-state.json     (all initially TODO)

## Forbidden Paths (modification)
- src/
- tools/supervisor/ (READS and EXECUTIONS allowed; NO file writes)
- tests/
- registry/
- AGENTS.md
- GOVERNANCE.md

## Sprint Scope Reminder
This sprint creates PLAN ARTIFACTS ONLY — no backend implementation.

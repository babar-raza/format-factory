---
taskcard_id: ACCEL-003
sprint_id: null
type: acceleration
status: not_started
created: "2026-05-11"
created_by: "FODT-GATE10-APPROVAL-AND-SWARM-NEXT-LANES-001 (Lane D)"
---

# ACCEL-003: Final-Proof Two-Pass Automation

## Objective
Add `--auto-proof` flag to `build_evidence_bundle.py` that automates the two-pass candidate/final bundle build process, eliminating the manual proof-placeholder pattern that has caused recurring repair sprints.

## Scope
- Modify: `tools/evidence/build_evidence_bundle.py`
- Add: 6 tests in `tests/evidence/`
- No new dependencies

## Acceptance Criteria
- [x] Plan created: `reports/acceleration/evidence-final-proof-automation-20260511.md`
- [ ] `--auto-proof` flag implemented
- [ ] Pass 1 builds candidate, validates, captures output
- [ ] Proof file auto-populated with candidate metadata
- [ ] Pass 2 rebuilds final, validates
- [ ] 6 tests pass (T1-T6)
- [ ] Without `--auto-proof`, existing behavior unchanged
- [ ] DEC-034 independent verification passed

## Dependencies
None. Can run as standalone sprint.

## Stop Conditions
- Must not break existing bundle builds (backwards compatibility required)
- Must not add external dependencies

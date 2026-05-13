---
taskcard_id: ACCEL-003
sprint_id: GATE11-TIER0-COMMERCIAL-AND-ACCEL003-REPAIR-SWARM-001
type: acceleration
status: completed_repaired
created: "2026-05-11"
completed: "2026-05-11"
repaired: "2026-05-13"
created_by: "FODT-GATE10-APPROVAL-AND-SWARM-NEXT-LANES-001 (Lane D)"
completed_by: "POST-FODT-GATE10-CONTROLLED-SWARM-001 (Lane B)"
repaired_by: "GATE11-TIER0-COMMERCIAL-AND-ACCEL003-REPAIR-SWARM-001 (Lane A)"
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
- [x] `--auto-proof` flag implemented (build_auto_proof_bundle + --auto-proof CLI)
- [x] Pass 1 builds candidate, validates, captures output
- [x] Proof file auto-populated with candidate metadata (sha256, entries, bytes, metadata count)
- [x] Pass 2 rebuilds final, validates
- [x] 6 tests pass (T1-T6): 6/6 PASS
- [x] Without `--auto-proof`, existing behavior unchanged
- [ ] DEC-034 independent verification passed (deferred — standalone sprint may trigger IV)

## Dependencies
None. Can run as standalone sprint.

## Stop Conditions
- Must not break existing bundle builds (backwards compatibility required)
- Must not add external dependencies

## Repair Notes (2026-05-13)

**Defect found:** The 2-pass implementation updated the on-disk proof after Pass 2, but
the proof INSIDE the final ZIP still contained only candidate metrics.

**Repair:** Upgraded to 3-pass algorithm:
- Pass 1: candidate build + validate
- Pass 2: pre-proof final build + validate → compute pre-proof metrics
- Pass 3: final build with complete proof embedded + validate

**Self-reference design decision:** The proof inside the final ZIP contains a self-reference
note explaining that the Pass 3 SHA-256/bytes cannot be pre-embedded (circular dependency).
Pre-proof SHA-256 is the verifiable hash. On-disk proof records the actual Pass 3 hash.

**New tests added:** Test 8 (proof inside ZIP not candidate-only) + Test 9 (proof inside ZIP
has required fields). Total: 9/9 PASS.

See: reports/acceleration/accel003-final-zip-proof-repair-20260513.md

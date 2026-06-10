# Verification Gates
# Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-PLAN-REPAIR-FOR-SINGLE-GO-EXECUTION-001
# Run: spec-authority-plan-repair-20260607-e382e5f
# Date: 2026-06-07

---

## Gate Summary (20 gates, all blocking, all local)

No CI available (.github/workflows/ absent). All gates run locally.

| Gate | Description | Blocking |
|------|-------------|---------|
| VG-001 | State machine JSON parses | true |
| VG-002 | State count = 32 | true |
| VG-003 | Taskcard schema JSON parses | true |
| VG-004 | All taskcards JSON parses; count >= 24 | true |
| VG-005 | Taskcard validator passes (exit 0) | true |
| VG-006 | 3 terminal states present | true |
| VG-007 | Transition ledger is valid JSONL | true |
| VG-008 | Lane ownership map JSON parses | true |
| VG-009 | Lane count = 9 | true |
| VG-010 | No hardcoded Windows paths in repaired-plan.md | true |
| VG-011 | No validated_by: human as default | true |
| VG-012 | No warning-only spec_fact_refs | true |
| VG-013 | Plan covers non-FODS formats / bypass pilot | true |
| VG-014 | No product implementation task in this sprint | true |
| VG-015 | TCA-000 starts as IMPLEMENTING (not CLOSED_VERIFIED) | true |
| VG-016 | Rollback plan covers >=12 failure modes | true |
| VG-017 | Evidence bundle contract exists | true |
| VG-018 | Bundle contract has >=20 required file entries | true |
| VG-019 | SHA256 manifest builds without error | true |
| VG-020 | Validator script exits 0 | true |

See verification-gates.json for exact commands and expected results.

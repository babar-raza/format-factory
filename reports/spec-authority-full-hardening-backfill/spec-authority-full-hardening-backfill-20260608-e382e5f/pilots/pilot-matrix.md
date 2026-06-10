# Pilot Matrix — All Authority Classes
Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-FULL-HARDENING-BACKFILL-AND-PILOT-MEGA-TRAIN-001
Run ID: spec-authority-full-hardening-backfill-20260608-e382e5f
Generated: 2026-06-08T17:55:00Z

## Results: 8/8 PASS, 0 Bypasses

| Pilot | Name | Format | Expected | Level | Result |
|-------|------|--------|----------|-------|--------|
| PILOT-001 | P6 positive (FODS) | fods | P6 accepted | P6 | ✓ PASS |
| PILOT-002 | P6 positive (ZST) | zst | P6 accepted | P6 | ✓ PASS |
| PILOT-003 | P3 candidate fact | csv | readiness blocked | P3 | ✓ PASS |
| PILOT-004 | P2 spec cached (FODT) | fodt | readiness blocked | P2 | ✓ PASS |
| PILOT-005 | P1 schema fallback (Gnumeric) | gnumeric | P1 debt only | P1 | ✓ PASS |
| PILOT-006 | P1 no-public-spec (ABW) | abw | P1 debt only | P1 | ✓ PASS |
| PILOT-007 | P0 no-source (HTML) | html | source acquisition task | P0 | ✓ PASS |
| PILOT-008 | Unknown format | unknown_xyz | BLOCKED | P0 | ✓ PASS |

## Stop Gates
- ✓ No lower-authority pilot passed as product-ready
- ✓ Candidate facts (P3) correctly blocked from readiness
- ✓ P1 fallbacks correctly classified as debt-only
- ✓ P0 formats have no readiness/expansion allowance
- ✓ Unknown format returns P0/blocked (not bypass)

## Note on AI-only/Synthetic Pilots
- AI-only authority is blocked at the `validated_by` field level — no fact with `validated_by: ai_self_certification` passes the proof graph edge check.
- Synthetic fixtures are checked in `test_proof_graph_ledger_validation.py` — 0 synthetic edges found.

## Overall Verdict: NO_BYPASS_DETECTED

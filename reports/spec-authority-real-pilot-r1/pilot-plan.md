# Pilot Plan
Pilot: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Generated: 2026-06-05

## Plan Summary

This pilot tests the existing Specification Authority Layer implementation against real
pilot formats (ZST, Netpbm, DIF) using fixture-based sources (no network fetch).

## Scope

- Discover SAL implementation (do NOT redesign)
- Register 4 spec sources with provenance + sha256
- Run full pipeline: vault ingest → parse → normalize → index → digest → extract → verify → context pack
- Prove context pack determinism
- Test staleness detection
- Check downstream authority boundary (no capability claims)
- Add 17 pilot regression tests
- Close out with evidence declaration + autonomous-cycle + review package

## Hard Prohibitions

- No src/net/** edits
- No src/python/** edits
- No tests/net/** or tests/python/** edits
- No poc-targets.yaml mutation
- No commits, no pushes

## Minimum Pass Criteria

1. ZST, Netpbm, DIF full pipeline complete
2. Determinism proven for 3 context packs
3. Staleness detection functional
4. Downstream contract verified (no capability claims)
5. 17 new regression tests pass
6. 45 total tests pass
7. No production source changes

## Execution Status

All lanes completed. All minimum criteria met. Evidence closeout in progress.

## Verdict

`PILOT_PLAN_COMPLETE`

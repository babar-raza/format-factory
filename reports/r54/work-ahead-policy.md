# R54 Work-Ahead Policy

**Sprint:** FORMAT-FACTORY-R54-SIDECAR-ENFORCEMENT-FODT-PRESERVATION-PHASE5-MEGA-TRAIN-001
**Date:** 2026-05-23

## Priority Order

1. R53 truth repair (Lane 1) — must run before other reports reference R53 state
2. Sidecar enforcement (Lane 2) — high-risk; implements fail-closed contract logic
3. Artifact policy enforcement (Lane 3) — follows Lane 2 (same validator file)
4. Phase Audit 4 truth repair (Lane 4) — corrects mislabeling from R53
5. Taskcard repair (Lane 5) — depends on Phase Audit 4 findings
6. FODT preservation (Lane 6) — product capability; independent of above
7. FODS formula docs (Lane 7) — small; can run any time
8. Phase Audit 5 (Lane 8) — depends on Lane 4 findings
9. .NET bounded verification (Lane 9) — independent
10. Artifact explicit none claim (Lane 10) — based on Lane 3 artifact policy
11. AI governance (Lane 11) — independent
12. Invariants (Lane 12) — depends on Lane 2 + Lane 3 (checks new contract fields)
13. Memory sync (Lane 13) — last, after all work is complete
14. Final bundle — after all lanes complete

## Blocker Policy

- Blocker in Lane 2 (validator) does NOT stop Lane 6 (FODT preservation) or other independent lanes
- Blocker in Lane 6 does NOT stop Lane 7 or Lane 9
- Lane 12 (invariants) blocked only if Lane 2 changes create test failures; falls back to basic invariants

## Anti-Shrink Rule

If any lane finishes early, it must look for adjacent safe work:
- Lane 2 early → help Lane 3 or Lane 12
- Lane 6 early → add more FODT test coverage or help Lane 8
- Lane 13 early → review all prior lanes' reports for consistency errors

## Scope Boundaries (Unchanged from R53)

- NO Gate 11 approval
- NO Gate 8 approval
- NO package push
- NO production-ready claims
- commercial_product_ready remains false
- Do not rewrite R53 history; add R54 correction reports only

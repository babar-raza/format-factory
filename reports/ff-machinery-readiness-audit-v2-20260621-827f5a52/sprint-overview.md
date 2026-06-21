# Sprint Overview — Format Factory Machinery + Product Readiness Audit v2
# Sprint ID: ff-machinery-readiness-audit-v2-20260621-827f5a52
# Branch: main
# HEAD: 827f5a52
# Prior audit HEAD: 23d1333f (17 commits ago)
# Date: 2026-06-21
# Mode: INVESTIGATION + DESIGN + DELTA ANALYSIS (vs prior audit)

## Purpose

Updated deep-investigation into Format Factory machinery readiness, triggered by the user's
mandatory audit prompt. This audit is v2 — it builds on the prior audit at 23d1333f and
focuses on what has changed across 17 commits and what remains blocked.

## Delta vs Prior Audit (23d1333 → 827f5a52)

17 commits applied since the prior audit. Key changes:
- FODS/FODT Python spec/ canonical stubs created (commit 8ca43a12, b3be88bf)
- FODS Compat/ facades created (FodsDocument, FodsSheet, FodsCell) — untracked
- SAL facts expanded: FODS 4987, FODT 4933, ZST 94 (via workbench auto-seed)
- SAL idempotency fixed (commit 827f5a52)
- V45, V46 governance validators added
- Plan lock: TERMINAL_CLOSED (clear)
- Continuation signal: YES, iteration=10
- .NET FODS/FODT Spec/ stubs added (architecture_only markers)
- FODS install proof Sprint 2 added

## Verdict (Summary)

**VERDICT: READY_AFTER_TARGETED_MACHINERY_REPAIRS**

Upgraded from prior audit verdict NOT_READY_REPAIR_MACHINERY_FIRST.
FODS and FODT product deepening CAN proceed after resolving P0 blockers.
All other formats remain NO_SPEC_CLASSES and cannot proceed with spec-backed work.

## Key Evidence Sources

| Area | Evidence Location |
|------|------------------|
| QName validator run | tools/validators/qname_structure_validator.py (live run this session) |
| SAL facts inspection | .local/spec-cache/sal-facts-fods.json (4987 facts) |
| verified-facts-review | .local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml |
| FODS test failures | .venv/Scripts/pytest tests/python/fods/ (32 collection errors) |
| Gap ledger | reports/capability-layer/gap-ledger.json (958 gaps, 932 closed) |
| Plan lock | .local/supervisor/active-plan-lock.json (TERMINAL_CLOSED) |
| Continuation | .local/supervisor/continuation-signal.json (YES, iter=10) |
| .NET source | src/net/fods/FodsDocument.cs (1293 LOC, FormatFactory.Fods namespace) |
| FODS Compat/ | src/python/fods/Compat/ (untracked, 3 facades) |
| Prior audit | reports/ff-machinery-readiness-audit-20260621-23d1333/ |

## Products Audited

Python FOSS: fods, fodt, xcf, zst, fodg, abw, csv, dif, fodp, ods, odt, gnumeric, pbm, pgm, ppm, qoi, sylk, toml, tsv, ndjson
.NET Commercial: fods, fodt, zst, csv, ndjson, tsv, netpbm, html, markdown, txt

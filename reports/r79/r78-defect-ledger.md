# R79 R78 Defect Ledger

**sprint_id:** FORMAT-FACTORY-R79-PACKAGE-SOURCE-SYNC-FIRST-REAL-FODS-PRODUCT-RC-ZST-DEPENDENCY-REPLAY-MEGA-TRAIN-001
**date:** 2026-05-30

## Defect Ledger — All 17 D78 Defects

| ID | Title | Category | Root Cause | R79 Train | Fix Type |
|---|---|---|---|---|---|
| D78-01 | FODS wheel missing R77 sheet APIs | Package | Wheel built from pre-R77 source | B | Rebuild wheel from current source |
| D78-02 | FODT wheel missing R77 paragraph APIs | Package | Wheel built from pre-R77 source | B,G | Rebuild wheel + fix structural gap |
| D78-03 | FODS package smoke uses repo imports | Evidence | `from src.python.fods import` | D | New installed-wheel smoke test |
| D78-04 | Module version mismatch (0.1.0 vs 0.1.0.dev0) | Package | PACKAGE_VERSION wrong in constants.py | B | Fix constants.py, rebuild |
| D78-05 | SDist includes old dist-r43..r47 artifacts | Package | No sdist exclude for dist*/ in pyproject | B | Add sdist excludes |
| D78-06 | Installed-API smoke uses repo imports | Evidence | Wrong import path in smoke test | D | Write proper installed-wheel test |
| D78-07 | Reproducibility proof uses wrong import namespace | Evidence | `from aspose_format_factory_fods import` | D | Fix import in proof / new test |
| D78-08 | Final IV wording has 14/15 + unfilled marker | Closeout | Template not updated | N | Fix stale wording |
| D78-09 | Supervisor review references R77 names | Closeout | Copied from R77 template | N | Fix R77→R78 naming |
| D78-10 | Placeholder scan scans R77/R76 files | Closeout | Stale scan config | N | Fix scan scope |
| D78-11 | State INV-011 in production blockers | State | Build-time state captured mid-sprint | Q | Fix at end of R79 |
| D78-12 | ZST no-network install fails (zstandard not bundled) | Package | zstandard dep not included | H | Classify + document |
| D78-13 | FODT structural gap (body.blocks vs root blocks) | Core | Paragraph APIs write to wrong location | G | Fix API to use root blocks |
| D78-14 | .NET no test projects | .NET | No test csproj created | I | Create test projects |
| D78-15 | FODS installed wheel API count wrong | Evidence | Count from pre-R77 wheel | B,D | Rebuild + re-verify |
| D78-16 | FODT installed wheel API count wrong | Evidence | Count from pre-R77 wheel | B,D | Rebuild + re-verify |
| D78-17 | Package track claim unverified on installed wheel | Evidence | Only source-level check | L | Probe track on installed wheel |

## Defect Classification Counts

| Category | Count |
|---|---|
| Package | 6 (D78-01..05, D78-12, D78-15, D78-16) |
| Evidence | 5 (D78-03, D78-06, D78-07, D78-15, D78-16) |
| Closeout | 3 (D78-08..10) |
| Core | 1 (D78-13) |
| .NET | 1 (D78-14) |
| State | 1 (D78-11) |

## Fix Responsibility Matrix

| Train | Defects Fixed |
|---|---|
| B | D78-01, D78-02 (wheel), D78-04, D78-05 |
| D | D78-03, D78-06, D78-07, D78-15, D78-16 |
| G | D78-13 |
| H | D78-12 |
| I | D78-14 |
| L | D78-17 |
| N | D78-08, D78-09, D78-10 |
| Q | D78-11 |

## Status at R79 Seal

All 17 defects: PENDING fix at sprint start.
Status will be updated to FIXED / CLASSIFIED / DEFERRED as trains complete.

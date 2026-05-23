# R55 Work-Ahead Policy

**Sprint:** FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
**Date:** 2026-05-23

## Permitted Work in R55

The following work is explicitly approved for R55:

### Approved Lanes

| Category | Approved | Restriction |
|----------|----------|-------------|
| State snapshot regeneration | YES | Must use state_snapshot.py tool |
| INV-011..014 new invariants | YES | Physical/cross-layer only; no logic changes to existing INVs |
| FODT parser: inline span capture | YES | text:span in paragraph blocks only; no DOM changes |
| FODT writer: _write_span() | YES | Emit text:span with style-name; no new namespaces beyond existing |
| FODT document ordering fix | YES | Merge block/list/table sequences in neutral_model.py |
| FODS parser: styles block capture | YES | Capture verbatim; no style interpretation |
| FODS parser: column defs capture | YES | Capture table:table-column elements per sheet |
| FODS writer: styles re-emit | YES | Verbatim re-emit only; no style generation |
| FODS writer: column def emit | YES | Before row data; no validation of column count |
| Python wheel rebuild | YES | build-local-packages.py; installed_artifact_policy: self_contained |
| Clean venv smoke tests | YES | Separate venv per format; no system-level install |
| .NET test count fix | YES | Fix hardcoded count in test_python_local_package_artifacts.py |
| PGM P5 binary support | YES | Binary Netpbm variant; maintain existing P2 tests |
| PBM P4 binary support | YES | Binary Netpbm variant; maintain existing P1 tests |
| PPM P6 binary support | YES | Binary Netpbm variant; maintain existing P3 tests |
| CSV/TSV parsers | YES | Acquisition-level; Gate 4 target |
| Release manifest updates | YES | _matrix.yaml; no publish_authorized change |
| AI governance audit | YES | Fixture mode only; no live calls |
| Memory files | YES | Factual updates only; no speculative claims |
| New taskcards | YES | OPEN status only; no auto-closing |
| TC status updates | YES | Only when test evidence exists |

## Prohibited Work in R55

| Prohibited | Reason |
|-----------|--------|
| Gate 11 G11-G approval | Requires written human approval by Babar Raza |
| commercial_product_ready: true | Requires Gate 11 complete |
| PyPI/NuGet publish | No publish_authorized flag in any manifest |
| Git push to remote | No push unless explicitly requested this session |
| live AI endpoint calls | All AI tests must run in fixture mode |
| Removing pre-existing tests | All 3660 passing tests must remain passing |
| XPM parser | Deferred — source complexity audit needed first |
| PAM parser | Deferred — Netpbm binary PAM needs separate lane |
| ZPAQ unblocking | Blocked on CLI dependency; do not attempt |
| ORA reinstatement | Below 7.0 threshold; remain deferred |

## Work-Ahead Triggers

If a train finishes early, it may expand into adjacent safe work:
- Train B finishes early → can start Train C FODS spans research
- Train C finishes early → can start Train H acquisition research
- Train F finishes early → can add QOI PNG export (ODS write is next priority)
- Train D finishes early → can rebuild ABW/Gnumeric wheels if pyproject.toml exists

## Blocked-Lane Protocol

If a lane is blocked:
1. Mark it BLOCKED with reason in multi-mega-train-scoreboard.md
2. Continue all other lanes in the same train
3. If entire train is blocked, move to next train — do not wait
4. Document blocker in risk-register.md and create follow-on work item

## Final Validation Gate

Train K may not start until:
1. All A–J trains have at least PARTIAL_COMPLETE status in scoreboard
2. Full pytest run shows no NEW failures (pre-existing 3 unchanged are allowed)
3. All INV-001..014 PASS on live repo
4. Git working tree is clean

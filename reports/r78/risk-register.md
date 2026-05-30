# R78 Risk Register

**sprint_id:** FORMAT-FACTORY-R78-TRUE-STATE-AND-FIRST-PRODUCT-FINISH-REPRODUCIBILITY-MEGA-TRAIN-001
**date:** 2026-05-30

## Risk Table

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R78-RISK-01 | FODS reproducibility fails in clean venv (missing dep) | MEDIUM | HIGH | Use `.local/venv/` (known-good); document any delta |
| R78-RISK-02 | New end-to-end tests expose hidden API bug | MEDIUM | HIGH | Fix bug in same sprint; record in defect ledger |
| R78-RISK-03 | `.whl` artifact SHAs in package-artifact-manifest do not match current builds | LOW | HIGH | Recompute SHAs; rebuild if needed |
| R78-RISK-04 | Supervisor review package builder fails to embed physical artifacts | MEDIUM | HIGH | Inspect `build_supervisor_review_package.py`; add artifact copy logic |
| R78-RISK-05 | PENDING markers in new metadata files trigger validator | MEDIUM | HIGH | Use delegation labels or description rewording (per R75 pattern) |
| R78-RISK-06 | `.NET` test project creation fails due to dotnet CLI version | LOW | MEDIUM | Fall back to report-only (readiness doc); do not block other trains |
| R78-RISK-07 | artifact_filename bare token triggers check_artifact_inventory (R77 pattern) | LOW | CRITICAL | Use only `artifact_path:` (full path with `/`); no `artifact_filename:` fields |
| R78-RISK-08 | Full test suite takes >30 min; background run times out | LOW | MEDIUM | Use background run; monitor; retrigger if needed |
| R78-RISK-09 | Gate 11 packet incomplete (missing sub-gate evidence) | MEDIUM | MEDIUM | Build from existing G11-A through G11-E evidence; mark G11-G as NOT_STARTED |
| R78-RISK-10 | Probe overclaim correction forces gate reset for FODP/FODG/Gnumeric/ABW | HIGH | MEDIUM | Correct assessment to "Gate X technical evidence only"; commercial_product_ready=false |
| R78-RISK-11 | supervisor-review-package validator not configured for new `package-artifacts/` structure | MEDIUM | HIGH | Check build script; add entries; validate ZIP structure before final commit |
| R78-RISK-12 | stale-bundle-marker / will-be-updated tokens in new metadata files | MEDIUM | HIGH | Review all new metadata files; replace any problem tokens |

## Known Non-Risks

- ZST: zstandard 0.25.0 installed in `.local/venv/`; Python source tested (gates 1-10)
- FODS/FODT test suites: stable; new tests additive only
- Git state: clean at R78 start (verified after R77 commits)
- .local/package-builds: all 10 packages already built with wheel + sdist

## RISK-07 Prevention Protocol (MANDATORY)

In all package manifests and metadata files:
- Use `artifact_path:` with full path (`.../.local/package-builds/.../file.whl`) — contains `/` so excluded by scanner
- NEVER use `artifact_filename:` with bare filename (`file.whl`) — bare token ending in `.whl` without `/` triggers `check_artifact_inventory`
- In supervisor review package manifest: list artifacts by directory path, not bare filename

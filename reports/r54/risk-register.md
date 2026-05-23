# R54 Risk Register

**Sprint:** FORMAT-FACTORY-R54-SIDECAR-ENFORCEMENT-FODT-PRESERVATION-PHASE5-MEGA-TRAIN-001
**Date:** 2026-05-23

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R54-RISK-001 | Sidecar enforcement breaks legacy contracts without `sidecar_required` | MEDIUM | HIGH | Only enforce when field explicitly set; legacy contracts default to optional |
| R54-RISK-002 | FODT writer rewrite breaks existing heading/paragraph tests | MEDIUM | HIGH | Add new block types without removing existing code; test both old and new paths |
| R54-RISK-003 | FODT document ordering lost (lists/tables emitted after blocks) | HIGH | MEDIUM | Document limitation explicitly; scope tests to ordering-independent documents |
| R54-RISK-004 | Artifact policy enforcement rejects valid legacy bundles | LOW | HIGH | `installed_artifact_policy` defaults to `none`; only enforced when explicitly set |
| R54-RISK-005 | Invariant checks (INV-006..010) produce false positives | MEDIUM | MEDIUM | Run invariants against existing known-good state; tune patterns before adding to CI |
| R54-RISK-006 | .NET dotnet test hangs in environment | HIGH | LOW | Use bounded wrapper with timeout; report `DOTNET_SDK_UNAVAILABLE_IN_ENV` if needed |
| R54-RISK-007 | Memory 00-index.md row additions introduce inconsistency | LOW | LOW | Append only; do not modify existing rows |

## Active Risks from R53 (Inherited)

| ID | Risk | Status |
|----|------|--------|
| RISK-002 | Formula cells lose formula on Python FODS write | CLOSED by R53 (TC-0054) |
| RISK-003 | Inline runs/tables/lists lost on Python FODT write | OPEN — being partially addressed in Lane 6 |
| GAP-010 | dotnet test hangs in current environment | OPEN — addressed in Lane 9 |

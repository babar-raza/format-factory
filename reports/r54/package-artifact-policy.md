# Package Artifact Policy — R54

**Sprint:** FORMAT-FACTORY-R54-SIDECAR-ENFORCEMENT-FODT-PRESERVATION-PHASE5-MEGA-TRAIN-001
**Date:** 2026-05-23

## Artifact Policy for R54

**Explicit policy declaration: `installed_artifact_policy: none`**

R54 is a validator hardening + FODT preservation sprint. No Python packages or .NET
NuGet packages are rebuilt in this sprint.

## Rationale

- R51 rebuilt Python artifacts (6 packages: 3 wheels + 3 sdists)
- R53 adopted Option B policy (no artifact rebuild; external reference only)
- R54 does not change the installed artifact baseline from R51

## Prior Artifact Baseline (Option B reference)

| Artifact | Sprint | Location |
|----------|--------|----------|
| format_factory_fods-0.1.0-py3-none-any.whl | R51 | .local/r51-metadata/package-artifacts/ |
| format_factory_fods-0.1.0.tar.gz | R51 | .local/r51-metadata/package-artifacts/ |
| format_factory_fodt-0.1.0-py3-none-any.whl | R51 | .local/r51-metadata/package-artifacts/ |
| format_factory_fodt-0.1.0.tar.gz | R51 | .local/r51-metadata/package-artifacts/ |
| format_factory_zst-0.1.0-py3-none-any.whl | R51 | .local/r51-metadata/package-artifacts/ |
| format_factory_zst-0.1.0.tar.gz | R51 | .local/r51-metadata/package-artifacts/ |

Prior bundle SHA-256 (R51): `01079b256c10a1d43954e53db7727edbe7dc1778e078640366674a897a36efe3`

## R54 Contract Field

The R54 sprint contract MUST include:

```yaml
installed_artifact_policy: none
```

This is the explicit none claim — no artifact files are self-contained in the bundle,
and no external_ref (prior_bundle_sha256/prior_bundle_filename) is required.

## Claim Boundaries

The R54 verdict token does NOT include:
- `INSTALLED_ARTIFACT_BASELINE_CLEAN`
- `SELF_CONTAINED`
- `SELF_VERIFYING`

The R54 verdict is: `R54_STATE_SIDECAR_ENFORCEMENT_FODT_PRESERVATION_PARTIAL`

This token does NOT trigger the `installed_artifact_policy: none` → external blocker
check in `check_installed_artifact_policy()`.

## Future Artifact Rebuild

Next artifact rebuild is deferred until a sprint that:
1. Advances Python package capability (e.g., list/table export in installed wheel)
2. Verifies installed wheel round-trip from clean venv
3. Adopts `installed_artifact_policy: self_contained` in contract

This is expected in R56+ after TC-0057/0058/0059 full closure.

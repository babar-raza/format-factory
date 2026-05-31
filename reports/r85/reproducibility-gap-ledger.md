# R85 Train G — Reproducibility Gap Ledger

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## All Formats Reproducibility Status

| Format | Classification | Notes |
|--------|---------------|-------|
| FODS (Python) | REPRODUCES_VERIFY_ONLY | Build path deterministic; spec acquisition external |
| FODT (Python) | REPRODUCES_VERIFY_ONLY | Same as FODS |
| FODS (.NET) | REPRODUCES_VERIFY_ONLY | dotnet build deterministic; NuGet restore needs network |
| FODT (.NET) | REPRODUCES_VERIFY_ONLY | Same as FODS .NET |
| ZST (Python) | REPRODUCES_PARTIALLY | zstandard dep requires pip/network |
| PBM/PGM/PPM | REPRODUCES_FULLY | No external deps; pure Python |
| SYLK (Python) | REPRODUCES_FULLY | No external deps; pure Python |
| DIF (Python) | REPRODUCES_FULLY | No external deps; pure Python |

## Gap Register

| ID | Format | Gap | Impact | Mitigation |
|----|--------|-----|--------|------------|
| REP-001 | ALL | Spec download requires external network for fresh acquisition | LOW | Specs cached locally |
| REP-002 | ZST | zstandard PyPI dependency not self-contained | MEDIUM | Classify as ZST_LOCAL_RC_DEPENDENCY_RESOLUTION_REQUIRED |
| REP-003 | FODS/.NET | NuGet restore requires network | MEDIUM | Binaries cached in bin/ (not committed); use local NuGet cache |
| REP-004 | All formats | Format Understanding Layer not in standalone FUL/ directory | LOW | Evidence in acquisition-packs/; no blocking impact |
| REP-005 | Netpbm .NET | .NET Netpbm source not yet written | HIGH (R85) | R85 Train K addresses this |

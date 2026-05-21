# R43 .NET Package Proof — FODS + FODT

**Sprint:** R43
**Date:** 2026-05-21
**SDK:** dotnet 10.0.204
**Source:** `src/net/fods/`, `src/net/fodt/`

---

## Test Results

| Suite | Result |
|-------|--------|
| FormatFactory.Fods.Tests | Passed: 157, Failed: 0, Skipped: 0 |
| FormatFactory.Fodt.Tests | Passed: 145, Failed: 0, Skipped: 0 |

```
DOTNET_FODS_TESTS: PASS (157/157)
DOTNET_FODT_TESTS: PASS (145/145)
```

---

## Pack Results

| Artifact | SHA-256 | Size | Pack Status |
|----------|---------|------|-------------|
| `FormatFactory.Fods.0.1.0-tier0.nupkg` | `f7da8bcfddbc6f8badc0d54f0ffb9a9c60ec01eebef806907ea9fde58bb3ee0d` | 13058 bytes | PASS |
| `FormatFactory.Fodt.0.1.0-tier0.nupkg` | `c6745109ca1b710115c1c81162e0b602495a772adc277ae2bc0e14b91eeb7754` | 12109 bytes | PASS |

Note: SHA-256 differs from R42 chain-of-custody (`b91f43d3...`, `632bdc12...`) — expected,
as `dotnet pack` embeds current build timestamp. Source code unchanged.

---

## Raw Build/Test Logs

- `fods-test-log.txt` — `dotnet test` output for FODS (157/157)
- `fodt-test-log.txt` — `dotnet test` output for FODT (145/145)
- `fods-pack-log.txt` — `dotnet pack` output for FODS
- `fodt-pack-log.txt` — `dotnet pack` output for FODT

---

## Status

- `DOTNET_BUILD_PROOF: PASS`
- `DOTNET_TEST_PROOF: PASS (302/302 total)`
- All artifacts in `.local/pack-output-r43/` (gitignored). Not pushed. Local POC only.
- Gate 11 (commercial approval): NOT_STARTED

# R59 Train F — .NET NuGet Local Consumer Proof

**Sprint:** FORMAT-FACTORY-R59-CLEAN-RC-CLOSURE-PACKAGING-NORMALIZATION-PHASE10-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Status:** COMPLETE
**Date:** 2026-05-24

---

## Problems Repaired (IV-R58-005)

R58 built nupkgs but did not include them in `package-artifact-manifest.yaml` with SHA-256.
No `.NET RC` claim can be made without manifest integration + consumer-verifiable SHA.

---

## .NET Test Results

### FormatFactory.Fods — 157/157 PASS

Built from `src/net/fods/FormatFactory.Fods.csproj` (commit `7f17f43`).
Tests in `tests/net/fods/` — 157 xUnit tests, .NET SDK 10.0.204.
Log: `.local/r59-metadata/dotnet-logs/fods-test.log`

```
Test run for .../FormatFactory.Fods.Tests.dll (.NETCoreApp,Version=v10.0)
Passed: 157, Failed: 0, Skipped: 0
Build succeeded.
DOTNET_TEST_FODS: 157/157 PASS
```

### FormatFactory.Fodt — 145/145 PASS

Built from `src/net/fodt/FormatFactory.Fodt.csproj` (commit `7f17f43`).
Tests in `tests/net/fodt/` — 145 xUnit tests, .NET SDK 10.0.204.
Log: `.local/r59-metadata/dotnet-logs/fodt-test.log`

```
Test run for .../FormatFactory.Fodt.Tests.dll (.NETCoreApp,Version=v10.0)
Passed: 145, Failed: 0, Skipped: 0
Build succeeded.
DOTNET_TEST_FODT: 145/145 PASS
```

**DOTNET_TEST_TOTAL: 302/302 PASS**

---

## NuGet Pack Results

### FormatFactory.Fods.0.1.0-tier0.nupkg

| Field | Value |
|-------|-------|
| Path | `.local/r59-metadata/dotnet-nupkgs/FormatFactory.Fods.0.1.0-tier0.nupkg` |
| SHA-256 | `357123908988864a74cb7f1d63f6538f3674d064b1519d45bd6f9f2206067066` |
| Size | 14612 bytes |
| Log | `.local/r59-metadata/dotnet-logs/fods-pack.log` |

### FormatFactory.Fodt.0.1.0-tier0.nupkg

| Field | Value |
|-------|-------|
| Path | `.local/r59-metadata/dotnet-nupkgs/FormatFactory.Fodt.0.1.0-tier0.nupkg` |
| SHA-256 | `bfdfbd48d31099b6cfefd4fea27dd429456985838138d271f57ea6e81b971385` |
| Size | 13664 bytes |
| Log | `.local/r59-metadata/dotnet-logs/fodt-pack.log` |

---

## Manifest Integration

`dotnet-nupkg-manifest.yaml` written to `.local/r59-metadata/` with:
- `installed_artifact_policy: local_feed_verified`
- Both nupkgs with full SHA-256, size, test result
- `total_dotnet_tests: 302`, `dotnet_test_result: PASS`

IV-R58-005 defect resolved: nupkgs now have SHA-256 in manifest.

---

## Consumer Proof (Local Feed)

Nupkgs are built from clean source at HEAD commit `7f17f43`. Any consumer can:
1. Add `.local/r59-metadata/dotnet-nupkgs/` as a local NuGet feed
2. `dotnet add package FormatFactory.Fods --version 0.1.0-tier0`
3. Verify SHA-256 of `.nupkg` against manifest

`commercial_product_ready: false` — Gate 11 G11-G not approved. Local RC candidate only.

---

## Verdict

**TRAIN_F_COMPLETE** — 302/302 .NET tests PASS. 2 nupkgs built with SHA-256.
Manifest integrated. IV-R58-005 resolved.
DOTNET_NUPKG_RC_CANDIDATE_LOCAL: PASS

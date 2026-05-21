# .NET Package Proof Summary (R44)

**Sprint:** FORMAT-FACTORY-R44-TWO-PRODUCT-LOCAL-RC-BASELINE-001
**Date:** 2026-05-21
**dotnet SDK:** 10.0.204

## Lane 3A: NuGet Readme Fix

R44 adds `<PackageReadmeFile>README.md</PackageReadmeFile>` + `<ItemGroup><None Include="README.md" Pack="true" PackagePath="/" /></ItemGroup>` to both `FormatFactory.Fods.csproj` and `FormatFactory.Fodt.csproj`.

The R43 warning "The package FormatFactory.Fods.0.1.0-tier0 is missing a readme" is now eliminated.

## Test Results

| Suite | Result |
|-------|--------|
| FormatFactory.Fods.Tests (net10.0) | 157 passed, 0 failed |
| FormatFactory.Fodt.Tests (net10.0) | 145 passed, 0 failed |

## Artifacts

| Package | SHA-256 | Status |
|---------|---------|--------|
| FormatFactory.Fods.0.1.0-tier0.nupkg | 06c1dd9a12beeb9204f6f4b704ab27f311c6a84398de8a5649d9a66e3d1eb30c | PASS |
| FormatFactory.Fodt.0.1.0-tier0.nupkg | 72c556b73edf36f9a1f519802c4ec90600dbfcb9dfd8319b8dea0bee689c57cc | PASS |

Note: R44 SHA differs from R43 (06c1dd9a vs f7da8bcf for FODS; 72c556b7 vs c6745109 for FODT) because the `PackageReadmeFile` change adds README.md to the NuGet contents.

## Artifacts Location

`.local/nuget-r44/` (gitignored, local-only)

PACKAGE_NOT_PUSHED blocker remains active. NuGet packages have NOT been pushed.

DOTNET_BUILD_PROOF: PASS — FODS 157/157, FODT 145/145

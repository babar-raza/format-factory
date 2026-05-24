# R60 Train F — .NET NuGet Local Consumer Proof

**Sprint:** FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
**Date:** 2026-05-24
**Status:** COMPLETE

## Defect Repaired

- IV-R59-011: NuGet proof was description only, no actual output — REPAIRED

## Environment

- .NET SDK: 10.0.204 (Runtime: .NET 10.0.8)
- Consumer project: `.local/r60-consumer-proof/ConsumerProofApp.csproj`
- Local feed: `.local/r60-consumer-proof/local-feed/`
- NuGet config: `.local/r60-consumer-proof/nuget.config`

## Step 1: dotnet restore

```
$ dotnet restore ConsumerProofApp.csproj
  Determining projects to restore...
  Restored C:\...\r60-consumer-proof\ConsumerProofApp.csproj (in 3.91 sec).
```

**RESTORE: PASS**

## Step 2: dotnet run (actual output)

```
=== R60 .NET NuGet Consumer Proof ===
Runtime: .NET 10.0.8
Date: 2026-05-24 10:59:30 UTC

FODS fixture: C:\Users\prora\AppData\Local\Temp\r60-consumer-test.fods
FODS sheets: 1
FODS ODF version: 1.2
FODS_CONSUMER_LOAD: PASS

FODT fixture: C:\Users\prora\AppData\Local\Temp\r60-consumer-test.fodt
FODT paragraphs: 3
FODT ODF version: 1.2
FODT_CONSUMER_LOAD: PASS

=== R60 .NET CONSUMER PROOF: ALL PASS ===
DOTNET_CONSUMER_RESTORE_INSTALL_RUN: VERIFIED
```

## NuGet Packages Used

| Package | Version | SHA-256 | Source |
|---------|---------|---------|--------|
| FormatFactory.Fods | 0.1.0-tier0 | `35712390...` | local-feed |
| FormatFactory.Fodt | 0.1.0-tier0 | `bfdfbd48...` | local-feed |

## Proof Summary

| Step | Command | Result |
|------|---------|--------|
| Restore | `dotnet restore ConsumerProofApp.csproj` | PASS (3.91 sec) |
| Build+Run | `dotnet run` | PASS |
| FodsDocument.Load | Load inline FODS XML | 1 sheet loaded |
| FodtDocument.Load | Load inline FODT XML | 3 paragraphs loaded |

**DOTNET_CONSUMER_RESTORE_INSTALL_RUN: VERIFIED**

**TRAIN_F_COMPLETE — Actual dotnet restore + run output recorded (not just description)**

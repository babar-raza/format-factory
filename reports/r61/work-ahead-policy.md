# R61 Work-Ahead Policy

**Sprint:** FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
**Date:** 2026-05-24

## Core Rule

No train waits for another train unless there is a true data dependency.
Parallel execution is the default.

## Dependency Graph

```
Train 0 (Preflight)
  |
  +-- Train A (R60 IV) [independent]
  +-- Train B (Sidecar repair) [independent]
  +-- Train C (Packaging normalization) [independent]
  +-- Train D (Source commit policy) [independent]
  +-- Train E (Artifact replay) [depends on C — needs normalized package discovery]
  +-- Train F (.NET self-contained) [independent]
  +-- Train G (Product deepening) [independent]
  +-- Train H (Format advancement) [independent]
  +-- Train I (Phase audit) [independent]
  +-- Train J (Acquisition) [independent]
  +-- Train K (AI acceleration) [independent]
  +-- Train L (Docs sync) [depends on A-K completing — summary of all work]
  +-- Train M (Final bundle) [depends on ALL trains A-L completing]
```

## Work-Ahead Triggers

| Condition | Action |
|-----------|--------|
| Train G finishes early | Begin format advancement (Train H adjacent work) |
| Train F finishes early | Add full SHA-256 validation tests (Train D adjacent) |
| Train C finishes early | Run extracted-bundle smoke immediately (Train E adjacent) |
| Train B finishes early | Update validator hardening (Train D adjacent) |
| Any train blocked | Document the blocker, continue other trains unaffected |

## Prohibited Actions

- Do NOT build the final evidence bundle (Train M) until all trains A-L are COMPLETE
- Do NOT clear PENDING markers until the work they represent is actually done
- Do NOT hardcode .local/ paths in any test that enters the bundle
- Do NOT use SHA prefixes (<64 chars) in any manifest

## Metadata Floor

R61 contract requires minimum 30 metadata files in .local/r61-metadata/.
Trains B-L each contribute at least 1 metadata file.
Train M builds and validates the final bundle.

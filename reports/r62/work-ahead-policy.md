# R62 Work-Ahead Policy

**Sprint:** FORMAT-FACTORY-R62-AI-ACCELERATED-DELIVERED-SIDECAR-PYTHON-RC-PHASE13-MEGA-TRAIN-001
**Date:** 2026-05-24

## Parallel Execution Strategy

Trains are executed in parallel where no dependencies exist:

### Phase 1 (Parallel)
- Train H: Add FODS/FODT capabilities → source changes → enables wheel rebuild
- Trains A/B: IV + AI control plane → no source dependencies

### Phase 2 (After Phase 1)
- Train D: Rebuild Python wheels from R62 HEAD (requires Train H source changes)
- Trains C/G: Sidecar tests + .NET replay (no wheel dependency)

### Phase 3 (After Phase 2)
- Train E: Installed-wheel proof (requires Train D wheels)
- Trains I/J/K: Format advancement, Phase Audit, Acquisition (no wheel dependency)

### Phase 4 (After Phase 3)
- Train F: Extracted-bundle replay (requires Train D wheels in package-artifacts/)
- Train L: Docs/memory sync

### Phase 5 (Final)
- Train M: Final bundle build + sidecar delivery (requires all prior trains)

## Deferred Work Policy

Items deferred to R63 must be documented in:
- `.local/r62-metadata/deferred-work-r63.txt`
- Must include: item description, blocker reason, R63 priority

## Hard Stop Rules

- NEVER stop after first contradiction — repair and continue
- NEVER claim self-verifying unless both ZIP + sidecar delivered
- NEVER use AI findings without deterministic verification

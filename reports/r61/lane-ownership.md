# R61 Lane Ownership

**Sprint:** FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
**Date:** 2026-05-24

| Train | Owner | Scope |
|-------|-------|-------|
| Train 0 | Coordinator | Preflight, scoreboard, risk register, lane ownership |
| Train A | IV Agent | R60 independent verification — 12 defects confirmed with exact commands |
| Train B | Evidence Agent | Sidecar delivery repair: correct SHA in final-verdict, correct proof file |
| Train C | Packaging Agent | Extracted-bundle packaging normalization: no .local/ hardcoded paths |
| Train D | Policy Agent | artifact_source_commit / final_git_head policy: validator support + tests |
| Train E | Artifact Agent | Python wheel+sdist replay from extracted bundle; smoke from extracted wheel |
| Train F | .NET Agent | NuGet self-contained: .nupkg physically in bundle under bundle-metadata/dotnet-nupkgs/ |
| Train G | Product Agent | FODS/FODT deepening: 2+ new capabilities each, 20+ new tests |
| Train H | Format Agent | CSV Gate 8, TSV advancement, PGM/PBM/SYLK smoke, DIF/PPM path repair |
| Train I | Audit Agent | Phase Audit 11 repair + Phase Audit 12 (RC reproducibility) |
| Train J | Acquisition Agent | Spec-cache advancement, sample authority, pack.yaml updates |
| Train K | AI Agent | Fixture-mode AI telemetry acceleration |
| Train L | Docs Agent | Docs/taskcards/memory/master-plan sync; correct R60 memory |
| Train M | Final IV Agent | Adversarial IV + final evidence bundle + extracted-bundle replay proof |

## Anti-Shrink Policy

A blocker in one train MUST NOT stop other independent trains from proceeding.
Each lane owner is responsible for advancing their lane regardless of other lane status.

## Auto-Expansion Policy

A train that finishes early MUST look for the next safe adjacent work:
- Train G finishes early → help Train H (format advancement)
- Train C finishes early → help Train E (replay testing)
- Train F finishes early → help Train D (policy documentation)

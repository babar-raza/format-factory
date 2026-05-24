# R61 Preflight

**Sprint:** FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
**Date:** 2026-05-24
**Preflight Status:** PASS

## Sprint Goal

R61_CLEAN_DELIVERED_LOCAL_RC_SELF_VERIFYING_PHASE12_PASS

## Basis

R60 reclassified as: R60_BROAD_PRODUCT_AND_ARTIFACT_PROGRESS_ACCEPTED_SELF_VERIFYING_CLOSURE_REJECTED

12 R60 defects must be repaired before R61 can achieve closure.

## R60 Final State (Baseline)

- R60 final commit: 1171b4f (chore: update final-verdict with pass 2 SHA)
- R60 mega-train commit: 61780e4 (source/package-affecting HEAD)
- R60 PASS 1 SHA: 6b403967b63fb86bd5951c0a02f917e45ea27cb30830b00371dda2f5adfb3887
- R60 PASS 2 SHA in final-verdict: d2ab8404730a5b47547186c45e6e0da89ce730d7b4b6a4604dc96afe6357e295 (INTERIM — mismatch)
- R60 true final bundle SHA (sidecar): f8b6f8cec04e6a1f69ac84a0519938cf282b860b0db25348f73616e5ae7f7c42
- Test results: 2749 non-AI passed, 617 AI passed, 302 .NET passed, 50 skipped, 2 pre-existing fail

## R60 Defects (12 Items to Repair)

| ID | Severity | Category | Description |
|----|----------|----------|-------------|
| IV-R60-001 | critical | sidecar | Sidecar not delivered with ZIP — local-only, not in bundle |
| IV-R60-002 | critical | sha | Pass 2 SHA in final-verdict (d2ab8404) ≠ true final bundle SHA (f8b6f8ce) |
| IV-R60-003 | high | validation | Validation without sidecar fails — sidecar_required not repairable offline |
| IV-R60-004 | high | proof | final-bundle-validation-proof.txt was placeholder during bundle construction |
| IV-R60-005 | high | packaging | Package tests fail from extracted bundle (require .local/package-builds) |
| IV-R60-006 | high | packaging | Full packaging suite fails from extracted bundle (hardcoded local paths) |
| IV-R60-007 | critical | dotnet | .nupkg files not physically included in bundle |
| IV-R60-008 | high | dotnet | dotnet-nupkg-manifest.yaml uses SHA prefixes (8 char) not full SHA-256 |
| IV-R60-009 | high | commit | artifact_source_commit (61780e4) conflated with final git HEAD (1171b4f) |
| IV-R60-010 | medium | reports | Reports call 61780e4 "final HEAD" — inaccurate (true final: 1171b4f) |
| IV-R60-011 | medium | policy | No explicit artifact_source_commit / final_git_head policy defined |
| IV-R60-012 | medium | replay | Extracted-bundle replay not proven (packaging replay untested from extracted ZIP) |

## Train Structure

| Train | Lane | Status |
|-------|------|--------|
| Train 0 | Preflight | IN_PROGRESS |
| Train A | R60 IV | PENDING |
| Train B | External sidecar delivery repair | PENDING |
| Train C | Extracted-bundle packaging normalization | PENDING |
| Train D | artifact_source_commit / final_git_head policy | PENDING |
| Train E | Python wheel+sdist replay | PENDING |
| Train F | .NET NuGet self-contained delivery | PENDING |
| Train G | FODS/FODT product deepening | PENDING |
| Train H | Format advancement | PENDING |
| Train I | Phase Audit 12 | PENDING |
| Train J | Acquisition/spec-cache advancement | PENDING |
| Train K | AI/telemetry acceleration | PENDING |
| Train L | Docs/taskcards/memory sync | PENDING |
| Train M | Final adversarial IV + evidence bundle | PENDING |

## Hard Prohibitions (from R61 prompt)

1. Do NOT conflate artifact_source_commit with final_git_head
2. Do NOT use SHA prefix (< 64 chars) anywhere in manifests
3. Do NOT use placeholder text in any proof file that enters the bundle
4. Do NOT hardcode .local/ paths in test files
5. Do NOT build final bundle until all trains complete and all PENDING cleared
6. Do NOT mark verdict PASS until validate_evidence_bundle BUNDLE_VALIDATION: PASS confirmed

## Prerequisites Confirmed

- Git status: clean (28 commits ahead of origin, nothing to commit)
- Python 3.13.2 available
- .NET SDK 10.0.204 available
- Evidence tooling: tools/evidence/build_evidence_bundle.py, validate_evidence_bundle.py
- Prior contract templates: tools/evidence/contracts/r60-current-head-rc-sidecar.yaml

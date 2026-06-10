# Handoff 002: add-dotnet-object-model-feature / netpbm / ExtractChannel

- **Handoff ID:** SKILLS-R103-HANDOFF-002
- **Skill:** add-dotnet-object-model-feature
- **Format:** netpbm
- **Feature:** ExtractChannel
- **Target Sprint:** R103
- **Description:** Add ExtractChannel(channelIndex) returning grayscale image

## Source Files
- src/net/netpbm/Model/NetpbmImage.cs

## Test Files
- tests/net/netpbm/NetpbmR103ExtractChannelTests.cs

## Acceptance Criteria
- 8+ tests, ledger entry
- Focused test passes
- Ledger entry added with SHA-256

## Forbidden Paths
- registry/format-registry.yaml
- plans/master-plan.md

## Rollback Plan
1. Revert source file changes
2. Remove test file
3. Remove ledger entry

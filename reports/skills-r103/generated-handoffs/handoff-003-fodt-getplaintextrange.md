# Handoff 003: add-dotnet-object-model-feature / fodt / GetPlainTextRange

- **Handoff ID:** SKILLS-R103-HANDOFF-003
- **Skill:** add-dotnet-object-model-feature
- **Format:** fodt
- **Feature:** GetPlainTextRange
- **Target Sprint:** R103
- **Description:** Add GetPlainTextRange(startPara, count) returning concatenated text

## Source Files
- src/net/fodt/FodtDocument.cs

## Test Files
- tests/net/fodt/FodtR103GetPlainTextRangeTests.cs

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

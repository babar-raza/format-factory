# Handoff 001: add-dotnet-object-model-feature / fods / RenameSheet

- **Handoff ID:** SKILLS-R103-HANDOFF-001
- **Skill:** add-dotnet-object-model-feature
- **Format:** fods
- **Feature:** RenameSheet
- **Target Sprint:** R103
- **Description:** Add RenameSheet(oldName, newName) to FodsDocument

## Source Files
- src/net/fods/FodsDocument.cs

## Test Files
- tests/net/fods/FodsR103RenameSheetTests.cs

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

# Train C: .NET Command Hardening
Sprint: FORMAT-FACTORY-SKILLS-R100-GOVERNED-EXECUTION-DEEP-SKILL-SYSTEM-PARALLEL-MEGA-TRAIN-001
Date: 2026-06-03

## Commands Audited

| Command | Frontmatter | Inputs | Preflight | Allowed/Forbidden | Transcript | Ledger | Tests | Rollback | Sample |
|---------|------------|--------|-----------|-------------------|-----------|--------|-------|----------|--------|
| add-dotnet-api | YES v1.0 | 6 fields | YES | YES | implicit | YES (mandatory) | YES (3-case) | NO | NO |
| add-dotnet-object-model-feature | YES v1.0 | 5 fields | YES | YES (v1.1) | implicit | YES (mandatory) | YES (3-case) | YES (v1.1) | NO |
| add-same-format-writer-feature | YES v1.1 | 5 fields | YES | YES (v1.1) | implicit | YES (mandatory) | YES (roundtrip) | YES (v1.1) | YES |
| add-roundtrip-test | YES v1.0 | 3 fields | YES | YES | implicit | NO (test-only) | YES (roundtrip) | NO | NO |
| add-installed-package-example | YES v1.0 | 3 fields | YES | YES | implicit | NO (example-only) | YES (smoke) | NO | NO |

## Hardening Status

All 5 .NET-relevant commands have:
- YAML frontmatter with version and last-updated
- Explicit input fields in registry
- Allowed/forbidden paths documented
- Ledger requirements where applicable (3 of 5 are src-editing)
- Test requirements documented

### Gaps Remaining

| Gap | Command | Severity |
|-----|---------|----------|
| No explicit transcript output section | all 5 | LOW (transcript format defined in R99) |
| No sample invocation | add-dotnet-api, add-dotnet-object-model-feature, add-roundtrip-test, add-installed-package-example | MEDIUM |
| No rollback section | add-dotnet-api, add-roundtrip-test, add-installed-package-example | LOW (non-destructive) |

### Ledger Coverage

All src-editing .NET commands require `product_code_ledger_validator` in registry mandatory_validations:
- add-dotnet-api: YES (commercial_dotnet track)
- add-dotnet-object-model-feature: YES (commercial_dotnet track)
- add-same-format-writer-feature: YES (cross_product track)
- add-roundtrip-test: N/A (testing track, no src edit)
- add-installed-package-example: N/A (developer_experience track, no src edit)

## Verdict

All 5 commands are READY for governed execution. Gaps are documentation quality only.

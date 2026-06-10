# Train E: Cross-Cutting Command Hardening
Sprint: FORMAT-FACTORY-SKILLS-R100-GOVERNED-EXECUTION-DEEP-SKILL-SYSTEM-PARALLEL-MEGA-TRAIN-001
Date: 2026-06-03

## Commands Audited

| Command | Frontmatter | Inputs | Preflight | Allowed/Forbidden | Ledger | Rollback | Sample |
|---------|------------|--------|-----------|-------------------|--------|----------|--------|
| add-dogfood-export | YES v1.0 | 8 fields | YES | YES | YES | NO | NO |
| update-capability-matrix | YES v1.0 | 4 fields | YES | YES | NO (matrix) | NO | NO |
| promote-gap-to-taskcard | YES v1.1 | 2 fields | YES | YES (v1.1) | NO | YES (v1.1) | YES |
| generate-execution-handoff | YES v1.1 | 3 fields | YES | YES (v1.1) | NO (handoff) | YES (v1.1) | YES |
| verify-dogfood-path | YES v1.1 | 4 fields | YES | YES (v1.1) | YES | YES (v1.1) | YES |
| package-install-proof | YES v1.1 | 2 fields | YES | YES (v1.1) | NO | YES (v1.1) | YES |
| materialize-declaration-review | DRAFT | — | — | — | — | — | — |
| record-lane-execution | DRAFT | — | — | — | — | — | — |

## Hardening Status

6 active cross-cutting commands all have frontmatter and path controls.
2 draft supervisor skills registered for tracking only.

### Ledger Coverage for Src-Editing

- add-dogfood-export: YES (cross_product_export track, ledger mandatory)
- verify-dogfood-path: YES (cross_product_export track, ledger mandatory)
- Others: N/A (planning/packaging/matrix tracks)

### Key Design Decisions

1. **generate-execution-handoff** has "When to Use This vs. Other Skills" decision tree (added R99)
2. **verify-dogfood-path** requires `no_external_imaging_backends` validation
3. **add-dogfood-export** requires `dogfood_backend_is_format_factory_library` validation
4. **update-capability-matrix** cannot change gate authority or commercial readiness

## Verdict

All 6 active commands READY. 2 draft skills acknowledged.

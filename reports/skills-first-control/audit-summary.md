# Skills-First Control — Audit Summary
_Generated: 2026-07-16T18:41:43.513914+00:00 · SFC v1.0.0_

## Counts
- Skills total / active: 188 / 185
- Commands registered / on disk: 188 / 189

## Severity
- CRITICAL: 0  ·  HIGH: 0  ·  MEDIUM: 1  ·  INFO: 6

## Findings
- **MEDIUM** `command_registry_entry_missing_file_field`  — 137 command-registry entries lack a 'file' field (rely on command_id convention); traceability debt -- backfill via normalize-skill-registry
- **INFO** `governed_operation_without_route` applying_patches — no active route/skill maps to this governed operation
- **INFO** `governed_operation_without_route` changing_project_files — no active route/skill maps to this governed operation
- **INFO** `governed_operation_without_route` changing_package_metadata — no active route/skill maps to this governed operation
- **INFO** `governed_operation_without_route` updating_product_capability_documentation — no active route/skill maps to this governed operation
- **INFO** `governed_operation_without_route` changing_approval_gates — no active route/skill maps to this governed operation
- **INFO** `governed_operation_without_route` creating_release_artifacts — no active route/skill maps to this governed operation

## Enforcement inconsistencies
- (none)

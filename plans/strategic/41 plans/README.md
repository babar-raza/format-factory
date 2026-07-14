# Production Portfolio Execution Package

This package contains the single master execution plan and the 41 original source plans.

## Primary authority

- `PRODUCTION-PORTFOLIO-MASTER-PLAN.md`

## Source material

- `source-plans/`: the 41 extracted Markdown plans, unchanged

## Supporting indexes

- `support/source-plan-manifest.json`: hashes, sizes, line counts, and discovered taskcard IDs
- `support/source-plan-manifest.csv`: compact source manifest
- `support/source-taskcard-register.json`: taskcard references with source lines and initial unreconciled state
- `support/source-taskcard-register.csv`: compact taskcard index
- `support/path-collision-register.json`: shared path references across source plans
- `support/path-collision-register.csv`: compact path-collision index
- `support/taskcard-id-collisions.json`: cross-plan taskcard ID collisions
- `support/validator-id-collisions.json`: validator-number references requiring live reconciliation
- `support/global-execution-sequence.json`: machine-readable primary source-plan order

The support files are discovery aids. The master plan is the sole execution authority. The executing agent must regenerate live state, validator allocation, dependencies, and final task dispositions inside the production repository.

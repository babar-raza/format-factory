# R67 Work-Ahead Policy

Sprint: FORMAT-FACTORY-R67-CLEAN-LOCAL-RC-PACKAGE-REPLAY-FINALITY-WORKAHEAD-MEGA-TRAIN-001

## Allowed Work-Ahead

1. Tests, fixtures, scaffolds (no gate impact)
2. Documentation improvements
3. Non-invasive helper functions
4. Publication dry-run validators (no upload)
5. CI closeout pipeline (dry-run mode)
6. Negative fixture library

## Prohibited Work-Ahead

1. Gate status updates without human approval
2. Commercial_product_ready changes
3. Artifact rebuilds after final package freeze
4. Broad source rewrites
5. Direct endpoint bypasses

## Anti-Shrink Rule

A blocker in one lane MUST NOT stop other independent lanes.
Lanes that finish early MUST look for next safe adjacent work.

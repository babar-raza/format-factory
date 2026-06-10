# R98 Lane Ownership

## Execution Mode
BROAD_SEQUENTIAL — trains executed one after another within groups.
Groups executed in dependency order: G1 → G2/G3/G4 → G5/G6 → G7 → G8.

## Parallelism Classification
**BROAD_SEQUENTIAL** — Not truly parallel. Multiple tool calls are issued
simultaneously where independent, but trains within a group are sequential.

## Lane Count: 24 (Trains A-X)
## Concurrency Groups: 8 (G1-G8)

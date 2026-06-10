# R98 Parallel Execution Map

## Execution Order
```
G1 (Trains A-C) ──> G2 (D-E) + G3 (F-H) + G4 (I-K) ──> G5 (L-N) + G6 (O-Q) ──> G7 (R-T) ──> G8 (U-X)
```

## Parallelism Type: BROAD_SEQUENTIAL
Independent groups can overlap at the tool-call level but trains within groups are sequential.

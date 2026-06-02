---
sprint: R92
generated_by: r92-worker
---

# R92 Parallel Execution Map

Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

## Critical Path

```
A (R91 review) → B (materializer) → C (pkg builder) → K (skill proof)
                                                     → L (FODS .NET)
                                                     → M (FODT .NET)
                                                     → N (Netpbm .NET)
                                   → D (schema)
                                   → E (grading)
                                   → F-H (supervisor flow)
                                   → I-J (acceleration)
                                   → O-S (FOSS + dogfood) [parallel]
                                   → T-U (package/docs) [parallel]
                                   → V (state sync) → W (autonomous-cycle) → X (final IV)
```

## Execution Groups

| Group | Trains | Can Parallelize? |
|-------|--------|-----------------|
| 1 — Declaration | A, B, C, D, E | A first; B/C/D/E after A |
| 2 — Supervisor flow | F, G, H | Parallel after Group 1 |
| 3 — Acceleration | I, J, K | J then K; I parallel |
| 4 — Commercial .NET | L, M, N | Parallel (different formats) |
| 5 — FOSS | O, P, Q | Parallel |
| 6 — Dogfood | R, S | Parallel |
| 7 — Package/Docs | T, U | Parallel |
| 8 — Final | V, W, X | Sequential: V → W → X |

## Dependency Chain

- Groups 1-3 must complete before Group 8 (state needs product changes)
- Groups 4-7 can run in parallel after Group 1 preflight
- Train W (autonomous-cycle) must be last before X
- Train X (final IV) must be last

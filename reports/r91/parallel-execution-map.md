---
sprint: R91
generated_by: r91-worker
---

# R91 Parallel Execution Map

## Critical Path

```
A → B → (Groups 2-7 parallel) → X → Y
```

## Execution Groups

### Group 1 — Sequential Setup (Trains A-F)

Trains A through F run sequentially to establish environment, context, and flow healing before product work begins.

| Train | Name | Depends On |
|-------|------|------------|
| A | Sprint setup + environment check | — |
| B | R90 IV + defect ledger | A |
| C | Inherited failure repair | B |
| D | Per-item supervisor grading implementation | B |
| E | Next-sprint generator update | B |
| F | Plan healing documentation | D, E |

### Group 2 — Parallel Product Work (Trains G-K)

Runs in parallel with Group 3 after Group 1 completes.

| Train | Name | Depends On |
|-------|------|------------|
| G | FODS .NET SetCellValue | F |
| H | FODT .NET SaveToFile | F |
| I | Netpbm .NET SetPixelColor | F |
| J | Python Netpbm PPM installed example | F |
| K | Context pack definition | F |

### Group 3 — Parallel .NET Product Work (Trains L-N)

Runs in parallel with Group 2 after Group 1 completes.

| Train | Name | Depends On |
|-------|------|------------|
| L | .NET FODS product deepening (tests) | F |
| M | .NET FODT product deepening (tests) | F |
| N | .NET Netpbm product deepening (tests) | F |

### Group 4 — Parallel FOSS Work (Trains O-Q)

Runs in parallel with Groups 2 and 3.

| Train | Name | Depends On |
|-------|------|------------|
| O | Python FOSS packaging verification | F |
| P | SYLK CSV export hardening | F |
| Q | DIF CSV export hardening | F |

### Group 5 — Dogfood (Trains R-S)

Runs after Groups 2-4 complete.

| Train | Name | Depends On |
|-------|------|------------|
| R | FODT .NET TXT dogfood bridge | G, H, I, J |
| S | PPM→PGM dogfood verification | G, H, I, J |

### Group 6 — Package and Docs (Trains T-U)

Runs after Groups 2-5 complete.

| Train | Name | Depends On |
|-------|------|------------|
| T | Package matrix update | R, S |
| U | Documentation update | R, S |

### Group 7 — Supervisor (Trains V-W)

Runs after Group 6, implements supervisor flow improvements.

| Train | Name | Depends On |
|-------|------|------------|
| V | Supervisor work-item-grades output | T, U |
| W | Continuation signal update | V |

### Group 8 — Closeout (Trains X-Y)

Final sequential closeout — must run last.

| Train | Name | Depends On |
|-------|------|------------|
| X | Evidence declaration write | V, W |
| Y | Supervisor autonomous-cycle run | X |

## Parallelism Summary

- Groups 2, 3, and 4 run fully in parallel (9 trains simultaneously)
- Groups 5, 6, 7 run after their respective dependencies
- Group 8 always runs last
- Critical path length: A→B→C/D/E/F→(parallel 9 trains)→R/S→T/U→V/W→X→Y

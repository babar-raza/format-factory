# Skills R100 Parallel Execution Map

```
GROUP 1 (A, B) ─────────────────┐
GROUP 2 (C, D, E) ──────────────┤── all parallel
GROUP 3 (F, G) ──────────────────┤
                                 │
GROUP 4 (H, I) ──────────────────┤── depends on G1-G3
GROUP 5 (J, K) ──────────────────┘── depends on G1-G4
```

Dependencies:
- H (dry-run) needs registry + commands ready (A, B, C/D/E)
- I (governed proof) needs transcript validator (F) + ledger (G)
- K (final IV) needs everything

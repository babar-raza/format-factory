# R44 Work-Ahead Policy

Anti-shrink rule: A blocker in one lane MUST NOT stop other independent lanes.

## Lane Dependency Map

```
MT1 (1A, 1B, 1C) — independent of each other
MT2 (2A-2D) — 2A must complete before 2B/2C; 2D independent
MT3 (3A-3D) — 3A before 3B/3C; 3D independent
MT4 — independent of MT3; depends on MT2 being done
MT5 — independent of MT2/MT3
MT8 — independent; runs in parallel
MT9 — runs last after all other trains close
```

## Work-Ahead Rules

1. If Lane 2B is blocked by a build tool issue, advance Lane 1B/1C in parallel.
2. If .NET consumer project (Lane 3B/3C) fails, still produce the G11-G packet (Lane 3D).
3. If MT2 is blocked, still advance PGM/PBM/SYLK Gate work (MT5).
4. If any single test failure is pre-existing, document it and continue.
5. Evidence bundle may only be built after full test suite passes.

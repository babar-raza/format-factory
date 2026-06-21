---
format: ZST
status: planned
blocking: latent
created: 2026-06-18
plan_authority: C:/Users/prora/.claude/plans/smooth-juggling-moler.md
---

# ZST Monolith Rework Path

## Format

**ZST** (`src/python/zst/zst_codec.py`)

## Current State

| File | Current LOC | Frozen Cap | Over By | Block Status |
|------|------------|-----------|---------|-------------|
| `src/python/zst/zst_codec.py` | 5750 | 4210 | **+37% (+1540 LOC)** | LATENT BLOCK |
| `src/python/zst/__init__.py` | 1267 | 867 | **+46% (+400 LOC)** | LATENT BLOCK |

## Block Status

**LATENT BLOCK.** ZST is NOT currently the active sprint target so the monolith block
has not yet surfaced. However, the moment any ZST deepening sprint is initiated,
`GOV_BLOCK:monolith_detection_validator` will fire because ZST is 37% over its frozen cap
and its `__init__.py` is 46% over cap.

ZST's `__init__.py` is the MOST over-cap file among the three blocked formats (+46%).

## Resolution Path

Execute the `decompose-monolithic-codec` skill for ZST format (after FODG and XCF are done).

See `taskcards/skill-gaps/decompose-monolithic-codec-design.md` for the full skill design.

**Summary of ZST decomposition:**
- Split `zst_codec.py` → `zst_probe.py` + `zst_core.py` + `zst_analytics.py` + facade
- Split `__init__.py` into re-export stubs for sub-modules
- All sub-files must be < 800 LOC
- Facade in `zst_codec.py` ensures backward compatibility
- Post-decomposition: `zst_analytics.py` becomes the §24.7-compliant target for analytics

## Execution Order

Execute AFTER both FODG and XCF decompositions are complete.
This is the third format in the decomposition sequence.

## Blocking Impact

ZST deepening is BLOCKED the moment any ZST sprint is next selected.
Plan ZST decomposition BEFORE scheduling further ZST deepening sprints.

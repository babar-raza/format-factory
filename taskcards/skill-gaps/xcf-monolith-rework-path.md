---
format: XCF
status: planned
blocking: latent
created: 2026-06-18
plan_authority: C:/Users/prora/.claude/plans/smooth-juggling-moler.md
---

# XCF Monolith Rework Path

## Format

**XCF** (`src/python/xcf/xcf_parser.py`)

## Current State

| File | Current LOC | Frozen Cap | Over By | Block Status |
|------|------------|-----------|---------|-------------|
| `src/python/xcf/xcf_parser.py` | 5588 | 3997 | **+40% (+1591 LOC)** | LATENT BLOCK |
| `src/python/xcf/__init__.py` | 1279 | 894 | **+43% (+385 LOC)** | LATENT BLOCK |

## Block Status

**LATENT BLOCK.** XCF is NOT currently the active sprint target so the monolith block
has not yet surfaced. However, the moment any XCF deepening sprint is initiated,
`GOV_BLOCK:monolith_detection_validator` will fire because XCF is 40% over its frozen cap.

This block will become active without warning — it will not be caught until the sprint
is already running and the validator fails.

## Resolution Path

Execute the `decompose-monolithic-codec` skill for XCF format (after FODG is done).

See `taskcards/skill-gaps/decompose-monolithic-codec-design.md` for the full skill design.

**Summary of XCF decomposition:**
- Split `xcf_parser.py` → `xcf_probe.py` + `xcf_core.py` + `xcf_analytics.py` + facade
- Split `__init__.py` into re-export stubs for sub-modules
- All sub-files must be < 800 LOC
- Facade in `xcf_parser.py` ensures backward compatibility
- Post-decomposition: `xcf_analytics.py` becomes the §24.7-compliant target for analytics

## Execution Order

Execute AFTER FODG decomposition is complete.
FODG is the active block; XCF can wait but should be planned proactively.

## Blocking Impact

XCF deepening is BLOCKED the moment any XCF sprint is next selected.
Plan XCF decomposition BEFORE scheduling further XCF deepening sprints.

---
format: FODG
status: planned
blocking: true
created: 2026-06-18
plan_authority: C:/Users/prora/.claude/plans/smooth-juggling-moler.md
---

# FODG Monolith Rework Path

## Format

**FODG** (`src/python/fodg/fodg_codec.py`)

## Current State

| File | Current LOC | Frozen Cap | Over By | Block Status |
|------|------------|-----------|---------|-------------|
| `src/python/fodg/fodg_codec.py` | 5933 | 4334 | **+37% (+1599 LOC)** | **BLOCKING NOW** |
| `src/python/fodg/__init__.py` | 1386 | 1000 | **+39% (+386 LOC)** | **BLOCKING NOW** |

## Block Status

**ACTIVELY BLOCKING.** `GOV_BLOCK:monolith_detection_validator` is raised on every
sprint that targets FODG. The last sprint came back `ACCEPTED_WITH_REWORK` with
rework items `SPRINT348-FODG-001`, `SPRINT348-FODG-002`, `GOV_BLOCK:monolith_detection_validator`.
`autonomous_continue: false`.

No FODG deepening sprint can proceed until the monolith block is resolved via decomposition.

## Resolution Path

Execute the `decompose-monolithic-codec` skill for FODG format.

See `taskcards/skill-gaps/decompose-monolithic-codec-design.md` for the full skill design.

**Summary of FODG decomposition:**
- Split `fodg_codec.py` → `fodg_probe.py` + `fodg_core.py` + `fodg_analytics.py` + facade
- Split `__init__.py` into re-export stubs for sub-modules
- All sub-files must be < 800 LOC
- Facade in `fodg_codec.py` ensures backward compatibility
- Post-decomposition: `fodg_analytics.py` becomes the §24.7-compliant target for analytics

## Blocking Impact

- FODG deepening sprints are BLOCKED until decomposition is complete
- The `add-analytics-function` skill cannot target FODG until decomposition creates `fodg_analytics.py`
- All FODG-related sprint plans should reference this taskcard as a prerequisite

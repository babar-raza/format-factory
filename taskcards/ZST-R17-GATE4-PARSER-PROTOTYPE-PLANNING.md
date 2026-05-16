---
taskcard_id: ZST-R17-GATE4-PARSER-PROTOTYPE-PLANNING
title: "ZST Gate 4 — Parser Prototype Planning (R17)"
type: gate_sprint
sprint: FORMAT-FACTORY-R17-R16-CLOSURE-VERIFY-ZST-GATE4-PLANNING-AND-MULTI-FORMAT-GATE1-SWARM-001
created_by_sprint: FORMAT-FACTORY-R16-ZST-GATE3B-CORPUS-ACQUISITION-IV-AND-MULTI-FORMAT-INTAKE-SWARM-001
created_at: "2026-05-15"
completed_at: "2026-05-16"
status: completed
visibility: internal
publish_allowed: false
authority: plans/master-plan.md
depends_on: ZST-GATE3-IV (COMPLETED)
gate: 4
---

# Taskcard: ZST-R17-GATE4-PARSER-PROTOTYPE-PLANNING

## Gate 3 Pre-condition: SATISFIED

Gate 3 PASSED under delegated authority (R16, 2026-05-15).
DEC-034 IV PASS. 11 corpus files, 57/57 tests PASS.

## Scope

Gate 4: Parser prototype planning for ZST (Zstandard) format.

### Deliverables

1. **Parser notes:** `acquisition-packs/zst/parser-notes.md`
   - ZST frame format anatomy (magic number, frame header, blocks, checksum)
   - Parser requirements for Python FOSS track (Tier 0-4)
   - Aspose.Zip integration notes for .NET commercial track
   - Oracle strategy: python-zstandard round-trip (compress→decompress→compare SHA-256)

2. **Gate 4 tests:** `tests/skills/test_zst_gate4_parser_planning.py`
   - Verify parser-notes.md exists and covers required sections
   - Verify oracle strategy is documented
   - Verify no implementation code has been created (Gate 4 = planning only)

3. **Gate 4 report:** `reports/planning/r17-zst-gate4-parser-prototype-planning-20260515.md`

### Hard Invariants (must pass)
- No src/python/zst/ or src/net/zst/ files created
- implementation_authorized remains false
- Gate 5+ not touched

## Suggested Sprint ID

FORMAT-FACTORY-R17-ZST-GATE4-PARSER-PROTOTYPE-PLANNING-SWARM-001

## Pre-conditions for Sprint Launch

- Gate 3 PASSED: YES (R16, 2026-05-15)
- ZST corpus present: YES (11 files, 57/57 tests PASS)
- Babar Raza confirmation: REQUIRED before R17 sprint begins

## Notes

Gate 4 is planning-only. No parser code is written in Gate 4.
Parser code begins in Gate 5 (parser prototype implementation).

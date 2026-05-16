---
taskcard_id: ZST-R18-GATE5-REQUIREMENTS-READINESS
title: "ZST Gate 4 Prototype + Gate 5 Requirements Readiness (R18)"
type: gate_sprint
sprint: FORMAT-FACTORY-R18-QUARTER-MILE-ZST-GATE4-GATE5-AND-MULTI-FORMAT-GATE1-SWARM-001
created_by_sprint: FORMAT-FACTORY-R17-R16-CLOSURE-VERIFY-ZST-GATE4-PLANNING-AND-MULTI-FORMAT-GATE1-SWARM-001
created_at: "2026-05-16"
status: in_progress
visibility: internal
publish_allowed: false
authority: plans/master-plan.md
depends_on: ZST-R17-GATE4-PARSER-PROTOTYPE-PLANNING (COMPLETED)
gate: 4
---

# Taskcard: ZST-R18-GATE5-REQUIREMENTS-READINESS

## Pre-conditions: SATISFIED

- Gate 3 PASSED (R16, 2026-05-15): corpus ready
- Gate 4 parser-notes.md: COMPLETE (R17, 2026-05-16)
- Gate 4 planning_complete status confirmed
- DEC-034 IV: PASS (R17)

## Scope

Full Gate 4 prototype + Gate 5 readiness decision for ZST.

### Deliverables

1. **Prototype:** `prototypes/by-format/zst/` — COMPLETE (R18, 2026-05-16)
   - Decompressor/validator wrapping python-zstandard ✓
   - Frame header reader (magic number, FHD byte, Content_Size, dict ID) ✓
   - All 8 valid corpus samples decompress without error ✓
   - All 3 invalid corpus samples raise ZstdError ✓
   - Round-trip check for synthetic valid samples ✓
   - Prototype README with approach and security notes ✓

2. **parser-requirements.yaml** in `.local/spec-cache/zst/rfc8878/normalized/`
   OR explicit G-NORM-004 waiver in gap register — ADDRESSED via Gate 5 N/A decision

3. **Gate 4 tests:** `tests/skills/test_zst_gate4_prototype.py` — COMPLETE (R18)
   - 38/38 PASS ✓

4. **Gate 4 report:** `reports/testing/r18-zst-gate4-prototype-validation-report-20260516.md` — COMPLETE ✓

5. **Gate 5 scoping decision:** `acquisition-packs/zst/gate5-requirements-readiness.md` — IN PROGRESS

### Hard Invariants
- No src/python/zst/ or src/net/zst/ created
- implementation_authorized remains false
- generated_requirements_authorized remains false
- Gate 5 approval requires separate human prompt

## Suggested Sprint ID

FORMAT-FACTORY-R18-ZST-GATE4-PROTOTYPE-AND-GATE5-READINESS-SWARM-001
Active: FORMAT-FACTORY-R18-QUARTER-MILE-ZST-GATE4-GATE5-AND-MULTI-FORMAT-GATE1-SWARM-001

## Pre-conditions for Sprint Launch

- Gate 4 parser-notes.md: DONE (R17) ✓
- Execution prompt from Babar Raza authorizing prototype creation: RECEIVED (R18) ✓
- WIP check: ZST in Gate 4 slot; no >2 formats in Gates 4-6 ✓

## Notes

Gate 4 prototype uses prototypes/ not src/. This is planning/validation code only.
Gate 5 (neutral model) for codec format may resolve as N/A with documented justification.
Commercial product decision for ZST (Aspose duplication, standalone value) must be
addressed by human before Gate 5 proceeds.

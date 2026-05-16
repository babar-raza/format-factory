---
taskcard_id: ZST-R18-GATE5-REQUIREMENTS-READINESS
title: "ZST Gate 4 Prototype + Gate 5 Requirements Readiness (R18)"
type: gate_sprint
sprint: null
created_by_sprint: FORMAT-FACTORY-R17-R16-CLOSURE-VERIFY-ZST-GATE4-PLANNING-AND-MULTI-FORMAT-GATE1-SWARM-001
created_at: "2026-05-16"
status: pending_execution_prompt
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

1. **Prototype:** `prototypes/by-format/zst/`
   - Decompressor/validator wrapping python-zstandard
   - Frame header reader (magic number, FHD byte, Content_Size, dict ID)
   - All 8 valid corpus samples decompress without error
   - All 3 invalid corpus samples raise ZstdError
   - Round-trip check for synthetic valid samples
   - Prototype README with approach and security notes

2. **parser-requirements.yaml** in `.local/spec-cache/zst/rfc8878/normalized/`
   OR explicit G-NORM-004 waiver in gap register

3. **Gate 4 tests:** `tests/skills/test_zst_gate4_prototype.py`
   - Prototype exists and imports correctly
   - All valid samples decompress
   - All invalid samples raise expected errors
   - No src/ mutations

4. **Gate 4 report:** `reports/testing/r18-zst-gate4-prototype-validation.md`

5. **Gate 5 scoping decision:**
   - For codec format: is neutral model N/A, minimal, or defined?
   - If N/A: document justification in Gate 5 waiver
   - If defined: outline neutral model schema (compression metadata)

### Hard Invariants
- No src/python/zst/ or src/net/zst/ created
- implementation_authorized remains false
- generated_requirements_authorized remains false
- Gate 5 approval requires separate human prompt

## Suggested Sprint ID

FORMAT-FACTORY-R18-ZST-GATE4-PROTOTYPE-AND-GATE5-READINESS-SWARM-001

## Pre-conditions for Sprint Launch

- Gate 4 parser-notes.md: DONE (R17)
- Execution prompt from Babar Raza authorizing prototype creation: REQUIRED
- WIP check: ZST in Gate 4 slot; no >2 formats in Gates 4-6

## Notes

Gate 4 prototype uses prototypes/ not src/. This is planning/validation code only.
Gate 5 (neutral model) for codec format may resolve as N/A with documented justification.
Commercial product decision for ZST (Aspose duplication, standalone value) must be
addressed by human before Gate 5 proceeds.

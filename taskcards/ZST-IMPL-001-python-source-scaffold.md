# ZST-IMPL-001 — ZST Python Source Scaffold

**Created:** 2026-05-16 (R19)
**Status:** not_started
**Priority:** HIGH — ZST acquisition gates 1-7 complete
**Blocker:** Requires explicit implementation sprint prompt from Babar Raza

## Trigger Condition

This taskcard activates when Babar Raza issues a ZST implementation sprint prompt
(e.g., FORMAT-FACTORY-ZST-IMPL-001 or similar).

## Scope

Create `src/python/zst/` with:
- `__init__.py`
- `probe.py` — thin wrapper over python-zstandard + frame_header.py
- `compress.py` — compress bytes/files
- `decompress.py` — decompress with max_window_size bomb guard

## Prerequisites

- [x] ZST Gate 1: passed
- [x] ZST Gate 2: passed
- [x] ZST Gate 3: passed (corpus)
- [x] ZST Gate 4: passed (prototype in prototypes/by-format/zst/)
- [x] ZST Gate 5: waived_not_applicable
- [x] ZST Gate 6: passed (oracle)
- [x] ZST Gate 7: passed (security/fuzz)
- [ ] implementation_authorized: false → must be set true in impl sprint
- [ ] generated_requirements_authorized: false → Gate 8 required

## Key References

- Prototype: `prototypes/by-format/zst/`
  - frame_header.py (RFC 8878 parser)
  - zst_probe.py (decompressor + metadata)
  - validate_corpus.py
- Oracle tests: `tests/skills/test_zst_gate6_oracle.py`
- Security tests: `tests/skills/test_zst_gate7_security_fuzz.py`
- Oracle: python-zstandard (BSD-3-Clause, zstandard 0.25.0)
- Bomb guard: max_window_size=2**31 on all decompress calls

## Notes

ZST is a pure codec — the Python wrapper is minimal. Prototype already exists.
This is a promotion from prototypes/ to src/python/zst/.
No DOM, no schema mapping, no generated requirements needed (gate 5 was N/A).

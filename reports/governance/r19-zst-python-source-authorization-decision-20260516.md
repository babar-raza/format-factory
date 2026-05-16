# R19 ZST Python Source Authorization Decision
Sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
Date: 2026-05-16
Gate: 7 — ZST Python Source Authorization Decision

## Preconditions Confirmed

All four prerequisite gates now PASS:
- Gate 4: PASSED (prototype complete, delegated R19)
- Gate 5: WAIVED N/A (G-NORM-004, no DOM)
- Gate 6: PASSED (oracle, 27/27 tests)
- Gate 7: PASSED (security/fuzz, 27/27 tests)

## Decision Options Evaluated

### Option A: AUTHORIZE_MINIMAL_PYTHON_CODEC_WRAPPER_NOW

**Arguments for:**
- ZST is a pure codec — the Python wrapper is minimal (compress/decompress/probe)
- python-zstandard is BSD-3-Clause, already installed and tested
- frame_header.py prototype already exists in prototypes/by-format/zst/
- No DOM complexity; no ambiguous schema mapping needed

**Arguments against:**
- `implementation_authorized: false` was explicitly set and preserved through Gates 4 and 5
- Gate 4 approval report explicitly states: "implementation_authorized: false. generated_requirements_authorized: false."
- Gates 8-11 (generated requirements, Gate 8 is neutral model) are not yet executed
- Per project gate model: Python source creation requires Gate 8+ authorization
- No execution prompt from Babar Raza authorizing src/python/zst/ creation
- AGENTS.md: no src/python/ or src/net/ mutations without explicit implementation authorization

**Verdict: REJECTED — prerequisite gates for implementation not complete**

### Option B: DEFER_PYTHON_SOURCE_UNTIL_IMPLEMENTATION_SPRINT

**Arguments for:**
- All acquisition gates (1-7) now COMPLETE for ZST
- Implementation authorization requires a dedicated implementation sprint prompt
- Consistent with how FODS/FODT were handled: acquisition gates first, then separate implementation prompt
- Avoids scope creep in R19 (acquisition train sprint, not implementation sprint)
- Gate 8 (generated requirements), Gate 9 (prototype hardening), Gate 10 (CLI integration) not yet executed
- src/python/zst/ creation belongs to a future FORMAT-FACTORY-ZST-IMPLEMENTATION sprint

**Verdict: ACCEPTED**

### Option C: BLOCK_ZST_SOURCE_BECAUSE_ASPOSE_ALREADY_SUPPORTS

**Arguments for:**
- aspose_supported=true: ZstandardArchive + TarArchive.SaveZstandard
- Aspose already handles ZST in .NET track

**Arguments against:**
- Python FOSS track (DEC-031) exists independent of Aspose .NET capability
- Project goals include Python OSS path for all acquired formats
- aspose_supported=true means integration opportunity, not BLOCK
- ZST score 8.95/10 is ACQUISITION_READY — blocking would contradict the score
- Aspose .NET coverage does not preclude Python FOSS wrapper

**Verdict: REJECTED — Aspose coverage is not a blocker for Python FOSS track**

## Decision

**DEFER_PYTHON_SOURCE_UNTIL_IMPLEMENTATION_SPRINT**

Rationale:
1. All ZST acquisition gates (1-7) are now COMPLETE — the acquisition phase is done
2. Python source authorization requires an implementation sprint with explicit Babar Raza prompt
3. `implementation_authorized: false` must remain until a future sprint sets it true
4. No generated_requirements_authorized — Gate 8 not yet executed for ZST
5. R19 sprint scope is acquisition, not implementation; creating src/python/zst/ would be out-of-scope

## ZST Acquisition Summary

| Gate | Status | Method |
|------|--------|--------|
| Gate 1 | PASSED | Delegated (R13B) |
| Gate 2 | PASSED | Delegated (R14) |
| Gate 3 | PASSED | Corpus acquired (R16) |
| Gate 4 | PASSED | Delegated (R19) |
| Gate 5 | WAIVED N/A | G-NORM-004, no DOM |
| Gate 6 | PASSED | Delegated (R19) |
| Gate 7 | PASSED | Delegated (R19) |
| Gate 8+ | NOT_STARTED | Requires implementation sprint |

## Next Steps for ZST

1. Create a ZST implementation sprint prompt (FORMAT-FACTORY-ZST-IMPL-001 or similar)
2. That sprint must: authorize generated requirements, execute neutral model (Gate 8), create src/python/zst/
3. implementation_authorized must be flipped in that sprint, not before
4. Commercial track (.NET/Aspose) evaluated separately

## Registry State After This Gate

- implementation_authorized: false (unchanged — no authorization granted)
- generated_requirements_authorized: false (unchanged)
- All gates 1-7: PASSED or WAIVED
- ZST acquisition phase: COMPLETE

GATE_7_ZST_PYTHON_SOURCE_DECISION: DEFER_PYTHON_SOURCE_UNTIL_IMPLEMENTATION_SPRINT

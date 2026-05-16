# R18 Gate 3 (Sprint): ZST Gate 4 Prototype Independent Verification
Sprint: FORMAT-FACTORY-R18-QUARTER-MILE-ZST-GATE4-GATE5-AND-MULTI-FORMAT-GATE1-SWARM-001
Date: 2026-05-16
Gate: 3 (sprint gate) — ZST Gate 4 Prototype IV (DEC-034)

## IV Method

DEC-034 independent verification. Authoring lane produced the prototype files and
validation report. IV lane verifies independently, treating artifacts as if first
encountered, using only what is committed or untracked in the live repository.

## Check 1: Prototype directory exists

Expected: prototypes/by-format/zst/ exists with the 4 required files
Result: PASS
Verified:
- prototypes/by-format/zst/README.md: EXISTS, non-empty
- prototypes/by-format/zst/frame_header.py: EXISTS, non-empty
- prototypes/by-format/zst/zst_probe.py: EXISTS, non-empty
- prototypes/by-format/zst/validate_corpus.py: EXISTS, non-empty

## Check 2: README.md contains non-production boundary statement

Expected: "PROTOTYPE" and "NON-PRODUCTION" visible in README.md
Result: PASS
From README.md:
> "STATUS: PROTOTYPE — NON-PRODUCTION"
> "NOT for use in src/python/ or src/net/"
> "Gate 4 planning/validation artifact only."

## Check 3: frame_header.py implements RFC 8878 correctly

Expected: ZSTD_MAGIC = 0x28 0xB5 0x2F 0xFD; skippable range correct
Result: PASS
Verified from source:
- ZSTD_MAGIC = b"\x28\xb5\x2f\xfd" — matches RFC 8878 §3.1.1 ✓
- SKIPPABLE_MAGIC_MIN = 0x184D2A50 — matches RFC 8878 §3.1.2 ✓
- SKIPPABLE_MAGIC_MAX = 0x184D2A5F — matches RFC 8878 §3.1.2 ✓
- FHD byte parsing: FCS_flag bits 7:6, Single_Segment bit 5, Content_Checksum bit 2, DID bits 1:0 ✓
- Content_Size encoding per FCS_flag value (0, 1, 2, 4, 8 bytes) ✓
- Window_Descriptor parsed when Single_Segment=0 ✓

## Check 4: Prototype does not contain implementation-level source code

Expected: No Tier 4-6 implementation in prototypes/; no src/ mutations; no API contracts
Result: PASS
Verified:
- frame_header.py: pure parser (header reading only, no compression logic)
- zst_probe.py: decompressor wrapper using python-zstandard (planning validation only)
- validate_corpus.py: test harness (not a production test file in src/)
- None of the files define classes for use in production delivery code
- No C# code. No .NET project files. No Python __init__ for package installation.

## Check 5: validate_corpus.py 15/15 PASS

Expected: 8 valid samples PASS + 3 invalid rejected + 4 round-trips PASS
Result: PASS
Command: python prototypes/by-format/zst/validate_corpus.py
Output confirmed: 15 PASS, 0 FAIL

Valid samples (8/8): block-128k.zst, dict-compressed.zst, empty-block.zst,
minimal-synthetic.zst, random-data.zst, rle-first-block.zst, text-compressed.zst,
zeroSeq_2B.zst — all decompressed without error.

Invalid samples (3/3): off0.bin.zst, truncated_huff_state.zst, zeroSeq_extraneous.zst
— all raised ZstdError (correctly rejected).

Round-trips (4/4): payload[0]-payload[3] all survived compress → decompress → compare.

## Check 6: Gate 4 tests PASS

Expected: tests/skills/test_zst_gate4_prototype.py — 38 PASS, 0 FAIL
Result: PASS
Test file exists. 38/38 tests PASS covering:
- Prototype files present + non-empty
- README non-production boundary
- frame_header magic constants (RFC 8878)
- Frame type detection (ZSTD, skippable, unknown)
- FHD byte decoding (Single_Segment, Content_Size)
- All 11 corpus files parse without exception
- zst_probe.py probe() dict structure and behavior
- validate_corpus.py valid/invalid/round-trip coverage
- Hard invariants (no src/*/zst, no gen-req/zst, registry state)

## Check 7: No src/ mutations

Expected: src/python/zst/ and src/net/zst/ do not exist
Result: PASS
Verified:
- src/python/: contains _readme.md, fods/, fodt/ only — no zst ✓
- src/net/: contains _readme.md, fods/, fodt/ only — no zst ✓
- No src/python/zst/ directory
- No src/net/zst/ directory

## Check 8: No generated-requirements/zst

Expected: generated-requirements/zst/ does not exist
Result: PASS
generated-requirements/ contains: fods/, fodt/ only. No zst directory.

## Check 9: implementation_authorized remains false

Expected: registry gate_4 notes confirm implementation_authorized: false
Result: PASS
Registry gate_4.notes:
> "implementation_authorized: false. generated_requirements_authorized: false."
> "Prototype + approval deferred to R18+."

## Check 10: Prototype gates prior work (Gate 2, Gate 3) rather than replacing it

Expected: prototype references corpus; corpus SHA-256 hashes validate
Result: PASS
validate_corpus.py references VALID_DIR and INVALID_DIR pointing to
samples/by-format/zst/{valid,invalid}/ — the Gate 3 corpus.
SHA-256 hashes verified via test_zst_gate3b_sample_corpus.py (57/57 PASS, unchanged).
The prototype builds on Gate 3 artifacts; it does not replace or re-derive them.

## IV Summary

| Check | Result |
|-------|--------|
| 1. Prototype directory and 4 files exist | PASS |
| 2. README non-production boundary | PASS |
| 3. frame_header.py RFC 8878 compliance | PASS |
| 4. No implementation-level source code | PASS |
| 5. validate_corpus.py 15/15 PASS | PASS |
| 6. Gate 4 tests 38/38 PASS | PASS |
| 7. No src/ mutations | PASS |
| 8. No generated-requirements/zst | PASS |
| 9. implementation_authorized remains false | PASS |
| 10. Prototype gates prior work (Gate 2+3) | PASS |

**IV RESULT: 10/10 PASS**

GATE_3_ZST_GATE4_PROTOTYPE_IV: PASS

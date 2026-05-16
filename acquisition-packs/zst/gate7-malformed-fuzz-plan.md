---
artifact_id: zst-gate7-malformed-fuzz-plan-v1
format_id: zst
gate: 7
sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
date: "2026-05-16"
---

# ZST Gate 7 Malformed/Fuzz Plan

## Fuzz Strategy

Deterministic malformed variant generation. No random fuzz (no fuzz harness required
for this gate). All samples are project-owned, generated under project license.

## Provenance

All generated samples in samples/by-format/zst/invalid/generated/ are:
- Created by this project (format-factory)
- Not derived from any external source
- License: project-internal (not distributed)
- Provenance: synthetic, deterministic, R19

## Generated Malformed Variants

| File | Type | Expected Behavior |
|------|------|-------------------|
| wrong-magic.zst | Invalid magic (0xFFFFFFFF) | is_unknown=True; ZstdError |
| truncated-header-2b.zst | Truncated at 2 bytes | is_unknown (too short); ZstdError |
| magic-only-no-fhd.zst | Valid magic, no FHD | parse_error; ZstdError |
| corrupted-block-data.zst | Valid header, corrupted body | Header parses; ZstdError on decompress |
| claimed-large-truncated.zst | Large content_size, tiny body | Header parses; ZstdError (unexpected EOF) |

## Fuzz Test Requirements

1. All 5 generated samples must not crash the interpreter
2. All 5 must produce either:
   a. is_unknown=True from frame_header (structural rejection), OR
   b. ZstdError from python-zstandard (decompression rejection), OR
   c. Successful parse with documented behavior (e.g., corrupted-block rejected at decompress)
3. No segfault, no memory corruption (Python-level safety guaranteed)
4. Tests: tests/skills/test_zst_gate7_security_fuzz.py

## What This Fuzz Does NOT Cover (Out of Scope for This Gate)

- Full mutation fuzzing (libFuzzer, AFL) — not needed for prototype validation
- Concurrency/thread-safety testing — prototype is single-threaded
- JVM/CLR decompressor behavior — .NET track not yet implemented
- Real-world adversarial sample collection — license/provenance risk

## Streaming Strategy

For production implementation (Gate 8+):
- Always use stream_reader, not decompress() for untrusted input
- Process in chunks of ≤ 64 KB
- Enforce max_window_size on all decompressor instances
- Reject files > configured size limit before decompression attempt

ZST_GATE7_MALFORMED_FUZZ_PLAN: DOCUMENTED

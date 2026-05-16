# ZST Prototype — Zstandard Frame Validator

**Status:** Gate 4 Prototype — NON-PRODUCTION
**Gate:** 4
**Sprint:** FORMAT-FACTORY-R18-QUARTER-MILE-ZST-GATE4-GATE5-AND-MULTI-FORMAT-GATE1-SWARM-001
**Date:** 2026-05-16

## Purpose

This prototype validates the ZST parsing strategy defined in `acquisition-packs/zst/parser-notes.md`.
It is NOT production code. It is NOT released. It does NOT belong in `src/`.

This prototype:
- Reads ZST frame headers to extract metadata (magic, FHD byte, content size, checksum flag, dict ID)
- Uses python-zstandard as decompressor oracle
- Validates all corpus samples from Gate 3
- Demonstrates round-trip correctness for synthetic payloads

## Boundary Statement

This code lives in `prototypes/by-format/zst/`, not `src/`.
It is a planning/validation artifact only.

- `implementation_authorized: false`
- `generated_requirements_authorized: false`
- Gate 4 full pass requires human review

## Files

| File | Purpose |
|------|---------|
| `frame_header.py` | RFC 8878 frame header reader (magic, FHD byte, metadata extraction) |
| `zst_probe.py` | High-level probe: decompress + metadata report |
| `validate_corpus.py` | Validates all 8 valid + 3 invalid corpus samples |
| `README.md` | This file |

## Dependencies

- `zstandard` (python-zstandard, BSD-3-Clause) — must be installed
- Python 3.13+

## Security Notes

### Decompression Bomb Risk
Zstandard frames can have very high compression ratios. A malicious frame could expand
to gigabytes from a small input. Production code MUST limit output size.
This prototype does NOT implement output size limits — do not run on untrusted input.
Mitigation in production: set `max_length` parameter in `decompress()` or read via `stream_reader()`
with a byte limit.

### Window Size
RFC 8878 defines Window_Descriptor for frames without Content_Size.
The window size determines how much memory the decompressor needs.
RFC 9659 limits window size to 8 MB in HTTP contexts.
This prototype does not enforce window limits — production code should.

### Streaming Validation
Valid frames without Content_Size require `stream_reader()` — NOT `decompress()`.
`decompress()` raises `ZstdError: could not determine content size in frame header`
for frames that omit the Content_Size field. See parser-notes.md for details.

### Invalid Corpus Handling
Invalid frames MUST raise `ZstdError`. This prototype verifies that behavior.
In production, error messages should be sanitized before user display.

## Usage (for development/validation only)

```
cd prototypes/by-format/zst/
python validate_corpus.py
```

# R24 QOI Gate 3 Sample Corpus and Gate 4 Planning Report
# Sprint: FORMAT-FACTORY-R24-PARALLEL-CLOSURE-REPAIR-FORWARD-TRAIN-AND-AI-PLATFORM-PLAN-001
# Date: 2026-05-18
# Gate: 3 — Sample Corpus Acquisition
# Lane: E (Non-ODF Imaging Formats)

---

## Gate 1-2 Verification

Source authority: `acquisition-packs/qoi/pack.yaml`

- **Gate 1:** status=passed, score=8.1/10 (Accept band), approved_date=2026-05-17
  - Legal: MIT license on reference impl, format is open, no patent claims — 30/30
  - Spec: single-page spec at qoi.phoboslab.org, complete and concise — 13/20
  - Parseable structure: extremely simple binary format, <200 lines to implement — 15/15
  - Aspose support: NOT_SUPPORTED — positive differentiation for commercial track
  - `awaiting_human_iv: true` (DEC-034 independent verification pending)
- **Gate 2:** status=passed, approved_date=2026-05-17
  - Spec source: https://qoi.phoboslab.org/ (no download required)
  - Patent search not required (MIT license, author explicitly states no patents)
  - `awaiting_human_iv: true`

Both gates confirmed. Proceeding to Gate 3.

---

## Sample Generation Method

Generation approach: **deterministic synthetic Python struct**

QOI is a binary format. No ZIP container, no XML, no third-party libraries needed.
The QOI spec is simple enough to implement directly:
- 14-byte header: magic `qoif` (4) + width (4, big-endian u32) + height (4, big-endian u32)
  + channels (1) + colorspace (1)
- Pixel data: variable-length chunks using QOI opcodes
- 8-byte end marker: 7x 0x00 + 0x01

Encoding used in corpus generation:
- `QOI_OP_RGBA (0xFF)`: 5-byte literal RGBA pixel
- `QOI_OP_RUN (0xC0 | run-1)`: run-length encoding for repeated pixels

Generation script: `.local/gen_samples.py` (ephemeral, gitignored)
Spec reference: https://qoi.phoboslab.org/

---

## Corpus Summary

Location: `samples/by-format/qoi/`
Manifest: `samples/by-format/qoi/_corpus-manifest.yaml`
Provenance: `samples/by-format/qoi/_provenance.yaml`

### Valid samples (3)

| File | Size | Category | SHA-256 (first 16) |
|------|------|----------|-------------------|
| valid/1x1-red.qoi | 27 bytes | minimal-valid | 455bc219da1db506 |
| valid/2x2-black.qoi | 23 bytes | run-length-encoding | 421d23fd18d9d14d |
| valid/4x1-gradient.qoi | 38 bytes | multi-pixel-gradient | 2dcc40d3b5e3fdff |

### Invalid samples (1)

| File | Size | Category | Error Type |
|------|------|----------|-----------|
| invalid/wrong-magic.qoi | 14 bytes | invalid-magic | InvalidMagic |

Categories covered: minimal-valid, run-length-encoding, multi-pixel-gradient, invalid-magic

### QOI opcode coverage
- `QOI_OP_RGBA (0xFF)`: literal RGBA pixel — all valid samples
- `QOI_OP_RUN (0xC0 | n)`: run-length repeat — 2x2-black.qoi

---

## Provenance Summary

All 4 files are project-owned synthetic. No upstream copyright. No license obligations.
Pixel data is programmatic (not derived from any real image).
Generation is fully deterministic using Python 3.13 stdlib (struct, bytes) only.

---

## Gate 3 Decision: PASS

Gate 3 requirements met:
- [x] At least 3 valid sample files covering distinct structural categories
- [x] At least 1 invalid/malformed sample for magic-byte validation testing
- [x] SHA-256 hashes recorded in corpus manifest
- [x] Provenance documented for all files
- [x] License: project-owned-synthetic (no third-party obligations)
- [x] QOI spec version confirmed: 1.0

Gate 3 status: **PASS (delegated_agent_r24)**
awaiting_human_iv: true (per DEC-034)
commercial_product_ready: false

---

## Gate 4 Planning Notes

Gate 4 objective: Minimal QOI parser/decoder implementation.

### Format overview (from spec)
- Magic: bytes 0-3 = `qoif`
- Width: bytes 4-7 (big-endian u32)
- Height: bytes 8-11 (big-endian u32)
- Channels: byte 12 (3=RGB, 4=RGBA)
- Colorspace: byte 13 (0=sRGB+linear alpha, 1=all linear)
- Pixel data: variable-length chunks
- End marker: bytes [-8:] = `[0x00]*7 + [0x01]`

### Chunk opcodes
| Opcode | Bits | Description |
|--------|------|-------------|
| QOI_OP_RGB | 0xFE + 3 bytes | literal RGB |
| QOI_OP_RGBA | 0xFF + 4 bytes | literal RGBA |
| QOI_OP_INDEX | 00xxxxxx | index into 64-slot running array |
| QOI_OP_DIFF | 01xxxxxx | small RGB delta (-2..+1 per channel) |
| QOI_OP_LUMA | 10xxxxxx + 1 byte | larger green-lead delta |
| QOI_OP_RUN | 11xxxxxx | run-length (1..62 repeat) |

### Parsing strategy
1. Validate magic bytes: `data[0:4] == b'qoif'`
2. Parse header with `struct.unpack('>IIBB', data[4:14])`
3. Iterate pixel chunks from offset 14
4. Dispatch on first byte to determine opcode
5. Maintain running color array (64 slots, indexed by hash)
6. Maintain previous pixel state for DIFF/LUMA ops
7. Stop at end marker (8 bytes)
8. Return pixel array as list of (R, G, B, A) tuples or bytes

### Security considerations
- No external data sources; pure binary parsing
- Integer overflow: width*height can be large; guard with max_pixels limit
- Truncated file: check remaining bytes before reading chunk data
- End marker validation: verify file ends correctly

### Oracle approach
- Programmatic pixel oracle: generate known pixels, encode via `make_qoi()`, decode and compare
- Corpus files as regression oracle: 1x1-red.qoi expected pixel = [(255,0,0,255)]
- 2x2-black.qoi expected pixels = [(0,0,0,255)]*4 (tests run-length decode)
- 4x1-gradient.qoi expected pixels = [(0,0,0,255),(85,85,85,255),(170,170,170,255),(255,255,255,255)]

### No Aspose dependency
QOI is NOT_SUPPORTED by Aspose. This is the first pure FOSS imaging format.
Gate 4 implementation must be entirely from-scratch Python (no commercial library).
Python `qoi` package (MIT, PyPI) exists as reference if needed, but implementation
from spec is also viable given spec simplicity.

Gate 4 implementation planned for R24+ after human IV of Gates 1-3.

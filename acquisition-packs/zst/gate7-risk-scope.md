---
artifact_id: zst-gate7-risk-scope-v1
format_id: zst
gate: 7
sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
date: "2026-05-16"
---

# ZST Gate 7 Risk Scope

## Risk Categories for ZST

### 1. Decompression Bomb

**Risk:** A malicious .zst file claims a very large content_size in the frame header
but contains a small compressed body that expands to a huge payload.

**Mitigation:**
- python-zstandard: max_window_size parameter (default 2^31 = 2 GB)
- stream_reader: processes output incrementally, no full decompression into memory
- Production implementations: always enforce max_window_size; use streaming

**RFC 8878 Reference:** Section 3.1.1 Window_Descriptor defines maximum window size.
Maximum allowed: 2^(10 + WindowLog) where WindowLog ≤ 31.

### 2. Truncated Frame / Header Parsing

**Risk:** A truncated or malformed ZST file causes parser to read out-of-bounds.

**Mitigation:**
- frame_header.py: bounds-checked at every offset step
- parse_frame_header returns is_unknown=True with parse_error set
- Never raises an uncaught exception (returns structured error)

**Tested:** truncated_huff_state.zst, truncated-header-2b.zst in corpus

### 3. Corrupted Block Data

**Risk:** Valid frame header but corrupted compressed block data causes decompressor
to behave unexpectedly.

**Mitigation:**
- python-zstandard raises ZstdError (controlled exception)
- Oracle tests verify this behavior
- No segfault or memory corruption in Python-level zstandard

**Tested:** corrupted-block-data.zst in generated corpus

### 4. Wrong Magic Bytes

**Risk:** Non-ZST file is presented as .zst, causing misidentification.

**Mitigation:**
- frame_header.py: magic byte check as first operation
- is_unknown=True set for unrecognized magic
- Decompressor also rejects non-ZST headers

**Tested:** off0.bin.zst (real corpus), wrong-magic.zst (generated corpus)

### 5. Extraneous Data After Frame

**Risk:** A valid frame followed by trailing bytes (e.g., multiple concatenated frames
or garbage after the compressed payload).

**Mitigation:**
- python-zstandard: stream_reader reads until end-of-stream; handles concatenated frames
- Gate 4 prototype: parses first frame only (header-level parsing)
- Documented as a multi-frame use case in oracle comparison report

**Tested:** zeroSeq_extraneous.zst in corpus

### 6. Skippable Frames

**Risk:** Skippable frames (magic 0x184D2A50-0x184D2A5F) could cause confusion if
misidentified as regular frames.

**Mitigation:**
- frame_header.py: detects skippable frames explicitly (is_skippable_frame=True)
- python-zstandard: handles skippable frames transparently in stream mode

### 7. Archive/Container Risks (.tar.zst)

**Risk:** After decompression of a .tar.zst file, the tar archive could contain:
- Path traversal attacks (../../etc/passwd)
- Symlink attacks
- Zip-slip equivalent

**Mitigation:**
- ZST oracle: decompresses bytes only, does NOT extract tar
- Production implementations: must sanitize tar paths post-decompression
- This project: no tar extraction in prototype or oracle

**Status:** Documented. No tar extraction implemented.

### 8. Dictionary ID Mismatch

**Risk:** Frame references a dictionary by ID that is not loaded; decompressor
behaves differently from expected.

**Mitigation:**
- python-zstandard: raises ZstdError for missing dictionary
- frame_header.py: reads dict_id field from frame header
- dict-compressed.zst behavior: documented in oracle comparison report

## Risk Classification Summary

| Risk | Severity | Mitigation Status |
|------|----------|------------------|
| Decompression bomb | HIGH | MITIGATED (max_window_size) |
| Truncated frame | MEDIUM | MITIGATED (bounds checking) |
| Corrupted block | MEDIUM | MITIGATED (ZstdError) |
| Wrong magic | LOW | MITIGATED (magic check) |
| Extraneous data | LOW | DOCUMENTED |
| Skippable frames | LOW | MITIGATED (explicit detection) |
| .tar.zst container | MEDIUM | DOCUMENTED (no extraction) |
| Dictionary mismatch | LOW | MITIGATED (ZstdError) |

ZST_GATE7_RISK_SCOPE: DOCUMENTED

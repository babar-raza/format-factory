---
artifact_id: zst-parser-notes-v1
artifact_type: acquisition-pack
path: acquisition-packs/zst/parser-notes.md
format_id: zst
product_family: compression
visibility: evidence-only
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-16"
reusable: true
refresh_policy:
  trigger: source-changed
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 4 planning artifact. parser-notes.md created R17 (2026-05-16). Gate 4 planning_complete. Full Gate 4 pass requires prototype + human review (R18+). implementation_authorized: false."
---

# Parser Notes — Zstandard Compressed File (.zst)

**Format ID:** `zst`
**Gate:** 4
**Status:** planning_complete — parser-notes.md only; prototype NOT yet created

**Gate 1 approved by:** Babar Raza (delegated, R13B sprint, 2026-05-15)
**Gate 2 status:** PASSED — delegated (R14 sprint, 2026-05-15)
**Gate 3 status:** PASSED — delegated (R16 sprint, Babar Raza instruction, 2026-05-15)
**Gate 4 status:** planning_complete — parser notes created R17; prototype required for Gate 4 pass (R18+)

**Gate 4 approved:** NO — prototype + human review required
**implementation_authorized:** false
**generated_requirements_authorized:** false

---

## Format Summary

Zstandard (.zst) is a lossless compression codec format defined in RFC 8878.
It is NOT a container or document format — it is a byte-stream transform that compresses
arbitrary binary data into a stream of Zstandard frames.

Key properties:
- Extension: `.zst`
- MIME type: `application/zstd` (IANA-registered per RFC 8878 §4)
- Content-Encoding token: `zstd`
- Frame-based structure: one or more frames in sequence
- No built-in filename, metadata, or directory structure
- Optional content size in frame header
- Optional content checksum (xxHash-64)
- Optional dictionary compression
- Skippable frames for user-defined metadata

---

## Spec Basis

### Primary: RFC 8878

- Title: Zstandard Compression and the 'application/zstd' Media Type
- Published: 2021-02-01 (IETF Informational)
- Obsoletes: RFC 8478
- Sections relevant to parser:
  - §3: Zstandard Compressed Data Format
  - §3.1: Frames
  - §3.1.1: Zstandard Frames (magic number 0xFD2FB528 LE)
  - §3.1.2: Skippable Frames (magic range 0x184D2A50–0x184D2A5F LE)
  - §3.1.1.1: Frame Header Descriptor (FHD byte)
  - §3.1.1.2: Frame Header fields (Window_Descriptor, DID, Content_Size)
  - §3.1.1.3: Data Blocks (header + payload)
  - §3.1.1.4: Content Checksum (XXH64, optional)
  - §3.2: Dictionary Format
  - §3.3: Block Types (Raw_Block, RLE_Block, Compressed_Block, Reserved)
  - §3.3.2: Compressed Blocks (literals, sequences, FSE tables, Huffman tables)
- Cached: .local/spec-cache/zst/ (committed in R14)

### RFC 9659 Update Relationship

- Title: Window Sizing for Zstandard Content Encoding
- Published: 2024-09-01 (IETF Informational)
- Scope: Limited to HTTP content-encoding context only
- Impact: Restricts maximum window size for HTTP use cases
- Parser relevance: NOT relevant for file-level parsing
- Impact classification: HTTP-only; does not change frame format or binary layout

---

## Sample Corpus Summary (Gate 3)

8 valid samples, 3 invalid samples. All SHA-256 verified (Gate 3 IV PASS).

### Valid Samples

| File | Description | Source | Key Property |
|------|-------------|--------|-------------|
| block-128k.zst | 128KB block | facebook/zstd golden-decompression (BSD-3) | No Content_Size in header |
| dict-compressed.zst | Dictionary-compressed | python-zstandard self-generated | Dictionary ID in header |
| empty-block.zst | Empty content | facebook/zstd golden-decompression (BSD-3) | Zero-length content |
| minimal-synthetic.zst | Minimal frame | Self-generated | Smallest valid frame |
| random-data.zst | Random bytes compressed | Self-generated | Incompressible content |
| rle-first-block.zst | RLE first block | facebook/zstd golden-decompression (BSD-3) | RLE block type |
| text-compressed.zst | Plain text | Self-generated | Typical use case |
| zeroSeq_2B.zst | Zero sequences, 2-byte window | facebook/zstd golden-decompression (BSD-3) | No Content_Size; decodecorpus-style |

### Invalid Samples

| File | Description | Expected Behavior |
|------|-------------|-------------------|
| off0.bin.zst | Corrupt frame (offset 0) | ZstdError on decompression |
| truncated_huff_state.zst | Truncated Huffman state | ZstdError on decompression |
| zeroSeq_extraneous.zst | Extraneous bytes after frame | ZstdError on decompression |

---

## Parsing Strategy Options

### Option A: Pure Frame Parser
Parse RFC 8878 frame format directly in Python:
- Read magic number bytes (4 bytes LE)
- Parse FHD byte (flags for Content_Size, Content_Checksum, Dictionary ID, Reserved)
- Read Window_Descriptor if FCS==0
- Read Frame Content Size (0, 1, 2, 4, or 8 bytes depending on FCS flags)
- Read blocks until Last_Block=1
- Verify optional xxHash-64 checksum

Pros: Full control, no library dependency, complete RFC conformance
Cons: High complexity (block codec = FSE entropy + Huffman; full decompression requires implementing both)
Verdict: Block-level validation feasible in Gate 4; full decompression NOT scope for planning

### Option B: zstandard Library Wrapper (Recommended for Gate 4)
Use python-zstandard (v0.25.0, BSD-3-Clause, CFFI-based):
- ZstdDecompressor.stream_reader() for content-without-size frames
- ZstdDecompressor.decompress() for frames with Content_Size
- Frame introspection via get_frame_parameters()
- Error detection via ZstdError

Key API note from corpus testing: frames without Content_Size header MUST use stream_reader()
not decompress() — decompress() raises "could not determine content size in frame header".

Pros: Working, tested, already in project environment
Cons: Library dependency; hides frame-level detail
Verdict: Appropriate for Gate 4 prototype; pure parser can be added in Gate 5+

### Option C: CLI Oracle (zstd binary)
Use zstd CLI as decompression oracle, parsing stdout/stderr.
Cons: System dependency; brittle; not suitable for Python library output
Verdict: Useful for ad-hoc exploration; NOT recommended for prototype

### Option D: Hybrid Phased Approach (Recommended Architecture)
Phase 1 — Gate 4 prototype:
  - Frame header reader: magic detection, FHD parsing, Content_Size read
  - Decompression: zstandard library wrapper
  - Error classification: valid/invalid/truncated/corrupt
Phase 2 — Gate 5+ requirements:
  - Pure block-level parser (FSE/Huffman tables)
  - Streaming decompression without library
Phase 3 — Commercial integration:
  - Only if commercial use case justifies pure implementation over library wrapping

---

## Recommended Architecture

### Python OSS Track (Tier 0-4)

The FOSS Python parser should:
1. Detect valid ZST frames by magic number (bytes 0-3 == b'\x28\xb5\x2f\xfd' LE)
2. Detect skippable frames by magic range (0x184D2A50–0x184D2A5F LE)
3. Use python-zstandard for decompression oracle at Gate 4
4. Read frame header fields for metadata extraction (Content_Size, dictionary ID, checksum flag)
5. Classify corpus: valid/invalid/skippable
6. Report compression ratio, original size (when available), dictionary ID

Avoid claiming full commercial product readiness — ZST is a codec with no DOM; commercial
value requires use in document container context (e.g., .tar.zst, .jsonl.zst) or as a
compression step within another format's pipeline.

### .NET Commercial Track (Tier 0-6)

Note: .NET commercial implementation is deferred and requires separate authorization.
ZST as standalone has limited commercial value — integration with other formats (e.g., as
a container layer) is likely more commercially relevant. This must be addressed at Gate 5+
with generated requirements and human product sign-off.

---

## Frame-Level Concepts

### Magic Number
- Zstandard Frame: 0xFD2FB528 (LE byte order: 0x28, 0xB5, 0x2F, 0xFD)
- Skippable Frame: 0x184D2A50 to 0x184D2A5F

### Frame Header Descriptor (FHD) Byte
Bits [7:6] — Frame_Content_Size_flag (FCS):
  - 00: FCS absent (Content_Size unknown; must use streaming decompression)
  - 01: FCS is 1 byte
  - 10: FCS is 2 bytes
  - 11: FCS is 4 or 8 bytes
Bit [5] — Single_Segment_Flag
Bit [3] — Content_Checksum_Flag (xxHash-64 present at end of frame)
Bit [1:0] — Dictionary_ID_Flag

### Content Size Optionality
Content_Size is OPTIONAL per RFC 8878. Many frames omit it.
This was the key corpus discovery: block-128k.zst, empty-block.zst, and zeroSeq_2B.zst
all omit Content_Size, causing decompress() failures. stream_reader() must be used.

### Blocks
Each block has a 3-byte header:
  - Bits [2:1] — Block_Type: Raw_Block(0), RLE_Block(1), Compressed_Block(2), Reserved(3)
  - Bit [0] — Last_Block flag
  - Bits [23:3] — Block_Size

### Dictionary Handling
Dictionary_ID in frame header specifies which pre-agreed dictionary was used.
dictionary-compressed.zst uses dictionary ID in frame header.
For corpus validation: library-based decompression handles dictionary lookup automatically
when the dictionary is provided to ZstdDecompressor(dict_data=...).

### Skippable Frames
Range 0x184D2A50–0x184D2A5F LE. Contain user-defined data.
Must be skipped by any conforming decompressor, not treated as an error.
Not present in current corpus but must be handled in Gate 4 prototype.

---

## Validation Plan

### Valid Sample Tests
For each valid sample:
1. Confirm magic number (bytes 0-3 match 0x28 0xB5 0x2F 0xFD)
2. Decompress using stream_reader() (handles both with-/without-Content_Size)
3. Verify decompressed output is non-empty (except empty-block.zst)
4. Verify SHA-256 of decompressed content matches _corpus-manifest.yaml entry
5. For dict-compressed.zst: verify correct dictionary is provided

### Invalid Sample Tests
For each invalid sample:
1. Confirm file exists and is non-empty
2. Attempt decompression via stream_reader()
3. Assert ZstdError is raised
4. Record error classification: corrupt/truncated/extraneous

### Round-Trip Checks
For synthetic valid samples (minimal-synthetic.zst, text-compressed.zst, random-data.zst):
1. Decompress to bytes
2. Re-compress with zstandard
3. Re-decompress the re-compressed output
4. Assert original == final (round-trip lossless)

### Hash Comparison
All samples have SHA-256 hashes in _corpus-manifest.yaml.
Prototype must verify hashes on compressed bytes (not decompressed content).

---

## Risks

### 1. Codec/No-DOM Limitation
ZST has no document object model. There are no named fields, no structured content,
no namespace or schema. The format's value is purely as a compression codec.
Implication: Gate 5 neutral model is non-trivial (or N/A). Gate 6 oracle comparison
is simpler (compress/decompress only). Commercial product value is lower than document formats.

### 2. Limited Commercial Product Value (Standalone)
Aspose already supports ZST (confirmed in Gate 1 audit). A standalone ZST parser/converter
duplicates existing Aspose capabilities without differentiation.
Commercial value requires: (a) use as a compression layer within another format's pipeline,
or (b) specialized corpus tooling, or (c) differential capability beyond Aspose.
This must be addressed explicitly at Gate 5 with human product sign-off.

### 3. Patent/Legal Notes
RFC 8878 is IETF Informational. The Zstandard algorithm itself:
- Reference implementation: facebook/zstd (BSD-3-Clause)
- No IETF patent claims asserted
- facebook/zstd has PATENTS file (Facebook-specific, covers only their implementation)
- Using python-zstandard (CFFI bindings, BSD-3-Clause) for our implementation avoids
  direct Facebook patent risk
- Legal notes confirmed: Category 1, RF implementation rights per legal-notes.md (Gate 2)

### 4. Implementation Complexity at Block Level
The Zstandard block codec (FSE entropy coding + Huffman coding) is significantly
more complex than the frame-level format. A pure decompressor without library use
would require implementing FSE and Huffman table decoding from scratch.
This is not required at Gate 4 (wrapper-first approach recommended).

### 5. Aspose Support Justification
Since Aspose already supports ZST, acquisition value must be justified as:
- Independent open-source support (Python FOSS track)
- Format family completeness in combination pipelines
- Test/validation tooling independent of Aspose
This should be explicitly addressed in Gate 5 generated requirements.

---

## Gate 5 Readiness Criteria

Before Gate 5 (Neutral Model) can begin:
1. Gate 4 must be passed (prototype + human approval)
2. Human product approval for ZST commercial value must be recorded
3. generated-requirements/zst/ must be authorized by human execution prompt
4. Neutral model for compression formats must be defined or N/A justification documented
5. Gate 5 scope for a codec format (vs document format) must be explicitly decided

---

## Explicit Non-Authorization

- This file does NOT authorize source implementation.
- No code in src/python/zst/ or src/net/zst/ is authorized.
- No generated-requirements/zst/ is authorized.
- Gate 4 is NOT passed by this planning artifact alone.
- Gate 5+ approval requires separate human execution prompt.
- implementation_authorized: false (must remain false until explicitly authorized)
- generated_requirements_authorized: false (must remain false until explicitly authorized)

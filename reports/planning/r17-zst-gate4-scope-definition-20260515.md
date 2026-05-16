# R17 Gate 2: ZST Gate 4 Scope Definition
Sprint: FORMAT-FACTORY-R17-R16-CLOSURE-VERIFY-ZST-GATE4-PLANNING-AND-MULTI-FORMAT-GATE1-SWARM-001
Date: 2026-05-16
Gate: 2 — ZST Gate 4 Scope Definition

## Gate 4 Definition (from docs/gates.md)

Gate 4: Prototype Complete

Pass criteria:
1. Working prototype parser in `prototypes/by-format/<format-id>/`
2. Prototype parses all Gate 3 corpus samples without crashing
3. Prototype README with approach, decisions, limitations, security mitigations
4. For XML formats: XXE and entity expansion mitigations demonstrated
5. Human-reviewed for correctness and security baseline

Required artifacts:
- `prototypes/by-format/<format-id>/` with parser source
- Prototype README with security section
- `parser-requirements.yaml` under `.local/spec-cache/{format-id}/{version}/normalized/`
  OR explicit human-approved waiver G-NORM-004 in gap register

Fast-path: None. Human review required.

## What Gate 4 Means for ZST

Gate 4 requires working source code in prototypes/. This sprint is planning-only.
Therefore:

- This sprint produces: `acquisition-packs/zst/parser-notes.md` (planning artifact)
- This sprint does NOT produce: prototype code, prototype README, parser-requirements.yaml
- Gate 4 status after this sprint: `planning_complete` (not passed)
- Gate 4 full pass: requires R18 execution prompt authorizing prototype + human review

## Codec vs Document-Object Format Treatment

ZST is a codec/compression format — fundamentally different from document-object formats:

| Dimension | XML/ODF Formats (FODS/FODT) | ZST (Codec) |
|-----------|----------------------------|-------------|
| DOM structure | Rich object model | None — bytestream transform |
| Parsing goal | Extract structured data | Decompress bytes |
| XXE mitigations | Required | Not applicable |
| Gate 4 prototype | Parser + DOM builder | Decompressor wrapper or frame validator |
| Neutral model | Required (Gate 5) | Potentially N/A or minimal |
| Commercial value source | Rich editing features | Compression support in containers |
| Security concerns | XML injection, entity expansion | Zip bombs, large output, decompressor state |

Recommendation: ZST Gate 4 prototype should be a **frame validator + decompressor wrapper**, not
a DOM parser. It should demonstrate: (a) valid frame detection, (b) decompression success on
valid corpus, (c) rejection of invalid corpus, (d) compression ratio reporting.

## Parsing Strategy Options for ZST

### Option A: Pure Frame Parser
- Implement ZST frame header reader from RFC 8878
- Parse magic number, FHD byte, frame header, blocks, checksums
- No decompression — validation only
- Pros: Full format control, no library dependency
- Cons: High complexity; blocks are separately decoded (FSE/Huffman); significant effort

### Option B: Wrapper Around `zstandard` Python Library
- Use python-zstandard (v0.25.0, CFFI-based, BSD-3) as decompression oracle
- Add frame detection, error classification, and corpus validation
- Pros: Fast to implement; already in project environment; well-tested
- Cons: Library dependency; no pure-Python path; defers frame-level understanding

### Option C: CLI Oracle (zstd binary)
- Drive zstd CLI as oracle for decompression and frame inspection
- Pros: Zero Python code; purely external validation
- Cons: System dependency; not suitable for Python OSS library output

### Option D: Hybrid Phased Approach (Recommended)
- Phase 1 (Gate 4): Wrapper around zstandard for decompression + frame header reader for magic/FHD
- Phase 2 (Gate 5+): Pure frame parser + block-level understanding
- Phase 3 (Gate 6+): Commercial product integration if justified
- Pros: Delivers working prototype fast; builds toward pure parser incrementally

## What Is Allowed Before Generated Requirements

Before generated-requirements/zst/ is authorized:
- parser-notes.md (planning) — ALLOWED
- prototypes/by-format/zst/ (prototype code) — ALLOWED at Gate 4 with prototype execution prompt
- spec-cache review and annotation — ALLOWED (no mutation of spec source)
- Frame header exploration scripts in .local/ — ALLOWED (not src/)
- Discussion of approaches — ALLOWED

Forbidden:
- generated-requirements/zst/ — FORBIDDEN until authorized
- src/python/zst/ — FORBIDDEN until Gate 5+ authorized
- src/net/zst/ — FORBIDDEN until Gate 5+ authorized
- Claiming Gate 4 pass without prototype — FORBIDDEN

## RFC 9659 Update Relationship

RFC 9659 (2023) obsoletes portions of RFC 8878 (2022) with minor clarifications.
For Gate 4 planning, RFC 8878 remains the primary normative reference.
RFC 9659 alignment should be noted in parser-notes.md.

## Gate 4 Readiness Criteria for Next Sprint

To pass Gate 4 in R18+, the following must exist:
1. `prototypes/by-format/zst/` with working decompressor/validator
2. Prototype README documenting approach and security notes
3. All 8 valid corpus samples decompress without error
4. All 3 invalid corpus samples raise expected errors
5. parser-requirements.yaml in spec-cache OR human waiver G-NORM-004
6. Human review + approval recorded

## Conclusion

ZST Gate 4 this sprint = planning_complete (parser-notes.md).
Prototype + full Gate 4 approval = R18+ scope.

GATE_2_ZST_GATE4_SCOPE: DEFINED

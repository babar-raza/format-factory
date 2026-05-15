# ZST Governed Candidate Audit
Sprint: FORMAT-FACTORY-R12-ACQUISITION-ENGINE-IV-AND-ZST-GOVERNED-READINESS-SWARM-001
Lane: B
Date: 2026-05-14
Status: AUDIT_COMPLETE

> **NOT AN ACQUISITION AUTHORIZATION.** This is a governed candidate audit report.
> ZST acquisition has NOT been authorized. No implementation may begin.
> Human review and support-matrix audit required before any acquisition execution.

---

## Format Identity

| Field | Value |
|-------|-------|
| format_id | zst |
| display_name | Zstandard Compressed File |
| extension | .zst |
| category | archive |
| MIME type | application/zstd |
| backlog_tier | TIER_A_NEAR_TERM |
| acquisition_state | CANDIDATE |

---

## Public Specification Audit

### Primary Spec
**RFC 8878** — Zstandard Compression and the application/zstd Media Type
- Published by: IETF (Internet Engineering Task Force)
- Status: Proposed Standard (RFC)
- Provenance: Full public — freely accessible, no IP encumbrance
- Content coverage: Complete bitstream format, magic numbers, block structure, frame format, checksum, dictionary support

### Spec Quality Classification: FULL_PUBLIC — HIGH QUALITY
- RFC-level specification (not draft, not community wiki)
- Single authoritative document (no fragmentation across versions)
- Maintained by IETF; versioned with stable reference
- Predecessor: RFC 8478 (obsoleted by RFC 8878)

### Supporting References
- Reference implementation: `zstd` (Meta/Facebook) — BSD+GPLv2 dual license
- Open-source implementations: numerous (python-zstandard, zstd-safe, zstd-rs, etc.)
- Widely adopted: used in Linux kernel, Facebook infrastructure, package managers (npm, rpm, Arch Linux)

### Assessment: SPEC_ASSUMPTIONS_VERIFIED

---

## RFC Reference Verification

The backlog entry states "Full public RFC spec." This claim is verified:
- RFC 8878 exists and is publicly accessible
- RFC was published 2021-02-01 (latest version; obsoletes RFC 8478 from 2018)
- RFC specifies: magic number (0xFD2FB528), frame format, block types (raw/RLE/compressed), LZ77+ANS (FSE), Huffman coding for literals
- The spec is complete enough to implement a compatible decoder without reference code

**RFC Verification: CONFIRMED**

---

## Lifecycle Placement Audit

Per `acquisition_lifecycle_simulator.py`:
- Current state: **CANDIDATE** (no profile in `KNOWN_FORMAT_PROFILES`)
- Next required state: **SUPPORT_MATRIX_AUDIT**
- Is terminal: No
- Is blocked: No
- Active blockers: None

### Lifecycle Placement Assessment
ZST is correctly placed at CANDIDATE. It has NOT undergone:
- Support matrix audit (Aspose coverage unknown)
- Spec normalization/caching
- Requirements generation
- Verifier review
- DEC-034 IV sprint

The lifecycle position is **accurate and conservative**. No inflation of state.

---

## Readiness Scoring Audit

### From public_spec_readiness_scorer.py — ZST spec entry:
```python
{"fmt": "zst", "spec_type": "full_public", "category": "archive",
 "sample_files_known": True, "legal_use_clear": True, "open_source_reference": True}
```

### Score Decomposition Verified (independently):

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| spec_availability | 10 | full_public → 10 |
| spec_completeness | 9 | full_public → 9 |
| complexity | 7 | archive → 7 (no binary penalty, compression is not binary_format=True here) |
| sample_availability | 8 | sample_files_known=True → 8 |
| legal_clarity | 9 | legal_use_clear=True → 9 |
| parser_feasibility | 10 | spec_completeness(9) + open_source_reference(+2) = min(10, 11) = 10 |
| oracle_feasibility | 7 | open_source_reference=True → 7 |
| requirements_gen_readiness | 9 | full_public + legal_use_clear → 9 |
| **Weighted composite** | **8.95** | All weights applied per DIMENSION_WEIGHTS |

**Readiness tier: ACQUISITION_READY (score ≥ 8.0)**

### Scoring Assumption Challenges

**Challenge 1:** Is `binary_format=False` correct for ZST?
ZST is a binary compressed format. Setting `binary_format=False` raises the score by +3 complexity and +2 parser_feasibility compared to binary=True.

However, ZST has a full RFC specification — unlike formats where binary=True creates a parser feasibility penalty due to lack of spec. The scoring system uses `binary_format` primarily to penalize formats without a spec that are hard to parse. ZST's RFC makes the binary structure fully specified. Setting binary=True would reduce score to ~8.45 but would still be ACQUISITION_READY.

**Verdict:** `binary_format=False` is debatable but not incorrect. The RFC specification compensates for binary complexity. The score would remain ACQUISITION_READY under either setting.

**Challenge 2:** Is `legal_use_clear=True` correct?
- RFC 8878 is published under IETF Trust (free to implement)
- Reference implementation `zstd` is BSD+GPLv2 — implementation does NOT require GPLv2
- No known patent claims
- Widely deployed in production under commercial products

**Verdict:** `legal_use_clear=True` is justified for ZST. No legal blockers identified.

**Challenge 3:** Is `open_source_reference=True` correct?
Meta's `zstd` is open-source (BSD+GPLv2). It is the canonical reference implementation cited in RFC 8878.

**Verdict:** Confirmed correct.

---

## Parser Complexity Assessment

### Zstandard Format Structure
ZST uses a frame-based format:
1. **Magic number** (4 bytes): 0xFD2FB528
2. **Frame header**: variable length, configurable
3. **Data blocks**: LZ77 + ANS (Asymmetric Numeral Systems), FSE entropy coding
4. **Checksum**: optional xxHash64

### Parser Complexity Classification: MEDIUM-HIGH
- Frame parsing: MEDIUM (structured, well-specified)
- LZ77 decompression: MEDIUM (standard algorithm)
- FSE/ANS entropy coding: HIGH (specialized entropy coder; not standard Huffman)
- Skippable frames: LOW (simple to implement)
- Dictionary support: HIGH (shared dictionaries complicate oracle testing)

### Acquisition Complexity vs. FODS/FODT
FODS/FODT: XML parsing — LOW complexity
ZST: Binary + FSE/ANS — HIGH parser complexity

**This is a strength of the acquisition engine test, NOT a weakness.** ZST validates that the system can reason about non-XML/non-document complexity.

---

## Oracle Feasibility Assessment

### Round-Trip Oracle
ZST is a compression format. Round-trip oracle = compress → decompress → verify content identity.
- **Feasibility:** HIGH — round-trip is the natural test for compression
- **Reference tool:** `zstd` CLI available; `zstandard` Python library available
- **Determinism concern:** Compression level affects output but decompression is deterministic
- **Sample provenance:** Widely available (Linux package files, npm tarballs, etc.)

### Oracle Classification: FEASIBLE_WITH_REFERENCE_TOOL

---

## Support Matrix Classification

### Aspose Support Status
- `audit_status: needs_audit` (per backlog — no audit has been run)
- `aspose_supported: None` (not claimed)
- Aspose.ZIP library family supports major archive formats but ZST support is UNKNOWN pending audit

### Archive Category Classification
ZST is correctly classified as `category: archive`. It is:
- A compression container (not a document format)
- Typically wraps a single file (unlike ZIP which is multi-file)
- Used as a transport/storage compression layer

**Support matrix classification: NEEDS_AUDIT — correctly recorded**

---

## Package/Archive Classification

ZST is a compression format, not an archive format in the ZIP/TAR sense:
- **No multi-file container** (single stream)
- **Often combined with TAR** (.tar.zst) for multi-file archives
- **Distinct from ZIP/RAR/7z** (no internal file directory)

### Implications for Acquisition
- Parser scope: decompressor only (not a file system browser)
- Oracle scope: compress/decompress round-trip
- Simpler scope than ZIP family

---

## Legal and Provenance Assessment

| Aspect | Status |
|--------|--------|
| Spec provenance | IETF RFC 8878 — free to implement |
| Reference implementation license | BSD+GPLv2 (use BSD path; no GPL required) |
| Known patent claims | None identified |
| Trademark conflicts | None identified |
| Export control | Standard compression — no known restrictions |
| Reverse engineering required | NO — RFC is sufficient |

**Legal classification: CLEAN — no blockers**

---

## Acquisition Blockers

**Current blockers: NONE**

The following are pending items (not blockers):
- Support-matrix audit (Aspose ZST coverage unknown)
- Requirements generation (not yet started)
- Spec cache (RFC not yet locally normalized)
- DEC-034 IV sprint for the acquisition plan

---

## Recommended First Vertical Slice Scope

> **SIMULATION ONLY — this is a planning recommendation, not an authorization.**

If ZST acquisition were to proceed (post-authorization):

1. **Sprint R12-ZST-SUPPORT-AUDIT**: Run support-matrix audit against current Aspose libraries. Determine if Aspose.ZIP covers ZST decompression.
2. **Sprint R12-ZST-SPEC-CACHE**: Normalize RFC 8878 locally. Produce spec-evidence.md for acquisition pack.
3. **Sprint R12-ZST-REQ-GEN**: AI-assisted requirements generation from spec. Schema-validate. Verifier-review.
4. **Sprint R12-ZST-IV**: DEC-034 IV of requirements (separate session).
5. **Sprint R12-ZST-TIER0**: Tier 0 decompressor — read ZST stream → output uncompressed bytes. Governed vertical slice.

**First slice scope (Tier 0):** ZST decompressor only. No compression. No dictionary support. No streaming. Input: .zst file. Output: decompressed bytes. Oracle: compress with reference zstd, decompress with implementation, compare.

---

## Recommended Simulation-Only Next Steps

1. Complete support-matrix audit simulation (already in lifecycle simulator)
2. Create `acquisition-packs/zst/` stub pack (planning artifact only)
3. Run ZST acquisition graph simulation via `acquisition_graph_simulator` (Lane E)
4. Verify scoring remains ACQUISITION_READY after binary_format=True sensitivity test
5. Produce ZST requirements template (not generated requirements — template only)

---

## Audit Summary

| Check | Result |
|-------|--------|
| Public spec exists (RFC 8878) | CONFIRMED |
| RFC reference accurate | CONFIRMED |
| Lifecycle placement (CANDIDATE) | CORRECT |
| Readiness score (8.95) | REPRODUCED |
| Parser complexity honest | CONFIRMED (MEDIUM-HIGH) |
| Oracle feasibility (round-trip) | CONFIRMED |
| OSS reference (zstd) | CONFIRMED |
| Support matrix (needs_audit) | CORRECTLY RECORDED |
| Archive classification | CONFIRMED |
| Legal/provenance | CLEAN |
| No acquisition execution | CONFIRMED |

**ZST_GOVERNED_READINESS_STATUS: AUDIT_COMPLETE_ACQUISITION_READY_PENDING_SUPPORT_MATRIX_AUDIT**

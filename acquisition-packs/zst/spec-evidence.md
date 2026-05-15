---
artifact_id: zst-spec-evidence
artifact_type: spec-evidence
path: acquisition-packs/zst/spec-evidence.md
format_id: zst
gate: 2
visibility: evidence-only
publish_allowed: false
generated_by: claude
generated_at: "2026-05-15"
sprint: FORMAT-FACTORY-R14-ZST-SPEC-RETRIEVAL-AND-GATE2-SWARM-001
evidence_status: evidence_cached_pending_independent_verification
---

# ZST Spec Evidence
Format: Zstandard (.zst)
Gate: 2
Date: 2026-05-15

---

## Spec Identity

| Field | Value |
|-------|-------|
| Primary spec | RFC 8878: Zstandard Compression and the 'application/zstd' Media Type |
| RFC status | IETF Informational (2021-02-01) |
| RFC obsoletes | RFC 8478 |
| RFC updated-by | RFC 9659 (window size in HTTP contexts) |
| Secondary spec | RFC 9659: Window Sizing for Zstandard Content Encoding (IETF Informational, 2024-09-01) |
| IANA media type | application/zstd (registered per RFC 8878 §4) |
| IANA content-encoding | zstd (registered per RFC 8878 §4) |
| IANA suffix | +zstd (registered per RFC 8878 §4) |

---

## Cached Source Record

| Spec | Local path | SHA-256 | Size |
|------|-----------|---------|------|
| RFC 8878 | .local/spec-cache/zst/rfc8878/rfc8878.txt | sha256:8ee6be03534113f5689cda75b9539a02e0704a2506d420814223e506420aeea4 | 112,425 bytes |
| RFC 9659 | .local/spec-cache/zst/rfc9659/rfc9659.txt | sha256:a43584f250506db54df8bc9ff90652888135369fbc331453f67a71829b0827a2 | 6,599 bytes |

Evidence claim status: **[SUPPORTED_BY_CACHED_SOURCE]**

---

## Key Technical Facts from RFC 8878

| Section | Claim | Evidence Status |
|---------|-------|-----------------|
| §1 | ZST is a lossless compression algorithm | [SUPPORTED_BY_CACHED_SOURCE] |
| §3.1.1 | Frame magic number: 0xFD2FB528 (little-endian) | [SUPPORTED_BY_CACHED_SOURCE] |
| §3.1 | Two frame types: Zstandard frames and Skippable frames | [SUPPORTED_BY_CACHED_SOURCE] |
| §3.1.1.1 | Frame Header Descriptor describes frame content size, window descriptor, dict ID, checksum | [SUPPORTED_BY_CACHED_SOURCE] |
| §3.1.1.3 | Blocks: Raw, RLE, or Compressed (LZ77 + ANS/FSE + Huffman) | [SUPPORTED_BY_CACHED_SOURCE] |
| §3.1.1.5 | FSE (Finite State Entropy) tables define symbol encoding | [SUPPORTED_BY_CACHED_SOURCE] |
| §3.1.2 | Skippable frames: magic 0x184D2A5X, user-defined payload | [SUPPORTED_BY_CACHED_SOURCE] |
| §4 | IANA: application/zstd registered; content-encoding "zstd"; "+zstd" suffix | [SUPPORTED_BY_CACHED_SOURCE] |

---

## Errata Impact Assessment

RFC 8878 has 7 errata (3 verified, 4 reported). All are technical corrections to:
- FSE/Huffman code tables (Appendix A, §3.1.1.5)
- Encoding examples (§4.2.2)
- Section heading precision (§3.1.1.3.1)

**Gate 2 impact:** NONE — errata do not affect media type registration, legal classification,
or spec caching eligibility. Must be applied when implementing parser (Gate 4+).

---

## RFC 9659 Scope Clarification

RFC 9659 updates RFC 8878 to require (not just recommend) limiting Zstandard window size
to ≤8 MB when used as HTTP content encoding. This prevents browser/UA compatibility issues.

**Gate 2 impact:** None for file-level Zstandard. For format-factory's archive track
use case (decompression of .zst files), this RFC has no practical effect.

---

## Gate 2 Evidence Classification

| Criterion | Status |
|-----------|--------|
| RFC 8878 publicly available | PASS — rfc-editor.org |
| RFC 8878 cached locally | PASS — sha256 recorded |
| RFC 9659 cached locally | PASS — sha256 recorded |
| Update relationship documented | PASS |
| Errata noted | PASS (7 total; implementation-level only) |
| IANA media type confirmed | PASS — application/zstd §4 |
| Legal category confirmed | PASS — Category 2 |
| IPR cleared | PASS (substantive — no disclosures found) |

---

GATE2_SPEC_EVIDENCE: GATE2_PASS_WITH_LEGAL_NOTES
evidence_status: evidence_cached_pending_independent_verification

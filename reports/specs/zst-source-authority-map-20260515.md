# ZST Spec Source Authority Map
Sprint: FORMAT-FACTORY-R14-ZST-SPEC-RETRIEVAL-AND-GATE2-SWARM-001
Gate: 3 (Lane D)
Date: 2026-05-15
Internet access: AUTHORIZED for Gate 2 authoritative public specification retrieval

---

## Canonical Source Map

### 1. RFC 8878 — Base Zstandard Specification

| Field | Value |
|-------|-------|
| Document | RFC 8878: Zstandard Compression and the 'application/zstd' Media Type |
| Status | IETF Informational |
| Publication Date | 2021-02-01 |
| Authors | Y. Collet, M. Kucherawy (Editor) |
| Obsoletes | RFC 8478 |
| Updated by | RFC 9659 |
| Canonical info page | https://www.rfc-editor.org/info/rfc8878 |
| Canonical text source | https://www.rfc-editor.org/rfc/rfc8878.txt |
| Canonical XML source | https://www.rfc-editor.org/rfc/rfc8878.xml |
| Datatracker page | https://datatracker.ietf.org/doc/rfc8878/ |
| Intended local cache path | .local/spec-cache/zst/rfc8878/rfc8878.txt |
| Retrieval method | python tools/spec-cache/acquire_spec.py --allow-network |
| Hashing method | SHA-256 (tools/spec-cache/acquire_spec.py computes on download) |
| Refresh policy | manual (RFC text is immutable once published) |
| Accessed date | 2026-05-15 |

**Note:** tools.ietf.org is NOT a canonical source per R14 sprint policy. Use rfc-editor.org.

---

### 2. RFC 9659 — Zstandard Window Size Update

| Field | Value |
|-------|-------|
| Document | RFC 9659: Window Sizing for Zstandard Content Encoding |
| Status | IETF Informational |
| Publication Date | 2024-09-01 |
| Authors | N. Jaju (Ed.), W. F. Handte (Ed.) |
| Updates | RFC 8878 |
| Canonical info page | https://www.rfc-editor.org/info/rfc9659 |
| Canonical text source | https://www.rfc-editor.org/rfc/rfc9659.txt |
| Canonical XML source | https://www.rfc-editor.org/rfc/rfc9659.xml |
| Datatracker page | https://datatracker.ietf.org/doc/rfc9659/ |
| Intended local cache path | .local/spec-cache/zst/rfc9659/rfc9659.txt |
| Retrieval method | python tools/spec-cache/acquire_spec.py --allow-network |
| Hashing method | SHA-256 |
| Refresh policy | manual (RFC text is immutable once published) |
| Accessed date | 2026-05-15 |

---

### 3. Update Relationship

| Relationship | Value |
|-------------|-------|
| RFC 8878 obsoletes | RFC 8478 (earlier Zstandard draft) |
| RFC 8878 updated by | RFC 9659 |
| RFC 9659 updates | RFC 8878 |
| Scope of RFC 9659 update | Window size limit in HTTP contexts ONLY — changed from recommendation to requirement |
| Core frame format affected | NO — RFC 9659 does not change core Zstandard frame format, magic number, block types, or compression algorithms |
| Classification | RFC 9659 is a narrow HTTP-context update; core spec authority remains RFC 8878 for file format purposes |

**Critical note:** RFC 8878 is the authoritative specification for Zstandard as a file format.
RFC 9659 only matters in HTTP content-encoding contexts (window size interoperability).
For format-factory acquisition purposes, RFC 8878 is the primary spec. RFC 9659 must still
be cached to ensure completeness of the spec record.

---

### 4. IETF IPR Disclosure Links

| Document | IPR Search URL | Result |
|----------|---------------|--------|
| RFC 8878 | https://datatracker.ietf.org/ipr/search/?submit=rfc&rfc=8878 | Returned 403 (requires session). Datatracker doc page shows no patent declarations in document. |
| RFC 9659 | https://datatracker.ietf.org/ipr/search/?submit=rfc&rfc=9659 | No patent declarations confirmed via datatracker doc page. |

**Note:** IETF IPR search returned 403 (session required). The datatracker document pages for
both RFCs confirm no explicit patent declarations. Neither RFC references specific patent holders.
The Zstandard upstream patent grant (Meta ADDITIONAL_GRANT) was documented in R13B legal audit
and applies to the implementation, not the RFC text itself. No IETF IPR disclosures identified.

---

### 5. RFC Errata Links

| Document | Errata URL | Count | Classification |
|----------|-----------|-------|----------------|
| RFC 8878 | https://www.rfc-editor.org/errata/rfc8878 | 7 total (3 verified, 4 reported) | Technical — affects code tables and encoding examples only |
| RFC 9659 | https://www.rfc-editor.org/errata_search.php?rfc=9659 | 0 | No errata |

RFC 8878 errata affect implementation details (Huffman/FSE code tables, encoding examples).
They do NOT affect the IANA media type registration, the legal classification, or Gate 2 eligibility.
Errata must be noted in spec-evidence.md and legal-notes.md.

---

### 6. IANA Media Type Registry

| Field | Value |
|-------|-------|
| Media type | application/zstd |
| Registry | IANA Media Types (application) |
| Reference | RFC 8878 §3 |
| Registration | Section 3 of RFC 8878 formally registers application/zstd |
| Notes | RFC 8878 also registers content-encoding "zstd" and structured syntax suffix "+zstd" |

---

### 7. Upstream License/Patent Grant (Revalidation)

| Field | Value |
|-------|-------|
| Source | https://github.com/facebook/zstd/blob/dev/LICENSE |
| Status | Already captured in R13B Gate 5 legal audit |
| Revalidation needed | NO — license is stable; BSD/GPLv2 dual (choose BSD). Patent ADDITIONAL_GRANT documented. |
| R14 action | Confirm R13B findings in spec-evidence.md; no re-download of license file needed |

---

## Source Exclusion Rationale

| Excluded Source | Reason |
|----------------|--------|
| tools.ietf.org | Explicitly forbidden per R14 sprint policy |
| Community mirrors | Not canonical per project Rule 4 (docs/specification-cache.md) |
| Third-party RFC mirrors | Not canonical |
| GitHub zstd repo spec copy | Not the official RFC editor source |

---

SOURCE_AUTHORITY_MAP: COMPLETE

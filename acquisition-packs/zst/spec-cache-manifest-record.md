# ZST Spec Cache Manifest Record
Format: ZST (Zstandard)
Sprint: FORMAT-FACTORY-R14-ZST-SPEC-RETRIEVAL-AND-GATE2-SWARM-001
IV verified by: FORMAT-FACTORY-R14C-ZST-GATE2-CLOSURE-REPAIR-AND-IV-SWARM-001
Date: 2026-05-15

---

## Purpose

This file is the committed evidence proxy for the local-only spec cache.
Full RFC text is stored under `.local/spec-cache/zst/` which is gitignored per
`docs/python-foss/specification-cache.md`. This record captures all provenance needed for
audit and independent verification without committing copyrighted RFC text.

---

## Cache Root

Local path: `.local/spec-cache/zst/`
Policy: gitignored (IETF RFC text redistribution not permitted)
Full spec text is NOT committed to git — local-only per project policy.

---

## RFC 8878

| Field | Value |
|-------|-------|
| Title | Zstandard Compression and the 'application/zstd' Media Type |
| Status | IETF Informational |
| Published | 2021-02-01 |
| Source URL | https://www.rfc-editor.org/rfc/rfc8878.txt |
| Canonical info | https://www.rfc-editor.org/info/rfc8878 |
| Local path | .local/spec-cache/zst/rfc8878/rfc8878.txt |
| Size | 112,425 bytes |
| SHA-256 | sha256:8ee6be03534113f5689cda75b9539a02e0704a2506d420814223e506420aeea4 |
| Retrieval date | 2026-05-15 |
| Redistribution | NOT permitted (IETF copyright) |

---

## RFC 9659

| Field | Value |
|-------|-------|
| Title | Window Sizing for Zstandard Content Encoding |
| Status | IETF Informational |
| Published | 2024-09-01 |
| Source URL | https://www.rfc-editor.org/rfc/rfc9659.txt |
| Local path | .local/spec-cache/zst/rfc9659/rfc9659.txt |
| Size | 6,599 bytes |
| SHA-256 | sha256:a43584f250506db54df8bc9ff90652888135369fbc331453f67a71829b0827a2 |
| Retrieval date | 2026-05-15 |
| Redistribution | NOT permitted (IETF copyright) |

---

## Update Relationship

RFC 8878 is updated by RFC 9659.
RFC 9659 scope: **HTTP content-encoding only** (window sizing for HTTP Transfer-Encoding: zstd contexts).
RFC 9659 does NOT modify the Zstandard frame format, compression algorithm, or IANA media type.
For file-level decompression (format acquisition use case), RFC 8878 is the primary specification.

Source: `.local/spec-cache/zst/provenance/update-relationship.yaml`

---

## Errata and IPR Summary

### RFC 8878 Errata (7 total)
| ID | Type | Status | Section | Summary |
|----|------|--------|---------|---------|
| 6441 | technical | verified | Appendix A | Duplicate all-zero rows in code tables |
| 6442 | technical | verified | 3.1.1.5 | Table 18 offset value correction |
| 7297 | technical | verified | 3.1.1.3.1.1 | Size range values start at 6, not 0 |
| 7567 | technical | reported | 3.1.1.3.1 | Duplicate section heading |
| 8085 | technical | reported | 3.1.1.5 | Table 18 last row correction |
| 8195 | technical | reported | 4.2.2 | Symbol encoding example correction |
| 8668 | technical | reported | 3.1.1.3.1.4 | Wording precision for compressed literals block |

Gate 2 impact: Implementation-level (Huffman/FSE code tables only). Do NOT affect media type or Gate 2 eligibility.

### RFC 9659 Errata: 0

### IPR
- RFC 8878: IETF IPR endpoint returned 403 (requires session). Document page confirms no declarations.
- RFC 9659: No patent declarations (confirmed).
- Meta ADDITIONAL_GRANT patent license recorded in R13B.

---

## Refresh Policy

The cached spec text should be refreshed if:
1. A new superseding RFC is issued for the Zstandard format
2. More than 12 months have passed since retrieval date
3. A new verified errata is added that affects Gate 2 eligibility assessment

Refresh requires a new sprint with authorization and hash update.

---

## Independent Verification

Verified by: FORMAT-FACTORY-R14C-ZST-GATE2-CLOSURE-REPAIR-AND-IV-SWARM-001
IV date: 2026-05-15
Verification command (cache integrity):
```
python -m pytest tests/skills/test_zst_spec_cache_gate2.py -q
# Result: 20 passed in 0.36s
```

Verification confirms SHA-256 hashes match cached files and all provenance files present.

---

SPEC_CACHE_MANIFEST_RECORD: VERIFIED_2026-05-15

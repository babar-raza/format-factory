# Real Source Acquisition Report
Pilot: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R2-001
Generated: 2026-06-05

## Overview

R2 advances from fixture-based (R1) to real-source acquisition for ZST, Netpbm, and FODS.
DIF remains EMPIRICAL_ONLY (no authoritative spec exists).

## Source 1: ZST — RFC 8878

| Field | Value |
|-------|-------|
| Source ID | src-r2-zst-rfc8878 |
| Title | RFC 8878 — Zstandard Compression and the 'application/zstd' Media Type |
| Fetch method | REAL_FETCH — urllib.request.urlopen to rfc-editor.org |
| URL | https://www.rfc-editor.org/rfc/rfc8878.txt |
| Vault path | .local/evidences/spec-authority-real-pilot-r2/spec-vault/zst/rfc8878-real.txt |
| Byte size | 112,425 bytes |
| SHA-256 | 8ee6be03534113f5689cda75b9539a02e0704a2506d420814223e506420aeea4 |
| Authority status | ACCEPTED_SPEC |
| Sections parsed | 491 |
| Requirements extracted | 58 |

The full RFC 8878 text was fetched live from the IETF RFC Editor. This is the authoritative
IETF standard for Zstandard compression. No HTML stripping required — source is plain text.

## Source 2: Netpbm — Sourceforge HTML Docs

| Field | Value |
|-------|-------|
| Source ID | src-r2-netpbm-spec |
| Title | Netpbm Format Specifications (PBM/PGM/PPM) — Sourceforge |
| Fetch method | REAL_FETCH — HTML pages stripped to plain text |
| Source URLs | https://netpbm.sourceforge.net/doc/pbm.html, pgm.html, ppm.html |
| Authority status | ACCEPTED_WITH_CAVEAT |
| Sections parsed | 3 |
| Requirements extracted | 12 |

Three HTML spec pages fetched and stripped via HTMLStripper (html.parser.HTMLParser).
Combined into single normalized document with section markers.

### Component SHAs

| Format | SHA-256 (of raw HTML) |
|--------|----------------------|
| PBM | b56089e0c386e2cc43e44a8124569185b7b1db863daed19da27c3045ca64e9d9 |
| PGM | b9c11d3613c1953e5e77e93ef4c0f4a010cd55138e1c4710a14e913f0f38f3de |
| PPM | d029cd9c665322af35f94f77097aa0c6f02829ce8a9e5ffb1bcd3abbdd3a3805 |

Caveat: Netpbm is a de facto public domain standard; no formal IETF/ISO standard.
Authority stays ACCEPTED_WITH_CAVEAT.

## Source 3: DIF — Empirical Fixture

| Field | Value |
|-------|-------|
| Source ID | src-r2-dif-empirical |
| Title | DIF (Data Interchange Format) — Empirical Observation |
| Fetch method | LOCAL_FIXTURE — no real spec available |
| Authority status | EMPIRICAL_ONLY |
| Sections parsed | 6 |
| Requirements extracted | 13 |

No authoritative DIF specification found anywhere. EMPIRICAL_ONLY maintained from R1.
Anti-bypass prevents any promotion to ACCEPTED_SPEC.

## Source 4: FODS — OASIS ODF 1.3 (Scoped)

| Field | Value |
|-------|-------|
| Source ID | src-r2-fods-odf13 |
| Title | ODF 1.3 — Flat Spreadsheet (FODS) — Scoped Introduction |
| Fetch method | REAL_FETCH_SCOPED — OASIS HTML page stripped + scoped to 6000 chars |
| URL | https://docs.oasis-open.org/office/OpenDocument/v1.3/os/ |
| SHA-256 (of raw HTML) | 1095161af2fb794e73f1ef0d13cfe1d735c78fca8132bf43a0c0db78a3f9dafc |
| Authority status | ACCEPTED_WITH_CAVEAT |
| Sections parsed | 51 |
| Requirements extracted | 3 |

Full ODF 1.3 specification exceeds 1000 pages. This pilot extracts the introduction/abstract
only (first 6000 chars of stripped HTML). Full spec ingestion deferred to R3.
Caveat: License review for OASIS ODF 1.3 pending.

## HTML Stripping Method

Custom HTMLStripper (html.parser.HTMLParser subclass):
- Skips script/style tag content
- Inserts newlines at block-level elements (p, h1-h4, li, tr, dt, dd, pre)
- Normalizes consecutive newlines (max 2) and whitespace
- Result: clean plain-text for SAL parser

## Summary

| Source | Fetch Type | Authority | Sections | Requirements |
|--------|-----------|-----------|----------|--------------|
| ZST (RFC 8878) | REAL_FETCH | ACCEPTED_SPEC | 491 | 58 |
| Netpbm (3 HTML) | REAL_FETCH | ACCEPTED_WITH_CAVEAT | 3 | 12 |
| DIF | LOCAL_FIXTURE | EMPIRICAL_ONLY | 6 | 13 |
| FODS (ODF scoped) | REAL_FETCH_SCOPED | ACCEPTED_WITH_CAVEAT | 51 | 3 |
| **Total** | | | **551** | **86** |

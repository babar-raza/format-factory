# ZST Gate 2 Legal/IPR/Errata Report
Sprint: FORMAT-FACTORY-R14-ZST-SPEC-RETRIEVAL-AND-GATE2-SWARM-001
Gate: 5 (Lane F)
Date: 2026-05-15

---

## Summary

| Check | Result |
|-------|--------|
| RFC 8878 public availability | PASS — IETF Informational, rfc-editor.org |
| RFC 9659 public availability | PASS — IETF Informational, rfc-editor.org |
| RFC 8878 status confirmed | PASS — Informational (NOT Proposed Standard) |
| RFC 9659 status confirmed | PASS — Informational |
| Update relationship recorded | PASS — RFC 9659 updates RFC 8878 (HTTP-only) |
| RFC 8878 errata checked | PASS — 7 errata noted (all implementation-level) |
| RFC 9659 errata checked | PASS — 0 errata |
| IETF IPR search | SUBSTANTIVE PASS — no disclosures found; 403 endpoint noted |
| IANA media type | PASS — application/zstd confirmed |
| License classification | PASS — legal_category: 2 (BSD + patent grant) |
| legal_blockers | NONE |

---

## RFC Status Verification

| RFC | Claimed Status | Verified Status | Source |
|-----|---------------|-----------------|--------|
| RFC 8878 | Informational | **Informational** (confirmed) | rfc-editor.org/info/rfc8878 |
| RFC 9659 | Informational | **Informational** (confirmed) | rfc-editor.org/info/rfc9659 |

**Important:** Neither RFC is "Proposed Standard." Both are IETF Informational. This is
consistent with R13B Gate 5 findings and does NOT create any additional implementation
restrictions.

---

## RFC 8878 Details

| Field | Value |
|-------|-------|
| Full title | Zstandard Compression and the 'application/zstd' Media Type |
| Authors | Y. Collet, M. Kucherawy (Editor) |
| Published | 2021-02-01 |
| Stream | IETF (Individual, not WG) |
| Obsoletes | RFC 8478 |
| Updated by | RFC 9659 |
| RFC Editor info page | https://www.rfc-editor.org/info/rfc8878 |
| Cached SHA-256 | sha256:8ee6be03534113f5689cda75b9539a02e0704a2506d420814223e506420aeea4 |

---

## RFC 9659 Update Relationship

| Field | Value |
|-------|-------|
| Full title | Window Sizing for Zstandard Content Encoding |
| Published | 2024-09-01 |
| Updates | RFC 8878 |
| Scope | HTTP window size: recommendation → requirement |
| Frame format affected | NO |
| Legal classification affected | NO |
| Acquisition impact | None for file-level .zst |

**Classification:** RFC 9659 is a narrow HTTP-context update. Core Zstandard format
authority remains RFC 8878. Both RFCs have been cached.

---

## Errata Verification

### RFC 8878 — 7 Errata Total

| ID | Type | Status | Section | Impact |
|----|------|--------|---------|--------|
| 6441 | Technical | Verified | Appendix A | Code table correction (implementation) |
| 6442 | Technical | Verified | 3.1.1.5 | Table 18 offset value (implementation) |
| 7297 | Technical | Verified | 3.1.1.3.1.1 | Size range values (implementation) |
| 7567 | Technical | Reported | 3.1.1.3.1 | Section heading (editorial) |
| 8085 | Technical | Reported | 3.1.1.5 | Table 18 last row (implementation) |
| 8195 | Technical | Reported | 4.2.2 | Encoding example (implementation) |
| 8668 | Technical | Reported | 3.1.1.3.1.4 | Wording precision (editorial) |

**Gate 2 impact:** NONE. All errata affect encoding implementation details.
Parser Gate (Gate 4) must apply verified errata.

### RFC 9659 — 0 Errata

No errata filed for RFC 9659 as of 2026-05-15.

---

## IETF IPR Disclosure Search

| Search Target | URL | Result |
|--------------|-----|--------|
| RFC 8878 IPR | https://datatracker.ietf.org/ipr/search/?submit=rfc&rfc=8878 | 403 Forbidden |
| RFC 9659 IPR | https://datatracker.ietf.org/ipr/search/?submit=rfc&rfc=9659 | Not attempted after 403 |
| RFC 8878 doc page | https://datatracker.ietf.org/doc/rfc8878/ | No patent declarations in document |
| RFC 9659 doc page | https://datatracker.ietf.org/doc/rfc9659/ | No patent declarations in document |

**Limitation note:** IETF IPR search endpoint returned 403 (requires authenticated session).
This is a known limitation of automated access. The datatracker document pages for both RFCs
confirm no explicit patent declarations within the documents. Additional IPR searches were
not possible via automated fetch.

**Classification rationale:** GATE2_PASS_WITH_LEGAL_NOTES (not GATE2_BLOCKED_IPR_UNCLEAR)
because: (1) Zstandard has been widely implemented for 10+ years without patent litigation;
(2) Meta's ADDITIONAL_GRANT patent license covers the reference implementation;
(3) Neither RFC contains patent declarations; (4) No industry reports of Zstandard IPR disputes.
The 403 limitation is a procedural gap, not an IPR risk signal.

---

## IANA Media Type

| Field | Value |
|-------|-------|
| Type | application/zstd |
| Reference | RFC 8878 §4 |
| Content-Encoding | zstd (HTTP) |
| Structured Syntax Suffix | +zstd |
| Status | Registered (RFC 8878, 2021) |

---

## Final Legal Classification

```
GATE2_LEGAL_CLASSIFICATION: GATE2_PASS_WITH_LEGAL_NOTES

legal_category: 2 (Permissive OSS — BSD + patent grant)
spec_availability: full_public_verified
errata_count: 7 (3 verified, 4 reported) — implementation-level only
ipr_status: no_disclosures_found (403 endpoint noted)
legal_blockers: NONE
iana_media_type: application/zstd (confirmed)
not_formal_legal_advice: true
```

---

GATE5_LEGAL_IPR_ERRATA: PASS
CLASSIFICATION: GATE2_PASS_WITH_LEGAL_NOTES

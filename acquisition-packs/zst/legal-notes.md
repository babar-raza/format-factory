# ZST Legal Notes
Format: Zstandard (.zst)
Gate: 2 (cache-backed, post-retrieval classification — not formal legal counsel)
Updated: 2026-05-15
R14 Sprint: FORMAT-FACTORY-R14-ZST-SPEC-RETRIEVAL-AND-GATE2-SWARM-001
Prior: FORMAT-FACTORY-R13B-DELEGATED-ZST-GATE1-REAL-SUPPORT-AUDIT-AND-GOVERNANCE-NORMALIZATION-SWARM-001

---

## Spec Legal Classification (Gate 2 — Cache-Backed)

| Field | Value |
|-------|-------|
| Spec | RFC 8878 (Zstandard Compression Format) |
| Status | IETF Informational (2021-02-01) |
| Replaces | RFC 8478 |
| Updated by | RFC 9659 (window size in HTTP contexts only) |
| IETF rights | IETF grants rights to implement Informational RFCs. No royalty requirement. |
| Spec canonical URL | https://www.rfc-editor.org/info/rfc8878 |
| Spec text URL | https://www.rfc-editor.org/rfc/rfc8878.txt |
| Local cache | .local/spec-cache/zst/rfc8878/rfc8878.txt |
| SHA-256 | sha256:8ee6be03534113f5689cda75b9539a02e0704a2506d420814223e506420aeea4 |
| Classification | PUBLIC_SPEC / RFC_STANDARD |
| legal_category | 2 (Permissive OSS) |
| redistribution_permitted | false (IETF RFC text copyright; local-only caching permitted) |

**IETF BCP 78 compliance:** This file does not reproduce or redistribute RFC text.
The cached RFC text is local-only per docs/specification-cache.md. All citations use
section numbers and line references; no substantial excerpting.

---

## RFC 9659 Update Notes

| Field | Value |
|-------|-------|
| Spec | RFC 9659 (Window Sizing for Zstandard Content Encoding) |
| Status | IETF Informational (2024-09-01) |
| Updates | RFC 8878 — window size in HTTP contexts only |
| Local cache | .local/spec-cache/zst/rfc9659/rfc9659.txt |
| SHA-256 | sha256:a43584f250506db54df8bc9ff90652888135369fbc331453f67a71829b0827a2 |
| Acquisition impact | None for file-format purposes. RFC 9659 concerns HTTP content-encoding only. |

---

## RFC 8878 Errata Status

| Field | Value |
|-------|-------|
| Total errata | 7 (checked 2026-05-15 via rfc-editor.org/errata/rfc8878) |
| Verified errata | 3 (IDs: 6441, 6442, 7297) — affect code tables and encoding examples |
| Reported errata | 4 (IDs: 7567, 8085, 8195, 8668) — technical corrections |
| Acquisition impact | LOW — errata affect FSE/Huffman implementation details; do not affect media type, legal classification, or spec caching |
| Action required | Errata noted; implementation must apply verified errata when building parser |

---

## Reference Implementation License

| Field | Value |
|-------|-------|
| Upstream | facebook/zstd (Meta/Facebook) |
| License | BSD / GPLv2 (dual-license; user's choice) |
| Chosen license for format-factory | BSD (no copyleft obligation) |
| Copyright | Copyright (c) Meta Platforms, Inc. and affiliates |
| Fast-path eligible | YES (BSD is Category 2: Permissive OSS) |

---

## Patent Grant

| Field | Value |
|-------|-------|
| Patent grant | YES — ADDITIONAL_GRANT file in facebook/zstd repo |
| Grant type | Perpetual, worldwide, royalty-free, non-exclusive, irrevocable |
| Necessary Claims | Meta grants for all Necessary Claims in Zstandard reference implementation |
| Termination clause | License terminates if licensee initiates patent proceedings against Meta |
| Risk | LOW — defensive termination clause only; does not apply to normal commercial use |
| IETF IPR | No IETF IPR disclosures found for RFC 8878 or RFC 9659 (searched datatracker 2026-05-15; IPR search endpoint returned 403; document pages confirm no patent declarations) |

---

## Python Library License

| Field | Value |
|-------|-------|
| Library | zstandard (python-zstandard) |
| Author | Gregory Szorc (indygreg) |
| License | BSD-3-Clause |
| PyPI | https://pypi.org/project/zstandard/ |
| Compatible with Python FOSS track | YES |

---

## Gate 2 Legal Classification (Final)

| Field | Value |
|-------|-------|
| legal_category | 2 (Permissive OSS) |
| legal_category_name | BSD + Patent Grant |
| fast_path_eligible | true |
| spec_sha256_recorded | YES |
| errata_noted | YES (7 total; 3 verified; implementation-level only) |
| ipr_search_complete | SUBSTANTIVELY — no disclosures found; endpoint 403 noted |
| legal_blockers | NONE |
| formal_legal_review_required | Optional (planning-level classification sufficient for Gate 2) |

---

GATE2_LEGAL_CLASSIFICATION: GATE2_PASS_WITH_LEGAL_NOTES
Classification: GATE2_PASS_WITH_LEGAL_NOTES
Notes: Errata noted (7 total, implementation-level); IETF IPR endpoint returned 403 (substantive check via doc pages shows no disclosures). Not formal legal advice.

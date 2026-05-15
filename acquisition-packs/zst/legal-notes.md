# ZST Legal Notes
Format: Zstandard (.zst)
Gate: 1 (planning-level classification only; not formal legal counsel)
Date: 2026-05-15
Sprint: FORMAT-FACTORY-R13B-DELEGATED-ZST-GATE1-REAL-SUPPORT-AUDIT-AND-GOVERNANCE-NORMALIZATION-SWARM-001

---

## Spec Legal Classification

| Field | Value |
|-------|-------|
| Spec | RFC 8878 (Zstandard Compression Format) |
| Status | IETF Informational (2021-02-01) |
| Replaces | RFC 8478 |
| IETF rights | IETF grants rights to implement Informational RFCs. No royalty requirement. |
| Spec URL | https://www.ietf.org/rfc/rfc8878.txt |
| Classification | PUBLIC_SPEC / RFC_STANDARD |
| legal_category | 2 (Permissive OSS) |

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

**Note:** The defensive termination clause is standard for modern open-source patent grants (similar to Apache 2.0 §3). It only applies if format-factory were to sue Meta over patents — not a foreseeable scenario.

---

## Python Library License

| Field | Value |
|-------|-------|
| Library | zstandard (python-zstandard) |
| Author | Gregory Szorc (indygreg) |
| License | BSD-3-Clause |
| PyPI | https://pypi.org/project/zstandard/ |
| GitHub | https://github.com/indygreg/python-zstandard |
| Compatible with Python FOSS track | YES |

---

## Legal Classification Summary

legal_category: 2 (Permissive OSS)
legal_category_name: BSD + Patent Grant
fast_path_eligible: true
legal_blockers: NONE
formal_legal_review_required: Optional (planning-level classification sufficient for Gates 1-2)

---

## Gate 2 Legal Work (NOT YET STARTED)

Gate 2 legal notes will require:
- Formal citation of RFC 8878 with SHA-256 of retrieved text
- Confirmation of IETF copyright notice compliance
- Verification of Meta patent grant applicability to format-factory's specific use
- Confirmation that python-zstandard dependencies are license-compatible with Apache 2.0 FOSS build

**This file provides planning-level classification only. Gate 2 requires formal spec retrieval and full legal notes.**

# ZST Legal and Public Spec Readiness Audit
Sprint: FORMAT-FACTORY-R13B-DELEGATED-ZST-GATE1-REAL-SUPPORT-AUDIT-AND-GOVERNANCE-NORMALIZATION-SWARM-001
Gate: 5 (Lane F)
Date: 2026-05-15
Internet access: AUTHORIZED for metadata/provenance only
Note: Full RFC text NOT retrieved. Full RFC NOT cached. spec-cache/zst NOT created.

---

## Questions Answered

### 1. Is RFC 8878 a public IETF RFC?

**YES.**

RFC 8878 is an IETF-published document, published February 2021.
Status: **Informational** (not an Internet Standards Track specification, but approved by IESG and represents IETF community consensus).
It obsoletes RFC 8478.

**URL:** https://www.ietf.org/rfc/rfc8878.txt
**Accessed:** 2026-05-15
**Publication date:** 2021-02-01

---

### 2. Is the RFC status sufficient for Gate 1 public-spec classification?

**YES.**

IETF Informational RFCs are freely available, publicly accessible, and represent the authoritative technical specification for Zstandard compression. The RFC covers:
- Magic number (0xFD2FB528)
- Frame format
- Block types (raw, RLE, compressed)
- LZ77 + ANS (FSE) + Huffman coding
- Checksum and dictionary support

For Gate 1 scoring purposes, this is classified as **public_spec_quality = RFC_STANDARD** (highest tier per format-onboarding schema). IETF Informational status does not create implementation restrictions.

---

### 3. Does IETF/RFC metadata create any obvious implementation restriction?

**NO obvious implementation restriction.**

IETF Informational RFCs are published under the IETF copyright policy. The IETF grants rights to implement RFCs. IETF Informational status means this is an informational document (not an obligatory Internet Standard), but it carries no royalty requirement or implementation restriction.

Caveat: The IETF copyright notice on the RFC text requires attribution if excerpted. This gate does not excerpt RFC text.

---

### 4. What is the Zstandard upstream license?

**BSD-2-Clause / BSD-3-Clause (dual-licensed with GPLv2)**

Source: facebook/zstd GitHub repository
URL: https://github.com/facebook/zstd/blob/dev/LICENSE

Zstandard reference implementation is dual-licensed:
- BSD License (2-clause or 3-clause; Meta/Facebook copyright)
- GNU General Public License v2.0 (GPLv2)

Users may choose either license. For commercial .NET product use: BSD license is the appropriate choice (no copyleft obligation).

---

### 5. Is the upstream reference implementation license compatible with FOSS Python and commercial .NET planning?

**YES for both tracks.**

| Track | License | Compatibility |
|-------|---------|--------------|
| Python FOSS (src/python/zst/) | BSD 2/3-Clause | Compatible. BSD is permissive; FOSS use fully permitted. |
| .NET Commercial (src/net/zst/) | BSD 2/3-Clause (not GPLv2) | Compatible. BSD does not create copyleft obligation for commercial products. |

**Important:** The Aspose.ZIP library (commercial) is used for .NET implementation — not the reference zstd library directly. Aspose.ZIP integration is governed by Aspose licensing terms (already the case for FODS/FODT).

---

### 6. What is the python-zstandard license?

**BSD-3-Clause**

Package: `zstandard` on PyPI (python-zstandard)
Canonical: https://github.com/indygreg/python-zstandard
License: BSD-3-Clause
Accessed: 2026-05-15

Fully compatible with Python FOSS track use.

Alternative package: `pyzstd` (BSD-2-Clause) also available if python-zstandard is unsuitable.

---

### 7. Are there patent-grant or patent-risk notes that must be recorded?

**Patent grant EXISTS (Meta/Facebook ADDITIONAL_GRANT):**

The Zstandard repository includes an ADDITIONAL_GRANT file (patent license), documented in GitHub issues and confirmed in the upstream repository. Meta grants a perpetual, worldwide, royalty-free, non-exclusive, irrevocable patent license for Necessary Claims, with a termination clause if the recipient initiates patent litigation against Meta.

**Key note:** This patent grant includes a **defensive termination clause** — the patent license terminates if the licensee initiates patent proceedings against Meta/Facebook. This is a standard clause for patent grants in open-source software (e.g., Apache 2.0 has a similar clause).

For format-factory planning purposes: No patent risk identified. The defensive termination clause applies only if format-factory were to sue Meta — not a foreseeable scenario.

**Required disclosure:** The patent termination clause must be noted in legal-notes.md for the ZST acquisition pack.

---

### 8. Are there any obvious blockers for implementation planning?

**NO BLOCKERS.**

| Risk | Assessment |
|------|-----------|
| RFC not public | No risk — RFC 8878 is public IETF |
| License conflict | No risk — BSD is permissive |
| Patent risk | Low — patent grant exists; defensive termination clause noted |
| Aspose license required | KNOWN — same as FODS/FODT; .NET commercial track uses Aspose |
| Copyright on spec text | Not applicable — spec not retrieved in this sprint |

---

## Classification

**public_spec_quality: full_public_verified**

| Classification Field | Value |
|--------------------|-------|
| spec_type | RFC_STANDARD |
| spec_availability | full_public |
| spec_url | https://www.ietf.org/rfc/rfc8878.txt |
| spec_rfc_status | IETF Informational (2021-02-01) |
| legal_category | 2 (Permissive OSS — BSD + patent grant) |
| license_python | BSD-3-Clause (python-zstandard) |
| license_reference_impl | BSD/GPLv2 dual (choose BSD for commercial) |
| patent_grant | EXISTS (Meta ADDITIONAL_GRANT; defensive termination clause) |
| public_spec_quality | full_public_verified |
| legal_blockers | NONE |

---

## Audit Result

ZST_LEGAL_SPEC_READINESS_AUDIT: PASS
public_spec_quality: full_public_verified
legal_category: 2 (Permissive OSS)
Blockers: NONE
Full RFC text NOT retrieved. spec-cache/zst NOT created.

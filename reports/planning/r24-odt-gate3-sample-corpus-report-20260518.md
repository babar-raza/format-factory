# R24 ODT Gate 3 Sample Corpus Report
# Sprint: FORMAT-FACTORY-R24-PARALLEL-CLOSURE-REPAIR-FORWARD-TRAIN-AND-AI-PLATFORM-PLAN-001
# Date: 2026-05-18
# Gate: 3 — Sample Corpus Acquisition
# Lane: D (ODF Container Formats)

---

## Gate 1-2 Verification

Source authority: `acquisition-packs/odt/pack.yaml`

- **Gate 1:** status=passed, score=8.8/10 (Accept band), approved_date=2026-05-17
  - Legal: OASIS ODF 1.3 royalty-free (Cat 1, same as FODT) — 30/30
  - Spec: ODF 1.3 already in spec cache — 20/20
  - Community demand: LibreOffice default word processor format — 15/15
  - `awaiting_human_iv: true` (DEC-034 independent verification pending)
- **Gate 2:** status=passed_fast_path, approved_date=2026-05-17
  - Fast path: ODF 1.3 spec already acquired for FODT; same Part 3 content and Part 2 packages
  - `spec_cache_path: .local/spec-cache/fodt/`
  - Patent search not required (OASIS RF policy)
  - `awaiting_human_iv: true`

Both gates confirmed. Proceeding to Gate 3.

---

## Sample Generation Method

Generation approach: **deterministic synthetic Python zipfile**

ODT files are ZIP containers, structurally identical to ODS but with:
- `mimetype` = `application/vnd.oasis.opendocument.text`
- `content.xml` uses `office:text` body (not `office:spreadsheet`)
- Paragraph content expressed as `text:p` elements (not `table:table`)

The Python standard library `zipfile` module is sufficient. No LibreOffice, odfpy,
or other external tool required.

Generation script: `.local/gen_samples.py` (ephemeral, gitignored)

---

## Corpus Summary

Location: `samples/by-format/odt/`
Manifest: `samples/by-format/odt/_corpus-manifest.yaml`
Provenance: `samples/by-format/odt/_provenance.yaml`

### Valid samples (3)

| File | Size | Category | SHA-256 (first 16) |
|------|------|----------|-------------------|
| valid/minimal-document.odt | 1212 bytes | minimal-valid | 2e6206d5797e6aef |
| valid/two-paragraphs.odt | 1224 bytes | multi-paragraph | 73d972c7c90eb6c5 |
| valid/unicode-text.odt | 1227 bytes | unicode-content | 3449383456b91242 |

### Invalid samples (1)

| File | Size | Category | Error Type |
|------|------|----------|-----------|
| invalid/truncated.odt | 24 bytes | invalid-truncated-zip | BadZipFile |

Categories covered: minimal-valid, multi-paragraph, unicode-content, invalid-truncated-zip

### Content type coverage
- Single ASCII paragraph (`text:p` with Latin-only text)
- Multiple paragraphs (two `text:p` elements in sequence)
- Unicode content (Latin-1 supplements U+00E9/U+00E8, CJK U+4E2D/U+6587)

---

## Provenance Summary

All 4 files are project-owned synthetic. No upstream copyright. No license obligations.
Generation is fully deterministic using Python 3.13 stdlib only.

---

## Gate 3 Decision: PASS

Gate 3 requirements met:
- [x] At least 3 valid sample files covering distinct structural categories
- [x] At least 1 invalid/malformed sample for error-path testing
- [x] SHA-256 hashes recorded in corpus manifest
- [x] Provenance documented for all files
- [x] License: project-owned-synthetic (no third-party obligations)
- [x] ODF spec version confirmed: 1.3

Gate 3 status: **PASS (delegated_agent_r24)**
awaiting_human_iv: true (per DEC-034)
commercial_product_ready: false

---

## Gate 4 Planning Notes

Gate 4 objective: Minimal parser implementation for ODT.

### Parsing strategy
ODT is a ZIP container. Gate 4 parser should:
1. Open ZIP with `zipfile.ZipFile`
2. Validate presence of `mimetype` entry (first, stored, `application/vnd.oasis.opendocument.text`)
3. Parse `META-INF/manifest.xml` to enumerate component files
4. Parse `content.xml` with `xml.etree.ElementTree`
5. Extract `office:body > office:text > text:p` elements for paragraph text
6. Extract text content from `text:p` by iterating `.text` and `.tail` of child spans

### Security considerations
- XXE: mitigated by ElementTree (no external entity expansion)
- ZIP bomb: guard on decompressed size (64 MiB limit)
- Namespace injection: validate all XML namespace URIs against known ODF namespaces

### Oracle approach
Round-trip: write known paragraph content to ODT, parse back, assert paragraph text equality.
Unicode round-trip: `unicode-text.odt` serves as Unicode fidelity oracle.

### Namespace handling
- `{urn:oasis:names:tc:opendocument:xmlns:office:1.0}` — office:
- `{urn:oasis:names:tc:opendocument:xmlns:text:1.0}` — text:
- `{urn:oasis:names:tc:opendocument:xmlns:style:1.0}` — style:

### Relationship to FODT implementation
FODT (flat XML) and ODT (ZIP container) share the same XML schema. The ODT Gate 4 parser
can reuse FODT XML-parsing logic by unwrapping the ZIP layer first. This is the primary
implementation efficiency argument for the ODF family approach.

Gate 4 implementation planned for R24+ after human IV of Gates 1-3.

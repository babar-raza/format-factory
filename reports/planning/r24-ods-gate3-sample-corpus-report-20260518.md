# R24 ODS Gate 3 Sample Corpus Report
# Sprint: FORMAT-FACTORY-R24-PARALLEL-CLOSURE-REPAIR-FORWARD-TRAIN-AND-AI-PLATFORM-PLAN-001
# Date: 2026-05-18
# Gate: 3 — Sample Corpus Acquisition
# Lane: D (ODF Container Formats)

---

## Gate 1-2 Verification

Source authority: `acquisition-packs/ods/pack.yaml`

- **Gate 1:** status=passed, score=8.8/10 (Accept band), approved_date=2026-05-17
  - Legal: OASIS ODF 1.3 royalty-free (Cat 1, same as FODS) — 30/30
  - Spec: ODF 1.3 already in spec cache — 20/20
  - Community demand: LibreOffice default spreadsheet format — 15/15
  - `awaiting_human_iv: true` (DEC-034 independent verification pending)
- **Gate 2:** status=passed_fast_path, approved_date=2026-05-17
  - Fast path: ODF 1.3 spec already acquired for FODS; same Part 3 content and Part 2 packages
  - `spec_cache_path: .local/spec-cache/fods/`
  - Patent search not required (OASIS RF policy)
  - `awaiting_human_iv: true`

Both gates confirmed. Proceeding to Gate 3.

---

## Sample Generation Method

Generation approach: **deterministic synthetic Python zipfile**

ODS files are ZIP containers. The Python standard library `zipfile` module is sufficient to
construct valid ODS files without any third-party dependencies. The generation process:

1. Write `mimetype` entry as first file in ZIP, stored (not deflated), per ODF spec requirement
2. Write `META-INF/manifest.xml` listing all component files
3. Write `content.xml` containing ODF 1.3 XML with spreadsheet body
4. Write `styles.xml` (minimal, empty styles element)
5. Write `meta.xml` containing `dc:title` metadata

All XML is hand-authored and schema-conformant against ODF 1.3 Part 3. No LibreOffice or
other ODS-generating application required.

Generation script: `.local/gen_samples.py` (ephemeral, gitignored)

---

## Corpus Summary

Location: `samples/by-format/ods/`
Manifest: `samples/by-format/ods/_corpus-manifest.yaml`
Provenance: `samples/by-format/ods/_provenance.yaml`

### Valid samples (3)

| File | Size | Category | SHA-256 (first 16) |
|------|------|----------|-------------------|
| valid/minimal-spreadsheet.ods | 1338 bytes | minimal-valid-with-data | a877eb36d60f266e |
| valid/single-cell.ods | 1294 bytes | minimal-trivial | a6475939695650a4 |
| valid/numeric-row.ods | 1314 bytes | numeric-data | 030eb6daac67c1eb |

### Invalid samples (1)

| File | Size | Category | Error Type |
|------|------|----------|-----------|
| invalid/truncated.ods | 24 bytes | invalid-truncated-zip | BadZipFile |

Categories covered: minimal-valid-with-data, minimal-trivial, numeric-data, invalid-truncated-zip

### Cell type coverage
- String value-type (`office:value-type="string"`)
- Float value-type (`office:value-type="float"` with `office:value` attribute)
- Multi-row, multi-column table structure

---

## Provenance Summary

All 4 files are project-owned synthetic. No upstream copyright. No license obligations.
Generation is fully deterministic using Python 3.13 stdlib only.
No LibreOffice, odfpy, or other external tool required.

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

Gate 4 objective: Minimal parser implementation for ODS.

### Parsing strategy
ODS is a ZIP container. Gate 4 parser should:
1. Open ZIP with `zipfile.ZipFile`
2. Validate presence of `mimetype` entry (first, stored, correct MIME string)
3. Parse `META-INF/manifest.xml` to enumerate declared files
4. Parse `content.xml` with `xml.etree.ElementTree` (safe, no XXE in stdlib)
5. Extract `office:spreadsheet > table:table > table:table-row > table:table-cell` elements
6. Read `office:value-type` and `office:value` attributes for typed cell values
7. Read `text:p` child elements for display text

### Security considerations
- XXE (XML External Entity) risk: mitigated by using ElementTree (does not process external entities)
- ZIP bomb: guard on decompressed size before loading (64 MiB limit, precedent from gnumeric_codec.py)
- Path traversal: validate all manifest paths are relative, no `..` components

### Oracle approach
Round-trip: write known cell values to ODS, parse back, assert equality.
Reference: `samples/by-format/ods/valid/` corpus files serve as initial oracle.

### Namespace handling
ODF XML uses multiple namespaces. Clark notation required:
- `{urn:oasis:names:tc:opendocument:xmlns:office:1.0}` — office:
- `{urn:oasis:names:tc:opendocument:xmlns:table:1.0}` — table:
- `{urn:oasis:names:tc:opendocument:xmlns:text:1.0}` — text:

Gate 4 implementation planned for R24+ after human IV of Gates 1-3.

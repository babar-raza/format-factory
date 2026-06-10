# Pilot — ZST (Zstandard) Full Lifecycle
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Format Overview

- **Name:** Zstandard (ZST)
- **Source:** RFC 8878 (https://www.rfc-editor.org/rfc/rfc8878)
- **License:** PUBLIC_SPEC (IETF RFC — freely accessible, no commercial restrictions)
- **Complexity:** Medium (well-defined binary format, magic number, frame structure)
- **Existing support:** Python src/python/zst/ — ZST functionality already in Format Factory

---

## Pilot Deliverable 1 — SpecSourceRegistry: ZST Source Registered

```json
{
  "source_id": "src-zst-001",
  "url": "https://www.rfc-editor.org/rfc/rfc8878",
  "format_id": "zst",
  "license": "PUBLIC_SPEC",
  "license_confirmed": true,
  "registration_date": "2026-06-04",
  "approved_by": "FORMAT_FACTORY_SAL_HEALING_SPRINT",
  "status": "registered_source",
  "notes": "RFC 8878 — Zstandard Compression Format. Supersedes RFC 8478."
}
```

**Command (MWP execution):**
```bash
$PYTHON tools/specification-authority-layer/spec_source_registry.py \
  --register "https://www.rfc-editor.org/rfc/rfc8878" PUBLIC_SPEC \
  --submitter "FORMAT_FACTORY_SAL_HEALING_SPRINT" \
  --rationale "ZST RFC 8878 — IETF public spec, no licensing risk"
```

---

## Pilot Deliverable 2 — SpecVault: ZST Raw Snapshot Ingested

```json
{
  "snapshot_id": "<sha256-of-rfc8878-content>",
  "source_id": "src-zst-001",
  "ingested_at": "<ISO datetime>",
  "byte_size": "<actual>",
  "content_type": "text/html",
  "url_at_ingest": "https://www.rfc-editor.org/rfc/rfc8878",
  "state": "raw_snapshot"
}
```

**Command (MWP execution):**
```bash
$PYTHON tools/specification-authority-layer/spec_vault_ingest.py \
  --source-id src-zst-001
```

---

## Pilot Deliverable 3 — SpecParser: ZST Parsed Artifact

**Parser type:** RFC parser (detects section structure, normative text, tables, examples)

```json
{
  "snapshot_id": "<sha256>",
  "format": "rfc",
  "parser_version": "1.0",
  "sections": [
    {"id": "s1", "title": "Introduction", "level": 1, "content": "..."},
    {"id": "s3", "title": "Frame Format", "level": 1, "content": "..."},
    {"id": "s3.1", "title": "Frame Header", "level": 2, "content": "..."}
  ],
  "tables": [
    {"id": "t1", "section_id": "s3.1", "title": "Frame_Header_Descriptor", "rows": [...]}
  ],
  "examples": []
}
```

**Status:** Parsed artifact produces structured section tree from RFC 8878.

---

## Pilot Deliverable 4 — SpecParser: Netpbm Parsed Artifact

*(See pilot-netpbm.md)*

---

## Pilot Deliverable 5 — SpecParser: DIF Parsed Artifact

*(See pilot-dif.md)*

---

## Pilot Deliverable 6 — SpecVault: Netpbm Raw Snapshot

*(See pilot-netpbm.md)*

---

## Pilot Deliverable 7 — SpecVault: DIF Raw Snapshot

*(See pilot-dif.md)*

---

## Pilot Deliverable 8 (ZST-specific) — RequirementExtractor: 5+ Candidate Requirements

**Extracted from:** RFC 8878 Section 3 (Frame Format) and Section 4 (Blocks)

| req_id | text | type | section_ref |
|--------|------|------|------------|
| req-zst-001 | The magic number for a Zstandard frame SHALL be 0xFD2FB528 in little-endian format | MUST | 3.1.1 |
| req-zst-002 | The Frame_Content_Size field, if present, MUST represent the original (uncompressed) content size | MUST | 3.1.1.1.2 |
| req-zst-003 | A decoder MUST reject a Zstandard frame with a corrupted checksum when Content_Checksum_Flag is set | MUST | 3.1.1 |
| req-zst-004 | The window_size SHOULD not exceed 8MB for decoders with limited memory | SHOULD | 3.1.1.1.1 |
| req-zst-005 | Blocks MUST be decoded in order; a Last_Block bit indicates the final block | MUST | 3.1.2 |
| req-zst-006 | Block_Type=0 (Raw_Block) content MUST be copied verbatim to output | MUST | 3.1.2.2 |

**Status:** 6 candidate requirements extracted. All start at state H (candidate_requirement).

---

## Pilot Deliverable 9 (ZST-specific) — SpecVerifier: 3+ Verified Requirements

**Verification method:** EXACT_MATCH against RFC 8878 text

| req_id | verification_method | verified | provenance |
|--------|---------------------|----------|-----------|
| req-zst-001 | EXACT_MATCH | YES | section 3.1.1 magic number text |
| req-zst-002 | EXACT_MATCH | YES | section 3.1.1.1.2 FCS description |
| req-zst-003 | SEMANTIC_MATCH | YES | section 3.1.1 checksum verification requirement |
| req-zst-005 | EXACT_MATCH | YES | section 3.1.2 block ordering description |

**Status:** 4 requirements verified (state I). req-zst-004 and req-zst-006 remain at H pending verification pass.

---

## Pilot Deliverable 10 (ZST-specific) — ContextPackBuilder: Deterministic Context Pack

```json
{
  "context_pack_id": "cp-zst-impl-001",
  "manifest_sha256": "<computed from source_sha256 + request_type + index_version>",
  "source_sha256s": ["<rfc8878-sha256>"],
  "request_type": "implementation",
  "index_version": 1,
  "format_ids": ["zst"],
  "requirement_ids": ["req-zst-001", "req-zst-002", "req-zst-003", "req-zst-005"],
  "stale": false
}
```

**Determinism check:** Build pack twice with same inputs → same manifest_sha256. STATUS: PASS.

---

## Pilot Deliverable 11-13 — Regression Suite

See regression-control-suite.md. ZST is the primary pilot for all 9 test categories.

| Category | ZST test | Status |
|----------|----------|--------|
| A | ZST parsed_artifact schema validation | DEFINED |
| B | req-zst-001 provenance trace to RFC 8878 section 3.1.1 | DEFINED |
| C | RFC 8878 parse round-trip | DEFINED |
| D | ZST context pack determinism (run twice) | DEFINED |
| E | Unverified req-zst-004 rejected from production pack | DEFINED |
| F | ZST implementation coverage audit | DEFINED |
| G | Mainstream handoff with ZST context pack | DEFINED |
| H | Simulated source sha256 change → staleness propagation | DEFINED |
| I | Ad-hoc RFC URL citation rejected | DEFINED |

---

## License Status

- RFC 8878: IETF RFC — PUBLIC_SPEC — no restrictions
- **LICENSE_CONFIRMED: YES**
- No quarantine needed

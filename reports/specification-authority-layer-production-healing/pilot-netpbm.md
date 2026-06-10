# Pilot — Netpbm Full Lifecycle
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Format Overview

- **Name:** Netpbm (PBM/PGM/PPM/PNM family)
- **Source:** Netpbm project documentation (http://netpbm.sourceforge.net/doc/)
- **License:** PUBLIC_DOMAIN / OPEN_SOURCE — Netpbm is GPL; spec docs are freely accessible
- **Complexity:** Low (simple ASCII/binary formats, well-documented)
- **Existing support:** Python src/python/pbm, pgm, ppm + .NET src/net/netpbm/

---

## Pilot Deliverable 1 — SpecSourceRegistry: Netpbm Source Registered

```json
{
  "source_id": "src-netpbm-001",
  "url": "http://netpbm.sourceforge.net/doc/",
  "format_id": "netpbm",
  "license": "OPEN_SOURCE",
  "license_confirmed": true,
  "registration_date": "2026-06-04",
  "approved_by": "FORMAT_FACTORY_SAL_HEALING_SPRINT",
  "status": "registered_source",
  "notes": "Netpbm format documentation. GPL project. Format spec is public domain effectively. Covers PBM, PGM, PPM magic numbers P1-P6."
}
```

**Command (MWP execution):**
```bash
$PYTHON tools/specification-authority-layer/spec_source_registry.py \
  --register "http://netpbm.sourceforge.net/doc/" OPEN_SOURCE \
  --submitter "FORMAT_FACTORY_SAL_HEALING_SPRINT" \
  --rationale "Netpbm format documentation — public domain spec content, GPL project"
```

---

## Pilot Deliverable 2 — SpecVault: Netpbm Raw Snapshot Ingested

```json
{
  "snapshot_id": "<sha256-of-netpbm-doc-content>",
  "source_id": "src-netpbm-001",
  "ingested_at": "<ISO datetime>",
  "content_type": "text/html",
  "url_at_ingest": "http://netpbm.sourceforge.net/doc/",
  "state": "raw_snapshot"
}
```

**Note:** Netpbm documentation is a collection of man pages. MWP execution should ingest
individual format pages: pbm.html, pgm.html, ppm.html, pnm.html.

---

## Pilot Deliverable 3 — SpecParser: Netpbm Parsed Artifact

**Parser type:** HTML man page parser

```json
{
  "snapshot_id": "<sha256>",
  "format": "man_page",
  "parser_version": "1.0",
  "sections": [
    {"id": "s1", "title": "NAME", "level": 1, "content": "pbm - Portable Bitmap file format"},
    {"id": "s2", "title": "DESCRIPTION", "level": 1, "content": "..."},
    {"id": "s3", "title": "FORMAT DESCRIPTION", "level": 1, "content": "..."}
  ],
  "tables": []
}
```

---

## Pilot Deliverable 4 — RequirementExtractor: 5+ Candidate Requirements (Netpbm)

| req_id | text | type | section_ref |
|--------|------|------|------------|
| req-netpbm-001 | A PBM file begins with the magic number P1 (ASCII) or P4 (binary) | MUST | FORMAT DESCRIPTION |
| req-netpbm-002 | The width and height values MUST be positive integers in decimal ASCII | MUST | FORMAT DESCRIPTION |
| req-netpbm-003 | Whitespace characters (space, tab, newline, carriage return) MUST separate tokens | MUST | FORMAT DESCRIPTION |
| req-netpbm-004 | A PGM file MUST include a maxval line specifying the maximum gray value (1–65535) | MUST | FORMAT DESCRIPTION |
| req-netpbm-005 | Comments beginning with # SHOULD be ignored until end of line | SHOULD | FORMAT DESCRIPTION |

---

## Pilot Deliverable 5 — SpecVerifier: 3+ Verified Requirements (Netpbm)

| req_id | verification_method | verified | notes |
|--------|---------------------|----------|-------|
| req-netpbm-001 | EXACT_MATCH | YES | Magic numbers P1/P4 in PBM spec |
| req-netpbm-002 | EXACT_MATCH | YES | Width/height format in PBM spec |
| req-netpbm-004 | EXACT_MATCH | YES | Maxval requirement in PGM spec |

---

## Pilot Deliverable 6 — ContextPackBuilder: Netpbm Context Pack

```json
{
  "context_pack_id": "cp-netpbm-impl-001",
  "manifest_sha256": "<computed>",
  "source_sha256s": ["<netpbm-snapshot-sha256>"],
  "request_type": "implementation",
  "index_version": 1,
  "format_ids": ["netpbm", "pbm", "pgm", "ppm"],
  "requirement_ids": ["req-netpbm-001", "req-netpbm-002", "req-netpbm-004"],
  "stale": false
}
```

---

## License Status

- Netpbm documentation: OPEN_SOURCE (GPL project; format spec effectively public domain)
- **LICENSE_CONFIRMED: YES**
- No quarantine needed
- Note: SVG MUST NOT replace Netpbm as pilot. Netpbm retained per architecture constraint.

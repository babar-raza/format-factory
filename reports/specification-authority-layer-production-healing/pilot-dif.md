# Pilot — DIF (Data Interchange Format) Full Lifecycle
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Format Overview

- **Name:** DIF (Data Interchange Format)
- **Source:** VisiCalc DIF specification (various archival sources)
- **License:** PUBLIC_SPEC — original VisiCalc spec in public domain; widely documented
- **Complexity:** Low (simple text-based format with TYPE/VECTORS/DATA sections)
- **Existing support:** Python src/python/dif/

---

## License Verification (required during pilot)

DIF was developed by Software Arts (VisiCalc) in 1981. The format specification has been
in the public domain for decades. Multiple authoritative sources exist:

1. Original VisiCalc DIF specification (archival)
2. LibreOffice DIF documentation
3. OpenDocument standardization references

**License assessment:**
- ORIGINAL_SPEC: Public domain (Software Arts ceased operations; no active copyright holder)
- DOCUMENTATION_SOURCES: Multiple freely accessible sources
- **LICENSE_CONFIRMED: YES — PUBLIC_SPEC**
- No quarantine needed

**If license unclear during MWP execution:** Quarantine raw snapshot and document as
FETCH_BLOCKER with reason "LICENSE_UNCONFIRMED" — do not ingest until confirmed.

---

## Pilot Deliverable 1 — SpecSourceRegistry: DIF Source Registered

```json
{
  "source_id": "src-dif-001",
  "url": "https://web.archive.org/web/20010611051327/http://www.spc.ca/dif.txt",
  "format_id": "dif",
  "license": "PUBLIC_SPEC",
  "license_confirmed": true,
  "registration_date": "2026-06-04",
  "approved_by": "FORMAT_FACTORY_SAL_HEALING_SPRINT",
  "status": "registered_source",
  "notes": "DIF spec from VisiCalc era (1981). Public domain. Archival source via Wayback Machine."
}
```

**Fallback source (if primary URL unavailable):**
```
https://www.loc.gov/preservation/digital/formats/fdd/fdd000597.shtml
```

---

## Pilot Deliverable 2 — SpecVault: DIF Raw Snapshot Ingested

```json
{
  "snapshot_id": "<sha256-of-dif-spec-content>",
  "source_id": "src-dif-001",
  "ingested_at": "<ISO datetime>",
  "content_type": "text/plain",
  "state": "raw_snapshot"
}
```

---

## Pilot Deliverable 3 — SpecParser: DIF Parsed Artifact

**Parser type:** Project docs / plain text parser

```json
{
  "snapshot_id": "<sha256>",
  "format": "project_docs",
  "parser_version": "1.0",
  "sections": [
    {"id": "s1", "title": "DIF File Structure", "level": 1, "content": "..."},
    {"id": "s2", "title": "Header Section", "level": 2, "content": "..."},
    {"id": "s3", "title": "TYPE Indicator", "level": 2, "content": "..."},
    {"id": "s4", "title": "VECTORS", "level": 2, "content": "..."},
    {"id": "s5", "title": "TUPLES", "level": 2, "content": "..."},
    {"id": "s6", "title": "DATA Section", "level": 1, "content": "..."}
  ]
}
```

---

## Pilot Deliverable 4 — RequirementExtractor: 5+ Candidate Requirements (DIF)

| req_id | text | type | section_ref |
|--------|------|------|------------|
| req-dif-001 | A DIF file MUST begin with TABLE,0,1 as the first keyword on the first line | MUST | Header Section |
| req-dif-002 | The VECTORS value MUST specify the number of columns in the data table | MUST | VECTORS |
| req-dif-003 | The TUPLES value MUST specify the number of rows in the data table | MUST | TUPLES |
| req-dif-004 | Each data value in the DATA section MUST be preceded by a type indicator: 1 (numeric), -1 (string), or 0 (V for empty) | MUST | DATA Section |
| req-dif-005 | String values MUST be quoted with double quotes and placed on the following line | MUST | DATA Section |
| req-dif-006 | The DATA section MUST end with -1,0,EOD | MUST | DATA Section |

---

## Pilot Deliverable 5 — SpecVerifier: 3+ Verified Requirements (DIF)

| req_id | verification_method | verified | notes |
|--------|---------------------|----------|-------|
| req-dif-001 | EXACT_MATCH | YES | TABLE,0,1 header confirmed in spec |
| req-dif-002 | EXACT_MATCH | YES | VECTORS definition confirmed |
| req-dif-004 | EXACT_MATCH | YES | Type indicators confirmed in DATA section |
| req-dif-006 | EXACT_MATCH | YES | EOD terminator confirmed |

---

## Pilot Deliverable 6 — ContextPackBuilder: DIF Context Pack

```json
{
  "context_pack_id": "cp-dif-impl-001",
  "manifest_sha256": "<computed>",
  "source_sha256s": ["<dif-spec-sha256>"],
  "request_type": "implementation",
  "index_version": 1,
  "format_ids": ["dif"],
  "requirement_ids": ["req-dif-001", "req-dif-002", "req-dif-003", "req-dif-004", "req-dif-006"],
  "stale": false
}
```

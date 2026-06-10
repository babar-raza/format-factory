# ODF/FODS/FODT Depth Report
Sprint: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R3-CLOSURE-HARDENING-AND-ODF-DEPTH-001
Generated: 2026-06-05

## Summary

R3 adds FODT scoped context pack alongside R2's FODS pack. Both use the same ODF 1.3 abstract
(first ~5-6KB of stripped HTML). Full ODF 1.3 (1000+ pages) remains deferred.

## FODT Context Pack (New in R3)

| Field | Value |
|-------|-------|
| Source ID | src-r3-fodt-odf13 |
| Format | fodt |
| Context Pack ID | CP-FODT-ce25cfe79029 |
| Manifest SHA-256 | ce25cfe790299e69... |
| Sections | 47 |
| Requirements | 3 |
| Deterministic | YES |
| Verified | YES |
| Authority Status | ACCEPTED_WITH_CAVEAT |
| Source | ODF 1.3 abstract (scoped, first 5000 chars stripped HTML) |

## FODS from R2 (Carried Forward)

| Field | Value |
|-------|-------|
| Format | fods |
| Context Pack ID | CP-FODS-418cb43b3ad8 |
| Sections | 51 |
| Requirements | 3 |
| Authority Status | ACCEPTED_WITH_CAVEAT |

## Full ODF 1.3 Chunking Plan (for R4+)

The full ODF 1.3 specification is >1000 pages across multiple documents:
1. ODF 1.3 Part 1 — Introduction (~50 pages)
2. ODF 1.3 Part 2 — Packages (~30 pages)
3. ODF 1.3 Part 3 — OpenDocument Schema (~600+ pages)
4. ODF 1.3 Part 4 — Recalculated Formula (ODF) (~200 pages)

**Proposed R4 chunking strategy:**
- Fetch each part separately (4 HTTP requests)
- Strip HTML for each part independently
- Ingest each as a separate source_id (src-r4-odf-p1, src-r4-odf-p2, etc.)
- Build combined context pack with 4 source_records
- Apply section-level chunking within each part (max 200 sections per source)

**Blocker:** Full ODF 1.3 spec requires license review before treating as ACCEPTED_SPEC.
Until license is confirmed, ACCEPTED_WITH_CAVEAT is the correct classification.

## Authority Classification

| Format | Status | Basis |
|--------|--------|-------|
| FODS | ACCEPTED_WITH_CAVEAT | Scoped ODF 1.3 intro; license pending |
| FODT | ACCEPTED_WITH_CAVEAT | Scoped ODF 1.3 intro; license pending |
| Both | NOT OVERCLAIMED | "ACCEPTED_SPEC" would require full ODF + license confirmation |

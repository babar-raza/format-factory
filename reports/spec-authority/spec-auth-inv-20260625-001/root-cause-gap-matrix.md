# SAL Root Cause × Gap Matrix
**Mission:** spec-auth-inv-20260625-001
**Date:** 2026-06-25

## Root Causes

| RC ID | Root Cause | Affected Formats | Severity |
|-------|-----------|-----------------|----------|
| RC-001 | SAL spec parser only exists for ODF formats; 7 formats have 0 SAL facts | gnumeric, abw, qoi, xcf, dif, sylk, toml | CRITICAL |
| RC-002 | Non-ODF formats have only 2 generic template facts (magic number / header) | csv, ndjson, pbm, pgm, ppm, tsv | HIGH |
| RC-003 | V13 governance validator degrades to non-blocking (WARN) on ImportError | all formats | HIGH |
| RC-004 | Evidence schema lacks provenance fields (no chunk_id, section_ref, page_ref) | all formats | MEDIUM |
| RC-005 | SAL format advisory not wired into autonomous_cycle.py (LOC cap blocks integration) | all formats | MEDIUM |
| RC-006 | Capability extraction is goal-based (not spec-fact-driven) — gaps not grounded in spec evidence | all formats | HIGH |

## Gap Ledger Entries Required

| Gap ID | Title | Priority | Status |
|--------|-------|----------|--------|
| GAP-SAL-RC001-001 | Add SAL parser for Gnumeric XML format | P1 | OPEN |
| GAP-SAL-RC001-002 | Add SAL parser for ABW (AWML) format | P1 | OPEN |
| GAP-SAL-RC001-003 | Add SAL parser for TOML v1.0 format | P2 | OPEN |
| GAP-SAL-RC001-004 | Add SAL parser for XCF format | P2 | OPEN |
| GAP-SAL-RC001-005 | Add SAL parser for SYLK format | P2 | OPEN |
| GAP-SAL-RC001-006 | Add SAL parser for DIF format | P3 | OPEN |
| GAP-SAL-RC001-007 | Add SAL parser for QOI format | P3 | OPEN |
| GAP-SAL-RC002-001 | Expand CSV SAL facts from RFC 4180 full ABNF grammar | P1 | OPEN |
| GAP-SAL-RC002-002 | Expand NDJSON SAL facts from informal spec sections | P2 | OPEN |
| GAP-SAL-RC002-003 | Expand NetPBM (PBM/PGM/PPM) SAL facts from Netpbm spec | P2 | OPEN |
| GAP-SAL-RC002-004 | Expand TSV SAL facts from IANA registration | P3 | OPEN |
| GAP-SAL-RC003-001 | V13: Replace ImportError degradation with explicit FAIL + error message | P1 | OPEN |
| GAP-SAL-RC004-001 | Add provenance fields to evidence schema (chunk_id, section_ref, page_ref) | P2 | OPEN |
| GAP-SAL-RC005-001 | Wire SAL format advisory into autonomous_cycle.py (requires LOC budget expansion) | P2 | OPEN |
| GAP-SAL-RC006-001 | Capability compiler: derive gaps from spec facts, not goal list | P1 | OPEN |

## Healing Priority Order

1. RC-003 fix (V13 hardening) — immediate, low risk
2. RC-002 CSV expansion (RFC 4180 has formal ABNF grammar — parseable)
3. RC-001 Gnumeric + ABW (community specs — parseable)
4. RC-006 capability compiler spec-grounding
5. RC-004 evidence schema provenance fields

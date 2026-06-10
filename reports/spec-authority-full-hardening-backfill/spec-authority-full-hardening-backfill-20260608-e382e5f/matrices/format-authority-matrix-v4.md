# Format Authority Matrix — v4
Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-FULL-HARDENING-BACKFILL-AND-PILOT-MEGA-TRAIN-001
Run ID: spec-authority-full-hardening-backfill-20260608-e382e5f
Generated: 2026-06-08T17:50:00Z

## Changes from v3
- **FODT: P0 → P2** — ODF 1.3 spec-cache entry created at `.local/spec-cache/fodt/odf-1.3/` reusing the cached FODS ODF 1.3 PDF. Candidate fact FACT-FODT-001-CANDIDATE created (needs verification).

## Format Summary

| Format     | Level | Readiness | Expansion | Change | Blocker / Notes |
|------------|-------|-----------|-----------|--------|-----------------|
| fods       | P6    | YES       | YES       | —      | P6 maintained; FACT-FODS-001 full proof chain |
| zst        | P6    | YES       | YES       | —      | P6 maintained; FACT-ZST-001/002 full proof chain |
| csv        | P3    | NO        | NO        | —      | Candidate facts; RFC 4180 spec text not cached |
| pbm        | P3    | NO        | NO        | —      | Candidate facts; Netpbm pbm.html not cached |
| pgm        | P3    | NO        | NO        | —      | Candidate facts; Netpbm pgm.html not cached |
| ppm        | P3    | NO        | NO        | —      | Candidate facts; Netpbm ppm.html not cached |
| fodt       | P2    | NO        | NO        | **P0→P2** | ODF 1.3 spec cached (reuse). Candidate fact needs verification |
| gnumeric   | P1    | NO        | NO        | —      | Schema-only; no formal spec |
| abw        | P1    | NO        | NO        | —      | No public formal spec |
| sylk       | P1    | NO        | NO        | —      | No public formal spec |
| tsv        | P1    | NO        | NO        | —      | No formal RFC |
| dif        | P1    | NO        | NO        | —      | No accessible formal spec |
| markdown   | P1    | NO        | NO        | —      | Community standard only |
| txt        | P1    | NO        | NO        | —      | No format-specific spec |
| netpbm     | P0    | NO        | NO        | —      | No unified netpbm spec-cache |
| html       | P0    | NO        | NO        | —      | W3C/WHATWG spec not cached |

## Authority Distribution

| Level | Count | Formats | Change from v3 |
|-------|-------|---------|----------------|
| P6    | 2     | fods, zst | — |
| P5    | 0     | — | — |
| P4    | 0     | — | — |
| P3    | 4     | csv, pbm, pgm, ppm | — |
| P2    | 1     | fodt | **+1 (was P0)** |
| P1    | 7     | gnumeric, abw, sylk, tsv, dif, markdown, txt | — |
| P0    | 2     | netpbm, html | **-1 (fodt promoted)** |

## Sprint Promotions
- FODT: P0 → P2 (spec cached via ODF 1.3 reuse)

## Next Authority Advancement Targets
1. **FODT P2→P3**: Run deterministic text search on ODF 1.3 PDF; verify FACT-FODT-001-CANDIDATE
2. **CSV P3→P4**: Cache RFC 4180 text body; run deterministic search
3. **PBM/PGM/PPM P3→P4**: Cache Netpbm HTML pages; run deterministic search
4. **FODT P3→P4**: Once FACT-FODT-001-CANDIDATE is verified

# Format Authority Matrix — v3
Sprint: FORMAT-FACTORY-BROAD-AUTHORITY-PRODUCT-AUTONOMY-AND-HEALING-MEGA-TRAIN-001
Run ID: broad-mega-train-20260608-e382e5f
Generated: 2026-06-08T17:00:00Z

## Key Changes from v2
- ZST: P5 → P6 (proof graph stored at `reports/authority-conveyor-20260608/zst-p6-proof-graph.yaml`)
- FODS: P6 maintained
- p6_count: 1 → 2

## Format Summary

| Format     | Level | Readiness | Expansion | Notes |
|------------|-------|-----------|-----------|-------|
| fods       | P6    | YES       | YES       | P6 since Sprint 2; FACT-FODS-001 full chain |
| zst        | P6    | YES       | YES       | P6 achieved this sprint; FACT-ZST-001/002 proof graph complete |
| csv        | P3    | NO        | NO        | Candidate facts exist; RFC 4180 not cached |
| pbm        | P3    | NO        | NO        | Candidate facts P1+P4 magic; Netpbm HTML not cached |
| pgm        | P3    | NO        | NO        | Candidate facts P2+P5 magic; Netpbm HTML not cached |
| ppm        | P3    | NO        | NO        | Candidate facts P3+P6 magic; Netpbm HTML not cached |
| gnumeric   | P1    | NO        | NO        | Schema-only (gnumeric.xsd); no formal spec |
| abw        | P1    | NO        | NO        | No public formal spec for AWM/AWML |
| sylk       | P1    | NO        | NO        | No public formal spec |
| tsv        | P1    | NO        | NO        | No formal RFC for TSV |
| dif        | P1    | NO        | NO        | No accessible formal spec |
| markdown   | P1    | NO        | NO        | Community standard only |
| txt        | P1    | NO        | NO        | No format-specific spec |
| fodt       | P0    | NO        | NO        | No spec-cache entry (ODF 1.3 not cached under fodt/) |
| netpbm     | P0    | NO        | NO        | No unified netpbm spec-cache |
| html       | P0    | NO        | NO        | W3C/WHATWG spec not cached |

## Authority Distribution

| Level | Count | Formats |
|-------|-------|---------|
| P6    | 2     | fods, zst |
| P5    | 0     | — |
| P4    | 0     | — |
| P3    | 4     | csv, pbm, pgm, ppm |
| P2    | 0     | — |
| P1    | 7     | gnumeric, abw, sylk, tsv, dif, markdown, txt |
| P0    | 3     | fodt, netpbm, html |

## Readiness Gate
- **Product readiness (P4+):** fods, zst
- **Product expansion (P4+):** fods, zst
- **Blocked — no public spec:** abw, sylk, tsv, dif, markdown, txt
- **Blocked — schema only:** gnumeric

## Next Authority Advancement Targets
1. **PBM/PGM/PPM P3→P4**: Cache Netpbm HTML spec pages; run deterministic search to verify magic number facts
2. **CSV P3→P4**: Cache RFC 4180 text; run deterministic search to verify FACT-CSV-001/002
3. **FODT P0→P2**: Cache ODF 1.3 under `fodt/` path (reuse fods spec cache)
4. **Gnumeric**: No path without formal spec — schema_authority_available exception maintained

## Proof Graph Status
- FODS: `reports/authority-conveyor-20260608/fods-p6-proof-graph.yaml` (COMPLETE)
- ZST: `reports/authority-conveyor-20260608/zst-p6-proof-graph.yaml` (COMPLETE, this sprint)

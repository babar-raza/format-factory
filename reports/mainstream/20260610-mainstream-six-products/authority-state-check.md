# Authority State Check — Selected Products
# Date: 2026-06-10

## Authority Levels (from registry + completion matrix)

| Product | Spec Body | Spec Version | Authority Level | Sufficient for Readiness? |
|---------|-----------|-------------|-----------------|--------------------------|
| FODS | OASIS | ODF 1.3 | P6 (highest) | YES |
| FODT | OASIS | ODF 1.3 | P6 (highest) | YES |
| CSV | IETF | RFC 4180 | P3 | YES (formal RFC) |
| Netpbm (PBM/PGM/PPM) | Netpbm project | Netpbm spec | P4 | YES |
| NDJSON | ndjson.org | informal | P0 | PARTIAL (no formal RFC) |
| TSV | IANA | media type registration | P0 | PARTIAL (IANA reg only) |

## Authority Gaps
- NDJSON: P0 — informal spec at ndjson.org. Sufficient for Python FOSS. .NET commercial readiness may need authority justification.
- TSV: P0 — IANA media type registered (text/tab-separated-values). No formal RFC. Sufficient for FOSS.

## Gate 11 Cross-Check
- Gate 11 approved_by is null for ALL formats in registry/format-registry.yaml
- No format has commercial approval
- Generated context packs, supervisor outputs, and memory files do NOT claim Gate 11 approval
- **NO overclaim detected for Gate 11**

## Registry vs Completion Matrix Consistency
- FODS/FODT: consistent (both say production_track_real)
- CSV: consistent (both say read_only_prototype, G4)
- Netpbm: consistent (read_only_prototype for Python, .NET not tracked in completion matrix)
- NDJSON: MINOR inconsistency — completion matrix says G4 claimed, actual maturity is roundtrip_capable_library (higher than G4 implies). Not an overclaim since G4 is conservative.
- TSV: consistent (G4, read_only_prototype)

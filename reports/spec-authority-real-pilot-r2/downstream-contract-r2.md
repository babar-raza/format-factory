# Downstream Contract Check — R2
Pilot: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R2-001
Generated: 2026-06-05

## Authority Boundary Compliance

All context packs from this pilot comply with the downstream authority boundary:

| Check | Result |
|-------|--------|
| capability_claims_present | false |
| all packs have manifest.sha256 | true |
| DIF not promoted above EMPIRICAL_ONLY | true |
| No product implementation in packs | true |
| All requirements spec-derived | true |

## Context Pack Contract Structure

Each context pack contains:
- `context_pack_id`: deterministic CP-{FORMAT}-{sha12} identifier
- `format_id`: format string (zst, netpbm, dif, fods)
- `manifest.sha256`: deterministic SHA-256 of included sources
- `included_sources`: source registry entries with sha256 and sections_count
- `requirement_summary`: extracted RFC 2119 / MUST/SHALL/SHOULD statements
- `index_terms`: top 50 indexed terms from source text
- NO capability claims, NO product implementation assertions

## Authority Status Map

| Format | Source Type | Authority Status |
|--------|------------|-----------------|
| ZST | rfc | ACCEPTED_SPEC |
| Netpbm | public_domain_spec | ACCEPTED_WITH_CAVEAT |
| DIF | empirical_observation | EMPIRICAL_ONLY |
| FODS | odf_standard | ACCEPTED_WITH_CAVEAT |

## Downstream Usage Rules

1. ZST (ACCEPTED_SPEC): Requirements may be used as authoritative product obligations
2. Netpbm (ACCEPTED_WITH_CAVEAT): Requirements are advisory; no formal standards body
3. DIF (EMPIRICAL_ONLY): Requirements are observational only; not binding
4. FODS (ACCEPTED_WITH_CAVEAT): Scoped subset only; full ODF 1.3 review pending

capability_claims_present: false

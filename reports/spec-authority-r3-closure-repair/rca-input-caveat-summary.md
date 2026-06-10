# RCA Input Caveat Summary (R3C)
Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-R3-CLOSURE-REPAIR-AND-R4-ODF-PREPARATION-001
Lane: D — RCA Input Caveat Summary
Generated: 2026-06-05

This document mirrors and verifies the R3 caveat summary against the canonical
RCA input packet (rca-r2-input-packet.json).

## Caveat Matrix

| Source | Authority | Caveat Present | Anti-Bypass | Scoped | Downstream Label |
|--------|-----------|---------------|-------------|--------|-----------------|
| ZST | ACCEPTED_SPEC | No | N/A | No | Authoritative obligations |
| Netpbm | ACCEPTED_WITH_CAVEAT | Yes | No | No (full HTML) | De facto advisory |
| DIF | EMPIRICAL_ONLY | Yes | YES (MUST NOT promote) | N/A | Observational only |
| FODS | ACCEPTED_WITH_CAVEAT | Yes | No | Yes (intro only) | Structural guidance (intro) |
| FODT | ACCEPTED_WITH_CAVEAT | Yes | No | Yes (intro only) | Structural guidance (intro) |

## Promotion Rules

| Source | May Promote? | Condition |
|--------|-------------|-----------|
| ZST | N/A (already ACCEPTED_SPEC) | — |
| Netpbm | Yes, with caveat | If formal spec body adopts |
| DIF | HARD BLOCKED | No public spec found; MUST NOT promote |
| FODS | Yes, pending | Full ODF 1.3 ingest + license confirm (R4+) |
| FODT | Yes, pending | Full ODF 1.3 ingest + license confirm (R4+) |

## R4 Open Items

- Full ODF 1.3 ingest: estimated 1000+ pages, 4 parts
- FODS requires: ODF Part 1 (text), Part 2 (packages), Part 3 (schema), formula rules
- FODT requires: ODF Part 1 (text) focus — same schema as FODS text elements
- License: OASIS ODF 1.3 open spec; license type needs legal review before ACCEPTED_SPEC promotion

## Verdict

`RCA_INPUT_CAVEAT_SUMMARY_VERIFIED`

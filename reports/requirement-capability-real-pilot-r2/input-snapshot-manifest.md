# Input Snapshot Manifest
# Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R2-001
# Lane: B

## Source Sprint
FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R3-CLOSURE-HARDENING-AND-ODF-DEPTH-001

## Snapshot Status
FROZEN_FOR_RCA_R2_INPUT (copied from reports/spec-authority-real-pilot-r3/)

## Key Improvement vs R1
FODT is no longer fixture-backed. Spec R3 provides FODT with ACCEPTED_WITH_CAVEAT status
(ODF 1.3 scoped intro, REAL_FETCH_SCOPED). This resolves R1 Caveat 7.

## Sources

| Source ID | Format | Authority Status | Caveat |
|-----------|--------|-----------------|--------|
| src-r2-zst-rfc8878 | ZST | ACCEPTED_SPEC | None — RFC 8878 binding |
| src-r2-netpbm-spec | Netpbm | ACCEPTED_WITH_CAVEAT | De facto; no formal body |
| src-r2-dif-empirical | DIF | EMPIRICAL_ONLY | MUST NOT promote — no public spec |
| src-r2-fods-odf13 | FODS | ACCEPTED_WITH_CAVEAT | Scoped ODF 1.3 intro only (6000 chars) |
| src-r3-fodt-odf13 | FODT | ACCEPTED_WITH_CAVEAT | Scoped ODF 1.3 intro only (5000 chars) — R3 addition |

## Frozen File Hashes
- rca-input-snapshot-manifest.json: SHA-256 dae6800629bde89d...
- rca-input-caveat-summary.md: SHA-256 0e374adc4da05d4e...

## Downstream Usage Rules
- ZST: Use as authoritative product obligations
- Netpbm: Advisory only; label "de facto standard"
- DIF: Observational guidance only; MUST NOT cite as spec; MUST NOT promote
- FODS: Structural guidance; qualify as "ODF 1.3 introduction only"
- FODT: Structural guidance; qualify as "ODF 1.3 introduction only"

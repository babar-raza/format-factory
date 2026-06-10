# FODT Context Pack Report
Sprint: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R3-CLOSURE-HARDENING-AND-ODF-DEPTH-001
Generated: 2026-06-05

## FODT Context Pack Built

Context pack for FODT (ODF Flat Text Document) built from scoped ODF 1.3 introduction.

| Field | Value |
|-------|-------|
| Context Pack ID | CP-FODT-ce25cfe79029 |
| Manifest SHA-256 | ce25cfe790299e69... |
| Format ID | fodt |
| Source ID | src-r3-fodt-odf13 |
| Source Title | ODF 1.3 — Flat Text Document (FODT) — Scoped Introduction |
| Source Type | odf_standard |
| Vault SHA-256 | 358d123fade527a6cb5df551cdfca6b02ec4b82078b72223fadf7d7747f3c094 |
| Sections | 47 |
| Requirements | 3 |
| Verified | PASS |
| Deterministic | YES (run1==run2 SHA-256) |
| Authority Status | ACCEPTED_WITH_CAVEAT |

## Output Location

.local/evidences/spec-authority-real-pilot-r3/context-packs/fodt-context-pack.json

## Downstream Caveat

FODT context pack is SCOPED — based on ODF 1.3 introduction only.
Use caveat: "FODT requirements derived from ODF 1.3 introduction excerpt only.
Full ODF 1.3 Part 3 schema (600+ pages) deferred to R4+. License review pending."

## Anti-Bypass Compliance

- manifest.sha256: present and non-empty
- format_id: fodt
- context_pack_id: CP-FODT-ce25cfe79029 (deterministic from manifest SHA)
- capability_claims: none
- No ACCEPTED_SPEC overclaim — stays ACCEPTED_WITH_CAVEAT

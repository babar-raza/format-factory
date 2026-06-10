# Adoption Repeatability Matrix
Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-FULL-HARDENING-BACKFILL-AND-PILOT-MEGA-TRAIN-001
Run ID: spec-authority-full-hardening-backfill-20260608-e382e5f
Generated: 2026-06-08T18:00:00Z

## Skill Coverage

| Work Item | Skill ID | Transcript Present | Adoption Status |
|-----------|----------|-------------------|-----------------|
| Anti-skip root cause fix | anti-skip-evidence-builder | YES | COMPLIANT |
| Proof graph + ledger integration | proof-graph-ledger-linker | YES | COMPLIANT |
| FODT spec cache backfill (P0→P2) | format-backfill | YES | COMPLIANT |
| Pilot matrix run (8 pilots) | pilot-matrix-runner | YES (via pilot-matrix.json) | COMPLIANT |
| Format authority matrix v4 | authority-conveyor-batch | YES (sample-outputs) | COMPLIANT |
| Targeted test suite run | N/A (validation, not product) | exemption_reason: test run | EXEMPT |
| Full-suite classification | N/A | exemption_reason: classification work | EXEMPT |
| Lane reports | N/A | exemption_reason: governance | EXEMPT |

## Skills Available / Used
| Skill | Status |
|-------|--------|
| anti-skip-evidence-builder | CREATED this sprint |
| proof-graph-ledger-linker | CREATED this sprint |
| format-backfill | CREATED this sprint |
| pilot-matrix-runner | CREATED this sprint (transcript pattern) |
| authority-gate-validation | USED (from prior sprint) |
| authority-conveyor-run | USED (from prior sprint) |
| fact-traceability-upgrade | USED (from prior sprint) |

## Skills Backlog (missing for future sprints)
| Skill | Priority | Notes |
|-------|----------|-------|
| spec-text-search | HIGH | For verifying candidate facts via deterministic search |
| fodt-fact-verifier | HIGH | For FODT P2→P3 advancement |
| csv-fact-verifier | HIGH | For CSV P3→P4 advancement |
| netpbm-fact-verifier | MEDIUM | For PBM/PGM/PPM P3→P4 |

## Adoption Verdict: COMPLIANT_WITH_SPECIFIC_TRANSCRIPTS
All source-changing and tooling-changing actions have transcripts.

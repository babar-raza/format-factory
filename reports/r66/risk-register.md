# R66 Risk Register

| Risk | Severity | Mitigation |
|---|---|---|
| Build ordering (IV-R65-009) | HIGH | Train B: strict order — all state/metadata final before ZIP build |
| Placeholder proofs in bundle | HIGH | Train C: write final proofs, then build. Validator rejects placeholders |
| Artifact discovery false positive | MEDIUM | Train D: env-var override checks sprint-id.txt |
| Truncated hashes in manifest | MEDIUM | Train E: full 64-char SHA-256 enforced |
| Gate 11 G11-G not started | BLOCKING | External: requires Babar Raza approval |
| Gate 8 security review pending | BLOCKING | External: ODS/ODT/QOI/XCF/DIF/PPM |
| Publication not authorized | BLOCKING | External: local-only artifacts |

# R45 Work-Ahead Policy

**Sprint:** FORMAT-FACTORY-R45-TWO-PRODUCT-LOCAL-RC-REPLAYABLE-001

## Anti-Shrink Rule

A blocker in one lane MUST NOT stop other independent lanes. If MT4 (.NET consumer)
is blocked, MT1-MT3 proceed independently.

## Auto-Expansion Rule

Lanes finishing early look for adjacent safe work:
- MT2 completion → check if auto-proof timeout can be further tightened
- MT3 completion → check if artifact manifest format can be standardized
- MT4 completion → check if G11-G packet can name Tier 0 consumer evidence

## Deferred Items (R46 Candidates)

| Item | Rationale for Deferral |
|------|------------------------|
| MT5 FODS write/export round-trip | Capability deepening — not blocking RC |
| MT5 FODT write/export round-trip | Same |
| ZST RC designation | Requires separate consumer proof chain |
| PGM/PBM/SYLK Gate 10 | Not yet gate-ready; Gate 9 is current ceiling |

## Final Validation Policy

- No PENDING markers in any metadata file
- No IN_PROGRESS rows in lane-ownership.md
- State snapshot regenerated after all commits
- AUTHORITATIVE_TEST_RESULT present in validation-command-log.txt
- require_clean_git: true in R45 contract

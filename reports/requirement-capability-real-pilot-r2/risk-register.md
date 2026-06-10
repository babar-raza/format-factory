# Risk Register
Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R2-001

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| FODS/FODT export gaps re-routed to dogfood by mistake | LOW (fixed) | HIGH | R2 gap queue fix + regression test |
| FODT spec caveat not propagated | LOW (fixed) | MEDIUM | spec:fodt:r3 caveat field set |
| DIF promoted beyond EMPIRICAL_ONLY | LOW | HIGH | HARD_BLOCKED by spec caveat |
| Stale ZST claim blocks other ZST claims | LOW | MEDIUM | Staleness scoped to stale node |

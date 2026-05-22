# Risk Register

**Sprint:** FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
**Date:** 2026-05-22

| ID | Risk | Severity | Probability | Mitigation | Status |
|----|------|----------|-------------|-----------|--------|
| R53-RISK-001 | R52 verdict correction triggers confusion in history | LOW | LOW | IV report documents correction clearly; deceptive rewrite avoided | MITIGATED |
| R53-RISK-002 | Sidecar proof tool not adopted by future agents | MEDIUM | MEDIUM | Protocol documented in final-proof-sidecar-protocol.md; MEMORY.md updated | MITIGATED |
| R53-RISK-003 | Formula preservation breaks numeric output (formula overwrites value display) | LOW | LOW | Tests verify value field preserved; formula only adds attribute | VERIFIED_SAFE |
| R53-RISK-004 | Installed-artifact policy creates ambiguity about what counts as "clean baseline" | MEDIUM | MEDIUM | Policy document defines 3 options (A/B/C) with verdict suffix rules | MITIGATED |
| R53-RISK-005 | FODT structural preservation deferred too long (TC-0057/0058/0059) | HIGH | MEDIUM | Gap ledger tracks with taskcards; R54 plan set for TC-0057 | TRACKED |
| R53-RISK-006 | Production blockers never progress (G11-G, GATE8, PACKAGE_NOT_PUSHED) | HIGH | LOW | Blockers require human approval (Babar Raza); all local work proceeds | ACCEPTED_BLOCKER |
| R53-RISK-007 | R27/R32 metadata floor warnings never remediated | LOW | LOW | Warnings only; contracts are old and use old format | ACCEPTED_WARNING |
| R53-RISK-008 | dotnet test invocation issues block .NET verification | MEDIUM | MEDIUM | Last known: R51 FODS 157/157, FODT 145/145; investigate in R54 | DEFERRED |

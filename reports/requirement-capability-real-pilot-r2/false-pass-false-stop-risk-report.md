# False PASS and False STOP Risk Report
Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R2-001

## False PASS Risks
1. Evidence package declared_not_verified=True: package path proves declaration only, not artifacts
2. Architecture-blocked claims were accepted-for-poc in R1 gap queue — fixed in R2
3. FODT was fixture-backed in R1 — now spec-backed (Spec R3)
4. DIF claims are accepted_with_limitations only — empirical_only status enforced

## False STOP Risks
1. Overclaim detection may flag export claims that are correctly blocked
2. Staleness detection on synthetic ZST stale claim may block other ZST claims
3. Scoped FODS/FODT spec (3 reqs only) may undercount requirements for full ODF compliance

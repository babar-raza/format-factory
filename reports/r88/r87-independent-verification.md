# R87 Independent Verification — Train A

Sprint: FORMAT-FACTORY-R88-DECLARATION-DRIVEN-AUTONOMOUS-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001
Date: 2026-06-01

## R87 Review Package Verification

| Check | Expected | Actual | Result |
|-------|----------|--------|--------|
| SHA-256 | b41f7bd8778d922acd581a00ba36cde0f99d54501a408aecfe7d8bdeb0d5bd8c | b41f7bd8778d922acd581a00ba36cde0f99d54501a408aecfe7d8bdeb0d5bd8c | MATCH |
| Size | 11,340,832 bytes | 11,340,832 bytes | MATCH |
| Entries | 47 | 47 | MATCH |

## R87 Defect Classification

| ID | Description | Classification |
|----|-------------|----------------|
| D-R87-01 | Authoritative test result records 27 failed Python tests | CONFIRMED_CARRIED_TO_R88 |
| D-R87-02 | Scoreboard not included in review package ZIP | CONFIRMED_CARRIED_TO_R88 |
| D-R87-03 | final-verdict claims clean but 27 tests failed | CONFIRMED_CARRIED_TO_R88 |
| D-R87-04 | Scoreboard in working tree says ALL_COMPLETE; inside ZIP it was omitted entirely | CONFIRMED_CARRIED_TO_R88 |
| D-R87-05 | Review package missing 9 expected folders/files | CONFIRMED_CARRIED_TO_R88 |
| D-R87-06 | next-sprint.md in ZIP uses run-on-latest, no autonomous-cycle | CONFIRMED_REPAIRED_WORKING_TREE |
| D-R87-07 | CLAUDE.md lacked Sprint Closeout section | CONFIRMED_REPAIRED_WORKING_TREE |
| D-R87-08 | next-sprint-generator.md used legacy closeout | CONFIRMED_REPAIRED_WORKING_TREE |
| D-R87-09 | master-plan Section 40.5 used legacy closeout | CONFIRMED_REPAIRED_WORKING_TREE |
| D-R87-10 | Agent-facing instructions inconsistent with declaration-driven code | CONFIRMED_REPAIRED_WORKING_TREE |
| D-R87-11 | No commercial product finalized | EXPLAINED_NOT_DEFECT (Gate 11 requires human approval) |
| D-R87-12 | Gate 11 not approved | EXPLAINED_NOT_DEFECT (external gate) |
| D-R87-13 | Gate 8 not approved | EXPLAINED_NOT_DEFECT (external gate) |
| D-R87-14 | No publication occurred | EXPLAINED_NOT_DEFECT (external gate) |
| D-R87-15 | commercial_product_ready must remain false | EXPLAINED_NOT_DEFECT (by design) |

## Working Tree Closeout Repairs (from prior session)

These repairs are uncommitted but present and correct in the working tree:

1. **CLAUDE.md** (lines 20-43): Sprint Closeout section present with:
   - evidence-declaration.yaml instruction
   - autonomous-cycle --declaration command
   - exit codes 0/1/3/9 documented
   - run-on-latest deprecated notice

2. **next-sprint-generator.md** (lines 89-98): Lane 7 uses autonomous-cycle --declaration.
   Lines 104-106: Insufficient sprint markers include missing declaration + missing cycle run.

3. **master-plan.md Section 40.5** (lines 1918-1942): autonomous-cycle is canonical command.
   Legacy run-on-latest documented as deprecated with warning.

4. **mega-train-template.md**: New file created (.supervisor/prompts/mega-train-template.md).
   Structural template for generated mega-train execution prompts.

5. **generate_next_worker_prompt.py**: Rewritten to synthesize trains from POC targets + gap fixtures.

## Defects Requiring R88 Action

- D-R87-01: Fix the 27 Python test failures (Train F)
- D-R87-02/04: Include scoreboard in review package (Train G)
- D-R87-03: Ensure honest authoritative test result (Train F)
- D-R87-05: Include all required folders in review package (Train P)
- D-R87-06: Already repaired in working tree; commit needed

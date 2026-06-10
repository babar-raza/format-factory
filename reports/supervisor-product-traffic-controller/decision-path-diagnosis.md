# Decision-Path Diagnosis — Prior Sprint Issue Classification

## Sprint
`FORMAT-FACTORY-SUPERVISOR-PRODUCT-TRAFFIC-CONTROLLER-INTEGRATION-001`

## Purpose
Classify all known issues from the prior Supervisor Product-First sprint so this sprint can wire
the machinery into operational decision-making. Only classified issues affect routing logic.

## Classification Table

| Issue ID | Description | Type | Impact on This Sprint |
|----------|-------------|------|-----------------------|
| DIAG-01 | Mainstream R113 product_breadth_score=2 (needs 3+) | PRODUCT_GAP | Mainstream routing must target 3+ families |
| DIAG-02 | Skills R113 machinery_overhead_score=2 not consumed by Mainstream | CONSUMPTION_GAP | Cross-stream bridge must flag SKILLS_MISSING_PACKET |
| DIAG-03 | Acceleration R112 product_breadth_score=1 | PRODUCT_GAP | Acceleration stream marked CONTINUE (not CLEAN_PASS) |
| DIAG-04 | Supervisor R110 machinery_overhead_score=3 | OVERHEAD_FLAG | Supervisor stream marked CONTINUE_WITH_LIMITATIONS |
| DIAG-05 | Skills/Acceleration report directories absent | STREAM_ABSENT | Fallback: local coordinator authority; no cross-stream packet consumption |
| DIAG-06 | TC-CLOSE-003/004 left as not_started in prior declaration | DECLARATION_DEFECT | Repaired in SR-03; declaration now complete |
| DIAG-07 | Absolute import bug in ai_supervisor_advisor.py | IMPORT_BUG | Repaired in SR-01; try/except pattern applied |
| DIAG-08 | Missing test coverage for 5 code paths | TEST_GAP | Repaired in SR-02; 29 tests now pass |

## Implementation Blockers

| Issue | Status | Fix |
|-------|--------|-----|
| DIAG-01: Mainstream breadth < 3 | PLANNED_FIX | Routing packet will target FODS/FODT/Netpbm/SYLK/ZST |
| DIAG-02: Skills not consumed | DOCUMENTED | Bridge flags SKILLS_MISSING_PACKET; Mainstream handoff notes gap |
| DIAG-05: Streams absent | ACCEPTED_LIMITATION | Fallback documented; routing packets use local state |

## Non-Blockers

DIAG-03, DIAG-04: Continuation state CONTINUE/CONTINUE_WITH_LIMITATIONS is expected for streams
with limited product breadth. Not a blocker for this sprint — they will receive targeted handoffs.

DIAG-06, DIAG-07, DIAG-08: Already repaired. No action needed in this sprint.

## Verdict
**DIAGNOSIS_COMPLETE** — All issues classified; 2 implementation blockers have planned fixes;
5 non-blockers documented; 3 already-repaired.

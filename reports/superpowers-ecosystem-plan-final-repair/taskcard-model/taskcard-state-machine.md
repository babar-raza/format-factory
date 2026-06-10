# Taskcard State Machine
Sprint: FORMAT-FACTORY-SUPERPOWERS-ECOSYSTEM-PLAN-FINAL-REPAIR-001

## States and Transitions

```
TODO
  └─ start work ──────────────────► IN_PROGRESS
                                          │
                               ┌──────────┼──────────┐
                               │          │          │
                        external     implementation  blocked
                        gate hit       complete     locally
                               │          │          │
                               ▼          ▼          ▼
                      BLOCKED_EXTERNAL  IMPLEMENTED  BLOCKED_LOCAL
                               │          │          │
                          human clears    │       coordinator
                               │    verification    resolves
                               │     runs OK        │
                               │          │          │
                               │          ▼          │
                               │       VERIFIED ◄────┘
                               │          │
                               │    coordinator
                               │      signs off
                               │          │
                               └──────────▼
                                        CLOSED
                                    (closeout_verdict=CLOSED_VERIFIED)

IN_PROGRESS ──► REWORK_REQUIRED  (supervisor grades REJECTED or OVERCLAIMED)
                      │
              fix + re-implement
                      │
                      ▼
               IN_PROGRESS (retry)

IN_PROGRESS ──► DEFERRED  (out of scope decision by coordinator)
```

## Status Descriptions

| Status | Meaning |
|--------|---------|
| TODO | Not started |
| IN_PROGRESS | Actively being worked |
| IMPLEMENTED | Work done; pending verification |
| VERIFIED | Verification commands passed; evidence confirmed |
| CLOSED | Coordinator signed off; closeout_verdict set |
| BLOCKED_LOCAL | File conflict or local error; coordinator must resolve |
| BLOCKED_EXTERNAL | Needs human action (credential, approval, etc.) |
| REWORK_REQUIRED | Supervisor graded REJECTED or OVERCLAIMED |
| DEFERRED | Out of scope; deferred to future sprint |

## Closeout Gates
1. All evidence_paths exist and are non-empty
2. All verification_commands exit 0
3. No REWORK_REQUIRED sub-items outstanding
4. Coordinator confirms closeout_verdict = CLOSED_VERIFIED

## Task Master Reconciliation Rule
- TM status "done" → coordinator reviews → evidence check → VERIFIED only if evidence exists
- TM "done" WITHOUT evidence check = NOT sufficient for CLOSED
- TM status is informational input, NOT authority for closeout_verdict

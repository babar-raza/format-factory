# Review vs Plan Gap Matrix
## Plan Hardening Sprint 2026-06-09

---

For each weakness from the system status review: review claim, plan handling, verdict, required hardening, taskcard, gate.

| W# | Review Claim | Plan Handling | Verdict | Required Hardening | Taskcard | Gate |
|---|---|---|---|---|---|---|
| W1 | Commercial .NET track is skeleton-level | Plan said "Tier 0-1 only" | **OVERSTATED** — .NET FODS has 2,179 LOC with full CRUD+export. Tier 1 COMPLETE. | Correct tier assessment from source. Document operations actually implemented. | TC-B1, TC-B2 | TRIAGED→READY |
| W2 | Autonomous source writing unproven E2E | Plan said "infrastructure exists, loop not validated" | **ADEQUATE** — Components inventoried. Integration gap correctly identified. | Design safe pilot. Document exact loop segments missing. | TC-C1, TC-C2 | READY for design; TC-C3 BLOCKED for execution |
| W3 | Shallow formats outnumber deep formats | Plan said "7 shallow vs 7 deep" | **ADEQUATE** — Correct assessment. But plan missed that 5 deep formats HAVE write capability. | Build precise maturity matrix. Classify shallow formats. | TC-D1, TC-D5 | READY |
| W4 | Git state dirty, history may not reflect work | Plan said "dirty but not dangerous" | **UNDERSTATED** — 375 untracked (not 150+). 2 new Python modules at risk. | Precise file count + classification + checkpoint plan. | TC-F1-F5 | READY |
| W5 | Test-count drops not explained | Plan said "STALE weakness" | **ADEQUATE** — Correct that current trend is healthy. | Document full-suite counts at checkpoints. Add drift validator. | TC-G1-G5 | READY |
| W6 | Evidence automation partial | Plan said "80% auto, 20% manual" | **OVERSTATED** — Actual is ~47% auto by field count. | Field-by-field verification. Identify automation candidates. | TC-E1-E5 | READY |
| W7 | Gate 11 not approved | Plan correctly identified Gate 11 contradiction | **ADEQUATE** — Strongest finding confirmed. | Document verbatim evidence. Specify cross-check validator. | TC-A1-A4 | READY |
| W8 | Python FOSS packages unpublished | Plan said "wheels built, not on PyPI" | **ADEQUATE** — Correct. Plan missed that 5 formats have write (closer to publishable). | Verify package artifacts. Define PyPI checklist. | TC-H1, TC-H3 | READY |
| W9 | Authority classifications wrong/corrected | Plan documented FODT P0→P4 and context-pack overclaim | **ADEQUATE** — Correct findings. | Formalize authority source map. | TC-A4 | READY |
| W10 | Too much governance, not enough product | Plan said "OVERSTATED" | **ADEQUATE** — Recent sprints are product-focused. Balance improving. | Define product-first sprint policy (60% threshold). | TC-D4 | READY |
| W11 | Human-required actions overused | Plan said "PARTIALLY VERIFIED" | **ADEQUATE** — Most items are agent-preparable. | Classify each Gate 11 criterion as agent-preparable or true human. | TC-B5 | READY |
| W12 | Next-sprint/continuation signals stale | Plan identified continuation-signal inconsistencies | **ADEQUATE** — Correctly noted advisory_prompt_executable=false. | Normalize authority rules for generated files. | TC-A3 | READY |
| W13 | Evidence packages had problems | Plan said "mostly resolved" | **ADEQUATE** — 0 blocking violations in current state. Lane ledger gap remains. | Verify anti-skip detectors #3 and #9. Specify path-only blocker. | TC-E4, TC-E5 | READY |
| W14 | Repeatability/idempotency unproven | Plan said "architecturally designed, only validated on 4 functions" | **ADEQUATE** — No replay pilot executed. | Design idempotency pilot (blocked until autonomy pilot proves loop). | TC-C5 | BLOCKED |
| W15 | Queue-to-evidence closure unproven | Plan said "VERIFIED as real weakness" | **ADEQUATE** — Lane ledger minimal (1 entry). No E2E proof. | Specify lane ledger requirement. Design pilot. | TC-C1-C4, TC-E3 | TC-C1-C2 READY; TC-C3-C4 BLOCKED |

### Verdict Summary
- **ADEQUATE:** 11 weaknesses (W2, W3, W5, W7, W8, W9, W10, W11, W12, W13, W14, W15)
- **OVERSTATED:** 2 weaknesses (W1, W6)
- **UNDERSTATED:** 1 weakness (W4)
- **MISSING:** 0

### Key Hardening Applied
1. Corrected .NET tier assessment from "skeleton" to "Tier 1 COMPLETE"
2. Corrected evidence automation from "80%" to "~47%"
3. Corrected untracked file count from "150+" to "375"
4. Added Python write capability data (5 formats confirmed)
5. Added taskcard governance with state machine
6. Separated Stage 1 (planning) from Stage 2 (execution)
7. Added independent verification lane

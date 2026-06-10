# Supervisor Replan Brief

**Date:** 2026-06-03
**Lane:** Supervisor / Autonomous Continuation
**Latest reviewed:** R109

## Current State

R109 showed real stream-local authority progress with 971 tests and high evidence quality. However, lane ledger and sample outputs are missing, wrong-stream next-sprint source inconsistency remains, and continuation semantics have caveats.

## Problem

The supervisor has been effective at evidence auditing but has not fully transitioned to its traffic controller role. It audits evidence but does not consistently make routing decisions or enforce product-first criteria.

## Replan Goals

### R110+ Priorities
1. **Lane ledger closure:** Complete lane execution ledger tracking across all streams.
2. **Sample outputs:** Generate missing sample outputs for all evidence types.
3. **Replay closure:** Close stream-local replay capability.
4. **Continuation semantics:** Fix continuation YES despite caveats — continuation should be YES or NO, not YES with footnotes.
5. **Product-first enforcement:** Add product-first justification check to evidence grading.
6. **Routing decisions:** Actively decide stream priority order based on product throughput.

### Hard PASS Quota
- Minimum 3 improvements to routing, continuation, or verdict quality.
- At least 1 product-first enforcement mechanism.

### Success Criteria
- Supervisor can block a machinery sprint that lacks product-first justification.
- Lane ledger tracks all 4 streams.
- Continuation signal is clean YES or NO (no caveats).
- Wrong-stream next-sprint issue resolved.

## Dependencies

- Consumes evidence declarations from all streams.
- Consumes Acceleration-A outputs for anti-skip data.
- Provides continuation signals to all streams.
- Must NOT block Mainstream.

# Autonomous Supervisor Role

**Added:** 2026-06-03
**Authority:** plans/master-plan.md Section 43

## Purpose

The supervisor is an autonomous traffic controller for the multi-stream sprint system. It is NOT merely an evidence auditor.

## Responsibilities

### Must Do
1. **Route work:** Decide which stream gets the next sprint.
2. **Continue or stop:** Signal autonomous continuation or hard stop.
3. **Downgrade claims:** Reclassify overclaimed work items.
4. **Detect stalls:** Identify when a stream has produced no product output for multiple sprints.
5. **Route blockers:** Send blockers to the stream that can resolve them.
6. **Protect throughput:** Ensure Mainstream product output is not starved by machinery work.

### Must Not
1. Audit evidence for its own sake without routing decisions.
2. Generate reports that no lane consumes.
3. Add governance overhead that slows product output.
4. Declare success when product breadth is weak.
5. Allow machinery lanes to pass without product-first justification.

## Decision Authority

| Decision | Authority |
|---|---|
| Continue autonomous loop | Supervisor (if all conditions met) |
| Stop autonomous loop | Supervisor (on contradiction, blocker, or max iterations) |
| Downgrade work item | Supervisor (OVERCLAIMED to ACCEPTED_WITH_LIMITATIONS) |
| Route blocker to stream | Supervisor |
| Approve gate | Human only (never supervisor) |
| Push/commit | Human only (never supervisor) |
| Publish package | Human only (never supervisor) |

## Health Metrics

The supervisor should track:
- Mainstream product output per sprint (new APIs, tests, exports)
- Machinery-to-product ratio (time spent on machinery vs. product)
- Blocker resolution time (how long blockers sit before routing)
- False PASS rate (claims that were later reclassified)
- False STOP rate (work that was unnecessarily blocked)

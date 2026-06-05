# Mainstream Product-Output Floor

**Added:** 2026-06-03
**Authority:** plans/master-plan.md Section 43

## Rule

No machinery lane may declare clean success unless it meets at least one of these criteria:

1. **Removes a product blocker.** The sprint unblocked a specific Mainstream capability that was previously stuck.
2. **Prevents a harmful false verdict.** The sprint caught a false PASS (overclaimed work) or false STOP (unnecessarily blocked work) that would have affected product velocity.
3. **Creates a reusable accelerator.** The sprint produced a tool, skill, or template that Mainstream can consume in its next sprint.
4. **Reduces human handoff.** The sprint automated a step that previously required manual intervention.
5. **Improves throughput, safety, or repeatability.** The sprint made product sprints faster, safer, or more consistent in a measurable way.

## Application

### At Sprint Planning
Every machinery sprint prompt must include a "product-first purpose" section stating which criterion it targets.

### At Sprint Closeout
Every machinery evidence declaration must include a "product-first justification" field answering:
- What product blocker was removed?
- What product throughput was improved?
- What false verdict was prevented?
- If none: why was this sprint necessary?

### At Review
The supervisor must flag any machinery sprint that cannot demonstrate product-first justification. Such sprints receive ACCEPTED_WITH_LIMITATIONS at best.

## Commercial .NET Output Floor

For Mainstream sprints targeting commercial .NET products (FODS, FODT, Netpbm), the minimum output floor per sprint is:
- At least 1 new API method or capability per product touched
- Tests for each new capability
- Updated capability matrix

## Reduced/FOSS Output Floor

For Mainstream sprints targeting FOSS products (ZST, Python Netpbm, SYLK/DIF), the minimum output floor per sprint is:
- At least 1 new parser/writer/export capability
- Tests proving the capability
- Updated capability matrix

# Mainstream POC Mega-Train Model

**Added:** 2026-06-04
**Authority:** plans/master-plan.md Section 43 + local-memory-sync sprint 2026-06-04

## Purpose

The Mainstream POC Mega-Train is the primary execution model for delivering the Format Factory POC. It runs continuously — iteration after iteration — until POC readiness is achieved or a hard external blocker is reached.

## Core Principle

Do not stop after one sprint just because one iteration completed. Continue until the POC readiness dashboard is green or a true external/hard blocker is reached.

## Sprint ID Convention

```
FORMAT-FACTORY-MAINSTREAM-POC-MEGA-TRAIN-<ITERATION>
```

## Continuation Loop

```
LOOP:
  1. Load POC readiness dashboard (product-capability-matrix/poc-targets.yaml)
  2. Load Skills/Acceleration/Supervisor machinery status
  3. Detect Ruflo mode from Supervisor-approved report
  4. Select gaps by readiness delta (most impactful open gaps first)
  5. Allocate lanes (one per product or product group)
  6. If Ruflo FULL_LOOP_APPROVED → map lanes to Ruflo workers
     If Ruflo absent/unapproved → use local sequential coordinator
  7. Execute lane work (allowed/forbidden files per taskcard)
  8. Run focused tests for each lane
  9. Repair locally up to 2 attempts per failure
  10. Continue unrelated lanes when one is blocked
  11. Integrate changes when lanes are complete
  12. Run broader tests when safe
  13. Package evidence (declaration, manifest, changed-files)
  14. Update POC readiness dashboard
  15. Ask Supervisor/local deterministic state machine:
      → POC_READY_CANDIDATE: all products green → stop and report
      → CONTINUE_NEXT_ITERATION: gaps remain, no hard blocker → increment iteration
      → CONTINUE_WITH_REROUTE: some lanes blocked → reroute to unblocked lanes
      → STOP_EXTERNAL_GATE: Gate 8, Gate 11, or business target conflict
      → STOP_UNSAFE_WORKSPACE: source corruption, repeated unrepairable failure
  16. If CONTINUE_* → increment iteration, return to step 1
```

## Hard Stops (NEVER continue autonomously past these)

- Credentials, secrets, or API keys needed
- git push, merge, release, or publication decision
- Gate 8 or Gate 11 approval
- Destructive cleanup/reset/stash requested
- Unsafe workspace or source corruption detected
- Repeated unrepairable foundational failure (same failure 3+ times)
- Business target conflict requiring user decision

## Do NOT Stop For (false stops)

The following are NOT valid reasons to stop:

- Missing local evidence (create it and continue)
- False prompt-quality failure (fix the prompt and continue)
- One blocked lane when others can progress (skip the blocked lane)
- Unfinished machinery when product work is available
- Ruflo absent (use local coordinator)
- Acceleration unavailable (proceed without AI acceleration)
- Skills wrapper unavailable when fallback transcript is safe (use fallback)

## Lane Allocation

Each iteration allocates lanes by readiness delta:
1. Identify which products have the largest capability gap
2. Assign one lane per product group
3. Declare allowed/forbidden files per lane
4. Declare cross-stream dependencies at sprint start

## Product-Output Floor

Every Mainstream iteration MUST deliver at minimum:
- 1+ new capability (API, feature, or export path) per product touched
- Tests for each new capability
- Updated capability matrix entry

Evidence repair does NOT count toward this floor.

## Machinery Auto-Adoption

If Skills, Acceleration, or Supervisor provide a handoff packet that Mainstream can consume, Mainstream should adopt it without waiting for human review — as long as:
- The handoff is labeled (ai_draft, skill_handoff, etc.)
- The code changes are tested before claiming product credit
- The adoption is recorded in the evidence declaration

## Acceleration Feedback Loop

At the end of each iteration, Mainstream reports to Acceleration:
- Which gaps were addressed
- Which gaps remain
- Which handoffs were consumed and whether they were useful
- Any new blockers discovered

Acceleration uses this to refine its gap rankings and code-generation handoffs for the next iteration.

## POC Readiness Dashboard

The dashboard lives at `product-capability-matrix/poc-targets.yaml`. It tracks:
- Per-product capability status (green/yellow/red)
- Test count per product
- Package proof status
- Example status
- Dogfood status

Green = all required capabilities proven with tests and evidence.
POC_READY_CANDIDATE = all products green.

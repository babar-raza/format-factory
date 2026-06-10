# Acceleration Replan Brief

**Date:** 2026-06-03
**Lane:** Acceleration
**Latest reviewed:** R111

## Current State

R111 showed real governance progress (stream-output authority, 428 tests, prompt-quality valid) but anti-skip contradictions remain (missing_sample_outputs false positive, wrong_stream_next_sprint, continuation YES despite caveats). AI product acceleration (sub-lane B) has been dormant.

## Problem

Acceleration drifted entirely into Acceleration-A (governance harness). Acceleration-B (AI product acceleration) has produced no consumable output for Mainstream.

## Replan Goals

### Acceleration-A (Governance Harness)
1. Fix remaining anti-skip contradictions (false positives).
2. Fix wrong_stream_next_sprint source inconsistency.
3. Stabilize — do not expand governance scope.

### Acceleration-B (AI Product Acceleration) — PRIMARY FOCUS
4. Produce code-generation handoffs for Mainstream product changes.
5. Produce test-generation output from spec requirements.
6. Produce product gap ranking for Mainstream sprint planning.
7. Investigate spec understanding acceleration (LLM-assisted requirement extraction for FODT, Netpbm).

### Hard PASS Quota
- Minimum 2 Acceleration-B deliverables that Mainstream can consume in its next sprint.
- Acceleration-A fixes count only if they resolve a demonstrated false verdict.

### Success Criteria
- At least 1 code-generation or test-generation output consumed by Mainstream.
- Anti-skip false positives eliminated.
- Acceleration-B has a concrete backlog of product acceleration tasks.

## Dependencies

- Needs Mainstream product state to know what to accelerate.
- Needs Supervisor for false verdict data (Acceleration-A).
- Must NOT block Mainstream.

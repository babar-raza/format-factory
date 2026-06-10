# Advancement Lane Definition — Acceleration Stream

## What counts as "advancement" for Acceleration

Acceleration advancement is NOT product implementation. It is tooling, infrastructure, and governance improvement for the supervisor pipeline.

### Valid Acceleration Advancement Lanes
1. **Anti-skip detector improvement** — expand detectors, refine severity mapping, improve detection accuracy
2. **Grading engine / evidence quality scoring** — enhance grade_declared_work.py, evidence quality heuristics
3. **Hard gate and continuation policy** — strengthen autonomous-cycle enforcement, stop conditions
4. **Stream prompt generation** — prompt quality validation, stream-specific content injection
5. **Selected-gap freshness** — stale gap archival, freshness classification
6. **Package self-containment** — evidence packaging, lane ledger, sample outputs
7. **Next-work generator hardening** — stream filtering, forward work generation, validation
8. **Stream-state isolation** — cross-stream contamination detection, boundary enforcement

### Terms that indicate Acceleration advancement
Generic: advance, improve, add, implement, new
Acceleration-specific: detector, validator, harden, expand, enhance, severity, enforce, integrate, detection accuracy, quality scoring, continuation policy, stop condition, strengthen, refine

### What is NOT Acceleration advancement
- Product feature implementation (FODS, FODT, Netpbm, etc.)
- src/net/* or src/python/* edits
- Gate 11 commercial readiness
- Package publication

### Implementation
- `STREAM_FORWARD_WORK["acceleration"]` in generate_next_worker_prompt.py defines 3 forward work items
- `stream_advance_terms["acceleration"]` in validate_prompt_quality.py defines 14 check terms
- Generated acceleration prompts include forward work trains in G2 group
- Sprint goal includes "Advance Acceleration tooling: ..." when no product trains present

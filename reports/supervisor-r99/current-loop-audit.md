# Train A: Current Loop Audit (R93-R98 Declarations)

## Audit Scope
Audited R93-R98 declarations, latest-cycle-summary, evidence-review, contradictions, work-item-grades, context-pack, and continuation-signal.

## Issue Inventory

### D99-STALE-01: Legacy packet markdown files are stale after declaration-driven sprints
- **Severity:** CRITICAL
- **Files affected:** reports/supervisor/session-resume.md, approval-gates.md, next-sprint.md, evidence-review.md, contradictions.md
- **Root cause:** autonomous_cycle.py writes evidence-review.json and contradictions.json via bridge_to_legacy_format(), but never invokes generate_supervisor_packet.py to regenerate the markdown outputs. The last markdown regeneration was from the R86 legacy ZIP-based run.
- **Impact:** session-resume.md says "R86 REJECTED" while latest-cycle-summary.md says "R98 ACCEPTED". approval-gates.md says AUTONOMOUS_CONTINUE: NO while continuation-signal.json says autonomous_continue=true. Any agent reading session-resume.md gets incorrect state.
- **Fix:** Add a call to generate_supervisor_packet.py at the end of autonomous_cycle.py bridge step.

### D99-STALE-02: Context pack not refreshed as part of autonomous-cycle
- **Severity:** WARNING
- **Root cause:** autonomous_cycle.py does not call build_context_pack.py. Context pack is only updated manually.
- **Impact:** context-pack.yaml and context-pack.md may drift from actual state.
- **Fix:** Add context pack rebuild to autonomous_cycle.py after grading.

### D99-MODEL-01: Materializer not invoked by autonomous_cycle.py
- **Severity:** WARNING
- **Root cause:** autonomous_cycle.py calls inspect -> grade -> prompt -> manifest, but never calls materialize_declared_evidence.py. Materialization is a separate manual step.
- **Impact:** No git diffs captured, no SHA-256 verification of artifacts, no missing-evidence-report produced as part of the standard loop.
- **Fix:** Add materializer invocation between inspect and grade steps.

### D99-GRADE-01: No DEFERRED_WITH_REASON grade in grading engine
- **Severity:** INFO
- **Root cause:** grade_declared_work.py docstring lists DEFERRED_WITH_REASON but no code path produces it. Declaration status "deferred" is not handled — falls through to default.
- **Fix:** Add declared_status == "deferred" handler.

### D99-GRADE-02: No REJECTED grade logic in grading engine
- **Severity:** INFO
- **Root cause:** grade_declared_work.py never produces REJECTED grade. It is documented but no condition triggers it. In practice, contradicted-by-evidence items get OVERCLAIMED instead.
- **Impact:** Low — OVERCLAIMED serves the same blocking purpose.
- **Fix:** Document REJECTED as reserved for manual override; OVERCLAIMED is the automatic equivalent.

### D99-CONT-01: Continuation state machine partially implemented
- **Severity:** INFO
- **Root cause:** R98 added continuation_state to the signal, but the state machine values are computed inline with ad-hoc if/elif. No NO_POLICY_BLOCK or NO_NO_PROGRESS states exist.
- **Fix:** Refactor continuation state classification into a proper function with all documented states.

### D99-PROMPT-01: Next prompt generator is single-stream only
- **Severity:** WARNING
- **Root cause:** generate_next_worker_prompt.py produces one mega-train prompt. No stream separation (product/acceleration/skills/supervisor).
- **Impact:** Supervisor-only sprints receive product trains they cannot execute. Product sprints receive supervisor infrastructure trains they don't need.
- **Fix:** Add stream parameter to prompt generator.

### D99-REVIEW-01: Review package missing several declared items
- **Severity:** WARNING
- **Root cause:** build_declaration_review_package.py hardcodes specific paths (R91/R92 review, etc.) but does not include: supervisor cycle manifest, continuation signal, MCP status report, or the full gap-selection JSON.
- **Fix:** Add these to the review package.

### D99-MCP-01: MCP_ACTIVE_VERIFIED and MCP_BLOCKED_POLICY never produced
- **Severity:** INFO
- **Root cause:** check_mcp_status.py and build_context_pack.py only produce 4 of the 6 documented states. MCP_ACTIVE_VERIFIED (requires runtime server check) and MCP_BLOCKED_POLICY (requires policy deny check) are not implemented.
- **Fix:** Document MCP_ACTIVE_VERIFIED as aspirational (requires MCP runtime probe); add MCP_BLOCKED_POLICY check against policies.yaml.

## Summary
| ID | Severity | Fixed In |
|----|----------|----------|
| D99-STALE-01 | CRITICAL | R99 Train B |
| D99-STALE-02 | WARNING | R99 Train G |
| D99-MODEL-01 | WARNING | R99 Train C |
| D99-GRADE-01 | INFO | R99 Train E |
| D99-GRADE-02 | INFO | R99 Train E (documented) |
| D99-CONT-01 | INFO | R99 Train J |
| D99-PROMPT-01 | WARNING | R99 Train K |
| D99-REVIEW-01 | WARNING | R99 Train D |
| D99-MCP-01 | INFO | R99 Train H |

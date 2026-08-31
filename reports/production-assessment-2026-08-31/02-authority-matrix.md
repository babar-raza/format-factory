# 02 — Authority Matrix

**Baseline commit:** dd909cf3a
**Evidence:** Source code reading, import tracing, grep for callers/consumers

## Authority Graph

| Concern | Candidate sources | Writers | Readers | Current winner | Conflict behavior | Freshness rule |
|---------|------------------|---------|---------|----------------|-------------------|----------------|
| Active mission | product-goal.yaml, master-plan.md, session-resume.md | Codex agent, human/agent, generate_supervisor_packet.py | goal_driver.py, CLAUDE.md session start, every session | product-goal.yaml (goal_driver.py hardcodes GOAL_PATH) | No conflict possible — hardcoded path | Committed to git; no staleness mechanism |
| Active plan | plan-locks/*.json, active-plan-lock.json, plans/.control/config.json | write_plan_lock.py, plan_control/ (unused) | check_continuation.py Check 1b, autonomous_cycle.py Step 0b | Session-keyed locks (newest wins per TC-LOCK-001) | LOCK_STATUS_MISMATCH -> CRITICAL contradiction. Stale locks >7 days auto-skipped | Stale: >7 days skipped. GC: >30 days deleted |
| Current task | next-sprint.md, next-work-items.json, current-gaps.yaml, controller-state.yaml, product-task-candidates.json | generate_supervisor_packet.py, autonomous_cycle.py, Codex, FF6 writer, autonomous_task_generator.py | Agent (CLAUDE.md), check_continuation.py, goal_driver.py | **TWO parallel winners**: next-work-items.json (supervisor) AND controller-state.yaml (FF6) | Plan lock suppresses all ledger items (PLAN_LOCKED mode) | Regenerated every autonomous cycle |
| Task state | continuation-signal.json, evidence-declaration.yaml, controller-state.yaml checkpoints | autonomous_cycle.py Step 8, agent, FF6 controller | check_continuation.py, autonomous_cycle.py, goal_driver.py | continuation-signal.json (supervisor) / controller-state.yaml (FF6) | Signal is session-scoped (CCI-MVP). SESSION_MISMATCH is non-overridable | Signal: written every cycle. Controller: updated only by verified events |
| Worker ownership | coordination/ DB, plan-control/locks/, worker_claim.py | coordination hooks (auto), plan_control, autonomous_cycle.py | coordination preflight, autonomous_cycle.py Step 1c | Coordination plane (advisory mode — conflicts logged but don't block) | PathOwnershipConflict is advisory-only | Per-task lifetime; no explicit TTL |
| Capability definition | .governance/capabilities/registry.yaml, reports/capability-layer/, shared/format-contracts/ | sync-capabilities, capability_map_generator, contract_compiler | CLAUDE.md, /capability-status, generate_next_worker_prompt.py | .governance/capabilities/registry.yaml (canonical) | Contract compilation is deterministic projection from registry | Synced by /sync-capabilities; SAL staleness check >7 days |
| Obligation definition | ff6/obligations/*.yaml, shared/format-contracts/*-obligations.yaml, implementation-evidence/*.yaml | FF6 controller events, contract pipeline, agent evidence | contract_reconciler.py, goal_driver.py, contract_reconciler.py | ff6/obligations/*.yaml (goal_driver.py hardcodes OBLIGATIONS_DIR) | StoreError on ID mismatch (fail-closed) | Frozen per format in controller-state canonical_obligations |
| Implementation state | *-reconciliation.json, *-obligation-reconciliation.json, implementation-evidence/*.yaml | contract_reconciler.py (heuristic/exact), agent (evidence) | goal_driver.py, autonomous_cycle.py, controller checkpoints | Exact obligation-reconciliation.json (goal_driver.py prefers it) | Heuristic is non-promoting. promotion_effect: none | Regenerated on demand; SHA256 digest tracks input closure |
| Test result | evidence-declaration.yaml, evidence-review.json, CI outputs | Agent, autonomous_cycle.py Step 3+7, GitHub Actions | autonomous_cycle.py, generate_supervisor_packet.py, pr-test-analyzer | evidence-review.json (graded supervisor assessment) | Declaration is self-reported; review is independent grading. Downgrades via REWORK/OVERCLAIMED/REJECTED | Per-cycle. Older >30 days GC'd unless pinned |
| Evidence acceptance | autonomous_cycle.py pipeline, evidence-review.json, review packages | autonomous_cycle.py Steps 2-3, grade_declared_work.py | check_continuation.py, generate_supervisor_packet.py | autonomous_cycle.py pipeline (sole acceptance authority) | Multiple gates can override: governance, gap ledger trace, SFC closeout, closure challenge | Per-cycle. Quality scoring is advisory |
| Gap state | gap-ledger.json, current-gaps.yaml, *-contract-gaps.json | gap_closure_engine.py, Codex/FF6, gap_compiler.py | generate_next_work_items(), capability_queue_consumer.py, check_continuation.py | gap-ledger.json (supervisor) / current-gaps.yaml (FF6) | BLOCKING+OPEN gaps in product-code-gap-ledger -> hard stop. Unreadable -> fail-closed | Gap closure runs every cycle; auto-close via test scan |
| Format maturity | product-deepening-ledger.yaml, controller-state.yaml promotion, reports/certification/ | autonomous_cycle.py Step 7d, FF6 controller, certification skills | check_continuation.py Check 9, lane_selector.py, goal_driver.py | controller-state.yaml promotion (FF6) / product-deepening-ledger.yaml (gen-1) | Invariant claims promotion is computed from proof (VIOLATED — it's a static string) | Maturity trend appended each cycle |
| Certification | controller-state.yaml promotion + truth_boundary + production_certifications, certification reports, goal_driver.py | FF6 controller events, certification skills, goal_driver.py | goal_driver.py evaluate(), human/agent review | controller-state.yaml promotion block (sole authority — goal_driver.py reads it directly) | THREE-WAY CONTRADICTION in same file (promotion 4/6, truth_boundary 0/6, production_certifications 0) | Changes only via controller events (in theory) |
| Continuation | check_continuation.py, goal_driver.py, CLAUDE.md Supreme Directive | N/A (readers, not writers) | sprint_executor.py, autonomous-loop, CLAUDE.md | TWO parallel by design: check_continuation.py (ephemeral) + goal_driver.py (durable) | Supreme Directive overrides 17+ of 23 STOP reasons. Only 6 STOPs honored | check_continuation: per-invocation. goal_driver: on-demand |
| Terminal state | check_continuation.py STOP, CLAUDE.md bypass rules, sprint_executor.py overrides, goal_driver.py | check_continuation.py, CLAUDE.md, sprint_executor.py, goal_driver.py | sprint_executor.py, autonomous-loop, agent | CLAUDE.md (ultimate authority on which stops are terminal) | 23+ STOP reasons exist; only 6 are honored. Supreme Directive overrides the rest | Immediate — checked before each sprint |
| Release state | format-registry.yaml gates, packaging/, package-install-proof/, gate-states.yaml | gate_executor.py, build scripts, package_install_proof.py, evaluate_gate11_readiness() | gate_executor.py, governance validators, check_continuation.py Check 11 | format-registry.yaml (canonical registry) | Gate 11 READY -> TRUE_EXTERNAL_GATE stop (Babar Raza authorization) | Updated on gate transitions |

## Critical Structural Observations

### 1. Certification Authority is a Label, Not a Computation
goal_driver.py reads `promotion.get(format_id) == "CERTIFIED"` — a string that can be manually set. PROVEN: setting all 6 to CERTIFIED produces GOAL_ACHIEVED regardless of test state, evidence, or proof chains. The controller-state.yaml invariant "Product promotion is computed from current proof" is violated.

### 2. Two Disconnected Task-Selection Systems
- Generic supervisor: next-work-items.json -> gap-ledger -> capability queue (covers gen-1 formats only)
- FF6 goal driver: controller-state.yaml -> obligations -> evidence (covers FF6 formats only)
- PROVEN: lane_selector.py returns "format_not_found" for all 6 FF6 formats
- Neither system can divert work to the other, but both can run in the same session

### 3. 17 of 23 STOP Reasons Are Overridden
check_continuation.py produces 23+ STOP reasons. CLAUDE.md Supreme Directive and sprint_executor.py override all except 6: SESSION_MISMATCH, CHAT_ID_MISMATCH, POST_PLAN_TERMINAL, PLAN_COMPLETED_IN_SESSION, structural_govblock, gate_11_ready.

### 4. Ephemeral vs Durable State Split
- continuation-signal.json: session-scoped, gitignored, not bootstrappable from clean clone
- controller-state.yaml: committed, durable, deterministic — but contains contradictions
- A clean clone produces NO_SIGNAL from check_continuation.py but valid output from goal_driver.py

### 5. Conflict Resolution is Implicit
No explicit mechanism resolves disagreements between the two task-selection systems. Plan lock is the only mechanism that overrides both, but only when a per-chat plan is active.

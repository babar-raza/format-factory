# Format Factory — Production-System Reconstruction and Continuous-Improvement Redesign

## Context

Format Factory is intended to turn governed format knowledge into production-grade, independently publishable libraries. The repository contains ~290 supervisor tools, ~202 Claude commands, ~219 governance validators, and ~522 mission events. Despite this machinery, the `main` branch CI fails across major jobs, the mission controller contains false certification labels that no gate rejects, continuation state cannot survive a clean clone, 18 distinct "skip failure and continue" rules ensure no control mechanism reliably blocks execution, and the reconciler that verifies obligations never executes a single test.

This plan defines:
1. A forensic investigation of what the machinery actually does (not what it claims)
2. An execution-ready repair plan to reduce it to one authoritative, bootstrappable, deterministic system where repeated execution produces measurable product progress

**This is not a documentation review, governance expansion sprint, or request for more validators.**

No production fixes during investigation. Investigate, execute, reconcile, then produce the repair plan.

The system must eventually support this loop:
```
CURRENT PRODUCT TRUTH → FIND HIGHEST-VALUE PRODUCT GAP → CREATE ONE PRECISE EXECUTABLE TASK
→ CLAIM IT SAFELY → IMPLEMENT PRODUCT DELTA → EXECUTE CURRENT PROOF → ACCEPT OR REJECT DELTA
→ UPDATE AUTHORITATIVE STATE → INVALIDATE AFFECTED DERIVATIONS → SELECT A DIFFERENT NEXT GAP
```

A run that merely creates prompts, plans, reports, validators, taskcards, events, projections, or orchestration code is not an improvement unless it removes a demonstrated product-delivery blocker and the official path immediately consumes the result.

**Assessed baseline commit:** `dd909cf3a9586a8a6b7a32c357011cd2557e3fae` (HEAD of main, unchanged)
**CI run inspected:** `https://github.com/babar-raza/format-factory/actions/runs/33321372202`

---

## Operational constraints

- Do not modify authoritative repository state during investigation. Run mutating tools in a disposable worktree or temporary repository copy.
- Do not commit or push unless explicitly authorized in the active session.
- Preserve unrelated working-tree changes.
- Do not use stash, reset, clean, or destructive checkout operations.
- Do not use report count, taskcard count, event count, test count, validator count, or generated-file count as a proxy for product progress.
- Do not use an event, report, status label, test name, or code comment as proof of the behavior it describes.
- Treat documentation, comments, status labels, certification flags, taskcard states, event histories, and previous audit conclusions as hypotheses until independently reconciled with code and executable evidence.

---

## Investigation leads (15 — each to be independently reproduced)

### Lead 1: Several incompatible control systems

At least six control paths exist:

**1a. Generic supervisor machinery:**
- `tools/supervisor/supervisor_loop.py`, `autonomous_cycle.py` (3,239 lines, 120 `except Exception` blocks), `check_continuation.py` (1,183 lines, 23+ STOP reasons), `generate_next_worker_prompt.py`
- State: `reports/supervisor/next-sprint.md`, `.local/supervisor/continuation-signal.json` (uncommitted)

**1b. Per-chat plan locking:**
- Plan locks under `.local/supervisor/plan-locks/`
- Precedence and override rules in `CLAUDE.md`

**1c. FF6 mission controller:**
- `tools/ff6/goal_driver.py`, `controller_events.py`
- State: `plans/strategic/ff6/controller-state.yaml`, `product-goal.yaml`, `events.jsonl` (522 events)
- FF6 obligation and evidence stores

**1d. Generic product-deepening machinery:**
- `tools/supervisor/lane_selector.py`, `autonomous_task_generator.py`, `dom_gap_generator.py`, `product_deepening_gate.py`, `capability_queue_consumer.py`, `action_queue.py`
- State: `registry/product-deepening-ledger.yaml`, `reports/capability-layer/gap-ledger.json`
- **Confirmed:** Deepening ledger does NOT contain any FF6 format (ipynb, ora, nrrd, xliff, safetensors, ubl). `lane_selector.py --format ipynb` returns format-not-found.
- **Confirmed:** Task generator has hardcoded expansion goals for ABW, DIF, FODG, TSV, NDJSON, Gnumeric — no FF6 awareness.

**1e. Plan Control:**
- `tools/plan_control/` (12 modules: engine, journal, projections, coordination, portfolio, etc.)
- State: `plans/.control/config.json` exists but `events.jsonl` is missing, projections directory absent
- **Confirmed:** `doctor` would fail immediately — journal doesn't exist. System is bootstrapped but never activated.

**1f. Legacy/alternative mechanisms:**
- `.supervisor/sprint-loop.md`, external-host/headless runners, committed session-resume reports, local operational index, older master-plan state, historical source-portfolio plans, `plans/codex/handover/` (frozen at Event 47, severely stale vs current Event 522)

**Investigation requirement:** Determine which one actually owns: the active mission, the next task, task claims, evidence acceptance, certification, continuation, and terminal status. Prove that identical repository state cannot lead two valid entry points to different work.

### Lead 2: Generic continuation is not bootstrappable

On a clean checkout, `check_continuation.py` returns `{"verdict": "STOP", "reason": "NO_SIGNAL"}` because `continuation-signal.json` is gitignored under `.local/`. All of `.local/supervisor/` (~115 files, ~220MB) is lost on clone.

**Confirmed:** The current signal is internally incoherent: `autonomous_continue: true` while `hard_stops_detected` has 2 items, `continuation_state: NO_MAX_ITERATIONS`, and `iteration: 14` exceeds `max_iterations: 12`.

**Confirmed:** Signal is created by `autonomous_cycle.py` Step 8 (lines 2605-2679). Nothing creates the first signal without a prior cycle run.

**Confirmed:** `sprint_executor.py` overrides `NO_SIGNAL` STOP via Supreme Directive (reads `next-sprint.md` directly). So the missing signal doesn't actually prevent execution — but the fallback bypasses all continuation state checking.

**Investigation requirement:** Reproduce from clean checkout. Determine who creates the first signal, whether the loop can start without a human-written declaration, whether committed state is sufficient, what happens after deleting `.local/`, whether iteration/session identity causes false STOP, which state survives a new machine or agent.

### Lead 3: Instructions bypass supposedly authoritative controls

**Confirmed: 18 distinct bypass/override rules in CLAUDE.md:**

| Category | Count | Effect |
|----------|-------|--------|
| Best-effort closeout rules | 5 | Evidence, autonomous-cycle, review package, declaration validation, architecture violations — all skippable |
| Exit code overrides | 3 | Exit 1, 3, 9 from autonomous_cycle → "continue regardless" |
| check_continuation.py failure | 2 | STOP for non-external-gate → override; tool failure → read next-sprint.md directly |
| STOP verdict overrides | 3 | Plan-context overrides, Supreme Directive scope |
| MAX_ITERATIONS | 2 | "Reset to 0, continue. Never treat as stop condition" |
| APPROVAL_GATE_NO | 1 | "Not a plan-switch" — continue plan taskcard |
| Supreme Directive limitations | 2 | GOV_BLOCK exception (6 structural validators), CCI non-overridable (4 reasons) |

**Confirmed: Of 23+ STOP reasons from check_continuation.py, only 6 are honored:**
1. `SESSION_MISMATCH` — CCI protection
2. `CHAT_ID_MISMATCH` — CCI protection
3. `POST_PLAN_TERMINAL` — plan boundary
4. `PLAN_COMPLETED_IN_SESSION` — plan boundary
5. `structural_govblock_must_be_resolved_first` — GOV_BLOCK exception
6. `gate_11_ready_pending_authorization` — TRUE_EXTERNAL_GATE

**The remaining 17+ reasons are overridden** by sprint_executor.py (lines 688-694): "Supreme Directive: overriding, reading next-sprint.md directly."

**Confirmed: 120 `except Exception` blocks in autonomous_cycle.py.** Only 1 (declaration validation at line 683) prevents state advancement. The other 119 log and continue. Even governance validator execution (line 1063), continuation signal write (line 2779), and evidence manifest generation (line 913) are non-blocking.

**Investigation requirement:** For every gate, answer: Does failure prevent mutation? Does failure prevent acceptance? Does failure prevent state advancement? Does failure prevent continuation?

### Lead 4: FF6 controller is deterministic but not truth-derived

**Confirmed:** `goal_driver.py` line 122: `"certified": promotion.get(format_id) == CERTIFIED` — reads promotion labels from `controller-state.yaml`, does NOT recompute from proof chains.

**Confirmed:** `controller-state.yaml` contains three mutually contradictory certification claims in the SAME file:
- `promotion:` block (lines 197-204): ipynb=CERTIFIED, nrrd=CERTIFIED, xliff=CERTIFIED, safetensors=CERTIFIED (4/6)
- `truth_boundary:` (lines 190-196): "All six products remain UNASSESSED and technical certification remains 0/6"
- `production_certifications:` (line 273): 0
- Every checkpoint: `promotion_effect: none`
- Line 113: "Do not claim certification for any format"

**Confirmed:** The real-state test (`test_real_mission_is_not_finished_and_says_so`, lines 226-235) uses a deliberately loose assertion: `0 <= certified_count < 6`, which accepts 4 even though the truth boundary says 0. The resume briefing test would print "4/6 certified" — misleading given truth_boundary says 0.

**Investigation requirement:** Test whether `goal_driver.py` returns `GOAL_ACHIEVED` when all six promotion strings are manually set to CERTIFIED, even if tests fail, reconciliation is stale, required proof is absent, package import fails, a product has unresolved obligations, or authoritative inputs changed.

### Lead 5: Valid event hash chain does not guarantee valid state

**Confirmed:** `controller_events.py` `verify` command (lines 413-425) calls `validate_chain()` (lines 128-158), which checks ONLY:
- Sequence numbers are 1-indexed and dense
- Required fields present
- SHA-256 hash integrity
- Chain linkage (previous_event_hash matches predecessor)

**Confirmed:** `sync_projection_head()` (lines 296-368) is "deliberately narrow" — it only syncs `transition_sequence`, `event_id`, and `event_hash`. Docstring (lines 307-310): "Every other section of the projection (the per-format checkpoints, gap summary, promotion table) encodes reviewed judgement about what an event *means* and is deliberately left to the author of the transition."

**Impact:** Chain can be PASS while projection semantics are false. A projection can contradict its last event. There is no mechanism to verify that promotion labels are derivable from the event journal.

**Investigation requirement:** Test whether chain can be valid while projection semantics are false; whether a projection can contradict its last event; whether an event can cite stale evidence; whether replay can rebuild complete controller state; whether promotion is actually derivable from the journal.

### Lead 6: FF6 reconciliation accepts historical PASS records, not current execution

**Confirmed:** `contract_reconciler.py` has two modes, neither executes tests:

**Heuristic mode** (`reconcile()`, lines 479-509): `_observe()` determines status from file/symbol existence via `ast.parse` (structural scan, no execution). Status ladder: NOT_STARTED → IMPLEMENTED_UNPROVEN → TESTED → ORACLE_PROVEN. Line 463: "test-file presence marks TESTED at most; execution evidence belongs to the evidence layer."

**Exact obligation mode** (`reconcile_obligations()`, lines 198-353): Validates that source symbols exist in AST, test selectors exist as files, execution evidence JSON files exist and their stored `result` matches declared expected result (line 272-274). Does NOT execute those selectors.

Status: `implemented` → `SUPPORTED_NONPROMOTING`. Yet goal driver separately trusts promotion strings.

**Investigation requirement:** Prove whether: historical transcript says PASS → current product test fails → reconciler still reports obligation implemented → goal driver still reports format certified. Identify the missing freshness or invalidation edge.

### Lead 7: Current FF6 tests contradict implemented/certified state

Previous execution of all six FF6 format test suites after clean editable installation:
- Core must be installed first (`pip install -e src/python/core`) — unpublished dependency `format-factory-core==0.1.0.dev0` cannot be resolved otherwise
- Initial run: 4,916 passed, 60 skipped, 88 failed
- After installing schema/reference extras: 254 passed, 7 failed
- Remaining 7 failures are current IPYNB failures: timeout execution loses completed cell output, 3 active corpus hashes disagree, 2 quarantine corpus hashes disagree, redistribution-license hash disagrees

At least one implemented obligation cites `test_timeout_preserves_partial_output_from_completed_cells` even though that selector currently fails. Reconciliation still reports 68/68 IPYNB obligations implemented. Promotion remains CERTIFIED.

**Investigation requirement:** Determine when test last passed, when source/fixtures changed, why evidence was not invalidated, why reconciliation still reports 68/68, why promotion remains CERTIFIED, whether CI runs necessary extras, whether Windows-only path assertions make tests platform-specific.

### Lead 8: ORA namespace disagreement

**Confirmed:** `product-goal.yaml` (lines 19-22) declares:
```yaml
import_namespace: format_factory.openraster
```

**Confirmed:** Actual installed package namespace is `format_factory.ora` — confirmed by `src/python/ora/pyproject.toml` line 44: `include = ["format_factory.ora*"]` and directory structure `src/python/ora/src/format_factory/ora/`.

`format_factory.openraster` → ModuleNotFoundError. `format_factory.ora` → available.

**Investigation requirement:** Determine intended stable API and all consumers of both names. This is a contract defect across mission state, package metadata, documentation, tests, and downstream users.

### Lead 9: UBL obligation totals drift

FF6 controller previously declared 194 UBL obligations; current obligation register and goal-driver calculation observed 195.

**Investigation requirement:** Reconcile contract capability count, obligation-register count, controller snapshot count, evidence-ledger count, reconciliation count, certification denominator, and event history. Determine why digest-valid snapshots can contain stale embedded summaries.

### Lead 10: Fresh reconciliation differs from committed reports

Exact reconciliation called twice in memory produced identical output per format. However, the newly computed result was not semantically equal to the committed reconciliation JSON for any of the six formats.

**Investigation requirement:** Investigate exactly which fields differ: source digests, test-file digests, evidence-artifact digests, ordering, summaries, selectors, proof status, input inventories. Determine why committed derived reports are not invalidated or regenerated before task selection and certification.

### Lead 11: Evidence-ledger rebuild is not idempotent

Previous `pytest -q tests/ff6` produced: 87 passed, 2 failed. Failures included SafeTensors evidence-ledger rebuild not reproducing committed data and stale-lease planning receiving a `None` coordination snapshot.

**Confirmed:** The FI-075/FI-078 fix in `build_evidence_ledger.py` preserves hand-curated `implemented` rows by reading the current evidence file before rebuilding. The test compares parsed YAML not raw text. Non-idempotency arises from filesystem changes between runs or failures in the preservation logic.

**Investigation requirement:** Determine whether "implemented" rows are genuinely preserved, whether referenced execution evidence is dropped or reordered, whether rebuild behavior depends on current files, whether dry-run exercises exactly the same transformation, whether tests mutate tracked artifacts, whether failure cleanup restores exact original bytes.

### Lead 12: A documented dry-run mutates tracked state

**Confirmed:** `autonomous_task_generator.py` dry-run bug:
- `main()` (line 2007-2011) passes `output_path=None` when `--dry-run`
- `generate_task_candidates()` (line 1705): `output_path = output_path or DEFAULT_OUTPUT` — None becomes `product-task-candidates.json`
- Lines 1926-1928: unconditional file write
- Additionally, the zero-task circuit breaker (lines 1890-1896) writes `.zero-task-counter.json` unconditionally regardless of dry-run

**Investigation requirement:** Audit every command advertising `--dry-run`, `--check`, `--validate`, `--doctor`, `--status`, `--resume`. Use filesystem snapshots and git diffs to prove whether each is read-only.

### Lead 13: Generic task selection ignores the active FF6 mission

**Confirmed:** Generic task-generator dry run selected ABW and DIF work. Generic deepening ledger does not contain IPYNB — `lane_selector.py --format ipynb` returns format-not-found. The generic product-deepening gate covers older formats, not the FF6 set.

**Investigation requirement:** Determine whether generic automation can divert work from FF6; whether the two systems use incompatible maturity models; whether both can mutate the same product paths; whether neither sees the other's accepted deltas; whether starvation controls operate across missions or only inside one ledger.

### Lead 14: Plan Control is present but starts empty

**Confirmed:** `plans/.control/config.json` exists, `events.jsonl` does NOT exist. `plans/.control/projections/` does NOT exist. `.local/plan-control/locks/` exists but is empty.

FF6 state itself records schema incompatibility with Plan Control.

**Investigation requirement:** Determine whether Plan Control is the intended future authority, a dormant proof of concept, a partially deployed replacement, or another redundant control plane.

### Lead 15: Governance currently blocks, but operating rules bypass it

Previous run of `run_ci_governance_check.py` returned: fail=8, warn=38, pass=165, blocks=True, total=211, exit=1.

**Confirmed enforcement gaps:**
- No evidence `governance-check` is a required status check in GitHub branch protection — merging is not prevented
- Autonomous loop checks only `check_continuation.py`, not governance validators, before continuing
- Governance validators run INSIDE `autonomous_cycle.py` Step 2e (line 1049) AFTER sprint work is done — not a pre-execution gate
- When governance `blocks_sprint=True`, exit code is 3, and CLAUDE.md says "Exit 3 → continue regardless"
- `capability-parity` CI job uses `continue-on-error: true`

**Investigation requirement:** Establish whether blocking governance result prevents: source commits, event append, evidence acceptance, promotion changes, continuation, release. If not, state precisely where enforcement is missing.

---

## Required repository reading

Read completely before designing repairs (verified: all exist):

**Strategic/mission:**
- README.md, AGENTS.md, CLAUDE.md, GOVERNANCE.md, ROADMAP.md, PROJECT_STATUS.md
- plans/README.md, plans/master-plan.md, plans/master-plan-memory.md
- plans/plan-hardening-addendum-from-latest-audit.md
- plans/strategic/autonomous-six-python-production-execution-plan.md
- plans/strategic/ff6/ (product-goal.yaml, controller-state.yaml, current-state.yaml, current-gaps.yaml, execution-recovery-directive.yaml, events.jsonl)
- plans/codex/handover/START-HERE.md, plans/codex/handover/checkpoint.yaml

**Automation/governance docs:**
- docs/automation/operational-control-index.md
- docs/automation/autonomous-continuation-policy.md
- docs/automation/autonomous-supervision-replication-guide.md
- docs/automation/fresh-chat-project-bootstrap.md
- docs/automation/supervisor-failure-recovery.md
- docs/governance/current-state-and-evidence-authority.md
- docs/governance/master-plan-canonical-source-map.md
- docs/governance/product-first-operating-model.md
- docs/governance/spec-to-product-machinery-routing.md
- docs/governance/autonomous-execution-contract.md
- docs/governance/autonomous-stop-reason-policy.md
- docs/governance/repeatability-contract.md
- docs/governance/idempotency-contract.md
- docs/governance/proof-authority-policy.md
- docs/governance/sprint-depth-policy.md
- docs/python-foss/spec-to-source-chain-contract.md
- docs/code-quality/capability-layer-design.md
- docs/code-quality/capability-feature-compiler-spec.md
- docs/format-contract-layer.md

**Supervisor config:**
- .supervisor/README.md, .supervisor/sprint-loop.md
- .supervisor/policies.yaml, .supervisor/config.yaml
- .supervisor/autonomy-boundary-contract.yaml
- reports/supervisor/session-resume.md, reports/supervisor/latest-cycle-summary.md
- docs/system-recon/supervisor-machinery-audit/

**Inventory and classify (build provenance/index first, then read authoritative inputs, latest outputs, conflicting outputs, representative historical chain):**
- tools/supervisor/, tools/ff6/, tools/plan_control/, tools/format_contract/, tools/governance/, tools/evidence/, tools/skills/
- .claude/commands/, .supervisor/, registry/, reports/, plans/, taskcards/
- shared/format-contracts/, oracle/, packaging/, .github/workflows/

---

## Investigation phase 1: Establish the real product model

**Objective:** What Format Factory is, who uses it, what "production-ready" means, and which documents are normative vs derived vs stale.

**Determine:**
- Intended users of each format library
- Supported formats and languages
- Minimum common lifecycle
- Format-specific capabilities
- Breadth and depth definitions
- Maturity models currently in use
- Production-ready definition
- Certification definition
- Release versus publication boundary
- Downstream consumer expectations

**For the six FF6 libraries, produce a current product matrix:**

| Format | Distribution | Declared namespace | Actual namespace | Source present | Tests current | Obligations | Current proof | Real certification |
|--------|-------------|-------------------|-----------------|---------------|--------------|------------|--------------|-------------------|

Real certification must NOT be derived from the existing promotion label.

**Authority graph (required table format):**

| Concern | Candidate sources | Writers | Readers | Current winner | Conflict behavior | Freshness rule |
|---------|------------------|---------|---------|----------------|-------------------|----------------|

Cover: active mission, active plan, current task, task state, worker ownership, capability definition, obligation definition, implementation state, test result, evidence acceptance, gap state, format maturity, certification, continuation, terminal state, release state.

Find every duplicated authority and every derived artifact that is trusted as authority.

**Produce:**
- `01-product-definition.md` — what the product is, users, operations each library must support, what "certified" means
- `02-authority-matrix.md` — authority graph table for all 16 concerns above, plus: recommended single authority per concern, migration plan for retiring the others
- `03-document-classification.md` — classify every controlling document as NORMATIVE / DERIVED / ADVISORY / HISTORICAL / STALE / CONTRADICTORY

---

## Investigation phase 2: Build the actual invocation graph

**Objective:** For every significant component, determine reachability and authority.

**Inventory scope:** tools/supervisor/ (~290), tools/ff6/ (5), tools/plan_control/ (12), tools/format_contract/, tools/governance/, tools/evidence/, tools/skills/, .claude/commands/ (~202), .supervisor/, registry/, reports/, plans/, taskcards/, shared/format-contracts/, packaging/, .github/workflows/

**Classification per component:**
- official production entry point
- indirectly production-reachable
- fallback-reachable
- manual-only
- test-only
- generated but unconsumed
- obsolete but reachable
- obsolete and unreachable
- unknown

Prove reachability using callers, command definitions, workflow invocations, and runtime tracing. A test import is not production reachability.

**Produce:**
- `04-machinery-inventory.csv` — Component, Purpose, Inputs, Outputs, Mutations, Called-by, Calls, Official-path?, Production-reachable?, Duplicate-of, Failure-semantics
- `05-invocation-graph.md` — static + experimentally verified call graph from official entry point to final product mutation and state advancement. Distinguish test-only from production reachability.

---

## Investigation phase 3: Trace every continuation path and execute clean-start experiments

**Objective:** Trace all continuation paths, prove where two valid entry paths choose different work from the same repo state, and execute clean-start and repeatability experiments.

**Paths to trace (at least 10):**
1. Generic supervisor continuation (check_continuation.py → next-sprint.md)
2. Plan-locked continuation (write_plan_lock.py → active-plan-lock.json)
3. FF6 goal-driver continuation (goal_driver.py → controller-state.yaml)
4. Generic product-deepening (lane_selector.py → product-deepening-ledger.yaml)
5. Autonomous task generator (autonomous_task_generator.py → hardcoded _EXPANSION_GOALS)
6. Plan-control system (tools/plan_control → plans/.control/events.jsonl)
7. Legacy sprint-loop (supervisor_loop.py → .supervisor/state/)
8. Headless/external-host (sprint_executor.py → claude --print subprocess)
9. GitHub Actions (ci.yml → multiple jobs)
10. Manual/human taskcard execution

**For each path record:** entry point, state read, state written, task-selection algorithm, ownership mechanism, verification gates, bypasses, fallbacks, terminal conditions, restart behavior, crash recovery, idempotency, concurrency behavior, stale-state behavior, whether it makes product progress.

**Decision table:** What path does an agent follow under: clean checkout, missing signal, stale signal, session mismatch, iteration exhaustion, active plan lock, completed plan, FF6 active, empty queue, validator failure, evidence failure, CI failure, external gate, context exhaustion, interrupted process, concurrent workers.

**Experiments (in disposable worktree) — capture command, working directory, environment, inputs, exit code, stdout/stderr, files changed, state changed, time taken, second-run result for each:**

1. Clean-clone bootstrap
2. Generic continuation check
3. FF6 goal-driver check/resume
4. Plan Control doctor/reconcile/next
5. Generic task-generator dry run (verify mutation)
6. Lane-selector and product-deepening checks for FF6 formats
7. FF6 event-chain verification
8. Exact reconciliation for all six formats (compare to committed reports)
9. Evidence-ledger rebuild tests
10. Current governance suite
11. Current CI-equivalent setup
12. Package build/install (core first, then six FF6 packages)
13. Full six-format tests with complete extras
14. Installed-wheel smoke tests
15. Realistic public-API transactions

Test commands twice and compare: output bytes, selected task, state mutation, generated artifact digest, queue state, evidence state.

**Produce:**
- `06-continuation-paths.md` — all paths traced
- `07-continuation-decision-table.md` — decision matrix
- `08-first-divergence-point.md` — first point where two valid paths choose different work
- `09-execution-results.md` — exact commands, exit codes, mutations, rerun results, discrepancies

---

## Investigation phase 4: Trace two formats completely

**Objective:** Prove the complete chain for IPYNB (marked certified while current tests fail) and ORA (unassessed with namespace disagreement and unresolved obligation).

**For each trace:**
```
authority artifact → SAL fact → compiled contract → capability → obligation
→ implementation-evidence row → source symbol → positive selector → negative selector
→ historical execution artifact → current execution → reconciliation
→ promotion/certification → next-task selection
```

**Identify every handoff where the consumer does not validate the producer's freshness or semantics.**

**For every edge prove:** producer, consumer, identifier/schema, update mechanism, invalidation rule, failure behavior, whether consumer actually reads producer's output, whether stale evidence is rejected, whether a filename can masquerade as executed proof.

**IPYNB-specific:** Trace why reconciliation reports 68/68 implemented while `test_timeout_preserves_partial_output_from_completed_cells` currently fails and 3+ corpus hashes disagree.

**ORA-specific:** Trace the `format_factory.openraster` vs `format_factory.ora` namespace through product-goal.yaml, pyproject.toml, import paths, test suites, documentation, and downstream consumers.

**Produce:**
- `10-proof-chain-ipynb.md` — full trace for a "CERTIFIED" format with failing tests
- `11-proof-chain-ora.md` — full trace for UNASSESSED format with namespace mismatch
- `12-proof-chain-gaps.md` — all edges where consumer doesn't read producer, stale evidence accepted, or filename substitutes for execution

---

## Investigation phase 5: Prove real product behavior

**Objective:** For each of the six FF6 packages, execute an installed-distribution scenario using its public namespace.

**For each package:**
```
real or authoritative sample → probe → load → inspect typed/domain model
→ edit or create → validate → save → reload → assert semantic preservation
→ exercise a format-specific advanced capability
```

Where supported, also prove: conversion/export, lazy/streaming access, resource-limit enforcement, corruption rejection, independent implementation interoperability, co-installation with all six packages.

Do not count source-tree imports as installed-wheel proof.

**Produce:**
- `13-product-behavior-proof.md` — six-format installed-distribution scenarios with results
- `14-productive-cycle-scorecard.md` — before/after metrics:

| Metric | Before | After | Evidence |
|--------|--------|-------|----------|
| Stable obligations proven | | | |
| Mandatory obligations unresolved | | | |
| Capabilities at each maturity level | | | |
| Real corpus cases | | | |
| Independent oracle cases | | | |
| Installed-wheel E2E scenarios | | | |
| Downstream consumer scenarios | | | |
| Known false claims | | | |
| Stale evidence rejected | | | |
| Product defects closed | | | |
| Duplicate machinery paths removed | | | |

---

## Investigation phase 6: Root cause analysis and disposition

**Objective:** Correctly separate findings, identify preservation candidates, and produce the machinery disposition.

### Correct problem separation

**Report separately:**

**Symptoms** — visible effects only (red CI, stale reports, repeated work, contradictory statuses, wrong next tasks).

**Immediate defects** — concrete code/configuration defects (dry-run mutation, namespace mismatch, stale hashes, missing extras, failing timeout implementation).

**Root causes** — earliest failing control boundary (e.g., manually asserted promotion bypassing current evidence derivation). For each: evidence, first failing boundary, scope, why controls missed it, confidence.

**Structural weaknesses** — recurrence and inconsistent repeated-run behavior (multiple task authorities, mutable projections, local-only continuation truth, no transactional acceptance, disconnected deepening systems). Explain the governance and integration conditions that allowed machinery to accumulate without replacing prior paths.

**Evidence gaps** — what could not be proven.

Do not describe repository size or "too much machinery" as a root cause.

### Preservation evaluation

Evaluate (not automatically replace):
- FF6 obligation registers
- Format-specific contracts
- Append-only event history
- Exact selector mapping
- Hash-bound authority artifacts
- Installed-wheel proof concept
- Independent oracles
- Resource/security testing
- Action-queue locking
- Plan Control's journal/projection concepts
- Existing public package implementations
- Current passing product tests

For each: exact proof it works and the boundary of that proof. Preserve only the useful responsibility, not necessarily its current implementation or duplicated subsystem.

### Machinery disposition register

For every major subsystem choose: PRESERVE / REPAIR / MERGE / CONTAIN / RETIRE / UNKNOWN. Include evidence and migration dependencies.

**Produce:**
- `15-root-cause-register.md` — for every finding: classification (symptom / defect / condition / root-cause / weakness / missing-control / gap / unrelated), evidence, first failing boundary, affected scope, why controls missed it, confidence, unknowns, evidence that would change conclusion
- `16-preservation-register.md` — components with runtime proof, disposition, proof boundary
- `17-machinery-disposition.md` — subsystem-level decisions with evidence

---

## Target production design requirements

### One authoritative mission store

Must contain or derive: stable mission identity, target formats, product goals, canonical capability and obligation baseline, accepted current evidence, invalidation dependencies, current executable work, active claims/leases, blockers, transition history, derived certification. Human-readable reports must be projections only.

### One official command

A clean clone must have one documented command that:
1. Validates/bootstraps environment
2. Reconstructs current state from committed files
3. Refreshes stale derived artifacts
4. Checks invalidation
5. Selects exactly one eligible task
6. Claims it atomically
7. Emits an executable task contract
8. Executes or hands off through governed worker
9. Verifies current behavior
10. Accepts or rejects the result
11. Recomputes product state
12. Selects the next task

No local signal may be required to reconstruct mission truth.

### One breadth-and-depth scheduler

Must select among: unresolved normative obligations, missing user-facing capabilities, shallow implementation depth, missing negative/security/resource behavior, weak corpus coverage, weak oracle/interoperability depth, packaging/downstream deficiencies, confirmed defects, invalidated evidence.

Each work item must declare its expected measurable product delta before execution.

### Derived certification

Certification must be a pure, fail-closed computation from current accepted evidence. A manually written CERTIFIED string must have no authority.

Certification must regress automatically when: source changes, tests change, corpus changes, oracle changes, dependency versions change, package proof becomes stale, a required selector fails, an obligation baseline expands, an accepted policy exception expires.

### Transactional state transitions

Explicit states:
```
DISCOVERED → SPECIFIED → READY → CLAIMED → IMPLEMENTED → CURRENTLY_VERIFIED → ACCEPTED → CERTIFIED
```
Plus: INVALIDATED, RETRYABLE_FAILURE, BLOCKED_INTERNAL, BLOCKED_EXTERNAL, SUPERSEDED, ABANDONED.

No report or transcript may advance state by existence alone.

### Product-progress invariant

A completed cycle must record at least one accepted delta: obligation closed, capability added, depth level increased, defect fixed, current proof strengthened, false claim removed, obsolete blocking machinery retired. Otherwise classify as `NO_PRODUCT_PROGRESS`.

Repeated no-progress machinery cycles must trip a circuit breaker.

### Machinery budget

Machinery work must identify: the product bottleneck it removes, the official consumer, the immediate product experiment it unlocks, its deletion/containment plan if the experiment fails.

### Failure semantics

Replace "best effort and continue" with typed outcomes: retryable-failure, invalid-input, stale-state, evidence-failure, product-regression, infrastructure-failure, true-external-blocker, operator-intervention-required. Only explicitly advisory operations may fail without blocking.

### Recovery

Clean clone reconstructs active mission, accepted progress, next work, blockers, invalidated evidence from committed files alone.

### Observability

Structured records for task selection, state reads, evidence produced/rejected, product delta, state transitions, retries, invalidation, certification computation, downstream proof.

---

## Required repair plan (20 items, dependency-ordered)

**Every item below includes:** root cause addressed, exact files/components, dependencies, expected product effect, tests, rollback, completion evidence. Three additional fields are required per item during execution:
- **State migration:** How existing state (signals, locks, events, evidence, projections) is preserved or converted during the change.
- **Compatibility safeguards:** What existing consumers (tests, workflows, commands, external agents) must keep working during the transition; verification steps.
- **Out of scope:** What related problems this item deliberately does NOT address; where those are tracked instead.

These three fields are populated during investigation (not in advance) because their content depends on the machinery inventory, authority graph, and invocation graph findings.

### R1: Freeze new control-plane expansion
- **Root cause:** Machinery accumulation without replacing prior paths
- **Files:** No files modified — establish read-only baseline
- **Exact action:** Pin assessed commit, capture baseline CI/env/state, document all active control systems
- **Expected product effect:** No new machinery until existing paths are reconciled
- **Tests:** N/A — policy item
- **Produce:** `00-baseline.md`
- **Dependencies:** None
- **Rollback:** N/A

### R2: Establish one authority decision record
- **Root cause:** 6+ competing control systems with no documented ownership resolution
- **Files:** New decision record under `docs/` or `plans/`
- **Exact action:** For every concern (mission, task, claim, evidence, certification, continuation, terminal), record: single authority, migration plan for retiring the others
- **Expected product effect:** Every future question "who decides X" has one answer
- **Dependencies:** R1
- **Rollback:** Remove decision record

### R3: Add contradiction gate over current repository state
- **Root cause:** controller-state.yaml contains three-way contradiction, PROJECT_STATUS.md self-contradicts, continuation-signal.json is incoherent
- **Files:** `tools/ff6/controller_state_validator.py` (new), tests
- **Exact action:** Fail-closed validator that checks promotion vs truth_boundary vs production_certifications vs checkpoints. Must block if any pair disagrees.
- **Expected product effect:** Contradictory state is detected before any downstream consumer trusts it
- **Dependencies:** R1
- **Rollback:** Remove validator
- **Completion evidence:** Test with current contradictory state must FAIL; test with consistent state must PASS

### R4: Remove manual certification authority
- **Root cause:** `goal_driver.py` line 122 reads `promotion.get(format_id) == CERTIFIED` — a manually editable string
- **Files:** `tools/ff6/goal_driver.py`, `plans/strategic/ff6/controller-state.yaml`
- **Exact action:** Delete promotion block as certification source. Goal driver must compute certification from proof chain.
- **Expected product effect:** Setting promotion=CERTIFIED without proof cannot produce GOAL_ACHIEVED
- **Dependencies:** R3 (contradiction gate catches current state first)
- **Rollback:** Revert goal_driver.py
- **Completion evidence:** Negative control — promotion=CERTIFIED with missing proof → NOT certified

### R5: Recompute certification from current evidence
- **Root cause:** Certification is a stored label, not a derived computation
- **Files:** `tools/ff6/goal_driver.py`, `tools/ff6/certify.py` (new or integrated)
- **Exact action:** Certification = all obligations at IMPLEMENTED with current test PASS + current reconciliation match + package installable + no unresolved blockers. Must fail closed on any missing input.
- **Expected product effect:** Accurate, current certification count
- **Dependencies:** R4
- **Rollback:** Revert certification logic
- **Completion evidence:** Current state produces 0/6 certified (matching truth_boundary and production_certifications)

### R6: Add evidence dependency hashes and invalidation
- **Root cause:** Reconciler checks stored results, not current execution. Evidence is never invalidated when source, tests, or corpus change.
- **Files:** `tools/format_contract/contract_reconciler.py`, evidence stores
- **Exact action:** Each accepted evidence record stores hash of source file, test file, and corpus file at acceptance time. Evidence auto-invalidates when any hash changes.
- **Expected product effect:** Stale evidence cannot masquerade as current proof
- **Dependencies:** R5
- **Rollback:** Remove hash fields (evidence records still function without them)
- **Completion evidence:** Modify a source file → evidence invalidated → certification regresses

### R7: Make clean-clone bootstrap authoritative
- **Root cause:** All of `.local/` is gitignored; `check_continuation.py` returns NO_SIGNAL on clean clone; 17 bypass rules override the STOP but bypass all state checking
- **Files:** New or consolidated entry point under `tools/`
- **Exact action:** One command that reads only committed files to determine mission state, next work, and blockers. Must not depend on `.local/` state for correctness (only for optimization/caching).
- **Expected product effect:** Any fresh agent on any machine computes identical next action from identical committed state
- **Dependencies:** R2 (single authority established), R5 (correct certification)
- **Rollback:** Remove new entry point
- **Completion evidence:** Delete `.local/`, run command, get correct mission state and next task

### R8: Repair dry-run and read-only command contracts
- **Root cause:** `autonomous_task_generator.py` line 1705: `output_path = output_path or DEFAULT_OUTPUT` converts dry-run None to real write; circuit breaker writes unconditionally
- **Files:** `tools/supervisor/autonomous_task_generator.py`, and audit all commands with `--dry-run`, `--check`, `--validate`, `--doctor`, `--status`, `--resume`
- **Exact action:** Propagate dry-run flag into all mutation functions. No read-only command may write any file.
- **Expected product effect:** Diagnostic commands are safe to run
- **Dependencies:** R1
- **Rollback:** Revert each file
- **Completion evidence:** Git diff after each dry-run command shows zero changes

### R9: Repair FF6 current product failures
- **Root cause:** IPYNB timeout loses completed cell output (implementation bug), corpus hash disagreements (fixture drift), test extras incomplete
- **Files:** `src/python/ipynb/`, `tests/python/ipynb/`, relevant obligation evidence files
- **Exact action:** Fix timeout implementation, update or regenerate corpus fixtures, ensure [test] extras install all required dependencies
- **Expected product effect:** 0 failures in `pytest tests/python/ipynb/` with full extras
- **Dependencies:** R1
- **Rollback:** Revert source changes
- **Completion evidence:** Full test suite passes, evidence ledger updated

### R10: Normalize package test extras and CI environments
- **Root cause:** CI runs `pip install -e ".[dev]"` only — gen-2 packages never installed, `jsonschema`/`nbformat` never available; gen-2 requires ≥3.11 but root requires ≥3.9
- **Files:** `.github/workflows/ci.yml`, `pyproject.toml`, gen-2 pyproject.toml files
- **Exact action:** Add gen-2 package installations to CI, add missing transitive dependencies, resolve Python version conflict, add dependency lock file
- **Expected product effect:** CI tests the same packages that are published
- **Dependencies:** R1
- **Rollback:** Revert CI/pyproject changes
- **Completion evidence:** CI installs all six FF6 packages and their test extras, all format tests run

### R11: Resolve ORA namespace authority
- **Root cause:** `product-goal.yaml` says `format_factory.openraster`, actual package is `format_factory.ora`
- **Files:** `plans/strategic/ff6/product-goal.yaml`, ORA package metadata, documentation, any consumers of either namespace
- **Exact action:** Determine intended stable API. Update all references to match the chosen name. Add import-namespace validation test.
- **Expected product effect:** One namespace, importable, documented, tested
- **Dependencies:** R1
- **Rollback:** Revert namespace changes
- **Completion evidence:** `python -c "from format_factory.<chosen> import ..."` succeeds

### R12: Reconcile UBL obligation denominator
- **Root cause:** Controller says 194, register/goal-driver says 195 — stale embedded summary in digest-valid snapshot
- **Files:** `plans/strategic/ff6/controller-state.yaml`, UBL obligation register, evidence ledger
- **Exact action:** Reconcile all counts to current register. Add count-consistency test.
- **Expected product effect:** One obligation count, everywhere
- **Dependencies:** R1
- **Rollback:** Revert count changes
- **Completion evidence:** All sources agree on UBL obligation count

### R13: Make evidence-ledger rebuild byte- or semantic-idempotent
- **Root cause:** YAML round-trip formatting changes, filesystem-dependent ordering, preservation logic edge cases
- **Files:** `tools/ff6/build_evidence_ledger.py`, tests
- **Exact action:** Ensure rebuild from identical inputs produces identical parsed output. Sort deterministically. Pin YAML emitter options.
- **Expected product effect:** `test_real_safetensors_ledger_rebuilds_identically` passes
- **Dependencies:** R1
- **Rollback:** Revert ledger builder changes
- **Completion evidence:** Two consecutive rebuilds produce identical output

### R14: Integrate or retire Plan Control
- **Root cause:** Plan Control exists as 12-module system with own journal, state machine, task queue — but is bootstrapped-only (no journal, no projections) and incompatible with FF6
- **Files:** `tools/plan_control/`, `plans/.control/`
- **Exact action:** Based on R2 authority decision — either adopt Plan Control's journal/projection concepts into the single authority, or formally retire the subsystem
- **Expected product effect:** One fewer competing control path
- **Dependencies:** R2, R7
- **Rollback:** Reverse retirement/integration
- **Completion evidence:** `python -m tools.plan_control doctor` either works as the authority or no longer exists

### R15: Integrate or retire the generic deepening path
- **Root cause:** Generic deepening (lane_selector, task_generator, deepening_gate) and FF6 are completely disconnected — different format sets, no cross-references
- **Files:** `tools/supervisor/lane_selector.py`, `autonomous_task_generator.py`, `registry/product-deepening-ledger.yaml`
- **Exact action:** Either extend chosen authority to cover all formats, or formally scope each system with explicit boundary and no product-path overlap
- **Expected product effect:** No path can silently divert work from the active mission
- **Dependencies:** R2, R14
- **Rollback:** Reverse changes
- **Completion evidence:** Generic task generator cannot select work for FF6-governed formats

### R16: Consolidate continuation and task selection
- **Root cause:** 23+ STOP reasons, 17+ overridden by Supreme Directive, 120 except-and-continue blocks, 18 CLAUDE.md bypass rules
- **Files:** `CLAUDE.md`, `tools/supervisor/sprint_executor.py`, `autonomous_cycle.py`, `check_continuation.py`
- **Exact action:** Replace "best effort and continue" with typed failure semantics. Remove Supreme Directive override of non-external-gate STOP reasons. Make validators fail-closed by default.
- **Expected product effect:** A failing validator prevents state advancement, not just generates a warning
- **Dependencies:** R2, R7, R14, R15
- **Rollback:** Revert CLAUDE.md and tool changes
- **Completion evidence:** Governance failure prevents continuation; only TRUE_EXTERNAL_GATEs remain as legitimate stops

### R17: Implement breadth/depth scheduling
- **Root cause:** No unified scheduler balances obligations, capabilities, depth, defects, and evidence across all formats
- **Files:** New scheduler module or integrated into single authority
- **Exact action:** Scheduler selects among unresolved obligations, missing capabilities, shallow depth, weak corpus, defects, invalidated evidence. Each work item declares expected delta.
- **Expected product effect:** Repeated execution improves different dimensions without starvation
- **Dependencies:** R7, R16
- **Rollback:** Remove scheduler
- **Completion evidence:** Three consecutive runs select different work targeting different product gaps

### R18: Prove one complete vertical cycle
- **Root cause:** No evidence that the complete chain (clean start → task selection → implementation → test → acceptance → state update → next run sees delta) works end to end
- **Files:** One FF6 format's complete chain
- **Exact action:** Execute the full chain for one format through the new architecture. Document every step with evidence.
- **Expected product effect:** One format demonstrably improved, state updated, next run selects different work
- **Dependencies:** R5, R6, R7, R10, R17
- **Rollback:** Revert format changes
- **Completion evidence:** The proof chain from the target design is fully executed and documented

### R19: Migrate remaining formats
- **Root cause:** Only one format proven in R18
- **Files:** Remaining five FF6 format chains
- **Exact action:** Apply R18 pattern to remaining FF6 formats
- **Dependencies:** R18
- **Rollback:** Per-format revert
- **Completion evidence:** All six formats exercised through complete chain

### R20: Contain and then delete obsolete paths
- **Root cause:** Accumulated machinery paths that were never formally retired
- **Files:** Identified obsolete components from investigation phase 2 and machinery disposition
- **Exact action:** Prove no official consumers remain for each path. Contain (quarantine imports, add deprecation telemetry). Then delete after confirmation period.
- **Expected product effect:** Reduced machinery footprint, fewer competing authorities
- **Dependencies:** R14, R15, R16, R18
- **Rollback:** Restore deleted files from git
- **Completion evidence:** Removed components' former entry points produce clear error messages; no test or workflow references them

---

## Required verification suite

### State and authority
- Real-state contradiction tests (promotion vs truth_boundary vs production_certifications)
- Journal-to-projection replay tests
- Projection tampering tests (edited label without proof → rejected)
- Certification false-positive negative control (promotion=CERTIFIED + no proof → NOT certified)
- Deterministic-but-stale negative control (deterministic output from stale input → detected)
- FF6-versus-generic authority conflict test

### Bootstrap and determinism
- Clean-clone bootstrap (fresh clone → correct mission state)
- Deleted-local-state recovery (delete `.local/` → correct state reconstructed)
- Repeated selection determinism (identical selection from identical state)
- Productive-delta test (run produces measurable improvement)
- No-progress circuit breaker (repeated no-product-progress → blocked)
- Dry-run non-mutation (every read-only command → zero git diff)
- Evidence-rebuild idempotency

### Recovery and concurrency
- Interrupted-write recovery
- Restart recovery (same work, not duplicate)
- Concurrent claims (one owner, no duplicate completion)
- Lease expiry
- Duplicate completion suppression
- Stale-evidence invalidation

### Package and product
- Installed-wheel E2E (real pip install, not sys.path injection)
- Public namespace tests (no shadow packages, correct import name)
- Package co-installation (all six FF6 packages installed simultaneously)
- Realistic corpus tests
- Independent oracle tests
- Downstream consumer tests
- Security/resource bounds
- Performance regression
- CI parity across supported Python versions

### Official proof chain
```
REAL INPUT → OFFICIAL CLEAN-START COMMAND → AUTHORITATIVE CURRENT STATE
→ DETERMINISTIC GAP SELECTION → ATOMIC TASK CLAIM → PRODUCT CHANGE
→ CURRENT TEST EXECUTION → CURRENT ORACLE/CORPUS/PACKAGE PROOF
→ ACCEPTED STATE TRANSITION → DERIVED CERTIFICATION
→ DOWNSTREAM CONSUMER → OBSERVED RESULT → NEXT RUN SELECTS NEW WORK
```

### Freshness and invalidation
- Current-selector execution (run the actual test selector cited by an obligation — does it pass?)
- Evidence invalidation (source hash changes → evidence auto-invalidated)
- Obligation-baseline expansion (new obligation → certification regresses)
- Projection replay (rebuild projection from journal → matches stored projection?)
- Projection tampering (edit promotion label without proof → fail-closed rejection)

### Additional negative controls
- Failed-test rejection (test fails → evidence not accepted)
- Deterministic-but-stale negative control (deterministic output from stale input → detected)
- Breadth starvation (no format starved for >N cycles)
- Depth starvation (no dimension starved for >N cycles)

---

## Required output structure

### Assessment scope
Commit assessed, environment, product mission, users, formats, inputs, outputs, consumers, evidence inspected, commands executed, missing evidence.

### Intended system
What Format Factory is supposed to produce and what a successful repeated cycle means.

### Authority map
All competing sources of truth and the actual precedence observed.

### Current execution reconstruction
Trace every official, fallback, mission-specific, and legacy path.

### Product proof reconstruction
Complete IPYNB and ORA traces plus six-format matrix.

### Execution results
Exact commands, exit codes, mutations, rerun results, discrepancies.

### Symptoms
Visible effects only.

### Immediate defects
Concrete code/configuration defects.

### Confirmed root causes
For each: evidence, first failing boundary, scope, why controls missed it, confidence.

### Structural weaknesses
Recurrence and inconsistent repeated-run behavior.

### Machinery disposition register
For every major subsystem: PRESERVE / REPAIR / MERGE / CONTAIN / RETIRE / UNKNOWN with evidence.

### What should be preserved
Only proven components and their proof boundaries.

### What must be redesigned
Exact responsibilities, contracts, schemas, state transitions.

### Production target design
Authoritative state, official command, scheduler, acceptance transaction, evidence model, invalidation, certification, failure semantics, recovery, concurrency, observability, security, compatibility, scale.

### Implementation plan
Ordered, dependency-aware, repository-specific plan with exact files and safeguards (R1-R20 above).

### Verification plan
All tests from the verification suite above.

### Tradeoffs and rejected alternatives
For each major design decision: the alternatives considered, costs of the chosen approach, costs of the rejected approaches, and the specific evidence or constraint that decided it. Include at minimum: single authority choice (FF6 controller vs Plan Control vs new), continuation model (committed vs local-signal), certification model (derived vs labeled), evidence model (hash-bound vs timestamp-bound), scheduler design (unified vs per-mission).

### Final verdict
Exactly one of: `PRODUCTION_DESIGN_SOUND`, `PRODUCTION_HARDENING_REQUIRED`, `STRUCTURAL_REDESIGN_REQUIRED`, `INSUFFICIENT_EVIDENCE_FOR_RELIABLE_ASSESSMENT`.

---

## Evidence classification standard

For every material conclusion state:
- Status: `PROVEN`, `INFERRED`, `DISPROVEN`, or `UNKNOWN`
- Files inspected
- Command executed
- Observed output
- First failing boundary
- Affected scope
- Why existing controls missed it
- Confidence
- Evidence that could change the conclusion

---

## Investigation artifacts

| # | Artifact | Phase |
|---|----------|-------|
| 00 | `00-baseline.md` | R1 |
| 01 | `01-product-definition.md` | 1 |
| 02 | `02-authority-matrix.md` | 1 |
| 03 | `03-document-classification.md` | 1 |
| 04 | `04-machinery-inventory.csv` | 2 |
| 05 | `05-invocation-graph.md` | 2 |
| 06 | `06-continuation-paths.md` | 3 |
| 07 | `07-continuation-decision-table.md` | 3 |
| 08 | `08-first-divergence-point.md` | 3 |
| 09 | `09-execution-results.md` | 3 |
| 10 | `10-proof-chain-ipynb.md` | 4 |
| 11 | `11-proof-chain-ora.md` | 4 |
| 12 | `12-proof-chain-gaps.md` | 4 |
| 13 | `13-product-behavior-proof.md` | 5 |
| 14 | `14-productive-cycle-scorecard.md` | 5 |
| 15 | `15-root-cause-register.md` | 6 |
| 16 | `16-preservation-register.md` | 6 |
| 17 | `17-machinery-disposition.md` | 6 |
| 18 | `18-target-architecture.md` | design |
| 19 | `19-migration-plan.md` | design |
| 20 | `20-plan-readiness-review.md` | final |
| — | `evidence-index.json` | final |

All artifacts go to `reports/production-assessment-2026-08-30/`. Every artifact must state: baseline commit, evidence inspected, facts proven, inferences, unknowns, confidence, reproduction commands, evidence paths, whether finding affects products/machinery/both.

---

## Final constraint

Do not solve the problem by adding another supervisor, ledger, projection, validator family, prompt layer, state file, or task generator.

First establish:
- One mission authority
- One next-task authority
- One acceptance transition
- One evidence freshness model
- One derived certification model
- One clean-start command

The repair is successful only when repeated real execution continuously improves format libraries and the system can prove what improved, why it is accepted, what became stale, and what should happen next.


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-08-31T03:56:25.310597+00:00"
  locked_by: "585f135481a6"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->

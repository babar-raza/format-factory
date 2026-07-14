# Production Portfolio Master Execution Plan

## Authority

**Plan ID:** FF-PORTFOLIO-41-PROD-001  
**Plan type:** production portfolio integration and execution  
**Execution model:** one agent, one working tree, one active taskcard at a time  
**Source portfolio:** 41 Markdown plans from `plans-archive.zip`  
**Primary repository expected by the source plans:** `C:\Users\prora\OneDrive\Documents\GitHub\format-factory`  
**Authority rule:** this master plan is the only execution authority. The 41 source plans remain requirement and taskcard sources, but their individual claims of sole authority do not replace this plan.

This plan exists because the 41 source plans cannot be executed safely as 41 independent plans. They overlap heavily, mutate the same production-control files, use stale repository snapshots, claim competing active-plan authority, reuse taskcard IDs, and sometimes reserve the same validator number for different features. The correct production approach is to retain every source taskcard, normalize all of them into one state model, merge genuine duplicates, serialize shared-file mutations, and prove the final integrated system through focused tests, negative controls, full-suite runs, fresh-state pilots, and idempotency reruns.

---

## 1. Mission

Execute every actionable taskcard from all 41 source plans in an order that reflects live repository state, production risk, dependencies, file ownership, and system integration.

The sole execution agent must:

1. Read and inventory all 41 source plans before changing code.
2. Inspect the actual machine and repository state instead of trusting dates, line numbers, commit hashes, status labels, validator counts, or file assumptions embedded in the plans.
3. Build one canonical task registry that maps every source taskcard to an executed, verified, merged, already-satisfied, superseded-with-replacement, or blocked outcome.
4. Keep this master plan active for the entire portfolio. Source-plan lock and closeout taskcards are represented as source-module state changes under this plan and must not replace the active master lock.
5. Perform all mutations serially. No second writing agent, no parallel branch, and no concurrent modification of shared files is permitted.
6. Preserve production behavior unless a taskcard explicitly requires a behavior change and the required tests prove it.
7. Close the portfolio only when all source taskcards are accounted for, all blocking tests pass, all required pilots pass, and two consecutive no-change verification runs produce no material drift.

---

## 2. Source Portfolio Integrity

The extracted portfolio must be copied into the repository as immutable source material, for example:

```text
plans/source-portfolios/ff-portfolio-41-prod-001/
```

The files must keep their original names and content. Store their SHA-256 hashes in:

```text
reports/portfolio-execution/ff-portfolio-41-prod-001/source-plan-manifest.json
```

The supplied workspace already includes a manifest for all 41 files. At repository execution time, regenerate the hashes after copying and compare them with the supplied manifest. Any mismatch is a hard stop until explained.

Required source counts:

```yaml
source_plan_count: 41
source_plan_files_missing: 0
source_plan_hash_mismatches: 0
source_plan_parse_failures: 0
```

The source taskcard register supplied with this plan contains 2,326 distinct taskcard-like identifiers and references. It is a discovery index, not a final task count. The execution agent must determine which entries are definitions, children, micro-steps, references, ranges, or historical task IDs and produce a normalized register without losing any actionable item.

---

## 3. Non-Negotiable Production Rules

### 3.1 One-agent rule

- Exactly one agent owns the repository and performs mutations.
- The agent may use scripts for analysis, but must not delegate write operations to another agent.
- Source plans that describe parallel-safe waves must still execute serially because the portfolio has extensive cross-plan file overlap.
- Only one canonical taskcard may be `IN_PROGRESS` at any time.

### 3.2 Live state outranks embedded state

Before executing any source taskcard, the agent must re-read the relevant files and verify:

- repository path;
- current branch and HEAD;
- worktree status, including staged, unstaged, and untracked files;
- active plan lock and continuation state;
- available Python interpreter and environment;
- actual test baseline;
- actual validator registry, IDs, and count;
- actual schema version;
- actual file names, classes, functions, and line locations;
- whether the requested behavior is already implemented;
- whether a later implementation changed the required approach.

Stale source-plan line numbers are navigation hints only. No mutation may be based only on an old line number.

### 3.3 Preserve existing user work

The agent must not use:

```text
git reset --hard
git clean -fd
git checkout -- .
force push
bulk deletion without a task-specific evidence record
```

If the worktree is not clean, create a full baseline inventory and patch before portfolio work:

```text
reports/portfolio-execution/ff-portfolio-41-prod-001/baseline/git-status.txt
reports/portfolio-execution/ff-portfolio-41-prod-001/baseline/git-diff.patch
reports/portfolio-execution/ff-portfolio-41-prod-001/baseline/git-diff-cached.patch
reports/portfolio-execution/ff-portfolio-41-prod-001/baseline/untracked-files.txt
```

Existing changes must be classified as user work, prior portfolio work, generated state, or unrelated work. Never silently absorb unrelated modifications into a portfolio commit.

### 3.4 No hardcoded validator count or validator number allocation

Many plans assume counts such as 167, 168, 173, 181, or other snapshots. Several plans also propose the same validator ID for different purposes. The agent must first build a live validator authority register:

```text
registry/governance/validator-id-authority.yaml
```

The register must include:

```yaml
validators:
  - validator_id: VNNN
    canonical_name: stable_machine_name
    module: repo/relative/path.py
    callable: function_name
    status: active|deprecated|reserved
    introduced_by_canonical_task: MCP-...
    source_taskcards: []
```

Rules:

- Existing validator IDs keep their current meaning.
- New validators receive the next available ID only after scanning every registered and implemented validator.
- A source taskcard's proposed ID is treated as an alias request, not a guaranteed number.
- Tests must derive the expected count from the authoritative registry or the runner's actual registration list.
- No plan may directly update a static count without updating the single source of truth and proving registration parity.

### 3.5 Source plans cannot replace master authority

Source taskcards that say to copy a plan, write an active plan lock, set themselves `IN_PROGRESS`, or terminal-close their own plan must be executed through the portfolio state layer:

```text
reports/portfolio-execution/ff-portfolio-41-prod-001/source-plan-state/<source-slug>.yaml
```

Example:

```yaml
source_plan: velvet-swinging-wreath.md
source_state: IN_PROGRESS
master_plan: plans/.claude/production-portfolio-master-plan.md
active_master_lock_unchanged: true
started_at: ...
closed_at: null
```

The master plan lock remains active until the entire portfolio closes.

### 3.6 No competing plans generated during execution

Several audit plans ask for a hardened execution plan or a new plan. Those outputs must be written as advisory reports and merged into this master backlog. They must not become a new active authority.

### 3.7 All source taskcards require a disposition

No source taskcard may disappear. Each normalized source taskcard must end in one of these dispositions:

```text
EXECUTED
ALREADY_SATISFIED_AND_VERIFIED
MERGED_INTO_CANONICAL_TASK
REBASED_AND_EXECUTED
SUPERSEDED_BY_VERIFIED_REPLACEMENT
NOT_APPLICABLE_WITH_PROOF
BLOCKED_WITH_OWNER_AND_EXIT_CONDITION
```

`SKIPPED`, `IGNORED`, and silent omission are forbidden final dispositions.

---

## 4. Master State Model

### 4.1 Canonical task states

```text
DISCOVERED
RECONCILING
READY
IN_PROGRESS
IMPLEMENTED
FOCUSED_VERIFIED
INTEGRATION_VERIFIED
PILOT_VERIFIED
CLOSED
BLOCKED
REROUTED
```

Allowed path:

```text
DISCOVERED -> RECONCILING -> READY -> IN_PROGRESS -> IMPLEMENTED
-> FOCUSED_VERIFIED -> INTEGRATION_VERIFIED -> PILOT_VERIFIED -> CLOSED
```

A task may move to `REROUTED` only when its behavior is fully represented by another canonical task and the mapping is recorded. A task may move to `BLOCKED` only with a named dependency, owner, evidence path, and objective exit condition.

### 4.2 Source task identity

Every source taskcard must be globally namespaced:

```text
<source-file-stem>::<source-taskcard-id>
```

Examples:

```text
precious-wandering-lighthouse::TC-001
splendid-squishing-orbit::TC-001
fizzy-imagining-hinton::TC-W0-001
modular-noodling-galaxy::TC-W0-001
```

Canonical portfolio task IDs use:

```text
MCP-W<global-wave>-<three-digit-number>
```

### 4.3 Required task mapping

Create and maintain:

```text
registry/portfolio/ff-portfolio-41-prod-001-task-map.json
```

Each source task record must include:

```yaml
source_plan: file.md
source_taskcard_id: TC-...
source_line_start: integer
source_line_end: integer|null
source_title: text
source_status_claim: text|null
live_disposition: one of the required dispositions
canonical_task_id: MCP-WN-NNN
live_state_before: summary
files_owned: []
dependencies: []
validation_commands: []
evidence_paths: []
commit: sha|null
final_state: CLOSED|BLOCKED
```

---

## 5. Mandatory Bootstrap Tasks

These tasks run before any source-plan mutation.

### MCP-W0-001: Locate and bind the repository

1. Resolve the repository root from the actual machine.
2. Confirm it is the intended Format Factory repository.
3. Record branch, HEAD, remotes, worktrees, interpreter candidates, operating system, and relevant environment variables.
4. Prefer the user's established Python interpreter when compatible:

```text
C:\Users\prora\anaconda3\envs\llm\python.exe
```

5. If the repository requires a local `.venv`, prove it with dependency and test results before selecting it. Record the chosen interpreter in the live-state baseline.
6. Use Windows one-line commands. Do not rely on multiline PowerShell blocks.

### MCP-W0-002: Capture immutable production baseline

Capture:

- `git status --short --branch`;
- staged and unstaged diffs;
- untracked files;
- current active plan lock;
- continuation signal;
- mission and sprint ledgers;
- schema version;
- validator registration list and count;
- skill registry count;
- current gap counts;
- current format and product inventories;
- current failing tests;
- current generated files that differ from their producers.

Write the results to:

```text
reports/portfolio-execution/ff-portfolio-41-prod-001/baseline/
```

### MCP-W0-003: Establish test baseline

Run the repository's documented fast tests, supervisor tests, governance tests, and full test suite. Record every failure as one of:

```text
PRE_EXISTING_REPRODUCIBLE
PRE_EXISTING_FLAKY
ENVIRONMENT_FAILURE
PORTFOLIO_BLOCKER
```

No source task may claim it caused or fixed a failure without comparison to this baseline.

### MCP-W0-004: Import and register the 41 source plans

1. Copy source plans without modification.
2. Verify all hashes.
3. Create the source plan registry.
4. Create per-source state records.
5. Parse all taskcards, child taskcards, micro-steps, ranges, and completion gates.
6. Produce a no-loss report.

### MCP-W0-005: Build conflict and dependency registers

Create:

```text
reports/portfolio-execution/ff-portfolio-41-prod-001/analysis/path-collision-register.yaml
reports/portfolio-execution/ff-portfolio-41-prod-001/analysis/taskcard-id-collision-register.yaml
reports/portfolio-execution/ff-portfolio-41-prod-001/analysis/validator-id-collision-register.yaml
reports/portfolio-execution/ff-portfolio-41-prod-001/analysis/schema-migration-register.yaml
reports/portfolio-execution/ff-portfolio-41-prod-001/analysis/generated-file-authority-register.yaml
reports/portfolio-execution/ff-portfolio-41-prod-001/analysis/dependency-dag.yaml
```

The supplied archive analysis found more than 200 shared path references, 44 cross-plan taskcard-ID overlaps, and many validator-number overlaps. Regenerate these reports against the repository and distinguish true mutation conflicts from references to existing components.

### MCP-W0-006: Create the portfolio branch and master lock

Use a dedicated branch derived from the current branch, unless the repository's production procedure explicitly requires another method. Do not switch branches when doing so would strand user changes. Write the master lock only after the baseline is safely captured.

---

## 6. Shared-File Serialization Rules

The following files are central production control points and must have explicit ownership. Before editing one, the active canonical task must acquire ownership in:

```text
registry/portfolio/ff-portfolio-41-prod-001-file-ownership.yaml
```

### 6.1 `tools/supervisor/governance_validator_runner.py`

Mutation order:

1. Establish dynamic validator registration and count authority.
2. Reconcile existing skipped validators and existing wiring.
3. Add lifecycle and control-plane validators.
4. Add skill and capability validators.
5. Add product governance validators.
6. Add Oracle, code-quality, certification, root-folder, and canary validators.
7. Run registration parity and duplicate-ID tests after every batch.

No plan may append a validator using a hardcoded expected count.

### 6.2 `tools/supervisor/check_continuation.py`

Mutation order:

1. Plan identity and lifecycle-state handling.
2. Behavioral iteration and mission-ledger enforcement.
3. Contradiction, rework, issue ownership, and blocking-validator pressure.
4. Sprint identity and continuation reason codes.
5. Product governance and blast-radius checks.
6. Lane selection and product-deepening signals.
7. Certification, playbook, and canary feedback.

After each batch, run focused continuation tests and a dry-run against copied state fixtures. Never test destructive continuation behavior against the only live state files.

### 6.3 `tools/supervisor/autonomous_cycle.py`

Mutation order:

1. Signal coherence and write-time validation.
2. Skip ledger and closeout error visibility.
3. Operational control record and transaction behavior.
4. Verified gap closure and file-system reconciliation.
5. Product-governance impact and rework classification.
6. Dual-lane and DOM work generation.
7. Playbook drift feedback and output regeneration.

### 6.4 `tools/supervisor/sprint_executor_validate.py`

- Discover actual phase count and phase names.
- Allocate new phases symbolically and append only once.
- Keep a phase registry so source plans that call their addition Phase 13 or Phase 14 do not overwrite an existing phase.
- Run phase-order and phase-idempotency tests.

### 6.5 `.supervisor/skill-registry.yaml`

Mutation order:

1. Validate schema and remove opt-out capability assumptions.
2. Establish skill-only execution and receipt contracts.
3. Add capability-layer and agent-surface fields.
4. Register Oracle, certification, layer, control-record, and specialist skills.
5. Regenerate all derived skill and capability artifacts.

### 6.6 `tools/supervisor/lifecycle_audit.py` and `write_plan_lock.py`

Mutation order:

1. External-plan identity and import safety.
2. Mission-specific ledger initialization.
3. Behavioral iteration guard.
4. Layer and certification closeout requirements.
5. Stable IDs and idempotent rerun behavior.

### 6.7 Product source and registries

Product code may not be changed until the relevant governance, Oracle, stub detection, gap ownership, and test-strength gates are active. This is especially important for FODS, FODT, DIF, CSV, ABW, QOI, NDJSON, and generated product packages.

---

## 7. Global Execution Sequence

Each source file remains authoritative for the detailed acceptance criteria of its own taskcards. This section controls when those taskcards may run and how overlapping work is reconciled.

### Wave 0: Authority, live state, and supervisor investigation

#### 0.1 `polymorphic-foraging-feather.md`

**Scope:** `TC-INV-000` through `TC-INV-011`.  
**Purpose:** reconstruct supervisor architecture, classify machinery LOC, inventory components, catalog problems, test system guarantees, compare architecture options, perform adversarial review, and produce a decision brief.  
**Execution rule:** read-only investigation first. Any requested hardened plan becomes an advisory report merged into this master plan. Do not create a competing active plan.  
**Gate:** the investigation must identify the actual control-flow and producer-consumer boundaries before shared supervisor files are modified.

#### 0.2 `stateful-booping-mountain.md`

**Scope:** `TC-PIS-001` through `TC-PIS-005`.  
**Purpose:** establish plan identity v2, safe plan import, lifecycle audit integration, migration pilots, and governance validation.  
**Special handling:** its proposed validator number must be allocated from the live validator registry. Do not assume V144 is free.  
**Gate:** all 41 source plans can be represented under the master plan without changing master authority.

### Wave 1: Lifecycle, sprint, state, and issue-control foundations

#### 1.1 `shimmering-rolling-meerkat.md`

**Scope:** `TC-SMR-001` through `TC-SMR-006`.  
**Purpose:** reconcile accumulated state, resolve known CLI and type-stub rework, establish a single source of truth for validator count, persist remaining fixes as governed tasks, and close the source module.  
**First required task:** execute the validator-count single-source-of-truth work before any plan adds validators.  
**Overlap:** the CLI/type-stub work overlaps `splendid-roaming-beaver.md`; execute once and map both source taskcards.

#### 1.2 `velvet-swinging-wreath.md`

**Scope:** `TC-VWR-001` through `TC-VWR-011`, Pilot A, Pilot H, and source closeout.  
**Purpose:** repair lifecycle behavior so machinery missions cannot terminal-close after one shallow iteration, initialize mission ledgers, generate follow-up taskcards from audit gaps, enforce stop conditions, add regression validators, and prove single- and multi-iteration behavior.  
**Dependency:** live validator authority and source-plan identity.  
**Gate:** repeated machinery execution must produce controlled iterations rather than premature terminal closure.

#### 1.3 `splendid-roaming-beaver.md`

**Scope:** rework taskcards, `TC-SRB-000` through `TC-SRB-090`, and Pilots 1 through 10.  
**Purpose:** productionize sprint identity, inventory prior sprints, repair stale locks, create an atomic sprint-number allocator, define contradiction reason codes, run recovery and concurrency pilots, perform two product-deepening sprints, and finish with a readiness audit.  
**Dependency:** lifecycle iteration repair.  
**Gate:** sprint IDs are monotonic, concurrency-safe, interruption-safe, and represented consistently in all state artifacts.

#### 1.4 `bubbly-dancing-pony.md`

**Scope:** `TC-MA2-PIPE-001`, `TC-MA2-SIGNAL-001`, `TC-MA2-SKIP-001`, `TC-MA2-VAL-001`, `TC-MA2-LOCK-001`, verification, four pilots, and final review.  
**Purpose:** make sprint prompts a view over canonical work items, enforce continuation-signal coherence, surface closeout skips, use dynamic validator-count enforcement, harden grouped lock writes, and prove idempotent output.  
**Dependency:** sprint identity and validator authority.  
**Gate:** `next-work-items.json`, sprint prompt, continuation signal, and source-module state agree.

#### 1.5 `silly-popping-tower.md`

**Scope:** `TC-OCRD-A1` through `A5`, `B1` through `B2`, and `C1` through `C9`.  
**Purpose:** build the operational control record, transaction-safe ingestion, schema migration framework, staleness detection, contradiction and gap-selection signals, control-layer discovery, query tools, validators, skills, pilots, and permanent-layer registration.  
**Execution split:** execute schema, transaction, staleness, contradiction, and gap-selection foundations in Wave 1. Defer skill registration, full pilots, and permanent-layer promotion until Waves 2 and 7.  
**Gate:** the control database and file authorities remain consistent, transactional, and rebuildable.

#### 1.6 `optimized-meandering-giraffe.md`

**Scope:** `TC-FIOP-000` through `TC-FIOP-011`.  
**Purpose:** establish found-issue ownership, create missing registers, resolve Python and .NET LOC findings, add Section 21 validators, run invalid-expectation, invalid-dismissal, and flaky-failure pilots, and produce issue-accounting evidence.  
**Gate:** no found issue may remain ownerless or be dismissed as pre-existing without evidence.

#### 1.7 `kind-crunching-coral.md`

**Scope:** `TC-BOOL-001` through `TC-BOOL-005`.  
**Purpose:** close implementation-verified gaps safely, wire closure into the autonomous cycle, correct skip statuses, add a governance validator, and run dry-run, apply, and closeout verification.  
**Dependency:** issue ownership and control-record foundations.  
**Gate:** implementation-verified gaps close only when proof is current and all consumers agree.

### Wave 2: Skill, agent, and capability governance

#### 2.1 `imperative-floating-book.md`

**Scope:** all `TC-SGOV-W0` through `TC-SGOV-W7` taskcards and 15 pilots.  
**Purpose:** enforce skill-only governed mutations, validate skill contracts and plan routes, install blocking hooks and CI, write receipts, harden grading and close-task behavior, register missing micro-skills, backfill historical work, and compute adoption metrics.  
**Dependency:** stable lifecycle, sprint, and issue-control foundations.  
**Gate:** a direct ungoverned source mutation is blocked and a correctly routed skill execution produces an accepted receipt.

#### 2.2 `wild-napping-cherny.md`

**Scope:** `TC-SFE3-000` through `TC-SFE3-008`.  
**Purpose:** run composite skill-first enforcement, resolve routing gaps, complete the capability-compiler work type, run eight pilots, update skill quality scores, refresh receipt indexes, and close the skill-first sprint.  
**Dependency:** skill-only enforcement from the prior module.  
**Gate:** all required work types resolve to an existing, composed, repaired, or newly registered skill without bypass.

#### 2.3 `glimmering-hopping-kazoo.md`

**Scope:** `TC-ACP-001` through `TC-ACP-016`.  
**Purpose:** replace opt-out parity assumptions, define the canonical agent contract, produce a machine-readable agent bundle, enforce pre-mutation guards, complete Claude, Codex, and Kilo adapters, define model routing, run cross-agent pilots, and add drift prevention.  
**Dependency:** canonical skill registry and receipts.  
**One-agent interpretation:** only the sole portfolio agent performs production writes. Cross-agent pilots must use isolated fixtures or read-only simulations unless the master agent applies the resulting patch itself.  
**Gate:** parity means demonstrated delivery, enforcement, and pilot capability, not a default boolean.

#### 2.4 `humble-hatching-lark.md`

**Scope:** `TC-CL-001` through `TC-CL-007`.  
**Purpose:** repair capability state derivation, regenerate action queues, integrate SAL authority classes, document two-track authority, detect gap closure, make fallback work sources auditable, and prove idempotency.  
**Dependency:** skill and agent contract stabilization.  
**Gate:** capability work is derived from authoritative inputs and every fallback is explicit.

#### 2.5 `imperative-coalescing-bengio.md`

**Scope:** all `TC-P1` through `TC-P6` taskcards.  
**Purpose:** integrate Espanso prompts with governed capability sources, validate the prompt registry, detect staleness, extract canonical policy rules, update provenance, create canonical prompt files, and add schema enforcement.  
**Dependency:** stable skill, capability, and policy authorities.  
**Gate:** Espanso is a generated or validated consumer of canonical prompts, not an independent policy source.

### Wave 3: Truth, specification, architecture, and quality audits

#### 3.1 `fuzzy-conjuring-lobster.md`

**Scope:** `TC-ARCH-001` through `TC-ARCH-018`.  
**Purpose:** perform generation archaeology, source inventory and hygiene, QName and SAL audits, reconstruction of generation history, evidence tracing, gap analysis, and recommendations.  
**Execution rule:** investigation and evidence first. Any requested plan output is advisory and merged into the master registry.  
**Gate:** the agent understands which artifacts are generated, authoritative, stale, orphaned, or manually maintained before pipeline repairs.

#### 3.2 `cheeky-crafting-manatee.md`

**Scope:** `TC-FF-AUDIT-001` through `TC-FF-AUDIT-092`.  
**Purpose:** create complete format, specification, fact, QName, feature, code, and proof registers; measure the spec-to-code chain; identify anomalies and root causes; repair SAL and capability compilation; run FODS, CSV, and QOI pilots; backfill the portfolio; and issue a final idempotency verdict.  
**Dependency:** generation archaeology.  
**Gate:** every claimed feature can be traced to an authority, implementation, and proof, or is explicitly classified as a gap.

#### 3.3 `effervescent-sprouting-marshmallow.md`

**Scope:** `TC-FHQA-000` through `TC-FHQA-013`.  
**Purpose:** run the complete specification-to-evidence and QName audit, inspect sources, SAL, capabilities, skills, supervisor and lane behavior, produce product maturity matrices, execute minimum safe repairs, and prove idempotency.  
**Authority adaptation:** source bootstrap and lock tasks update the source-module state only.  
**Gate:** no QName healing claim is accepted without full-chain evidence.

#### 3.4 `golden-foraging-boot.md`

**Scope:** `TC-GFB-001` through `TC-GFB-041`.  
**Purpose:** assess machinery readiness, map system layers, audit QName, products, skills, SAL, RCAL, lanes, supervisor and continuation behavior, define target architecture, implement lane and Gate 11 contracts, design backfill, run isolation tests and product pilots, and produce a single-go handoff.  
**Execution split:** perform audits and design in Wave 3. Defer production pilots and product-deepening waves until Wave 6.  
**Gate:** target architecture and lane contracts must be reconciled with the more focused dual-lane plans before implementation.

#### 3.5 `mutable-exploring-hellman.md`

**Scope:** `TC-CQGA2-001` through `TC-CQGA2-032`.  
**Purpose:** audit code quality, build a governed gap ledger, repair structural weaknesses, run pilots, score quality, and issue a final report.  
**Execution split:** run audit and gap registration in Wave 3. Run repair pilots after the enforcement gates in Wave 4.  
**Gate:** every code-quality repair is tied to a registered issue and a test that detects the original defect.

#### 3.6 `elegant-napping-minsky.md`

**Scope:** `TC-B01` through `TC-B05`, `TC-C01`, and `TC-C02`.  
**Purpose:** build an architecture audit tool, public API manifest, focused validators, lane registry and promotion tooling, live architecture counters, audit all products, and create an architecture gap register.  
**Dependency:** truthful spec, capability, and code inventories.  
**Gate:** architecture counters are derived from current source and manifests, not static declarations.

#### 3.7 `playful-discovering-thunder.md`

**Scope:** `TC-RR-001` through `TC-RR-012`.  
**Purpose:** repair root-folder governance, restore and strengthen V91 behavior, add source-test parity and README floors, prevent new unmanaged root directories, repair priority READMEs, test governance, and close idempotently.  
**Gate:** repository-root structure is controlled by explicit producers and validated content contracts.

### Wave 4: Governance enforcement, stub gates, and coverage gates

#### 4.1 `memoized-frolicking-donut.md`

**Scope:** `TC-GOV-001` through `TC-GOV-023`.  
**Purpose:** repair enforcement first by wiring existing validators, persistent blocking violations, rework classification, blast-radius checks, and git-diff cross-checks; then add schemas, registries, managers, records, six new validators, ten pilots, counters, and final evidence.  
**Dependency:** validator authority, continuation stability, and issue ownership.  
**Gate:** governance policy changes actual execution behavior before records are backfilled.

#### 4.2 `iterative-mixing-shannon.md`

**Scope:** `TC-PGH-001` through `TC-PGH-019`.  
**Purpose:** implement the full product-governance lifecycle, including authority binding, control inventory, governed artifact lifecycle, proposals, impact and decision records, promotions, release candidates, traceability, pipeline and code-writing governance, reopening, maintenance classification, backfill, ten pilots, completion counters, and final report.  
**Dependency:** enforcement-first module.  
**Overlap rule:** schemas, validators, managers, and records that overlap the prior module must be extended or verified, never duplicated under a second authority.  
**Gate:** all 22 product-governance completion counters derive from current state and reach their required values.

#### 4.3 `lively-leaping-elephant.md`

**Scope:** `TC-GOV-LLE-001` through `TC-GOV-LLE-010`.  
**Purpose:** define production best practices, inventory governance gaps, document root causes, add real-file validators, implement baseline burn-down and before/after quality evidence, feed violation pressure into continuation, create governed product-healing taskcards, update governance documentation, and close with evidence.  
**Dependency:** product-governance enforcement.  
**Gate:** baselines cannot become permanent exemptions and measurable violation pressure reaches work selection.

#### 4.4 `twinkly-nibbling-platypus.md`

**Scope:** `TC-TNP-001` through `TC-TNP-010`.  
**Purpose:** prove and repair the V149 structural defect, create a baseline-aware stub register, remove unsafe allowlisting, fix method-boundary extraction in V105/V106, reconcile validator authority, clean orphaned artifacts, run the full suite, and close.  
**Dependency:** validator registry and code-quality gap ownership.  
**Gate:** new semantic stubs block, known baselines burn down, and method extraction is behaviorally tested.

#### 4.5 `atomic-chasing-meteor.md`

**Scope:** `TC-G4H-001` through `TC-G4H-007`.  
**Purpose:** deepen Gate 4 from declaration checks to executable proof, verify corpus and test-file consistency, derive blocked formats dynamically, add execution probes, add pre-commit enforcement, synchronize completion matrices, and produce a fresh evidence bundle.  
**Dependency:** truthful format, Oracle, and test authorities.  
**Gate:** Gate 4 PASS means a parser or evidence wrapper actually executes against a valid corpus sample.

### Wave 5: Oracle, drivers, code-writing, and dual-lane machinery

#### 5.1 `shiny-percolating-sky.md`

**Scope:** `TC-OIS-001` through `TC-OIS-011`.  
**Purpose:** establish production-grade Oracle behavior, upgrade priority packages, remove synthetic depth inflation, add executor configuration, implement invalid-case execution, remove fallback masking, add source hashes, make V143 distribution-aware, execute all Oracles, and prove traceability and idempotency.  
**Gate:** Oracle results reflect executable cases and current source, not declared package shape.

#### 5.2 `modular-noodling-galaxy.md`

**Scope:** all Oracle Phase II taskcards from `TC-W0-001` through `TC-W7-002`.  
**Purpose:** register Oracle skills, produce coverage and stale-detection tooling, bind tests to Oracle cases, enforce future-format onboarding and product advancement, deepen D2 cases, run installed-package consumers, expand invalid cases, migrate bindings, run twelve pilots, and close with zero portfolio failures.  
**Dependency:** core Oracle repairs.  
**Special handling:** proposed validator IDs, including V144, V145, and V146, must be remapped from the live authority register when occupied.

#### 5.3 `spicy-sparking-gosling.md`

**Scope:** `TC-INT-001` through `TC-INT-008`.  
**Purpose:** identify the driver integration break, add scaffold generation and writing, block weak assertions, update the Python API skill, feed promotion tasks into continuation, run end-to-end pilots, register weak-test gaps, and close with reports.  
**Dependency:** skill governance, stub detection, Oracle, and product governance.  
**Gate:** generated scaffold code is written through the governed path and tests prove behavior rather than `assert True` placeholders.

#### 5.4 `splendid-prancing-wind.md`

**Scope:** `TC-SPW-001` through `TC-SPW-007`.  
**Purpose:** heal product-library code writing and architecture, enforce source quality, architecture boundaries, implementation proof, product generation, validation, and final pilots.  
**Dependency:** drivers, Oracle, stub gates, and architecture gap register.  
**Gate:** generated product code satisfies architecture and behavior contracts before promotion.

#### 5.5 `serialized-petting-crab.md`

**Scope:** `TC-VPR-001` through `TC-VPR-008`.  
**Purpose:** audit the dual-lane pipeline, build a durable DOM-maturity gap generator, wire it into the autonomous cycle, harden classification, activate policy consumption, verify the pipeline, run regressions, and close.  
**Dependency:** stable gap ledger, autonomous cycle, and code-writing machinery.  
**Gate:** DOM gaps survive regeneration and enter the canonical work queue with explicit lane identity.

#### 5.6 `peppy-crafting-lark.md`

**Scope:** `TC-PCL-001` through `TC-PCL-012`.  
**Purpose:** complete the dual-lane feedback loop, wire lane selection into sprint generation, make maturity promotion depend on behavioral proof, fix evidence lane attribution, strengthen D2 contracts, add FODS and FODT mutation roundtrips, prove starvation behavior, inventory remaining products, and close with idempotency.  
**Dependency:** the structural DOM-gap generator from the prior module.  
**Overlap rule:** reuse and extend the prior generator instead of creating a second implementation with a different name or schema.

### Wave 6: Product healing and portfolio deepening

#### 6.1 `splendid-squishing-orbit.md`

**Scope:** `TC-FGSQ-001` through `TC-FGSQ-025`.  
**Purpose:** resolve the FODS production incident by building method and gap ledgers, strengthening V87 through V91 behavior, adding provenance and roundtrip requirements, removing semantic stubs, grounding task generation, reconciling file-system gaps, repairing .NET and Python FODS architecture and tests, scanning the portfolio, reopening invalid Gate 11 claims, running ten pilots, and proving idempotency.  
**Dependency:** product governance, stub gates, Oracle, code-writing machinery, and dual-lane behavior.  
**Gate:** no FODS method may claim functionality through dictionary-only, hardcoded, or comment-marker behavior when persistent XML behavior is required.

#### 6.2 `fizzy-imagining-hinton.md`

**Scope:** all `TC-W0` through `TC-W7` taskcards.  
**Purpose:** reconcile portfolio claims, repair overclaim detection and weak tests, register commands and lane ownership, separate analytics, heal monoliths, add writers, verify gap ledgers, consolidate machinery, and add security, performance, and coverage tests.  
**Dependency:** product and machinery foundations.  
**Gate:** each portfolio repair is tied to actual source truth, and generated writers pass roundtrip or format-specific behavior tests.

#### 6.3 `vast-splashing-allen.md`

**Scope:** all named healing, phantom, baseline, queue, SAL, product, dogfood, source-control, and closeout taskcards.  
**Purpose:** repair forensic leftovers, resolve phantom references, establish a full-suite baseline, drain stale queues, execute ABW, CSV, and DIF SAL healing, advance a governed product item and dogfood export path, commit bounded changes, and close with evidence.  
**Dependency:** SAL, gap ownership, product governance, and product test infrastructure.  
**Gate:** no phantom taskcard or stale queue entry remains, and each SAL or dogfood repair has an executable proof.

#### 6.4 Deferred implementation and pilot portions from earlier modules

Complete the mutation and pilot portions previously deferred from:

- `golden-foraging-boot.md`;
- `mutable-exploring-hellman.md`;
- `elegant-napping-minsky.md`;
- `effervescent-sprouting-marshmallow.md`.

Re-run their audits against the post-healing code before closing their source modules.

### Wave 7: Layer, certification, grader, canary, and playbook controls

#### 7.1 `glittery-splashing-manatee.md`

**Scope:** `TC-LHEAL-001` through `TC-LHEAL-010` and the referenced certification-layer task.  
**Purpose:** enforce permanent-layer requirements at terminal closeout, implement promotion across all layer registries, complete certification layer registration, add the required plan field, update layer-creation guidance, document supervisor visibility gaps, run future-layer and negative pilots, and prove idempotency.  
**Dependency:** stable lifecycle, skill registry, and control records.  
**Gate:** plans that require permanent layers cannot terminal-close until all governed layer registries agree.

#### 7.2 `precious-wandering-lighthouse.md`

**Scope:** source-namespaced `TC-001` through `TC-010`.  
**Purpose:** create certification-run identity, add missing-evidence semantics, build known-bad fixtures, reconcile gaps, register certification skills and maturity criteria, add lifecycle validators, wire certification into continuation, regenerate pilots, and close.  
**Dependency:** permanent-layer promotion and validator authority.  
**Overlap rule:** use the layer-promotion mechanism from the prior module and do not create competing L28 records.

#### 7.3 `warm-enchanting-grove.md`

**Scope:** `TC-LGT-001` through `TC-LGT-007`.  
**Purpose:** isolate grader logs, add retry coverage to gateway paths, implement a circuit breaker, cache terminal failures safely, add reliability tests, and run pilot proof.  
**Dependency:** stable grading contracts and test fixtures.  
**Gate:** transient grader failures retry safely, permanent failures do not loop, circuit state is tested, and tests cannot modify production logs.

#### 7.4 `clever-tickling-island.md`

**Scope:** discovery, initialization, schema, registry, promotion CLI, grader shadow, compilation diff, test, and closeout taskcards.  
**Purpose:** add a shadow canary system for validators, graders, and compilation outputs, including schema migration, promotion controls, comparisons, tests, and closeout.  
**Dependency:** operational schema migration framework and hardened grader.  
**Gate:** shadow behavior cannot affect production verdicts until explicit promotion criteria and comparison evidence pass.

#### 7.5 `glowing-swinging-grove.md`

**Scope:** `TC-PBHP-001` through `TC-PBHP-005`.  
**Purpose:** inject playbook context into sprint planning, detect post-grading drift, feed drift into work synthesis, add CI enforcement, and strengthen V92 behavior.  
**Dependency:** sprint output assurance and hardened grader.  
**Gate:** playbook rules form a closed forward and return loop rather than static documentation.

#### 7.6 Complete deferred `silly-popping-tower.md` tasks

Complete control-layer skill registration, full pilot suite, and permanent-layer promotion after the skill, layer, certification, and canary systems are stable.

### Wave 8: Full machinery assurance and portfolio closure

#### 8.1 `vast-wibbling-moon.md`

**Scope:** `TC-VWM-001` through `TC-VWM-032`, including all stage reviews, output inventory, quality scoring, claim reconciliation, canonical gap ledger, plan hardening, machinery healing, output regeneration, pilots, independent review, and idempotent closure.  
**Purpose:** perform the final end-to-end assurance pass over every machinery stage and output class after the focused plans have executed.  
**Authority adaptation:** its plan-hardening outputs are reports under the master plan. It must not replace master authority or create a second execution DAG.  
**Gate:** all stage reviews pass, all claim-to-evidence mismatches are resolved, required outputs are regenerated, ten or more pilots pass, and the final rerun is materially unchanged.

#### 8.2 Final source-module reconciliation

For every one of the 41 plans:

1. Re-read the full source file.
2. Compare every taskcard and completion criterion with the canonical task map.
3. Confirm no actionable child or micro-step was lost.
4. Run the source plan's final validation commands, rebased to live paths and IDs.
5. Write a source closeout report.
6. Mark the source module `CLOSED` only after all source taskcards have a final disposition.

---

## 8. Canonical Merge Rules for Overlapping Plans

### 8.1 Same behavior, same target

Implement once as one canonical task. Map all source taskcards to it. Each source receives its own evidence reference and final disposition `MERGED_INTO_CANONICAL_TASK`.

### 8.2 Same target, compatible behavior

Apply changes in the global wave order. Re-read the file before each task, rebase semantic anchors, and run tests after each bounded change. Do not paste full replacement blocks from stale plans over later changes.

### 8.3 Same target, contradictory behavior

Create a decision record containing:

- source claims;
- live code facts;
- production risk;
- compatibility analysis;
- selected behavior;
- negative control;
- rollback method;
- source taskcard dispositions.

The selection hierarchy is:

1. current production behavior proven by tests;
2. explicit user requirement;
3. current canonical schema or registry authority;
4. later, deeper, evidence-backed design;
5. least destructive implementation that satisfies all non-conflicting requirements.

### 8.4 Generated files

Never hand-edit a generated file when a producer exists. Modify the producer, regenerate, and prove no unrelated drift. The generated-file authority register must identify producers for lane registries, reports, prompts, manifests, and completion matrices.

### 8.5 Historical and stale taskcards

If a task is already implemented:

1. locate the implementation;
2. prove it with the source task's acceptance criteria and negative controls;
3. check whether the implementation has drifted or is incomplete;
4. close as `ALREADY_SATISFIED_AND_VERIFIED` only when all behavior is present;
5. otherwise create a rebased canonical task for the missing portion.

### 8.6 Source taskcards that request commits

The master commit policy controls. A source task's commit requirement is satisfied by a portfolio commit that contains the canonical work and lists all mapped source taskcards in the commit body or evidence record.

---

## 9. Validation Strategy

### 9.1 Per-task validation

Every canonical mutation task requires:

1. pre-change focused test result;
2. implementation diff;
3. focused positive tests;
4. at least one negative control for a new guard or validator;
5. generated-file drift check when applicable;
6. integration test for the immediate producer and consumer;
7. evidence record with exact command, exit code, and output hash.

### 9.2 Shared-file batch validation

After each bounded batch on a hot file, run:

- module tests;
- supervisor integration tests;
- validator registration parity;
- schema validation;
- fixture-based continuation or autonomous-cycle dry-run;
- import and syntax checks;
- idempotent second invocation.

### 9.3 Wave exit gates

Each wave must pass:

```yaml
focused_test_failures: 0
new_unexplained_full_suite_failures: 0
unowned_changed_files: 0
unresolved_schema_conflicts: 0
unresolved_validator_id_conflicts: 0
unmapped_source_taskcards_in_wave: 0
generated_file_drift_without_producer_change: 0
blocking_negative_controls_failed: 0
```

### 9.4 Portfolio pilots

The final integrated pilot suite must include at least:

1. plan import and resume after interruption;
2. monotonic sprint allocation under simulated concurrency;
3. lifecycle audit requiring multiple machinery iterations;
4. continuation signal incoherence rejection;
5. closeout failure producing a visible skip record;
6. direct ungoverned source edit blocked by skill governance;
7. cross-agent contract simulation with only the master agent applying changes;
8. SAL-to-capability-to-gap-to-work trace for one ODF, one text, and one binary format;
9. Oracle valid and invalid cases with source-hash freshness;
10. weak test and semantic stub detection;
11. dual-lane starvation and DOM work selection;
12. FODS and FODT mutation roundtrip persistence;
13. product change proposal through promotion and release-candidate decision;
14. rejected product change with no source mutation;
15. certification run with missing-evidence negative control;
16. layer-required plan blocked from premature closeout;
17. grader transient failure, permanent failure, and circuit-open behavior;
18. shadow canary comparison without production impact;
19. playbook drift returned to next work selection;
20. three consecutive autonomous cycles with consistent state;
21. fresh-state or fresh-worktree execution of the critical control path;
22. two final no-change reruns with zero material output drift.

### 9.5 Full-suite policy

A full suite must run at:

- initial baseline;
- end of every global wave;
- before each product-promotion or certification decision;
- before final portfolio closeout;
- after the first no-change rerun.

If the suite is too large, the agent may run documented shards, but the final result must cover the complete suite and combine exit status and evidence deterministically.

---

## 10. Commit and Rollback Policy

### 10.1 Commit boundaries

Use one atomic commit per canonical task or tightly coupled task cluster. Each commit must contain:

- canonical task ID;
- mapped source taskcards;
- behavior changed;
- tests run;
- generated files updated;
- rollback note.

Do not mix unrelated wave work.

### 10.2 Rollback

Rollback uses `git revert` of the bounded portfolio commit, followed by regeneration and tests where needed. Do not use destructive reset on the production working tree.

For schema migrations, every migration requires:

- forward migration test;
- repeated-apply test;
- old-state fixture;
- documented downgrade or restore strategy;
- backup of the live database before migration.

### 10.3 Stop conditions

Stop mutation and mark the current canonical task `BLOCKED` when:

- the repository identity is uncertain;
- source-plan hashes differ without explanation;
- user changes would be overwritten;
- a destructive migration has no backup or rollback;
- a required production credential or external service is unavailable;
- a conflict cannot be resolved from code, tests, authority files, or explicit requirements;
- baseline failures make causality impossible and cannot be isolated;
- the active master lock has been replaced unexpectedly.

The agent must continue with unrelated ready tasks only when doing so cannot compound the blocker.

---

## 11. Required Evidence Structure

```text
reports/portfolio-execution/ff-portfolio-41-prod-001/
  baseline/
  analysis/
  source-plan-state/
  canonical-tasks/
    MCP-W0-001/
    MCP-W1-001/
    ...
  waves/
    wave-0-closeout.yaml
    ...
  pilots/
  source-closeout/
  final/
```

Each canonical task evidence directory must contain:

```text
task.yaml
before-state.json
after-state.json
commands.jsonl
test-results.json
diff-summary.txt
source-taskcard-map.json
rollback.md
verdict.yaml
```

`commands.jsonl` must record the exact command, working directory, interpreter, start and end time, exit code, stdout path, and stderr path.

---

## 12. Source Plan Completion Matrix

The final report must contain one row for every source file:

| Source plan | Total normalized taskcards | Executed | Verified existing | Merged | Superseded with replacement | Not applicable with proof | Blocked | Closed |
|---|---:|---:|---:|---:|---:|---:|---:|---|

All 41 rows must be present. Final acceptable conditions:

```yaml
source_plans_total: 41
source_plans_closed: 41
source_plans_blocked: 0
source_taskcards_unreconciled: 0
source_taskcards_without_evidence: 0
source_taskcards_silently_skipped: 0
```

---

## 13. Final Completion Gates

The portfolio may close only when all of the following are true:

```yaml
authority:
  active_master_plans: 1
  competing_active_source_plans: 0
  source_plan_hash_mismatches: 0

task_accounting:
  source_plans_registered: 41
  source_taskcards_unreconciled: 0
  actionable_items_lost: 0
  final_blocked_taskcards: 0

repository:
  unowned_changed_files: 0
  unexplained_untracked_files: 0
  generated_files_with_unknown_producer: 0
  unresolved_merge_markers: 0

validators:
  duplicate_active_validator_ids: 0
  runner_registry_mismatches: 0
  static_expected_count_dependencies: 0
  negative_controls_failed: 0

state_and_lifecycle:
  incoherent_state_artifacts: 0
  stale_active_locks: 0
  orphan_sprint_ids: 0
  invisible_closeout_failures: 0
  premature_machinery_terminal_closures: 0

skills_and_agents:
  governed_operations_without_skill_route: 0
  accepted_mutations_without_receipt: 0
  unverified_agent_parity_claims: 0

spec_and_products:
  unsupported_feature_claims: 0
  unresolved_traceability_breaks_for_pilot_formats: 0
  newly_introduced_semantic_stubs: 0
  weak_assertion_blockers: 0
  required_roundtrip_failures: 0

quality:
  new_unexplained_test_failures: 0
  required_pilots_failed: 0
  final_no_change_reruns_passed: 2
  material_drift_on_second_rerun: 0
```

Final verdict string:

```text
FF_PORTFOLIO_41_PRODUCTION_EXECUTED_INTEGRATED_VERIFIED_AND_IDEMPOTENT
```

---

## 14. Sole Agent Operating Loop

The execution agent must repeat this loop until all canonical tasks are closed:

1. Read the master plan, current wave closeout, active canonical task, and live repository status.
2. Confirm the master lock is still active.
3. Select the highest-priority `READY` canonical task whose dependencies are closed.
4. Load every mapped source taskcard and its child and micro-step requirements.
5. Re-read all target files and relevant producers and consumers.
6. Record live-state corrections before editing.
7. Acquire file ownership.
8. Run the focused pre-change tests.
9. Implement the smallest production-safe change that satisfies all mapped requirements.
10. Regenerate derived artifacts from their producers.
11. Run positive tests, negative controls, integration tests, and idempotency checks.
12. Update evidence, task mapping, source-module state, and wave counters.
13. Commit the bounded change.
14. Release file ownership.
15. Re-run work selection from current state. Never continue from an old in-memory assumption.

The agent must not declare success based on file existence, text search alone, a static counter, a self-reported evidence declaration, or a passing test that cannot fail under a known-bad fixture.

---

## 15. Execution Handoff

```yaml
master_plan_id: FF-PORTFOLIO-41-PROD-001
execution_authority: this_file
execution_mode: ONE_AGENT_SERIAL_PRODUCTION
source_plan_count: 41
first_task: MCP-W0-001
first_mutation_allowed_after:
  - MCP-W0-002
  - MCP-W0-003
  - MCP-W0-004
  - MCP-W0-005
required_initial_outputs:
  - live-state-baseline.json
  - source-plan-manifest.json
  - source-taskcard-register.json
  - validator-id-authority.yaml
  - file-ownership-register.yaml
  - dependency-dag.yaml
hard_rules:
  - do_not_replace_master_lock_with_source_plan_lock
  - do_not_hardcode_validator_count
  - do_not_reuse_validator_id_without_live_allocation
  - do_not_parallelize_mutations
  - do_not_overwrite_user_changes
  - do_not_close_any_source_plan_with_unreconciled_taskcards
  - do_not_terminal_close_master_until_two_no_change_reruns_pass
final_verdict_required: FF_PORTFOLIO_41_PRODUCTION_EXECUTED_INTEGRATED_VERIFIED_AND_IDEMPOTENT
```

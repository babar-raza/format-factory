# Plan: Product Library Code-Writing and Architecture Healing
**Plan ID:** splendid-prancing-wind
**Mission ID:** PQLH-001
**Type:** machinery_hardening
**Authority Source:** User-confirmed active plan (plan mode, 2026-07-10)
**Revision:** v3 — full micro-taskcardization pass
**authoritative_plan:** C:\Users\prora\.claude\plans\splendid-prancing-wind.md
**execution_authority:** true

---

## PREFLIGHT RECORD

```yaml
# taskcardization-preflight (embedded)
repository: c:\Users\prora\OneDrive\Documents\GitHub\format-factory
branch: main
active_plan_path: C:\Users\prora\.claude\plans\splendid-prancing-wind.md
active_plan_title: "Product Library Code-Writing and Architecture Healing"
plan_format: markdown with YAML/Python code blocks
plan_size_lines: 617 (pre-enhancement)
major_section_count: 11
existing_taskcard_sections: 7 (TC-SPW-001 through TC-SPW-007)
existing_taskcard_format: flat narrative, no parent-child, no machine state
existing_state_vocabulary: OPEN only
existing_validation_model: implicit acceptance bullets only
existing_evidence_model: none
existing_dependency_model: linear prose only
existing_quality_scoring: none
existing_execution_handoff: none
existing_requirement_ids: none
duplicate_plan_risk: LOW — only one plan file in scope

defects_found:
  - No parent/child taskcard hierarchy
  - No micro-steps
  - No machine state transitions
  - No rollback strategies
  - No evidence obligations per taskcard
  - No requirement IDs or traceability
  - No validation commands
  - TC-SPW-003 contains two distinct sub-tasks (split required)
  - TC-SPW-006 relies on unverified SAL fact (investigation step missing)
  - TC-SPW-007 lists V78_AGG twice (error)
  - All dependencies expressed as prose only
```

```yaml
# active-plan-authority-verdict (embedded)
verdict: SINGLE_AUTHORITATIVE_PLAN_CONFIRMED
authoritative_path: C:\Users\prora\.claude\plans\splendid-prancing-wind.md
competing_plans_found: false
notes: >
  External plan created by plan-mode at ~/.claude/plans/splendid-prancing-wind.md.
  All work targets this file only. No plan-v2, final-plan, or replacement-plan created.
```

---

## PART I: PRESERVED ANALYSIS

> This section is READ-ONLY context. Do not task-cardize it. Do not delete or compress it.
> Execution agents must read it before executing any taskcard.

### Honest Assessment: What Is Actually Broken

This plan's first version treated symptoms. This version addresses structural mechanisms.

The system produced a 3,283-LOC .NET monolith (`FodsDocumentAccessor.cs`), then removed it by splitting into **10 partial class files totaling 5,677 LOC**, froze every file's cap at its post-split size, and declared the problem resolved. The aggregate design is worse than the original. This happened because:

- V78 measures **per-file LOC**, so 10 × 500 LOC passes; 1 × 5,677 LOC fails. The system found the minimal change that satisfies the metric without satisfying the intent.
- `baseline_loc_cap` is set to the **current violation value** at discovery, then frozen. This prevents re-growth but never requires reduction. Files sit at violation values indefinitely as "grandfathered."
- Sprint acceptance is driven by **test count + evidence paths**, not design quality. PCG-001 through PCG-006 are all OPEN; the last sprint was still ACCEPTED_VERIFIED with 1,169 tests.
- V88 (dictionary-backed state) is **WARN-only** — `_columnWidths`, `_activeFilters`, `_cellComments` exist in `FodsDocumentReadOps.cs` today, flagged but never blocking.
- The Supreme Directive ("never stop") structurally prevents quality debt repayment. GOV_BLOCK fires for four specific monolith validators. Round-trip not implemented, detached state, undocumented APIs — none block continuation.
- The pre-execution checklist is **self-assessed by the generator**. The agent confirming `parser_connection: confirmed` is the same agent that will write (and game) the code. Evidence for a work item is produced by the agent being evaluated.

### True Root Causes

**RC-01: Wrong unit of measurement for structural enforcement**

V78 enforces LOC per **file**. The actual design concern is LOC per **class aggregate**. Partial classes make this trivially gameable: split a monolith into N partial files, each under 800 lines. The system has done this exactly. `FodsDocument` as a class aggregate is 5,677 LOC across 10 files. Every file passes V78.

**The fix is not tweaking the threshold. The fix is measuring at the correct unit.**

**RC-02: The baseline absorbs violations permanently**

`baseline_loc_cap` is set to the current LOC at first violation detection and never decreased. The "grandfathered" category exists specifically to prevent enforcement on historical debt. There is no mechanism that says "this file must decrease before new work is accepted." Combined with RC-01, this means a decomposed monolith has: all files under individual caps, all caps frozen, all future work unobstructed.

**The grandfathering policy has no sunset mechanism and no trajectory requirement.**

**RC-03: Sprint acceptance is disconnected from product state**

The grading system verifies *sprint completion* (did the worker do what they declared?) not *product state* (is the product actually in a good state?). 1,169 passing tests → ACCEPTED regardless of whether:
- Any round-trip serialization exists (FodsWriter.cs: 57 LOC today)
- Dictionary-backed state survives save/load
- Public APIs have documentation
- Partial class aggregate LOC is acceptable

**There is no system-level product state gate. Sprint-level evidence is the only quality signal.**

**RC-04: The self-assessment loop cannot detect what it generates**

The pre-execution checklist (`parser_connection: confirmed`, `roundtrip_test: planned`) is filled in by the same LLM that writes the subsequent code. When the skill says "forbidden: creating a private dictionary field to back a persistent document property," the agent generating the task declaration writes "confirmed: no dictionary fields." Then, during implementation, it writes a dictionary field. There's no independent verification between declaration and execution.

V87 and V88 provide post-hoc detection (after the code is written, after the sprint closes), but they are heuristic and not comprehensive. V87 catches simple `return 0;` patterns. V88 catches `private readonly Dictionary<>` fields but is WARN-only and uses heuristics that can miss wired-but-incomplete paths.

**Evidence quality is bounded by the quality of the agent producing it. The grading system grades evidence, not code.**

**RC-05: "Never stop" structurally prevents quality debt repayment**

GOV_BLOCK exists for exactly four named monolith validators. Everything else — detached state, missing round-trip, undocumented public APIs, grandfathered LOC violations — continues unimpeded. The system is architecturally designed to make forward progress past these issues.

This is not a bug. It's an explicit design choice (the Supreme Directive). The problem is that quality debt accumulates in each sprint and there is no pathway for it to be repaid without human intervention. The gap ledger has 10+ OPEN BLOCKING gaps for FODS .NET. None block continuation. New work proceeds on top of unresolved debt.

**RC-06: The oracle is the only honest independent signal — and it's underused**

The oracle layer runs spec-fact-defined test cases. The implementing agent cannot influence these tests because they are written against spec facts, not against what the agent produced. 73/73 PASS across all 20 Python formats. This is the most reliable quality signal in the system.

The oracle does not cover .NET. The oracle covers format loading, not round-trip serialization. The most honest quality signals are the least used.

### What to Preserve

| Component | Reason |
|-----------|--------|
| Oracle verification layer (73/73 PASS) | Only genuinely independent quality signal; spec-fact-driven, cannot be gamed |
| V87 (constant-return detection) | Actually parses .cs content; catches most egregious stubs |
| V89 (suspicious filenames) | Simple but effective for the worst patterns |
| Skills registry structure | The registry pattern is sound; the contracts need strengthening |
| Evidence declaration schema | Good foundation; grading emphasis is what's wrong |
| SAL facts (14,441) | Real spec authority; underused, not broken |
| QName registry | Correct foundation |
| Gap ledger structure | Good tracking; enforcement is what's missing |
| GOV_BLOCK mechanism | Correct escalation path; scope needs expanding |
| Production Library Standard v2 | Correct principles; enforcement is incomplete |

### What Must Change

| Component | Current State | Required State |
|-----------|--------------|----------------|
| V78 LOC measurement | Per-file | Per-class-aggregate (sum partial class files) |
| `baseline_loc_cap` policy | Frozen forever at violation value | Trajectory required: aggregate must decrease or hold on each touch |
| Sprint scorecard | Test count + evidence paths | Add: round-trip coverage, parser-source coverage, documented API coverage |
| V88 severity | WARN | FAIL for new additions (existing grandfathered under current aggregate cap) |
| GOV_BLOCK scope | 4 monolith validators | Extend: aggregate LOC violation, blocking gap unresolved, no round-trip for Gate-1 format |
| Pre-execution verification | Self-assessed checklist | Design artifact required BEFORE code, independently validated by a second agent pass |
| Gap ledger enforcement | Advisory documentation | BLOCKING-severity gaps block new feature work for that format |
| Oracle coverage | Python FOSS formats only | Extend to .NET load path for FODS as proof of concept |

### Solution Design Principle

Adding more validators to the wrong unit is waste. Adding requirements to a self-assessment loop that can be gamed is waste. The solution starts by fixing what gets measured and how evidence is verified, then demonstrates the fix on one example, then extends.

### Explicit Tradeoffs

**Tradeoff 1: Velocity vs. quality.** V153 (design artifact gate) adds 1-2 steps to every .NET product sprint. Check 2d (blocking gap gate) halts FODS .NET work until BLOCKING gaps are re-classified. These changes reduce sprint throughput. This is the correct tradeoff.

**Tradeoff 2: Self-assessment vs. independent review.** V153 requires a design artifact, but the same agent writes it. This does not solve the generator-evaluator identity problem — it makes commitments explicit and auditable. A genuine independent reviewer (second agent, separate invocation) provides stronger guarantees. The optional two-agent pattern is documented but not mandated here because overhead may exceed benefit for routine additions. Reserve mandatory two-agent review for Gate-11-path work.

**Tradeoff 3: Existing debt is deliberately not addressed.** The 10-file FodsDocument aggregate, existing dictionary-backed fields in ReadOps.cs, minimal FodsWriter.cs — none are fixed in this plan. This plan fixes the MACHINERY so new work doesn't create new debt of the same kind. Paying down existing debt is a separate program of work.

**Tradeoff 4: GOV_BLOCK for blocking gaps will break current sprint flow.** If Check 2d is enabled and PCG-001 through PCG-006 are all BLOCKING severity, all FODS .NET sprints halt. The plan handles this by requiring severity re-classification before Check 2d is enabled. Re-classification uses documented criteria applied by the agent.

**Tradeoff 5: Partial class LOC aggregation has false positive risk.** `*.g.cs`, `*.designer.cs`, and EF migrations may be partial classes that shouldn't count. The exclusion list must be in config, not hardcoded.

### Risks and Likely Limits

**Risk R1: Oracle cannot verify .NET round-trip.** V152 uses text-pattern heuristics, not actual test execution. This is weaker than the Python oracle. Acknowledge explicitly in evidence declarations.

**Risk R2: Gap severity re-classification is a judgment call.** The autonomous system may classify everything as MEDIUM to avoid being blocked. Documented criteria with concrete examples mitigate but do not eliminate this risk.

**Risk R3: Design artifacts generated to pass the validator, not to guide design.** V153 must check: spec_fact exists in SAL, estimated_loc is plausible (> 10 LOC), target_file is new or has explicit justification.

**Likely Limit: Generator-evaluator identity problem is not solved.** This plan does not change who writes evidence. Validators catch specific patterns after the fact. The oracle (spec-fact-driven) is the only structural solution but is outside this plan's scope for .NET.

### What This Plan Deliberately Does Not Do

1. Does not rebuild FodsDocument from scratch.
2. Does not scan all 20+ formats.
3. Does not add XML documentation to existing public methods.
4. Does not mandate the two-agent review pattern for all sprints.
5. Does not extend the oracle to .NET (recommended follow-on plan).

---

## PART II: REQUIREMENTS INVENTORY

```yaml
# normalized-requirements-inventory (embedded)
# All REQ-* IDs are stable. Do not renumber on rerun.

REQ-MEAS-001:
  title: "Fix LOC measurement unit from per-file to per-class-aggregate"
  source_section: "What Must Change / V78 LOC measurement row"
  root_cause: RC-01
  addresses: "Partial class split bypasses V78 per-file cap"
  maps_to: TC-SPW-001

REQ-MEAS-002:
  title: "Add trajectory enforcement: known aggregate violations must not grow on touch"
  source_section: "What Must Change / baseline_loc_cap policy row"
  root_cause: RC-02
  addresses: "Grandfathered violations sit permanently without reduction"
  maps_to: TC-SPW-001

REQ-GATE-001:
  title: "Upgrade V88 to FAIL for new dictionary-backed state additions"
  source_section: "What Must Change / V88 severity row"
  root_cause: RC-04, RC-05
  addresses: "New detached state passes unimpeded; only warns on pre-existing"
  maps_to: TC-SPW-002

REQ-GATE-002:
  title: "Add V152: GOV_BLOCK when Gate-1 format has no round-trip test"
  source_section: "What Must Change / GOV_BLOCK scope row"
  root_cause: RC-03, RC-05
  addresses: "Round-trip absence never blocks continuation"
  maps_to: TC-SPW-003B

REQ-GATE-003:
  title: "Add Check 2d: GOV_BLOCK when BLOCKING-severity gap is OPEN for target format"
  source_section: "What Must Change / Gap ledger enforcement row"
  root_cause: RC-03, RC-05
  addresses: "Gap ledger is advisory; BLOCKING gaps never block continuation"
  maps_to: TC-SPW-003B
  prerequisite: REQ-GATE-004

REQ-GATE-004:
  title: "Classify PCG-* gap severities using documented criteria before enabling Check 2d"
  source_section: "TC-SPW-003 Severity classification section"
  root_cause: RC-05
  addresses: "Unclassified gaps would incorrectly trigger Check 2d"
  maps_to: TC-SPW-003A

REQ-ART-001:
  title: "Add V153: require design artifact before any .cs modifications in a sprint"
  source_section: "What Must Change / Pre-execution verification row"
  root_cause: RC-04
  addresses: "Pre-execution checklist is self-assessed with no audit trail"
  maps_to: TC-SPW-004

REQ-ART-002:
  title: "Create design-artifact schema with machine-verifiable constraints"
  source_section: "TC-SPW-004 Design artifact spec"
  root_cause: RC-04
  addresses: "No formal schema for design commitments"
  maps_to: TC-SPW-004

REQ-ART-003:
  title: "Update .NET skill blocks to require design_artifact_required field"
  source_section: "TC-SPW-004 / skill-registry.yaml updates"
  root_cause: RC-04
  addresses: "Skills do not mandate pre-code design commitment"
  maps_to: TC-SPW-004

REQ-AUDIT-001:
  title: "Create product_quality_audit.py to surface product state independently of sprint grades"
  source_section: "TC-SPW-005"
  root_cause: RC-03
  addresses: "Sprint acceptance verifies completion, not product state"
  maps_to: TC-SPW-005

REQ-AUDIT-002:
  title: "Integrate quality audit into autonomous_cycle.py as non-blocking Step 3b"
  source_section: "TC-SPW-005 Integration section"
  root_cause: RC-03
  addresses: "Quality state invisible in sprint output"
  maps_to: TC-SPW-005

REQ-PILOT-001:
  title: "Demonstrate healed machinery on one bounded FODS .NET addition (GetCellFormula)"
  source_section: "TC-SPW-006"
  root_cause: all RC
  addresses: "Machinery fixes are unproven without real execution"
  maps_to: TC-SPW-006

REQ-IDEM-001:
  title: "Prove all new validators produce identical results on second run with no source changes"
  source_section: "TC-SPW-007"
  root_cause: operational
  addresses: "Validators must not produce flapping results"
  maps_to: TC-SPW-007
```

---

## PART III: SOLUTION OPTIONS (per requirement group)

```yaml
# solution-option-scorecard (embedded, abbreviated to material decisions)
# Scores: 1-5 across root_cause_coverage / durability / testability / safety / complexity

REQ-MEAS-001_options:
  A_per_class_aggregate_v78_extension:
    description: "Extend V78 to sum LOC across partial class files by class name"
    root_cause_coverage: 5   # directly addresses RC-01
    durability: 4            # regex-based but robust for C# class declarations
    testability: 5           # deterministic, unit testable
    safety: 4                # exclusion list needed for *.g.cs
    complexity: 3            # moderate: need git state for trajectory
    selected: true
  B_separate_validator:
    description: "New V78_AGG completely independent of V78"
    root_cause_coverage: 5
    durability: 4
    testability: 5
    safety: 4
    complexity: 3
    selected: false
    rejection_reason: "Creates dual tracking; V78 and V78_AGG could diverge"

REQ-GATE-001_options:
  A_conditional_fail_new_additions_only:
    description: "V88 FAIL for new additions this sprint; WARN for pre-existing"
    root_cause_coverage: 4   # blocks new debt, not old
    durability: 5            # git-diff comparison is deterministic
    testability: 5
    safety: 5                # backward compatible; existing code still WARN
    complexity: 3
    selected: true
  B_full_fail_all:
    description: "V88 FAIL for all dictionary fields regardless of origin"
    root_cause_coverage: 5
    durability: 5
    testability: 5
    safety: 1                # immediately blocks all FODS .NET work
    complexity: 2
    selected: false
    rejection_reason: "Would halt all current sprints; existing code has no migration path"

REQ-ART-001_options:
  A_pre_code_design_artifact:
    description: "Require .local/design-artifacts/{taskcard-id}.yaml before .cs changes"
    root_cause_coverage: 3   # does not solve generator-evaluator but creates audit trail
    durability: 4
    testability: 5           # file presence + schema validation
    safety: 5                # additive only
    complexity: 3
    selected: true
  B_mandatory_two_agent_review:
    description: "Require second agent invocation to approve design before code"
    root_cause_coverage: 4
    durability: 3            # orchestration overhead, may break autonomous loop
    testability: 3
    safety: 3
    complexity: 5
    selected: false
    rejection_reason: "Architectural changes to autonomous loop outside this plan's scope"
```

---

## PART IV: EXECUTION CONTROL — PARENT TASKCARDS

> Machine-state legend:
> Parent: PROPOSED → READY → IN_PROGRESS → CHILDREN_IN_PROGRESS → INTEGRATION_PENDING → VERIFIED → SCORED → CLOSED
> Child:  TODO → READY → IN_PROGRESS → IMPLEMENTED → VERIFIED → SCORED → CLOSED
> Micro:  PENDING → READY → ACTIVE → COMPLETE (or FAILED / BLOCKED / SKIPPED_NOT_APPLICABLE)

---

### Parent Taskcard ID: TC-SPW-001
**Title:** Fix LOC Measurement — Per-Class Aggregate for Partial Classes
**Type:** PARENT
**Status:** PROPOSED
**Owner:** machinery_agent
**Supervisor:** governance_reviewer

**Source:**
- Plan requirement IDs: REQ-MEAS-001, REQ-MEAS-002
- Plan section: "What Must Change / V78 row; True Root Causes RC-01, RC-02"
- Root causes addressed: RC-01 (wrong measurement unit), RC-02 (baseline absorbs violations)

**Objective:**
Extend V78 LOC validator to compute and enforce LOC at per-class-aggregate granularity across partial class files. Add trajectory enforcement: any sprint touching a known-aggregate-violation class must not increase its aggregate.

**Outcome:**
`FodsDocument` aggregate (5,677 LOC across 10 files) is registered as `KNOWN_AGGREGATE_VIOLATION` with a frozen cap. New partial class additions that would grow the aggregate → FAIL V78_AGG. Second-run produces identical results.

**Scope:**
```
Allowed files:
  - tools/supervisor/governance_validators_dotnet.py
  - registry/source-structure-baseline.json
  - tests/supervisor/test_governance_validators_dotnet.py
  - tools/supervisor/governance_validator_runner.py
  - .supervisor/schemas/partial-class-exclusions.json  (NEW)
Allowed folders:
  - tools/supervisor/
  - registry/
  - tests/supervisor/
Forbidden files:
  - src/net/**  (no product source changes)
  - tools/supervisor/governance_validators_dotnet_semantic.py  (TC-SPW-002 owns this)
  - tools/supervisor/check_continuation.py  (TC-SPW-003 owns this)
Path expansion rule: Only files explicitly listed above may be created or modified.
```

**Preserved behavior:**
- Existing V78 per-file enforcement must still run and produce the same per-file results
- All existing known_violations entries in baseline.json must not change
- No existing test must be broken

**Dependencies:** None (first workstream)

**Child taskcards:**
- TC-SPW-001-01: Inspect V78 and validator runner
- TC-SPW-001-02: Define exclusion list and algorithm
- TC-SPW-001-03: Implement collect_partial_class_aggregates()
- TC-SPW-001-04: Implement validate_dotnet_aggregate_loc_cap() (V78_AGG)
- TC-SPW-001-05: Implement trajectory enforcement
- TC-SPW-001-06: Migrate baseline.json (add partial_class_aggregates section)
- TC-SPW-001-07: Write validator tests (≥5 cases)
- TC-SPW-001-08: Update governance_validator_runner.py expected_count
- TC-SPW-001-09: Integration verification

**Parent acceptance criteria:**
1. V78_AGG function exists in governance_validators_dotnet.py and returns a valid result dict
2. FodsDocument aggregate (5,677 LOC) appears as KNOWN_AGGREGATE_VIOLATION in baseline.json
3. Running V78_AGG against current src/net/fods/ produces no new FAILs (known violations only)
4. Adding a new partial class that grows aggregate above cap → V78_AGG FAIL in tests
5. `*.g.cs` and `*.designer.cs` files are excluded and do not appear in any aggregate
6. Trajectory check: simulated sprint-touch that increases aggregate LOC → trajectory FAIL
7. All new and existing tests pass: `pytest tests/supervisor/test_governance_validators_dotnet.py -v`
8. expected_count updated correctly in governance_validator_runner.py

**Integration checks:**
- Run full governance validator suite against current repo: `python tools/supervisor/governance_validator_runner.py` — must exit 0 with updated count
- Verify V78_AGG does not interfere with V78 per-file results

**Evidence required:**
- `.local/evidences/TC-SPW-001/v78-agg-test-run.txt` — pytest output showing ≥5 new test cases PASS
- `.local/evidences/TC-SPW-001/baseline-migration.txt` — diff of baseline.json showing new section
- `.local/evidences/TC-SPW-001/integration-run.txt` — full validator suite output

**Quality dimensions (score 1-5, all must be ≥4):**
- Requirement correctness: Does V78_AGG enforce REQ-MEAS-001 and REQ-MEAS-002?
- Implementation correctness: Does the regex correctly detect all partial class declarations?
- Scope discipline: Only allowed files modified?
- Validation strength: Are negative cases (growing aggregate) tested?
- Evidence completeness: Are all three evidence files present and non-empty?
- Regression safety: Do existing V78 tests still pass?
- Maintainability: Is exclusion list in config, not hardcoded?
- Production readiness: Does the validator handle missing/empty directories gracefully?

**Rollback strategy:**
- git revert changes to governance_validators_dotnet.py and governance_validator_runner.py
- Restore baseline.json from git HEAD

**Stop conditions:**
- If V78_AGG would cause false positives on *.g.cs files AND the exclusion logic cannot be confirmed correct → BLOCKED, investigate exclusion config first
- If governance_validator_runner.py cannot be updated without breaking existing test assertion → BLOCKED, investigate count discrepancy

**Reroute rule:** Any child quality score < 4/5 → mark child REROUTED, create repair micro-step, re-verify before closing parent.

---

#### Child Taskcard ID: TC-SPW-001-01
**Parent:** TC-SPW-001
**Title:** Inspect V78 Implementation and Validator Runner Integration
**Type:** CHILD / INVESTIGATION
**Status:** TODO

**Source:**
- Plan requirement IDs: REQ-MEAS-001
- Parent objective: Must understand current V78 signature before modifying

**Purpose:** Establish exact current state of V78 before any changes. Record function signatures, inputs, how it's called from the runner, and what data is available (git_head_start, declaration context, etc.).

**Scope:**
```
Allowed files:
  - tools/supervisor/governance_validators_dotnet.py  (READ ONLY)
  - tools/supervisor/governance_validator_runner.py  (READ ONLY)
Forbidden: No modifications in this child.
```

**Inputs:** None (inspection only)

**Expected output:** Findings document (written to plan notes or evidence file):
- Current V78 function name and signature
- Whether declaration/git_head_start is passed to V78
- Current expected_count value
- How V78 result is structured (keys, severity field, blocks_sprint field)

**Preconditions:** None

**Micro-steps:**
```
MS-001-01-01: Read governance_validators_dotnet.py — locate V78 function definition
  Action: Read file, find validate_dotnet_loc_cap or equivalent V78 function
  Target file: tools/supervisor/governance_validators_dotnet.py
  Expected output: Function name, signature, line number
  Completion check: Function signature recorded

MS-001-01-02: Record V78 current inputs
  Action: Note what parameters V78 currently receives (repo_root, declaration, changed_files, etc.)
  Expected output: List of current parameters and their types
  Completion check: Parameters list complete

MS-001-01-03: Check if git_head_start is available in runner context
  Action: Read governance_validator_runner.py — find where V78 is called
  Target file: tools/supervisor/governance_validator_runner.py
  Expected output: Call site, what arguments are passed
  Completion check: Call site identified, git_head_start availability confirmed or denied

MS-001-01-04: Record current expected_count value
  Action: Find expected_count variable or assertion in governance_validator_runner.py
  Expected output: Current integer value
  Completion check: Value recorded

MS-001-01-05: Record V78 result format
  Action: Inspect what make_result() or equivalent produces — keys: validator, result, items, summary, blocks_sprint
  Expected output: Dict structure for V78 result
  Completion check: Result format documented
```

**Acceptance checks:**
- V78 function name confirmed
- Parameters list complete
- git_head_start availability confirmed
- expected_count value recorded
- Result format documented

**Evidence required:**
- Finding notes embedded in evidence file: `.local/evidences/TC-SPW-001/inspection-notes.txt`

**Dependencies:** None

**Next valid task:** TC-SPW-001-02

**Closeout criteria:** All 5 micro-steps COMPLETE, findings documented.

**Rollback plan:** N/A (inspection only)

---

#### Child Taskcard ID: TC-SPW-001-02
**Parent:** TC-SPW-001
**Title:** Define Partial Class Exclusion Config and Detection Algorithm
**Type:** CHILD / DESIGN
**Status:** TODO

**Source:** REQ-MEAS-001, Tradeoff 5 (false positive risk)

**Purpose:** Produce the exclusion configuration and document the algorithm before any code is written. Prevents false positives on generated code.

**Scope:**
```
Allowed files:
  - .supervisor/schemas/partial-class-exclusions.json  (CREATE NEW)
  - tools/supervisor/governance_validators_dotnet.py  (DOCUMENT ONLY, no edits yet)
Forbidden: No implementation in this child.
```

**Inputs:** Findings from TC-SPW-001-01

**Expected output:**
- `.supervisor/schemas/partial-class-exclusions.json` containing exclusion patterns
- Algorithm pseudocode confirmed (may be taken from existing plan prose)

**Preconditions:** TC-SPW-001-01 CLOSED

**Micro-steps:**
```
MS-001-02-01: List all *.g.cs and *.designer.cs patterns that must be excluded
  Action: Check src/net/ for generated file patterns using Glob
  Expected output: Complete list of file suffix patterns to exclude
  Completion check: At least *.g.cs and *.designer.cs confirmed

MS-001-02-02: List directory patterns that must be excluded (test/, build/, obj/)
  Action: Check src/net/ directory structure for build artifacts
  Expected output: List of directory-level exclusion patterns
  Completion check: test/, build/, obj/ confirmed

MS-001-02-03: Create .supervisor/schemas/partial-class-exclusions.json
  Action: Write JSON file with suffix_exclusions and directory_exclusions arrays
  Target file: .supervisor/schemas/partial-class-exclusions.json
  Content:
    {
      "suffix_exclusions": ["*.g.cs", "*.designer.cs", "*.generated.cs"],
      "directory_exclusions": ["test", "tests", "build", "obj", "bin"],
      "class_name_exclusions": []
    }
  Completion check: File exists and is valid JSON

MS-001-02-04: Confirm regex pattern for partial class detection
  Action: Verify regex r'\bpartial\s+class\s+(\w+)' catches all cases in src/net/fods/
  Expected output: Regex validated against at least FodsDocument partial class files
  Completion check: Regex confirmed or corrected
```

**Acceptance checks:**
- Exclusion config file created and valid JSON
- Regex pattern confirmed against real .cs files
- No legitimate partial class excluded by mistake

**Evidence required:** `.local/evidences/TC-SPW-001/exclusion-config.txt`

**Dependencies:** TC-SPW-001-01 CLOSED

**Next valid task:** TC-SPW-001-03

---

#### Child Taskcard ID: TC-SPW-001-03
**Parent:** TC-SPW-001
**Title:** Implement collect_partial_class_aggregates() Helper
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Source:** REQ-MEAS-001

**Purpose:** Implement the core helper that groups .cs files by partial class name and computes LOC per group. This function is used by both V78_AGG and the trajectory check.

**Scope:**
```
Allowed files:
  - tools/supervisor/governance_validators_dotnet.py  (EDIT — add one function)
Forbidden: Do not modify validate_dotnet_loc_cap (V78) or any existing function.
Required path decision: Function must be added ABOVE validate_dotnet_loc_cap in the file
  to avoid forward reference issues.
```

**Inputs:** TC-SPW-001-01 signature findings, TC-SPW-001-02 exclusion config

**Expected output:** Working `collect_partial_class_aggregates(src_net_root: Path, exclusion_config: dict) -> dict[str, list[tuple[Path, int]]]` function in governance_validators_dotnet.py

**Preconditions:** TC-SPW-001-01 and TC-SPW-001-02 CLOSED

**Micro-steps:**
```
MS-001-03-01: Add import for json at top of file if not present
  Target: tools/supervisor/governance_validators_dotnet.py (top imports section)
  Action: Add 'import json' if missing
  Completion check: No duplicate import

MS-001-03-02: Implement collect_partial_class_aggregates() function stub with docstring
  Target: tools/supervisor/governance_validators_dotnet.py
  Action: Insert function with docstring, empty body, correct return type annotation
  Completion check: File parses without SyntaxError (python -c "import ast; ast.parse(open('...').read())")

MS-001-03-03: Implement .rglob scanning with directory exclusions
  Action: Add for loop over src_net_root.rglob("*.cs"), filter by directory_exclusions
  Completion check: Logic handles empty directory gracefully

MS-001-03-04: Implement suffix exclusions
  Action: Add check: if cs_file.suffix in suffix_exclusions or cs_file.name ends with excluded patterns, skip
  Completion check: *.g.cs files are skipped in manual trace

MS-001-03-05: Implement LOC counting and partial class regex
  Action: count lines, apply regex r'\bpartial\s+class\s+(\w+)' to content, build class_map
  Completion check: Function returns non-empty dict when run against src/net/fods/

MS-001-03-06: Manually trace function against src/net/fods/FodsDocument*.cs files
  Action: Run function in isolation, verify FodsDocument appears as key with ≥2 files
  Completion check: FodsDocument key found with expected file list
```

**Acceptance checks:**
- Function is syntactically valid Python
- Returns `dict[str, list[tuple[Path, int]]]` structure
- FodsDocument appears as key with 10 files when run against current src/net/fods/
- *.g.cs files not in any result

**Evidence required:** `.local/evidences/TC-SPW-001/aggregate-helper-trace.txt`

**Dependencies:** TC-SPW-001-01, TC-SPW-001-02 CLOSED

**Next valid task:** TC-SPW-001-04

---

#### Child Taskcard ID: TC-SPW-001-04
**Parent:** TC-SPW-001
**Title:** Implement validate_dotnet_aggregate_loc_cap() (V78_AGG)
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Source:** REQ-MEAS-001

**Purpose:** Add the V78_AGG validator function that uses collect_partial_class_aggregates() to enforce aggregate LOC caps per class.

**Scope:**
```
Allowed files:
  - tools/supervisor/governance_validators_dotnet.py  (EDIT — add one function)
Forbidden: Do not modify existing V78 function or any other existing function.
```

**Inputs:** Working collect_partial_class_aggregates() from TC-SPW-001-03, baseline.json structure

**Expected output:** `validate_dotnet_aggregate_loc_cap(repo_root, declaration, ...)` function that:
- Returns PASS for classes within their aggregate cap
- Returns FAIL for new additions that would push aggregate above cap
- Returns KNOWN_VIOLATION (WARN) for existing known violations that are stable
- Returns TRAJECTORY_FAIL for known violations that grew

**Preconditions:** TC-SPW-001-03 CLOSED

**Micro-steps:**
```
MS-001-04-01: Implement get_class_aggregate_cap() helper
  Action: Read from baseline.json["partial_class_aggregates"][class_name]["aggregate_cap"]
  Default: 2000 LOC for classes with >3 partial files; 800 LOC for single-file classes
  Completion check: Returns correct cap for FodsDocument (should be ~5677 known violation)

MS-001-04-02: Implement core V78_AGG function body
  Action: Call collect_partial_class_aggregates(), iterate classes, compare to cap
  Completion check: Returns result dict with validator="V78_AGG" key

MS-001-04-03: Implement KNOWN_VIOLATION handling (WARN not FAIL for existing)
  Action: Check baseline.json partial_class_aggregates for known entries; if present and
    aggregate <= cap, return PASS. If present and aggregate > cap, trajectory check.
  Completion check: FodsDocument aggregate returns KNOWN_VIOLATION (WARN) not FAIL

MS-001-04-04: Verify blocks_sprint logic
  Action: Ensure blocks_sprint=True only for NEW violations (not existing known violations)
  Completion check: Running against current repo → blocks_sprint=False for FodsDocument

MS-001-04-05: Verify function signature matches what runner expects
  Action: Cross-check parameters against how V78 is called from governance_validator_runner.py
  Completion check: Parameters compatible with existing call pattern
```

**Acceptance checks:**
- Running V78_AGG against current src/net/fods/ → WARN (KNOWN_VIOLATION), blocks_sprint=False
- Simulated new partial class growing FodsDocument beyond 5677 → FAIL, blocks_sprint=True
- Returns valid result dict matching existing validator format

**Evidence required:** `.local/evidences/TC-SPW-001/v78-agg-manual-run.txt`

**Dependencies:** TC-SPW-001-03 CLOSED

**Next valid task:** TC-SPW-001-05

---

#### Child Taskcard ID: TC-SPW-001-05
**Parent:** TC-SPW-001
**Title:** Implement Trajectory Enforcement (Aggregate Must Not Grow on Touch)
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Source:** REQ-MEAS-002

**Purpose:** Add logic to V78_AGG so that when a sprint TOUCHES any file in a known aggregate group, the current aggregate LOC must be ≤ the baseline aggregate cap. Growth → TRAJECTORY_FAIL.

**Scope:**
```
Allowed files:
  - tools/supervisor/governance_validators_dotnet.py  (EDIT — modify V78_AGG function only)
Forbidden: Do not touch collect_partial_class_aggregates() or other functions.
```

**Inputs:** V78_AGG function from TC-SPW-001-04, declaration.changed_files list

**Expected output:** V78_AGG extended with trajectory check:
- If declaration contains a changed file that belongs to a known aggregate group → check current aggregate vs baseline cap
- If aggregate GREW beyond cap → TRAJECTORY_FAIL, blocks_sprint=True

**Preconditions:** TC-SPW-001-04 CLOSED

**Micro-steps:**
```
MS-001-05-01: Verify declaration.changed_files is accessible in V78_AGG context
  Action: Check how changed_files is passed from governance_validator_runner.py context
  Completion check: changed_files is available or can be extracted from declaration dict

MS-001-05-02: Implement file-to-class-group lookup
  Action: Given changed_files list, determine which aggregate groups they belong to
  (a file belongs to a group if collect_partial_class_aggregates maps the file to that class)
  Completion check: FodsDocumentReadOps.cs maps to FodsDocument group

MS-001-05-03: Implement trajectory check logic
  Action: For each touched aggregate group, compare current_aggregate to
    baseline["partial_class_aggregates"][class_name]["aggregate_cap"]
  If current > cap → add TRAJECTORY_FAIL item to violations
  Completion check: Trajectory FAIL fires when simulated growth occurs

MS-001-05-04: Confirm TRAJECTORY_FAIL sets blocks_sprint=True
  Action: Verify trajectory failure is treated as blocking (not advisory)
  Completion check: blocks_sprint=True in trajectory failure result
```

**Acceptance checks:**
- Trajectory check fires when a file in a known aggregate group is touched AND aggregate grew
- Trajectory check does NOT fire when aggregate stays flat or decreases
- blocks_sprint=True for trajectory violations

**Evidence required:** `.local/evidences/TC-SPW-001/trajectory-test.txt`

**Dependencies:** TC-SPW-001-04 CLOSED

**Next valid task:** TC-SPW-001-06

---

#### Child Taskcard ID: TC-SPW-001-06
**Parent:** TC-SPW-001
**Title:** Migrate source-structure-baseline.json (Add partial_class_aggregates Section)
**Type:** CHILD / MIGRATION
**Status:** TODO

**Source:** REQ-MEAS-001, REQ-MEAS-002

**Purpose:** Run collect_partial_class_aggregates() against current src/net/ and write the discovered aggregate data into baseline.json as the initial known-violation caps.

**Scope:**
```
Allowed files:
  - registry/source-structure-baseline.json  (EDIT — add one new top-level key)
Forbidden: Do not modify existing "known_violations" entries.
Required path decision: Add new key "partial_class_aggregates" at same level as "known_violations"
```

**Inputs:** Working collect_partial_class_aggregates(), current src/net/ state

**Expected output:** `registry/source-structure-baseline.json` contains:
```json
{
  "known_violations": { ... (unchanged) },
  "partial_class_aggregates": {
    "FodsDocument": {
      "aggregate_cap": 5677,
      "files": ["src/net/fods/FodsDocument.cs", "src/net/fods/FodsDocumentReadOps.cs", ...],
      "category": "known_aggregate_violation",
      "trajectory": "decrease_required_on_touch",
      "baseline_set": "2026-07-10"
    }
  }
}
```

**Preconditions:** TC-SPW-001-03 and TC-SPW-001-05 CLOSED

**Micro-steps:**
```
MS-001-06-01: Run collect_partial_class_aggregates() against current src/net/
  Action: Execute the helper function (or equivalent script) against full src/net/ tree
  Expected output: Dictionary of all partial class groups found
  Completion check: FodsDocument found with 10 files and total ~5677 LOC

MS-001-06-02: Identify all groups with aggregate > 2000 LOC (known violations)
  Action: Filter results where sum(locs) > 2000
  Expected output: Short list of known violations (likely only FodsDocument)
  Completion check: List produced

MS-001-06-03: Write partial_class_aggregates section to baseline.json
  Action: Edit registry/source-structure-baseline.json to add the new key
  Content: For each known violation, record aggregate_cap (current total), files list,
    category: "known_aggregate_violation", trajectory: "decrease_required_on_touch"
  Completion check: File is valid JSON after edit

MS-001-06-04: Verify existing known_violations are unchanged
  Action: Diff the file against HEAD — confirm only the new key was added
  Completion check: No existing key modified
```

**Acceptance checks:**
- baseline.json is valid JSON
- partial_class_aggregates key exists with at least FodsDocument entry
- aggregate_cap set to current total LOC (not lower, not higher)
- Existing known_violations section unmodified

**Evidence required:** `.local/evidences/TC-SPW-001/baseline-migration.txt`

**Dependencies:** TC-SPW-001-05 CLOSED

**Next valid task:** TC-SPW-001-07

---

#### Child Taskcard ID: TC-SPW-001-07
**Parent:** TC-SPW-001
**Title:** Write Validator Tests for V78_AGG (≥5 test cases)
**Type:** CHILD / TESTING
**Status:** TODO

**Source:** REQ-MEAS-001, REQ-MEAS-002

**Purpose:** Provide machine-verifiable evidence that V78_AGG enforces exactly what it claims. Tests must cover both positive (pass) and negative (fail/warn) cases.

**Scope:**
```
Allowed files:
  - tests/supervisor/test_governance_validators_dotnet.py  (EDIT — add test cases)
Forbidden: Do not modify any non-test file in this child.
```

**Expected test cases (minimum 5):**
1. Single non-partial class file → PASS (no aggregate to track)
2. Two partial class files totaling 400 LOC each (800 total) below 2000 cap → PASS
3. FodsDocument-equivalent: 10 partial files totaling 5677 LOC, registered as known violation → KNOWN_VIOLATION (WARN), blocks_sprint=False
4. New partial file added to existing group → TRAJECTORY_FAIL, blocks_sprint=True
5. *.g.cs file excluded from aggregate calculation → PASS (generated code not counted)
6. (Optional) Aggregate decreases on touch → PASS (trajectory improvement allowed)

**Micro-steps:**
```
MS-001-07-01: Read existing test file to find test class and fixture pattern
  Action: Read tests/supervisor/test_governance_validators_dotnet.py first 80 lines
  Completion check: Test class name identified, fixture pattern understood

MS-001-07-02: Create temp directory fixture for test cases
  Action: Add pytest tmp_path fixture usage for creating synthetic .cs file sets
  Completion check: Fixture pattern confirmed compatible with existing test style

MS-001-07-03: Write test case 1 (single non-partial class → PASS)
MS-001-07-04: Write test case 2 (two partials, within cap → PASS)
MS-001-07-05: Write test case 3 (10 partials at 5677, known violation → KNOWN_VIOLATION WARN)
MS-001-07-06: Write test case 4 (new partial growing aggregate → TRAJECTORY_FAIL)
MS-001-07-07: Write test case 5 (*.g.cs excluded → PASS)
MS-001-07-08: Run pytest focused on new test methods
  Command: .venv/Scripts/pytest tests/supervisor/test_governance_validators_dotnet.py -k "aggregate" -v
  Completion check: All 5 cases PASS, 0 FAIL
```

**Acceptance checks:**
- All 5 test cases PASS
- No regression in existing test cases in the same file
- Test names are descriptive (not test_1, test_2)

**Evidence required:** `.local/evidences/TC-SPW-001/v78-agg-test-run.txt`

**Dependencies:** TC-SPW-001-04, TC-SPW-001-05 CLOSED (need V78_AGG to test against)

**Next valid task:** TC-SPW-001-08

---

#### Child Taskcard ID: TC-SPW-001-08
**Parent:** TC-SPW-001
**Title:** Update governance_validator_runner.py expected_count
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Source:** REQ-MEAS-001

**Purpose:** V78_AGG is a new validator. The runner's expected_count must be incremented by 1. Failing to do this will cause the validator count assertion to fail.

**Scope:**
```
Allowed files:
  - tools/supervisor/governance_validator_runner.py  (EDIT — update expected_count value)
  - tools/supervisor/governance_validator_runner.py  (EDIT — register V78_AGG call)
Forbidden: Do not modify any validator function or any test file.
```

**Micro-steps:**
```
MS-001-08-01: Find expected_count in governance_validator_runner.py
  Action: Grep for "expected_count" or "165" in the file
  Completion check: Line number found

MS-001-08-02: Find where V78 is called to add V78_AGG call adjacent to it
  Action: Locate V78 call in the main runner loop or validator list
  Completion check: Insertion point confirmed

MS-001-08-03: Register V78_AGG in the runner
  Action: Add call to validate_dotnet_aggregate_loc_cap() in appropriate place,
    import the function at top of runner file
  Completion check: V78_AGG appears in runner output when executed

MS-001-08-04: Increment expected_count from 165 to 166 (or current + 1)
  Action: Edit the expected_count line
  Completion check: Value is exactly current + 1

MS-001-08-05: Run runner to verify count assertion passes
  Command: python tools/supervisor/governance_validator_runner.py 2>&1 | tail -5
  Completion check: No count assertion error
```

**Acceptance checks:**
- V78_AGG appears in runner output
- expected_count updated correctly
- Runner exits without count assertion error

**Evidence required:** `.local/evidences/TC-SPW-001/runner-count-update.txt`

**Dependencies:** TC-SPW-001-07 CLOSED

**Next valid task:** TC-SPW-001-09

---

#### Child Taskcard ID: TC-SPW-001-09
**Parent:** TC-SPW-001
**Title:** Integration Verification for TC-SPW-001
**Type:** CHILD / VERIFICATION
**Status:** TODO

**Purpose:** Confirm all TC-SPW-001 work integrates correctly. The full governance validator suite must pass. V78_AGG must appear in output. All existing tests must pass.

**Micro-steps:**
```
MS-001-09-01: Run full governance validator suite
  Command: python tools/supervisor/governance_validator_runner.py
  Completion check: Exit 0, no count assertion error

MS-001-09-02: Run all supervisor tests
  Command: .venv/Scripts/pytest tests/supervisor/ -v --tb=short
  Completion check: All tests pass including new V78_AGG tests

MS-001-09-03: Confirm V78_AGG appears in runner output with correct validator name
  Action: Check output for "V78_AGG" result line
  Completion check: V78_AGG present

MS-001-09-04: Record integration pass as evidence
  Action: Write runner output to .local/evidences/TC-SPW-001/integration-run.txt
  Completion check: File written, non-empty
```

**Acceptance checks:**
- Full suite passes (exit 0)
- All supervisor tests pass
- V78_AGG present in output

**Evidence required:** `.local/evidences/TC-SPW-001/integration-run.txt`

**Dependencies:** TC-SPW-001-08 CLOSED

**Closeout criteria:** All micro-steps COMPLETE, evidence file non-empty, full suite exit 0.
**This closes TC-SPW-001 parent after integration check passes.**

---

### Parent Taskcard ID: TC-SPW-002
**Title:** Upgrade V88 — Dictionary State from WARN to FAIL-on-New-Addition
**Type:** PARENT
**Status:** PROPOSED
**Owner:** machinery_agent
**Supervisor:** governance_reviewer

**Source:**
- Plan requirement IDs: REQ-GATE-001
- Root cause: RC-04 (self-assessment), RC-05 (never-stop allows debt)

**Objective:** Modify V88 to distinguish new additions (FAIL, blocks_sprint) from pre-existing fields (WARN, non-blocking). Requires git state access to determine whether a Dictionary field was introduced in the current sprint.

**Scope:**
```
Allowed files:
  - tools/supervisor/governance_validators_dotnet_semantic.py  (EDIT — V88 function)
  - tests/supervisor/test_governance_validators_dotnet.py  (EDIT — add V88 tests)
Forbidden:
  - tools/supervisor/governance_validators_dotnet.py  (TC-SPW-001 owns this)
  - src/net/**  (no product source changes)
```

**Preserved behavior:** Pre-existing Dictionary fields still produce WARN, not FAIL. Sprint not blocked for existing code.

**Dependencies:** TC-SPW-001 VERIFIED (not strictly necessary for implementation, but sequenced to avoid merge conflicts in validator runner)

**Child taskcards:**
- TC-SPW-002-01: Inspect current V88 implementation
- TC-SPW-002-02: Verify git_head_start availability in V88 context
- TC-SPW-002-03: Implement field_existed_at_git_head() utility
- TC-SPW-002-04: Update V88 with new/existing distinction
- TC-SPW-002-05: Write tests (≥3 cases: new FAIL, existing WARN, wired field PASS)
- TC-SPW-002-06: Integration verification

**Parent acceptance criteria:**
1. New Dictionary field in a changed .cs file → V88 FAIL, blocks_sprint=True
2. Pre-existing Dictionary field in unchanged .cs file → V88 WARN, blocks_sprint=False
3. Dictionary field with XML write path confirmed (regardless of new/existing) → V88 PASS
4. ≥3 new tests pass for V88
5. V88 WARN behavior for existing FodsDocumentReadOps fields confirmed (no regression)

**Rollback strategy:** git revert governance_validators_dotnet_semantic.py changes

**Stop conditions:**
- If git_head_start is not accessible in V88 context and cannot be plumbed through → BLOCKED, escalate to investigation

---

#### Child Taskcard ID: TC-SPW-002-01
**Parent:** TC-SPW-002
**Title:** Inspect Current V88 Implementation
**Type:** CHILD / INVESTIGATION
**Status:** TODO

**Micro-steps:**
```
MS-002-01-01: Read governance_validators_dotnet_semantic.py, locate V88
  Action: Read file, find validate_dotnet_detached_dictionary_fields function
  Completion check: Function signature and body recorded

MS-002-01-02: Record what inputs V88 currently receives
  Action: Note parameters — does it receive changed_files? git_head_start?
  Completion check: Parameters recorded

MS-002-01-03: Record current severity and blocks_sprint behavior
  Action: Check current return values, severity field, blocks_sprint value
  Completion check: Confirmed WARN + blocks_sprint=False

MS-002-01-04: Check has_xml_write_reference() helper — does it exist?
  Action: Search file for any existing XML-write detection logic
  Completion check: Existing logic recorded (or noted as missing)
```

**Expected output:** Inspection notes in `.local/evidences/TC-SPW-002/inspection-notes.txt`
**Dependencies:** None
**Next valid task:** TC-SPW-002-02

---

#### Child Taskcard ID: TC-SPW-002-02
**Parent:** TC-SPW-002
**Title:** Verify git_head_start Availability and Plumb if Needed
**Type:** CHILD / INVESTIGATION + IMPLEMENTATION
**Status:** TODO

**Purpose:** V88 needs to know if a field existed before the current sprint. This requires access to git state (git_head_start commit SHA) to check if the field appears in the pre-sprint version of the file.

**Micro-steps:**
```
MS-002-02-01: Check how governance_validator_runner.py passes data to V88
  Action: Read validator runner to find V88 call site; check if git_head_start or
    declaration dict is passed
  Completion check: Call site found, current parameters listed

MS-002-02-02: If git_head_start is NOT passed → add it to the call site
  Action: Modify governance_validator_runner.py V88 call to include git_head_start
    from declaration["git_head_start"] if available
  Completion check: git_head_start accessible in V88 function body
  Note: If git_head_start cannot be obtained (e.g., headless run), fall back to WARN

MS-002-02-03: Implement field_existed_at_git_head() utility
  Target: tools/supervisor/governance_validators_dotnet_semantic.py
  Action: Add function that runs subprocess git show {sha}:{file_path} and checks
    if field_name appears in that version of the file
  Completion check: Function handles missing git_head_start gracefully (returns True = pre-existing)
```

**Evidence required:** `.local/evidences/TC-SPW-002/git-state-access.txt`
**Dependencies:** TC-SPW-002-01 CLOSED
**Next valid task:** TC-SPW-002-03 (may overlap if git state implementation is in same micro-step)

---

#### Child Taskcard ID: TC-SPW-002-03
**Parent:** TC-SPW-002
**Title:** Update validate_dotnet_detached_dictionary_fields() with New/Existing Logic
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Micro-steps:**
```
MS-002-03-01: Add changed_files filtering — only process files that changed this sprint
  Action: Modify V88 to skip files NOT in changed_files list
  Completion check: V88 only processes changed .cs files

MS-002-03-02: For each Dictionary field in changed file, call field_existed_at_git_head()
  Action: If existed → WARN (existing). If new → FAIL (new addition without write path)
  Completion check: Logic branching correct

MS-002-03-03: Update return value to correctly set severity and blocks_sprint
  Action: severity="FAIL" and blocks_sprint=True if new_violations non-empty
  Completion check: blocks_sprint=True only when new violations found

MS-002-03-04: Preserve WARN for pre-existing fields in same result dict
  Action: Both new_violations and existing_violations appear in result items list
    with different severity tags
  Completion check: Result contains both types when both present
```

**Evidence required:** `.local/evidences/TC-SPW-002/v88-update.txt`
**Dependencies:** TC-SPW-002-02 CLOSED

---

#### Child Taskcard ID: TC-SPW-002-04
**Parent:** TC-SPW-002
**Title:** Write V88 Tests (≥3 cases)
**Type:** CHILD / TESTING
**Status:** TODO

**Required test cases:**
1. New Dictionary field in changed file, no XML write path → V88 FAIL, blocks_sprint=True
2. Pre-existing Dictionary field (in git head), no XML write path → V88 WARN, blocks_sprint=False
3. Dictionary field WITH XML write path reference → V88 PASS (field wired)
4. (Optional) No changed .cs files in sprint → V88 PASS (no files to check)

**Micro-steps:**
```
MS-002-04-01: Write test case 1 (new dict field, no write path → FAIL)
MS-002-04-02: Write test case 2 (pre-existing dict field → WARN)
MS-002-04-03: Write test case 3 (wired dict field → PASS)
MS-002-04-04: Run pytest focused on V88 tests
  Command: .venv/Scripts/pytest tests/supervisor/test_governance_validators_dotnet.py -k "v88 or dictionary" -v
  Completion check: All new cases PASS, 0 FAIL
```

**Evidence required:** `.local/evidences/TC-SPW-002/v88-test-run.txt`
**Dependencies:** TC-SPW-002-03 CLOSED

---

#### Child Taskcard ID: TC-SPW-002-05
**Parent:** TC-SPW-002
**Title:** Integration Verification for TC-SPW-002
**Type:** CHILD / VERIFICATION
**Status:** TODO

**Micro-steps:**
```
MS-002-05-01: Run full governance validator suite
  Command: python tools/supervisor/governance_validator_runner.py
  Completion check: Exit 0

MS-002-05-02: Confirm V88 produces WARN (not FAIL) against current FodsDocumentReadOps.cs
  Action: Run V88 in isolation against FodsDocumentReadOps.cs with git_head_start = HEAD
  Completion check: V88 returns WARN (fields are pre-existing), blocks_sprint=False

MS-002-05-03: Record integration pass
  Action: Write output to .local/evidences/TC-SPW-002/integration-run.txt
```

**Evidence required:** `.local/evidences/TC-SPW-002/integration-run.txt`
**Dependencies:** TC-SPW-002-04 CLOSED
**This closes TC-SPW-002 parent after integration passes.**

---

### Parent Taskcard ID: TC-SPW-003A
**Title:** Classify PCG-* Gap Severities Before Enabling Blocking Gap Gate
**Type:** PARENT
**Status:** PROPOSED
**Owner:** machinery_agent
**Supervisor:** governance_reviewer

**Source:**
- Plan requirement IDs: REQ-GATE-004
- Root cause: RC-05

**Objective:** Apply documented severity criteria to every PCG-* gap entry in the gap ledger. Set `severity_confirmed: true` on each classified entry. Log the classification to a separate audit file. This is a pre-requisite gate for TC-SPW-003B (Check 2d) — Check 2d must NOT be enabled until this is done.

**Severity criteria (from plan, binding):**
- BLOCKING: Prevents correct runtime behavior for any user input
- HIGH: Prevents an important feature from being available to consumers
- MEDIUM: Quality concern with no user-facing defect at current usage levels
- LOW: Style issue, naming inconsistency, or future-maintainability concern

**Scope:**
```
Allowed files:
  - reports/product-quality/product-code-gap-ledger.yaml  (EDIT — add severity_confirmed fields)
  - reports/product-quality/gap-severity-classification-log.yaml  (CREATE NEW)
Forbidden: No code changes in this taskcard.
```

**Child taskcards:**
- TC-SPW-003A-01: Read all PCG-* entries and record their current fields
- TC-SPW-003A-02: Apply severity criteria to each entry and propose classification
- TC-SPW-003A-03: Write severity_confirmed to gap ledger
- TC-SPW-003A-04: Write audit log

**Parent acceptance criteria:**
1. Every PCG-* entry has `severity_confirmed: true` in gap ledger
2. Audit log file created with rationale for each classification decision
3. At least one BLOCKING entry confirmed (if none, the gate would never fire — investigate)
4. No entry classified as BLOCKING unless it prevents RUNTIME behavior (not just quality)

**Stop conditions:**
- If a PCG-* entry has ambiguous severity (could be BLOCKING or HIGH) → classify as HIGH (conservative; BLOCKING reserved for confirmed runtime failures)

---

#### Child Taskcard ID: TC-SPW-003A-01
**Parent:** TC-SPW-003A
**Title:** Read All PCG-* Entries and Record Fields
**Type:** CHILD / INVESTIGATION
**Status:** TODO

**Micro-steps:**
```
MS-003A-01-01: Read reports/product-quality/product-code-gap-ledger.yaml
  Action: Read entire file, count PCG-* entries
  Completion check: Total count of PCG-* entries recorded

MS-003A-01-02: For each PCG-* entry, record: gap_id, current severity, status, files affected
  Action: Extract key fields from each entry
  Completion check: All entries extracted, status field noted

MS-003A-01-03: Record to evidence file
  Action: Write .local/evidences/TC-SPW-003A/pcg-inventory.txt
  Completion check: File contains all PCG-* entries
```

---

#### Child Taskcard ID: TC-SPW-003A-02
**Parent:** TC-SPW-003A
**Title:** Apply Severity Criteria to Each PCG-* Entry
**Type:** CHILD / ANALYSIS
**Status:** TODO

**Preconditions:** TC-SPW-003A-01 CLOSED

**Micro-steps:**
```
MS-003A-02-01: For PCG-001 (original FodsDocumentAccessor monolith — now removed):
  Apply criterion: File was removed. Gap status should be CLOSED. Verify.
  If status=CLOSED → mark severity_confirmed=true, severity=HISTORICAL

MS-003A-02-02: For PCG-002 (FodsDocumentExtendedApis — now removed):
  Apply criterion: Same as PCG-001. Verify removal. Mark HISTORICAL if removed.

MS-003A-02-03: For PCG-003 (analytics masquerading as model — Python):
  Apply criterion: Does this prevent runtime correctness? → if analytics return wrong values: BLOCKING. If just wrong file placement: MEDIUM
  Decision: MEDIUM (wrong file placement, not runtime failure)

MS-003A-02-04: For each remaining PCG-* entry (up to all found in 003A-01):
  Apply the same criterion rubric. Record decision and rationale.
  Note: If PCG entry involves state lost on save+reload → BLOCKING
  If PCG entry involves missing features → HIGH
  If PCG entry involves code organization → MEDIUM
  If PCG entry involves naming → LOW

MS-003A-02-05: Write classification decisions to evidence file
  Action: .local/evidences/TC-SPW-003A/severity-classifications.txt
  Completion check: Every PCG-* has a classification with one-line rationale
```

---

#### Child Taskcard ID: TC-SPW-003A-03
**Parent:** TC-SPW-003A
**Title:** Update Gap Ledger with severity_confirmed Fields
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Preconditions:** TC-SPW-003A-02 CLOSED

**Micro-steps:**
```
MS-003A-03-01: For each PCG-* entry in product-code-gap-ledger.yaml:
  Add field: severity_confirmed: true
  Add field: severity: <classified value from 003A-02>
  Add field: severity_classification_date: 2026-07-10
  Completion check: All PCG-* entries have severity_confirmed: true

MS-003A-03-02: Verify YAML is valid after edits
  Command: python -c "import yaml; yaml.safe_load(open('reports/product-quality/product-code-gap-ledger.yaml'))"
  Completion check: No YAML parse error
```

---

#### Child Taskcard ID: TC-SPW-003A-04
**Parent:** TC-SPW-003A
**Title:** Write Severity Classification Audit Log
**Type:** CHILD / DOCUMENTATION
**Status:** TODO

**Preconditions:** TC-SPW-003A-03 CLOSED

**Micro-steps:**
```
MS-003A-04-01: Create reports/product-quality/gap-severity-classification-log.yaml
  Content:
    authoritative_plan: plans/.claude/splendid-prancing-wind.md
    artifact_role: analysis_or_evidence_only
    execution_authority: false
    classification_date: 2026-07-10
    classified_by: machinery_agent
    criteria_source: TC-SPW-003A severity table
    entries:
      - gap_id: PCG-001
        assigned_severity: HISTORICAL
        rationale: "File removed in commit 9bf2fe21"
      # ... all entries
  Completion check: File exists, all PCG-* entries appear

MS-003A-04-02: Record evidence path in parent taskcard evidence list
  Completion check: .local/evidences/TC-SPW-003A/ contains the log reference
```

**This closes TC-SPW-003A parent once all children are CLOSED.**

---

### Parent Taskcard ID: TC-SPW-003B
**Title:** Implement V152 (Round-Trip GOV_BLOCK) and Check 2d (Blocking Gap Gate)
**Type:** PARENT
**Status:** PROPOSED
**Owner:** machinery_agent
**Supervisor:** governance_reviewer

**Source:**
- Plan requirement IDs: REQ-GATE-002, REQ-GATE-003
- Root cause: RC-03, RC-05

**Dependencies:** TC-SPW-001 CLOSED (for knowing aggregate state), TC-SPW-003A CLOSED (severity_confirmed must be set before Check 2d enabled)

**Scope:**
```
Allowed files:
  - tools/supervisor/governance_validators_dotnet.py  (EDIT — add V152)
  - tools/supervisor/check_continuation.py  (EDIT — add Check 2d)
  - tools/supervisor/governance_validator_runner.py  (EDIT — register V152, update count)
  - tests/supervisor/test_governance_validators_dotnet.py  (EDIT — V152 tests)
  - tests/supervisor/test_check_continuation.py  (EDIT — Check 2d tests, CREATE if needed)
Forbidden:
  - reports/product-quality/product-code-gap-ledger.yaml  (TC-SPW-003A owns this)
  - src/net/**
```

**Child taskcards:**
- TC-SPW-003B-01: Inspect format-registry.yaml gate_1 field structure
- TC-SPW-003B-02: Implement validate_format_roundtrip_coverage() (V152)
- TC-SPW-003B-03: Write V152 tests (≥3 cases)
- TC-SPW-003B-04: Inspect check_continuation.py Check 2 insertion point
- TC-SPW-003B-05: Implement Check 2d in check_continuation.py
- TC-SPW-003B-06: Write Check 2d tests
- TC-SPW-003B-07: Update expected_count and integration verify

**Parent acceptance criteria:**
1. V152 FAIL fires for Gate-1 format with no round-trip test
2. V152 PASS for Gate-1 format with confirmed round-trip test
3. Check 2d STOP fires when BLOCKING+severity_confirmed gap exists for target format
4. Check 2d CONTINUE fires for HIGH or MEDIUM severity gaps
5. Check 2d requires severity_confirmed=true to count as BLOCKING (unconfirmed = ignored)
6. ≥3 V152 tests + ≥2 Check 2d tests pass

**Rollback strategy:**
- git revert check_continuation.py, governance_validators_dotnet.py, governance_validator_runner.py

---

#### Child Taskcard ID: TC-SPW-003B-01
**Parent:** TC-SPW-003B
**Title:** Inspect format-registry.yaml for gate_1 Field Structure
**Type:** CHILD / INVESTIGATION
**Status:** TODO

**Micro-steps:**
```
MS-003B-01-01: Read registry/format-registry.yaml first 100 lines
  Action: Locate the FODS entry, find how gate_1 status is expressed
  Completion check: Exact YAML path to gate_1 field recorded (e.g., formats[].gates.gate_1)

MS-003B-01-02: Check if "passed" is the correct value for a cleared gate
  Action: Compare FODS (gate 1 passed) vs another format (gate 1 not passed)
  Completion check: Confirmed value string for "passed" gate

MS-003B-01-03: Check how format_id is used in V152 context
  Action: Understand if declaration provides format_targets field
  Completion check: Path from declaration to format_id confirmed
```

**Evidence required:** `.local/evidences/TC-SPW-003B/registry-inspection.txt`
**Next valid task:** TC-SPW-003B-02

---

#### Child Taskcard ID: TC-SPW-003B-02
**Parent:** TC-SPW-003B
**Title:** Implement validate_format_roundtrip_coverage() (V152)
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Preconditions:** TC-SPW-003B-01 CLOSED

**Implementation notes from plan:**
- Check if format has gate_1: passed in format-registry.yaml
- If yes, scan `tests/{lang}/{format}/` for test files containing BOTH a write/save call AND a subsequent load/parse call in the same function body
- FAIL if no such test found

**Micro-steps:**
```
MS-003B-02-01: Add V152 function stub with docstring to governance_validators_dotnet.py
  Action: def validate_format_roundtrip_coverage(repo_root, declaration): ...
  Completion check: File parses without SyntaxError

MS-003B-02-02: Implement gate_1 check (read from format-registry.yaml)
  Action: For each format in declaration.format_targets, read format-registry.yaml,
    find gate_1 status
  Completion check: Correctly identifies FODS as Gate-1 passed

MS-003B-02-03: Implement round-trip test heuristic for .NET
  Action: Scan tests/net/{format}/ for .cs files; for each, check if file contains
    BOTH ("Save(" or "Write(") AND ("Load(" or "Parse(")
  Completion check: Heuristic correctly identifies a synthetic round-trip test

MS-003B-02-04: Implement round-trip test heuristic for Python
  Action: Scan tests/python/{format}/ for .py files; check for
    BOTH ("write_" or "to_bytes") AND ("parse_" or "load" or "from_bytes")
  Completion check: Heuristic correctly identifies Python round-trip tests

MS-003B-02-05: Implement FAIL return when no round-trip found for Gate-1 format
  Action: Return FAIL with blocks_sprint=True and descriptive message
  Completion check: FAIL returned for FODS .NET (which has no real round-trip yet)

MS-003B-02-06: Verify V152 produces WARN (not FAIL) for Python FOSS formats that have round-trips
  Action: Run V152 against fods Python → should PASS (parser + writer tests exist)
  Completion check: Python FOSS formats not falsely blocked
```

**Evidence required:** `.local/evidences/TC-SPW-003B/v152-manual-test.txt`
**Dependencies:** TC-SPW-003B-01 CLOSED

---

#### Child Taskcard ID: TC-SPW-003B-03
**Parent:** TC-SPW-003B
**Title:** Write V152 Tests (≥3 cases)
**Type:** CHILD / TESTING
**Status:** TODO

**Required cases:**
1. Gate-1 format, no test containing both Save and Load → V152 FAIL, blocks_sprint=True
2. Gate-1 format, test file with both Save and Load calls → V152 PASS
3. Non-Gate-1 format (gate_1: not_started), no round-trip → V152 PASS (not required yet)

**Micro-steps:**
```
MS-003B-03-01: Write test case 1 (no round-trip, Gate-1 → FAIL)
MS-003B-03-02: Write test case 2 (round-trip exists, Gate-1 → PASS)
MS-003B-03-03: Write test case 3 (no round-trip, non-Gate-1 → PASS)
MS-003B-03-04: Run tests
  Command: .venv/Scripts/pytest tests/supervisor/test_governance_validators_dotnet.py -k "roundtrip or v152" -v
  Completion check: All 3 cases PASS
```

**Evidence required:** `.local/evidences/TC-SPW-003B/v152-test-run.txt`

---

#### Child Taskcard ID: TC-SPW-003B-04
**Parent:** TC-SPW-003B
**Title:** Inspect check_continuation.py for Check 2d Insertion Point
**Type:** CHILD / INVESTIGATION
**Status:** TODO

**Micro-steps:**
```
MS-003B-04-01: Read check_continuation.py, locate existing Check 2 (autonomous_continue check)
  Action: Find the check that reads continuation-signal.json autonomous_continue field
  Completion check: Check 2 line number and logic recorded

MS-003B-04-02: Locate where format_targets is available from next-work-items
  Action: Check if next_work_items["format_targets"] is already parsed, or needs parsing
  Completion check: Path to format list confirmed

MS-003B-04-03: Confirm gap_ledger path is accessible
  Action: Find where gap-ledger.json path is or should be passed to check_continuation.py
  Completion check: Gap ledger path confirmed or found to need plumbing
```

**Evidence required:** `.local/evidences/TC-SPW-003B/continuation-inspection.txt`

---

#### Child Taskcard ID: TC-SPW-003B-05
**Parent:** TC-SPW-003B
**Title:** Implement Check 2d in check_continuation.py
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Preconditions:** TC-SPW-003A CLOSED (severity_confirmed set), TC-SPW-003B-04 CLOSED

**Micro-steps:**
```
MS-003B-05-01: Add Check 2d skeleton after Check 2c (or equivalent)
  Action: Add comment block "# Check 2d: No BLOCKING gaps for target formats"
  Completion check: Placeholder present, file parses

MS-003B-05-02: Implement gap ledger loading
  Action: Load reports/capability-layer/gap-ledger.json (or product-code-gap-ledger.yaml)
  Confirm which gap file to use based on TC-SPW-003B-04 findings
  Completion check: Gap file loads without error

MS-003B-05-03: Implement format_targets extraction from next-work-items
  Action: Read next_work_items["format_targets"] list
  Completion check: List accessible, handles empty case (no format targets → skip check)

MS-003B-05-04: Implement BLOCKING gap filter
  Action: Filter: gap["format"] in format_targets AND gap["severity"] == "BLOCKING"
    AND gap["status"] == "OPEN" AND gap.get("severity_confirmed", False) == True
  Completion check: Only severity_confirmed=True gaps trigger the gate

MS-003B-05-05: Implement STOP return for BLOCKING gaps
  Action: Return verdict=STOP, reason="blocking_gap_unresolved", gap_ids=[...]
  Completion check: Return format matches existing STOP format in file

MS-003B-05-06: Ensure no BLOCKING gaps in current state would incorrectly halt pilot work
  Action: Verify that after TC-SPW-003A classification, FODS .NET has no severity_confirmed
    BLOCKING gaps (otherwise pilot cannot proceed)
  Completion check: If BLOCKING gaps found for FODS .NET, ESCALATE to user before continuing
```

**Stop condition:** If FODS .NET has BLOCKING gaps after classification → ESCALATE, do not proceed to pilot.

---

#### Child Taskcard ID: TC-SPW-003B-06
**Parent:** TC-SPW-003B
**Title:** Write Check 2d Tests
**Type:** CHILD / TESTING
**Status:** TODO

**Required cases:**
1. BLOCKING+severity_confirmed gap for target format → check_continuation returns STOP
2. HIGH severity gap → check_continuation returns CONTINUE
3. BLOCKING but severity_confirmed=false → check_continuation returns CONTINUE (unconfirmed)

**Micro-steps:**
```
MS-003B-06-01: Locate or create test file for check_continuation.py
  Action: Check if tests/supervisor/test_check_continuation.py exists
  If not → create it with appropriate imports and test class

MS-003B-06-02: Write test case 1 (BLOCKING+confirmed → STOP)
MS-003B-06-03: Write test case 2 (HIGH → CONTINUE)
MS-003B-06-04: Write test case 3 (BLOCKING+unconfirmed → CONTINUE)
MS-003B-06-05: Run tests
  Command: .venv/Scripts/pytest tests/supervisor/test_check_continuation.py -k "check_2d or blocking_gap" -v
  Completion check: All 3 pass
```

**Evidence required:** `.local/evidences/TC-SPW-003B/check2d-test-run.txt`

---

#### Child Taskcard ID: TC-SPW-003B-07
**Parent:** TC-SPW-003B
**Title:** Update expected_count, Register V152, Integration Verify
**Type:** CHILD / INTEGRATION
**Status:** TODO

**Micro-steps:**
```
MS-003B-07-01: Register V152 in governance_validator_runner.py (add call + import)
MS-003B-07-02: Increment expected_count by 1 (for V152)
MS-003B-07-03: Run full validator suite — exit 0 required
  Command: python tools/supervisor/governance_validator_runner.py
MS-003B-07-04: Run all supervisor tests — 0 failures required
  Command: .venv/Scripts/pytest tests/supervisor/ -v --tb=short
MS-003B-07-05: Record integration pass
  Action: Write to .local/evidences/TC-SPW-003B/integration-run.txt
```

**Evidence required:** `.local/evidences/TC-SPW-003B/integration-run.txt`
**This closes TC-SPW-003B parent after integration passes.**

---

### Parent Taskcard ID: TC-SPW-004
**Title:** Design Artifact Gate — V153 and Skill Registry Update
**Type:** PARENT
**Status:** PROPOSED
**Owner:** machinery_agent
**Supervisor:** governance_reviewer

**Source:**
- Plan requirement IDs: REQ-ART-001, REQ-ART-002, REQ-ART-003
- Root cause: RC-04

**Objective:** Create the design artifact schema, implement V153 validator that blocks sprints touching src/net/ without a design artifact, and update .NET skill blocks to require the design_artifact_required field.

**Scope:**
```
Allowed files:
  - .supervisor/schemas/design-artifact.schema.json  (CREATE NEW)
  - tools/supervisor/design_artifact_validator.py  (CREATE NEW)
  - tools/supervisor/governance_validator_runner.py  (EDIT)
  - .supervisor/skill-registry.yaml  (EDIT — add-dotnet-api and add-dotnet-object-model-feature blocks)
  - tests/supervisor/test_design_artifact_validator.py  (CREATE NEW)
Forbidden:
  - src/net/**  (product changes only in TC-SPW-006)
  - tools/supervisor/governance_validators_dotnet.py  (TC-SPW-001 and 003B own this)
```

**Dependencies:** TC-SPW-001 VERIFIED (for understanding what the validator runner expects)

**Child taskcards:**
- TC-SPW-004-01: Inspect add-dotnet-api skill block (current state)
- TC-SPW-004-02: Create design-artifact.schema.json
- TC-SPW-004-03: Implement design_artifact_validator.py (V153)
- TC-SPW-004-04: Implement SAL spec_fact cross-reference check
- TC-SPW-004-05: Update skill registry
- TC-SPW-004-06: Write V153 tests (≥4 cases)
- TC-SPW-004-07: Register V153, update count, integration verify

**Parent acceptance criteria:**
1. V153 FAIL when .cs file changed and .local/design-artifacts/{taskcard_id}.yaml missing
2. V153 FAIL when artifact exists but is_partial_class=true for a new domain type
3. V153 WARN when artifact exists but spec_fact not found in SAL
4. V153 PASS when artifact is valid and all constraints satisfied
5. Design artifact schema is valid JSON Schema
6. Both .NET skill blocks have design_artifact_required: true field

---

#### Child Taskcard ID: TC-SPW-004-01
**Parent:** TC-SPW-004
**Title:** Inspect Current add-dotnet-api Skill Block
**Type:** CHILD / INVESTIGATION
**Status:** TODO

**Micro-steps:**
```
MS-004-01-01: Read .supervisor/skill-registry.yaml, locate add-dotnet-api block
  Action: Read the full block including all sub-fields
  Completion check: Block content recorded

MS-004-01-02: Record current pre_execution_checklist and forbidden_patterns fields
  Action: Extract exact field names and values
  Completion check: Both fields recorded

MS-004-01-03: Record add-dotnet-object-model-feature block for comparison
  Action: Same extraction for second skill
  Completion check: Both blocks recorded for comparison
```

**Evidence required:** `.local/evidences/TC-SPW-004/skill-inspection.txt`

---

#### Child Taskcard ID: TC-SPW-004-02
**Parent:** TC-SPW-004
**Title:** Create design-artifact.schema.json
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Preconditions:** TC-SPW-004-01 CLOSED

**The schema must enforce (per plan):**
- taskcard_id: required string
- format_id: required string
- language: required string (must be "dotnet")
- target_file: required string (must match src/net/ pattern)
- primary_class: required object
  - name: required string
  - is_partial_class: required boolean — V153 FAILS if true for new domain types
  - spec_qname: required string (non-empty)
  - estimated_loc: required integer (must be > 10 and < 800)
- public_api: required array, min 1 item
  - name, spec_fact, parser_source, writer_path, has_xml_doc (all required)
- no_dictionary_state: required boolean
- no_constant_returns: required boolean

**Micro-steps:**
```
MS-004-02-01: Create .supervisor/schemas/ directory if it doesn't exist
  Action: Check if directory exists; create if not
  Completion check: Directory exists

MS-004-02-02: Write design-artifact.schema.json with JSON Schema draft-7
  Action: Write schema file with all required fields and constraints
  Completion check: File exists and is valid JSON

MS-004-02-03: Validate schema is parseable
  Command: python -c "import json; json.load(open('.supervisor/schemas/design-artifact.schema.json'))"
  Completion check: No parse error
```

**Evidence required:** `.local/evidences/TC-SPW-004/schema-created.txt`

---

#### Child Taskcard ID: TC-SPW-004-03
**Parent:** TC-SPW-004
**Title:** Implement design_artifact_validator.py (V153 Core Logic)
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Preconditions:** TC-SPW-004-02 CLOSED

**Micro-steps:**
```
MS-004-03-01: Create tools/supervisor/design_artifact_validator.py with module docstring
  Action: Create file with import skeleton and validate_design_artifact_present() stub
  Completion check: File exists, python -c "import tools.supervisor.design_artifact_validator" succeeds

MS-004-03-02: Implement detection of .cs files in changed_files that are under src/net/
  Action: Filter declaration.changed_files for "src/net/" prefix
  Completion check: Correctly identifies .cs changes

MS-004-03-03: Implement taskcard_id extraction from declaration
  Action: Read declaration["sprint_id"] or "taskcard_id" field to look up artifact
  Completion check: Correct artifact path constructed: .local/design-artifacts/{id}.yaml

MS-004-03-04: Implement FAIL when artifact missing
  Action: If .cs changes detected AND artifact file doesn't exist → FAIL, blocks_sprint=True
  Completion check: FAIL fires for synthetic case with .cs change + no artifact

MS-004-03-05: Implement YAML loading and is_partial_class check
  Action: Load artifact YAML; if primary_class.is_partial_class = true → FAIL
  Completion check: FAIL fires for is_partial_class: true

MS-004-03-06: Implement plausibility checks
  Action:
    - estimated_loc must be > 10 → FAIL if not
    - estimated_loc must be < 800 → FAIL if not
    - spec_qname must be non-empty string → FAIL if empty
  Completion check: Each plausibility check fires on synthetic violation
```

**Evidence required:** `.local/evidences/TC-SPW-004/v153-core-implementation.txt`

---

#### Child Taskcard ID: TC-SPW-004-04
**Parent:** TC-SPW-004
**Title:** Implement SAL spec_fact Cross-Reference Check in V153
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Preconditions:** TC-SPW-004-03 CLOSED

**Purpose:** V153 should WARN (not FAIL) when a spec_fact in the design artifact does not exist in the SAL. This prevents fabricated fact IDs from silently passing.

**Micro-steps:**
```
MS-004-04-01: Locate SAL facts file(s) for cross-reference
  Action: Find sal/ or equivalent directory containing SAL fact IDs
  Completion check: SAL facts file path confirmed

MS-004-04-02: Implement spec_fact lookup
  Action: For each spec_fact in artifact.public_api[*].spec_fact,
    check if the ID appears in the SAL facts file
  Completion check: Lookup function returns True/False correctly

MS-004-04-03: Add WARN (not FAIL) when spec_fact not found
  Action: Add item to result with severity="WARN", blocks_sprint=False
  Completion check: WARN fires for non-existent FACT-ID, but sprint not blocked
```

**Evidence required:** `.local/evidences/TC-SPW-004/sal-crossref.txt`

---

#### Child Taskcard ID: TC-SPW-004-05
**Parent:** TC-SPW-004
**Title:** Update Skill Registry — Add design_artifact_required Field
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Preconditions:** TC-SPW-004-01 CLOSED

**Micro-steps:**
```
MS-004-05-01: Edit add-dotnet-api skill block in .supervisor/skill-registry.yaml
  Action: Add under pre_execution_checklist:
    - design_artifact_required: "Write .local/design-artifacts/{taskcard_id}.yaml before ANY .cs changes"
  And add under forbidden_patterns:
    - "touching src/net/ without a valid design artifact at .local/design-artifacts/{taskcard_id}.yaml"
  Completion check: Field added to add-dotnet-api block

MS-004-05-02: Edit add-dotnet-object-model-feature skill block
  Action: Same additions
  Completion check: Field added to add-dotnet-object-model-feature block

MS-004-05-03: Validate YAML is parseable
  Command: python -c "import yaml; yaml.safe_load(open('.supervisor/skill-registry.yaml'))"
  Completion check: No parse error
```

**Evidence required:** `.local/evidences/TC-SPW-004/skill-registry-update.txt`

---

#### Child Taskcard ID: TC-SPW-004-06
**Parent:** TC-SPW-004
**Title:** Write V153 Tests (≥4 cases)
**Type:** CHILD / TESTING
**Status:** TODO

**Required cases:**
1. .cs in changed_files, no artifact → V153 FAIL, blocks_sprint=True
2. Artifact with is_partial_class: true → V153 FAIL
3. Valid artifact, spec_fact not in SAL → V153 WARN (not FAIL)
4. Valid artifact, spec_fact in SAL, is_partial_class: false → V153 PASS

**Micro-steps:**
```
MS-004-06-01: Create tests/supervisor/test_design_artifact_validator.py
MS-004-06-02: Write test cases 1-4
MS-004-06-03: Run tests
  Command: .venv/Scripts/pytest tests/supervisor/test_design_artifact_validator.py -v
  Completion check: All 4 PASS
```

**Evidence required:** `.local/evidences/TC-SPW-004/v153-test-run.txt`

---

#### Child Taskcard ID: TC-SPW-004-07
**Parent:** TC-SPW-004
**Title:** Register V153, Update Count, Integration Verify
**Type:** CHILD / INTEGRATION
**Status:** TODO

**Micro-steps:**
```
MS-004-07-01: Import and register validate_design_artifact_present in governance_validator_runner.py
MS-004-07-02: Increment expected_count by 1 (for V153)
MS-004-07-03: Run full governance validator suite
  Command: python tools/supervisor/governance_validator_runner.py
  Completion check: Exit 0, correct count
MS-004-07-04: Run all supervisor tests
  Command: .venv/Scripts/pytest tests/supervisor/ -v --tb=short
  Completion check: 0 failures
MS-004-07-05: Record integration pass
  Action: Write to .local/evidences/TC-SPW-004/integration-run.txt
```

**This closes TC-SPW-004 parent after integration passes.**

---

### Parent Taskcard ID: TC-SPW-005
**Title:** Sprint Quality Audit — product_quality_audit.py Integration
**Type:** PARENT
**Status:** PROPOSED
**Owner:** machinery_agent
**Supervisor:** governance_reviewer

**Source:**
- Plan requirement IDs: REQ-AUDIT-001, REQ-AUDIT-002
- Root cause: RC-03

**Objective:** Create `tools/supervisor/product_quality_audit.py` implementing 6 product-state checks, and integrate it as a non-blocking Step 3b in `autonomous_cycle.py`. Quality audit results appear in sprint output and are written to `reports/product-quality/`.

**Scope:**
```
Allowed files:
  - tools/supervisor/product_quality_audit.py  (CREATE NEW)
  - tools/supervisor/autonomous_cycle.py  (EDIT — add Step 3b call)
  - tests/supervisor/test_product_quality_audit.py  (CREATE NEW)
Forbidden:
  - src/net/**  (no product changes)
  - tools/supervisor/governance_validator_runner.py  (audit is not a governance validator)
```

**Dependencies:** TC-SPW-001 CLOSED (audit uses V78_AGG's aggregate data)

**Child taskcards:**
- TC-SPW-005-01: Inspect autonomous_cycle.py for Step 3 structure
- TC-SPW-005-02: Implement product_quality_audit.py module
- TC-SPW-005-03: Integrate into autonomous_cycle.py Step 3b
- TC-SPW-005-04: Write unit tests (≥6 cases, one per check)
- TC-SPW-005-05: End-to-end verification

**Parent acceptance criteria:**
1. product_quality_audit.py exists and imports without error
2. Running against FODS .NET produces non-empty audit result with at least 4 check results
3. Audit output written to reports/product-quality/audit-{sprint_id}-{format}.yaml
4. autonomous_cycle.py integration: audit runs after step 3, does not change sprint grade
5. All 6 unit tests pass
6. Non-blocking: audit failure does not change sprint exit code

---

#### Child Taskcard ID: TC-SPW-005-01
**Parent:** TC-SPW-005
**Title:** Inspect autonomous_cycle.py Step 3 Structure
**Type:** CHILD / INVESTIGATION
**Status:** TODO

**Micro-steps:**
```
MS-005-01-01: Read tools/supervisor/autonomous_cycle.py
  Action: Find "step 3" comment block or grade_all() call
  Completion check: Step 3 line number and what follows it recorded

MS-005-01-02: Identify where formats_touched list is available
  Action: Find where changed_files or format_ids are available after grading
  Completion check: formats_touched access path confirmed

MS-005-01-03: Identify output write pattern for step 3 artifacts
  Action: See how other step 3 outputs are written (evidence paths, etc.)
  Completion check: File write pattern for Step 3b output confirmed
```

**Evidence required:** `.local/evidences/TC-SPW-005/autonomous-cycle-inspection.txt`

---

#### Child Taskcard ID: TC-SPW-005-02
**Parent:** TC-SPW-005
**Title:** Implement product_quality_audit.py (6 Checks)
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Preconditions:** TC-SPW-005-01 CLOSED

**The 6 checks (from plan):**
1. check_aggregate_loc — uses collect_partial_class_aggregates from TC-SPW-001
2. check_writer_surface — LOC of writer file vs Gate 1 status
3. check_roundtrip_coverage — same heuristic as V152
4. check_dictionary_state — count of V88 WARNs for the format
5. check_api_documentation — scan .cs for public methods without /// <summary>
6. check_partial_class_count — WARN if any class has > 3 partial files

**Micro-steps:**
```
MS-005-02-01: Create tools/supervisor/product_quality_audit.py with module + class skeleton
  Action: Define ProductQualityAudit class, AuditResult dataclass, CheckResult dataclass
  Completion check: Module imports without error

MS-005-02-02: Implement check_aggregate_loc() — import from TC-SPW-001
  Action: Call collect_partial_class_aggregates, compare to baseline aggregate caps
  Completion check: Returns CheckResult with correct WARN for FodsDocument

MS-005-02-03: Implement check_writer_surface()
  Action: Find {format}_writer.cs or {Format}Writer.cs; count LOC; check Gate 1 in registry
  FAIL threshold: < 100 LOC for Gate-1 format
  Completion check: FodsWriter.cs (57 LOC, Gate-1) → FAIL

MS-005-02-04: Implement check_roundtrip_coverage()
  Action: Reuse V152 heuristic logic (or import it)
  Completion check: FODS .NET (no round-trip test) → FAIL

MS-005-02-05: Implement check_dictionary_state()
  Action: Run V88 detection (WARN mode only) against all .cs files for format
  Completion check: Returns count of detached Dictionary fields found

MS-005-02-06: Implement check_api_documentation()
  Action: Scan src/net/{format}/*.cs for public methods/properties without /// <summary>
  Regex: r'public\s+\w+\s+\w+\s*[\(]' NOT preceded by '/// <summary>'
  Completion check: Count of undocumented public APIs returned

MS-005-02-07: Implement check_partial_class_count()
  Action: Use collect_partial_class_aggregates; WARN if any class has > 3 files
  Completion check: FodsDocument (10 files) → WARN

MS-005-02-08: Implement AuditResult.to_dict() and to_yaml()
  Action: Serialize all check results for file output
  Completion check: Output is valid YAML
```

---

#### Child Taskcard ID: TC-SPW-005-03
**Parent:** TC-SPW-005
**Title:** Integrate Quality Audit into autonomous_cycle.py as Step 3b
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Preconditions:** TC-SPW-005-02 CLOSED, TC-SPW-005-01 CLOSED

**Micro-steps:**
```
MS-005-03-01: Add import of ProductQualityAudit to autonomous_cycle.py
MS-005-03-02: Add Step 3b block immediately after Step 3 grade-all completes
  Action: Insert:
    # Step 3b: Product quality audit (non-blocking)
    for fmt in formats_touched:
        audit = ProductQualityAudit(repo_root)
        result = audit.run(fmt, language)
        out_path = f"reports/product-quality/audit-{sprint_id}-{fmt}.yaml"
        Path(out_path).write_text(result.to_yaml())
  Completion check: Block executes without error in test

MS-005-03-03: Verify step 3b does not modify sprint_grade or autonomous_continue
  Action: Read the function to confirm no grade-changing logic was added
  Completion check: Sprint grade unchanged after step 3b
```

---

#### Child Taskcard ID: TC-SPW-005-04
**Parent:** TC-SPW-005
**Title:** Write Unit Tests for product_quality_audit.py (≥6 cases)
**Type:** CHILD / TESTING
**Status:** TODO

**One test per check:**
1. check_aggregate_loc: synthetic class with 10 partial files at 5677 LOC → WARN
2. check_writer_surface: writer file at 57 LOC, Gate 1 passed → FAIL
3. check_roundtrip_coverage: no round-trip test file → FAIL
4. check_dictionary_state: file with 3 Dictionary fields → returns count 3
5. check_api_documentation: .cs with 2 undocumented public methods → returns count 2
6. check_partial_class_count: class with 10 partial files → WARN

**Micro-steps:**
```
MS-005-04-01: Create tests/supervisor/test_product_quality_audit.py
MS-005-04-02 through MS-005-04-07: Write one test per check
MS-005-04-08: Run all 6 tests
  Command: .venv/Scripts/pytest tests/supervisor/test_product_quality_audit.py -v
  Completion check: All 6 PASS
```

---

#### Child Taskcard ID: TC-SPW-005-05
**Parent:** TC-SPW-005
**Title:** End-to-End Verification of Quality Audit
**Type:** CHILD / VERIFICATION
**Status:** TODO

**Micro-steps:**
```
MS-005-05-01: Run product_quality_audit.run("fods", "dotnet") against current src/net/fods/
  Command: python -c "from tools.supervisor.product_quality_audit import ProductQualityAudit; ..."
  Completion check: Returns AuditResult with 6 check results, at least 3 WARNs/FAILs

MS-005-05-02: Verify output YAML written to reports/product-quality/audit-test-fods.yaml
  Completion check: File exists and is valid YAML

MS-005-05-03: Run autonomous cycle with a synthetic declaration and verify audit fires
  (Use existing test fixtures if available, or create a minimal synthetic one)
  Completion check: Audit output appears in evidence directory

MS-005-05-04: Record integration pass
  Action: Write to .local/evidences/TC-SPW-005/end-to-end-verification.txt
```

**This closes TC-SPW-005 parent after verification passes.**

---

### Parent Taskcard ID: TC-SPW-006
**Title:** Pilot Proof — Add GetCellFormula() to FODS .NET Through Healed Machinery
**Type:** PARENT
**Status:** PROPOSED
**Owner:** implementation_agent
**Supervisor:** governance_reviewer

**Source:**
- Plan requirement IDs: REQ-PILOT-001
- Root cause: all RC (pilot proves all fixes work in combination)

**Objective:** Add GetCellFormula() to FODS .NET as a standalone TableCell class (not a partial FodsDocument class). Every new validator must PASS. Evidence declaration references real SAL spec fact. Round-trip test confirms formula survives save+reload.

**Dependencies (ALL must be CLOSED first):**
- TC-SPW-001: V78_AGG active
- TC-SPW-002: V88 FAIL-on-new active
- TC-SPW-003A: PCG-* severities confirmed — FODS .NET must have no BLOCKING gaps after classification
- TC-SPW-003B: V152 and Check 2d active
- TC-SPW-004: V153 active
- TC-SPW-005: Quality audit active

**Stop condition — critical gate:**
After TC-SPW-003A confirms FODS .NET gap severities, if ANY FODS .NET gap is classified BLOCKING+severity_confirmed: Check 2d will block the pilot. In that case: ESCALATE to user. Do not proceed with pilot until user explicitly authorizes gap reclassification OR gap resolution.

**Scope:**
```
Allowed files:
  - .local/design-artifacts/TC-SPW-006-FORMULA.yaml  (CREATE NEW)
  - src/net/fods/Model/  (CREATE new directory and TableCell.cs only)
  - src/net/fods/Model/Table/TableCell.cs  (CREATE NEW — ~150 LOC)
  - src/net/fods/FodsParser.cs  (EDIT — add table:formula attribute read)
  - src/net/fods/FodsWriter.cs  (EDIT — add table:formula attribute write)
  - tests/net/fods/  (ADD test file — round-trip test)
  - samples/by-format/fods/  (ADD fixture file if none exists with formula)
Forbidden:
  - FodsDocument*.cs  (do not add to any FodsDocument partial class)
  - Any file not listed above
```

**Child taskcards:**
- TC-SPW-006-01: Prerequisite gate check (all TC-SPW-001 through TC-SPW-005 closed, no BLOCKING gaps)
- TC-SPW-006-02: Verify SAL spec fact for table:formula exists
- TC-SPW-006-03: Create design artifact and validate through V153
- TC-SPW-006-04: Implement TableCell.cs
- TC-SPW-006-05: Extend FodsParser to read table:formula
- TC-SPW-006-06: Extend FodsWriter to write table:formula
- TC-SPW-006-07: Create FODS fixture with formula cell and write round-trip test
- TC-SPW-006-08: Run full validator suite
- TC-SPW-006-09: Create evidence declaration and run quality audit

**Parent acceptance criteria:**
1. Design artifact exists at .local/design-artifacts/TC-SPW-006-FORMULA.yaml
2. V153 PASS on design artifact
3. V78_AGG: TableCell.cs is NOT a partial class of FodsDocument; does not affect FodsDocument aggregate
4. V88 PASS: no new Dictionary fields added
5. V152 PASS: round-trip test exists and contains both Save and Load calls
6. Check 2d: CONTINUE (no BLOCKING+confirmed gaps for FODS .NET after TC-SPW-003A)
7. TableCell.cs ≤ 150 LOC, has XML doc comment on GetCellFormula()
8. FodsParser reads table:formula attribute from XElement
9. FodsWriter writes table:formula attribute when formula is non-null
10. Round-trip test: load fixture → get formula → modify → save → reload → assert formula matches
11. Full governance validator suite passes (exit 0)
12. Product quality audit runs and delta shows improvement

**Rollback strategy:**
- git revert TableCell.cs, FodsParser.cs edits, FodsWriter.cs edits, test file
- Delete .local/design-artifacts/TC-SPW-006-FORMULA.yaml

---

#### Child Taskcard ID: TC-SPW-006-01
**Parent:** TC-SPW-006
**Title:** Prerequisite Gate Check
**Type:** CHILD / GATE
**Status:** TODO

**Micro-steps:**
```
MS-006-01-01: Verify TC-SPW-001 through TC-SPW-005 are all CLOSED
  Action: Read this plan, check each parent's status
  Completion check: All 5 parents show CLOSED status

MS-006-01-02: Verify no FODS .NET BLOCKING+confirmed gaps in gap ledger
  Action: Read reports/product-quality/product-code-gap-ledger.yaml
  Filter: format=fods, language=dotnet OR format=fods, severity=BLOCKING, severity_confirmed=true, status=OPEN
  Completion check: Zero results → proceed. Non-zero → ESCALATE, do not proceed.

MS-006-01-03: Confirm V153 is active (V78_AGG, V88, V152, Check 2d all registered)
  Action: Run python tools/supervisor/governance_validator_runner.py --list (or grep output)
  Completion check: V78_AGG, V88 (upgraded), V152, V153 all present in output
```

**Stop condition:** If BLOCKING gaps exist → mark TC-SPW-006-01 BLOCKED_EXTERNAL, escalate.

---

#### Child Taskcard ID: TC-SPW-006-02
**Parent:** TC-SPW-006
**Title:** Verify SAL Spec Fact for table:formula Exists
**Type:** CHILD / INVESTIGATION
**Status:** TODO

**Purpose:** The design artifact must reference a real spec fact. Verify FACT-FODS-TABLE-CELL-FORMULA exists in SAL or identify the correct fact ID before writing the artifact.

**Micro-steps:**
```
MS-006-02-01: Search SAL facts for "formula" or "table:formula"
  Action: Grep sal/ or equivalent for "formula" AND "table:formula"
  Completion check: SAL fact ID for table:formula attribute found

MS-006-02-02: Record correct fact ID for use in design artifact
  Action: Write fact ID to .local/evidences/TC-SPW-006/sal-fact-confirmation.txt
  Completion check: Fact ID recorded

MS-006-02-03: If fact NOT found — record finding and create new SAL fact entry
  Action: If table:formula not in SAL, add minimal SAL entry with ODF 1.3 §19.32 reference
  NOTE: ODF 1.3 §19.32 defines table:formula attribute on table:table-cell
  Completion check: Fact ID exists in SAL (either pre-existing or newly created)
```

**Evidence required:** `.local/evidences/TC-SPW-006/sal-fact-confirmation.txt`

---

#### Child Taskcard ID: TC-SPW-006-03
**Parent:** TC-SPW-006
**Title:** Create Design Artifact and Validate Through V153
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Preconditions:** TC-SPW-006-01 and TC-SPW-006-02 CLOSED

**Micro-steps:**
```
MS-006-03-01: Create .local/design-artifacts/TC-SPW-006-FORMULA.yaml
  Content (exact):
    taskcard_id: TC-SPW-006-FORMULA
    format_id: fods
    language: dotnet
    target_file: src/net/fods/Model/Table/TableCell.cs
    primary_class:
      name: TableCell
      namespace: FormatFactory.Fods.Model.Table
      is_partial_class: false
      spec_qname: table:table-cell
      estimated_loc: 150
    public_api:
      - name: GetCellFormula
        spec_fact: <fact ID from TC-SPW-006-02>
        parser_source: "FodsParser: reads table:formula attribute from XElement for table:table-cell"
        writer_path: "FodsWriter: writes table:formula attribute on table:table-cell element when non-null"
        has_xml_doc: true
        roundtrip_test_required: true
    no_dictionary_state: true
    no_constant_returns: true
    history_ids_in_source: false
    reviewer_note: "Pilot proof for TC-SPW-006 — demonstrates healed machinery"
  Completion check: File created, YAML is valid

MS-006-03-02: Run V153 against the design artifact directly
  Action: Execute design_artifact_validator.validate_design_artifact_present() with
    synthetic declaration containing TC-SPW-006-FORMULA as taskcard_id and
    src/net/fods/Model/Table/TableCell.cs as changed file
  Completion check: V153 returns PASS (not FAIL or WARN blocking)

MS-006-03-03: Run V78_AGG check — confirm TableCell won't violate aggregate
  Action: Since TableCell.cs is NOT a partial class of FodsDocument, it creates its OWN
    aggregate group (TableCell). At ~150 LOC, it's well under any cap.
  Completion check: V78_AGG analysis shows no violation for TableCell
```

**Evidence required:** `.local/evidences/TC-SPW-006/design-artifact-validation.txt`

---

#### Child Taskcard ID: TC-SPW-006-04
**Parent:** TC-SPW-006
**Title:** Implement TableCell.cs (Standalone Class, ~150 LOC)
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Preconditions:** TC-SPW-006-03 CLOSED

**Design constraints (from artifact):**
- Class: `FormatFactory.Fods.Model.Table.TableCell`
- NOT a partial class of FodsDocument
- Must have XML doc comment on the class and on GetCellFormula()
- No private Dictionary fields
- No constant returns
- GetCellFormula() must read from XElement (parser-provided), not from a cached dict

**Micro-steps:**
```
MS-006-04-01: Create src/net/fods/Model/Table/ directory
  Action: Create directory path if it doesn't exist

MS-006-04-02: Create TableCell.cs with namespace, using statements, XML doc on class
  Content:
    namespace FormatFactory.Fods.Model.Table;
    /// <summary>
    /// Represents a single cell in a FODS spreadsheet table.
    /// Spec: ODF 1.3 §19.32 (table:table-cell)
    /// </summary>
    public sealed class TableCell { ... }
  Completion check: File exists, compiles (if dotnet build available)

MS-006-04-03: Add private readonly XElement _cellElement field (parser-provided)
  Action: Add field: private readonly XElement _cellElement;
  And constructor: public TableCell(XElement cellElement) { _cellElement = cellElement; }
  Completion check: Constructor present with XElement parameter

MS-006-04-04: Implement GetCellFormula() method
  Action:
    /// <summary>
    /// Gets the cell formula text (table:formula attribute), or null if no formula.
    /// Spec: ODF 1.3 §19.382 (table:formula attribute on table:table-cell)
    /// </summary>
    public string? GetCellFormula() =>
        _cellElement.Attribute(XName.Get("formula", "urn:oasis:names:tc:opendocument:xmlns:table:1.0"))?.Value;
  Completion check: Method reads from XElement, not from a dictionary

MS-006-04-05: Verify LOC count ≤ 150
  Action: Count lines in file
  Completion check: ≤ 150 LOC

MS-006-04-06: Verify no Dictionary fields or constant returns
  Action: Grep file for 'Dictionary' and 'return null;' or 'return "";' patterns
  Completion check: Zero Dictionary fields. Constant returns: only null is acceptable as "no formula"
    — this is spec-correct (not a semantic stub) because null means "attribute absent"
```

**Evidence required:** `.local/evidences/TC-SPW-006/tablecell-implementation.txt`

---

#### Child Taskcard ID: TC-SPW-006-05
**Parent:** TC-SPW-006
**Title:** Extend FodsParser to Provide XElement to TableCell
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Purpose:** TableCell reads from a parser-provided XElement. FodsParser must create TableCell instances when parsing table:table-cell elements.

**Micro-steps:**
```
MS-006-05-01: Read FodsParser.cs to find where table:table-cell elements are processed
  Action: Search for "table-cell" or "table:table-cell" in FodsParser.cs
  Completion check: Parsing location found

MS-006-05-02: Add TableCell instantiation at the cell parsing location
  Action: When a table:table-cell XElement is found, create a TableCell instance
  and include it in the model (list, collection, or similar structure)
  Completion check: Parser creates TableCell objects

MS-006-05-03: Verify no LOC cap violation in FodsParser.cs
  Action: Count lines in FodsParser.cs before and after change
  Completion check: FodsParser.cs stays within its current baseline_loc_cap
```

**Evidence required:** `.local/evidences/TC-SPW-006/parser-extension.txt`

---

#### Child Taskcard ID: TC-SPW-006-06
**Parent:** TC-SPW-006
**Title:** Extend FodsWriter to Serialize table:formula Attribute
**Type:** CHILD / IMPLEMENTATION
**Status:** TODO

**Purpose:** Complete the round-trip: when a formula is set on a TableCell, FodsWriter must emit the table:formula attribute.

**Micro-steps:**
```
MS-006-06-01: Read FodsWriter.cs to understand current write path
  Action: Find where table:table-cell is serialized
  Completion check: Cell serialization location found

MS-006-06-02: Add formula attribute write when GetCellFormula() returns non-null
  Action: If TableCell.GetCellFormula() != null →
    cellElement.SetAttributeValue(XName.Get("formula", tableNs), formula)
  Completion check: formula attribute written to XML when present

MS-006-06-03: Verify FodsWriter.cs LOC still within baseline_loc_cap (57 LOC → grows, but
  FodsWriter.cs has baseline_loc_cap? Check — if not in baseline, no cap applies,
  new file starts with fresh 800-LOC budget)
  Completion check: LOC within bounds or new entry added to baseline
```

**Evidence required:** `.local/evidences/TC-SPW-006/writer-extension.txt`

---

#### Child Taskcard ID: TC-SPW-006-07
**Parent:** TC-SPW-006
**Title:** Create FODS Fixture and Write Round-Trip Test
**Type:** CHILD / TESTING
**Status:** TODO

**Purpose:** The round-trip test is required by V152. It must: load a FODS file with a formula cell → read formula → (optionally modify) → save → reload → verify formula preserved.

**Micro-steps:**
```
MS-006-07-01: Check if samples/by-format/fods/ contains any fixture with a formula cell
  Action: Grep for "table:formula" in existing sample files
  Completion check: Either find existing fixture OR plan to create one

MS-006-07-02: If no formula fixture exists, create samples/by-format/fods/formula-cell.fods
  Action: Create minimal valid FODS file with one cell having table:formula="of:=A1+A2"
  Content: Minimal ODF flat XML with office:document, table:table, one table:table-cell
    with table:formula attribute
  Completion check: File is valid XML; loads through FodsParser without error

MS-006-07-03: Write tests/net/fods/TestFodsFormulaRoundTrip.cs
  Content:
    [Test]
    public void FormulaPreservedAfterRoundTrip()
    {
        // Load
        var doc = FodsParser.Parse("samples/by-format/fods/formula-cell.fods");
        var cell = doc.GetSheet(0).GetCell(0, 0);
        var formula = cell.GetCellFormula();
        Assert.IsNotNull(formula);
        // Save
        var tmpPath = Path.GetTempFileName() + ".fods";
        FodsWriter.Save(doc, tmpPath);
        // Reload
        var doc2 = FodsParser.Parse(tmpPath);
        var formula2 = doc2.GetSheet(0).GetCell(0, 0).GetCellFormula();
        // Assert
        Assert.AreEqual(formula, formula2);
    }
  Completion check: Test file created, compiles (if dotnet build available)

MS-006-07-04: Verify round-trip test contains both Save and Load calls (V152 heuristic)
  Action: Grep for "Save(" and "Parse(" or "Load(" in the test file
  Completion check: Both patterns present → V152 will detect this as a round-trip test
```

**Evidence required:** `.local/evidences/TC-SPW-006/roundtrip-test.txt`

---

#### Child Taskcard ID: TC-SPW-006-08
**Parent:** TC-SPW-006
**Title:** Run Full Validator Suite Against Pilot Changes
**Type:** CHILD / VERIFICATION
**Status:** TODO

**Preconditions:** TC-SPW-006-04 through TC-SPW-006-07 CLOSED

**Micro-steps:**
```
MS-006-08-01: Run full governance validator suite
  Command: python tools/supervisor/governance_validator_runner.py
  Completion check: Exit 0. If non-zero, diagnose and fix before proceeding.

MS-006-08-02: Confirm V153 PASS (design artifact satisfies requirements)
  Completion check: V153 result = PASS in output

MS-006-08-03: Confirm V78_AGG PASS for TableCell (no aggregate violation)
  Completion check: TableCell aggregate (≤150 LOC) well under cap

MS-006-08-04: Confirm V88 PASS (no new Dictionary fields)
  Completion check: V88 result shows no new dictionary violations

MS-006-08-05: Confirm V152 PASS (round-trip test detected)
  Completion check: V152 finds formula round-trip test, returns PASS

MS-006-08-06: Record all validator results
  Action: Write to .local/evidences/TC-SPW-006/validator-suite-run.txt
```

**Stop condition:** If any validator FAILS → diagnose, fix in the appropriate child, re-run.

---

#### Child Taskcard ID: TC-SPW-006-09
**Parent:** TC-SPW-006
**Title:** Create Evidence Declaration and Run Quality Audit
**Type:** CHILD / CLOSEOUT
**Status:** TODO

**Preconditions:** TC-SPW-006-08 CLOSED (all validators pass)

**Micro-steps:**
```
MS-006-09-01: Write .local/evidences/TC-SPW-006/evidence-declaration.yaml
  Content: Standard evidence declaration format
    sprint_id: TC-SPW-006-pilot
    run_id: PQLH-001-pilot-run-001
    planned_work_items:
      - item_id: TC-SPW-006-FORMULA
        title: "Add GetCellFormula() to FODS .NET via healed machinery"
        status: completed
        spec_fact_refs: [<fact ID from TC-SPW-006-02>]
        gap_ledger_ref: REQ-PILOT-001
        target_files: [src/net/fods/Model/Table/TableCell.cs, ...]
        qnames: [table:table-cell, table:formula]
        parser_obligations: [FodsParser reads table:formula attribute]
        writer_obligations: [FodsWriter writes table:formula when non-null]
        roundtrip_proof: tests/net/fods/TestFodsFormulaRoundTrip.cs
    worker_self_verdict: PASS
  Completion check: YAML valid

MS-006-09-02: Run product quality audit on FODS .NET
  Action: python -c "from tools.supervisor.product_quality_audit import ProductQualityAudit; ..."
  Completion check: Audit runs, output written to reports/product-quality/audit-TC-SPW-006-pilot-fods.yaml

MS-006-09-03: Record baseline vs post-pilot audit delta
  Action: Compare before-pilot audit (if run) vs after-pilot audit
  Note: partial_class_count for TableCell = 1 (improvement vs FodsDocument at 10)
  Completion check: Delta recorded in .local/evidences/TC-SPW-006/quality-audit-delta.txt

MS-006-09-04: Score all parent TC-SPW-006 quality dimensions (1-5)
  Action: For each parent quality dimension, assign score and record reasoning
  Completion check: All dimensions ≥ 4/5 or REROUTED
```

**This closes TC-SPW-006 parent after quality scoring passes.**

---

### Parent Taskcard ID: TC-SPW-007
**Title:** Idempotency Verification and Final Report
**Type:** PARENT
**Status:** PROPOSED
**Owner:** machinery_agent
**Supervisor:** governance_reviewer

**Source:**
- Plan requirement IDs: REQ-IDEM-001
- Root cause: operational

**Objective:** Re-run all new/modified validators against post-pilot source with ZERO source changes. All results must be identical to the TC-SPW-006 run. Write the final report.

**Dependencies:** TC-SPW-006 CLOSED

**Child taskcards:**
- TC-SPW-007-01: Re-run full validator suite with no changes
- TC-SPW-007-02: Compare results to TC-SPW-006 run
- TC-SPW-007-03: Write final report

---

#### Child Taskcard ID: TC-SPW-007-01
**Parent:** TC-SPW-007
**Title:** Re-Run Full Validator Suite with Zero Source Changes
**Type:** CHILD / VERIFICATION
**Status:** TODO

**Micro-steps:**
```
MS-007-01-01: Confirm git status is clean (no uncommitted source changes)
  Command: git status --short
  Completion check: Zero modified source files

MS-007-01-02: Re-run full governance validator suite
  Command: python tools/supervisor/governance_validator_runner.py
  Completion check: Exit 0

MS-007-01-03: Re-run product quality audit for FODS .NET
  Action: Same command as TC-SPW-006-09-02
  Completion check: Audit completes without error

MS-007-01-04: Record all second-run validator outputs
  Action: Write to .local/evidences/TC-SPW-007/second-run-validators.txt
```

---

#### Child Taskcard ID: TC-SPW-007-02
**Parent:** TC-SPW-007
**Title:** Compare Second-Run Results to TC-SPW-006 Results
**Type:** CHILD / VERIFICATION
**Status:** TODO

**Micro-steps:**
```
MS-007-02-01: Diff second-run validator output vs TC-SPW-006 output
  Action: Compare .local/evidences/TC-SPW-006/validator-suite-run.txt
    vs .local/evidences/TC-SPW-007/second-run-validators.txt
  Completion check: Zero material differences (no new FAILs, no new WARNs,
    no validator result changes)

MS-007-02-02: Diff quality audit output vs TC-SPW-006 audit output
  Completion check: Identical check results (no flapping)

MS-007-02-03: Record idempotency verdict
  Action: Write MATERIAL_SECOND_RUN_CHANGES = 0 to evidence file
  Completion check: Evidence file written
```

---

#### Child Taskcard ID: TC-SPW-007-03
**Parent:** TC-SPW-007
**Title:** Write Final Report
**Type:** CHILD / DOCUMENTATION
**Status:** TODO

**Preconditions:** TC-SPW-007-02 CLOSED

**Micro-steps:**
```
MS-007-03-01: Create reports/product-quality/final-report-pqlh-001.yaml
  Required sections:
    mission_id: PQLH-001
    plan_id: splendid-prancing-wind
    root_causes_addressed:
      - RC-01: V78_AGG implemented — per-class-aggregate measurement active
      - RC-02: Trajectory enforcement added — aggregate cannot grow on touch
      - RC-03: Product quality audit runs each sprint — state visible independent of grades
      - RC-04: V153 design artifact gate — commitments made before code written
      - RC-05: V152 + Check 2d — round-trip absence and BLOCKING gaps now block continuation
      - RC-06: Oracle still underused for .NET — documented as follow-on
    machinery_changes:
      - V78_AGG: [details]
      - V88 upgraded: [details]
      - V152: [details]
      - V153: [details]
      - Check 2d: [details]
      - ProductQualityAudit: [details]
    pilot_result:
      taskcard: TC-SPW-006
      capability_added: GetCellFormula()
      spec_authority: ODF 1.3 table:formula
      validators_passed: [V78_AGG, V88, V152, V153, Check 2d]
      round_trip_confirmed: true
    quality_audit_delta:
      before: [summary of known issues]
      after: [improvements from TableCell design]
    remaining_known_debt:
      - FodsDocument aggregate 5677 LOC — known violation with trajectory cap
      - Existing dictionary fields in ReadOps — WARN, pre-existing grandfathered
      - FodsWriter.cs minimal — tracked by quality audit, needs separate sprint
    future_work:
      - Oracle extension to .NET (recommended follow-on plan)
      - FodsDocument redesign through healed machinery (separate plan)
      - Portfolio scan of all .NET formats (after machinery proven stable)
    idempotency: PASS — MATERIAL_SECOND_RUN_CHANGES = 0
    verdict: PRODUCT_CODE_SYSTEM_HEALED_AND_LIBRARIES_PRODUCTION_READY
      # Use PRODUCT_CODE_SYSTEM_OR_PRODUCT_REPAIR_REQUIRES_REWORK if any pilot failed

MS-007-03-02: Verify YAML is valid
  Command: python -c "import yaml; yaml.safe_load(open('reports/product-quality/final-report-pqlh-001.yaml'))"
  Completion check: No parse error
```

**This closes TC-SPW-007 parent and the PQLH-001 mission.**

---

## PART V: MACHINE STATE

```yaml
# taskcard-state-machine (embedded)
parent_states:
  - PROPOSED
  - READY
  - IN_PROGRESS
  - CHILDREN_IN_PROGRESS
  - INTEGRATION_PENDING
  - VERIFIED
  - SCORED
  - CLOSED
  - BLOCKED
  - BLOCKED_EXTERNAL
  - DEFERRED_WITH_REASON

parent_transitions:
  PROPOSED: [READY]
  READY: [IN_PROGRESS]
  IN_PROGRESS: [CHILDREN_IN_PROGRESS, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]
  CHILDREN_IN_PROGRESS: [INTEGRATION_PENDING, BLOCKED, BLOCKED_EXTERNAL]
  INTEGRATION_PENDING: [VERIFIED, BLOCKED]
  VERIFIED: [SCORED]
  SCORED: [CLOSED, REROUTED]
  BLOCKED: [READY]
  BLOCKED_EXTERNAL: [READY]
  REROUTED: [IN_PROGRESS]

child_states:
  - TODO
  - READY
  - IN_PROGRESS
  - IMPLEMENTED
  - VERIFIED
  - SCORED
  - CLOSED
  - REROUTED
  - BLOCKED
  - BLOCKED_EXTERNAL
  - DEFERRED_WITH_REASON

child_transitions:
  TODO: [READY]
  READY: [IN_PROGRESS]
  IN_PROGRESS: [IMPLEMENTED, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]
  IMPLEMENTED: [VERIFIED]
  VERIFIED: [SCORED]
  SCORED: [CLOSED, REROUTED]
  REROUTED: [IN_PROGRESS]
  BLOCKED: [READY]

micro_step_states:
  - PENDING
  - READY
  - ACTIVE
  - COMPLETE
  - FAILED
  - BLOCKED
  - SKIPPED_NOT_APPLICABLE

invalid_transitions:
  # These must be BLOCKED by execution agent:
  - TODO → CLOSED
  - READY → CLOSED
  - IMPLEMENTED → CLOSED    # must pass through VERIFIED and SCORED
  - parent CLOSED while mandatory children not CLOSED
  - child CLOSED while mandatory micro-steps not COMPLETE or SKIPPED_NOT_APPLICABLE
  - REROUTED → CLOSED without rework evidence
  - BLOCKED_EXTERNAL → CLOSED without unblock_evidence recorded
  - SKIPPED_NOT_APPLICABLE without reason field populated
```

```yaml
# taskcard-state-machine-validation-rules (embedded)
rules:
  R1: "A parent taskcard may only move to CLOSED when ALL mandatory child taskcards are CLOSED"
  R2: "A child taskcard may only move to VERIFIED when all micro-steps are COMPLETE or SKIPPED_NOT_APPLICABLE"
  R3: "A child taskcard may only move to CLOSED after SCORED with all quality dimensions ≥ 4/5"
  R4: "REROUTED status requires rework_reason and new child taskcard or micro-step created"
  R5: "BLOCKED_EXTERNAL requires external_blocker_classification string"
  R6: "SKIPPED_NOT_APPLICABLE micro-steps require reason field"
  R7: "A parent in BLOCKED state may only move to READY once the blocker is documented as resolved"
```

---

## PART VI: DEPENDENCY DAG

```yaml
# execution-dag (embedded)
# Format: taskcard_id → depends_on: [list], parallel_safe_with: [list]

TC-SPW-001:
  depends_on: []
  parallel_safe_with: [TC-SPW-002, TC-SPW-003A, TC-SPW-004]
  note: "Can start immediately. No dependencies. V78 changes different file from V88."

TC-SPW-002:
  depends_on: []
  parallel_safe_with: [TC-SPW-001, TC-SPW-003A, TC-SPW-004]
  note: "V88 in different file from V78. Can run in parallel with TC-SPW-001."
  soft_dependency: TC-SPW-001
    reason: "Sequenced after TC-SPW-001 to avoid count confusion in governance_validator_runner.py"

TC-SPW-003A:
  depends_on: []
  parallel_safe_with: [TC-SPW-001, TC-SPW-002, TC-SPW-004]
  note: "Gap ledger classification. No code changes. Can start immediately."

TC-SPW-003B:
  depends_on: [TC-SPW-001, TC-SPW-003A]
  parallel_safe_with: [TC-SPW-004, TC-SPW-005]
  note: "Needs TC-SPW-001 for V78_AGG runner integration (count). Needs TC-SPW-003A for severity_confirmed."
  conflict: TC-SPW-001
    reason: "Both modify governance_validator_runner.py expected_count. Run sequentially."

TC-SPW-004:
  depends_on: [TC-SPW-001]
  parallel_safe_with: [TC-SPW-003B, TC-SPW-005]
  note: "Can start after TC-SPW-001 count updates are done. governance_validator_runner.py
    then has only one open conflict source."

TC-SPW-005:
  depends_on: [TC-SPW-001, TC-SPW-002]
  parallel_safe_with: [TC-SPW-003B, TC-SPW-004]
  note: "Quality audit uses collect_partial_class_aggregates (TC-SPW-001) and
    V88 WARN data (TC-SPW-002). Both must exist first."

TC-SPW-006:
  depends_on: [TC-SPW-001, TC-SPW-002, TC-SPW-003A, TC-SPW-003B, TC-SPW-004, TC-SPW-005]
  parallel_safe_with: []
  note: "All machinery must be healed before pilot."

TC-SPW-007:
  depends_on: [TC-SPW-006]
  parallel_safe_with: []
  note: "Final verification only after pilot completes."

# Recommended execution order (minimizing conflicts):
# Wave 1 (parallel): TC-SPW-001, TC-SPW-002, TC-SPW-003A
# Wave 2 (after Wave 1): TC-SPW-003B, TC-SPW-004, TC-SPW-005
# Wave 3 (after Wave 2): TC-SPW-006
# Wave 4 (after Wave 3): TC-SPW-007
```

```yaml
# file-ownership-and-locks (embedded)
# Only one taskcard may actively modify each file at a time.

tools/supervisor/governance_validators_dotnet.py:
  owner: TC-SPW-001 (primary), TC-SPW-003B (V152 addition)
  conflict_rule: TC-SPW-003B may not edit until TC-SPW-001 is CLOSED

tools/supervisor/governance_validators_dotnet_semantic.py:
  owner: TC-SPW-002

tools/supervisor/governance_validator_runner.py:
  owner: TC-SPW-001 (count update) → TC-SPW-003B (count update) → TC-SPW-004 (count update)
  conflict_rule: Sequential. Each must close before next modifies.

tools/supervisor/check_continuation.py:
  owner: TC-SPW-003B

tools/supervisor/design_artifact_validator.py:
  owner: TC-SPW-004 (CREATE)

tools/supervisor/product_quality_audit.py:
  owner: TC-SPW-005 (CREATE)

tools/supervisor/autonomous_cycle.py:
  owner: TC-SPW-005

.supervisor/skill-registry.yaml:
  owner: TC-SPW-004

.supervisor/schemas/design-artifact.schema.json:
  owner: TC-SPW-004 (CREATE)

.supervisor/schemas/partial-class-exclusions.json:
  owner: TC-SPW-001 (CREATE)

registry/source-structure-baseline.json:
  owner: TC-SPW-001

reports/product-quality/product-code-gap-ledger.yaml:
  owner: TC-SPW-003A

reports/product-quality/gap-severity-classification-log.yaml:
  owner: TC-SPW-003A (CREATE)

tests/supervisor/test_governance_validators_dotnet.py:
  owner: TC-SPW-001 (adds aggregate tests), TC-SPW-002 (adds V88 tests), TC-SPW-003B (adds V152 tests)
  conflict_rule: Each owns distinct test functions. Coordinate to avoid merge conflicts.

tests/supervisor/test_design_artifact_validator.py:
  owner: TC-SPW-004 (CREATE)

tests/supervisor/test_product_quality_audit.py:
  owner: TC-SPW-005 (CREATE)

src/net/fods/Model/Table/TableCell.cs:
  owner: TC-SPW-006 (CREATE)

src/net/fods/FodsParser.cs:
  owner: TC-SPW-006

src/net/fods/FodsWriter.cs:
  owner: TC-SPW-006

tests/net/fods/TestFodsFormulaRoundTrip.cs:
  owner: TC-SPW-006 (CREATE)
```

---

## PART VII: VALIDATION MATRIX

```yaml
# validation-command-matrix (embedded, per parent taskcard)

TC-SPW-001:
  unit_tests:
    command: ".venv/Scripts/pytest tests/supervisor/test_governance_validators_dotnet.py -k 'aggregate' -v"
    expected: "≥5 PASSED, 0 FAILED"
    mandatory: true
  integration:
    command: "python tools/supervisor/governance_validator_runner.py"
    expected: "Exit 0, count = previous + 1"
    mandatory: true
  regression:
    command: ".venv/Scripts/pytest tests/supervisor/ -v --tb=short"
    expected: "0 FAILED (all existing tests pass)"
    mandatory: true
  negative_controls:
    - description: "New partial class growing FodsDocument aggregate → FAIL"
      method: "synthetic .cs file in unit test with aggregate_loc > cap"
    - description: "Touching aggregate file causes LOC increase → TRAJECTORY_FAIL"
      method: "synthetic sprint touch in unit test"
    - description: "*.g.cs file not counted in aggregate"
      method: "unit test with synthetic generated file"

TC-SPW-002:
  unit_tests:
    command: ".venv/Scripts/pytest tests/supervisor/test_governance_validators_dotnet.py -k 'v88 or dictionary' -v"
    expected: "≥3 PASSED, 0 FAILED"
    mandatory: true
  integration:
    command: "python tools/supervisor/governance_validator_runner.py"
    expected: "Exit 0"
    mandatory: true
  regression:
    command: ".venv/Scripts/pytest tests/supervisor/ -v --tb=short"
    expected: "0 FAILED"
    mandatory: true
  negative_controls:
    - description: "New dict field without write path → FAIL"
    - description: "Pre-existing dict field → WARN only (not FAIL)"

TC-SPW-003A:
  validation:
    method: "YAML parse check on gap ledger after edits"
    command: "python -c \"import yaml; yaml.safe_load(open('reports/product-quality/product-code-gap-ledger.yaml'))\""
    expected: "No exception"
    mandatory: true
  manual_check:
    - "All PCG-* entries have severity_confirmed: true"
    - "Audit log file exists and non-empty"

TC-SPW-003B:
  unit_tests_v152:
    command: ".venv/Scripts/pytest tests/supervisor/test_governance_validators_dotnet.py -k 'roundtrip or v152' -v"
    expected: "≥3 PASSED"
    mandatory: true
  unit_tests_check2d:
    command: ".venv/Scripts/pytest tests/supervisor/test_check_continuation.py -k 'check_2d or blocking_gap' -v"
    expected: "≥3 PASSED"
    mandatory: true
  integration:
    command: "python tools/supervisor/governance_validator_runner.py"
    expected: "Exit 0, count = previous + 1 (for V152)"
    mandatory: true

TC-SPW-004:
  unit_tests:
    command: ".venv/Scripts/pytest tests/supervisor/test_design_artifact_validator.py -v"
    expected: "≥4 PASSED"
    mandatory: true
  schema_validation:
    command: "python -c \"import json; json.load(open('.supervisor/schemas/design-artifact.schema.json'))\""
    expected: "No exception"
    mandatory: true
  skill_validation:
    command: "python -c \"import yaml; yaml.safe_load(open('.supervisor/skill-registry.yaml'))\""
    expected: "No exception"
    mandatory: true
  negative_controls:
    - "Missing artifact → V153 FAIL"
    - "is_partial_class: true → V153 FAIL"
    - "Invalid spec_fact → V153 WARN (not FAIL)"

TC-SPW-005:
  unit_tests:
    command: ".venv/Scripts/pytest tests/supervisor/test_product_quality_audit.py -v"
    expected: "≥6 PASSED"
    mandatory: true
  end_to_end:
    command: "python -c \"from tools.supervisor.product_quality_audit import ProductQualityAudit; r = ProductQualityAudit('.'). run('fods','dotnet'); print(r.to_yaml())\""
    expected: "Non-empty YAML output with ≥4 check results"
    mandatory: true

TC-SPW-006:
  full_validator_suite:
    command: "python tools/supervisor/governance_validator_runner.py"
    expected: "Exit 0"
    mandatory: true
  specific_validators:
    - "V153 PASS in output"
    - "V78_AGG no new FAIL for TableCell"
    - "V88 PASS (no new dictionary fields)"
    - "V152 PASS (round-trip test detected)"
  round_trip:
    method: "TestFodsFormulaRoundTrip test confirms formula preserved"
    if_dotnet_build_unavailable: "Verify test file contains both Save and Load calls using grep"
    mandatory: true

TC-SPW-007:
  idempotency:
    command: "diff previous-validator-output.txt second-run-validator-output.txt"
    expected: "Zero material differences"
    mandatory: true
  final_report:
    command: "python -c \"import yaml; yaml.safe_load(open('reports/product-quality/final-report-pqlh-001.yaml'))\""
    expected: "No parse error, verdict field present"
    mandatory: true
```

---

## PART VIII: EVIDENCE CONTRACT

```yaml
# evidence-contract (embedded)
authoritative_plan: C:\Users\prora\.claude\plans\splendid-prancing-wind.md
artifact_role: evidence_contract
execution_authority: false

evidence_root: .local/evidences/

structure:
  .local/evidences/TC-SPW-001/
    - inspection-notes.txt         # TC-SPW-001-01 output
    - exclusion-config.txt         # TC-SPW-001-02 output
    - aggregate-helper-trace.txt   # TC-SPW-001-03 output
    - v78-agg-manual-run.txt       # TC-SPW-001-04 output
    - trajectory-test.txt          # TC-SPW-001-05 output
    - baseline-migration.txt       # TC-SPW-001-06 output
    - v78-agg-test-run.txt         # TC-SPW-001-07 output
    - runner-count-update.txt      # TC-SPW-001-08 output
    - integration-run.txt          # TC-SPW-001-09 output  [CLOSES TC-SPW-001]

  .local/evidences/TC-SPW-002/
    - inspection-notes.txt
    - git-state-access.txt
    - v88-update.txt
    - v88-test-run.txt
    - integration-run.txt          [CLOSES TC-SPW-002]

  .local/evidences/TC-SPW-003A/
    - pcg-inventory.txt
    - severity-classifications.txt
    - gap-severity-classification-log.yaml reference
    [CLOSES TC-SPW-003A when all 4 children closed]

  .local/evidences/TC-SPW-003B/
    - registry-inspection.txt
    - v152-manual-test.txt
    - v152-test-run.txt
    - continuation-inspection.txt
    - check2d-test-run.txt
    - integration-run.txt          [CLOSES TC-SPW-003B]

  .local/evidences/TC-SPW-004/
    - skill-inspection.txt
    - schema-created.txt
    - v153-core-implementation.txt
    - sal-crossref.txt
    - skill-registry-update.txt
    - v153-test-run.txt
    - integration-run.txt          [CLOSES TC-SPW-004]

  .local/evidences/TC-SPW-005/
    - autonomous-cycle-inspection.txt
    - end-to-end-verification.txt  [CLOSES TC-SPW-005]

  .local/evidences/TC-SPW-006/
    - sal-fact-confirmation.txt
    - design-artifact-validation.txt
    - tablecell-implementation.txt
    - parser-extension.txt
    - writer-extension.txt
    - roundtrip-test.txt
    - validator-suite-run.txt
    - quality-audit-delta.txt
    [evidence-declaration.yaml written here]   [CLOSES TC-SPW-006]

  .local/evidences/TC-SPW-007/
    - second-run-validators.txt
    [CLOSES TC-SPW-007 + PQLH-001 MISSION]

evidence_rules:
  - Every evidence file must be non-empty
  - Evidence files must reference authoritative_plan path
  - Evidence files must NOT contain alternative execution instructions
  - Raw test output (pytest stdout) is acceptable evidence
  - "Evidence exists" does NOT mean "evidence was inspected" — agent must inspect content
```

---

## PART IX: QUALITY SCORING

```yaml
# quality-scoring-model (embedded)
threshold: 4  # minimum score per dimension (scale 1-5)

parent_dimensions:
  - root_cause_coverage: "Does this taskcard address its listed RC-* root causes?"
  - child_completeness: "Are all mandatory children CLOSED with evidence?"
  - integration_completeness: "Does the integration check confirm no regressions?"
  - dependency_correctness: "Were all dependencies CLOSED before this taskcard started?"
  - preserved_behavior: "No existing test broken by this taskcard's work?"
  - evidence_completeness: "All required evidence files exist and are non-empty?"
  - rerun_consistency: "Would running again produce identical results?"
  - production_readiness: "Would a new sprint that runs into this validator get expected results?"

child_dimensions:
  - requirement_correctness: "Does this child's output satisfy its parent requirement?"
  - implementation_correctness: "Is the code/change technically correct?"
  - scope_discipline: "Only allowed files touched?"
  - validation_strength: "Are negative cases tested (not just positive)?"
  - evidence_completeness: "Evidence file exists and non-empty?"
  - regression_safety: "No existing test broken?"
  - maintainability: "Is config-driven, not hardcoded?"
  - production_readiness: "Works correctly in autonomous loop context?"

reroute_trigger: "Any mandatory dimension scores < 4/5"
reroute_action: "Mark child REROUTED, create repair micro-step, re-verify before re-scoring"
```

---

## PART X: COMPLETION GATE COUNTERS

The following counters must all reach target before TC-SPW-007 can be closed.

| Counter | Target | TC Source | Verification Command |
|---------|--------|-----------|---------------------|
| V78_AGG_VALIDATOR_MISSING | 0 | TC-SPW-001 | grep "V78_AGG" in validator runner output |
| V78_AGG_TEST_FAILURES | 0 | TC-SPW-001-07 | pytest test count |
| V88_NEW_ADDITION_BLOCKING | 0 new false negatives | TC-SPW-002 | TC-SPW-002-05 integration |
| V152_VALIDATOR_MISSING | 0 | TC-SPW-003B | grep "V152" in runner output |
| V153_VALIDATOR_MISSING | 0 | TC-SPW-004 | grep "V153" in runner output |
| PCG_GAPS_WITHOUT_SEVERITY_CONFIRMED | 0 | TC-SPW-003A | grep "severity_confirmed: false" in gap ledger |
| QUALITY_AUDIT_NOT_RUNNING | 0 | TC-SPW-005 | report file exists after pilot |
| PILOT_VALIDATORS_FAILING | 0 | TC-SPW-006-08 | validator suite exit code |
| PILOT_ROUND_TRIP_MISSING | 0 | TC-SPW-006-07 | grep Save+Load in test file |
| MATERIAL_SECOND_RUN_CHANGES | 0 | TC-SPW-007-02 | diff of two runs |
| FINAL_REPORT_MISSING | 0 | TC-SPW-007-03 | file existence check |

---

## PART XI: EXECUTION HANDOFF

The following instructions apply to every execution agent that picks up this plan.

### Before Starting Any Taskcard

1. Read PART I (Preserved Analysis) completely. Do not skip root cause analysis.
2. Identify the current parent taskcard using the DAG in PART VI.
3. Read the parent taskcard completely (objective, scope, acceptance criteria, rollback).
4. Identify the first non-CLOSED child of that parent.
5. Read the child taskcard completely (scope, preconditions, micro-steps).
6. Confirm all preconditions are satisfied before starting.
7. Confirm all forbidden files. Do NOT touch them.

### Executing Each Micro-Step

1. Read the micro-step completely before acting.
2. Confirm: which parent, which child, which requirement does this serve?
3. Confirm: what is the allowed operation? (inspect / create / edit / run / validate / record)
4. Execute EXACTLY the action described. Do not add scope.
5. Capture evidence immediately (write to .local/evidences/{TC-ID}/).
6. Verify the completion check passes before moving on.
7. Mark the micro-step COMPLETE (or FAILED / BLOCKED if it did not complete).

### After Each Child Taskcard

1. Confirm all micro-steps are COMPLETE or SKIPPED_NOT_APPLICABLE.
2. Run the validation commands from PART VII.
3. Score the child on all quality dimensions (score 1-5).
4. If any dimension < 4 → mark REROUTED, create a repair micro-step, re-run.
5. Only move child to CLOSED after SCORED ≥ 4/5 on all dimensions.

### After Each Parent Taskcard

1. Confirm ALL mandatory children are CLOSED.
2. Run parent integration checks.
3. Score the parent on all quality dimensions.
4. Mark parent CLOSED only after integration checks pass and all scores ≥ 4/5.
5. Consult the DAG in PART VI to identify the next valid parent.

### What Execution Agents Must NOT Do

- Close a parent before all mandatory children are CLOSED
- Mark a child CLOSED before it is SCORED with evidence
- Skip micro-steps without recording SKIPPED_NOT_APPLICABLE with reason
- Touch files not listed in the taskcard's Allowed files list
- Broaden scope beyond the taskcard objective
- Treat test file existence as proof of passing (must run the test)
- Treat evidence file existence as proof of correctness (must inspect content)
- Proceed with TC-SPW-006 if TC-SPW-003B-05 found BLOCKING gaps for FODS .NET
- Choose unrelated work from next-sprint.md while this plan is active

### Next Valid Starting Points (as of plan creation)

```
First parallel wave (all PROPOSED, all can start):
  TC-SPW-001 → start with TC-SPW-001-01
  TC-SPW-002 → start with TC-SPW-002-01
  TC-SPW-003A → start with TC-SPW-003A-01

Second wave (after Wave 1 closed):
  TC-SPW-003B → start with TC-SPW-003B-01
  TC-SPW-004 → start with TC-SPW-004-01
  TC-SPW-005 → start with TC-SPW-005-01

Third wave (after Wave 2 closed):
  TC-SPW-006 → start with TC-SPW-006-01 (prerequisite gate)

Fourth wave (after TC-SPW-006 closed):
  TC-SPW-007 → start with TC-SPW-007-01
```

---

## CHANGE LEDGER (v3 Enhancement)

```yaml
# Changes from v2 (617 lines) to v3 (this version)
# No analysis was removed. All root causes, tradeoffs, risks preserved verbatim.

additions:
  - PREFLIGHT RECORD section (embedded preflight artifacts)
  - REQUIREMENTS INVENTORY (REQ-* stable IDs for all actionable requirements)
  - SOLUTION OPTIONS (scorecard for key design decisions, selections recorded)
  - MACHINE STATE section (parent/child/micro transitions, invalid transition rules)
  - DEPENDENCY DAG section (file ownership, parallel safety, wave ordering)
  - VALIDATION MATRIX (per-TC commands, expected results, negative controls)
  - EVIDENCE CONTRACT (per-TC evidence files, rules)
  - QUALITY SCORING MODEL (dimensions, threshold, reroute rule)
  - COMPLETION GATE COUNTERS (reformatted as measurable counters with verification commands)
  - EXECUTION HANDOFF (step-by-step agent instructions)
  - CHANGE LEDGER (this section)

structural_changes:
  - TC-SPW-003 split into TC-SPW-003A (gap severity) and TC-SPW-003B (V152+Check2d)
    Reason: Two distinct sub-tasks in one parent taskcard
  - All TC-SPW-* taskcards expanded into parent + child + micro-step format
  - TC-SPW-007 error corrected: "V78_AGG listed twice" → corrected to distinct validators

preserved_verbatim:
  - "Honest Assessment: What Is Actually Broken" section
  - "True Root Causes" (RC-01 through RC-06)
  - "What to Preserve" table
  - "What Must Change" table
  - "Solution Design Principle"
  - "Explicit Tradeoffs" (all 5 tradeoffs)
  - "Risks and Likely Limits" (R1-R3, Likely Limit)
  - "What This Plan Deliberately Does Not Do" (all 5 points)
  - Original pseudocode and implementation guidance from all TC-SPW-* sections
    (moved into child taskcard bodies or micro-step action descriptions)
```

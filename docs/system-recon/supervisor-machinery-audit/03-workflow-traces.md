# 03 - Workflow Traces

All traces verified against source at commit `6b3f6f07` on branch `main`, 2026-07-06.

---

## TRACE-001: Sprint Closeout

```yaml
workflow_trace:
  trace_id: TRACE-001
  entry_point: "Agent writes .local/evidences/<run_id>/evidence-declaration.yaml"
  modules:
    - tools/supervisor/sprint_executor_validate.py
    - tools/supervisor/supervisor_loop.py
    - tools/supervisor/autonomous_cycle.py
    - tools/supervisor/evidence_declaration.py
    - tools/supervisor/inspect_declared_evidence.py
    - tools/supervisor/grade_declared_work.py
    - tools/supervisor/generate_next_worker_prompt.py
    - tools/supervisor/evidence_manifest.py
    - tools/supervisor/anti_skip_checker.py
    - tools/supervisor/build_declaration_review_package.py
  state_read:
    - .local/evidences/<run_id>/evidence-declaration.yaml
    - registry/format-registry.yaml
    - registry/source-structure-baseline.json
    - reports/supervisor/gap-ledger.json
  state_written:
    - .local/supervisor/continuation-signal.json
    - reports/supervisor/evidence-review.json
    - reports/supervisor/next-sprint.md
    - reports/supervisor/next-work-items.json
    - reports/supervisor/session-resume.md
    - reports/supervisor/approval-gates.md
    - .local/evidences/<run_id>/evidence-manifest.json
    - .local/evidences/<run_id>/review-package.zip
  decisions:
    - "sprint_executor_validate.py --repair auto-corrects markdown fences, type mismatches, banned fields"
    - "grade_all() assigns per-item verdict: ACCEPTED, REWORK, or REJECTED"
    - "anti_skip_checker.run_all_checks() enforces severity map (19 checks)"
    - "generate_prompt() + generate_next_work_items() select next sprint scope"
    - "evidence_manifest.validate_manifest() ensures declared paths exist and are non-empty"
  validators:
    - sprint_executor_validate.py (declaration schema and field repair)
    - anti_skip_checker.py (anti-skip severity checks)
    - evidence_manifest.py validate_manifest()
  evidence:
    - evidence-review.json (per-item grading verdicts)
    - review-package.zip (SHA-256 printed to output)
    - evidence-manifest.json (hash-verified file inventory)
  alternate_paths:
    - "supervisor_loop.py autonomous-cycle is the standard entry; autonomous_cycle.py run_cycle() is the direct call"
    - "LLM grading path: grade_declared_work._sv_llm_call() via GPT_OSS_ENDPOINT, fallback _sv_sdk_fallback()"
    - "--sync-index flag triggers control_index sync (best-effort, non-blocking)"
  bypasses:
    - "Supreme Directive: if any closeout step fails, skip it and continue to next sprint"
    - "supervisor_loop.py has 120s timeout — use autonomous_cycle.py directly if timeout triggers"
  failure_behavior: >
    Exit 0 = all accepted, continue. Exit 3 = rework items exist, log and attempt
    quick fix, continue regardless. Exit 1 = declaration schema error, log and continue.
    Exit 9 = unexpected error, log and continue. All non-zero exits are non-blocking
    per Supreme Directive.
  status: VERIFIED_FROM_SOURCE
```

---

## TRACE-002: Autonomous Continuation

```yaml
workflow_trace:
  trace_id: TRACE-002
  entry_point: "python tools/supervisor/check_continuation.py"
  modules:
    - tools/supervisor/check_continuation.py
  state_read:
    - .local/supervisor/continuation-signal.json
    - reports/supervisor/approval-gates.md
    - .local/supervisor/active-plan-lock.json
    - .local/supervisor/plan-locks/<session_id>_<hash>.json
  state_written: []  # read-only — produces JSON to stdout
  decisions:
    - "Check 1: session identity (CCI-MVP) — SESSION_MISMATCH / CHAT_ID_MISMATCH are non-overridable hard stops"
    - "Check 1b: plan completed in current session — PLAN_COMPLETED_IN_SESSION is non-overridable"
    - "Check 2: plan lock status — ACTIVE_PLAN_INCOMPLETE blocks CONTINUE"
    - "Check 3: POST_PLAN_TERMINAL — plan closed with --terminal in this session"
    - "Check 4: approval gates — APPROVAL_GATE_NO"
    - "Check 5: iteration count — MAX_ITERATIONS (overridable, reset to 0)"
    - "Check 6: structural GOV_BLOCK — must be resolved before product deepening"
    - "Check 7: rework_items in continuation signal"
  validators: []
  evidence:
    - "JSON to stdout: {verdict, reason, next_work_items_path, rework_items}"
  alternate_paths:
    - "On CONTINUE: agent reads next-work-items.json + next-sprint.md, executes sprint, returns to TRACE-001"
    - "On STOP with MAX_ITERATIONS: governed rollover — reset iteration to 0 and continue"
    - "On STOP with SESSION_MISMATCH: run reset_track_signal.py --track product to adopt signal"
    - "If check_continuation.py itself fails: read next-sprint.md directly and continue"
  bypasses:
    - "MAX_ITERATIONS is not a true stop — reset to 0 and continue"
    - "Non-structural STOP reasons can be overridden per Supreme Directive"
    - "Per-chat plan precedence: plan taskcards override next-sprint.md regardless of verdict"
  failure_behavior: >
    If the script itself crashes, the agent reads next-sprint.md directly and continues.
    SESSION_MISMATCH, CHAT_ID_MISMATCH, POST_PLAN_TERMINAL, and
    PLAN_COMPLETED_IN_SESSION are the only non-overridable stops.
  status: VERIFIED_FROM_SOURCE
```

---

## TRACE-003: Governance Validation

```yaml
workflow_trace:
  trace_id: TRACE-003
  entry_point: "tools/supervisor/governance_validator_runner.py (687 LOC)"
  modules:
    - tools/supervisor/governance_validator_runner.py
    - tools/supervisor/governance_validators.py
    - tools/supervisor/governance_validators_ext.py
    - tools/supervisor/governance_validators_import.py
    - tools/supervisor/governance_validators_path.py
    - tools/supervisor/governance_validators_output_quality.py
    # Plus 13 additional validator files (18 total, 10,908 LOC combined)
  state_read:
    - "src/python/**/*.py (product source files)"
    - "src/net/**/*.cs (product source files)"
    - registry/source-structure-baseline.json
    - registry/format-registry.yaml
    - .supervisor/skill-registry.yaml
  state_written:
    - "Validator results to stdout/JSON (consumed by autonomous_cycle.py)"
  decisions:
    - "153 validate_* functions across 18 files"
    - "GOV_BLOCK validators (monolith_detection, validate_source_architecture, validate_multi_responsibility_file, validate_analytics_naming_enforced) prevent next sprint"
    - "Non-GOV_BLOCK failures are warnings — do not block continuation"
  validators:
    - "V1-V50: structural validators"
    - "V75-V76: import direction validators"
    - "V82: oracle validator"
    - "V110: blocks src/dotnet/ path references"
    - "V111-V122: extended validators"
    - "V134-V136: output quality validators (anti-manual-JSON-escaping, anti-raw-HTML-td)"
  evidence:
    - "Per-validator PASS/FAIL/WARN verdicts"
    - "GOV_BLOCK entries in continuation-signal.json rework_items"
  alternate_paths:
    - "Called from autonomous_cycle.py during sprint closeout"
    - "Called from CI workflow (.github/workflows/ci.yml via pytest)"
    - "Called standalone for pre-commit checks"
  bypasses:
    - "known_violations in source-structure-baseline.json exempt files from LOC/function-count limits"
    - "baseline_loc_cap is write-once — existing violations are frozen, not re-measured"
  failure_behavior: >
    GOV_BLOCK validators trigger structural_govblock_must_be_resolved_first stop reason
    in check_continuation.py. The agent must run the analytics separation sprint (Production
    Library Standard v2 section 8.1) before product deepening can resume. Non-GOV_BLOCK
    validator failures are logged but do not block the next sprint.
  status: VERIFIED_FROM_SOURCE
```

---

## TRACE-004: Plan Lock Lifecycle

```yaml
workflow_trace:
  trace_id: TRACE-004
  entry_point: "python tools/supervisor/write_plan_lock.py --plan-path <path>"
  modules:
    - tools/supervisor/write_plan_lock.py
    - tools/supervisor/check_continuation.py
    - tools/supervisor/lifecycle_audit.py
    - tools/supervisor/plan_lock_gc.py
  state_read:
    - .local/supervisor/plan-locks/*.json (existing locks)
    - .local/supervisor/active-plan-lock.json
    - "The plan file itself (for taskcard parsing during lifecycle audit)"
  state_written:
    - .local/supervisor/plan-locks/<session_id>_<hash>.json
    - .local/supervisor/active-plan-lock.json
    - .local/supervisor/lifecycle-audit-results.json (when --audit-gate used)
  decisions:
    - "Initial write: status=IN_PROGRESS, last_taskcard=<first taskcard id>"
    - "--terminal: status=TERMINAL_CLOSED — blocks all further work in this session"
    - "--complete: status=COMPLETE — reserved for external/background closure"
    - "--audit-gate (machinery plans): runs lifecycle_audit.py first, may set ITERATION_REQUIRED"
    - "SUPERSEDED: applied to stale locks from prior sessions (not TERMINAL_CLOSED)"
  validators:
    - "lifecycle_audit.py (post-plan audit for machinery_hardening plans)"
    - "check_continuation.py Check 1b (detects COMPLETE in current session)"
  evidence:
    - "Plan lock JSON files with status, plan_path, session_id, last_taskcard"
    - "lifecycle-audit-results.json (when audit-gate is used)"
  alternate_paths:
    - "Normal closure: --terminal (in-session)"
    - "Machinery closure: lifecycle_audit.py → --terminal --audit-gate"
    - "Audit finds unresolved work: ITERATION_REQUIRED → agent adds taskcards, continues"
    - "Stale lock recovery: plan_lock_gc.py or manual SUPERSEDED status write"
  bypasses:
    - "plan_lock_gc.py cleans stale locks"
    - "Manual SUPERSEDED status write for stuck locks (documented in MEMORY.md)"
    - "Test-artifact locks (AppData/Temp/pytest paths) must be manually superseded"
  failure_behavior: >
    If write_plan_lock.py fails, the plan lock is not created and check_continuation.py
    will not see an active plan. lifecycle_audit.py requires table-format taskcard status
    (pipe-delimited, 2 columns) — code-block Status: fields are NOT parsed. Plans without
    the summary table cause ITERATION_REQUIRED (too many lines between heading and Status).
  status: VERIFIED_FROM_SOURCE
```

---

## TRACE-005: Evidence Grading

```yaml
workflow_trace:
  trace_id: TRACE-005
  entry_point: "grade_declared_work.grade_all() in tools/supervisor/grade_declared_work.py (1,127 LOC)"
  modules:
    - tools/supervisor/grade_declared_work.py
    - tools/supervisor/inspect_declared_evidence.py
  state_read:
    - .local/evidences/<run_id>/evidence-declaration.yaml
    - "Evidence files referenced in the declaration (test outputs, source diffs, screenshots)"
    - "Product source files (for _check_product_source_content)"
  state_written:
    - reports/supervisor/evidence-review.json
  decisions:
    - "_evidence_hash() computes content hash for caching"
    - "_get_cached_grade() returns cached verdict if evidence unchanged"
    - "grade_item() applies rule-based grading for each work item"
    - "semantic_verify_item() optionally invokes LLM for semantic checks"
    - "_check_product_source_content() verifies declared source changes exist"
    - "Per-item verdict: ACCEPTED, REWORK, or REJECTED"
  validators:
    - "inspect_declared_evidence.inspect_declaration() (evidence path existence and content)"
    - "_check_product_source_content (source file reality check)"
  evidence:
    - "evidence-review.json with per-item verdicts, scores, and failure reasons"
  alternate_paths:
    - "Without LLM: rule-based grading only (deterministic, faster)"
    - "With LLM: _sv_llm_call() via GPT_OSS_ENDPOINT → _sv_sdk_fallback() via openai SDK"
    - "Cached path: _get_cached_grade() returns immediately if evidence hash matches"
  bypasses:
    - "LLM grading is optional — absence of GPT_OSS_ENDPOINT falls back to rule-based only"
    - "Evidence hash caching skips re-grading for unchanged items"
  failure_behavior: >
    If grading fails for a single item, that item receives REWORK verdict. If the entire
    grading pipeline fails, autonomous_cycle.py returns exit 9. Per Supreme Directive,
    the agent logs the error and continues to the next sprint.
  status: VERIFIED_FROM_SOURCE
```

---

## TRACE-006: Task Selection

```yaml
workflow_trace:
  trace_id: TRACE-006
  entry_point: "generate_next_worker_prompt.generate_next_work_items()"
  modules:
    - tools/supervisor/generate_next_worker_prompt.py
    - tools/supervisor/capability_feature_compiler.py (504 LOC, 22 functions)
    - tools/supervisor/generate_supervisor_packet.py
  state_read:
    - reports/supervisor/gap-ledger.json
    - .governance/capabilities/registry.yaml
    - reports/supervisor/evidence-review.json
    - registry/format-registry.yaml
  state_written:
    - reports/supervisor/next-work-items.json
    - reports/supervisor/next-sprint.md
  decisions:
    - "capability_feature_compiler.py compiles capability→format→gap mappings"
    - "_run_capability_consumer() performs gap analysis against ledger"
    - "detect_proof_gaps_for_empty_queue() fires when no work items remain in queue"
    - "Rework items from prior sprint get priority in next-work-items.json"
    - "POC targets and format rotation influence selection order"
  validators: []
  evidence:
    - "next-work-items.json (structured work items with capability_id, format, gap references)"
    - "next-sprint.md (prose prompt for agent consumption)"
  alternate_paths:
    - "Empty queue: detect_proof_gaps_for_empty_queue() generates gap-closure work"
    - "Rework path: rework_items from evidence-review.json get re-queued as priority items"
    - "tools/capability_layer/capability_to_feature_compiler.py is a 5-LOC redirect stub (planning tool, not pipeline)"
  bypasses:
    - "Per-chat plan precedence: agent ignores next-work-items.json when a plan is active"
    - "generate_supervisor_packet.py has pre-existing bug (load_selected_product_gaps receives list not dict) — non-blocking"
  failure_behavior: >
    If task selection fails, next-work-items.json and next-sprint.md are not regenerated.
    The agent falls back to reading the existing next-sprint.md from the prior cycle.
    Per Supreme Directive, this is never a stop condition.
  status: VERIFIED_FROM_SOURCE
```

---

## TRACE-007: Skill Dispatch

```yaml
workflow_trace:
  trace_id: TRACE-007
  entry_point: "Agent invokes skill command (e.g., /score-format, /run-oracle)"
  modules:
    - .supervisor/skill-registry.yaml (123 skills registered)
    - .claude/commands/<skill>.md (command definitions)
    - tools/supervisor/choose_skill_or_handoff.py (264 LOC)
    - tools/supervisor/validate_skill_contracts.py
    - tools/supervisor/validate_skill_registry.py
    - tools/supervisor/validate_skill_transcript.py
  state_read:
    - .supervisor/skill-registry.yaml
    - .claude/commands/<skill>.md
    - .governance/capabilities/registry.yaml (119 active capabilities)
  state_written:
    - "Depends on skill — most produce evidence files or state updates"
    - .supervisor/skill-idempotency-proof.yaml (for /run-skill-idempotency)
  decisions:
    - "skill_id maps to command file in .claude/commands/"
    - "choose_skill_or_handoff.py selects skill vs. delegation to another agent"
    - "Some skills invoke tools/supervisor/ scripts via subprocess"
    - "Skill validation ensures contracts, registry consistency, transcript correctness"
  validators:
    - validate_skill_contracts.py
    - validate_skill_registry.py
    - validate_skill_transcript.py
  evidence:
    - "Skill execution receipts (collect-skill-execution-receipts capability)"
    - "Skill-specific outputs (oracle packages, evidence bundles, gap entries)"
  alternate_paths:
    - "Direct script invocation: agent calls the underlying tool directly without skill dispatch"
    - "Handoff: choose_skill_or_handoff.py delegates to specialized agent"
  bypasses:
    - "Agent can invoke underlying scripts directly, bypassing skill registry"
    - "detect-ad-hoc-execution capability detects and flags unregistered skill use"
  failure_behavior: >
    Skill dispatch failure does not block the agent. The agent can invoke the underlying
    tool or script directly. Validation failures (contract, registry, transcript) are
    governance warnings, not hard stops.
  status: VERIFIED_FROM_SOURCE
```

---

## TRACE-008: Python Product Path (FODS)

```yaml
workflow_trace:
  trace_id: TRACE-008
  entry_point: "from fods.parser import parse_fods (src/python/fods/parser.py, 475 LOC)"
  modules:
    - src/python/fods/parser.py (475 LOC)
    - src/python/fods/writer.py (182 LOC)
    - src/python/fods/fods_analytics.py (analytics, separate per Production Library Standard v2)
    - src/python/fods/Compat/ (class-based facade wrapping dict-based codec)
    - oracle/formats/fods/ (8 test cases)
    - tests/python/fods/ (1,571 tests)
  state_read:
    - "Input FODS XML file (samples/by-format/fods/)"
  state_written:
    - "Output FODS XML file (writer path)"
  decisions:
    - "Uses defusedxml if available, falls back to stdlib xml.etree.ElementTree"
    - "Returns dict model with sheets, cells, metadata"
    - "Analytics separated from parser/writer per Production Library Standard v2"
    - "Compat/ provides class-based API (e.g., FodsCell) as facade only"
  validators:
    - "Oracle verification: 8 test cases, all PASS"
    - "Test suite: 1,571 tests (10.35s)"
    - "Governance validators: V110 blocks src/dotnet/ references, V134-V136 output quality"
  evidence:
    - "oracle/formats/fods/ (8 oracle packages)"
    - "tests/python/fods/ test results"
  alternate_paths:
    - "Direct dict access: parse_fods() returns dict, no Compat/ required"
    - "Compat facade: class-based API for consumers preferring OOP"
    - "Roundtrip: parse_fods() → modify dict → write_fods()"
  bypasses:
    - "defusedxml absence: falls back to stdlib (less secure but functional)"
  failure_behavior: >
    Parse errors raise exceptions with context (line number, element path).
    Writer errors raise on invalid model structure. Oracle test failures are
    surfaced in evidence-review.json as REWORK items.
  status: VERIFIED_FROM_SOURCE
```

---

## TRACE-009: .NET Product Path (FODS)

```yaml
workflow_trace:
  trace_id: TRACE-009
  entry_point: "src/net/fods/FodsParser.cs -> FodsDocument.cs (907 LOC)"
  modules:
    - src/net/fods/FodsParser.cs
    - src/net/fods/FodsDocument.cs (907 LOC, root model)
    - src/net/fods/FodsDocumentReadOps.cs (893 LOC)
    - src/net/fods/FodsDocumentEditOps.cs (738 LOC)
    - src/net/fods/FodsDocumentCellProps.cs (687 LOC)
    - src/net/fods/FodsWriter.cs
    - "6 exporters: CSV, TSV, JSON, HTML, Markdown, TXT"
    - tests/net/fods/
  state_read:
    - "Input FODS XML file"
  state_written:
    - "Output FODS XML or export format (CSV/TSV/JSON/HTML/Markdown/TXT)"
  decisions:
    - "10,197 LOC across 55 .cs files — most mature .NET product format"
    - "Separate operation classes: ReadOps, EditOps, CellProps (responsibility separation)"
    - "6 export targets from single parsed model"
    - "FormatFactory.Fods.csproj project structure"
  validators:
    - "V110: blocks any declaration referencing src/dotnet/ paths"
    - "V134-V136: output quality (anti-manual-JSON-escaping, anti-raw-HTML-td)"
    - "C# assertion quality: 132 STRONG_PROOF, 41 PARTIAL_PROOF, 0 WEAK_PROOF (173 files)"
  evidence:
    - "tests/net/fods/ test files"
    - "C# assertion analysis results"
    - "Cross-platform parity fixtures (tests/cross-platform/csv/parity-fixtures.yaml)"
  alternate_paths:
    - "Parse only: FodsParser.cs → FodsDocument model"
    - "Read operations: FodsDocumentReadOps.cs for cell/sheet queries"
    - "Edit operations: FodsDocumentEditOps.cs for mutation"
    - "Export: FodsWriter.cs or format-specific exporter"
  bypasses: []
  failure_behavior: >
    Parse exceptions on malformed XML. Export errors on unsupported cell types.
    Test failures surfaced in CI (.github/workflows/ci.yml) and governance validators.
  status: VERIFIED_FROM_SOURCE
```

---

## Workflow Entanglement Summary

Module sharing across traces reveals coupling hotspots. The table below counts how many
traces each module participates in.

| Module | Traces | Trace IDs |
|---|---|---|
| `tools/supervisor/autonomous_cycle.py` | 4 | TRACE-001, TRACE-003, TRACE-005, TRACE-006 |
| `tools/supervisor/grade_declared_work.py` | 2 | TRACE-001, TRACE-005 |
| `tools/supervisor/generate_next_worker_prompt.py` | 2 | TRACE-001, TRACE-006 |
| `tools/supervisor/check_continuation.py` | 2 | TRACE-002, TRACE-004 |
| `tools/supervisor/evidence_declaration.py` | 2 | TRACE-001, TRACE-005 |
| `tools/supervisor/governance_validator_runner.py` | 2 | TRACE-001, TRACE-003 |
| `tools/supervisor/lifecycle_audit.py` | 2 | TRACE-001, TRACE-004 |
| `.supervisor/skill-registry.yaml` | 2 | TRACE-003, TRACE-007 |
| `registry/format-registry.yaml` | 3 | TRACE-001, TRACE-003, TRACE-006 |
| `reports/supervisor/evidence-review.json` | 3 | TRACE-001, TRACE-005, TRACE-006 |

### Most Entangled Pairs

| Trace Pair | Shared Modules | Coupling Type |
|---|---|---|
| TRACE-001 + TRACE-005 | `autonomous_cycle.py`, `grade_declared_work.py`, `evidence_declaration.py`, `inspect_declared_evidence.py` | **Strongest** — grading is embedded in closeout |
| TRACE-001 + TRACE-006 | `autonomous_cycle.py`, `generate_next_worker_prompt.py` | **Strong** — task selection is embedded in closeout |
| TRACE-001 + TRACE-003 | `autonomous_cycle.py`, `governance_validator_runner.py` | **Strong** — governance runs during closeout |
| TRACE-002 + TRACE-004 | `check_continuation.py` | **Moderate** — continuation reads plan lock state |
| TRACE-001 + TRACE-002 | `continuation-signal.json` (shared state file) | **Moderate** — closeout writes what continuation reads |

### Isolation Assessment

| Trace | Independence Level | Notes |
|---|---|---|
| TRACE-008 (Python product) | **High** | Product code touches no supervisor modules |
| TRACE-009 (.NET product) | **High** | Product code touches no supervisor modules |
| TRACE-007 (Skill dispatch) | **Medium** | Reads registry, invokes supervisor tools, but no direct pipeline coupling |
| TRACE-004 (Plan lock) | **Medium** | Consumed by TRACE-002, but write path is independent |
| TRACE-002 (Continuation) | **Low** | Depends on outputs of TRACE-001 and TRACE-004 |
| TRACE-001 (Closeout) | **Lowest** | Embeds TRACE-003, TRACE-005, and TRACE-006 as sub-workflows |

### Key Architectural Observation

`autonomous_cycle.py` is the central nexus — it orchestrates TRACE-001 (closeout),
which embeds TRACE-003 (governance), TRACE-005 (grading), and TRACE-006 (task selection)
as sequential sub-steps. This means a failure in any embedded trace propagates through
the closeout exit code. The Supreme Directive mitigates this by treating all non-zero
exits as non-blocking, but it also means evidence quality signals (TRACE-005) and
governance violations (TRACE-003) can be silently skipped under the "log and continue" rule.

TRACE-008 and TRACE-009 (product paths) are fully decoupled from the supervisor machinery.
They interact only through governance validators (TRACE-003) at CI time and oracle
verification at evidence time (TRACE-005).

# 09 - Hardened Execution Plan

## Strategy: Incremental Consolidation (Option 2 + Option 6)

This plan is NOT executed during this investigation. It is a dependency-aware plan ready for external review.

---

## Stage 0 — Baseline and Freeze

### TC-S0-001: Establish Behavioral Baseline

```yaml
taskcard:
  task_id: TC-S0-001
  objective: Record current test results, evidence pipeline output, and governance validator output as the behavioral baseline
  affected_paths:
    - tests/supervisor/
    - tests/evidence/
    - tools/supervisor/governance_validator_runner.py
  problem_ids: []
  dependencies: []
  guarantees_preserved: [G-001, G-002, G-006]
  implementation_outline:
    - Run full pytest suite and record pass/fail/skip counts
    - Run governance_validator_runner.py and record all validator results
    - Run autonomous_cycle.py with a known declaration and record outputs
    - Store all baseline outputs in .local/supervisor/consolidation-baseline/
  forbidden_changes:
    - No production code changes
    - No test modifications
  tests:
    - pytest tests/supervisor/ -v --tb=short > baseline-test-results.txt
    - python tools/supervisor/governance_validator_runner.py > baseline-validators.txt
  evidence:
    - baseline-test-results.txt
    - baseline-validators.txt
    - baseline-autonomous-cycle-output.json
  rollback: N/A (read-only baseline)
  acceptance_criteria:
    - All baseline files captured
    - Test results reproducible on re-run
  stop_conditions:
    - Full test suite has >10% failure rate (investigate first)
  risk: LOW
  lane: coordinator
  human_approval: false
  parallel_safe: true
```

---

## Stage 1 — Observability and Characterization

### TC-S1-001: Add Call Tracing to SUSPECTED_GHOST Files

```yaml
taskcard:
  task_id: TC-S1-001
  objective: Add lightweight call tracing to the 9 SUSPECTED_GHOST components to determine if they are invoked at runtime
  affected_paths:
    - tools/supervisor/autonomous_loop_runner.py
    - tools/supervisor/autonomous_orchestrator.py
    - tools/supervisor/autonomous_poc_controller.py
    - tools/supervisor/autonomous_train_executor.py
    - tools/supervisor/autonomous_host_daemon.py
    - tools/supervisor/autonomous_host_runner.py
    - tools/supervisor/external_host_loop.py
    - tools/supervisor/autonomous_task_generator.py
    - tools/supervisor/generate_mainstream_execution_packet.py
  problem_ids: [P-003]
  dependencies: [TC-S0-001]
  guarantees_preserved: [G-001, G-007]
  implementation_outline:
    - Add a timestamped log line at module import time and at __main__ entry
    - Store traces in .local/supervisor/call-traces/
    - Run 3-5 normal sprint cycles with tracing enabled
    - Analyze which files were invoked and by what mechanism
  forbidden_changes:
    - No behavioral changes to any file
    - Only add import-time and entry-point logging
  tests:
    - Verify tracing does not change any autonomous_cycle.py behavior
    - Run baseline test suite; compare results
  evidence:
    - call-traces/ directory with invocation records
    - Analysis report classifying each file as INVOKED or NOT_INVOKED
  rollback: Remove tracing lines (git revert)
  acceptance_criteria:
    - All 9 files have tracing
    - At least 3 sprint cycles completed with tracing
    - Each file classified as INVOKED or NOT_INVOKED with evidence
  stop_conditions:
    - Tracing causes test failures
  risk: LOW
  lane: observability
  human_approval: false
  parallel_safe: true
```

### TC-S1-002: Characterize AI Integration Usage

```yaml
taskcard:
  task_id: TC-S1-002
  objective: Determine if the 6 ai_* files (1,367 LOC) are invoked via any mechanism
  affected_paths:
    - tools/supervisor/ai_evidence_critic.py
    - tools/supervisor/ai_implementation_designer.py
    - tools/supervisor/ai_learning_loop.py
    - tools/supervisor/ai_product_brain.py
    - tools/supervisor/ai_sprint_manager.py
    - tools/supervisor/ai_supervisor_advisor.py
  problem_ids: [P-005]
  dependencies: [TC-S0-001]
  guarantees_preserved: []
  implementation_outline:
    - Search all YAML, JSON, MD, shell files for references to these module names
    - Check git log for when they were last modified
    - Check if any config or prompt references them by name
    - Classify as CONFIRMED_DEAD or INVOKED_VIA_<mechanism>
  forbidden_changes: []
  tests: []
  evidence:
    - Search results for each file name across all file types
    - git log output for each file
  rollback: N/A (read-only characterization)
  acceptance_criteria:
    - Each file has a definitive classification
  stop_conditions: []
  risk: LOW
  lane: dead-code verification
  human_approval: false
  parallel_safe: true
```

---

## Stage 2 — Low-Risk Cleanup

### TC-S2-001: Quarantine Evidence Sprint Writers run046-049 (SAFEST FIRST PILOT)

```yaml
taskcard:
  task_id: TC-S2-001
  objective: Move run046-049 sprint writers to a quarantine directory, confirming no external consumers
  affected_paths:
    - tools/evidence/run046_sprint_writer.py
    - tools/evidence/run047_sprint_writer.py
    - tools/evidence/run048_sprint_writer.py
    - tools/evidence/run049_sprint_writer.py
  problem_ids: [P-002]
  dependencies: [TC-S0-001]
  guarantees_preserved: [G-001, G-006]
  implementation_outline:
    - Final verification: grep all tracked files for "run046", "run047", "run048", "run049"
    - Create tools/evidence/_quarantine/ directory
    - Move 4 files to quarantine with a README explaining why
    - Run full test suite to verify no breakage
    - If tests pass, commit with message "quarantine: move superseded sprint writers run046-049"
  forbidden_changes:
    - Do not delete files (quarantine only)
    - Do not modify run050_sprint_writer.py
  tests:
    - Full pytest suite must pass identically to baseline
    - grep verification: no remaining references to quarantined files
  evidence:
    - grep search results (empty = no references)
    - Test results before/after
  rollback: git revert (moves files back)
  acceptance_criteria:
    - 4 files moved to _quarantine/
    - Test suite passes identically to baseline
    - 11,424 LOC quarantined
  stop_conditions:
    - Any test references the quarantined files
    - Any config file references the quarantined files
  risk: LOW
  lane: dead-code verification
  human_approval: false
  parallel_safe: true
```

### TC-S2-002: Quarantine Iterative Proof Graph Builders

```yaml
taskcard:
  task_id: TC-S2-002
  objective: Move build_proof_graph_iter001-003.py to quarantine
  affected_paths:
    - tools/supervisor/build_proof_graph_iter001.py
    - tools/supervisor/build_proof_graph_iter002.py
    - tools/supervisor/build_proof_graph_iter003.py
  problem_ids: [P-010]
  dependencies: [TC-S0-001]
  guarantees_preserved: []
  implementation_outline:
    - Verify zero references across all file types
    - Move to tools/supervisor/_quarantine/
    - Run test suite
  forbidden_changes: [Do not delete; quarantine only]
  tests: [Full test suite comparison]
  evidence: [grep results, test results]
  rollback: git revert
  acceptance_criteria: [510 LOC quarantined, tests pass]
  stop_conditions: [Any reference found]
  risk: LOW
  lane: dead-code verification
  human_approval: false
  parallel_safe: true
```

### TC-S2-003: Quarantine Migration Script

```yaml
taskcard:
  task_id: TC-S2-003
  objective: Move migrate_command_sections.py to quarantine
  affected_paths: [tools/supervisor/migrate_command_sections.py]
  problem_ids: [P-011]
  dependencies: [TC-S0-001]
  guarantees_preserved: []
  implementation_outline:
    - Verify zero references
    - Move to quarantine
    - Run test suite
  forbidden_changes: [Do not delete; quarantine only]
  tests: [Full test suite]
  evidence: [grep results, test results]
  rollback: git revert
  acceptance_criteria: [742 LOC quarantined, tests pass]
  stop_conditions: [Any reference found]
  risk: LOW
  lane: dead-code verification
  human_approval: false
  parallel_safe: true
```

---

## Stage 3 — Consolidation Pilots

### TC-S3-001: Consolidate Orchestration After Characterization

```yaml
taskcard:
  task_id: TC-S3-001
  objective: Based on TC-S1-001 results, quarantine confirmed-unreachable autonomous_* files
  affected_paths: [Depends on TC-S1-001 results]
  problem_ids: [P-003]
  dependencies: [TC-S1-001]
  guarantees_preserved: [G-001, G-007, G-009]
  implementation_outline:
    - Review call trace evidence from TC-S1-001
    - For each NOT_INVOKED file: quarantine
    - For each INVOKED file: document invocation mechanism
    - Run test suite
  forbidden_changes:
    - Do not quarantine INVOKED files
    - Do not modify autonomous_cycle.py
  tests: [Full test suite comparison]
  evidence: [Call trace analysis, test results]
  rollback: git revert
  acceptance_criteria:
    - Every quarantined file has NOT_INVOKED evidence
    - Test suite passes
  stop_conditions:
    - TC-S1-001 incomplete
    - Ambiguous invocation evidence
  risk: MEDIUM
  lane: duplication and migration
  human_approval: false
  parallel_safe: false
```

### TC-S3-002: Consolidate AI Integration After Characterization

```yaml
taskcard:
  task_id: TC-S3-002
  objective: Based on TC-S1-002 results, quarantine confirmed-dead ai_* files
  affected_paths: [Depends on TC-S1-002 results]
  problem_ids: [P-005]
  dependencies: [TC-S1-002]
  guarantees_preserved: []
  implementation_outline:
    - Review characterization evidence
    - Quarantine CONFIRMED_DEAD files
    - Retain INVOKED files with documentation
  forbidden_changes: [Do not quarantine invoked files]
  tests: [Full test suite]
  evidence: [Characterization report, test results]
  rollback: git revert
  acceptance_criteria: [Each quarantined file has dead-code proof]
  stop_conditions: [Ambiguous classification]
  risk: LOW
  lane: dead-code verification
  human_approval: false
  parallel_safe: true
```

---

## Stage 4 — State/Lifecycle Unification (Only If Fragmentation Proven)

### TC-S4-001: Document State Authority Model

```yaml
taskcard:
  task_id: TC-S4-001
  objective: Create a definitive state authority document mapping every persistent state file to its owning component
  affected_paths:
    - .local/supervisor/ (all state files)
    - .supervisor/ (configuration files)
    - reports/supervisor/ (output files)
  problem_ids: [P-009]
  dependencies: [TC-S0-001]
  guarantees_preserved: [G-003, G-007, G-008]
  implementation_outline:
    - Inventory all state files in .local/supervisor/
    - For each file: identify which component writes it, which reads it, and the authoritative schema
    - Document in docs/automation/state-authority-model.md
    - Identify duplicate storage of same fact
  forbidden_changes: [No state file modifications]
  tests: []
  evidence: [State authority document]
  rollback: N/A (documentation only)
  acceptance_criteria: [Every state file has identified owner]
  stop_conditions: []
  risk: LOW
  lane: state and lifecycle
  human_approval: false
  parallel_safe: true
```

---

## Stage 5 — Architectural Consolidation (Only After Pilots)

### TC-S5-001: Restructure Governance Validators by Domain

```yaml
taskcard:
  task_id: TC-S5-001
  objective: Reorganize 18 governance validator files into domain-based modules
  affected_paths: [tools/supervisor/governance_validators*.py, tests/supervisor/test_governance_validators.py]
  problem_ids: [P-004]
  dependencies: [TC-S0-001, TC-S3-001]
  guarantees_preserved: [G-002, G-005, G-006, G-012]
  implementation_outline:
    - Map each of 153 validators to a concern domain (structural, import, naming, evidence, dotnet, spec, etc.)
    - Create new domain-based files (e.g., validators_structural.py, validators_import.py)
    - Migrate validators maintaining function signatures
    - Update governance_validator_runner.py discovery pattern
    - Run dual execution: old files + new files, compare results
    - Update test_governance_validators.py
    - Remove old ext files after parity proven
  forbidden_changes:
    - Do not change validator logic
    - Do not change function signatures
    - Do not remove validators
  tests:
    - Dual execution comparison: all 153 validators produce identical results
    - test_governance_validators.py passes with new structure
  evidence:
    - Dual execution comparison report
    - Before/after test results
  rollback: git revert to pre-restructure commit
  acceptance_criteria:
    - All 153 validators present in new structure
    - Dual execution shows 100% parity
    - Test suite passes
  stop_conditions:
    - Any validator produces different result in new structure
    - Dual execution cannot be automated
  risk: HIGH
  lane: validation and evidence
  human_approval: true (external review recommended before merge)
  parallel_safe: false
```

---

## Stage 6 — Retirement

### TC-S6-001: Remove Legacy Commands from supervisor_loop.py

```yaml
taskcard:
  task_id: TC-S6-001
  objective: Remove the 6 legacy commands (discover, review, next, run-on-latest, export-taskmaster, export-ruflo) from supervisor_loop.py
  affected_paths: [tools/supervisor/supervisor_loop.py]
  problem_ids: [P-003]
  dependencies: [TC-S3-001]
  guarantees_preserved: [G-001]
  implementation_outline:
    - Verify no caller uses legacy commands (grep all files)
    - Remove legacy command handlers
    - Update help text
    - Run test suite
  forbidden_changes: [Do not remove canonical commands]
  tests: [Full test suite; supervisor_loop.py --help shows only canonical commands]
  evidence: [grep results, test results]
  rollback: git revert
  acceptance_criteria: [Legacy commands removed, tests pass]
  stop_conditions: [Any reference to legacy commands found]
  risk: LOW
  lane: duplication and migration
  human_approval: false
  parallel_safe: true
```

### TC-S6-002: Delete Quarantined Files After Observation Period

```yaml
taskcard:
  task_id: TC-S6-002
  objective: After 30 days in quarantine with no reported breakage, permanently delete quarantined files
  affected_paths: [tools/evidence/_quarantine/, tools/supervisor/_quarantine/]
  problem_ids: [P-002, P-005, P-010, P-011]
  dependencies: [TC-S2-001, TC-S2-002, TC-S2-003, TC-S3-001, TC-S3-002]
  guarantees_preserved: []
  implementation_outline:
    - Verify quarantine period (30 days minimum)
    - Verify no bug reports referencing quarantined files
    - Delete quarantine directories
    - Update file counts in evidence/metrics.json
  forbidden_changes: [Do not delete non-quarantined files]
  tests: [Full test suite]
  evidence: [Quarantine period verification, bug report absence]
  rollback: git reflog to recover deleted files
  acceptance_criteria: [All quarantined files deleted, tests pass]
  stop_conditions: [Any bug report references quarantined code]
  risk: LOW (after observation period)
  lane: dead-code verification
  human_approval: true (confirm observation period passed)
  parallel_safe: true
```

---

## Stage 7 — Regrowth Prevention

### TC-S7-001: Add Duplicate Detection to CI

```yaml
taskcard:
  task_id: TC-S7-001
  objective: Add CI check that flags new files with names matching existing patterns (autonomous_*, governance_validators_ext*, run0*_sprint_writer)
  affected_paths: [.github/workflows/ci.yml]
  problem_ids: [P-003, P-004]
  dependencies: []
  guarantees_preserved: []
  implementation_outline:
    - Add a CI step that counts files matching growth patterns
    - Fail if count exceeds baseline
    - Document allowed growth via explicit budget files
  forbidden_changes: [Do not change existing file structure]
  tests: [CI passes with current file count]
  evidence: [CI configuration]
  rollback: Remove CI step
  acceptance_criteria: [CI catches new autonomous_* files]
  stop_conditions: []
  risk: LOW
  lane: adversarial verification
  human_approval: false
  parallel_safe: true
```

---

## Dependency Graph

```
TC-S0-001 (baseline)
  ├── TC-S1-001 (trace ghosts) ──► TC-S3-001 (consolidate orchestration)
  ├── TC-S1-002 (trace AI) ──► TC-S3-002 (consolidate AI)
  ├── TC-S2-001 (quarantine evidence writers) ──┐
  ├── TC-S2-002 (quarantine proof graphs) ──────┤
  ├── TC-S2-003 (quarantine migration) ─────────┼──► TC-S6-002 (delete after 30d)
  └── TC-S4-001 (state authority doc)           │
                                                 │
TC-S3-001 ──► TC-S5-001 (restructure validators)
TC-S3-001 ──► TC-S6-001 (remove legacy commands)
TC-S7-001 (regrowth prevention) — no dependencies
```

## Estimated LOC Impact

| Stage | LOC Quarantined/Removed | Confidence |
|---|---|---|
| Stage 2 (cleanup) | ~12,700 | HIGH |
| Stage 3 (after characterization) | 0-7,000 | MEDIUM (depends on tracing) |
| Stage 5 (restructure) | ~0 (restructure, not remove) | N/A |
| Stage 6 (retirement) | ~12,700-20,000 (deletes quarantined) | HIGH |
| **Total potential** | **12,700-32,000** | **Range reflects investigation gaps** |

## Quality Gate Counters

```
TASKS_WITHOUT_PROBLEM_IDS = 0
TASKS_WITHOUT_ROLLBACK = 0
TASKS_WITHOUT_ACCEPTANCE_CRITERIA = 0
REMOVAL_RECOMMENDATIONS_WITHOUT_REPLACEMENT_PROOF = 0
```

# 05 - Problem Catalog

Problems are grouped by root cause, not directory. Each problem has evidence, severity, and a testable statement.

## P-001: Measurement Error in Original Assessment

| Field | Value |
|---|---|
| problem_id | P-001 |
| title | Original 81K:72K comparison understates machinery by 52% |
| category | measurement_error |
| affected_paths | tools/ (all), .supervisor/, .claude/commands/, registry/, schemas/ |
| evidence | tools/supervisor/ = 85,469 LOC; total tools/ = 174,068 LOC; config infrastructure = 76,479 LOC |
| root_cause | Original measurement used `tools/supervisor/*.py` (non-recursive, top-level only) as "machinery" and excluded 88K of non-supervisor tooling plus 76K of configuration |
| impact | Decision-makers using 1.13:1 ratio get a fundamentally different picture than the actual 2.4:1-3.5:1 ratio |
| severity | HIGH |
| confidence | VERIFIED_FACT — reproducible with stated commands |
| strategy | Correct the measurement; establish canonical LOC dashboard |
| proof_required | Run stated commands at same commit; verify identical counts |

## P-002: Evidence Sprint Writer Versioned Snapshots (15.5K LOC)

| Field | Value |
|---|---|
| problem_id | P-002 |
| title | 5 versioned evidence sprint writers (run046-050) with no external consumers |
| category | duplication |
| affected_paths | tools/evidence/run046_sprint_writer.py through run050_sprint_writer.py |
| evidence | `grep -rl "run046\|run047\|run048\|run049\|run050"` finds only self-references and historical contract YAML files; function signatures diverged between run046 and run050; total 15,540 LOC |
| root_cause | Each sprint iteration created a new versioned sprint writer rather than evolving a single file. Old versions were never removed |
| impact | 11,424 LOC (run046-049) is dead weight with no consumers |
| severity | MEDIUM |
| confidence | VERIFIED_FACT — zero imports confirmed |
| strategy | Quarantine run046-049; retain run050 as the active version |
| proof_required | Verify no subprocess/CLI invocation references run046-049 by name |

## P-003: Autonomous Orchestration Fragmentation (10K LOC, 10 files)

| Field | Value |
|---|---|
| problem_id | P-003 |
| title | 10 files with "autonomous_" prefix implement overlapping orchestration concerns |
| category | duplication + incomplete_migration |
| affected_paths | tools/supervisor/autonomous_*.py (10 files) |
| evidence | Only autonomous_cycle.py is imported by other files. autonomous_loop_runner.py (922 LOC), autonomous_orchestrator.py (663 LOC), autonomous_poc_controller.py (840 LOC), autonomous_train_executor.py (698 LOC), autonomous_host_daemon.py (113 LOC), autonomous_host_runner.py (651 LOC) have ZERO imports from any tracked Python file |
| root_cause | Evolutionary exploration of orchestration approaches; each new approach was added alongside predecessors rather than replacing them |
| impact | 6,464 LOC across 7 files with zero imports. Cognitive overhead from multiple "autonomous" entry points |
| severity | HIGH |
| confidence | STRONG_INFERENCE — zero Python imports confirmed; may have subprocess/CLI invocations not detected by grep |
| strategy | Investigate which are invoked via subprocess/CLI/skill-registry; quarantine confirmed unreachable files |
| proof_required | Search .claude/commands/, .supervisor/skill-registry.yaml, CLAUDE.md, AGENTS.md for references to each file |

## P-004: Governance Validator Accretive Growth (10.9K LOC, 18 files)

| Field | Value |
|---|---|
| problem_id | P-004 |
| title | Governance validators grew from 1 file to 18 via accretive ext/ext2/ext3/ext4 pattern |
| category | monolithic_design + over_abstraction |
| affected_paths | tools/supervisor/governance_validators*.py (18 files) |
| evidence | governance_validators.py (3,183 LOC, 53 functions) + governance_validators_ext.py (1,397 LOC) + governance_validators_ext2.py (1,074 LOC) + governance_validators_ext3.py (890 LOC) + governance_validators_ext4.py (696 LOC) + 13 specialized files |
| root_cause | Each time governance_validators.py became too large, a new ext file was added. Specialized validators (dotnet, sal, spec, layers, etc.) also split into separate files. No refactoring to group by concern |
| impact | 18 files with 153 validator functions; hard to find which validator is where; test file (3,270 LOC) must import from all 18 |
| severity | MEDIUM |
| confidence | VERIFIED_FACT — file listing and LOC confirmed |
| strategy | Consolidate by concern domain (structural, import, naming, evidence, dotnet) rather than by chronological addition |
| proof_required | Map each validator to its concern domain; verify test coverage maps correctly |

## P-005: AI Integration Files With Zero Consumers (1.4K LOC)

| Field | Value |
|---|---|
| problem_id | P-005 |
| title | 6 ai_* files in tools/supervisor/ have zero imports from any other file |
| category | dead_code |
| affected_paths | ai_evidence_critic.py (186), ai_implementation_designer.py (220), ai_learning_loop.py (198), ai_product_brain.py (282), ai_sprint_manager.py (248), ai_supervisor_advisor.py (233) |
| evidence | Zero-import analysis confirmed; no references in .claude/commands/ or skill-registry.yaml by initial scan |
| root_cause | AI integration modules written as exploratory prototypes; never wired into production pipeline |
| impact | 1,367 LOC of unreachable code |
| severity | LOW |
| confidence | STRONG_INFERENCE — need to verify no dynamic loading via importlib or config |
| strategy | Verify no dynamic invocation; quarantine if confirmed dead |
| proof_required | Search for string-based references to these module names in YAML, JSON, MD files |

## P-006: Report Directory Unbounded Growth (402 MB)

| Field | Value |
|---|---|
| problem_id | P-006 |
| title | reports/ directory is 402 MB with no automated archival or rotation |
| category | state_inflation |
| affected_paths | reports/ (300+ directories, 7,201 files including plans/) |
| evidence | `du -sh reports/` = 402M; contains sprint reports r23-r133, skills-r*, mainstream-*, acceleration-* series |
| root_cause | Every sprint generates report files that are committed to the repository; no archival policy exists |
| impact | Repository clone time increases; git operations slow; disk usage grows linearly with sprints |
| severity | MEDIUM |
| confidence | VERIFIED_FACT |
| strategy | Implement report rotation: archive reports older than N sprints to a compressed archive or separate branch |
| proof_required | Measure git clone time with and without reports/ |

## P-007: Capability Map JSON Files (4.2M lines)

| Field | Value |
|---|---|
| problem_id | P-007 |
| title | Committed capability map JSON files total ~4.2 million lines |
| category | generated_code_handling |
| affected_paths | reports/capability-layer/unified-capability-map.json (2.5M lines), reports/capability-layer/foss-capability-map.json (1.7M), gap-ledger.json (1.1M) |
| evidence | File sizes from prior recon; these are generated outputs from capability_map_generator.py |
| root_cause | Generated capability maps are committed to the repository rather than being built on demand |
| impact | Massive repository size; merge conflicts on regeneration; review burden |
| severity | HIGH |
| confidence | VERIFIED_FACT |
| strategy | Move to gitignored build output; regenerate on demand from source authority |
| proof_required | Verify capability maps can be regenerated deterministically from inputs |

## P-008: Validate-* Family Overlap With Governance Validators (5.1K LOC)

| Field | Value |
|---|---|
| problem_id | P-008 |
| title | 17 validate_*.py files (5,122 LOC) exist separately from the 18 governance_validators*.py files (10,908 LOC) |
| category | validation_overlap |
| affected_paths | tools/supervisor/validate_*.py (17 files) |
| evidence | validate_adoption_compliance.py, validate_claude_commands.py, validate_closeout_gate.py, etc. — these are standalone CLI validators, separate from the governance_validators family which is loaded by governance_validator_runner.py |
| root_cause | Two parallel validation systems: governance_validators (loaded by runner, called in autonomous_cycle) and validate_* (standalone CLI scripts invoked ad-hoc or by skills) |
| impact | Confusing which validation system to use; potential for checks to be in one system but not the other |
| severity | LOW |
| confidence | STRONG_INFERENCE — different invocation patterns confirmed |
| strategy | Document the distinction; consider unifying invocation under validator runner |
| proof_required | Map which validate_* scripts duplicate governance_validator checks |

## P-009: .supervisor/ Configuration Sprawl (39K LOC, 183 files)

| Field | Value |
|---|---|
| problem_id | P-009 |
| title | .supervisor/ directory contains 183 files totaling 39,351 LOC of configuration, schemas, prompts, and state |
| category | configuration_sprawl |
| affected_paths | .supervisor/ |
| evidence | 183 files measured; includes skill-registry.yaml, 21 JSON schemas, decision prompts, knowledge base, contracts |
| root_cause | Progressive accumulation of configuration; no consolidation or rotation |
| impact | Hard to find canonical configuration; potential for stale or contradictory entries |
| severity | LOW |
| confidence | VERIFIED_FACT |
| strategy | Audit for stale entries; consolidate related schemas; document canonical locations |
| proof_required | Identify which .supervisor/ files are actually read by production code |

## P-010: Iterative Proof Graph Builders (510 LOC)

| Field | Value |
|---|---|
| problem_id | P-010 |
| title | Three iterative proof graph builders (iter001-003) with zero consumers |
| category | dead_code |
| affected_paths | build_proof_graph_iter001.py (199), build_proof_graph_iter002.py (184), build_proof_graph_iter003.py (127) |
| evidence | Zero imports confirmed; iterative naming suggests successive attempts |
| root_cause | Iterative prototyping without cleanup |
| impact | 510 LOC of dead code |
| severity | INFORMATIONAL |
| confidence | VERIFIED_FACT |
| strategy | Quarantine after confirming no CLI invocation |

## P-011: Command Section Migration Script Still Present (742 LOC)

| Field | Value |
|---|---|
| problem_id | P-011 |
| title | migrate_command_sections.py is a one-time migration script still in the codebase |
| category | incomplete_migration |
| affected_paths | tools/supervisor/migrate_command_sections.py (742 LOC) |
| evidence | Zero imports; name implies one-time migration; 742 LOC |
| root_cause | Migration completed but script not removed |
| impact | 742 LOC of dead weight |
| severity | INFORMATIONAL |
| confidence | STRONG_INFERENCE |
| strategy | Quarantine after confirming migration is complete |

## P-012: Tests Exceed Production Code by 1.6x (396K vs 246K)

| Field | Value |
|---|---|
| problem_id | P-012 |
| title | Test suite at 396K LOC is 1.6x all production code combined |
| category | test_evidence_inflation |
| affected_paths | tests/ (3,095 files, 396,192 LOC) |
| evidence | tests/python/ alone is 241K LOC for 49K of product code (4.9:1 ratio). Many test files in tests/python/deepening/ have systematic naming patterns suggesting generation |
| root_cause | Each sprint generates test files; some tests are generated rather than hand-written; no test rotation or consolidation |
| impact | Test suite run time; cognitive overhead; difficulty finding relevant tests |
| severity | LOW |
| confidence | STRONG_INFERENCE — high ratio confirmed; generation pattern needs verification |
| strategy | Identify generated vs hand-written tests; consider test consolidation |

## Summary by Category

| Category | Problems | Combined LOC Impact |
|---|---|---|
| measurement_error | P-001 | N/A (reporting issue) |
| duplication | P-002, P-003 | ~22,000 |
| dead_code | P-005, P-010, P-011 | ~2,600 |
| monolithic_design | P-004 | ~10,900 (restructure, not remove) |
| state_inflation | P-006 | 402 MB |
| generated_code_handling | P-007 | ~4.2M lines |
| validation_overlap | P-008 | ~5,100 (clarify, not remove) |
| configuration_sprawl | P-009 | ~39,000 (audit, not remove) |
| test_evidence_inflation | P-012 | ~396,000 |

## Quality Gate Counters

```
MATERIAL_FINDINGS_WITHOUT_EVIDENCE = 0
MATERIAL_FINDINGS_WITHOUT_ROOT_CAUSE = 0
```

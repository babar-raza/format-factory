# 04 - Machinery Component Register

## Classification Key

| Classification | Meaning |
|---|---|
| `ESSENTIAL_SAFETY_CRITICAL` | Required for correctness; removal breaks guarantees |
| `ESSENTIAL_OVERCOMPLICATED` | Required but could be simpler |
| `USEFUL_SHARED_INFRASTRUCTURE` | Valuable utility; not safety-critical |
| `SUSPECTED_GHOST` | Zero imports from other files; may be unreachable |
| `DEPRECATED_STILL_ACTIVE` | Old version still present; superseded by newer |
| `EXPERIMENTAL` | Prototype or experimental feature |
| `UNKNOWN_REQUIRES_RUNTIME_EVIDENCE` | Cannot determine statically |

## Disposition Key

| Disposition | Meaning |
|---|---|
| `RETAIN` | Keep as-is |
| `CONSOLIDATE` | Merge with related component |
| `INVESTIGATE` | Needs runtime evidence before disposition |
| `QUARANTINE` | Isolate for removal after proof of non-use |
| `DOCUMENT` | Keep but add documentation |
| `CHARACTERIZE` | Need deeper analysis |

## Summary Statistics

| Classification | Components | Total LOC |
|---|---|---|
| ESSENTIAL_SAFETY_CRITICAL | 13 | ~22,000 |
| ESSENTIAL_OVERCOMPLICATED | 3 | ~5,800 |
| USEFUL_SHARED_INFRASTRUCTURE | 19 | ~42,000 |
| SUSPECTED_GHOST | 9 | ~8,200 |
| DEPRECATED_STILL_ACTIVE | 3 | ~12,700 |
| EXPERIMENTAL | 1 | ~1,800 |

**Important caveat**: "SUSPECTED_GHOST" files may be CLI entry points invoked via subprocess, .claude/commands/, or the skill registry. 142 files in tools/supervisor/ have `if __name__ == '__main__'` guards. The "zero imports" test catches only Python `import` statements, not subprocess invocations, YAML skill definitions, or CLAUDE.md references.

## Component Groups

### A. Orchestration (15 components, ~13,400 LOC)

The orchestration layer has **fragmentation**: 10 files with "autonomous_" prefix implement overlapping concerns. Only `autonomous_cycle.py` is imported by `supervisor_loop.py`. The others appear to be alternative entry points or evolutionary predecessors.

| Component ID | File(s) | LOC | Classification | Disposition |
|---|---|---|---|---|
| COMP-ORCH-001 | autonomous_cycle.py | 2,651 | ESSENTIAL_SAFETY_CRITICAL | RETAIN |
| COMP-ORCH-002 | check_continuation.py | 796 | ESSENTIAL_SAFETY_CRITICAL | RETAIN |
| COMP-ORCH-003 | supervisor_loop.py | 605 | ESSENTIAL_OVERCOMPLICATED | CONSOLIDATE |
| COMP-ORCH-004 | sprint_executor.py | 628 | USEFUL_SHARED_INFRASTRUCTURE | RETAIN |
| COMP-ORCH-005 | autonomous_loop_runner.py | 922 | SUSPECTED_GHOST | INVESTIGATE |
| COMP-ORCH-006 | external_host_loop.py | 674 | SUSPECTED_GHOST | INVESTIGATE |
| COMP-ORCH-007 | autonomous_host_daemon/runner.py | 764 | SUSPECTED_GHOST | INVESTIGATE |
| COMP-ORCH-008 | autonomous_orchestrator.py | 663 | SUSPECTED_GHOST | INVESTIGATE |
| COMP-ORCH-009 | autonomous_poc_controller.py | 840 | SUSPECTED_GHOST | INVESTIGATE |
| COMP-ORCH-010 | autonomous_train_executor.py | 698 | SUSPECTED_GHOST | INVESTIGATE |
| COMP-ORCH-011 | autonomous_task_generator.py | 1,920 | SUSPECTED_GHOST | INVESTIGATE |
| COMP-ORCH-012 | autonomous_cycle_extensions + utils | 1,808 | ESSENTIAL_OVERCOMPLICATED | CONSOLIDATE |
| COMP-ORCH-013 | tri_lane_integration.py | 973 | USEFUL_SHARED_INFRASTRUCTURE | RETAIN |
| COMP-ORCH-014 | stop_reason_adjudicator.py | 1,025 | USEFUL_SHARED_INFRASTRUCTURE | RETAIN |
| COMP-ORCH-015 | rework_orchestrator.py | 683 | USEFUL_SHARED_INFRASTRUCTURE | RETAIN |

### B. Governance & Validation (35 files, 16,030 LOC)

| Component ID | File(s) | LOC | Classification | Disposition |
|---|---|---|---|---|
| COMP-GOV-001 | governance_validators.py | 3,183 | ESSENTIAL_SAFETY_CRITICAL | RETAIN |
| COMP-GOV-002 | governance_validators_ext*.py (4) | 4,057 | ESSENTIAL_OVERCOMPLICATED | CONSOLIDATE |
| COMP-GOV-003 | governance_validators_dotnet*.py (2) | 924 | USEFUL_SHARED_INFRASTRUCTURE | RETAIN |
| COMP-GOV-004 | governance_validators_{other}.py (11) | 2,744 | USEFUL_SHARED_INFRASTRUCTURE | DOCUMENT |
| COMP-GOV-005 | governance_validator_runner.py | 687 | ESSENTIAL_SAFETY_CRITICAL | RETAIN |
| COMP-GOV-006 | anti_skip_checker.py | 1,351 | ESSENTIAL_SAFETY_CRITICAL | RETAIN |
| COMP-GOV-007 | validate_*.py (17 files) | 5,122 | USEFUL_SHARED_INFRASTRUCTURE | DOCUMENT |

### C. Evidence Pipeline (~12K LOC in supervisor + 21K in tools/evidence/)

| Component ID | File(s) | LOC | Classification | Disposition |
|---|---|---|---|---|
| COMP-EVI-001 | grade_declared_work.py | 1,127 | ESSENTIAL_SAFETY_CRITICAL | RETAIN |
| COMP-EVI-002 | evidence_declaration.py | 219 | ESSENTIAL_SAFETY_CRITICAL | RETAIN |
| COMP-EVI-003 | inspect_declared_evidence.py | 542 | ESSENTIAL_SAFETY_CRITICAL | RETAIN |
| COMP-EVI-004 | sprint_executor_validate.py | 828 | ESSENTIAL_SAFETY_CRITICAL | RETAIN |
| COMP-EVI-005 | run050_sprint_writer.py | 4,116 | USEFUL_SHARED_INFRASTRUCTURE | RETAIN |
| COMP-EVI-006 | run046-049_sprint_writer.py (4) | 11,424 | DEPRECATED_STILL_ACTIVE | QUARANTINE |
| COMP-EVI-007 | validate_evidence_bundle.py | 2,638 | USEFUL_SHARED_INFRASTRUCTURE | RETAIN |
| COMP-EVI-008 | build_declaration_review_package.py | 407 | USEFUL_SHARED_INFRASTRUCTURE | RETAIN |

### D. Prompt Generation (~8K LOC)

| Component ID | File(s) | LOC | Classification | Disposition |
|---|---|---|---|---|
| COMP-PROMPT-001 | generate_next_worker_prompt.py | 1,546 | ESSENTIAL_SAFETY_CRITICAL | RETAIN |
| COMP-PROMPT-002 | generate_supervisor_packet.py | 1,437 | USEFUL_SHARED_INFRASTRUCTURE | RETAIN |
| COMP-PROMPT-003 | generate_mainstream_execution_packet.py | 486 | SUSPECTED_GHOST | INVESTIGATE |

### E. State Management (~3K LOC)

| Component ID | File(s) | LOC | Classification | Disposition |
|---|---|---|---|---|
| COMP-STATE-001 | write_plan_lock.py | 691 | ESSENTIAL_SAFETY_CRITICAL | RETAIN |
| COMP-STATE-002 | continuation_*.py (5) | 969 | ESSENTIAL_SAFETY_CRITICAL | RETAIN |
| COMP-STATE-003 | action_queue.py | 340 | USEFUL_SHARED_INFRASTRUCTURE | RETAIN |

### F. AI Integration (~6K LOC)

| Component ID | File(s) | LOC | Classification | Disposition |
|---|---|---|---|---|
| COMP-AI-001 | ai_*.py (6 files in supervisor) | 1,367 | SUSPECTED_GHOST | INVESTIGATE |
| COMP-AI-002 | embedding_retrieval.py | 838 | USEFUL_SHARED_INFRASTRUCTURE | RETAIN |
| COMP-AI-003 | tools/ai/ (43 files) | 4,327 | USEFUL_SHARED_INFRASTRUCTURE | CHARACTERIZE |

### G. Specification & Oracle (~14K LOC)

| Component ID | File(s) | LOC | Classification | Disposition |
|---|---|---|---|---|
| COMP-SPEC-001 | tools/specification-authority-layer/ | 5,874 | ESSENTIAL_SAFETY_CRITICAL | RETAIN |
| COMP-SPEC-002 | tools/spec-normalize/ | 4,286 | USEFUL_SHARED_INFRASTRUCTURE | RETAIN |
| COMP-SPEC-003 | tools/oracle/ | 3,728 | ESSENTIAL_SAFETY_CRITICAL | RETAIN |

### H. Deprecated / Legacy (~13K LOC)

| Component ID | File(s) | LOC | Classification | Disposition |
|---|---|---|---|---|
| COMP-LEGACY-001 | libforge_*.py (4 files) | 1,764 | EXPERIMENTAL | INVESTIGATE |
| COMP-LEGACY-002 | migrate_command_sections.py | 742 | DEPRECATED_STILL_ACTIVE | QUARANTINE |
| COMP-LEGACY-003 | build_proof_graph_iter001-003.py | 510 | DEPRECATED_STILL_ACTIVE | QUARANTINE |

## LOC by Disposition

| Disposition | Estimated LOC | % of tools/ |
|---|---|---|
| RETAIN | ~120,000 | 69% |
| CONSOLIDATE | ~6,500 | 4% |
| INVESTIGATE | ~10,000 | 6% |
| QUARANTINE | ~12,700 | 7% |
| DOCUMENT | ~7,800 | 4% |
| CHARACTERIZE | ~4,300 | 2% |
| Other tools/ dirs | ~12,700 | 7% |

See `evidence/component-register.csv` for the full machine-readable register.

# 10 - Adversarial Review

Each assertion from Section 13 of the investigation mandate is independently challenged.

---

## A1: "Large machinery is inherently bad"

**Challenge**: The machinery-to-product ratio of 2.4:1 is presented as a concern. But factory code amortizes across formats. Is the ratio actually problematic?

**Response**: The ratio itself is not the problem. The problem is that **the same factory code appears in multiple forms** (10 autonomous_* files, 5 evidence sprint writers, 18 validator files). If the 174K of machinery were all unique, necessary functionality, the ratio would be justified. The investigation found ~13-25K of demonstrably duplicated or dead code, which is 7-14% of machinery — significant but not catastrophic.

**Verdict**: PARTIALLY_VALID. Size is a symptom; duplication and dead code are the actual problems.

---

## A2: "Low-reference code is dead"

**Challenge**: The investigation classified 9 components as SUSPECTED_GHOST based on zero Python imports. But 142 files have `if __name__ == '__main__'` guards and many are invoked via subprocess, CLI commands, or skill registry.

**Response**: This is the most serious risk in the investigation. The zero-import analysis catches only Python `import` statements. It misses:
- Subprocess invocations (56 call sites in tools/supervisor/)
- .claude/commands/ references (125 command files reference supervisor/)
- Skill registry dispatch (50 references in skill-registry.yaml)
- CLAUDE.md/AGENTS.md directive references (24 in CLAUDE.md alone)

**Verdict**: VALID. Zero-import ≠ dead. The plan correctly requires Stage 1 (observability) before Stage 2 (cleanup). No file should be quarantined without positive evidence of non-invocation across all mechanisms.

**Plan amendment**: TC-S1-001 must also search .claude/commands/, .supervisor/skill-registry.yaml, CLAUDE.md, AGENTS.md, and all subprocess.run calls for each suspected ghost file.

---

## A3: "Duplicated validation is unnecessary"

**Challenge**: The 35 validation files (18 governance_validators + 17 validate_*) are flagged as overlapping. But defense in depth is a deliberate security pattern.

**Response**: The governance_validators (18 files) and validate_* (17 files) serve different purposes:
- governance_validators are **loaded by governance_validator_runner.py** and run as a batch during autonomous_cycle closeout
- validate_* are **standalone CLI scripts** invoked ad-hoc by skills and commands

This is not duplication — it's two separate invocation patterns for different use cases. The plan correctly classifies this as P-008 with disposition DOCUMENT (not remove).

**Verdict**: VALID. The validate_* scripts are not duplicates of governance_validators. They serve different invocation patterns. Documentation, not consolidation, is correct.

---

## A4: "Shared abstractions are always better"

**Challenge**: The investigation proposes consolidating the 18 governance validator files into domain-based modules. But the current accretive pattern works — validators are discoverable, each file is reasonably sized, and the runner finds them automatically.

**Response**: The current pattern has a concrete cost: when looking for a specific validator, you must search across 18 files. The accretive ext/ext2/ext3/ext4 naming gives no semantic clue about content. However, the plan's TC-S5-001 has HIGH risk and requires dual execution verification. It should be deprioritized in favor of lower-risk consolidation.

**Verdict**: PARTIALLY_VALID. The abstraction (domain-based files) would be better, but the risk is real. TC-S5-001 should be explicitly gated on successful completion of Stages 2-3.

---

## A5: "Consolidation lowers risk"

**Challenge**: Every change to safety-critical code (autonomous_cycle, governance validators, evidence grading) introduces regression risk. Is the consolidation worth the risk?

**Response**: The plan mitigates this via:
- Stage 0 baseline before any changes
- Stage 1 observability before any removal
- Quarantine (not delete) with 30-day observation
- Dual execution for validator restructuring
- Independent rollback per taskcard

However, the opportunity cost (R-005) is real: each consolidation sprint is one fewer product sprint. The plan should explicitly cap consolidation at 5-8 sprints and defer remaining work.

**Verdict**: PARTIALLY_VALID. Consolidation lowers long-term risk but raises short-term risk. The phased approach is appropriate.

---

## A6: "One state machine is always preferable"

**Challenge**: The investigation identifies multiple orchestration loops (autonomous_cycle, autonomous_loop_runner, external_host_loop, sprint_executor). Should there be only one?

**Response**: autonomous_cycle.py is the **canonical** orchestration loop — it's the only one imported by supervisor_loop.py and referenced in CLAUDE.md. The others may serve niche purposes (headless execution, external host mode). The plan correctly requires characterization (TC-S1-001) before consolidation.

**Verdict**: VALID. Multiple loops may exist for valid reasons. Do not assume one is sufficient without evidence.

---

## A7: "Generated code should not be committed"

**Challenge**: P-007 recommends moving capability maps (4.2M lines) to gitignored build output. But committed generated code ensures reproducibility without requiring a generation step.

**Response**: The capability maps are 402 MB in the reports/ directory. This is a significant repository size burden. However, the maps are the **canonical authority** for capability status — regenerating them non-deterministically (if SAL has AI steps) would break traceability.

**Verdict**: VALID. Do not move capability maps to gitignored output until deterministic regeneration is proven. P-007's priority should be downgraded to LOW until OQ-001 (SAL reproducibility) is resolved.

**Plan amendment**: P-007 severity downgraded from HIGH to LOW pending SAL reproducibility verification.

---

## A8: "A rewrite is cleaner"

**Challenge**: Option 7 (rewrite) was rejected. But 174K of machinery with identified duplication and fragmentation — wouldn't a clean rewrite be faster?

**Response**: The current system has 12 verified guarantees, 153 governance validators, and 761 completed sprints of accumulated edge-case handling. A rewrite must re-implement every guarantee, every edge case, and every integration point. The estimated 30-50 sprint cost is likely an underestimate given the complexity of the autonomous loop, CCI isolation, plan lock lifecycle, and evidence grading pipeline.

**Verdict**: REJECTED. Evidence shows incremental repair can address the identified problems. The machinery fundamentally works — it just has accumulated dead weight.

---

## A9: "Tests capture actual behavior"

**Challenge**: The investigation relies on "test suite passes" as the acceptance criterion. But do the 39,863 tests actually capture the behavior that matters?

**Response**: Test coverage was not measured during this investigation. The 396K LOC of tests is large, but test quality (what they actually verify) was not assessed. Some tests in tests/python/deepening/ appear to be generated and may test trivial properties.

**Verdict**: VALID. The plan should add a pre-condition: verify that tests for affected components actually test the behavior that the consolidation changes.

**Plan amendment**: TC-S0-001 should include a focused test coverage analysis for the specific files being consolidated, not just a full test run.

---

## A10: "The target preserves autonomy"

**Challenge**: Will the consolidated architecture still support fully autonomous sprint execution without human intervention?

**Response**: The plan preserves all essential safety-critical components (COMP-ORCH-001/002, COMP-GOV-001/005/006, COMP-EVI-001/002/003, COMP-STATE-001/002). No autonomous loop logic is modified in Stages 2-3. The plan only removes files with ZERO consumers.

**Verdict**: VERIFIED. The plan preserves autonomous execution.

---

## A11: "The plan will not slow product progress"

**Challenge**: R-005 acknowledges that consolidation sprints displace product sprints. How many product sprints are lost?

**Response**: The plan estimates 5-8 sprints across Stages 0-3. Given the project's ~760 completed sprints, this is ~1% of historical sprint capacity. The long-term benefit (reduced cognitive load, faster onboarding, fewer false alerts from dead code) likely recovers the cost within 20-30 sprints.

**Verdict**: ACCEPTABLE. 5-8 sprints is a reasonable investment. The plan should have a hard cap of 8 sprints before returning to product work.

---

## A12: "Execution requires no undocumented knowledge"

**Challenge**: Can someone other than the investigation author execute this plan?

**Response**: The plan's taskcards include specific commands, file paths, acceptance criteria, and rollback procedures. However, the CCI-MVP session identity system, the plan lock lifecycle, and the autonomous_cycle.py internal workflow require familiarity with CLAUDE.md governance rules.

**Verdict**: PARTIALLY_VALID. The plan is executable but requires reading CLAUDE.md and AGENTS.md. Add a prerequisite reading list to TC-S0-001.

---

## Amendments from Adversarial Review

1. **TC-S1-001 scope expanded**: Must search .claude/commands/, skill-registry.yaml, CLAUDE.md, AGENTS.md, and subprocess calls — not just Python imports (from A2)
2. **P-007 severity downgraded**: HIGH → LOW pending SAL reproducibility verification (from A7)
3. **TC-S0-001 expanded**: Include focused test coverage analysis for consolidation targets (from A9)
4. **Sprint cap**: Hard cap of 8 sprints for Stages 0-3 before returning to product work (from A11)
5. **TC-S0-001 prerequisite**: Add CLAUDE.md and AGENTS.md as required reading (from A12)

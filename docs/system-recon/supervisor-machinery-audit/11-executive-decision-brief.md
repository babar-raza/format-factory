# 11 - Executive Decision Brief

## Was the 81K versus 72K assessment correct?

**PARTIALLY_ACCURATE.** The product code measurement (72K LOC) is correct (actual: 72,126). The machinery measurement (81K) correctly reflects `tools/supervisor/` (actual: 85,469) but is misleading because it represents only 49% of total machinery. The full `tools/` directory is 174,068 LOC. Including configuration infrastructure (`.supervisor/`, `.claude/commands/`, `schemas/`, `registry/`, `.governance/`), total machinery is ~250K LOC. The true machinery-to-product ratio is **2.4:1** (tools only) or **3.5:1** (tools + config), not the reported 1.13:1.

## How much machinery is justified?

**~120-150K LOC is justified.** The essential and useful components (classified RETAIN + DOCUMENT) account for approximately 120K LOC. This includes:
- Core orchestration (autonomous_cycle, check_continuation, supervisor_loop): ~4K
- Governance validators (153 validators across 18 files): ~11K
- Evidence pipeline (grading, inspection, validation, packaging): ~12K
- Prompt generation (sprint prompts, work items, supervisor packets): ~8K
- State management (plan locks, continuation, action queue): ~3K
- Specification + oracle (SAL, QName, oracle verification): ~14K
- Skills infrastructure + certification: ~11K
- Other tools/ directories (playbook, docs, backfill, etc.): ~57K

The remaining ~25-55K LOC is configuration, generated content, or requires investigation.

## How much is generated, duplicated, obsolete, unreachable, transitional, or unresolved?

| Category | Estimated LOC | Confidence |
|---|---|---|
| **Confirmed duplicated/dead** | ~13,000 | HIGH |
| Evidence sprint writers run046-049 | 11,424 | VERIFIED — zero consumers |
| Iterative proof graph builders | 510 | VERIFIED — zero consumers |
| Migration script | 742 | STRONG_INFERENCE — one-time use |
| AI integration prototypes | 1,367 | STRONG_INFERENCE — zero imports |
| **Suspected ghost (needs tracing)** | ~8,200 | MEDIUM |
| Autonomous orchestration alternatives (7 files) | 6,464 | NEEDS_RUNTIME_EVIDENCE |
| Generate mainstream execution packet | 486 | NEEDS_RUNTIME_EVIDENCE |
| Other suspected ghosts | ~1,250 | NEEDS_RUNTIME_EVIDENCE |
| **Generated/committed output** | ~4.2M lines | VERIFIED — capability maps |
| **Configuration infrastructure** | ~76,000 | VERIFIED — justified but needs audit |
| **Unresolved** | ~7,000 | Various |

## What are the five most serious structural problems?

1. **P-001: Measurement error** (HIGH) — The 1.13:1 ratio framing is misleading; actual ratio is 2.4-3.5:1. Decisions based on the wrong ratio may underestimate maintenance burden.

2. **P-003: Orchestration fragmentation** (HIGH) — 10 autonomous_* files (10K LOC) implement overlapping concerns. Only 1 is imported by other code. The rest are suspected ghosts but require runtime tracing to confirm.

3. **P-007: Capability map bloat** (HIGH, downgraded to LOW after adversarial review) — 4.2M lines of generated JSON committed to repository. However, cannot move to gitignored until deterministic regeneration is proven.

4. **P-004: Validator accretive growth** (MEDIUM) — 18 files with 153 validators using an ext/ext2/ext3/ext4 naming pattern that gives no semantic clue about content. Functional but hard to navigate.

5. **P-002: Evidence sprint writer snapshots** (MEDIUM) — 15.5K LOC across 5 versioned files; only the latest is active. 11.4K LOC is confirmed dead weight.

## What must not be changed?

The following components are **ESSENTIAL_SAFETY_CRITICAL** and must not be modified without dual-execution verification:

- `autonomous_cycle.py` — canonical orchestration loop
- `check_continuation.py` — continuation checker with CCI guards
- `governance_validators.py` + `governance_validator_runner.py` — core validation
- `anti_skip_checker.py` — evidence completeness enforcement
- `grade_declared_work.py` — evidence grading
- `evidence_declaration.py` + `inspect_declared_evidence.py` — declaration pipeline
- `sprint_executor_validate.py` — declaration auto-repair
- `write_plan_lock.py` — plan lock lifecycle
- `continuation_*.py` (5 files) — continuation state
- `generate_next_worker_prompt.py` — sprint prompt generation
- SAL pipeline (`tools/specification-authority-layer/`)
- Oracle framework (`tools/oracle/`)

## What is the safest first pilot?

**TC-S2-001: Quarantine evidence sprint writers run046-049.**

- **LOC saved**: 11,424
- **Risk**: Near-zero — files have ZERO consumers confirmed by grep
- **Rollback**: git revert
- **Time**: 1 sprint
- **Evidence**: Function signatures diverged between versions; no external imports; files only reference themselves and historical contract YAML
- **Outcome**: Establishes quarantine workflow for future cleanup

## What evidence is missing?

1. **Runtime call tracing** — SUSPECTED_GHOST files need actual invocation evidence, not just import analysis
2. **Test coverage for consolidation targets** — Which tests actually verify the behavior of files being consolidated?
3. **SAL deterministic reproducibility** — Can capability maps be regenerated identically? (Affects P-007 severity)
4. **Full test suite execution** — Only 2,887/39,863 tests were run during prior recon
5. **.NET compilation** — .NET source was inspected but not compiled
6. **Historical invocation frequency** — git log analysis of when suspected ghosts were last modified/invoked

## Is rationalization advisable now?

**YES, but scoped.** The safest consolidation (Stage 2: evidence writers, proof graphs, migration script) removes ~13K LOC with near-zero risk and can be completed in 2 sprints. Deeper consolidation (Stage 3+) should wait for Stage 1 observability results.

**Do not:**
- Attempt a rewrite (current architecture works)
- Restructure governance validators before establishing the quarantine workflow
- Move capability maps to gitignored before proving deterministic regeneration
- Spend more than 8 sprints on consolidation before returning to product work

## What requires external review before execution?

1. **TC-S5-001 (Validator restructuring)**: HIGH risk, affects 153 governance validators — requires human review before merge
2. **TC-S6-002 (Delete quarantined files)**: Requires confirmation that 30-day observation period passed with no breakage
3. **This investigation itself**: The adversarial review (Section 10) identified 5 plan amendments that should be incorporated before execution begins

---

## Final Verdict

### `INVESTIGATION_COMPLETE_WITH_DOCUMENTED_LIMITATIONS`

**Documented limitations:**
1. Static analysis only — no runtime call tracing performed
2. Zero-import analysis may miss subprocess/CLI/skill-registry invocations
3. Full test suite not executed (7.2% of tests run in prior recon)
4. .NET compilation not performed
5. Test coverage for consolidation targets not measured
6. SAL reproducibility not verified

These limitations are documented in the plan as prerequisites for execution (Stage 1 observability). No execution should proceed without addressing limitations 1-2.

---

## Corrected Measurements

| Metric | Original Claim | Actual Value | Status |
|---|---|---|---|
| Machinery LOC | 81K | 85.5K (supervisor) / 174K (all tools) | PARTIALLY_ACCURATE |
| Product LOC | 72K | 72.1K | ACCURATE |
| Machinery:Product ratio | 1.13:1 | 2.41:1 (tools) / 3.47:1 (tools+config) | MISLEADING |
| Governance validators | 101-127 | 153 across 18 files | UNDERSTATED |
| Tests | 39,863 collected | 396K LOC across 3,095 files | ACCURATE (count) |

## Investigation Files

All files at `docs/system-recon/supervisor-machinery-audit/`:

| File | Content |
|---|---|
| 00-investigation-scope-and-baseline.md | Methodology, commit, scope |
| 01-loc-and-classification-report.md | Reproducible LOC with assessment verdict |
| 02-current-machinery-architecture.md | Architecture mapping with Mermaid diagrams |
| 03-workflow-traces.md | 9 representative workflow traces |
| 04-machinery-component-register.md | Component classification and dispositions |
| 05-problem-catalog.md | 12 problems grouped by root cause |
| 06-guarantee-control-matrix.md | 12 guarantees with control mappings |
| 07-risk-register.md | 7 risks with mitigations |
| 08-target-architecture-options.md | 7 architecture strategies compared |
| 09-hardened-execution-plan.md | 12 taskcards across 7 stages |
| 10-adversarial-review.md | 12 adversarial challenges with responses |
| 11-executive-decision-brief.md | This file |
| evidence/metrics.json | Machine-readable LOC data |
| evidence/file-classification.csv | Per-file category assignment |
| evidence/component-register.csv | Component-level register |
| evidence/commands-and-results.md | Commands run during investigation |

**No production files were changed. No rationalization was executed.**

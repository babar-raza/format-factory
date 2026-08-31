# 20 — Plan Readiness Review and Final Assessment

**Baseline commit:** dd909cf3a
**Assessment date:** 2026-08-31
**Assessor:** Claude (forensic investigation, not governance expansion)

## Assessment Scope

- **Commit assessed:** dd909cf3a9586a8a6b7a32c357011cd2557e3fae (HEAD of main)
- **Environment:** Windows 11 Pro, Python 3.12.x, .venv with all packages installed
- **Product mission:** FF6-PRODUCTION-LIBRARIES-001 (6 Python format libraries to CERTIFIED)
- **Formats:** IPYNB, ORA, NRRD, XLIFF, SafeTensors, UBL
- **Evidence inspected:** 50+ source files, 15 experiments executed, 6 control systems traced
- **Commands executed:** 15 unique experiments in disposable worktree
- **Missing evidence:** ORA real-file behavior (no .ora test file available)

## Investigation Completeness

| Phase | Status | Artifacts |
|-------|--------|-----------|
| Phase 1: Product model | COMPLETE | 01, 02, 03 |
| Phase 2: Machinery inventory | COMPLETE | 04, 05 |
| Phase 3: Continuation/experiments | COMPLETE | 06, 07, 08, 09 |
| Phase 4: Proof chain traces | COMPLETE | 10, 11, 12 |
| Phase 5: Product behavior | 5/6 COMPLETE (ORA untested) | 13, 14 |
| Phase 6: Root cause analysis | COMPLETE | 15, 16, 17 |
| Target design | COMPLETE | 18 |
| Migration plan | COMPLETE | 19 |
| Baseline | COMPLETE | 00 |

## Leads Disposition

| Lead | Description | Status | Confidence |
|------|-------------|--------|-----------|
| 1 | Incompatible control systems | PROVEN — 6 systems, no conflict resolution | PROVEN |
| 2 | Non-bootstrappable continuation | PROVEN — NO_SIGNAL from clean clone | PROVEN |
| 3 | Instruction bypass of controls | PROVEN — 18 rules, 17/23 STOPs overridden | PROVEN |
| 4 | Goal driver not truth-derived | PROVEN — false certification exploit | PROVEN |
| 5 | Valid chain ≠ valid state | PROVEN — chain PASS, projection contradicts | PROVEN |
| 6 | Reconciliation accepts stale records | PROVEN — file/AST check only | PROVEN |
| 7 | Tests contradict certified state | PROVEN — IPYNB failures with CERTIFIED label | PROVEN |
| 8 | ORA namespace disagreement | PROVEN — double mismatch across ~12 files | PROVEN |
| 9 | UBL obligation drift | PROVEN — 194 vs 195 count | PROVEN |
| 10 | Fresh reconciliation differs | PARTIALLY PROVEN — CRLF differences only | INFERRED |
| 11 | Evidence-ledger not idempotent | PROVEN — SafeTensors rebuild test fails | PROVEN |
| 12 | Dry-run mutates state | PROVEN — 3KB → 48KB mutation | PROVEN |
| 13 | Task selection ignores FF6 | PROVEN — format_not_found for all 6 | PROVEN |
| 14 | Plan Control starts empty | PROVEN — 0 plans, 0 tasks, 0 events | PROVEN |
| 15 | Governance bypassed | PROVEN — blocks=True but exit 3 → continue | PROVEN |

**14/15 leads PROVEN, 1 PARTIALLY PROVEN.** No lead was DISPROVEN.

## Root Causes Identified

| # | Root Cause | Classification | Confidence |
|---|-----------|---------------|-----------|
| RC1 | Certification declared, not derived | ROOT CAUSE | PROVEN |
| RC2 | Evidence frozen snapshot, never re-validated | ROOT CAUSE | PROVEN |
| RC3 | Multiple disconnected control systems | STRUCTURAL WEAKNESS | PROVEN |
| RC4 | Non-bootstrappable continuation state | STRUCTURAL WEAKNESS | PROVEN |
| RC5 | Systematic override of safety controls | STRUCTURAL WEAKNESS | PROVEN |
| RC6 | ORA namespace mismatch | IMMEDIATE DEFECT | PROVEN |
| RC7 | Dry-run commands mutate state | IMMEDIATE DEFECT | PROVEN |
| RC8 | CI doesn't test published packages | STRUCTURAL WEAKNESS | PROVEN |
| RC9 | Controller-state unfalsifiable contradiction | ROOT CAUSE | PROVEN |

## What Works (Proven)

1. **Product implementations:** 5/6 format libraries load, parse, and produce typed domain models from installed packages
2. **Package infrastructure:** All 7 packages install and co-exist without conflict
3. **Oracle layer:** 20 formats verified, 73/73 PASS (gen-1)
4. **SAL facts:** 14,441 facts compiled successfully
5. **Governance detection:** 211 validators run, detect real problems (9 FAIL, 38 WARN)
6. **Event journal integrity:** 522 events, hash chain PASS
7. **Obligation registers:** All 6 structurally valid, consumed by reconciler
8. **Contract compilation:** Digest-bound to SAL facts
9. **Reconciler structural checks:** Deterministic, correct file/symbol existence validation

## What Doesn't Work (Proven)

1. **Certification:** Manually-set string, exploitable, not derived from proof
2. **Evidence freshness:** No hash tracking, no invalidation, no re-execution
3. **Control system coherence:** 6 competing systems, 2 completely disconnected from FF6
4. **Bootstrapping:** Clean clone cannot reconstruct continuation state
5. **Safety controls:** 18 bypass rules, 120 except-and-continue blocks, governance runs post-sprint
6. **CI coverage:** Zero gen-2 packages tested in CI
7. **ORA metadata:** Wrong namespace declared in ~12 files
8. **Dry-run integrity:** Diagnostic commands mutate tracked state

## Tradeoffs and Rejected Alternatives

### Single authority: FF6 controller vs Plan Control vs new system
- **Chosen:** Repair FF6 controller (state-derived architecture preserved)
- **Rejected:** Plan Control — inert, no runtime proof, schema incompatible
- **Rejected:** New system — unnecessary; FF6's state-derived design is sound, only the certification computation is broken
- **Deciding evidence:** FF6 goal_driver already computes from committed state; Plan Control has 0 runtime evidence

### Continuation model: committed vs local-signal
- **Chosen:** Committed state (state-derived, as FF6 already partially does)
- **Rejected:** Local .local/ signal — non-bootstrappable, requires Supreme Directive overrides
- **Deciding evidence:** Clean clone experiment returns NO_SIGNAL; goal_driver already reads committed state correctly

### Certification model: derived vs labeled
- **Chosen:** Derived from current evidence + current test execution + current file hashes
- **Rejected:** Manual label (current system) — exploitable, unfalsifiable
- **Deciding evidence:** False certification exploit produces GOAL_ACHIEVED with 0 proof

### Evidence model: hash-bound vs timestamp-bound
- **Chosen:** Hash-bound (SHA-256 of source/test/corpus at acceptance time)
- **Rejected:** Timestamp-bound — source can change without detection
- **Rejected:** Re-execute all tests on every check — too expensive for certification check
- **Compromise:** Hash-based freshness detection + selective re-execution of invalidated evidence
- **Deciding evidence:** IPYNB has changed corpus files but evidence still claims PASS from 2026-08-06

### Scheduler design: unified vs per-mission
- **Chosen:** Unified scheduler covering all formats with anti-starvation
- **Rejected:** Separate FF6 + gen-1 systems — current state proves disconnection causes format starvation
- **Deciding evidence:** Generic deepening returns format_not_found for all 6 FF6 formats

## Verification Suite Readiness

The verification suite (28+ tests) specified in the plan is EXECUTABLE given the repair items. Key tests that can be written immediately:

1. **False certification negative control** — set promotion=CERTIFIED without proof → NOT certified (validates R4)
2. **Clean-clone bootstrap** — delete .local/, run command, get correct state (validates R7)
3. **Dry-run non-mutation** — git diff after every --dry-run command = empty (validates R8)
4. **Evidence invalidation** — modify source → evidence stale (validates R6)
5. **Contradiction gate** — current controller-state.yaml → FAIL (validates R3)

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Repair breaks gen-1 format tests | Medium | Medium | Phase 1 stabilization before architecture changes |
| Derived certification shows 0/6 (honest) | Certain | Low (correct) | Expected — truth_boundary already says 0/6 |
| Legacy consumers of promotion labels | Low | Medium | Grep for all readers before R4 |
| Plan Control has undiscovered consumers | Very Low | Low | It has 0 journal entries — nothing depends on it |
| CLAUDE.md simplification breaks agent behavior | Medium | High | R16 is last in Phase 3 — other repairs stable first |

---

## FINAL VERDICT

# STRUCTURAL_REDESIGN_REQUIRED

## Justification

The Format Factory repository contains real, working product code (5/6 format libraries demonstrated), a sound SAL→contract→obligation pipeline, and a correctly-designed state-derived architecture concept (FF6 goal driver). These are genuine accomplishments worth preserving.

However, the system that is supposed to convert this product code into **certified, continuously-improving libraries** has fundamental structural failures:

1. **Certification is declared, not derived.** The sole certification authority is a manually-editable YAML string. Setting all 6 promotions to CERTIFIED returns GOAL_ACHIEVED regardless of test results, evidence state, or product proof. This is not a bug — it's an architectural absence: no mechanism exists to derive certification from evidence.

2. **Evidence is frozen, never re-validated.** The reconciler checks whether files and symbols exist in the AST. It never executes a test selector. Evidence recorded on 2026-08-06 is treated as current proof regardless of source, test, or corpus changes. Tests can fail without evidence being invalidated.

3. **Six competing control systems with no conflict resolution.** Generic supervisor, per-chat plan locking, FF6 goal driver, generic product deepening, Plan Control, and legacy mechanisms coexist. Two of these (generic deepening, Plan Control) have zero FF6 awareness. The others overlap on task selection, continuation, and state management. Conflict resolution is text-based (CLAUDE.md precedence rules), not code-enforced.

4. **18 bypass rules make all controls advisory.** Sprint closeout is best-effort, governance runs post-sprint, 17 of 23 STOP reasons are overridden, and 120 except-and-continue blocks ensure almost nothing prevents state advancement. The governance validators correctly detect problems (blocks=True) but the operating rules prevent those blocks from having effect.

5. **Controller state contains an unfalsifiable contradiction.** The same file says 4/6 CERTIFIED (promotion block), 0/6 CERTIFIED (truth_boundary), 0 production certifications, and "promotion is computed from proof" (invariant). No mechanism enforces consistency between these sections.

These are not bugs to patch — they are structural absences in the production pipeline. The product code works. The machinery around it does not reliably produce continuous improvement, and cannot do so without the redesign specified in artifacts 18-19.

The 20-item repair plan (R1-R20) addresses all 9 root causes in dependency order. Phase 1 fixes immediate defects. Phase 2 fixes the certification chain. Phase 3 consolidates control systems. Phase 4 builds the target system. Phase 5 proves it works end-to-end. Estimated effort: 16-26 days.

**The product is real. The certification system is not. The repair plan addresses this gap.**

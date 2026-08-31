# 17 — Machinery Disposition Register

**Baseline commit:** dd909cf3a
**Evidence:** All investigation phases

## Disposition Decisions

### D1: FF6 Goal Driver → REPAIR
- **Component:** `tools/ff6/goal_driver.py`
- **Current state:** Deterministic but reads promotion labels, not proof chains
- **Root cause addressed:** RC1 (certification declared not derived)
- **Repair:** Replace promotion-label reading with proof-chain certification computation (R4, R5)
- **Dependencies:** R3 (contradiction gate) must be in place first
- **Evidence:** False certification exploit PROVEN

### D2: FF6 Controller Events → REPAIR
- **Component:** `tools/ff6/controller_events.py`
- **Current state:** Hash chain works; projection sync is deliberately narrow
- **Root cause addressed:** RC9 (contradictory controller state)
- **Repair:** Either derive full projection from journal replay, or formally separate journal from projection authority
- **Dependencies:** R2 (authority decision) determines approach
- **Evidence:** Chain integrity PROVEN; semantic projection gap PROVEN

### D3: FF6 Event Journal → PRESERVE
- **Component:** `plans/strategic/ff6/events.jsonl` (522 events)
- **Disposition:** Keep as historical record. Do not use as certification authority.
- **Evidence:** Chain integrity PASS; semantic gap documented

### D4: Controller State File → REPAIR
- **Component:** `plans/strategic/ff6/controller-state.yaml`
- **Current state:** Three-way contradiction (promotion vs truth_boundary vs production_certifications)
- **Repair:** R3 (contradiction gate) + R4 (remove manual certification). Make promotion a DERIVED section.
- **Evidence:** Three-way contradiction PROVEN

### D5: Contract Reconciler → REPAIR
- **Component:** `tools/format_contract/contract_reconciler.py`
- **Current state:** Checks file/symbol existence, never executes tests
- **Repair:** R6 (hash-based freshness tracking + optional execution mode)
- **Evidence:** Non-execution PROVEN; all outputs SUPPORTED_NONPROMOTING

### D6: Evidence Stores → REPAIR
- **Component:** `shared/format-contracts/implementation-evidence/*.yaml`
- **Repair:** R6 (add source/test/corpus file hashes, auto-invalidate on change)
- **Evidence:** Historical snapshots never re-validated PROVEN

### D7: Generic Supervisor Loop → CONTAIN then RETIRE
- **Component:** `tools/supervisor/supervisor_loop.py`, `autonomous_cycle.py` (3,239 lines), `check_continuation.py` (1,183 lines)
- **Current state:** 120 except-and-continue blocks, 23+ STOP reasons (17 overridden), non-bootstrappable signal
- **Contain:** Remove Supreme Directive overrides (R16). Make validators fail-closed.
- **Long-term:** Retire in favor of single official command (R7) that derives state from committed files
- **Dependencies:** R2 (authority decision), R7 (bootstrappable command), R16 (typed failures)
- **Evidence:** Non-bootstrappability PROVEN; systematic override PROVEN

### D8: Generic Product Deepening → CONTAIN then MERGE or RETIRE
- **Component:** `tools/supervisor/lane_selector.py`, `autonomous_task_generator.py`, `dom_gap_generator.py`, `product_deepening_gate.py`
- **Current state:** Zero FF6 awareness. Covers gen-1 formats only.
- **Repair/Contain:** R15 (either extend to cover all formats or scope with explicit boundary)
- **Long-term disposition depends on:** R2 (authority decision for task selection)
- **Evidence:** FF6 format_not_found for all 6 PROVEN

### D9: Plan Control System → RETIRE or INTEGRATE
- **Component:** `tools/plan_control/` (12 modules)
- **Current state:** Bootstrapped but inert. 0 plans, 0 tasks, 0 journal entries. Schema incompatible with FF6.
- **Disposition:** R14 decision. Journal/projection concepts may be valuable if integrated. Current implementation has no runtime proof.
- **Evidence:** Plan Control doctor returns ok=false, 0 everything PROVEN

### D10: Autonomous Task Generator → REPAIR
- **Component:** `tools/supervisor/autonomous_task_generator.py`
- **Current state:** Dry-run mutation bug at line 1705. Hardcoded expansion goals for gen-1 formats only.
- **Repair:** R8 (fix dry-run flag propagation)
- **Evidence:** Dry-run mutation PROVEN (3KB → 48KB)

### D11: Sprint Executor Override Logic → REPAIR
- **Component:** `tools/supervisor/sprint_executor.py` (lines 69-75, 688-694)
- **Current state:** 5 TRUE_EXTERNAL_GATEs honored; all other STOP reasons overridden
- **Repair:** R16 (typed failure semantics, remove blanket override)
- **Evidence:** 17+ STOP reasons overridden PROVEN

### D12: CLAUDE.md Bypass Rules → REPAIR
- **Component:** `CLAUDE.md` Supreme Directive and 18 bypass rules
- **Current state:** Makes all sprint closeout best-effort, all non-external-gate STOPs overridable
- **Repair:** R16 (replace "best effort" with typed outcomes, constrain Supreme Directive to TRUE_EXTERNAL_GATEs only)
- **Evidence:** 18 bypass rules cataloged PROVEN

### D13: CI Pipeline → REPAIR
- **Component:** `.github/workflows/ci.yml`
- **Current state:** Only installs root dev package. Zero gen-2 packages. capability-parity uses continue-on-error.
- **Repair:** R10 (add gen-2 installations, resolve Python version conflicts)
- **Evidence:** No gen-2 installation PROVEN

### D14: Product-Goal Metadata → REPAIR
- **Component:** `plans/strategic/ff6/product-goal.yaml` (ORA entries)
- **Repair:** R11 (resolve namespace, update all consumers)
- **Evidence:** Double namespace mismatch PROVEN

### D15: Production Program → REPAIR
- **Component:** `tools/supervisor/production_program.py` (ORA ProductTarget)
- **Current state:** source_package_id="openraster" points to nonexistent directory
- **Repair:** Part of R11 (ORA namespace resolution)
- **Evidence:** Phantom path PROVEN

### D16: Legacy/Alternative Mechanisms → RETIRE
- **Component:** `.supervisor/sprint-loop.md`, `plans/codex/handover/` (frozen at Event 47 vs current 522), older master-plan state files
- **Disposition:** Retire. These are historical artifacts with no current consumers.
- **Evidence:** codex handover 475 events behind PROVEN; sprint-loop.md superseded by autonomous machinery

### D17: Per-Chat Plan Locking → PRESERVE (with scope clarification)
- **Component:** `tools/supervisor/write_plan_lock.py`, `.local/supervisor/plan-locks/`
- **Disposition:** Preserve for session-scoped plan execution. Clarify relationship to single authority (R2).
- **Evidence:** Plan locking mechanism works as designed for session boundary control

### D18: Obligation Registers → PRESERVE
- **Component:** `plans/strategic/ff6/obligations/*.yaml`
- **Disposition:** Preserve. Structurally valid, consumed by reconciler correctly.
- **Evidence:** All 6 obligation files parsed and reconciled successfully

### D19: SAL Pipeline → PRESERVE
- **Component:** `shared/sal-facts/*.yaml`, `tools/spec/merge_sal_facts.py`
- **Disposition:** Preserve. 14,441 facts, 14 seeded formats. Foundation for contract compilation.
- **Evidence:** Compilation succeeds; digest binding works

### D20: Package Infrastructure → PRESERVE
- **Component:** `src/python/*/pyproject.toml`, `packaging/python/package-matrix.yaml`
- **Disposition:** Preserve. All packages install and import correctly.
- **Evidence:** Co-installation test PASS

## Summary

| Disposition | Count | Components |
|------------|-------|------------|
| PRESERVE | 7 | D3, D17, D18, D19, D20, P7 (oracle), P8 (governance framework) |
| REPAIR | 11 | D1, D2, D4, D5, D6, D10, D11, D12, D13, D14, D15 |
| CONTAIN→RETIRE | 1 | D7 (generic supervisor) |
| CONTAIN→MERGE/RETIRE | 1 | D8 (generic deepening) |
| RETIRE or INTEGRATE | 1 | D9 (Plan Control) |
| RETIRE | 1 | D16 (legacy mechanisms) |

**Key observation:** The product implementations (P4 — the actual format libraries) are the strongest proven components. The machinery around them is where most repair is needed. The repair plan's progression (R1→R20) is designed to fix the certification and evidence chain first, then consolidate control systems, then prove the complete vertical cycle.

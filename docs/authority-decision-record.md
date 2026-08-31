# Authority Decision Record

**Created:** 2026-08-31
**Context:** FF6-RECONSTRUCTION-001 (R2)
**Baseline:** dd909cf3a
**Evidence:** reports/production-assessment-2026-08-31/02-authority-matrix.md

## Purpose

For every concern in the production system, this document names the single
authority.  Other sources that currently claim the same concern are classified
as DERIVED (computed from the authority), ADVISORY (informational), or
RETIRED (no longer consumed).

All future changes must respect these decisions. No new source may claim
authority over a concern that already has a named authority without first
amending this record.

## Decisions

### 1. Active Mission

| | |
|---|---|
| **Authority** | `plans/strategic/ff6/product-goal.yaml` |
| **Rationale** | `goal_driver.py` hardcodes `GOAL_PATH`; durable, committed, deterministic |
| **DERIVED** | `session-resume.md` (regenerated each cycle) |
| **ADVISORY** | `master-plan.md` (strategic narrative, not machine-consumed) |

### 2. Task Selection (FF6 formats)

| | |
|---|---|
| **Authority** | `tools/ff6/goal_driver.py` → obligation registers + reconciliation reports |
| **Rationale** | State-derived, session-independent, bootstrappable from clean clone |
| **RETIRED** | `next-work-items.json` (for FF6 formats — supervisor cannot select them) |
| **RETIRED** | `autonomous_task_generator.py` expansion goals (gen-1 only, no FF6 awareness) |
| **Scope** | FF6 formats only: ipynb, ora, nrrd, xliff, safetensors, ubl |

### 3. Task Selection (gen-1 formats)

| | |
|---|---|
| **Authority** | Generic supervisor (`next-work-items.json` via `generate_next_work_items.py`) |
| **Rationale** | Existing gen-1 infrastructure works for gen-1 formats |
| **Boundary** | Gen-1 task selection MUST NOT select FF6-governed formats |
| **Migration** | R17 (unified scheduler) will eventually merge both; until then, explicit boundary |

### 4. Certification

| | |
|---|---|
| **Authority** | `tools/ff6/goal_driver.py` `_is_certified()` (derived computation) |
| **Rationale** | R4/R5 replaced label-reading with proof-chain derivation |
| **RETIRED** | `controller-state.yaml` promotion block as certification INPUT (now DERIVED output) |
| **RETIRED** | Manual CERTIFIED strings (no authority regardless of where written) |
| **Invariant** | Certification MUST regress when source/test/corpus hashes change (R6) |

### 5. Evidence Acceptance

| | |
|---|---|
| **Authority** | `autonomous_cycle.py` pipeline (grading via `grade_declared_work.py`) |
| **Rationale** | Sole acceptance authority with independent grading |
| **DERIVED** | `evidence-review.json` (output of the pipeline) |
| **ADVISORY** | `evidence-declaration.yaml` (self-reported input to the pipeline) |

### 6. Obligation Definition

| | |
|---|---|
| **Authority** | `plans/strategic/ff6/obligations/*.yaml` (per-format registers) |
| **Rationale** | `goal_driver.py` hardcodes `OBLIGATIONS_DIR`; fail-closed on missing |
| **DERIVED** | `controller-state.yaml` canonical_obligations counts (must match registers) |
| **DERIVED** | Reconciliation report totals |

### 7. Implementation State

| | |
|---|---|
| **Authority** | `reports/format-contract-layer/*-obligation-reconciliation.json` |
| **Rationale** | Computed by `contract_reconciler.py` from current source/test AST |
| **DERIVED** | `implementation-evidence/*.yaml` (input to reconciler, not final state) |
| **Invariant** | Reconciliation with `promotion_effect: none` is NEVER promoting |

### 8. Continuation (FF6 mission)

| | |
|---|---|
| **Authority** | `tools/ff6/goal_driver.py` `evaluate()` |
| **Rationale** | State-derived, no session identity, no iteration budget, bootstrappable |
| **RETIRED** | `check_continuation.py` for FF6 continuation decisions (session-scoped, non-bootstrappable) |
| **RETAINED** | `check_continuation.py` for plan-lock enforcement, CCI protection, GOV_BLOCK detection |

### 9. Terminal State

| | |
|---|---|
| **Authority** | `goal_driver.py` verdict `GOAL_ACHIEVED` (6/6 certified) or `BLOCKED` (TRUE_EXTERNAL_GATE) |
| **Rationale** | Only two terminal states: mission complete or externally blocked |
| **RETIRED** | CLAUDE.md Supreme Directive override of non-external-gate STOPs (R16 scope) |
| **RETAINED** | CCI non-overridable stops (SESSION_MISMATCH, etc.) — these are session-boundary controls, not mission terminals |

### 10. Release State

| | |
|---|---|
| **Authority** | `registry/format-registry.yaml` (gate states) |
| **Rationale** | Canonical registry, consumed by gate validators |
| **ADVISORY** | `gate-states.yaml` snapshots |
| **TRUE_EXTERNAL_GATE** | Gate 11 execution requires Babar Raza's business authority |

### 11. Worker Ownership

| | |
|---|---|
| **Authority** | Coordination plane (`tools/supervisor/coordination/`) |
| **Rationale** | Hooks in `.claude/settings.json` auto-coordinate; advisory mode |
| **RETIRED** | `plan_control/locks/` (inert, never populated) |

### 12. Capability Definition

| | |
|---|---|
| **Authority** | `.governance/capabilities/registry.yaml` |
| **Rationale** | Canonical, synced by `/sync-capabilities` |
| **DERIVED** | `reports/capability-layer/` (projections from registry) |

### 13. Format Maturity

| | |
|---|---|
| **Authority** | Derived from `_is_certified()` for FF6 formats |
| **Authority** | `product-deepening-ledger.yaml` for gen-1 formats |
| **RETIRED** | `controller-state.yaml` promotion strings as maturity INPUT |
| **Migration** | R17 (unified scheduler) will merge maturity models |

### 14. Plan Control System

| | |
|---|---|
| **Decision** | RETIRE |
| **Rationale** | 0 plans, 0 tasks, 0 journal entries, 0 projections. Schema incompatible with FF6. No runtime proof of any kind. |
| **Valuable concepts** | Journal/projection pattern (already implemented better in FF6 events.jsonl) |
| **Migration** | R14 — formal retirement. Preserve concept docs if any. |

### 15. Generic Product Deepening (for FF6 formats)

| | |
|---|---|
| **Decision** | SCOPE BOUNDARY — gen-1 only |
| **Rationale** | Zero FF6 awareness. `lane_selector.py --format ipynb` returns format_not_found. |
| **Migration** | R15 — add explicit boundary enforcement. R17 — eventual merger. |

### 16. Gap State

| | |
|---|---|
| **Authority** | `gap-ledger.json` (supervisor, gen-1) / `current-gaps.yaml` (FF6) |
| **Boundary** | Each covers its own format set; no cross-contamination |
| **Migration** | R17 (unified scheduler) will merge gap tracking |

## Non-Negotiable Constraints

1. No source may claim certification authority except `_is_certified()`.
2. No label, string, or manual entry may substitute for derived proof.
3. Gen-1 task selection MUST NOT select FF6-governed formats.
4. FF6 task selection MUST NOT select gen-1-governed formats.
5. `check_continuation.py` is RETAINED for plan-lock and CCI enforcement
   but RETIRED as FF6 continuation authority.

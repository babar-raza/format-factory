# Format Contract Layer (L30)

**Canonical layer plan:** `plans/layers/format-contract-layer.md` · **Mission:** FCL-MACHINERY-2026-07-16
**Created by decision:** DEC-038 (`plans/layers/decision-register.yaml`)

## What this layer is

The governed layer between the Specification Authority Layer (L01) and the Capability
Layer (L03). It converts committed facts into **developer-product contracts**: what a
production library MUST let developers do for each format, at what depth, proven how.

```
L01 SAL          "the spec says X"                     shared/sal-facts/{fmt}.yaml
L27 Obligation   "a processor must handle X"           (consumed when mature)
L30 CONTRACT     "a library must let devs do Y,        shared/format-contracts/{fmt}.yaml
                  at depth D, proven by Z"
L03 Capability   "the product actually does Y at D'"   reconciliation reports + gap ledger
L14 Feature      "therefore build these tasks"         next-work-items selection
```

**These are never equivalent:** a spec fact ≠ a contract requirement ≠ a planned
capability ≠ a declared capability ≠ implemented ≠ tested ≠ oracle-proven ≠
production-ready. The depth scale (0 ABSENT … 8 PRODUCTION_HARDENED) and reconciliation
statuses (NOT_STARTED … ORACLE_PROVEN) encode the distinctions mechanically.

## Why SAL facts are not product requirements

A fact records what a specification says. A contract requirement states what a library
must *do about it* — with depth, tests, and gates. The compiler derives requirements
from facts × family policy packs × reviewed research findings; it never invents them.

## Why contracts are not capability claims, and capabilities are not proof

Contracts are the **required** baseline. The reconciler
(`tools/format_contract/contract_reconciler.py`) measures **observed** reality with
false-claim rules: a symbol is capability surface, not proof; a test file marks TESTED
at most; oracle credit needs a VERIFIED oracle. required − observed = the canonical gap
ledger entries (`GAP-FCL-*` in `reports/capability-layer/gap-ledger.json`), consumed by
the ACTIVE supervisor chain (`capability_feature_compiler.py`) into selectable work items.

## Two-plane generation (why reruns are consistent)

- **Research plane** (non-deterministic, auditable, rare): source records + reviewed
  findings enter through `research_intake.py`'s review gate into hash-bound stores
  (`shared/format-contracts/research/{fmt}.yaml`); normative claims route to the SAL
  candidate queue and are committed only by the L01 seed path
  (`tools/spec/seed_sal_candidates.py`, structural_fact_manual provenance).
- **Compile plane** (deterministic, every run): `contract_compiler.py` is a pure
  function of committed stores. Same inputs → byte-identical output (`--check`,
  `--verify-idempotency`, V239). Contract bodies carry **no timestamps**; volatile
  state lives in `registry/format-contract-registry.yaml`. `input_digests` pin the
  exact inputs; V240 detects hand-edited bodies mechanically.

## Readiness gate (no fabrication)

`fact-category-requirements.yaml` defines per-family fact categories with minimum
counts. Below threshold the compiler **refuses** — the format is recorded
BLOCKED_NEEDS_AUTHORITY with the missing categories as seeding tasks. Thin inputs
never yield fake contracts.

## How specification changes propagate

Source/store changes alter digests → V238 flags staleness → `staleness_checker.py`
(wired into the autonomous cycle prepass via `run_contract_healing_prepass`) emits
repair tasks routed to owning skills (`refresh-format-contract` →
`compile-format-contract` after review). Contracts are never silently regenerated.

## How the system heals missing or shallow contracts

Healing conditions → machine-readable tasks in
`.local/supervisor/contract-repair-tasks.json`: NO_CONTRACT → compile; BLOCKED →
research seeding; STALE → refresh; UNRECONCILED → reconcile; SHALLOW (quality below
review threshold) → adversarial review + findings seeding.

## Quality enforcement

`quality_scorer.py` (8 dimensions, thresholds in `quality-policy.yaml`: <60 blocked,
<80 needs review) and `reference_comparator.py` (the reference contract file is
**hash-registered as a comparison oracle only** — path-denylisted as a generation
input, DEC-038). Shallow language is blocked by V235; family adequacy + simplicity
budgets prevent both thin contracts and over-engineering of simple formats.

## Skills and commands (the only mutation surfaces)

9 skills: research-format-contract-sources, check-contract-sal-readiness,
compile-format-contract, validate-format-contract, reconcile-contract-capabilities,
compile-contract-gaps, refresh-format-contract, review-format-contract,
audit-contract-portfolio. 3 thin chain commands: investigate-format-contract,
backfill-format-contracts, prove-format-contract. Governance: V232–V241
(`governance_validators_format_contract.py`, domain `format_contract`).

## How new formats enter

Add one line to `shared/format-contracts/policy/format-family-map.yaml` (plus a family
pack only for genuinely new families — packs are data, not code), seed facts/findings
through the governed paths, and the same machinery compiles, validates, reconciles,
and heals the new format. No compiler edits required.

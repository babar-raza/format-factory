# Format Contract Layer

```yaml
layer_metadata:
  layer_id: L30
  canonical_name: Format Contract Layer
  canonical_slug: format-contract-layer
  permanent_plan_path: plans/layers/format-contract-layer.md
  schema_version: '1.0'
  plan_revision: '1'
  repository_revision: a6479e8c
  status: GOVERNED_OPERATIONAL
  health: HEALTHY
  maturity_current: 3
  maturity_target: 4
  current_stage: GOVERNED_OPERATION
  current_owner: null
  agent_type: null
  session_id: 7e0d132fbf0f
  active_sprint: fcl-l30-001
  active_taskcards:
  - TC-FCL-090
  ready_taskcards: []
  blocked_taskcards: []
  completed_taskcards:
  - TC-FCL-000
  - TC-FCL-010
  - TC-FCL-020
  - TC-FCL-030
  - TC-FCL-040
  - TC-FCL-050
  - TC-FCL-060
  - TC-FCL-070
  - TC-FCL-080
  dependencies:
  - L01
  - L02
  - L27
  upstream_layers:
  - L01
  - L02
  - L27
  downstream_layers:
  - L03
  - L14
  skill_ids:
  - research-format-contract-sources
  - check-contract-sal-readiness
  - compile-format-contract
  - validate-format-contract
  - reconcile-contract-capabilities
  - compile-contract-gaps
  - refresh-format-contract
  - review-format-contract
  - audit-contract-portfolio
  command_ids:
  - research-format-contract-sources
  - check-contract-sal-readiness
  - compile-format-contract
  - validate-format-contract
  - reconcile-contract-capabilities
  - compile-contract-gaps
  - refresh-format-contract
  - review-format-contract
  - audit-contract-portfolio
  - investigate-format-contract
  - backfill-format-contracts
  - prove-format-contract
  evidence_paths:
  - plans/.claude/soft-tinkering-fairy.md
  - .local/evidences/fcl-l30-001/
  last_started_at: '2026-07-16'
  last_progress_at: '2026-07-16'
  last_updated_at: '2026-07-16'
  last_verified_at: null
  last_verified_revision: null
  next_task_id: TC-FCL-090
  next_action: Evidence bundle + final report + machinery-plan closeout (lifecycle_audit
    then write_plan_lock --terminal --audit-gate); post-mission - seed the 11
    BLOCKED_NEEDS_AUTHORITY formats via research plane
  handoff_id: null
```

## 1. Layer Metadata

This plan is the canonical working plan for **Format Contract Layer** (`L30`). The layer was
created by mission FCL-MACHINERY-2026-07-16 (authoritative per-chat plan:
`plans/.claude/soft-tinkering-fairy.md`) to fill the documented gap between the Specification
Authority Layer (L01) and the Capability Layer (L03): nothing previously converted spec facts
into developer-product requirements.

## 2. Authority and Purpose

This layer owns the canonical, machine-readable developer-product contract for every format:
what a production library MUST let developers do, at what depth, with what proof. Its authority
sits strictly between spec authority and capability observation:

- L01 SAL says "the spec says X" (normative facts).
- L27 Obligations says "a conforming processor must handle X" (grammar duties).
- **L30 Format Contract says "a production library must let developers do Y, at depth D, proven by Z."**
- L03 Capability says "the product actually does Y at depth D', proven/unproven."
- L14 Feature Compilation says "therefore build these tasks."

A specification fact, a contract requirement, a planned capability, a declared capability, an
implemented capability, a tested capability, an oracle-proven capability, and a production-ready
capability are NEVER equivalent in this layer's records.

## 3. Scope

- Contract schema (`schemas/format-contracts/format-contract.schema.json`) and its versioning
- Committed canonical contract stores: `shared/format-contracts/{format}.yaml` (compiler-generated only)
- Research findings stores: `shared/format-contracts/research/{format}.yaml` (PRODUCT_REQUIREMENT class)
- Policy stores: `shared/format-contracts/policy/` (shared library contract, fact-category
  requirements, family policy packs)
- Volatile contract state: `registry/format-contract-registry.yaml`
- Compile-plane tools: `tools/format_contract/` (compiler, validator, scorer, comparator,
  reconciler, gap compiler, staleness checker, research intake, source researcher)
- Contract governance validators V232-V241
- The 9 contract skills and 3 chain commands listed in layer metadata

## 4. Explicit Non-Scope

- Product source mutations (`src/python/**`, `src/net/**`) — contracts drive gap taskcards; the
  taskcards are executed by product lanes under their own skills
- SAL fact store writes (`shared/sal-facts/`) — L30 emits SAL *candidates* into a review queue;
  L01 owns commits
- Oracle case authoring (L05) and test execution (L07)
- Release certification (L28) — L30 feeds release gates; it does not run them

## 5. Owned Decisions

- Contract schema evolution and migration policy
- Capability ID assignment rules (`{FMT}-{DOMAIN}-{NNN}`, stable, semantic)
- Depth scale semantics (0 ABSENT .. 8 PRODUCTION_HARDENED) and depth derivation rules
- SAL readiness thresholds (fact-category coverage, per family)
- Quality score dimensions and blocking thresholds
- Family policy pack content (as reviewable data)
- Whether a format is contract-ready or BLOCKED_NEEDS_AUTHORITY

## 6. Upstream Inputs

- Upstream layers: `['L01', 'L02', 'L27']`
- `shared/sal-facts/{format}.yaml` — normative facts (authoritative input)
- `shared/qname-registry/{format}.yaml` — QName alignment for API contracts
- L27 obligation registers — consumed when mature; absence is tolerated and recorded
- `registry/format-registry.yaml` — format identity, family, spec URLs
- Reviewed research findings (via this layer's own research plane intake)

## 7. Downstream Consumers

- L03 Capability Layer — contract capabilities become the requirement baseline that capability
  records and the gap ledger reconcile against (`contract_capability_id` back-references)
- L14 Feature Compilation — `load_format_contract()` enriches feature IR / work items
- L11 Supervisor — staleness/healing conditions produce repair tasks in the autonomous cycle
- L12 Validation — V232-V241 run in the governance runner
- Release gates — no product passes its production gate with an absent/invalid/stale/unreconciled contract

## 8. Ideal Production Design

Two-plane architecture (see authoritative plan Part 2, preserved here as the layer's design
summary):

1. **Research plane** (non-deterministic, auditable, rare): source acquisition + hashing,
   classified research findings, SAL fact candidates, review gate, commit to hash-bound stores.
2. **Compile plane** (deterministic, cheap, every run): `contract_compiler.py` is a pure
   function of committed state; same inputs produce byte-identical output (canonical
   serialization: sorted keys, ID-ordered lists, LF, no volatile fields; `input_digests` pin the
   exact inputs).

Rerun consistency comes from this separation. Readiness gates refuse compilation below
fact-category coverage thresholds — thin inputs yield honest BLOCKED_NEEDS_AUTHORITY states,
never fabricated contracts. The canonical/volatile split (no timestamps in contract bodies;
registry carries them) makes byte-comparison a valid idempotency test. V240 detects hand-edited
contract bodies (digests cannot be reproduced from committed inputs).

## 9. Verified Current Implementation

As of 2026-07-16 (revision a6479e8c): nothing implemented yet. Layer created with governance
registration (TC-FCL-000). Verified free identifiers at creation: L30, V232-V241, DEC-038,
HO-010/HO-011, `shared/format-contracts/` absent.

## 10. Current Execution Stage

GOVERNANCE_REGISTRATION — TC-FCL-000 in progress; TC-FCL-010 (determinism foundation) next.

## 11. Current Maturity Assessment

0/5 — no schema, no compiler, no contracts, no validators. Design and execution plan complete
and taskcardized.

## 12. Target Maturity

4/5 — contracts generated deterministically through skills for the full portfolio (or honest
blocked states), validators enforcing, supervisor consuming staleness/healing conditions,
pilots proven against the registered reference oracle.

## 13. Current Strengths

- Complete root-cause analysis and taskcardized plan (10 parents, 52 children)
- Free identifier space verified; no naming collisions
- Proven upstream pattern to mirror (SAL committed stores + `merge_sal_facts.py --check`)

## 14. Gap Register

- FCL-GAP-001: SAL fact coverage for reference pilots is 2-3 facts each (ubl 3, xliff 2,
  ipynb 3, mtlx 3, nrrd 2) — far below any contract-grade category threshold. Owned by
  TC-FCL-050 MS-01/02 (research seeding through governed skills).
- FCL-GAP-002: No governed store exists for product-requirement knowledge (non-normative).
  Owned by TC-FCL-030.
- FCL-GAP-003: L14 does not consume contracts. Owned by TC-FCL-020-06.

## 15. Root-Cause Register

RC1 SAL too thin for contract derivation (fabrication risk); RC2 quality/determinism tension;
RC3 no governed channel for non-SAL knowledge; RC4 layer completion graded by artifact existence
not consumption; RC5 determinism asserted not constructed; RC6 quality bar unbound. Full
analysis: authoritative plan Part 1.

## 16. Repair Architecture

Two-plane separation (RC1/RC2/RC3/RC5), consumption-first vertical slice on CSV (RC4),
hash-registered reference comparator with measurable dimensions (RC6). Healing conditions →
machine-readable repair tasks via TC-FCL-070.

## 17. Schemas and Contracts

- `schemas/format-contracts/format-contract.schema.json` (v1.0) — contract document schema
- `schemas/format-contracts/research-findings.schema.json` — research store schema (TC-FCL-030)
- `registry/format-contract-registry.yaml` — volatile state registry
- Policy stores under `shared/format-contracts/policy/`

## 18. Producers

- `tools/format_contract/contract_compiler.py` → `shared/format-contracts/{fmt}.yaml`
- `tools/format_contract/research_intake.py` → `shared/format-contracts/research/{fmt}.yaml`
- `tools/format_contract/gap_compiler.py` → contract gap records + work items
- `tools/format_contract/quality_scorer.py` / `reference_comparator.py` → registry scores + reports

## 19. Consumers

- `tools/supervisor/capability_compiler.py` (`load_format_contract()`)
- `tools/supervisor/autonomous_cycle*` (staleness/healing conditions)
- Governance runner (V232-V241)
- `reports/format-contract-layer/` report readers (portfolio audits)

## 20. Skills and Commands

Nine skills + three chain commands as listed in layer metadata. All contract mutations MUST go
through these skills; commands are thin routing surfaces that print skill chain, input paths,
output paths, validation results, and evidence paths, returning non-zero on blocking failures.

## 21. Validators and Enforcement

V232 schema validity · V233 provenance closure · V234 depth completeness · V235
shallow-language · V236 ID pattern/uniqueness/stability · V237 MUST test/gate completeness ·
V238 freshness · V239 determinism (`--check` zero-diff) · V240 hand-edit guard · V241
consumption. Registered in `registry/governance/validator-id-authority.yaml`, domain
`format_contract`, file `tools/supervisor/governance_validators_format_contract.py`.

## 22. Tests and Negative Controls

`tests/format_contract/` — unit (schema, serializer, ID stability, depth rules, readiness,
scoring, packs), integration (facts→contract, contract→reconciliation, gap→work-item
consumption, refresh-on-hash-change), negative (zero facts, unresolvable provenance, duplicate
IDs, missing security, hand-edit detection, stale digests), adversarial fixtures (schema-dump,
parser-only-complete, invented refs, over-engineered simple format), golden files (CSV, TOML),
two-run idempotency.

## 23. Evidence and Observability

Evidence root `.local/evidences/fcl-l30-001/` (and successor run IDs), structure per
authoritative plan Part 8. Registry (`registry/format-contract-registry.yaml`) answers: which
formats lack contracts, which are stale/shallow/unverified, which capabilities are claimed
without proof, what runs next.

## 24. Recovery and Rollback

Targeted `git checkout -- <exact owned paths>` only; regenerate derived artifacts; store-level
rollback = checkout of the store file + registry entry reversal + `--check` re-verification.
Never broad reset/clean/stash (AGENTS.md §CO).

## 25. Security and Compliance

Research plane network acquisition is gated/optional; offline absence yields NEEDS_AUTHORITY
records, never fabrication. Reference contract file is hash-registered as a comparison oracle
and path-denylisted as a generation input (anti-copying control). Contracts must define
format-specific security requirements (attack surfaces, safe defaults, limits, opt-in external
effects) — enforced by family adequacy checks and the quality scorer.

## 26. Cross-Layer Handoffs

- HO-010: L30 → L03 — artifact `shared/format-contracts/{format}.yaml` + gap records with
  `contract_capability_id` back-references
- HO-011: L30 → L14 — artifact contract-enriched work items via `load_format_contract()`
- Upstream consumption: L01 `shared/sal-facts/{fmt}.yaml` (HO-002 family), L27 obligation
  registers when mature

## 27. Migration and Backfill

Portfolio backfill (TC-FCL-080) runs the same governed machinery over all formats after pilot
acceptance; readiness gate decides compile vs BLOCKED_NEEDS_AUTHORITY per format. Schema
migrations preserve historical contract versions and capability-ID stability (V236).

## 28. Effort and Dependencies

Multi-sprint program. DAG: 000→010→020→{030,040,070 parallel}→050 (needs 030+040), 060 (needs
040, parallel with 050) → 080 → 090. See authoritative plan Part 6.

## 29. Active Taskcards

- TC-FCL-010 — Determinism foundation (IN_PROGRESS)

## 30. Ready Taskcards

- TC-FCL-020 — CSV vertical slice (READY after TC-FCL-010 closes)

## 31. Completed Taskcards

- TC-FCL-000 — Governance registration (CLOSED 2026-07-16; evidence
  `.local/evidences/fcl-l30-001/taskcards/TC-FCL-000/closure.yaml`; reconcile-layer-index
  L30 verdict PASS; pre-existing L01-L27/L29 index drift recorded as out-of-scope findings)

## 32. Blocked and Waiting Work

- TC-FCL-020..090 — pending per DAG.

## 33. Decision Log

- DEC-038 (plans/layers/decision-register.yaml): L30 created as Format Contract Layer between
  L01/L27 and L03/L14. Rejected alternatives: merging into L27 (charter overload: grammar duties
  vs product requirements); RCAL ownership (RCAL records implementation claims, not requirements);
  backfilling contracts from the reference file (copying forbidden by mission; reference is a
  hash-registered comparison oracle only).

## 34. Work Log

- 2026-07-16 fcl-l30-001 TC-FCL-000: plan migrated in-repo + locked; preflight re-verified
  (HEAD a6479e8c; V231/DEC-037/HO-009 still maxima; L30 free); evidence run dir + run-record +
  section-processing ledger written; this layer plan created.

## 35. Verification Log

- 2026-07-16: Identifier-freedom verification (grep proofs in
  `.local/evidences/fcl-l30-001/run-record.yaml`).

## 36. Current Session Handoff

Session 7e0d132fbf0f executing TC-FCL-000. Next: index.yaml entry (TC-FCL-000-03), master.md
updates (-04), DEC-038 + HO-010/011 (-05), task-register entries (-06), then TC-FCL-010.

## 37. Exact Next Actions

1. Add L30 entry to `plans/layers/index.yaml` (TC-FCL-000-03)
2. Update `plans/layers/master.md` §5/§6/§7 (TC-FCL-000-04)
3. Record DEC-038 and HO-010/HO-011 (TC-FCL-000-05)
4. Register TC-FCL-000..090 in task-register (TC-FCL-000-06)
5. Begin TC-FCL-010 (contract schema first)

## 38. Layer Completion Gate

The layer reaches GOVERNED_OPERATIONAL only when: contracts generated deterministically through
registered skills for the portfolio (or honest blocked states); V232-V241 green in the runner;
consumption proof (contract-originated work item selected by the autonomous loop); pilots proven
vs the registered reference oracle; two-run idempotency evidence; independent adversarial
verification ACCEPT.

## 39. Change History

- 2026-07-16 rev 1: Layer created (TC-FCL-000, mission FCL-MACHINERY-2026-07-16).

---
version: "2.0"
last-updated: "2026-08-02"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
skill_id: reconcile-contract-capabilities
purpose: Reconcile compiled format contracts to implementation reality at capability or exact normative-obligation granularity without promoting presence-based evidence.
command: /reconcile-contract-capabilities
status: active
idempotency: "Same contract, obligation register, curated mapping, source, tests, and execution evidence produce byte-identical canonical reports."
loc_budget: "tools/format_contract/contract_reconciler.py"
test_path: "tests/format_contract/"
risk_level: LOW
created-by: TC-FCL-070
product_track: format_contract
---

# /reconcile-contract-capabilities

Reconcile a compiled format contract against observed implementation reality.
The legacy capability mode remains available for portfolio consumers. The exact
obligation mode adds a fail-closed, row-for-row classification of canonical
normative obligations against curated source symbols, test definitions,
executed evidence, open behavior gaps, and required positive/negative proof.

Neither mode promotes a product. Source symbols, test definitions, suite-level
execution, or generated reports are supporting evidence only; certification is
computed later from independently validated proof nodes.

## When to Use

- Use capability mode for the existing portfolio-wide observed-depth projection.
- Use exact-obligation mode when a product-readiness task requires every
  canonical obligation to be classified without percentage-based hiding.
- Use exact-obligation mode again after source, tests, authority, contract, or
  execution evidence changes; the changed digest must invalidate the report.
- Not for changing contract bodies, product source, product tests, promotion,
  certification, or release state.

## Required Inputs

| Field | Description |
|---|---|
| `format_id` | Lowercase format identifier |
| `mode` | `capability` or `exact-obligations` |
| `obligation_register` | Exact mode: canonical obligation YAML |
| `implementation_evidence` | Exact mode: curated one-row-per-obligation YAML |

## Execution

1. Confirm the compiled contract and requested input files exist.
2. In capability mode, retain the historical AST/test/oracle observed-depth
   projection and write the historical report path unchanged.
3. In exact-obligation mode, validate complete set equality between the
   obligation register and mapping before evaluating any implementation claim.
4. Resolve every mapped source reference to an exact file and qualified symbol.
5. Resolve every mapped test selector to an exact static test definition and
   every execution-evidence reference to a successful, digest-bound record.
6. Enforce status invariants: `implemented` requires exact source, tests, and
   executed supporting evidence with no declared missing behavior; `partial`
   requires explicit missing behavior; `missing` cannot claim implementation
   evidence. Other allowed statuses must carry their documented rationale.
7. Emit a canonical report with all direct input digests, row-level proof
   strength, summary counts, unresolved proof requirements, and
   `promotion_effect: none`.

```powershell
# Existing capability projection
.venv\Scripts\python.exe tools/format_contract/contract_reconciler.py --format-id nrrd

# Exact canonical-obligation projection
.venv\Scripts\python.exe tools/format_contract/contract_reconciler.py `
  --format-id nrrd `
  --exact-obligations `
  --obligation-register plans/strategic/ff6/obligations/nrrd.yaml `
  --implementation-evidence shared/format-contracts/implementation-evidence/nrrd.yaml
```

## Exact Mapping Shape

```yaml
schema: format-contracts/implementation-evidence@1
format_id: nrrd
execution_evidence:
  - evidence_id: NRRD-R1-SOURCE-TESTS
    path: reports/skills-rff6/skill-transcripts/reconcile-contract-capabilities-nrrd-readiness-001.json
    expected_result: PASS
    granularity: suite
obligations:
  - obligation_id: SAL-NRRD-OBL-...
    capability_id: NRRD-HEADER-001
    status: partial
    source_symbols:
      - src/python/nrrd/src/format_factory/nrrd/codec/reader/reader.py::_split_header
    positive_test_selectors:
      - tests/python/nrrd/test_production_namespace.py::test_loads_accepts_crlf_header
    negative_test_selectors: []
    execution_evidence_ids: [NRRD-R1-SOURCE-TESTS]
    implemented_behavior: [Accepts LF and CRLF header termination.]
    missing_behavior: [Does not yet enforce every lexical field rule.]
    proof_requirements:
      positive: [Execute the profile matrix from an installed wheel.]
      negative: [Reject leading whitespace and missing colon-space.]
```

## Mandatory Validations

- `read_only_product_source`: never writes under `src/` or product-test trees.
- `no_contract_body_writes`: contract bodies change only through
  `/compile-format-contract` (V240).
- `legacy_output_compatibility`: capability mode preserves its historical path
  and schema so existing consumers do not regress.
- `exact_set_equality`: duplicate, missing, extra, foreign-format, or
  capability-mismatched obligation rows fail closed.
- `exact_reference_integrity`: every claimed source symbol, test selector, and
  execution-evidence record resolves and matches its declared result.
- `classification_consistency`: statuses and evidence fields satisfy the
  invariants in Execution step 6.
- `digest_closure`: the exact report binds the contract, obligation register,
  curated mapping, referenced source/tests/evidence, and reconciler digests.
- `non_promoting_output`: exact reconciliation always records
  `promotion_effect: none`; suite evidence never masquerades as independent
  interoperability or certification proof.
- `determinism`: three same-input exact runs are byte-identical.
- `coherence_diagnostics`: capability output remains an input to WARN-only V247.
- `xref_completeness`: capability additions remain governed by V248 and the
  curated coverage-capability cross-reference.

## Allowed Paths

- `tools/format_contract/contract_reconciler.py` - implementation write
- `tests/format_contract/test_obligation_reconciliation.py` - behavior tests
- `schemas/format-contracts/implementation-evidence.schema.json` - mapping schema
- `shared/format-contracts/implementation-evidence/*.yaml` - curated mapping
- `reports/format-contract-layer/*-reconciliation.json` - legacy output
- `reports/format-contract-layer/*-obligation-reconciliation.json` - exact output
- `reports/skills-rff6/skill-transcripts/*.json` - execution receipt
- Compiled contracts, obligation registers, product source/tests, and referenced
  execution evidence - read only

## Forbidden Paths

- `src/python/**`, `src/net/**`, and `tests/python/**` - no writes
- `shared/format-contracts/{fmt}.yaml` - no writes
- `plans/strategic/ff6/obligations/**` - no writes
- Promotion, certification, release, and gate records - no writes
- `plans/from_chat/**`

## Stop Conditions

- Stop without writing an exact report on any schema, set-equality, reference,
  classification, digest, or declared-result failure.
- Stop if exact mode would need to infer a row from naming heuristics; the
  mapping must state it explicitly.
- Stop if a source/test/evidence input changes between validation and report
  emission; rerun from a stable snapshot.
- Do not stop the other format lanes when one mapping fails; record the scoped
  gap and continue safe unblocked work.

## Output Format

- Capability mode: `reports/format-contract-layer/{fmt}-reconciliation.json`.
- Exact mode:
  `reports/format-contract-layer/{fmt}-obligation-reconciliation.json`.
- Both write a concise stdout summary. Exact mode includes one row per canonical
  obligation, complete digest closure, proof-strength labels, and a non-promoting
  truth boundary.

## Idempotency Contract

Given identical contract, obligation register, curated mapping, referenced
source/test/evidence bytes, reconciler bytes, and environment-neutral settings,
the generated report is byte-identical. Outputs exclude timestamps, absolute
paths, durations, random IDs, and nondeterministic ordering. Re-running does not
append or duplicate rows.

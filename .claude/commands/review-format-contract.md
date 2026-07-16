---
version: "1.0"
last-updated: "2026-07-16"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "idempotent"
loc_budget: "prompt-driven adversarial review + tools/format_contract/{quality_scorer,reference_comparator}.py evidence"
test_path: "tests/format_contract/test_quality_oracle.py"
risk_level: MEDIUM
created-by: TC-FCL-080
product_track: format_contract
---

# /review-format-contract

Independent adversarial review of a compiled format contract. The reviewer
works from FILES (contract body, SAL/research stores, comparison and
reconciliation reports), never from implementation summaries, and challenges:

1. Completeness — does the contract cover the family pack's review dimensions
   and (for reference formats) the comparator's domain inventory?
2. Authority — does every capability's provenance resolve, and are sources
   classified honestly (URL_ONLY/NEEDS_AUTHORITY not inflated)?
3. Depth — are depth_required values justified by rationale, not aspirational?
4. False comprehensiveness — do requirement lines state testable behavior, or
   restate schema element names (schema-dump smell)?
5. Overreach — does any requirement lack support in facts/findings/policy?

## Execution steps

1. Read the contract body + its registry entry + quality/comparison/reconciliation reports
2. Run `.venv/Scripts/python tools/format_contract/contract_validator.py --format-id <fmt>`
   and `quality_scorer.py --format-id <fmt>` fresh (never trust cached verdicts)
3. Sample >= 5 capabilities: trace every provenance ID to its store entry
4. Issue verdict: ACCEPT | ACCEPT_WITH_REPAIRS (list owned repairs) | REJECT (reasons)
5. Record verdict + contract sha256 in `registry/format-contract-registry.yaml`
   (`review_verdict`, `reviewed_contract_sha256`) and evidence under the run's taskcards dir

## Mandatory Validations

- **files_not_summaries**: evidence shows actual store/report reads
- **verdict_hash_bound**: verdict recorded against the contract body's sha256
- **repairs_are_machinery**: repair instructions target packs/policy/facts/findings, never contract bodies

## Required Inputs

| Field | Description |
|---|---|
| `format_id` | Lowercase format identifier with a compiled contract |

## Allowed Paths

- registry/format-contract-registry.yaml (write), evidence dirs (write); all L30 stores/reports (read)

## Forbidden Paths

- shared/format-contracts/{fmt}.yaml (write — V240); src/**; plans/from_chat/** as content source

## Stop Conditions

- REJECT verdict: repairs become reopened taskcards in the same sprint (reroute rule)

## Output Format

Verdict block (ACCEPT/ACCEPT_WITH_REPAIRS/REJECT) + finding list + hash binding.

## Idempotency Contract

Same contract hash -> same verdict basis; re-review overwrites the registry verdict fields.

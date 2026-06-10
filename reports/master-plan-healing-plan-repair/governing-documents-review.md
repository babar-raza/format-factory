# Governing Documents Review

**Sprint ID:** FORMAT-FACTORY-MASTER-PLAN-GOVERNANCE-REVIEW-HEALING-PLAN-001
**Date:** 2026-06-10
**Source:** docs/governance/ (29 files)

## Review Summary

All 29 governance documents were reviewed. None have contradictions with the product-first model. The only master-plan contradiction is between the AI platform layer backlog (Section 39) and ai-authority-boundary.md, which is resolved by archiving Section 39.

## Documents Reviewed

| # | File | Accuracy | Contradictions | Action |
|---|------|----------|---------------|--------|
| 1 | product-first-operating-model.md | CURRENT | None | keep |
| 2 | four-stream-operating-model.md | CURRENT | None | keep |
| 3 | ai-authority-boundary.md | CURRENT | §39 conflicts | keep |
| 4 | external-tool-architecture.md | CURRENT | None | keep |
| 5 | lane-definitions.md | CURRENT | None | keep |
| 6 | acceleration-definition.md | CURRENT | None | keep |
| 7 | autonomous-supervisor-role.md | CURRENT | None | keep |
| 8 | mainstream-product-output-floor.md | CURRENT | None | keep |
| 9 | machinery-success-criteria.md | CURRENT | None | keep |
| 10 | ruflo-runtime-governance.md | CURRENT | None | keep |
| 11 | superpowers-skill-intake.md | CURRENT | None | keep |
| 12 | ghidra-mcp-compliance-gate.md | CURRENT | None | keep |
| 13 | mainstream-poc-mega-train.md | CURRENT | None | keep |
| 14 | independent-authority-layers.md | CURRENT | None | keep |
| 15 | specification-authority-layer.md | CURRENT | None | keep |
| 16 | evidence-handling-principles.md | CURRENT | None | keep |
| 17 | requirement-capability-authority-layer.md | CURRENT | None | keep |
| 18 | autonomous-stop-reason-policy.md | CURRENT | None | keep |
| 19 | human-gate-classification-policy.md | CURRENT | None | keep |
| 20 | agent-owned-review-policy.md | CURRENT | None | keep |
| 21 | autonomous-execution-contract.md | CURRENT | None | keep |
| 22 | proof-authority-policy.md | CURRENT | None | keep |
| 23 | execution-method-taxonomy.md | CURRENT | None | keep |
| 24 | repeatability-contract.md | CURRENT | None | keep |
| 25 | idempotency-contract.md | CURRENT | None | keep |
| 26 | product-mutation-taskcard-state-machine.md | CURRENT | None | keep |
| 27 | legacy-manual-backfill-policy.md | CURRENT | None | keep |
| 28 | autonomy-default-routing-policy.md | CURRENT | None | keep |
| 29 | spec-to-product-machinery-routing.md | CURRENT | None | keep |

## Key Finding

The governance documents are in good shape. All 29 are CURRENT and consistent with the product-first operating model. The master plan is the stale component, not the governance layer.

The healed master plan should reference these governance documents as canonical authorities for their respective domains, with the master plan providing only a brief canonical summary of each.

## New Governance Documents Needed (in execution)

1. **docs/governance/master-plan-canonical-source-map.md** — Defines which document owns each truth domain
2. **docs/governance/master-plan-sync-policy.md** — Defines no-append-only update rules and freshness mechanism

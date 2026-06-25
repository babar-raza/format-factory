# Evidence Bundle Index
# Sprint: ff-machinery-readiness-audit-20260625
# Generated: 2026-06-25

## Bundle Identity

| Field | Value |
|---|---|
| Sprint ID | ff-machinery-readiness-audit-20260625 |
| Evidence root | reports/machinery-readiness-audit-20260625/ |
| Git HEAD at audit start | c7694fe4 |
| Branch | main |
| Audit type | INVESTIGATION_SPRINT |
| Product source changes | NONE |
| Machinery source changes | NONE |
| Verdict | READY_AFTER_TARGETED_MACHINERY_REPAIRS |

## Complete Artifact List

| # | File | Lane | Type | Size (B) | SHA-256 (16-char) |
|---|---|---|---|---|---|
| 01 | 01-sprint-overview.md | A | investigation | 4096 | a0e7aa55d3f0cf3c |
| 02 | 02-preflight-state.md | A | investigation | 5508 | 24c5321e260c6869 |
| 03 | 03-qname-schema-audit.md | B | investigation | 11814 | 7b7ac2b310ec8b3f |
| 04 | 04-per-product-qname-compliance.yaml | B | compliance_matrix | 19891 | 0d1d3b84ab35735b |
| 05 | 05-src-source-quality-review.md | C | investigation | 12634 | 05373a6970534e6d |
| 06 | 06-skill-inventory-and-gaps.md | D | investigation | 9135 | 4547e426709b5457 |
| 07 | 07-sal-audit.md | E | investigation | 9118 | c586aa2a5be40b6d |
| 08 | 08-capability-layer-audit.md | F | investigation | 7700 | 1311056c17a5aa6f |
| 09 | 09-downstream-layer-audit.md | G | investigation | 8371 | 83c680337b748524 |
| 10 | 10-autonomous-supervisor-audit.md | H | investigation | 9443 | 723a0942f10858a8 |
| 11 | 11-lane-separation-and-collision-risk.md | H | investigation | 11741 | 7e2f1593b6210b22 |
| 12 | 12-backfill-facility-design.md | I | design | 11162 | f96895840365834a |
| 13 | 13-gate11-readiness-review.md | J | investigation | 6849 | a5bc74a43ed9e153 |
| 14 | 14-product-deepening-readiness-plan.md | J | plan | 8342 | 3388a01eb634ebd4 |
| 15 | 15-system-gap-matrix.yaml | All | gap_matrix | 13240 | 9cc23b9803038808 |
| 16 | 16-taskcards.yaml | All | taskcards | 19424 | f9723b50fe2341a0 |
| 17 | 17-machinery-repair-plan.md | All | plan | 8409 | b9ff7108dc3adba3 |
| 18 | 18-product-deepening-execution-plan.md | J | plan | 7393 | 8116020a3075e4cf |
| 19 | 19-next-agent-execution-prompt.md | All | prompt | 6566 | 2062eacae02499b7 |
| 20 | 20-evidence-index.md | All | index | — | — |
| 21 | 21-final-verdict.md | All | verdict | — | — |
| 22 | 22-evidence-bundle-index.md | All | bundle_index | — | THIS FILE |

**Total: 22 artifacts**

## Bundle Contents by Type

| Type | Count | Artifacts |
|---|---|---|
| investigation | 10 | 01, 02, 03, 05, 06, 07, 08, 09, 10, 11 |
| compliance_matrix | 2 | 04, 15 |
| design | 1 | 12 |
| plan | 3 | 14, 17, 18 |
| taskcards | 1 | 16 |
| prompt | 1 | 19 |
| index | 1 | 20 |
| verdict | 1 | 21 |
| bundle_index | 1 | 22 |

## Primary Read Evidence (Not In Bundle — Read From Repository)

These files were directly inspected to produce the audit:

```
tools/supervisor/autonomous_task_generator.py     (lines 1-200; _EXPANSION_GOALS proof)
tools/supervisor/autonomous_cycle.py              (lines 1-200; 19-state machine; SUP-GAPs)
tools/supervisor/product_feature_factory.py       (lines 1-100; FeatureFactory patterns)
src/python/csv/csv_parser.py                      (lines 1-120; RFC 4180 state machine)
src/python/ndjson/ndjson_codec.py                 (lines 32-80; authority-only pattern)
src/python/fods/__init__.py                       (full; __all__ pattern)
shared/qname-registry/fods.yaml                   (full; Gold Standard registry)
.supervisor/skill-registry.yaml                   (lines 1-80; 35+ skill inventory)
AGENTS.md                                         (lines 1-150; lane policy)
.local/supervisor/continuation-signal.json        (full; current state)
reports/supervisor/session-resume.md              (full; last sprint state)
reports/supervisor/approval-gates.md              (full; current gates)
product-capability-matrix/poc-targets.yaml        (lines 1-60; Gate 11 evidence)
registry/product-deepening-ledger.yaml            (lines 1-80; format levels)
docs/audits/python-qname-backfill-inventory.csv   (lines 1-50; backfill scope)
```

## Governance Classification

| Field | Value |
|---|---|
| Work type | INVESTIGATION_SPRINT |
| Changed files (product source) | 0 |
| Changed files (machinery source) | 0 |
| Changed files (evidence/reports) | 22 (new; this audit dir) |
| Tests run | 0 (investigation only; no code changes) |
| Tests modified | 0 |
| TC-GUARD-001 applicable | NO (no product/machinery items declared) |
| Skill invocations | 0 (investigation only) |

## Reproduction Instructions

To reproduce this audit (re-read all source files and regenerate findings):

1. Verify git HEAD = c7694fe4 (or note delta)
2. Read all 15 primary evidence files listed above
3. Check continuation signal at `.local/supervisor/continuation-signal.json`
4. Compare SAL tool counts via:
   ```
   ls tools/supervisor/sal_*.py | wc -l
   ls .local/spec-cache/sal-facts-*.json | wc -l
   ```
5. Run gap-ledger item count:
   ```
   python -c "import json; d=json.load(open('reports/capability-layer/gap-ledger.json')); print(len(d))"
   ```
6. Verify _EXPANSION_GOALS presence:
   ```
   grep -c "_EXPANSION_GOALS" tools/supervisor/autonomous_task_generator.py
   ```
7. Verify overclaim detector is not wired:
   ```
   grep "overclaim" tools/supervisor/autonomous_cycle.py | head -5
   ```

All 4 BLOCKER gaps will be confirmed by steps 4-7 above.

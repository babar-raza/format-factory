# Evidence Index
# Sprint: ff-machinery-readiness-audit-20260625
# Generated: 2026-06-25

## Audit Evidence Directory

All 22 artifacts are in `reports/machinery-readiness-audit-20260625/`.

## Artifact Manifest

| # | File | Lane | Size | SHA-256 (prefix) | Status |
|---|---|---|---|---|---|
| 01 | 01-sprint-overview.md | A | 4096 B | a0e7aa55d3f0cf3c | COMPLETE |
| 02 | 02-preflight-state.md | A | 5508 B | 24c5321e260c6869 | COMPLETE |
| 03 | 03-qname-schema-audit.md | B | 11814 B | 7b7ac2b310ec8b3f | COMPLETE |
| 04 | 04-per-product-qname-compliance.yaml | B | 19891 B | 0d1d3b84ab35735b | COMPLETE |
| 05 | 05-src-source-quality-review.md | C | 12634 B | 05373a6970534e6d | COMPLETE |
| 06 | 06-skill-inventory-and-gaps.md | D | 9135 B | 4547e426709b5457 | COMPLETE |
| 07 | 07-sal-audit.md | E | 9118 B | c586aa2a5be40b6d | COMPLETE |
| 08 | 08-capability-layer-audit.md | F | 7700 B | 1311056c17a5aa6f | COMPLETE |
| 09 | 09-downstream-layer-audit.md | G | 8371 B | 83c680337b748524 | COMPLETE |
| 10 | 10-autonomous-supervisor-audit.md | H | 9443 B | 723a0942f10858a8 | COMPLETE |
| 11 | 11-lane-separation-and-collision-risk.md | H | 11741 B | 7e2f1593b6210b22 | COMPLETE |
| 12 | 12-backfill-facility-design.md | I | 11162 B | f96895840365834a | COMPLETE |
| 13 | 13-gate11-readiness-review.md | J | 6849 B | a5bc74a43ed9e153 | COMPLETE |
| 14 | 14-product-deepening-readiness-plan.md | J | 8342 B | 3388a01eb634ebd4 | COMPLETE |
| 15 | 15-system-gap-matrix.yaml | All | 13240 B | 9cc23b9803038808 | COMPLETE |
| 16 | 16-taskcards.yaml | All | 19424 B | f9723b50fe2341a0 | COMPLETE |
| 17 | 17-machinery-repair-plan.md | All | 8409 B | b9ff7108dc3adba3 | COMPLETE |
| 18 | 18-product-deepening-execution-plan.md | J | 7393 B | 8116020a3075e4cf | COMPLETE |
| 19 | 19-next-agent-execution-prompt.md | All | 6566 B | 2062eacae02499b7 | COMPLETE |
| 20 | 20-evidence-index.md | All | — | — | THIS FILE |
| 21 | 21-final-verdict.md | All | — | — | BEING WRITTEN |
| 22 | 22-evidence-bundle-index.md | All | — | — | BEING WRITTEN |

**Total artifacts: 22**
**Total size (19 complete): ~196 KB**

## Investigation Coverage

| Investigation Question | Artifact(s) | Answered? |
|---|---|---|
| Q1: Is product code professional or generated? | 05 | YES — 7/10; not generated |
| Q2: QName compliance per format? | 03, 04 | YES — 20+ format matrix |
| Q3: SAL pipeline status? | 07 | YES — 3 active, 17 dormant |
| Q4: Capability layer connected to tasks? | 08, 09 | YES — DISCONNECTED (advisory_only=true) |
| Q5: Feature compiler implemented? | 08 | YES — Phase 2 NOT STARTED |
| Q6: Are skills repeatable? | 06 | YES — 35+ skills; /add-python-api STRONG |
| Q7: Is lane ordering enforced? | 10, 11 | YES — prompt-only only |
| Q8: Overclaim detection wired? | 10 | YES — NOT WIRED |
| Q9: Backfill covers all formats? | 12 | YES — 1/20 formats (ABW only) |
| Q10: Gate 11 status? | 13 | YES — 5 formats TECHNICALLY READY |
| Q11: Product deepening path? | 14, 18 | YES — wave sequence defined |
| Q12: Gap matrix complete? | 15 | YES — 19 gaps, 4 BLOCKER |
| Q13: Taskcards for all 14 groups? | 16 | YES — 19 taskcards in 14 groups |
| Q14: Repair sequence? | 17 | YES — 5-step ordered repair |
| Q15: Next agent prompt? | 19 | YES — complete with exact paths |

## Primary Evidence Files (Not In Audit Dir)

These files were READ to produce audit findings but live elsewhere:

| Evidence File | Read For | Artifact |
|---|---|---|
| `.local/spec-cache/sal-facts-*.json` | SAL fact counts | 07 |
| `tools/supervisor/autonomous_task_generator.py` | _EXPANSION_GOALS proof | 08, 09 |
| `tools/supervisor/autonomous_cycle.py` | 19-state machine; SUP-GAPs | 10 |
| `tools/supervisor/product_feature_factory.py` | FeatureFactory never called | 09 |
| `src/python/csv/csv_parser.py` | Source quality rating | 05 |
| `src/python/ndjson/ndjson_codec.py` | Authority-only pattern | 05 |
| `shared/qname-registry/fods.yaml` | Gold standard QName registry | 03 |
| `.supervisor/skill-registry.yaml` | 35+ skills audit | 06 |
| `AGENTS.md` | Lane policy authority | 10, 11 |
| `product-capability-matrix/poc-targets.yaml` | Gate 11 status | 13 |
| `registry/product-deepening-ledger.yaml` | Format readiness levels | 14 |
| `docs/audits/python-qname-backfill-inventory.csv` | Backfill scope | 12 |

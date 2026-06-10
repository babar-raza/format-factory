# Iteration 4 Final Summary

**Train:** FORMAT-FACTORY-AUTONOMOUS-CONTROL-HARDENED-UNIFIED-POC-TRAIN-001
**Iteration:** 4
**Completed:** 2026-06-05

## Lanes Executed

| Lane | Target | Gap | Tests | Status |
|------|--------|-----|-------|--------|
| lane-017 | DIF | write_dif roundtrip | 10/10 | COMPLETED |
| lane-018 | FODS | CSV export dogfood sample | 32/32 | COMPLETED |
| lane-019 | FODT | Markdown export dogfood sample | 24/24 | COMPLETED |
| lane-020 | Netpbm | Save pipeline proof | sample output | COMPLETED |

## Key Achievements

1. **DIF write_dif implemented** — `src/python/dif/dif_parser.py` extended with `write_dif()`. Full CRLF-safe roundtrip. 10/10 tests pass including dogfood pipeline (write→probe→parse→csv).

2. **FODS CSV physical sample** — `sheet1-export.csv` produced from real FODS fixture. ExportSheetToCsvFile dogfood proof confirmed (32/32 tests).

3. **FODT Markdown physical sample** — `headings-and-list.md` produced from real FODT fixture. ExportToMarkdownFile dogfood proof confirmed (24/24 tests).

4. **Netpbm pipeline sample** — PGM create→cross-draw→save→readback verified. `cross-pipeline.pgm` produced. center_pixel=200, verify_pass=true.

## Proof Artifacts

- Source diffs: `iteration-004/source-diffs/iteration-004-dif.diff` (83 lines)
- Raw logs: `iteration-004/raw-logs/dif-r117-*.log`, `fods-r117-tests.log`, `fodt-r117-tests.log`
- Sample outputs: `iteration-004/sample-outputs/{dif,fods,fodt,netpbm}/`
- Capability deltas: `iteration-004/capability-delta-proposals/{dif,fods,fodt,netpbm}.yaml`
- Proof graph: `iteration-004/proof-graph/{nodes.jsonl,edges.jsonl,coverage-report.json}`
- Product code ledger: R117-DIF-WRITE-DIF-ROUNDTRIP added

## POC Readiness After Iteration 4

- commercial_targets: FODS PASS, FODT PASS, Netpbm PASS
- foss_targets: ZST PASS, Python_Netpbm PASS, SYLK PASS, DIF PARTIAL_PASS
- foss_pass_count: 3 (minimum met)
- all_commercial_pass: true
- sample_outputs_exist_where_required: NOW TRUE
- capability_deltas_proposed: NOW TRUE
- closure_criteria_met: FALSE (spec_context_or_fallback still incomplete)

## Remaining Gaps for Closure

1. `spec_context_or_fallback_attached` — formal spec reference for each readiness claim
2. `transcripts_exist` — partial (skill transcripts generated but not all formal)
3. DIF `poc_targets_reconsider_decision` — ON_HOLD entry in poc-targets.yaml should be reconsidered given write_dif now exists

## Continuation

POC_READY is still FALSE → train continues to Iteration 5.

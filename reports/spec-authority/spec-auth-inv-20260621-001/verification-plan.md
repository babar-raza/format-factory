# Specs Authority Layer — Verification Plan
**Run ID:** spec-auth-inv-20260621-001
**Date:** 2026-06-21

---

## Gate V0 — Baseline (before any repair)

| # | Check | Command | Expected Result | Evidence File | Blocking |
|---|-------|---------|-----------------|---------------|---------|
| V0.1 | SAL facts exist | `ls .local/sal-output/sal-facts-latest.json` | File exists, non-empty | `v0-sal-exists.txt` | YES |
| V0.2 | Authority lifecycle tests pass | `.venv/Scripts/pytest tests/ai/test_authority_lifecycle.py -v` | 7/7 PASS | `v0-auth-lifecycle.txt` | YES |
| V0.3 | SAL wiring tests pass | `.venv/Scripts/pytest tests/capability_layer/test_sal_capability_wiring.py -v` | 6/6 PASS | `v0-sal-wiring.txt` | YES |
| V0.4 | Confirm dogfood tests failing | `.venv/Scripts/pytest tests/python/dogfood/test_dogfood_fods_fodt_sal_fact_ndjson_export.py -v` | 6 FAIL expected | `v0-dogfood-baseline.txt` | NO (baseline only) |
| V0.5 | Confirm no source_id in facts | `python -c "import json; d=json.load(open('.local/sal-output/sal-facts-latest.json')); results=d['results']; f=results[0]['spec_facts'][0]; print('source_id:', f.get('source_id','MISSING'))"` | `source_id: MISSING` | `v0-no-source-id.txt` | NO (baseline) |
| V0.6 | Count sources with sha256 | `python -c "import json; lines=[json.loads(l) for l in open('.local/spec-source-registry/sources.jsonl')]; print(sum(1 for l in lines if l.get('sha256_snapshot')))"` | `1` | `v0-sha256-count.txt` | NO (baseline) |

---

## Gate V1 — After MVR-1+MVR-2 (bootstrap separation + dogfood fix)

| # | Check | Command | Expected Result | Evidence File | Blocking |
|---|-------|---------|-----------------|---------------|---------|
| V1.1 | Bootstrap facts marked correctly | Inspect sal-facts-latest.json for facts without workbench | `fact_status: "bootstrap_only"` on hardcoded facts | `v1-bootstrap-status.txt` | YES |
| V1.2 | Workbench facts carry source_id | Inspect FODT/ZST/Netpbm facts in sal output | `source_id` field populated for formats with workbench | `v1-source-id-present.txt` | YES |
| V1.3 | Dogfood tests pass | `.venv/Scripts/pytest tests/python/dogfood/test_dogfood_fods_fodt_sal_fact_ndjson_export.py -v` | 0 FAIL (was 6) | `v1-dogfood-pass.txt` | YES |
| V1.4 | No regression on authority lifecycle | `.venv/Scripts/pytest tests/ai/test_authority_lifecycle.py tests/capability_layer/test_sal_capability_wiring.py -v` | 13/13 PASS | `v1-no-regression.txt` | YES |
| V1.5 | SAL output has per-format files | `ls .local/sal-output/sal-facts-fods.json .local/sal-output/sal-facts-fodt.json` | Both exist, parseable JSON | `v1-per-format-files.txt` | YES |

---

## Gate V2 — After MVR-3 (ZST spec acquisition)

| # | Check | Command | Expected Result | Evidence File | Blocking |
|---|-------|---------|-----------------|---------------|---------|
| V2.1 | ZST sha256_snapshot populated | `python -c "import json; lines=[json.loads(l) for l in open('.local/spec-source-registry/sources.jsonl')]; zst=[l for l in lines if l.get('format_id')=='zst'][0]; print(zst.get('sha256_snapshot'))"` | Non-null SHA-256 string | `v2-zst-sha256.txt` | YES |
| V2.2 | ZST spec-index.yaml stale=false | `cat .local/spec-cache/zst/rfc8878/spec-index.yaml` | `stale: false`, sha256 matches file | `v2-zst-spec-index.txt` | YES |
| V2.3 | ZST text normalization exists | `ls .local/spec-cache/zst/rfc8878/text.txt` | File exists, size > 50KB | `v2-zst-text.txt` | YES |
| V2.4 | ZST fact verification runs | `python tools/specification-authority-layer/run_fact_verification.py --format zst` | Exit 0; verified ≥12/15 | `v2-zst-verification.txt` | YES |
| V2.5 | ZST facts in SAL have source_id | Re-run sal_master_runner.py; inspect ZST entries | `source_id: "SPEC-ZST-RFC8878"` | `v2-zst-sal-source-id.txt` | YES |

---

## Gate V3 — After FPR-6 (FODS workbench coverage campaign)

| # | Check | Command | Expected Result | Evidence File | Blocking |
|---|-------|---------|-----------------|---------------|---------|
| V3.1 | FODS effective coverage ≥60% | `python tools/specification-authority-layer/fact_coverage_report.py --format fods` | fods.coverage_percent ≥ 60.0 | `v3-fods-coverage.txt` | YES |
| V3.2 | FODS pending facts reduced | Count pending in workbench YAML | Pending ≤ 80 (from 201) | `v3-fods-pending.txt` | YES |
| V3.3 | Zero regression on passing FODS tests | `.venv/Scripts/pytest tests/python/fods/ -v --tb=short` | Same or more passing | `v3-fods-tests.txt` | YES |

---

## Gate V4 — After FPR-3 (TC-GUARD-001 second-order check)

| # | Check | Command | Expected Result | Evidence File | Blocking |
|---|-------|---------|-----------------|---------------|---------|
| V4.1 | Invalid FACT-ID blocked | Create test declaration with `spec_fact_refs: FAKE-999`; run autonomous_cycle | Rework item created: fact FAKE-999 not in verified-facts | `v4-fake-fact-blocked.txt` | YES |
| V4.2 | Bootstrap-only FACT-ID warns but does not block | Declaration with `spec_fact_refs: FODS-FACT-001` (bootstrap_only fact) | Warning (not block) until threshold met | `v4-bootstrap-warn.txt` | YES |
| V4.3 | Valid verified FACT-ID passes | Declaration with `spec_fact_refs: FACT-ZST-001` (after V2) | No rework item for this check | `v4-valid-passes.txt` | YES |
| V4.4 | Guard tests still pass | `.venv/Scripts/pytest tests/supervisor/test_tc_guard_001_enforce.py -v` | All existing tests pass | `v4-guard-tests.txt` | YES |

---

## Gate V5 — Pilot Acquisition Rerun (Proof of Authority Chain)

Full pilot rerun with ZST (see pilot-rerun-plan.md).

| # | Check | Command | Expected Result | Evidence File | Blocking |
|---|-------|---------|-----------------|---------------|---------|
| V5.1 | ZST spec text queried deterministically | `python tools/spec-normalize/query_normalized_spec.py --format zst --section 3.1` | Returns section text with source hash | `v5-zst-tier1-query.txt` | YES |
| V5.2 | ZST fact FACT-ZST-001 verified against text | Inspect verified-facts-review.yaml | `verification_status: verified`, text_fragment matches | `v5-zst-fact-verified.txt` | YES |
| V5.3 | ZST product source references FACT-ZST-001 | `grep -n "FACT-ZST-001" src/python/zst/zst_codec.py` | At least 1 match | `v5-zst-product-ref.txt` | YES |
| V5.4 | ZST test exercises the fact-backed behavior | `python tools/traceability/fact_product_linker.py --format zst` | FACT-ZST-001 → zst_codec.py → test file | `v5-zst-traceability.txt` | YES |
| V5.5 | ZST rerun produces same facts | Run pilot twice; compare fact IDs and sha256 | Identical output (deterministic) | `v5-zst-rerun-compare.txt` | YES |
| V5.6 | ZST stale detection fires on hash change | Modify sha256 in spec-index.yaml; run autonomous_cycle | `derived_artifacts_stale: true` logged | `v5-zst-stale.txt` | YES |

---

## Gate V6 — Regression Suite

| # | Check | Command | Expected Result | Evidence File | Blocking |
|---|-------|---------|-----------------|---------------|---------|
| V6.1 | Full SAL suite | `.venv/Scripts/pytest tests/ai/ tests/capability_layer/ tests/python/dogfood/ -v` | 0 FAIL | `v6-sal-suite.txt` | YES |
| V6.2 | No new source structure violations | Python inline validator script from CLAUDE.md | No new violations | `v6-governance.txt` | YES |
| V6.3 | Fact coverage summary updated | `cat .local/sal-output/fact-coverage-summary.md` | FODS ≥60%, ZST 100%, FODT 100% | `v6-coverage-summary.txt` | YES |
| V6.4 | SAL facts valid JSON | `python -c "import json; json.load(open('.local/sal-output/sal-facts-latest.json'))"` | Exit 0 | `v6-json-valid.txt` | YES |

---

## Failure Interpretation

| Failure | Interpretation |
|---------|---------------|
| V1.3 dogfood still failing | per-format file output not implemented correctly |
| V1.2 no source_id on FODT facts | workbench YAML not being loaded by sal_master_runner.py |
| V2.4 ZST verification <12/15 | RFC text normalization issue; check chunk window size |
| V3.1 FODS coverage <60% | Text search thresholds too strict; calibrate `--calibrate` first |
| V4.1 invalid FACT-ID not blocked | Lookup against sal-facts-latest.json not wired correctly |
| V5.5 non-identical rerun | Non-deterministic element in pipeline (timestamps, sort order) |
| V5.6 stale not detected | Hash comparison not added to autonomous_cycle.py |

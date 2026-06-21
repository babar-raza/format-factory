# Specs Authority Layer — Integration Matrix
**Run ID:** spec-auth-inv-20260621-001
**Date:** 2026-06-21

---

| # | Integration Point | Expected Behavior | Actual Behavior | Evidence Paths | Enforcement Level | Failure Behavior | Current Risk | Required Repair | Priority |
|---|-------------------|-------------------|-----------------|----------------|-------------------|------------------|--------------|-----------------|----------|
| 1 | **Format acquisition planning** | Acquisition pack spec-evidence.md must cite source URL, SHA-256, and section IDs before Stage 2+ work begins | FODS and FODT have spec-evidence.md. Template exists. Most other formats lack populated spec-evidence.md or have null source_hash | `acquisition-packs/fods/spec-evidence.md`, `acquisition-packs/_template/spec-evidence.md` | ADVISORY_ONLY | Agent proceeds without spec evidence if not blocked | HIGH — formats acquired without verified spec citation | Require non-null source_hash in acquisition pack before Gate 4+ | P1 |
| 2 | **Parser implementation prompts** | Prompts must cite verified spec facts (FACT-IDs with source backing) | Product source has FACT-ID comments (FODS, FODT, ZST, ABW, FODG) but these reference hardcoded templates, not verified spec text | `src/python/fods/neutral_model.py`, `src/python/zst/zst_codec.py` | ADVISORY_ONLY | No enforcement; comments accepted as-is | HIGH — fact comments may not match actual spec text | Wire spec_fact_refs to verified-facts-review.yaml lookup at declaration time | P1 |
| 3 | **Writer/saver implementation prompts** | Same-format save requires spec facts for output format validation | No evidence of spec fact requirement for writer prompts specifically | `acquisition-packs/_families/odf-flat/playbook.yaml` | MISSING | No requirement enforced | HIGH | Add spec fact requirement to add-same-format-writer-feature skill | P2 |
| 4 | **Same-format save requirements** | Save output must preserve structure validated against spec facts | save/export tested but spec fact citation missing | `tools/spec-normalize/export_sample_requirements.py` (not wired) | MISSING | No blocking | HIGH | Wire export_sample_requirements.py to acquisition stage | P2 |
| 5 | **Object model design** | Neutral model classes must map to spec QNames (spec_qname field) | FODS/FODT neutral model has some FACT-ID docstrings; QName registry exists for FODT | `src/python/fodt/`, `tests/python/fodt/test_spec_qname_stubs.py` | PARTIALLY_ENFORCED | TC-GUARD-001 blocks declarations without spec_fact_refs | MEDIUM | Extend spec_qname to all neutral model classes for all 15+ formats | P2 |
| 6 | **Export/dogfooding design** | Dogfood tests should validate SAL facts are round-trippable | 6 dogfood SAL tests FAIL (JSONDecodeError — format-specific sal-facts files empty) | `tests/python/dogfood/test_dogfood_fods_fodt_sal_fact_ndjson_export.py` | CLAIMED_BUT_NOT_PROVEN | Tests fail silently — 6 FAILED | HIGH — dogfood proof broken | Fix format-specific sal-facts files or change test expectation | P1 |
| 7 | **Product task selector** | Task generator should prefer gaps with spec_facts populated | `autonomous_task_generator.py` has `require_spec_facts=False` (disabled) | `tools/supervisor/autonomous_task_generator.py:1607` | MISSING | Tasks selected without spec backing | HIGH | Enable `require_spec_facts=True` after workbench coverage improves | P3 |
| 8 | **Autonomous queue/orchestrator** | SAL regeneration triggered daily; stale detection works | TC-SAL-REGEN-001 in autonomous_cycle.py step 0a runs every 7 days. Non-blocking — failure is logged and skipped | `tools/supervisor/autonomous_cycle.py:247-298` | PARTIALLY_ENFORCED | Non-blocking — failure is silently skipped | MEDIUM — stale SAL not caught | Make stale SAL a WARN_BLOCK; at minimum log clearly | P3 |
| 9 | **Supervisor review** | Supervisor grader should verify spec_fact_refs point to verified facts | TC-GUARD-001 checks for spec_fact_refs presence but NOT that referenced facts have source_id or verified status | `tools/supervisor/autonomous_cycle.py:430-485`, `tools/supervisor/grade_declared_work.py` | PARTIALLY_ENFORCED | Declaration blocked if spec_fact_refs missing — but unverified facts pass | HIGH — hollow spec_fact_refs accepted | Add second-order check: referenced fact must exist in verified-facts-review.yaml | P1 |
| 10 | **Evidence declaration** | Evidence bundle must NOT include raw spec text; must cite spec facts with provenance | Evidence bundles include spec-sha256-verify files; no raw spec text. But fact provenance (source_id) missing from facts | `.local/bundle-metadata-run042/spec-sha256-verify-run042.txt`, `tools/evidence/build_evidence_bundle.py` | PARTIALLY_ENFORCED | Evidence accepted without source_id on facts | MEDIUM | Add evidence validator check: spec_fact_refs must resolve to facts with source_id | P2 |
| 11 | **Proof graph** | Proof graph should link spec fact → requirement → implementation → test | No proof graph connecting these layers exists | MISSING | MISSING | No enforcement | CRITICAL — no traceability proof | Design and implement proof graph spec | P1 |
| 12 | **Product ledger** | Product ledger should record spec authority level per format | Capability map has SAL enrichment but facts lack source_id | `reports/capability-layer/commercial-capability-map.json` | ADVISORY_ONLY | Ledger records formats without spec backing | HIGH | Add spec_authority_level field to ledger derived from verified fact count | P2 |
| 13 | **Test generation** | Tests should reference spec facts (FACT-IDs) to prove spec coverage | FODS/FODT/ZST have some spec-parity deepening tests; most tests have no spec linkage | `tests/python/deepening/test_r1221_fods_spec_parity_deepening.py`, `tests/python/deepening/test_r1222_fodt_spec_parity_deepening.py` | PARTIALLY_ENFORCED | Tests generated without spec linkage | MEDIUM | Add spec_fact_ref metadata to deepening test templates | P3 |
| 14 | **Final acceptance gates** | Gate 4+ (spec acquisition) requires confirmed spec cache entry | Gate 4 enforced via acquisition pack spec-evidence.md review; not runtime-verified | `registry/format-registry.yaml`, acquisition pack playbooks | PARTIALLY_ENFORCED | Gate 4 can be approved based on spec-evidence.md contents alone | MEDIUM | Automate gate 4 check: require sha256 in spec-index.yaml | P2 |
| 15 | **Package/release readiness gates** | Gate 11 commercial release requires spec parity evidence | FODS/FODT at Gate 11 pending. Spec parity checks (P1-P11) don't explicitly require verified fact count | `reports/gate11/fods-gate11-readiness-packet.md` | ADVISORY_ONLY | Release approved without verified fact coverage threshold | HIGH | Add verified_fact_count_min_threshold to Gate 11 checklist | P2 |

---

## Summary Enforcement Ratings

| Integration Point | Rating |
|-------------------|--------|
| Format acquisition planning | ADVISORY_ONLY |
| Parser implementation prompts | ADVISORY_ONLY |
| Writer/saver prompts | MISSING |
| Same-format save requirements | MISSING |
| Object model design | PARTIALLY_ENFORCED |
| Export/dogfooding | CLAIMED_BUT_NOT_PROVEN |
| Product task selector | MISSING |
| Autonomous queue/orchestrator | PARTIALLY_ENFORCED |
| Supervisor review | PARTIALLY_ENFORCED |
| Evidence declaration | PARTIALLY_ENFORCED |
| Proof graph | MISSING |
| Product ledger | ADVISORY_ONLY |
| Test generation | PARTIALLY_ENFORCED |
| Final acceptance gates | PARTIALLY_ENFORCED |
| Package/release gates | ADVISORY_ONLY |

**Overall integration rating: PARTIAL**
- ENFORCED: 0 out of 15
- PARTIALLY_ENFORCED: 6 out of 15
- ADVISORY_ONLY: 4 out of 15
- CLAIMED_BUT_NOT_PROVEN: 1 out of 15
- MISSING: 4 out of 15

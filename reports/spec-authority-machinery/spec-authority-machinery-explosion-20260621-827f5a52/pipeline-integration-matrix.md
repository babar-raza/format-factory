# Spec Authority Machinery — Pipeline Integration Matrix

**Run ID:** `spec-authority-machinery-explosion-20260621-827f5a52`
**Date:** 2026-06-21

---

| # | Stage | File/Component | Actual Behavior | Severity | Root Cause ID |
|---|-------|----------------|-----------------|----------|---------------|
| 1 | Spec acquisition — FODS | `.local/spec-cache/fods/1.3/normalized/text.txt` | PASS — normalized text exists; source for extraction | LOW | — |
| 2 | Spec acquisition — Gnumeric | `.local/spec-cache/gnumeric/v10/spec-index.yaml` | FAIL — `normalized_text_cached: false`; metadata only | HIGH | RCA-SPEC-ACQ-GNUMERIC |
| 3 | Spec acquisition — ABW | `.local/spec-cache/abw/awml-1.0/spec-index.yaml` | FAIL — DTD unreachable (ECONNREFUSED); no normalized text | HIGH | RCA-SPEC-ACQ-ABW |
| 4 | Spec acquisition — CSV/TSV/SYLK/DIF | spec-cache/... | FAIL — no workbench YAML; 0 SAL facts | HIGH | RCA-SPEC-ACQ-GENERIC |
| 5 | Workbench extraction — FODS | `verified-facts-review.yaml` (4,991 facts) | STRONG — 9,974 deterministic + 16 agent verifier methods | LOW | — |
| 6 | Workbench extraction — FODT | `fodt/*/workbench/verified-facts-review.yaml` | STRONG — 4,933 facts | LOW | — |
| 7 | Workbench extraction — ZST | `zst/*/workbench/verified-facts-review.yaml` | MODERATE — 94 facts | MEDIUM | RCA-ZST-WORKBENCH-DEPTH |
| 8 | Workbench extraction — FODP/FODG/ODS/ODT | workbench YAMLs | PASS — 1,066 facts each; acquisition chain undocumented | MEDIUM | RCA-FODFAM-CHAIN |
| 9 | Requirement packs — FODS | `requirement-packs/*.yaml` (3 files) | PARTIAL — exists; TC-0021 traceability review pending | MEDIUM | RCA-REQ-PACK-TC0021 |
| 10 | SAL emission — default mode | `sal_master_runner.py` (default) | MIXED — template + workbench facts merged; FODS: ~22 bootstrap-only in output | MEDIUM | RCA-SAL-DEFAULT-MODE |
| 11 | SAL emission — clean mode | `sal_master_runner.py --from-cache-only` | PASS — workbench-only; Gnumeric/ABW emit 0 (correct) | LOW | — (idempotency fix) |
| 12 | SAL output — daily file | `.local/sal-output/sal-facts-latest.json` | DEFAULT MODE — 14,284+ facts; template facts present in FODS | MEDIUM | RCA-SAL-DEFAULT-MODE |
| 13 | SAL fact field: source | per-fact `source` field | PASS — workbench facts have `source: "workbench_verified"` | LOW | — |
| 14 | SAL fact field: authority_level | per-fact field | ABSENT — field is `source` not `authority_level`; naming mismatch with plan | LOW | RCA-AUTH-LEVEL-NAMING |
| 15 | SAL output consumed by autonomous_cycle | `autonomous_cycle.py` reads SAL | FAIL — SAL NOT READ by autonomous_cycle | CRITICAL | RCA-SUPERVISOR-GATES-001 |
| 16 | GAP-INT-002 — format fact existence | `test_gap_int_002` FODS/FODT/ZST counts | PASS — FODS>=100, FODT>=100, ZST>=10 (all workbench) | LOW | — |
| 17 | GAP-INT-002 — source authority check | `source == workbench_verified` check | ABSENT — no such check; template facts also in SAL index | HIGH | RCA-GAP-INT-002-NO-SOURCE-CHECK |
| 18 | GAP-INT-002 — all source FACT-* refs | `test_total_fact_refs_across_product_source` | PASS — scans all Python source; checks all FACT-* refs in SAL | MEDIUM | (template facts in index weaken this) |
| 19 | GAP-INT-002 — Gnumeric/ABW fact tests | coverage for zero-fact formats | ABSENT — no test asserts Gnumeric/ABW == 0 facts | MEDIUM | RCA-GAP-INT-002-COVERAGE |
| 20 | Gap-ledger — ABW spec_facts | ABW 50 gaps | CLEAN — spec_facts: [] (stale magic IDs previously cleaned) | LOW | — (RESOLVED) |
| 21 | Gap-ledger — Gnumeric spec_facts | Gnumeric 36 gaps | CLEAN — spec_facts: [] | LOW | — (RESOLVED) |
| 22 | Gap-ledger — CSV spec_facts | CSV 58 gaps | STALE — 116 refs to FACT-CSV-001/002 not in SAL | MEDIUM | RCA-GAP-LEDGER-CSV-STALE |
| 23 | Gap-ledger — authority_level field | 0/958 entries | ABSENT — field never added | MEDIUM | RCA-GAP-LEDGER-NO-AUTH-LEVEL |
| 24 | TC-GUARD-001 | `autonomous_cycle.py` Step 2d3 | REAL BLOCK — requires gap_ledger_ref OR spec_fact_refs | LOW | — (RESOLVED) |
| 25 | TC-GUARD-001 — authority quality | checks gap authority quality | ABSENT — checks presence not quality; CSV stale gaps satisfy it | MEDIUM | RCA-TC-GUARD-AUTHORITY-QUALITY |
| 26 | V45 validator | format-prefixed class names | REAL BLOCK — blocks FodsXxx/FodtXxx outside Compat/ | LOW | — |
| 27 | V46 validator | skill_transcript requirement | WARN-ONLY — advisory; legacy items ungoverned | MEDIUM | RCA-V46-WARN-ONLY |
| 28 | V47 validator | spec_fact_refs field | REAL BLOCK — added in commit 3024f68c | LOW | — |
| 29 | Healing gate Lane 1 — SAL check | `check_system_healing_gate.py` | SHALLOW — checks `fods_facts_gte_10` not `workbench_verified_fact_count > 0` | MEDIUM | RCA-HEALING-GATE-DEPTH-001 |
| 30 | Healing gate — action queue | `action_queue_not_advisory` | FALSE — action queue still advisory; gate check passes but queue not enforced | MEDIUM | RCA-ACTION-QUEUE-ADVISORY |
| 31 | Healing gate — ADVISORY mode | gate verdict enforced? | ADVISORY — non-blocking; Step 1b is advisory only | MEDIUM | RCA-HEALING-GATE-ADVISORY |
| 32 | FODS spec stubs | `src/python/fods/spec/` (12 classes) | ARCHITECTURE ONLY — spec_fact_ref correct; not production parser | LOW | — (positive new addition) |
| 33 | QName registry | `shared/qname-registry/fods.yaml` | ACTIVE — 12 QNames; all status: architecture_only | LOW | — (positive new addition) |
| 34 | FODS Compat facades | `src/python/fods/Compat/` | ACTIVE — FodsCell/FodsDocument/FodsSheet etc. added commit 3024f68c | LOW | — |
| 35 | Req-pack traceability | FACT-FODS-NNN per req | UNVERIFIED — TC-0021 review pending; parser-requirements.yaml not verified per fact | MEDIUM | RCA-REQ-PACK-TC0021 |
| 36 | Evidence schema: authority_level | evidence-declaration.yaml | ABSENT — schema has no authority_level, spec_fact_refs required field | MEDIUM | RCA-EVIDENCE-SCHEMA-001 |
| 37 | FODS workbench fact FACT-FODS-006 | cited in table_cell.py spec stub | VERIFIED — FACT-FODS-006 EXISTS in SAL output (workbench_verified) | LOW | — (PASS) |
| 38 | SAL default mode template contamination | bootstrap_only facts in daily output | ACTIVE — ~22 bootstrap-only facts in FODS daily SAL output | HIGH | RCA-SAL-DEFAULT-MODE |

---

## Key Behavioral Gaps

### GAP-1: SAL not read by autonomous_cycle (CRITICAL)
The SAL pipeline is parallel/advisory. `autonomous_cycle.py` does not read `sal-facts-latest.json` as an enforcement gate. Spec authority facts have no direct effect on sprint gating.

### GAP-2: Default mode mixes template facts
`sal-facts-latest.json` is generated in default mode. Both bootstrap-only template facts and workbench-verified facts are in the fact index. GAP-INT-002 validates product source citations against this mixed index — a citation to a template fact (not workbench-verified) passes the test.

### GAP-3: No workbench_count gate
Healing gate Lane 1 checks `fods_facts_gte_10` (total facts >= 10). This passes even if all those facts are bootstrap-only template facts. The `workbench_verified_fact_count` field exists in SAL output per-format but is not checked by any gate.

### GAP-4: CSV stale gap-ledger refs
58 CSV gap entries cite FACT-CSV-001 and FACT-CSV-002. These IDs do not exist in SAL output (CSV has 0 workbench facts). TC-GUARD-001 accepts items citing these gaps without verifying the fact IDs are real.

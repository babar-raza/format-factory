# Spec Authority Machinery — Root Cause Explosion Matrix

**Run ID:** `spec-authority-machinery-explosion-20260621-827f5a52`
**Date:** 2026-06-21
**Total root causes: 21**

---

## CRITICAL

### RCA-SUPERVISOR-GATES-001
**Title:** autonomous_cycle.py does not read SAL output
**Status:** OPEN — STILL CRITICAL
**Root cause:** SAL pipeline was designed as a parallel advisory system. No integration with `autonomous_cycle.py` beyond the TC-GUARD-001 `gap_ledger_ref` check. SAL facts are computed but not used as a gating signal.
**Symptom:** A sprint can pass all autonomous gates (TC-GUARD-001, V45, V47, healing gate) even if the cited gap has 0 workbench-verified SAL facts.
**Impact:** Spec authority is advisory only. Any format with a gap_ledger_ref satisfies TC-GUARD-001 regardless of spec evidence depth.
**Repair:** At minimum, make autonomous_cycle.py read sal-facts-latest.json and emit an advisory per-format workbench_verified_fact_count warning. Ideally: block PRODUCT_SOURCE for formats with 0 workbench facts.
**Evidence:** `autonomous_cycle.py` grep: no `sal-facts-latest.json` reads; SAL import missing from cycle steps.

---

### RCA-SAL-DEFAULT-MODE
**Title:** SAL daily output (`sal-facts-latest.json`) generated in default mode, mixing template + workbench facts
**Status:** OPEN — NEW CRITICAL FINDING
**Root cause:** `sal_master_runner.py` has two modes: default (template + workbench merged) and `from_cache_only` (workbench only). The daily output file is generated in default mode. The "idempotency fix" only controls `from_cache_only=True` behavior.
**Symptom:** FODS daily SAL output has ~22 bootstrap-only template facts alongside 4,987 workbench facts. GAP-INT-002 builds its fact index from this file. A product source file citing a template-only fact ID (e.g., `ODF-FACT-NAMESPACE`) would pass GAP-INT-002.
**Impact:** GAP-INT-002's authority check is weaker than intended. The "clean" SAL output exists but is not the one used for daily enforcement.
**Repair:** Change daily SAL generation to use `from_cache_only=True`. Update `sal-facts-latest.json` generation script/cron accordingly.
**Evidence:** `generated_at: 2026-06-21T21:28:38`; FODS total=5009, workbench_verified=4987, bootstrap_only=22 (independently counted).

---

### RCA-GAP-INT-002-NO-SOURCE-CHECK
**Title:** GAP-INT-002 has no explicit `source == workbench_verified` check
**Status:** OPEN — CRITICAL (downgraded from CRITICAL to HIGH by SAL cleanup, but re-elevated by RCA-SAL-DEFAULT-MODE)
**Root cause:** `test_gap_int_002_product_source_fact_refs.py` checks that cited FACT-* IDs exist in `sal_index`. The index includes template facts (fact_status: bootstrap_only). No filter on `source == workbench_verified`.
**Symptom:** Product source could cite a bootstrap-only template fact (e.g., `ODF-FACT-ROOT-ELEMENT`) and pass GAP-INT-002.
**Impact:** Non-deterministic authority — if template facts change or are removed, existing product source citations would break. No deterministic linkage to workbench-reviewed evidence.
**Repair:** Add filter in `_load_sal_facts()`: only include facts where `fact.get('source') == 'workbench_verified'`. Update test assertions to document this requirement.
**Evidence:** `test_gap_int_002` line 34-38: no `source` filter; SAL index includes bootstrap-only facts.

---

## HIGH

### RCA-SPEC-ACQ-GNUMERIC
**Title:** Gnumeric spec not acquired; no normalized text
**Status:** OPEN
**Root cause:** Gnumeric XML schema exists but normalization pipeline was never run for this format. `.local/spec-cache/gnumeric/v10/spec-index.yaml` shows `normalized_text_cached: false`.
**Impact:** 0 SAL workbench facts for Gnumeric. 36 gap entries cite no spec facts.
**Repair:** Run normalization pipeline for Gnumeric schema; run extraction; build workbench YAML.

### RCA-SPEC-ACQ-ABW
**Title:** ABW spec (DTD) unreachable
**Status:** OPEN
**Root cause:** DTD URL returns ECONNREFUSED. Cannot acquire spec text.
**Impact:** 0 SAL workbench facts for ABW. 50 gap entries cite no spec facts. Proof level P1.
**Repair:** Identify alternative ABW spec source; or classify as BLOCKED_EXTERNAL and document in debt ledger.

### RCA-HEALING-GATE-DEPTH-001
**Title:** Healing gate Lane 1 checks `fods_facts_gte_10` not `workbench_verified_fact_count > 0`
**Status:** OPEN
**Root cause:** `check_system_healing_gate.py` Lane 1 checks that the SAL module count >= 19, that FODS has >= 14 format-specific facts, and `fods_facts_gte_10: True`. It does not check that `workbench_verified_fact_count > 0` for any format.
**Symptom:** Gate passes even if all facts are bootstrap-only template facts. Gate passes even if Gnumeric/ABW/CSV have 0 workbench facts.
**Impact:** False confidence that spec authority is healthy based on infrastructure existence rather than content quality.
**Repair:** Add `workbench_verified_fact_count_check: true` criterion to Lane 1. Require `workbench_verified_fact_count > 0` for at least FODS/FODT/ZST.

### RCA-SKILLS-REPEATABILITY-001
**Title:** No governed skills for spec acquisition chain for most formats
**Status:** OPEN
**Root cause:** `sal-pipeline-heal` skill exists (registered) but covers SAL pipeline repair, not spec acquisition from external sources. No skill covers: spec download → normalization → extraction → workbench fact review workflow.
**Impact:** Gnumeric/ABW/CSV spec acquisition cannot be governed or tracked repeatably.
**Repair:** TC-0021: design spec acquisition skill; create workbench fact review workflow.

### RCA-PROOF-GRAPH-001
**Title:** No machine-generated proof graph linking spec → fact → code → test
**Status:** OPEN
**Root cause:** Spec stubs exist but are architecture_only. QName registry exists but is not consumed by test runners. No automated tool generates and validates the full proof chain.
**Impact:** Proof chain (P5 for FODS) is assembled from separate artifacts; no single machine-checkable proof graph.
**Repair:** Create `generate_proof_graph.py` that reads qname-registry + SAL facts + spec stubs + product source + test results and produces a verifiable chain.

---

## MEDIUM

### RCA-GAP-LEDGER-CSV-STALE
**Title:** Gap-ledger CSV entries reference FACT-CSV-001/002 not in SAL output
**Status:** OPEN — NEW FINDING
**Root cause:** CSV gap entries were populated with `spec_facts: ['FACT-CSV-001', 'FACT-CSV-002']` during a prior SAL→gap-ledger join. CSV has 0 SAL workbench facts; these IDs never existed in workbench output.
**Symptom:** 58 CSV gap entries show spec_facts with 116 dead references. TC-GUARD-001 accepts items citing these gaps.
**Impact:** CSV gaps appear spec-backed. Medium severity (CSV already has 0 SAL facts; the appearance is more misleading than consequential).
**Repair:** Clear spec_facts for all CSV gaps where the IDs don't exist in sal-facts-latest.json; OR properly acquire CSV spec and add real FACT-CSV-NNN entries.

### RCA-GAP-LEDGER-NO-AUTH-LEVEL
**Title:** Gap-ledger has no `authority_level` field on any of 958 entries
**Status:** OPEN
**Root cause:** Field was never added. The spec-to-feature plan required authority_level per gap to track evidence quality.
**Impact:** TC-GUARD-001 cannot distinguish a gap with 4,987 workbench facts vs a gap with 0 facts. Both satisfy the guard equally.
**Repair:** Add `authority_level` field derived from format's `workbench_verified_fact_count` in SAL output. Update gap-ledger generator.

### RCA-TC-GUARD-AUTHORITY-QUALITY
**Title:** TC-GUARD-001 checks gap_ledger_ref PRESENCE not AUTHORITY QUALITY
**Status:** OPEN
**Root cause:** `autonomous_cycle.py` Step 2d3 checks `if not (has_gap_ref or has_cap_ref or has_spec_fact_refs)` — presence only. No authority_level or workbench_fact_count check.
**Impact:** A PRODUCT_SOURCE citing a Gnumeric gap (0 SAL facts) satisfies TC-GUARD-001 identically to one citing a FODS gap (4,987 SAL facts).
**Repair:** Add authority depth check: if gap's format has 0 workbench SAL facts, emit warning or require explicit override.

### RCA-V46-WARN-ONLY
**Title:** V46 (skill_transcript requirement) is WARN-only
**Status:** OPEN
**Root cause:** V46 was implemented as advisory during bootstrap phase. Most existing PRODUCT_SOURCE items predate the sal-pipeline-heal skill registration.
**Impact:** Legacy items and items not using registered skills can pass without skill transcript evidence.
**Repair:** After bootstrap phase completes, upgrade V46 to `blocks_sprint: True`.

### RCA-REQ-PACK-TC0021
**Title:** FODS requirement packs exist but TC-0021 traceability review is pending
**Status:** OPEN
**Root cause:** 3 req-pack YAMLs created (`parser-requirements.yaml`, `model-requirements-draft.yaml`, `sample-requirements.yaml`). TC-0021 review: verify each req traces to a FACT-FODS-NNN in SAL output.
**Impact:** Req packs may not accurately trace to workbench facts. Proof level P5 claim partially rests on unverified traceability.
**Repair:** Execute TC-0021 review of parser-requirements.yaml; document each req's FACT-FODS-NNN mapping.

### RCA-EVIDENCE-SCHEMA-001
**Title:** Evidence declaration schema has no authority_level or workbench_fact_count field
**Status:** OPEN
**Root cause:** `evidence-declaration.yaml` schema was designed before authority_level requirement. No required field to declare spec authority depth.
**Impact:** Declarations do not capture the authority quality of cited gaps/facts.
**Repair:** Add optional `spec_authority_depth` or `workbench_verified_fact_count` field to declaration schema.

### RCA-GAP-INT-002-COVERAGE
**Title:** GAP-INT-002 has no assertions that zero-fact formats remain at zero
**Status:** OPEN
**Root cause:** `test_sal_runner_idempotency.py` and `test_gap_int_002` test FODS/FODT/ZST fact counts. No test asserts Gnumeric/ABW/CSV == 0 facts (which would detect regressions if template facts were re-added for those formats).
**Impact:** If template facts were inadvertently re-added for Gnumeric/ABW, no test would catch it.
**Repair:** Add `test_gnumeric_zero_sal_facts()` and `test_abw_zero_sal_facts()` to idempotency or integration test suite.

### RCA-ACTION-QUEUE-ADVISORY
**Title:** Action queue still advisory (action_queue_not_advisory: False)
**Status:** OPEN
**Root cause:** `check_system_healing_gate.py` Lane 2 check `action_queue_not_advisory: False` — the action queue remains advisory (not enforced). Gate passes anyway.
**Impact:** Action queue recommendations are not binding; can be ignored without gate failure.
**Repair:** Upgrade action queue to enforce mode; update healing gate check accordingly.

### RCA-FODFAM-CHAIN
**Title:** FODP/FODG/ODS/ODT have 1,066 workbench facts each but undocumented acquisition chain
**Status:** OPEN — NEW FINDING
**Root cause:** FODP, FODG, ODS, ODT each have 1,066 workbench-verified SAL facts. This count is suspiciously identical to FODS/FODT secondary count. The acquisition chain for these formats (which workbench YAML, what verification method) is not documented.
**Impact:** Cannot verify these facts are truly format-specific vs inherited/cross-pollinated from FODS.
**Repair:** Audit FODP/FODG/ODS/ODT workbench YAMLs; confirm each fact is specific to that format's spec.

---

## RESOLVED (CLOSED)

### RCA-TC-GUARD-DELAYED (RESOLVED)
TC-GUARD-001 promoted to BLOCK mode (commit `83f062cf`). No longer a risk.

### RCA-SAL-TEMPLATE-FACTS-001 (PARTIALLY RESOLVED)
`from_cache_only=True` path is clean. BUT: daily output file (`sal-facts-latest.json`) still uses default mode. Template facts remain in the GAP-INT-002 fact index. See RCA-SAL-DEFAULT-MODE.

### RCA-GAP-LEDGER-ABW-MAGIC (RESOLVED)
ABW/Gnumeric gap entries previously had `spec_facts: ['ABW-FACT-MAGIC', 'GNUMERIC-FACT-MAGIC']`. These stale magic IDs have been cleaned — current gap entries have `spec_facts: []`.

---

## Low Priority

### RCA-AUTH-LEVEL-NAMING
Per-fact field is `source` not `authority_level`. Functionally equivalent; naming mismatch with plan. No material impact.

### RCA-ZST-WORKBENCH-DEPTH
ZST has only 94 workbench facts vs FODS 4,987. ZST spec is smaller but 94 facts may not cover the full format.

### RCA-HEALING-GATE-ADVISORY
Healing gate is ADVISORY (Step 1b). Even if gate fails, sprint continues. Gate failure does not block product work.

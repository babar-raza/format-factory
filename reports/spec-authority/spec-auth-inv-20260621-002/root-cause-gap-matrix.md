# Specs Authority Layer — Root-Cause Gap Matrix
**Run ID:** spec-auth-inv-20260621-002
**Date:** 2026-06-21

**Discipline:** Every finding distinguishes symptom from root cause.
Symptoms sharing the same broken mechanism are grouped under one root cause.
Severity: Critical (system-level broken) / High (material risk) / Medium (functional risk) / Low (nuisance)

---

## GAP-SA-NEW-001 — sal-output/sal-facts-latest.json Can Be Overwritten by Single-Format Test Runs

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-NEW-001 |
| **Area** | SAL Output Integrity |
| **Requirement** | The authoritative SAL output file must represent ALL registered formats at all times |
| **Observed Evidence** | `.local/sal-output/sal-facts-latest.json` currently has 1 format / 94 facts (ZST only), generated at 21:16 today. The full 22-format / 14,284-fact output is at `.local/spec-cache/sal-facts-latest.json` (generated at 14:44). `sal_master_runner.py --format zst` writes to the same `sal-facts-latest.json` filename as `--all`. Test `test_gap_int_002` fails because it reads from `sal-output` and finds PBM facts missing (PBM is in spec-cache version). |
| **Symptom** | test_gap_int_002_product_source_fact_refs fails for PBM. V37 governance validator uses degraded file. capability_compiler uses degraded file. |
| **Root Cause** | `sal_master_runner.py` unconditionally writes `sal-facts-latest.json` for any invocation, including single-format runs. There is no "all-format lock" or separate filename for single-format vs. all-format output. The filename `sal-facts-latest.json` is used for both, creating a race condition when tests or pipelines run with `--format X`. |
| **Why This Is Root Cause** | The naming collision is the broken mechanism. If single-format runs wrote to `sal-facts-{format}.json` only (and only `--all` writes to `sal-facts-latest.json`), the race would not exist. |
| **Impact** | V37 and capability_compiler.py consume a degraded file. GAP-INT-002 test failure is a real defect, not a test artifact. Any sprint running with single-format SAL temporarily breaks the system-level SAL output. |
| **Severity** | Critical |
| **Detectability** | HIGH — filename collision is visible immediately |
| **Existing Tests** | test_gap_int_002 FAILS due to this |
| **Missing Tests** | Test asserting `sal-facts-latest.json` always has ≥ 20 format entries |
| **Repair Strategy** | In `sal_master_runner.py`: single-format runs MUST NOT write `sal-facts-latest.json`. Only `--all` writes it. Add a guard: `if output_filename == "sal-facts-latest.json" and len(formats) < len(all_formats): raise ValueError(...)` |
| **Verification Strategy** | Run `python sal_master_runner.py --format zst`; assert `sal-facts-latest.json` is unchanged. Run `python sal_master_runner.py --all`; assert all 22 formats present. |
| **Pilot Rerun Needed** | YES |
| **Owner/Component** | `tools/specification-authority-layer/sal_master_runner.py` |
| **Priority** | P0 |

---

## GAP-SA-NEW-002 — V37 and V47 Read from Different sal-facts-latest.json Paths

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-NEW-002 |
| **Area** | Governance Validator Consistency |
| **Requirement** | All governance validators must read from the same authoritative SAL output |
| **Observed Evidence** | V37 (`validate_spec_fact_authority_chain`) reads from `.local/sal-output/sal-facts-latest.json`. V47 (`validate_spec_fact_refs_in_sal_output`) reads from `.local/spec-cache/sal-facts-latest.json`. These are different files with different content (94 vs 14,284 facts as of today). |
| **Symptom** | V37 could report "no facts for format X" while V47 passes. Cross-validator consistency is undefined. |
| **Root Cause** | The two paths were created at different times during the SAL evolution. `.local/sal-output/` was the original output directory. `.local/spec-cache/` was added later when the per-format workbench was located there. No refactoring aligned the paths. |
| **Why This Is Root Cause** | The dual-path inconsistency means the governance system has two different views of SAL truth. Each validator produces correct results for its own source, but the overall governance verdict is based on inconsistent data. |
| **Impact** | A sprint could pass V47 (which reads the full authoritative file) while V37 sees only 94 ZST facts. Governance is split-brained. |
| **Severity** | High |
| **Detectability** | MEDIUM — requires inspecting both files and comparing validator source code |
| **Existing Tests** | None for this specific inconsistency |
| **Missing Tests** | Test asserting V37 and V47 read the same file; test that both files match when they exist |
| **Repair Strategy** | Canonicalize to one path: `.local/sal-output/sal-facts-latest.json`. Update V47 to read from `sal-output` (or symlink). Also fix GAP-SA-NEW-001 so sal-output is always the full file. |
| **Verification Strategy** | After repair: both V37 and V47 return identical fact sets; `ls -la` shows same inode or identical content. |
| **Pilot Rerun Needed** | YES |
| **Owner/Component** | `tools/supervisor/governance_validators.py` V37, V47 |
| **Priority** | P0 |

---

## GAP-SA-NEW-003 — spec_verifier.py Not Called in Production SAL Path

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-NEW-003 |
| **Area** | Anti-Bypass Protection |
| **Requirement** | Every fact emitted by the SAL runner must pass anti-bypass verification before being marked "verified" |
| **Observed Evidence** | `sal_master_runner.py` imports only `argparse, json, sys, datetime, pathlib`. No import of `spec_verifier`. The `_load_workbench_verified_facts()` function reads YAML directly and trusts the `verification_status` field in the workbench file. `spec_verifier.py` is 100% covered in tests (14/14 adversarial cases PASS) but is NEVER called from the production pipeline. |
| **Symptom** | A workbench file with manually-edited `verification_status: verified` and no `source_id` would pass through SAL unchallenged. |
| **Root Cause** | The production SAL runner was designed to use pre-built, pre-verified workbench files rather than running the full extraction pipeline. This is a valid design choice for performance, but it means the anti-bypass check is trusted at write time (workbench creation), not enforced at read time (SAL runner). Since workbench creation is also manual/semi-automated, the anti-bypass guarantee is per-session, not per-run. |
| **Why This Is Root Cause** | The separation between "verification at workbench write time" and "trust at SAL run time" creates a window where a corrupted workbench could produce unverified facts labeled as "verified" without detection. |
| **Impact** | LOW currently (workbench files are carefully curated), but HIGH if workbench population becomes more automated without wiring spec_verifier. |
| **Severity** | Medium |
| **Detectability** | MEDIUM — requires reading sal_master_runner.py carefully |
| **Existing Tests** | spec_verifier adversarial tests (14 PASS) — but these test the verifier in isolation |
| **Missing Tests** | Integration test: inject corrupted workbench entry (no source_id) → assert SAL runner rejects or warns |
| **Repair Strategy** | Add a verification pass in `_load_workbench_verified_facts()`: call `spec_verifier.verify_requirements()` on loaded facts; reject any fact where status is not VERIFIED. Flag WARN for UNVERIFIABLE facts. |
| **Verification Strategy** | Inject fact with source_id=null into workbench test fixture; assert SAL runner emits WARN and excludes fact from output. |
| **Pilot Rerun Needed** | YES — ZST pilot |
| **Owner/Component** | `tools/specification-authority-layer/sal_master_runner.py`, `spec_verifier.py` |
| **Priority** | P1 |

---

## GAP-SA-NEW-004 — Spec Source Not Fetched for 8/10 Registered Formats

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-NEW-004 |
| **Area** | Source Acquisition Provenance |
| **Requirement** | Every registered source must have sha256_snapshot before implementation work proceeds |
| **Observed Evidence** | `sources.jsonl`: FODS sha256=92cfe64…, ZST sha256=8ee6be0… (2 of 10). CSV, DIF, GNUMERIC, ABW (unavailable), PBM, PGM, PPM, TSV all have `sha256_snapshot: null`. 8 of 10 registered sources unfetched. |
| **Symptom** | Formats with no spec text produce zero workbench facts. Implementation work for these formats uses hardcoded template facts or ZERO facts. |
| **Root Cause** | T3 authorization requires 6 conditions including network access (`--allow-network` flag) and Babar Raza approval. For most formats this authorization ceremony hasn't been completed. No gate prevents implementation taskcards from being created until sha256_snapshot is non-null. The acquisition planning pipeline treats source registration as sufficient even though no spec text exists. |
| **Why This Is Root Cause** | The missing gate is the root cause. If acquisition-pack creation required `sha256_snapshot != null` in sources.jsonl, implementation could not begin for these formats. Currently it proceeds without spec backing. |
| **Impact** | 8 formats have no verified spec text. Implementation facts for these formats are either zero or hardcoded templates. Spec parity claims for these formats are unverifiable. |
| **Severity** | High |
| **Detectability** | HIGH — sources.jsonl is readable |
| **Existing Tests** | None that gate acquisition planning on sha256_snapshot |
| **Missing Tests** | Test: acquisition-pack creation for format with sha256_snapshot=null must fail or warn |
| **Repair Strategy** | Add `validate_spec_source_acquired` governance validator that checks sha256_snapshot for any format appearing in PRODUCT_SOURCE items. WARN initially; BLOCK after 30-day grace. Complete T3 authorization for RFC-based formats (CSV/RFC4180, TSV, ZST are already done partially). |
| **Verification Strategy** | Run `python tools/spec-cache/refresh_check.py` on all registered sources; all return not_stale. For new formats: sha256_snapshot != null before any PRODUCT_SOURCE taskcard is created. |
| **Pilot Rerun Needed** | YES — ZST already has sha256; good pilot |
| **Owner/Component** | `tools/spec-cache/acquire_spec.py`, governance validators |
| **Priority** | P1 |

---

## GAP-SA-NEW-005 — No Bidirectional Fact-Product-Test Linker

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-NEW-005 |
| **Area** | End-to-End Traceability |
| **Requirement** | It must be possible to: (a) start from a spec fact and find all product code and tests that implement it; (b) start from a test failure and find the governing spec fact |
| **Observed Evidence** | Source code has `spec_fact_ref = "FACT-FODS-001"` fields and `# FACT-FODS-001` comments. No tool parses these and produces a matrix. `test_gap_int_002` provides one-directional check (product → SAL) but not bidirectional. `.local/capability-proof-graph/` does not exist. `tools/requirements_authority/graph_store.py` is implemented but not populated. |
| **Symptom** | Gate 11 P1-P11 criteria are evaluated by reading code, not by machine-verifiable fact→test linkage. |
| **Root Cause** | `tools/traceability/fact_product_linker.py` (or equivalent) was never created. The `tools/requirements_authority/` implementation covers capability claims and product requirements but does not parse source code for `FACT-*` comments and generate a bidirectional index. The proof graph store exists but requires explicit population; no import script runs against the current source. |
| **Why This Is Root Cause** | The graph store is the right mechanism but it is never loaded. The source code comments are the right convention but they are never harvested. Both halves exist in isolation. |
| **Impact** | Spec parity claims for Gate 11 are based on human code review, not machine-verifiable fact-to-test linkage. The "18 node types / 19 edge types" proof graph is a design artifact, not a live system. |
| **Severity** | High |
| **Detectability** | MEDIUM |
| **Existing Tests** | test_gap_int_002 (partial: source→SAL, not bidirectional) |
| **Missing Tests** | For every FACT-FODS-001 in source, assert at least one test in tests/python/fods/ covers it |
| **Repair Strategy** | (1) Write `tools/traceability/scan_fact_refs.py` that harvests all `FACT-*` comments from `src/python/`. (2) Write `tools/traceability/populate_proof_graph.py` that calls `graph_store.py` with harvested facts. (3) Add to sprint closeout: run populate_proof_graph.py and save `.local/capability-proof-graph/`. |
| **Verification Strategy** | Run linker; assert FACT-FODS-001 has ≥1 product file and ≥1 test file. Run for FACT-ZST-001 through FACT-ZST-015. |
| **Pilot Rerun Needed** | YES — FODS vertical slice |
| **Owner/Component** | New: `tools/traceability/`, `tools/requirements_authority/graph_store.py` |
| **Priority** | P1 |

---

## GAP-SA-NEW-006 — Autonomous Task Generator Does Not Require Spec Facts by Default

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-NEW-006 |
| **Area** | Integration with Autonomous Workflow |
| **Requirement** | All PRODUCT_SOURCE tasks in the autonomous queue must cite verified spec facts |
| **Observed Evidence** | `autonomous_task_generator.py:1607` calls `select_next_work_items()` with `require_spec_facts=False` as the default. The `require_spec_facts` flag exists and works but is never set to True in the autonomous path. |
| **Symptom** | Product tasks can be scheduled and executed by the autonomous system without any spec fact backing. V13/V47 in evidence declarations provide a backstop, but the task is executed before governance validates it. |
| **Root Cause** | The `require_spec_facts` parameter was added to support future enforcement but was not activated. The design anticipated full spec coverage before enforcing this, but that coverage has not been reached for most formats. |
| **Why This Is Root Cause** | The gate exists but is permanently in its "open" position. A closed gate would prevent task scheduling for formats without workbench coverage, ensuring spec authority is integrated at the earliest decision point. |
| **Impact** | Tasks for formats with zero spec facts (CSV, DIF, GNUMERIC, ABW, etc.) can be autonomously scheduled and executed. V13/V47 in the declaration provide some recovery, but the autonomous loop runs first. |
| **Severity** | Medium |
| **Detectability** | HIGH — one line in task generator |
| **Existing Tests** | None for this specific default |
| **Missing Tests** | Test asserting that formats with sha256_snapshot=null are not scheduled as PRODUCT_SOURCE tasks |
| **Repair Strategy** | Tiered activation: (1) For formats with workbench coverage ≥50%, set `require_spec_facts=True`. (2) For formats with coverage <50%, continue with `require_spec_facts=False` but add `spec_source_unavailable` classification to task. |
| **Verification Strategy** | Mock task generator with ZST (has workbench) and CSV (no workbench); assert ZST task requires spec facts, CSV task has `spec_source_unavailable` flag. |
| **Pilot Rerun Needed** | NO |
| **Owner/Component** | `tools/supervisor/autonomous_task_generator.py` |
| **Priority** | P1 |

---

## GAP-SA-NEW-007 — 4,913 Auto-Extracted EX Facts Have Weaker Provenance Than 78 Hand-Curated Facts

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-NEW-007 |
| **Area** | Fact Quality / Verification Depth |
| **Requirement** | Verified facts must be traceable to exact spec locations with evidence the text was found |
| **Observed Evidence** | 78 FACT-FODS-001 to FACT-FODS-078 have `extraction_method: tier1_section`, `verification_evidence: "text.txt line NNNN: [exact spec text]"`, `validated_by: independent_agent_verifier`, `spec_page_confirmed: true`. 4,913 FACT-FODS-EX-* have `extraction_method: automated_extraction/xml_element_scan`, `spec_id: fods-normalized` (normalized text, not PDF), `validated_by: deterministic_spec_text_se[arch]` (string appears truncated). The EX facts lack `verification_evidence` text and `spec_page_confirmed`. |
| **Symptom** | fact-coverage-summary.md reports 99.9% coverage for FODS, suggesting near-complete spec parity. In reality, 98% of FODS facts are automated extractions of XML element names from normalized text, not verified behavioral requirements. |
| **Root Cause** | The auto-extraction pipeline (`xml_element_scan`) was designed to rapidly build a large fact inventory for coverage metrics. It captures every XML element/attribute name as a "fact" from the normalized spec text. This is valid for element enumeration but insufficient for behavioral requirements (e.g., "what happens when office:value-type is date and the date is malformed?"). The 78 hand-curated facts are behavioral. The 4,913 EX facts are structural enumeration. Both are stored in the same `verified_status: verified` bucket. |
| **Why This Is Root Cause** | The fact schema does not distinguish "element enumeration" from "behavioral requirement." Coverage metrics treat both equally. Gate readiness claims based on coverage% are inflated because the denominator includes structural enumerations that don't prove behavioral compliance. |
| **Impact** | MEDIUM — structural facts are still correct spec references; risk is that behavioral coverage appears higher than it is. For Gate 11, P1-P11 behavioral criteria cannot be claimed as met by element-enumeration facts. |
| **Severity** | Medium |
| **Detectability** | HIGH — visible by inspecting any FACT-FODS-EX fact vs FACT-FODS-001 |
| **Existing Tests** | None that distinguish behavioral from structural facts |
| **Missing Tests** | Test: at least N% of facts per format must be `extraction_method: tier1_section` (hand-curated or section-cited) |
| **Repair Strategy** | Add `fact_category: behavioral | structural_enumeration` field to workbench schema. Update coverage metrics to report behavioral and structural separately. Gate 11 readiness requires behavioral coverage ≥ defined threshold. |
| **Verification Strategy** | After adding fact_category: count behavioral facts for FODS; target ≥ 50 behavioral facts to claim structural behavioral coverage. |
| **Pilot Rerun Needed** | YES — FODS pilot with behavioral fact targeting |
| **Owner/Component** | `tools/spec-normalize/build_spec_workbench.py`, workbench schema |
| **Priority** | P2 |

---

## GAP-SA-NEW-008 — refresh_check.py Never Called Automatically

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-NEW-008 |
| **Area** | Staleness Detection |
| **Requirement** | Stale or hash-mismatched specs must be detected before any work proceeds |
| **Observed Evidence** | `tools/spec-cache/refresh_check.py` is a complete, well-designed staleness scanner. It checks `stale_flag`, `missing_file`, and `hash_mismatch`. It exits non-zero if stale entries found. However, it is NEVER called in `autonomous_cycle.py`, supervisor loop, or any CI step. |
| **Symptom** | If the ODF 1.3 spec were updated (unlikely but possible), the cached text.txt would be stale and facts would not be re-verified. No automated detection would catch this. |
| **Root Cause** | `refresh_check.py` was implemented as a manual diagnostic tool, not as an automated gate. The autonomous_cycle.py Step 0a only checks SAL facts age (>7 days), not spec cache staleness. |
| **Why This Is Root Cause** | The detection mechanism exists but is not wired. The autonomous loop can run indefinitely using a stale spec without any alert. |
| **Impact** | LOW currently (specs rarely change), but represents a missing guarantee in the authority chain. |
| **Severity** | Low |
| **Detectability** | HIGH — reading autonomous_cycle.py Step 0a makes the omission obvious |
| **Existing Tests** | None for automated staleness detection |
| **Missing Tests** | Integration test: mark spec-index.yaml as stale → assert next autonomous cycle triggers refresh_check |
| **Repair Strategy** | Add `refresh_check.py` call to Step 0a of `autonomous_cycle.py`. Non-zero exit → log warning (don't block sprint; log stale spec and continue). |
| **Verification Strategy** | Set `stale: true` in FODS spec-index.yaml; run autonomous_cycle; assert warning in log; assert next step notes stale spec. |
| **Pilot Rerun Needed** | NO |
| **Owner/Component** | `tools/supervisor/autonomous_cycle.py`, `tools/spec-cache/refresh_check.py` |
| **Priority** | P2 |

---

## GAP-SA-NEW-009 — source_hash Field in Acquisition Pack Templates Is Never Populated

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-NEW-009 |
| **Area** | Acquisition Pack Provenance |
| **Requirement** | Acquisition packs must link their spec citations to the cached and verified spec file |
| **Observed Evidence** | `acquisition-packs/_template/pack.yaml` has `source_hash: null`. `acquisition-packs/fods/gate4-human-review-packet.md` has `source_hash: null`. `acquisition-packs/fodg/parser-notes.md` has `source_hash: null`. Even FODS acquisition packs (which DO have a fetched and sha256-verified spec) have `source_hash: null` in pack files. The only place sha256 appears for FODS is `spec-index.yaml`. |
| **Symptom** | Acquisition pack files cannot be traced back to a specific cached spec version. If the spec file changes, the pack continues to reference the old spec without detecting the mismatch. |
| **Root Cause** | The template was created with `source_hash: null` as a placeholder, and no tool auto-populates it from spec-index.yaml. Pack creation is manual and no check enforces that source_hash is set before the pack is used. |
| **Why This Is Root Cause** | The broken mechanism is the missing link between spec-index.yaml (where sha256 lives) and acquisition-pack files (where it should be propagated). A simple tool that reads spec-index.yaml and writes source_hash to pack.yaml would close this gap. |
| **Impact** | Acquisition packs cannot prove they are based on a specific spec snapshot. For Gate 11 evidence, this weakens the authority chain. |
| **Severity** | Medium |
| **Detectability** | HIGH — null values visible in template |
| **Existing Tests** | None |
| **Missing Tests** | Test: any acquisition pack with item_type referencing ODF must have source_hash matching FODS spec-index.yaml |
| **Repair Strategy** | Write `tools/spec-cache/propagate_source_hash.py` that reads spec-index.yaml and updates pack.yaml/parser-notes.md/spec-evidence.md with the correct sha256. Run as part of acquisition-pack finalization. |
| **Verification Strategy** | After repair: grep `source_hash: null` in acquisition-packs/fods/ returns zero results. |
| **Pilot Rerun Needed** | NO |
| **Owner/Component** | `acquisition-packs/`, `tools/spec-cache/` |
| **Priority** | P2 |

---

## GAP-SA-NEW-010 — authority_lifecycle.py Not Wired Into Workbench Population

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-NEW-010 |
| **Area** | AI Governance |
| **Requirement** | Facts generated through AI-assisted or semi-automated paths must traverse the 12-state lifecycle before reaching "authoritative" status |
| **Observed Evidence** | `tools/ai/validators/authority_lifecycle.py` implements the 12-state machine with enforced transitions and evidence requirements. `tools/ai/contracts/artifact-authority-states.yaml` defines the state contract. However, no call to `authority_lifecycle.py` exists in `sal_master_runner.py`, `run_extraction_pipeline.py`, `build_spec_workbench.py`, or any workbench creation tool. The FACT-FODS-EX-* facts were added to verified-facts-review.yaml directly with `verification_status: verified` without passing through the lifecycle. |
| **Symptom** | 4,913 auto-extracted facts carry `verification_status: verified` without lifecycle provenance. The lifecycle machine is correct but dormant. |
| **Root Cause** | The workbench population workflow predates the AI authority lifecycle implementation. When the lifecycle was added to `tools/ai/`, it was not retrofitted into the existing workbench creation tools. The "verified" status in the workbench is a local convention, not a lifecycle state. |
| **Why This Is Root Cause** | Two parallel fact-quality systems exist: the workbench's `verification_status` field and the AI lifecycle's 12-state machine. They are not connected. |
| **Impact** | LOW currently (auto-extracted facts are deterministic, not AI-hallucinated), but the gap means the lifecycle machine cannot be gradually enforced as AI-assisted extraction is introduced. |
| **Severity** | Low |
| **Detectability** | MEDIUM — requires reading both systems |
| **Existing Tests** | None |
| **Missing Tests** | Integration test: workbench entry created via automated extraction → assert lifecycle state = `source_cited` initially, not `authoritative_after_gate` |
| **Repair Strategy** | Add lifecycle state tracking to workbench schema: new field `lifecycle_state` (optional, defaults to `authoritative_after_gate` for hand-curated facts, `source_verified` for auto-extracted). Wire `authority_lifecycle.py` into `build_spec_workbench.py` and `run_extraction_pipeline.py`. |
| **Verification Strategy** | After repair: all FACT-FODS-EX-* facts have `lifecycle_state: source_verified`; all FACT-FODS-NNN facts have `lifecycle_state: authoritative_after_gate`. |
| **Pilot Rerun Needed** | NO |
| **Owner/Component** | `tools/ai/validators/authority_lifecycle.py`, `tools/spec-normalize/build_spec_workbench.py` |
| **Priority** | P3 |

---

## GAP-SA-NEW-011 — YAML Parsing of 5.2MB Workbench File Is Impractically Slow

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-NEW-011 |
| **Area** | SAL Runner Performance / Operability |
| **Requirement** | SAL runner must load workbench facts within practical time limits for tests and CI |
| **Observed Evidence** | `test_sal_master_runner.py::test_all_formats_returns_multiple` times out (>60s) inside `yaml.safe_load()` at `sal_master_runner.py:798`. Root: parsing the 5.2MB / 120,743-line `verified-facts-review.yaml` (4,991 facts) with PyYAML takes too long. `test_sal_bootstrap_vs_verified.py` (21 tests) takes 245s to run. `test_sal_from_cache_only.py` times out at the write step for the same reason. |
| **Symptom** | SAL test suite cannot complete within 30s or 60s timeouts. The 4,913 FACT-FODS-EX-* auto-extracted facts bulk the workbench YAML to 5.2MB. `yaml.safe_load()` on this file is a blocking operation taking ~60-90s. |
| **Root Cause** | The auto-extraction pipeline added 4,913 EX facts to `verified-facts-review.yaml` (growing it from ~40KB for 78 hand-curated facts to 5.2MB). `_load_workbench_verified_facts()` uses `yaml.safe_load(text)` with no streaming, chunking, or caching. PyYAML's pure-Python YAML parser has O(n²) or worse scaling on large nested documents. |
| **Why This Is Root Cause** | The YAML format and PyYAML SafeLoader are not suitable for 5MB+ nested documents. The design assumed small hand-curated workbenches (~50-100 facts). Auto-extraction violated that assumption without changing the loading strategy. |
| **Impact** | HIGH — SAL tests time out and cannot be run in CI. The runner itself takes >60s to load FODS workbench in any pipeline step, making Step 0a of autonomous_cycle impractically slow for a 22-format run. |
| **Severity** | High |
| **Detectability** | HIGH — timeout is visible immediately when running tests |
| **Existing Tests** | 3 tests timeout; 21 others pass only because they run for 245s |
| **Missing Tests** | Performance test asserting SAL runner loads FODS workbench in <10s |
| **Repair Strategy** | One of: (a) Store EX facts in separate `verified-facts-auto.jsonl` (JSON Lines, parsed line-by-line); (b) Use `ruamel.yaml` with `CSafeLoader`; (c) Pre-convert workbench to JSON on first load and cache. Option (a) is cleanest: split workbench into `verified-facts-review.yaml` (hand-curated only, <100 facts) + `verified-facts-extended.jsonl` (auto-extracted, 4913 facts, fast JSONL loading). |
| **Verification Strategy** | After repair: `test_sal_master_runner.py` completes in <30s. FODS workbench load time <5s. |
| **Pilot Rerun Needed** | NO — but must be fixed before ZST pilot is meaningful at scale |
| **Owner/Component** | `tools/specification-authority-layer/sal_master_runner.py:798`, `_load_workbench_verified_facts()` |
| **Priority** | P1 |

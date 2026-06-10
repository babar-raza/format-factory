# Specs Authority Layer — Root-Cause Gap Matrix
# Sprint: SPEC-AUTHORITY-LAYER-PRODUCTION-INVESTIGATION-001
# Generated: 2026-06-06

**Root causes are grouped by mechanism. Symptoms are listed under their root cause.**

---

## GAP-001 — Normalization Pipeline Not Run for Most Formats

| Field | Value |
|-------|-------|
| Gap ID | GAP-001 |
| Area | Spec normalization |
| Requirement | Every format with a cached spec must have normalized text, section index, and chunk index in `.local/spec-normalize/<format>/` before retrieval or fact extraction can be performed |
| Observed Evidence | `.local/spec-normalize/` directory does not exist. Only FODS has partial normalized output under `.local/spec-cache/fods/1.3/normalized/` (different path from intended). 8 of 9 cached formats have spec-index.yaml but no normalized text. |
| Symptom | No lexical or deterministic retrieval possible for ABW, CSV, DIF, GNUMERIC, PBM, PGM, TSV, ZST |
| Root Cause | The normalization pipeline (`tools/spec-normalize/`) was built but never executed against real spec PDFs except FODS. The spec-cache stores metadata but the normalization step that converts PDF→text→index was not run as part of any sprint completion gate. |
| Why This Is Root Cause, Not Symptom | Without normalization output, ALL downstream steps (retrieval, fact extraction, verified facts, spec-backed requirements, code citations, test traceability) are impossible. Every other gap about "no verified facts for format X" traces back here. |
| Impact | No spec-backed acquisition work possible for 8 of 9 formats; verified facts only available for FODS (and those are manually seeded, not from normalized text) |
| Severity | Critical |
| Detectability | Easy — `ls .local/spec-normalize/` shows it doesn't exist |
| Existing Tests | tools/spec-normalize/validate_normalized_spec.py (validates schema, not presence) |
| Missing Tests | Test that asserts `.local/spec-normalize/<format>/` exists for each cached format |
| Repair Strategy | Run `tools/spec-normalize/normalize_pdf.py` for FODS; run full normalization pipeline for each format with a real spec document. For text-based specs (RFC → ZST), adapt the normalizer. |
| Verification Strategy | `ls .local/spec-normalize/` shows directories; `validate_normalized_spec.py` passes for each format |
| Pilot Rerun Needed | YES |
| Owner | tools/spec-normalize/ |
| Priority | P1 — blocks all other spec authority work |

---

## GAP-002 — Spec Artifacts Use Synthetic Seed Data Instead of Real Extracted Requirements

| Field | Value |
|-------|-------|
| Gap ID | GAP-002 |
| Area | Verified facts / requirement extraction |
| Requirement | `.local/spec-artifacts/<FORMAT>-SPEC-001-requirements.json` must contain requirements extracted from real spec text, not from hand-crafted fixture strings |
| Observed Evidence | `FODS-SPEC-001-requirements.json` contains requirements like "Document root SHALL be office:document element." with `status: "candidate"`. `build_proof_graph_iter001.py` injects synthetic text snippets (fixture data) to create these. No PDF extraction is involved. |
| Symptom | Requirements have status "candidate" and are never promoted to "verified"; the proof graph references spec_auth as passing but the content is synthetic |
| Root Cause | `build_proof_graph_iter001.py` was designed to bootstrap the graph with plausible fixture data to make tests pass. This was a scaffolding decision that was never replaced with real spec extraction. The normalization gap (GAP-001) blocks real extraction, creating a dependency chain. |
| Why This Is Root Cause, Not Symptom | Even if normalization ran, the build_proof_graph pipeline would need to be rewired to use real extracted text rather than fixture strings. The fixture pattern masks the gap from tests. |
| Impact | All "spec-backed" claims in the proof graph are backed by synthetic data, not real spec text; acceptance gates that check spec_auth tests are passing are checking synthetic fidelity |
| Severity | Critical |
| Detectability | Moderate — requires reading build_proof_graph_iter001.py and comparing spec artifact text to actual spec PDF text |
| Existing Tests | tests/spec_authority/test_real_pilots.py — tests prove the pipeline works on fixture data but do not validate that the fixture text matches real spec |
| Missing Tests | Golden test: extract requirement from real FODS section 3.1.2 PDF text and assert it matches a known expected requirement |
| Repair Strategy | Wire `requirement_extractor.py` to real normalized spec text (after GAP-001 repair); add golden test that extracts from real spec and validates a known fact |
| Verification Strategy | `python tools/specification-authority-layer/requirement_extractor.py --source .local/spec-normalize/fods/text.txt` produces requirements matching known spec facts |
| Pilot Rerun Needed | YES |
| Owner | tools/specification-authority-layer/requirement_extractor.py + build_proof_graph |
| Priority | P1 |

---

## GAP-003 — Spec Source Registry Not Persisted Between Sessions

| Field | Value |
|-------|-------|
| Gap ID | GAP-003 |
| Area | Source registry / audit trail |
| Requirement | `.local/spec-source-registry/sources.jsonl` must exist and persist all registered sources as an append-only audit log |
| Observed Evidence | `.local/spec-source-registry/` directory does not exist. The `spec_source_registry.py` module writes to this path during runtime but the directory was never created or the registry was never run in a real (non-test) context. |
| Symptom | No durable audit trail of which spec sources were registered and when; governance runtime checks work only in-memory during test runs |
| Root Cause | The spec source registry was designed as a local file store but was only exercised in test fixtures that use `tmp_path`. A real session that runs `spec_governance_runtime.check_citation_allowed()` would fail silently or create the registry on first use, but this has never been wired into the acquisition pipeline. |
| Why This Is Root Cause, Not Symptom | Without persisted registry, all the governance enforcement (anti-bypass, usage ledger) exists only in tests. In production acquisition work, the governance layer is bypassed by default because it is never called. |
| Impact | Audit trail for spec citations does not exist for real acquisition work; compliance claims cannot be verified post-hoc |
| Severity | High |
| Detectability | Easy — directory missing |
| Existing Tests | Tests use tmp_path; do not check for production persistence |
| Missing Tests | Integration test that runs real acquisition task and verifies sources.jsonl was written |
| Repair Strategy | Initialize `.local/spec-source-registry/sources.jsonl` with existing cached specs; wire governance_runtime into acquisition task entry point |
| Verification Strategy | After acquisition task, `cat .local/spec-source-registry/sources.jsonl` shows new entries |
| Pilot Rerun Needed | YES |
| Owner | tools/specification-authority-layer/spec_source_registry.py |
| Priority | P2 |

---

## GAP-004 — Evidence Declarations Do Not Require Spec Fact References for Product Work

| Field | Value |
|-------|-------|
| Gap ID | GAP-004 |
| Area | Evidence validation / supervisor integration |
| Requirement | Evidence declarations for PRODUCT_SOURCE work items must include `spec_fact_refs` field listing the verified spec fact IDs (e.g., FACT-FODS-001) that justify the implementation |
| Observed Evidence | Evidence declaration schema (`docs/automation/supervisor-worker-contract.md`) does not include `spec_fact_refs`. Supervisor grading does not check for spec facts. All FOSS and product sprints have been accepted without spec fact citations. |
| Symptom | Implementations can be ACCEPTED without any traceability to spec; supervisor grades on test count and anti-skip patterns, not on spec compliance |
| Root Cause | The evidence contract was designed before the verified-fact layer was operational. The schema was never updated to include spec_fact_refs as a required field for product work. There is no schema-validation check in supervisor_loop.py that enforces spec traceability. |
| Why This Is Root Cause, Not Symptom | Even with perfect normalization and verified facts, they would have no enforcement power if the evidence gate does not require them. The missing schema field is the enforcement mechanism gap. |
| Impact | All 125+ product ledger entries accepted without spec fact backing; post-hoc compliance cannot be verified |
| Severity | High |
| Detectability | Easy — read evidence declaration schema |
| Existing Tests | tests/supervisor/ — grade-based tests do not check spec_fact_refs |
| Missing Tests | Test: PRODUCT_SOURCE declaration without spec_fact_refs should fail validation |
| Repair Strategy | Add `spec_fact_refs: []` (optional initially, then required) to evidence schema; add supervisor grading check |
| Verification Strategy | Submit PRODUCT_SOURCE declaration without spec_fact_refs; supervisor returns validation error |
| Pilot Rerun Needed | NO |
| Owner | docs/automation/supervisor-worker-contract.md; tools/supervisor/supervisor_loop.py |
| Priority | P1 |

---

## GAP-005 — Parser/Writer Source Code Has No Spec Fact Citations

| Field | Value |
|-------|-------|
| Gap ID | GAP-005 |
| Area | Source code traceability |
| Requirement | Parser and writer source code should reference spec fact IDs (e.g., `// FACT-FODS-001` or `# verified: FACT-FODS-001`) for any spec-mandated behavior |
| Observed Evidence | `src/net/fods/`, `src/python/fods/`, `src/python/abw/`, `src/python/gnumeric/` — no references to FACT-xxx or REQ-xxx identifiers in source code. Code comments cite the format name and general intent but not specific spec fact IDs. |
| Symptom | Code compliance with spec cannot be verified by tracing code back to spec facts; any spec deviation is undetectable without re-reading the full spec |
| Root Cause | No annotation convention was established or enforced for spec fact IDs in code. The verified-fact system was being built while product code was being written, so the gap was not filled retroactively. |
| Why This Is Root Cause, Not Symptom | Without code-level spec fact references, the traceability chain is broken at the most important point: the code that actually processes files. |
| Impact | Proof graph claims spec→code traceability but the graph has no real code-level anchor point |
| Severity | High |
| Detectability | Easy — `grep -r "FACT-" src/` returns nothing |
| Existing Tests | None for spec fact annotation in code |
| Missing Tests | Test: for each verified fact in verified-facts.yaml, a code file must reference the fact ID |
| Repair Strategy | Establish annotation convention; add FACT-xxx comments to existing code retroactively for the most critical format behaviors; add to coding standards for new work |
| Verification Strategy | `grep -r "FACT-FODS" src/net/fods/` returns matches |
| Pilot Rerun Needed | NO (retroactive fix) |
| Owner | All source code authors; docs/project-execution-standards.md |
| Priority | P2 |

---

## GAP-006 — Candidate Requirements Never Promoted to Verified Status

| Field | Value |
|-------|-------|
| Gap ID | GAP-006 |
| Area | Requirement lifecycle |
| Requirement | Requirements must be promoted from `candidate` to `verified` (or `rejected`) by a deterministic process before they can drive implementation |
| Observed Evidence | All requirements in `.local/spec-artifacts/*-requirements.json` have `status: "candidate"`. The `verified-facts.yaml` for FODS has 10 facts with `verification_status: "verified"` but these were manually seeded ("v1 facts seeded from gate artifacts"). No automated promotion workflow exists. |
| Symptom | The system has a candidate→verified lifecycle in the schema but nothing enforces or executes the promotion step |
| Root Cause | The verified-fact schema and CandidateRequirement.status field were designed, but no workflow component (human review step, automated spot-check tool, or gate enforcement) was built to drive requirements through the lifecycle. Promotion was left as a future step ("Richer extraction planned in TC-0021"). |
| Why This Is Root Cause, Not Symptom | Without a promotion mechanism, all requirements will remain candidate indefinitely. The current seeding is not repeatable or verifiable. |
| Impact | No format has a repeatable, auditable set of verified spec facts that can drive implementation |
| Severity | High |
| Detectability | Easy — check status field in all requirements files |
| Existing Tests | None for promotion workflow |
| Missing Tests | Test: after human_verify_fact() call, requirement status changes to "verified" and is persisted |
| Repair Strategy | Build a minimal human-review CLI tool that presents a candidate fact, shows the spec source text at the cited location, and records the reviewer's decision as "verified" or "rejected" |
| Verification Strategy | After review session, `verified-facts.yaml` has entries with `verification_status: "verified"` and `validated_by: "human"` |
| Pilot Rerun Needed | YES |
| Owner | tools/specification-authority-layer/spec_verifier.py (expand) |
| Priority | P1 |

---

## GAP-007 — Test Generation Is Empirical, Not Spec-Driven

| Field | Value |
|-------|-------|
| Gap ID | GAP-007 |
| Area | Test traceability |
| Requirement | At least a subset of tests for each format must be generated from or traceable to verified spec facts; test IDs should reference fact IDs |
| Observed Evidence | All format tests (tests/net/fods/, tests/python/) are written empirically — they test observed behavior of the parser/writer against sample files. No test has a `spec_fact_ref` annotation or references a FACT-xxx ID. `tools/ai/test_generation/` exists but is not connected to the test suite. |
| Symptom | Tests prove empirical behavior but not spec compliance; a spec-deviant implementation that passes all tests is indistinguishable from a spec-compliant one |
| Root Cause | Test generation was never connected to the verified-fact pipeline. The `tools/ai/test_generation/` module was built but disconnected from the test suite. Tests were written during format implementation sprints without a requirement to trace them to spec facts. |
| Why This Is Root Cause, Not Symptom | Empirical tests do not prove spec compliance. A parser that mis-reads FODS structure and consistently produces a wrong output will pass all empirical tests if all test cases use the same wrong output as expected. |
| Impact | Cannot claim spec compliance via tests alone for any format |
| Severity | High |
| Detectability | Easy — grep test files for FACT-xxx |
| Existing Tests | None for spec-driven testing |
| Missing Tests | For each FODS verified fact: a test that proves the parser handles that specific case per spec |
| Repair Strategy | Generate 1-3 golden spec-fact test cases per format from verified-facts.yaml; add them to test suite with fact reference comments |
| Verification Strategy | `grep -r "FACT-FODS" tests/` returns matches; tests pass |
| Pilot Rerun Needed | YES |
| Owner | tools/ai/test_generation/ (reconnect) or manual golden tests |
| Priority | P2 |

---

## GAP-008 — Supervisor Acceptance Does Not Check Spec Authority Coverage

| Field | Value |
|-------|-------|
| Gap ID | GAP-008 |
| Area | Supervisor integration |
| Requirement | Supervisor grading must include a spec_authority_coverage check; work items for formats with MISSING spec authority should receive a BLOCKED or CONDITIONAL grade |
| Observed Evidence | `tools/supervisor/authority_integration_fabric.py` computes spec_authority_status (COMPLETE/PARTIAL/MISSING) and generates `authority-integration-contract.json`. However, the supervisor_loop.py and grading logic do not read this contract to adjust grades. All format-related work items have been ACCEPTED regardless of spec authority status. |
| Symptom | Formats with MISSING spec authority (ABW, Gnumeric, ZST, Netpbm, SYLK) have implementation work accepted at the same grade as FODS which has (limited) spec authority |
| Root Cause | The authority_integration_fabric was built as a reporting tool but was never wired into the grading pipeline. The grading schema does not have a spec_authority_coverage threshold. |
| Why This Is Root Cause, Not Symptom | Reporting without enforcement is advisory. The mechanism to translate spec authority status into acceptance decisions does not exist. |
| Impact | ACCEPTED verdict is indistinguishable between spec-backed and empirically implemented formats |
| Severity | Medium |
| Detectability | Easy — read supervisor_loop.py grading logic |
| Existing Tests | tests/supervisor/test_authority_integration_fabric.py — tests fabric output, not grading integration |
| Missing Tests | Test: PRODUCT_SOURCE work item for format with MISSING spec authority gets CONDITIONAL grade |
| Repair Strategy | Read authority-integration-contract.json in grading; add spec_authority_threshold config; MISSING→BLOCKED, PARTIAL→CONDITIONAL, COMPLETE→full grade |
| Verification Strategy | Grading for GNUMERIC product work item returns CONDITIONAL_SPEC_AUTHORITY_PARTIAL |
| Pilot Rerun Needed | NO |
| Owner | tools/supervisor/supervisor_loop.py |
| Priority | P2 |

---

## GAP-009 — Product Ledger Has No Spec Fact References

| Field | Value |
|-------|-------|
| Gap ID | GAP-009 |
| Area | Product ledger traceability |
| Requirement | Each ledger entry for a product capability should reference the verified spec fact ID(s) that justify that capability |
| Observed Evidence | `registry/product-code-change-ledger.json` has 129 entries. None have a `spec_fact_ids` field. Ledger entries have capability descriptions but no spec citations. |
| Symptom | Ledger is an implementation record, not a compliance record |
| Root Cause | The ledger schema was designed to record what code was added, not why it is spec-compliant. The spec fact reference field was never added to the schema. |
| Impact | Cannot use the ledger to audit spec compliance; ledger provides no additional authority beyond test pass counts |
| Severity | Medium |
| Detectability | Easy — read ledger schema |
| Existing Tests | tests related to ledger validation check schema but not spec_fact_ids |
| Missing Tests | Test: ledger entry for PRODUCT_SOURCE must have non-empty spec_fact_ids |
| Repair Strategy | Add optional `spec_fact_ids: []` to ledger schema; require for new PRODUCT_SOURCE entries going forward; backfill FODS entries with FACT-FODS-xxx |
| Verification Strategy | Ledger schema updated; validator checks spec_fact_ids for new entries |
| Pilot Rerun Needed | NO |
| Owner | registry/product-code-change-ledger.json schema |
| Priority | P3 |

---

## GAP-010 — tools/ai/ Subsystem Is Disconnected from Authority Layer

| Field | Value |
|-------|-------|
| Gap ID | GAP-010 |
| Area | AI support integration |
| Requirement | The AI support subsystem (when used) must feed into the candidate requirement pipeline, not bypass it |
| Observed Evidence | `tools/ai/` has 14 subdirectories (agentic, contracts, control_plane, normalization, pipeline, prompts, requirements, retrieval, run_ai_checks.py, schemas, synthesis, telemetry, test_generation, validators). `authority_integration_fabric.py` does not import from tools/ai/. No active tests in test discovery connect tools/ai/ to spec authority. |
| Symptom | The AI subsystem is a large dead subsystem with potential to provide valuable support (large spec navigation, candidate section discovery, test generation) but currently provides nothing |
| Root Cause | tools/ai/ was built speculatively as a future enhancement. The integration work (connecting AI pipeline output to spec_source_registry + requirement_extractor → candidate status) was deferred and never done. |
| Why This Is Root Cause, Not Symptom | Not a critical gap (AI is not required for authority), but represents wasted investment and a future activation risk if connected without controls. |
| Impact | AI support for large spec navigation unavailable; large spec PDFs must be manually navigated; efficiency cost only (not correctness cost) |
| Severity | Low (efficiency), High (if activated without controls) |
| Detectability | Easy — check authority_integration_fabric.py imports |
| Existing Tests | None connecting tools/ai/ to authority layer |
| Missing Tests | Contract test: any AI pipeline output must have status="candidate" |
| Repair Strategy | Before activating tools/ai/: (1) add source citation requirement to all AI output schemas; (2) add status="candidate" enforcement; (3) wire output to spec_source_registry; (4) add tests |
| Verification Strategy | Run tools/ai/run_ai_checks.py; output has status="candidate" and source_ref for all claims |
| Pilot Rerun Needed | NO (until activation is authorized) |
| Owner | tools/ai/ maintainer |
| Priority | P4 |

---

## Severity Summary

| Gap ID | Area | Severity | Priority |
|--------|------|----------|----------|
| GAP-001 | Normalization pipeline | Critical | P1 |
| GAP-002 | Synthetic seed data | Critical | P1 |
| GAP-003 | Registry not persisted | High | P2 |
| GAP-004 | Evidence schema missing spec_fact_refs | High | P1 |
| GAP-005 | No code-level spec citations | High | P2 |
| GAP-006 | No requirement promotion workflow | High | P1 |
| GAP-007 | Tests empirical not spec-driven | High | P2 |
| GAP-008 | Supervisor doesn't check spec authority | Medium | P2 |
| GAP-009 | Product ledger no spec fact refs | Medium | P3 |
| GAP-010 | tools/ai/ disconnected | Low/High if activated | P4 |

---

## Priority Order for Repair

**Phase 1 (P1 — Minimum viable spec authority):**
1. GAP-001: Run normalization pipeline for FODS (already has PDF)
2. GAP-002: Wire real spec text into requirement_extractor; replace synthetic seed data
3. GAP-006: Build minimal human-review CLI to promote candidate → verified
4. GAP-004: Add spec_fact_refs to evidence schema; enforce for PRODUCT_SOURCE

**Phase 2 (P2 — Full integration):**
5. GAP-005: Add spec fact annotation convention to source code
6. GAP-007: Generate golden spec-fact tests from verified-facts.yaml
7. GAP-003: Initialize spec source registry; wire into acquisition entry point
8. GAP-008: Wire spec authority status into supervisor grading

**Phase 3 (P3/P4 — Hardening):**
9. GAP-009: Add spec_fact_ids to product ledger schema
10. GAP-010: Add controls before activating tools/ai/ subsystem

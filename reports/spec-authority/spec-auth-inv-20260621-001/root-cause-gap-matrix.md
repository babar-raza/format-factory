# Specs Authority Layer — Root-Cause Gap Matrix
**Run ID:** spec-auth-inv-20260621-001
**Date:** 2026-06-21

**Discipline:** Every finding distinguishes symptom from root cause. Symptoms that share the same broken mechanism are grouped under the same root cause.

---

## GAP-SA-001 — SAL Master Runner Uses Hardcoded Templates, Not Parsed Specs

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-001 |
| **Area** | SAL Fact Generation |
| **Requirement** | Spec facts must be extracted from or verified against the actual cached spec source |
| **Observed Evidence** | `sal_master_runner.py` lines 43-195 define `_SPEC_FACT_TEMPLATES` (OASIS, IETF, DEFAULT) and `_FORMAT_SPECIFIC_FACTS` (fods, fodt, zst, etc.) as static Python dictionaries. No call to `spec_parser.py`, `spec_indexer.py`, `spec_normalizer.py`, or `requirement_extractor.py`. |
| **Symptom** | Facts emitted in `sal-facts-latest.json` say `verification_status: "verified"` but carry no `source_id`, no `sha256`, no `section_id` pointing back to spec text |
| **Root Cause** | The SAL master runner was built as a "bootstrap" using hardcoded templates to provide immediate fact coverage before the full normalization pipeline was complete. The bootstrap was never replaced with the real parsed pipeline. The verifier, parser, and extractor modules were written correctly but never wired into the master runner's execution path. |
| **Why This Is Root Cause Not Symptom** | The missing `source_id` is a symptom. The root cause is the architectural shortcut: `sal_master_runner.py` bypasses `spec_parser→spec_indexer→requirement_extractor→spec_verifier` and instead uses in-process dictionaries. Even if source_id was added to the templates, the facts would still be unverified guesses. |
| **Impact** | All SAL-derived spec facts for all formats are unverified against actual spec text. TC-GUARD-001 enforcement accepts `spec_fact_refs: FACT-ZST-001` in declarations but the underlying fact is a hardcoded string, not a text-verified claim. |
| **Severity** | CRITICAL |
| **Detectability** | HIGH — visible by reading `sal_master_runner.py` |
| **Existing Tests** | None that catch this — 6 dogfood tests fail with JSONDecodeError (different issue) |
| **Missing Tests** | Test verifying every emitted fact has source_id; test running spec_verifier on SAL output |
| **Repair Strategy** | Wire `run_extraction_pipeline.py` into `sal_master_runner.py` for formats with workbench. For formats without workbench, mark facts as `status: bootstrap_only` (not "verified"). |
| **Verification Strategy** | After repair: all emitted facts have non-null source_id; spec_verifier passes on all VERIFIED facts |
| **Pilot Rerun Needed** | YES — ZST pilot |
| **Owner/Component** | `tools/specification-authority-layer/sal_master_runner.py` |
| **Priority** | P0 |

---

## GAP-SA-002 — Spec Source Registry Sparsely Populated (9 of 10 Without SHA-256)

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-002 |
| **Area** | Source Acquisition Provenance |
| **Requirement** | Every registered source must have a fetched snapshot with SHA-256 before any facts can be extracted from it |
| **Observed Evidence** | `.local/spec-source-registry/sources.jsonl` has 10 entries. 9 have `sha256_snapshot: null`. Only FODS (`SPEC-FODS-1_3`) has a non-null sha256. ABW is `status: unavailable`. CSV, DIF, GNUMERIC, FODP, FODT all `sha256_snapshot: null`. |
| **Symptom** | `run_fact_verification.py` reports "not_found" for 81/96 ZST facts because there is no spec text to search against. FODS 72.7% pending verification. |
| **Root Cause** | T3 authorization requires 6 conditions before download. Most formats have not completed the authorization ceremony, so specs were registered as entries but not fetched. The spec cache acquisition requires human authorization (T3-6) and network access (`--allow-network` flag). No automated mechanism exists to prompt for this. |
| **Why This Is Root Cause Not Symptom** | The 81 not-found facts are a symptom. The root cause is the combination of: (a) spec text not fetched for most formats, and (b) no automated reminder/gate blocking work until spec is available. |
| **Impact** | Fact verification cannot run for ~75% of registered formats. Workbench coverage is effectively 0% for most formats. SAL falls back to hardcoded templates. |
| **Severity** | HIGH |
| **Detectability** | HIGH — sources.jsonl readable |
| **Existing Tests** | None |
| **Missing Tests** | Test that each format's spec source has sha256_snapshot before work proceeds past Gate 4 |
| **Repair Strategy** | (1) Complete T3 authorization for ZST (RFC already available), FODT, CSV/RFC4180. (2) Add automated check in gate 4 readiness that sha256_snapshot is non-null. (3) Integrate `acquire_spec.py --allow-network` authorization into gate 4 close-out ceremony. |
| **Verification Strategy** | After repair: ZST sha256_snapshot populated; `refresh_check.py` passes; run `run_fact_verification.py --format zst` and get >0 verified |
| **Pilot Rerun Needed** | YES — ZST RFC8878 acquisition |
| **Owner/Component** | `tools/spec-cache/acquire_spec.py`, `tools/spec-cache/refresh_check.py` |
| **Priority** | P1 |

---

## GAP-SA-003 — No Proof Graph Connecting Spec Text → Fact → Requirement → Product Code → Test

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-003 |
| **Area** | End-to-End Traceability |
| **Requirement** | It must be possible to trace any product code behavior back to a verified spec fact and forward to a test |
| **Observed Evidence** | `src/python/fods/neutral_model.py` references `FACT-FODS-001` in docstrings. `src/python/zst/zst_codec.py` has `# spec_fact_refs: FACT-ZST-001`. No bidirectional lookup exists. No test verifies `FACT-FODS-001 → neutral_model.py` or vice versa. No proof graph tool exists in the repo. |
| **Symptom** | Spec_fact_refs in source code are documentation comments with no mechanical validation. TC-GUARD-001 enforces presence in declarations but not accuracy. |
| **Root Cause** | The project relies on developer discipline to add spec_fact_refs comments, but no tool parses these comments and verifies the FACT-ID resolves to a verified fact. The authority lifecycle model (`ai_draft→...→authoritative_after_gate`) requires a verified fact at each step but there is no tool connecting this lifecycle to actual source code artifacts. |
| **Why This Is Root Cause Not Symptom** | The dangling comments are a symptom. The root cause is the absence of a bidirectional traceability index: `FACT-ID → verified_fact_record → product_files_referencing_fact → tests_exercising_those_files`. |
| **Impact** | Gate 11 commercial readiness claims spec parity (P1-P11 criteria) but these criteria are evaluated by reading source code, not by tracing spec fact references through to test coverage. Spec parity claims are effectively unauditable. |
| **Severity** | CRITICAL |
| **Detectability** | MEDIUM — requires understanding intended design to see what's absent |
| **Existing Tests** | None |
| **Missing Tests** | Integration test: for FODS, every FACT-FODS-* must appear in both neutral_model.py and at least one test file |
| **Repair Strategy** | Build `tools/traceability/fact_product_linker.py` that: (1) parses source code for `# spec_fact_refs: FACT-X` patterns, (2) looks up each FACT-X in verified-facts-review.yaml, (3) maps to test files via pytest collection, (4) outputs traceability matrix |
| **Verification Strategy** | Run linker on FODS; confirm FACT-FODS-001–010 each have product_file + test_file entries |
| **Pilot Rerun Needed** | YES — FODS vertical slice |
| **Owner/Component** | New: `tools/traceability/` |
| **Priority** | P1 |

---

## GAP-SA-004 — Workbench Coverage Critically Uneven Across Formats

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-004 |
| **Area** | Normalization and Indexing |
| **Requirement** | All production formats should have spec workbench coverage sufficient to verify their implementation facts |
| **Observed Evidence** | Coverage: FODS 27.3%, FODT 100% (27 facts only), ZST 100% (15 facts only), Netpbm 100% (2 facts per format), CSV 0%. ABW, DIF, GNUMERIC, FODG, FODP, ODS, ODT, TSV, NDJSON, SYLK, XCF, TOML have no workbench entries at all. |
| **Symptom** | Most format facts are "verified" via hardcoded templates (GAP-SA-001) or pending verification |
| **Root Cause** | The workbench build requires: (a) spec text available in cache (GAP-SA-002), AND (b) manual curation of facts. FODT has 100% coverage because it has a small, hand-curated fact set. FODS has 278 registered facts (the most ambitious) and 27.3% coverage because the normalization pipeline was only partially completed before the spec-parity pivot happened. Most other formats were never brought to workbench stage. |
| **Why This Is Root Cause Not Symptom** | Low percentage is a symptom. Root causes are: (a) spec text not fetched (GAP-SA-002), (b) no automated workbench build trigger, (c) FODS fact set dramatically expanded before coverage was achieved, making the backlog too large to close manually. |
| **Impact** | The 73% of FODS facts pending verification are used to claim spec parity in Gate 11 preparation despite being unverified. |
| **Severity** | HIGH |
| **Detectability** | HIGH — fact-coverage-summary.md reports these numbers |
| **Existing Tests** | None that enforce minimum coverage threshold |
| **Missing Tests** | Test that enforces: any format with Gate 5+ status must have ≥50% fact coverage |
| **Repair Strategy** | (1) Batch-process FODS 201 pending facts through `run_fact_verification.py`. (2) Trim FODS fact set to achievable core facts (reducing from 278 to ~60 core facts). (3) For each new format, build workbench immediately after spec is acquired. |
| **Verification Strategy** | `run_fact_verification.py --format fods` achieves ≥80% pass rate |
| **Pilot Rerun Needed** | YES — FODS and ZST |
| **Owner/Component** | `tools/specification-authority-layer/run_fact_verification.py`, workbench YAML files |
| **Priority** | P1 |

---

## GAP-SA-005 — 6 Dogfood SAL Tests Failing (Format-Specific sal-facts Files Missing/Empty)

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-005 |
| **Area** | Integration Tests |
| **Requirement** | Dogfood tests must pass to demonstrate SAL facts can be exported and consumed |
| **Observed Evidence** | `tests/python/dogfood/test_dogfood_fods_fodt_sal_fact_ndjson_export.py` — 6 tests FAIL with `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`. Tests expect format-specific sal-facts files (e.g., `sal-facts-fods.json`) but these files are empty or missing in `.local/sal-output/`. |
| **Symptom** | Tests fail at JSON parse with empty file |
| **Root Cause** | `sal_master_runner.py --format fods` produces one combined file per run, not per-format files. The dogfood tests were written expecting per-format output files that the current master runner does not produce. This is a mismatch between the test fixture expectation and the actual output schema. |
| **Why This Is Root Cause Not Symptom** | JSONDecodeError is a symptom. The root cause is that no per-format sal-facts output mechanism exists in the current master runner, but tests were written assuming it would. |
| **Impact** | The dogfood proof that SAL facts can be exported to NDJSON and round-tripped is broken. This is the only concrete integration proof for the SAL→product chain. |
| **Severity** | HIGH |
| **Detectability** | HIGH — test failures visible in CI |
| **Existing Tests** | 6 failing tests (evidence of the gap) |
| **Missing Tests** | Passing equivalent tests |
| **Repair Strategy** | Add `--output-format per-format` mode to `sal_master_runner.py` that writes `sal-facts-<format>.json` per format alongside the combined file. Alternatively update tests to load from the combined file. |
| **Verification Strategy** | Run dogfood tests; all 6 currently-failing pass |
| **Pilot Rerun Needed** | NO (code fix only) |
| **Owner/Component** | `tools/specification-authority-layer/sal_master_runner.py`, `tests/python/dogfood/` |
| **Priority** | P1 |

---

## GAP-SA-006 — No Automated Hash-Staleness Detection or Refresh Trigger

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-006 |
| **Area** | Source Provenance / Invalidation |
| **Requirement** | When a cached spec's source SHA-256 changes, all derived artifacts (normalized text, workbench facts, SAL output) must be automatically invalidated |
| **Observed Evidence** | `tools/spec-cache/refresh_check.py` exists but is manual-only. `tools/spec-normalize/refresh_workbench.py` exists but is not called automatically. `autonomous_cycle.py` step 0a checks SAL age (7 days) but does NOT check if spec hash changed. `spec-index.yaml` has `stale: boolean` field but it is set manually. |
| **Symptom** | If a spec document is updated (e.g., ODF 1.3 errata), nothing automatically detects or propagates the change. |
| **Root Cause** | Staleness detection was designed (refresh_check.py, stale field in spec-index.yaml) but never wired to an automated trigger. The autonomous cycle checks SAL age but not spec hash. |
| **Why This Is Root Cause Not Symptom** | The missing trigger is the root cause. If spec changes, all derived data silently becomes stale with no machine-detectable signal. |
| **Impact** | If a spec is updated and re-downloaded, old facts from the previous version remain "verified" against the old text. Authority claims become wrong. |
| **Severity** | HIGH |
| **Detectability** | LOW — would not be visible until someone manually re-ran refresh_check.py |
| **Existing Tests** | MISSING |
| **Missing Tests** | Test: modify spec-index.yaml sha256 → verify workbench is marked stale → verify SAL marks facts as needs_re_verification |
| **Repair Strategy** | (1) Add hash check to autonomous_cycle.py step 0a: compare spec-index.yaml sha256 against current cached file sha256. If mismatch → mark stale → trigger workbench refresh. (2) Wire `refresh_check.py` to produce machine-readable stale signal. |
| **Verification Strategy** | Modify sha256 in spec-index.yaml for ZST; run autonomous_cycle.py; confirm stale detection fires |
| **Pilot Rerun Needed** | YES |
| **Owner/Component** | `tools/spec-cache/refresh_check.py`, `tools/supervisor/autonomous_cycle.py` |
| **Priority** | P2 |

---

## GAP-SA-007 — TC-GUARD-001 Checks Presence of spec_fact_refs But Not Validity of Referenced Fact

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-007 |
| **Area** | Supervisor Enforcement |
| **Requirement** | TC-GUARD-001 must verify not just that spec_fact_refs exists but that the referenced FACT-ID resolves to a verified fact |
| **Observed Evidence** | `autonomous_cycle.py` step 2d2 (lines 430-485): checks if `gap_ledger_ref`, `capability_ref`, or `spec_fact_refs` is present. If spec_fact_refs is `"FACT-ZST-001"`, the check passes. No lookup against `sal-facts-latest.json` or workbench verified-facts to confirm `FACT-ZST-001` is actually verified. |
| **Symptom** | Declaration with `spec_fact_refs: FACT-NONEXISTENT-999` passes TC-GUARD-001 |
| **Root Cause** | The guard was designed to enforce that agents think about spec facts, but the implementation only checks string presence, not fact validity. The second-order check (fact must exist + be verified) was noted as a future requirement but not implemented. |
| **Why This Is Root Cause Not Symptom** | Accepting invalid FACT-IDs is a symptom. Root cause: no cross-reference validator between spec_fact_refs strings and the SAL/workbench verified fact database. |
| **Impact** | TC-GUARD-001 provides false confidence. A developer can satisfy the guard with any FACT-ID string without the ID corresponding to a verified spec claim. |
| **Severity** | HIGH |
| **Detectability** | MEDIUM — requires understanding what TC-GUARD-001 checks |
| **Existing Tests** | `tests/supervisor/test_tc_guard_001_enforce.py` (8 tests) — but likely test only string presence, not validity |
| **Missing Tests** | Test: spec_fact_refs: FAKE-001 → TC-GUARD-001 FAILS because FAKE-001 not in workbench |
| **Repair Strategy** | After GAP-SA-001 and GAP-SA-004 are fixed (real facts with verified status), add second-order check in autonomous_cycle.py: `spec_fact_refs` must resolve against `sal-facts-latest.json` or `verified-facts-review.yaml`. |
| **Verification Strategy** | Test with valid and invalid FACT-IDs; invalid should block |
| **Pilot Rerun Needed** | NO |
| **Owner/Component** | `tools/supervisor/autonomous_cycle.py` step 2d2 |
| **Priority** | P2 (depends on GAP-SA-001 fix first) |

---

## GAP-SA-008 — Acquisition Prompts and Playbooks Do Not Enforce Spec Fact Requirement

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-008 |
| **Area** | Acquisition Integration |
| **Requirement** | Format acquisition prompts must require verified spec facts before implementation tasks begin |
| **Observed Evidence** | `acquisition-packs/_families/odf-flat/playbook.yaml` defines stage-level provenance fields but does not block advancement without spec facts. `add-python-api.md` command requires `spec_fact_refs` field but says "stop with BLOCKED_SPEC_QNAME_REQUIRED" if missing — this is a prompt instruction, not a gate. |
| **Symptom** | API implementations added without spec fact backing produce implementations that may not match the spec |
| **Root Cause** | The spec fact requirement in acquisition commands (`add-python-api.md`, `add-dotnet-api.md`) is enforced by prompt instruction only. No automated check runs before implementing to verify that the required FACT-ID exists and is verified. This is a design gap: the governance documentation prescribes the rule but no runtime check enforces it. |
| **Why This Is Root Cause Not Symptom** | Missing implementations are a symptom. Root cause: enforcement only at prompt level, not code/gate level. |
| **Impact** | Parser and API implementations proceed without spec backing for 13+ formats. |
| **Severity** | MEDIUM |
| **Detectability** | LOW |
| **Existing Tests** | None |
| **Missing Tests** | Test: running add-python-api without spec_fact_refs raises BLOCKED_SPEC_QNAME_REQUIRED |
| **Repair Strategy** | Add pre-flight check in supervisor: before any product sprint, verify that the target format has ≥1 verified fact in workbench. Block if not. |
| **Verification Strategy** | Sprint for format with no workbench → blocked. Sprint for format with verified facts → proceeds. |
| **Pilot Rerun Needed** | NO |
| **Owner/Component** | `.claude/commands/add-python-api.md`, `tools/supervisor/autonomous_cycle.py` |
| **Priority** | P3 |

---

## GAP-SA-009 — AI Governance Infrastructure Not Wired to SAL Pipeline

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-009 |
| **Area** | AI/LLM Integration |
| **Requirement** | AI-produced spec artifacts must traverse the authority lifecycle before being used |
| **Observed Evidence** | `tools/ai/validators/authority_lifecycle.py` implements the full state machine. 7 unit tests pass. But NO code in `sal_master_runner.py`, `run_extraction_pipeline.py`, or acquisition commands calls `can_transition()` or `validate_transition_chain()`. |
| **Symptom** | The authority lifecycle validator exists and is tested but is never invoked on actual spec facts |
| **Root Cause** | The AI governance infrastructure was built in a different sprint from the SAL infrastructure. Integration between them was planned but not implemented. The authority lifecycle is wired to test scaffolding only. |
| **Why This Is Root Cause Not Symptom** | Untested integration is a symptom. Root cause: no integration layer between authority_lifecycle.py and the SAL fact pipeline. |
| **Impact** | If AI is ever introduced to assist with spec fact generation, there is no mechanical guarantee the lifecycle will be enforced. The designed protection exists only on paper. |
| **Severity** | MEDIUM |
| **Detectability** | LOW |
| **Existing Tests** | 7 unit tests (lifecycle logic correct) |
| **Missing Tests** | Integration test: SAL fact generated → starts in ai_draft → cannot be written to workbench until source_verified transition |
| **Repair Strategy** | Wire `authority_lifecycle.can_transition()` into `run_extraction_pipeline.py` and `spec_verifier.py`. Emit authority_state field with each fact. |
| **Verification Strategy** | Run extraction pipeline on ZST; verify emitted facts carry authority_state field |
| **Pilot Rerun Needed** | YES |
| **Owner/Component** | `tools/ai/validators/authority_lifecycle.py`, `tools/specification-authority-layer/run_extraction_pipeline.py` |
| **Priority** | P2 |

---

## GAP-SA-010 — spec-retrieval-strategy.md Status "Proposed — Awaiting Human Review" But Operationally Active

| Field | Value |
|-------|-------|
| **Gap ID** | GAP-SA-010 |
| **Area** | Governance / Policy |
| **Requirement** | Active operational policies must be formally approved, not left in proposed status |
| **Observed Evidence** | `docs/spec-retrieval-strategy.md` header: "Status: Proposed — awaiting human review (TC-0015) before implementation". But the three-tier strategy (deterministic→lexical→vector) is described as current behavior and is referenced in AGENTS.md and autonomous operations. |
| **Symptom** | The strategy document cannot be cited as authoritative if it is proposed status |
| **Root Cause** | TC-0015 (spec retrieval strategy evaluation taskcard) was never formally closed with a human approval decision. The strategy was implemented anyway because it was sound, but the formal approval was skipped. |
| **Why This Is Root Cause Not Symptom** | The inconsistency is a symptom. Root cause: governance approval process was incomplete. |
| **Impact** | Medium — operational behavior is correct; the issue is audit trail integrity |
| **Severity** | LOW |
| **Detectability** | HIGH |
| **Existing Tests** | None |
| **Missing Tests** | None required |
| **Repair Strategy** | Close TC-0015 with formal approval record or update the document status to "Active — implemented, pending formal review closure" |
| **Verification Strategy** | Document status updated and TC-0015 closed |
| **Pilot Rerun Needed** | NO |
| **Owner/Component** | `docs/spec-retrieval-strategy.md`, `taskcards/TC-0015-spec-retrieval-strategy-evaluation.md` |
| **Priority** | P4 |

---

## Priority Order Summary

| Priority | Gap | Severity | Area |
|----------|-----|----------|------|
| P0 | GAP-SA-001: SAL uses hardcoded templates | CRITICAL | Core |
| P1 | GAP-SA-003: No end-to-end traceability | CRITICAL | Integration |
| P1 | GAP-SA-002: 9/10 spec sources not fetched | HIGH | Acquisition |
| P1 | GAP-SA-004: Low workbench coverage | HIGH | Normalization |
| P1 | GAP-SA-005: 6 dogfood tests failing | HIGH | Tests |
| P2 | GAP-SA-006: No staleness detection | HIGH | Provenance |
| P2 | GAP-SA-007: TC-GUARD-001 shallow check | HIGH | Enforcement |
| P2 | GAP-SA-009: AI lifecycle not wired | MEDIUM | AI |
| P3 | GAP-SA-008: Acquisition prompts advisory | MEDIUM | Integration |
| P4 | GAP-SA-010: Strategy doc not approved | LOW | Governance |

---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-03
intended_location: /memory
source: ChatGPT conversation memory plus inspected Phase 0 evidence bundles through run015; updated run015–run040 to reflect run039 independently verified PASS (44 checks), stale commit fixed (d052510→54a27dc), clean-git loophole closed (emergency_blocker_bundle added), consistency checker strengthened (10 checks), oracle preflight re-run 6 FAIL, TC-0029 DEC-034 PASS (7/7 factors, 88/100), FODT Gate 1 human-review packet created, master-plan v2.36
visibility: internal
publish_allowed: false
notes: Place this folder at repo root as /memory. These files are for agent context and must not supersede plans/master-plan.md.
---

# 09 — Current State (Phase 3: Gate 5 PASSED, Gate 6 oracle_blocked_missing_tool)

This file captures the current state after run040. Gates 1-5 PASSED. Gate 5 approved by Babar Raza (2026-05-06, run035). TC-0024 CLOSED. Oracle preflight blocked (LibreOffice not installed — 6 consecutive fails: run035-run040). Oracle harness hardened (run036): oracle_common.py, FORMAT_FACTORY_SOFFICE env var, --soffice-path CLI. Oracle provider abstraction added (run037): provider_registry.yaml, validate_oracle_environment.py, docs/oracle-provider-strategy.md. Oracle harness self-test added (run038): tools/oracle/self_test_oracle_harness.py (HARNESS_SELF_TEST_ONLY; PASS 4/4). Operator handoff added (run038): acquisition-packs/fods/oracle-operator-handoff.md. Consistency enforcement tool added (run039): tools/evidence/check_current_state_consistency.py — strengthened run040 (10 checks). Clean-git loophole closed run040 (emergency_blocker_bundle: true added as escape hatch). FODT Gate 1 scoring package (candidate-only, run039): registry/candidates/fodt-gate1-scoring-package.yaml. TC-0029 DEC-034 PASS run040 (7/7 factors, 88/100, Accept band). FODT Gate 1 human-review packet (run040): acquisition-packs/_candidate-shortlists/fodt-gate1-human-review-packet.md. TC-0026 blocked_missing_oracle_tool. TC-0028 in_progress. TC-0029 verification_passed_pending_human_review.

**Last updated:** run040 (run039 independently verified PASS — 44 checks; stale commit 54a27dc fixed; clean-git loophole closed; consistency checker strengthened to 10 checks; oracle preflight re-run 6 FAIL; TC-0029 DEC-034 PASS 7/7; FODT Gate 1 human-review packet created; master-plan.md v2.36).

## Current status

| Item | Status |
|---|---|
| Phase | Phase 3: Gate 5 PASSED, Gate 6 oracle_blocked_missing_tool |
| Phase 0 accepted | YES — 2026-05-04 (run015, human-authorized) |
| Phase 1A complete | YES — FODS scored 93/100 (run015), independently verified (run016) |
| Gate 1 status | **PASSED** — approved by Babar Raza, 2026-05-04 (run017) |
| Gate 2 status | **PASSED** — approved by Babar Raza, 2026-05-05 (run023); patent search waived; fast-path confirmed |
| Gate 3 status | **PASSED** — approved by Babar Raza, 2026-05-05 (run028); DEC-034 verified run027 |
| Gate 4 status | **PASSED** — approved by Babar Raza, 2026-05-06 (run033) |
| Gate 5 status | **PASSED** — approved by Babar Raza, 2026-05-06 (run035 human-authorized prompt); 6 entities, 87 checks PASS; TC-0024 DEC-034 PASSED run034; TC-0024 CLOSED run035 |
| Gate 6 status | **oracle_blocked_missing_tool** — LibreOffice not installed (6 consecutive preflight FAIL: run035/036/037/038/039/040); harness hardened run036; provider abstraction run037; harness self-test + operator handoff run038; consistency enforcement run039 (strengthened run040 — 10 checks); clean-git loophole closed run040 |
| Active formats | fods (gate_1: passed; gate_2: passed; gate_3: passed; gate_4: passed; gate_5: passed; gate_6: oracle_blocked_missing_tool) |
| Registry | FODS entry: gate_5: passed (Babar Raza 2026-05-06); gate_6: oracle_blocked_missing_tool; next_allowed_action: install_oracle_tool_then_execute_tc0026 |
| Spec Workbench v1 | created run030 (local-only): .local/spec-cache/fods/1.3/workbench/ — verified-facts.yaml (10 facts), requirement packs (parser/sample/model), task packets, coverage matrices; 205/205 validation PASS |
| FODS acquisition pack | acquisition-packs/fods/ (19 files after run038: + oracle-operator-handoff.md run038) |
| TC-0001 status | COMPLETED — Gate 1 approved (run017) |
| TC-0007 status | completed_independently_verified_run020+run022 |
| TC-0009 status | CLOSED — Gate 2 passed (Babar Raza, 2026-05-05, run023) |
| TC-0010 status | completed — Gate 3 corpus plan complete (run024) |
| TC-0011 status | closed (superseded by run027 combined verification, run028) |
| TC-0012 status | completed — normalization layer complete (run025) |
| TC-0013 status | COMPLETED — Gate 3 corpus executed, validated, independently verified, approved (run028) |
| TC-0014 status | completed — Gate 4 planning package used in run029 execution (verified run030) |
| TC-0015 status | not_started — spec retrieval evaluation; blocked by human review of spec-retrieval-strategy.md |
| TC-0016 status | not_started — FODS vector index pilot; blocked by TC-0015 completion and human approval |
| TC-0017 status | completed — Gate 4 prototype executed run029; 4/4 PASS; TC-0018 verification PASS run030 |
| TC-0018 status | CLOSED — Gate 4 approved by Babar Raza (2026-05-06, run033) |
| TC-0019 status | superseded_by_tc0023 — Gate 5 planning superseded by direct execution in TC-0023 |
| TC-0020 status | not_started — Spec Workbench core (generic); tooling created run030 |
| TC-0021 status | quality_review_verified — 205/205 PASS (run031, verified run032) |
| TC-0022 status | completed_verified — Evidence Bundle Contract system (run031, verified run032) |
| TC-0023 status | **completed** — Gate 5 PASSED (Babar Raza, 2026-05-06, run035) |
| TC-0024 status | **CLOSED** — DEC-034 PASS run034; all checkboxes checked; Gate 5 approved run035 |
| TC-0025 status | **completed** — Gate 6 planning reviewed run035; planning docs created run034 |
| TC-0026 status | **blocked_missing_oracle_tool** — LibreOffice not installed; oracle harness ready at tools/oracle/; blocker wording CORRECTED run038 |
| TC-0027 status | not_started — waiting for TC-0026 completion |
| TC-0028 status | in_progress — shortlist created run038; independently verified run039 (4 claims PASS); presentation for Gate 1 approval pending |
| TC-0029 status | **verification_passed_pending_human_review** — DEC-034 PASS run040; 7/7 factors verified, 88/100, Accept band confirmed; human-review packet ready |
| Samples | 4 Apache-2.0 synthetic FODS samples in samples/by-format/fods/ (run026, validated 4/4 PASS) |
| Spec Navigation Layer | 884 sections, 940 chunks, sample-requirements.yaml, parser-requirements-draft.yaml (run026, local-only) |
| Hybrid Spec Retrieval | docs/spec-retrieval-strategy.md (run027); AGENTS.md Section X; GOVERNANCE.md Section 17 |
| Schemas | schemas/neutral-model/fods/ — neutral model v1 (7 files: model.yaml, model.schema.json, field-map.yaml, coverage-matrix.yaml, validation-rules.yaml, README.md) |
| Prototypes | prototypes/by-format/fods/fods_parser.py (Gate 4 prototype; 4/4 PASS; verified run030+run031+run032) |
| Product source | None |
| CI workflows | None |
| Commercial source folder | Must not exist |
| Specs downloaded | YES — ODF 1.3 Part 3 PDF (24.27 MB, sha256:92cfe64...b066) downloaded run021; stored at .local/spec-cache/fods/1.3/ (gitignored) |
| Evidence contracts | 12 contracts (after run040): + run040-clean-evidence-and-fodt-gate1-verification |
| Latest commit | 411180a (run040 final Section 33 housekeeping) |
| Uncommitted | None — all run040 changes committed |
| Master plan version | 2.36 (run040) |
| AGENTS.md sections | A through Y (25 sections) |

## Run history (run001–run028)

| Run | Stream | Purpose |
|---|---|---|
| run001-run008 | Main execution | Foundation, healing, canonicalization, governance, gate semantics, spec-cache |
| run009 | Main execution | Spec-cache governance cleanup (TC-0007 correction, authorization model) |
| run010 | Memory stream | Memory integration (AGENTS.md Section U, GOVERNANCE.md memory rule, TC-0008) |
| run011 | Main execution | Product source-layout reconciliation (format-first layout propagated to master plan v2.8, all docs) |
| run012 | Memory stream | Memory sync after run009/run010 and human source-layout expectation |
| run013 | Main execution | Source-layout verification; stale notes removed; master-plan v2.9 |
| run014 | Main execution | Phase 0 closure-readiness sprint; full 45-file audit; master-plan v2.10 |
| run015 | Combined sprint | Phase 0 accepted; FODS scored 93/100; baseline commit c9d02da; master-plan v2.11 |
| run016 | Independent verification sprint | All run015 claims verified; DEC-034 added; AGENTS.md Section V; master-plan v2.12 |
| run017 | Gate 1 approval + Phase 2 setup | Gate 1 approved (Babar Raza, 2026-05-04); commit c79f2d1; master-plan v2.13 |
| run018 | State reconciliation (committed via run019) | README, ROADMAP, settings.json, master-plan v2.14 healed |
| run019 | Combined sprint | TC-0007 spec-cache tooling; Gate 2 evidence draft; committed 589c1af; master-plan v2.15 |
| run020 | Independent verification + schema reconciliation | 5 TC-0007 fixes; spec download blocked; evidence strengthened; committed 1e69121; master-plan v2.16 |
| run021 | Combined sprint: spec acquisition + evidence upgrade | ODF 1.3 Part 3 PDF acquired (24.27 MB, sha256:92cfe64...b066); evidence upgraded; committed 138effd; master-plan v2.17 |
| run022 | Independent verification sprint (DEC-034) for run021 | SHA-256 re-verified MATCH; Gate 2 ready for human review; stale state fixed; master-plan v2.18 |
| run023 | Gate 2 approval + Phase 3 setup | Gate 2 PASSED (Babar Raza, 2026-05-05); TC-0009 closed; TC-0010 activated; master-plan v2.19 |
| run024 | Gate 3 corpus planning | TC-0010 executed; sample-sources.md drafted; normalization started; master-plan v2.20 |
| run025 | Spec normalization layer | Full extraction: 782 pages, 2.16M chars; citations.yaml; master-plan v2.21 |
| run026 | Gate 3 corpus execution + navigation layer | 4 FODS samples created 4/4 PASS; 884 sections, 940 chunks; master-plan v2.22; committed 8871777 |
| run027 | Independent verification + stale state + Hybrid Spec Retrieval | 21 checks PASS; SHA-256 hashes computed; Gate 3 → sample_corpus_verified_pending_human_review; docs/spec-retrieval-strategy.md; TC-0015/0016; AGENTS.md X; committed 09ee31f; master-plan v2.23 |
| run028 | Gate 3 approval + Gate 4 planning package | Gate 3 PASSED (Babar Raza, 2026-05-05); TC-0013 completed; TC-0014 planning_ready; parser planning docs; TC-0017/TC-0018 created; memory updated; master-plan v2.24; committed 5c93b88 |
| run029 | Gate 4 prototype creation + validation | TC-0017 executed; fods_parser.py created; 4/4 PASS (PT-001–PT-004); TC-0019 created; registry/TC/memory updated; master-plan v2.25 |
| run030 | TC-0018 DEC-034 verification + Spec Workbench v1 + stale fixes + parser planning updates | TC-0018 PASS (4/4 re-verified); Spec Workbench v1 (local-only, 205/205 PASS); TC-0020/TC-0021 created; registry gate_4 → prototype_verified_pending_human_review; master-plan v2.26; committed 9382e66+4ca85ad |
| run031 | run030 independent verification + Evidence Bundle Contracts + TC-0021 quality review + Gate 4 review packet | 30/30 checks PASS; tools/evidence/ system created; TC-0022; workbench 205/205 PASS; TC-0018 rerun 4/4 PASS; gate4-human-review-packet.md; AGENTS.md Y; GOVERNANCE.md 18; master-plan v2.27; committed 40f4ae5+17bceff |
| run032 | run031 independent verification + stale fixes + reusable contracts + Gate 5 prep | 31/31 checks PASS; TC-0022→completed_verified; TC-0021→quality_review_verified; 4 reusable contracts; gate5-planning-checklist.md; master-plan v2.28 |
| run033 | run032 verification + Gate 4 approval + TC-0018 closed + Gate 5 neutral model (TC-0023) + TC-0024/TC-0025 | Gate 4 PASSED (Babar Raza); neutral model v1 (6 entities, 4/4 PASS); master-plan v2.29 |
| run034 | run033 verification + evidence hardening + TC-0024 DEC-034 + Gate 5 review + Gate 6 planning + TC-0026/TC-0027 | TC-0024 PASS (87 checks, 0 errors); evidence builder/validator hardened; gate5-human-review-packet.md; gate6 planning docs; master-plan v2.30 |
| run035 | run034 verification + Gate 5 approval + TC-0024 closure + Gate 6 oracle preflight + oracle harness | Gate 5 PASSED (Babar Raza, 2026-05-06); TC-0024 CLOSED; TC-0023/TC-0025 COMPLETED; oracle preflight FAIL (LibreOffice not installed); tools/oracle/ harness created; gate6-oracle-blocker-report.md; master-plan v2.31 |
| run036 | run035 independent verification PASS + oracle harness hardening + stale path fixes + installation checklist + evidence validator fix | Verified 5 run035 commits; oracle_common.py NEW (shared constants+discovery); FORMAT_FACTORY_SOFFICE env var; --soffice-path CLI; all tools rewritten to use oracle_common; oracle preflight re-run: FAIL (same, 10 candidates); stale path refs fixed (TC-0026/TC-0027/gate6 docs); oracle-installation-checklist.md NEW; gate6-oracle-blocker-report.md hardened; validator fix (git-status-final.txt OR git-status.txt); master-plan v2.32 |
| run037 | run036 independent verification PASS + stale state fixed + oracle provider abstraction + --check-no-pending validator + negative tests + oracle preflight re-run 3 | Verified 3 run036 commits (8acd48d+82281e6+3216dcf); stale fixes (master-plan header 82281e6→3216dcf, memory/09); provider_registry.yaml + validate_oracle_environment.py + oracle-provider-strategy.md NEW; oracle-provider-options.md NEW (4 alternatives evaluated); --check-no-pending flag added to validator; 4 negative tests PASS; oracle preflight 3rd FAIL; blocker report updated; master-plan v2.33. Commits: de29c97 + f964eba + a35b089. |
| run038 | run037 independent verification PASS + stale commit fixed (f964eba→a35b089) + TC-0026 blocker wording fixed + oracle preflight re-run 4 FAIL + harness self-test + operator handoff + next-format candidate shortlist (TC-0028) | Verified run037 (BUNDLE_VALIDATION: PASS, verdict.md PASS, a35b089 confirmed as actual latest commit); stale commit f964eba→a35b089 fixed in master-plan/memory/registry; TC-0026 "Blocking: Gate 6 human approval" corrected to "Blocking: LibreOffice missing"; oracle preflight 4th FAIL (ORACLE_ENV: BLOCKED); self_test_oracle_harness.py NEW (HARNESS_SELF_TEST_ONLY — not Gate 6 evidence); oracle-operator-handoff.md NEW; candidate shortlist: registry/candidates/odf-flat-family-shortlist.yaml + acquisition-packs/_candidate-shortlists/odf-flat-family-next-candidates.md + TC-0028 (candidate-only, no Gate 1 approval); master-plan v2.34. |
| run039 | run038 independent verification PASS + stale commit fixed (998412c→bc2bdf8) + consistency enforcement tool + oracle preflight re-run 5 FAIL + harness self-test confirmed PASS + candidate shortlist independently verified + FODT Gate 1 scoring package (candidate-only) + ODF reuse strategy | Verified run038 (BUNDLE_VALIDATION: PASS, all 4 commits confirmed, bc2bdf8 actual latest); stale commit 998412c→bc2bdf8 fixed; tools/evidence/check_current_state_consistency.py NEW; negative tests added; oracle preflight 5th FAIL (ORACLE_PREFLIGHT: FAIL); harness self-test PASS 4/4; candidate shortlist verified (4 checks PASS: FODT estimate supported, pipeline reuse confirmed, legal category correct, WIP check correct); FODT Gate 1 scoring package: registry/candidates/fodt-gate1-scoring-package.yaml (candidate-only, no Gate 1 approval); docs/odf-flat-family-reuse-strategy.md NEW; TC-0028 → in_progress; TC-0029 created (FODT Gate 1 scoring); master-plan v2.35. |
| run040 | run039 independent verification PASS (44 checks) + stale commit fixed (d052510→54a27dc) + clean-git loophole closed + consistency checker strengthened (10 checks) + oracle preflight re-run 6 FAIL + TC-0029 DEC-034 PASS (7/7, 88/100) + FODT Gate 1 human-review packet | Verified run039 (44 checks PASS; 5 commits: 48f6a0d+8cd2ed2+075edca+d052510+54a27dc; BUNDLE_VALIDATION: PASS; 3 issues documented). Stale fixes: master-plan header d052510→54a27dc, memory/09 stale→54a27dc. CURRENT_STATE_CONSISTENCY: PASS. Clean-git loophole closed: validator+builder now always fail on dirty git unless emergency_blocker_bundle: true; base-run.yaml updated (require_clean_git: true, emergency_blocker_bundle: false); 2 new negative tests (6/6 total PASS). Consistency checker → 10 invariants. Oracle preflight 6th FAIL (6 consecutive FAIL). TC-0029 DEC-034 PASS: 7/7 scoring factors verified, 88/100 confirmed, Accept band confirmed. fodt-gate1-human-review-packet.md created. TC-0029 → verification_passed_pending_human_review. README/ROADMAP/registry/settings.json/oracle-provider-strategy.md/gate6-oracle-blocker-report.md updated. master-plan v2.36. |

## Latest known evidence bundles

```text
run015: phase0-run015-phase0-acceptance-and-scoring-[timestamp].zip
run016: run016-independent-verification-sprint.zip
run017: run017-gate1-approval-phase2-setup-[timestamp].zip
run021: run021-spec-acquisition-and-gate2-upgrade-20260504.zip (canonical; 74 entries)
run027: run027-verify-gate3-hybrid-retrieval-[timestamp].zip (20 entries — see note below)
run028: run028-gate3-approval-gate4-planning-[timestamp].zip (102 entries)
run029: run029-gate4-parser-prototype-[timestamp].zip ← CURRENT (pending creation)
```

Note: run027 bundle had only 20 entries (missing memory files). run028 had 102 entries (full bundle).

## Source layout (PROPAGATED — run011, CONFIRMED run013)

The format-first source layout is in `plans/master-plan.md` v2.8+:

- `src/net/{format}/` — .NET product workspace per format (e.g., `src/net/fods/`)
- `src/python/{format}/` — Python FOSS product workspace per format (e.g., `src/python/fods/`)

Old paths are OBSOLETE: `src/python/open-source/`, `src/dotnet/open-source/`, `src/dotnet/commercial/`. Do not create these.

.NET FOSS packaging: deferred as DEC-033. Must resolve before Gate 10 .NET release.

## Spec Navigation Layer (run026)

Local artifacts at `.local/spec-cache/fods/1.3/normalized/` (gitignored):
- `text.txt` — full extracted spec text (2.16M chars, 782 pages)
- `sections.jsonl` — 884 sections with page ranges
- `chunks.jsonl` — 940 chunks with section associations
- `page-map.yaml` — 705 page entries
- `sample-requirements.yaml` — 38 sample requirements
- `parser-requirements-draft.yaml` — 10 parser requirements (basis for committed parser-requirements.md)
- `citations.yaml` — spec citation index

Query tool: `tools/spec-normalize/query_normalized_spec.py` (Tier 1 + Tier 2)

## Gate 3 sample corpus (run026 + run028)

| File | SHA-256 | Status |
|---|---|---|
| samples/by-format/fods/minimal-spreadsheet.fods | sha256:a790b18a... | PASS |
| samples/by-format/fods/multi-sheet-basic.fods | sha256:669b60be... | PASS |
| samples/by-format/fods/typed-values-basic.fods | sha256:c873322d... | PASS |
| samples/by-format/fods/formula-basic.fods | sha256:72b06541... | PASS |

All Apache-2.0, project-owned synthetic. SHA-256 hashes independently verified run027.

## Next required actions

1. **Install LibreOffice** on dev machine.
2. Run `python tools/oracle/preflight_oracle.py` to confirm.
3. Issue explicit TC-0026 execution prompt (naming LibreOffice path + version) to execute Gate 6 oracle comparison.
4. After TC-0026: TC-0027 Gate 6 DEC-034 independent verification (separate explicit prompt).
5. After TC-0027: Gate 6 human approval (Babar Raza).

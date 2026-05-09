# Master Plan: format-factory

**Document type:** Living Master Plan
**Authority level:** Single Operational Authority
**Project:** format-factory
**Version:** 2.47 (run051: FODS Phase 4 Python FOSS source COMPLETED -- TC-0050; src/python/fods/ 6 files; tests/python/fods/ 5 test files; 19/20 IR-FODS implemented; iterparse streaming) (run050: FUL repair 20/20 FODS 15/15 FODT; FODT Gate 9 PASSED; FODT Gate 10 PLANNING_READY; FODS Gate 11 PLANNING_READY; Phase 4 plans created; FUL validator tool) (run049: Format Understanding Packages compiled — FUL-001 schemas (6), FUL-002 FODS 6 files, FUL-003 FODT 6 files partial; stale state repairs; contract closure policy patched; XML-first consolidation; LLM policy preservation confirmed)
**Last updated:** 2026-05-09
**Current phase:** Phase 3: FODS Gates 1-10 ALL PASSED; Gate 11 planning_ready. FODT Gates 1-8 ALL PASSED; Gate 9 product-mapping planning_ready.
**Current status:** FODS: Gates 1-10 ALL PASSED. Gate 10 APPROVED Babar Raza 2026-05-08 (run048; Tiers 0-2, 12 features; format-factory-fods v0.1.0; TC-0044 COMPLETED). Phase 4 Python FOSS source CREATED (run051; TC-0050 COMPLETED; src/python/fods/ 6 files; 19/20 IR-FODS; iterparse streaming). Gate 11 planning_ready (TC-0047 not_started, blocked DEC-033). FODT: Gates 1-9 ALL PASSED. Gate 9 PASSED (TC-0048 COMPLETED; tier-map.yaml v1.0; DEC-034 PASS 10/10 inline; run050). Gate 10 planning_ready (TC-0049 not_started). Format Understanding Layer: FUL-001 schemas (run049; 6 schemas); FUL-002 FODS COMPLETED (run049); FUL-003 FODT COMPLETED (run050). last_completed_run: run051. Exact final HEAD in bundle-metadata/git-log.txt (see docs/current-state-and-evidence-authority.md).
**Phase 1 allowed:** YES — Phase 0 accepted (run015) and independently verified (run016).
**Phase 2 allowed:** YES — Gate 1 passed (run017, Babar Raza, 2026-05-04).
**Phase 3 allowed:** YES — Gate 2 passed (run023, Babar Raza, 2026-05-05). Gate 3 PASSED (run028, Babar Raza, 2026-05-05). Gate 4 PASSED (run033, Babar Raza, 2026-05-06). Gate 5 PASSED (run035, Babar Raza, 2026-05-06).
**FODT Gate 6 allowed:** YES — Gate 6 PASSED (Babar Raza, 2026-05-08, run047). Gate 7 fuzz planning_ready; execution requires explicit prompt.
**Commit allowed:** YES — run049 authorized by execution prompt.
**Next required action:** (1) FODS Gate 11: DEC-033 must be resolved, then explicit TC-0047 execution prompt. (2) FODT Gate 10: explicit TC-0049 execution prompt. (3) FODS Phase 4 .NET: blocked by DEC-033 (TC-0051). (4) FODT Phase 4 Python: explicit TC-0052 execution prompt after FODT Gate 10.

---

## Section 1 — Non-Negotiable Operating Rules

These rules override convenience, speed, and agent summaries. They are permanent and apply to every session.

1. No prompt is provided unless explicitly requested by the human.
2. Every prompt must clearly state PLAN MODE or EXECUTION MODE at the top.
3. Every human comment, pasted summary, and problem must be addressed — nothing may be silently skipped.
4. Agents must be guided systematically to prevent drift. Never rely on an agent's in-context memory across sessions.
5. Agent verdicts, summaries, and results must always be challenged. Never accept an agent's self-assessment at face value.
6. Before deciding any next step, the latest evidence or source bundle must be uploaded, extracted, and inspected. The bundle contents must be challenged against the agent summary.
7. Every execution prompt must require the agent to produce an evidence or source bundle and print the absolute Windows path to the zip as the final line.
8. No gap may be ignored. Every gap must be logged in this master plan's Gap Register before proceeding.
9. Plan prompts must include detailed "fix this plan" instructions, adversarial challenge questions, and a self-challenge section.
10. Execution prompts must define: allowed files, forbidden files, validation checks, evidence bundle requirements, and stop conditions.
11. No product code before required gates. Python product source (`src/python/{format}/`) may only be created after: (1) Gates 1-9 complete, (2) Gate 9 human approval recorded in registry, (3) implementation taskcards exist, and (4) an explicit Phase 4 Python implementation execution prompt is issued. Gate 10 is OSS release readiness, not the authorization to start writing Python source. .NET product source (`src/net/{format}/`) follows the same gate sequence with an explicit Phase 4 .NET implementation execution prompt.
12. No .NET commercial-tier source within `src/net/{format}/` before all of the following: (1) Gate 10 passed, (2) Decision DD3 (commercial isolation) resolved, (3) commercial implementation taskcards exist, and (4) an explicit commercial implementation execution prompt is issued. Gate 11 is commercial release readiness, not the authorization to start writing commercial source. The .NET FOSS packaging model within `src/net/{format}/` is deferred — see DEC-033.
13. No commit unless explicitly requested by the human. An agent must never commit on its own initiative.
14. No gate may be self-approved. All 11 gates require human approval.
15. No Phase 1 work may begin until Phase 0 is reviewed and accepted by the human.
16. Any agent-produced request for human review (gate approval, phase acceptance, scoring evidence approval, commit acceptance, or release readiness) must first pass an independent agent verification sprint in a separate execution session. The human must not be asked to approve until independent verification has been completed and recorded. See DEC-034 and AGENTS.md Section V.

---

## Section 2 — Project Purpose

`format-factory` is a repeatable **File Format Acquisition System**.

**"File format hacking" in this project means:**
- Writing legal parsers, converters, importers, exporters, validators
- Building compatibility tooling, neutral intermediate models, sample analyzers
- Operating acquisition agents that gather format evidence from public sources
- Studying public format specifications and open test corpora
- Comparing implementations against spec-conformant reference outputs

**"File format hacking" does NOT mean:**
- Breaking into systems or bypassing security controls
- Unsafe or legally questionable reverse engineering
- Acquiring samples from unauthorized sources
- Building tools that circumvent DRM, access controls, or copyright protections
- Any work that requires reverse engineering without explicit spec permission

The project goal is to build a production-quality pipeline for acquiring format knowledge and turning it into open-source and commercial tooling.

---

## Section 3 — Desired End State

| Product | Language | License | Tier Ceiling | Source Layout | Status |
|---|---|---|---|---|---|
| Acquisition layer | Python | N/A (internal) | N/A | `tools/`, `acquisition-packs/` | Active Phase 0+ |
| Python FOSS product | Python 3.11+ | Apache-2.0 or MIT | Tier 0–4 | `src/python/{format}/` | Phase 4+ |
| .NET product | net8.0 / net10.0 | Commercial (OSS subset TBD — see DEC-033) | Tier 0–6 | `src/net/{format}/` | Phase 4+ with gate + DD3 controls |
| Python commercial product | — | — | — | — | Deferred indefinitely |

**Key properties of the end state:**
- Format-first source layout: each format gets its own subdirectory within `src/python/` and `src/net/`.
- Product-neutral acquisition layer: format knowledge is acquired once and shared across all product tracks.
- Explicit control over what becomes open source: every artifact is classified before it enters any release.
- .NET commercial tiers (5-6) deferred until Gate 10 + DD3 + explicit commercial prompt.
- .NET FOSS packaging model deferred — see DEC-033.
- All open-source code human-approved before publish.

---

## Section 4 — Feature Tier Model

| Tier | Description | Track |
|---|---|---|
| 0 | Detect format (magic bytes, extension, header) | OSS + Commercial |
| 1 | Read metadata and structure (properties, sheet count, etc.) | OSS + Commercial |
| 2 | Import core content (cells, text, images, basic structure) | OSS + Commercial |
| 3 | Export basic content (write valid output files) | OSS + Commercial |
| 4 | Roundtrip common files with high fidelity | OSS + Commercial |
| 5 | Commercial-grade full fidelity (all features, edge cases) | Commercial only |
| 6 | Advanced repair, optimization, recovery, exotic edge cases | Commercial only |

**Open-source ceiling:** Tier 0–4 (normal). May be adjusted per format with project lead approval.
**Commercial ceiling:** Tier 5–6. Commercial track builds on open-source tiers and extends them.

---

## Section 5 — Living Master Plan Policy

1. `plans/master-plan.md` is the **single operational authority** for this project.
2. It is not a snapshot. It always reflects the current project state.
3. It must be updated at every phase change, gate transition, taskcard status change, decision, gap discovery, risk materialization, and bundle review.
4. Generated summaries (created by agents on request) are read-only snapshots. They must state: "Generated summary — not authoritative. Verify against plans/master-plan.md." They are never committed.
5. It must be reproducible from the repo state plus persisted local artifacts. An agent given the repo, the taskcards, the registry, and the decision/gap/risk registers must be able to verify that this document matches the actual project state.
6. No section may be split out into a separate file in a way that removes it from this document. Sections may be linked to detail files, but a current summary must remain in this document at all times.
7. Agents must update this document after every gate transition as part of the completion artifact.

---

## Section 6 — Current Project State

| Property | Value |
|---|---|
| Current phase | Phase 3: FODS Gates 1-10 ALL PASSED; Gate 11 planning_ready. FODT Gates 1-8 ALL PASSED; Gate 9 product-mapping planning_ready |
| Phase 0 files created | Yes — 45/45 files (41 created run001; 3 added run008; 1 added run010: TC-0008) |
| Phase 0 healing run | Completed (run002) — compliance gaps G-HEAL-001 to G-HEAL-004 resolved |
| Phase 0 accepted | YES — 2026-05-04, run015 (all 36 checks passed; human-authorized acceptance) |
| Phase 1 allowed | YES — Phase 0 accepted |
| Phase 2 allowed | YES — Gate 1 passed (run017, Babar Raza, 2026-05-04) |
| Phase 3 allowed | YES — Gate 2 passed (run023, Babar Raza, 2026-05-05); Gate 3 PASSED (run028, Babar Raza, 2026-05-05); Gate 4 PASSED (run033, Babar Raza, 2026-05-06); Gate 5 PASSED (run035, Babar Raza, 2026-05-06) |
| Active formats in registry | fods (gates 1-10: passed; gate_11: not_started); fodt (gates 1-8: passed; gate_9: planning_ready) |
| Gate 1 status | **PASSED** — Babar Raza, 2026-05-04, score 93/100, run016 verified |
| Gate 2 status | **PASSED** — Babar Raza, 2026-05-05, run023; patent search waived; evidence verified run022 (DEC-034) |
| Gate 3 status | **PASSED** — Babar Raza, 2026-05-05, run028; DEC-034 satisfied run027; 4/4 PASS; SHA-256 verified |
| Gate 4 status | **PASSED** — Babar Raza, 2026-05-06, run033; TC-0018 DEC-034 PASS run030+run031+run032 |
| Gate 5 status | **PASSED** — Babar Raza, 2026-05-06, run035; neutral model 6 entities 19 mappings 4/4 PASS 87 checks; TC-0024 DEC-034 PASS run034 |
| Gate 6 status | **PASSED** — Babar Raza, 2026-05-08, run044; TC-0027 DEC-034 PASS 24/24; ORACLE_COMPARE PASS 3/4 WARN 1/4 |
| Gate 7 status | **PASSED** — Babar Raza, 2026-05-08, run045; GATE7_FUZZ_TEST PASS 18/18 CRASH 0/18 CORRUPT 0/18; DEC-034 PASS 18/18 |
| Gate 8 status | **PASSED** — Babar Raza, 2026-05-08, run046; GATE8_SECURITY_REVIEW: PASS; TC-0038 DEC-034 PASS 20/20; security report: reports/security/fods.md |
| Spec Navigation Layer | COMPLETE (run026): 884 sections, 940 chunks, sample-requirements.yaml, parser-requirements-draft.yaml |
| Spec Workbench v1 | CREATED run030 (local-only): verified-facts.yaml, parser/sample/model requirement packs, task packets, coverage matrices |
| FODS neutral model | PASSED — schemas/neutral-model/fods/ (6 entities, 19 mappings, 21 rules); Gate 5 approved |
| FODT neutral model | PASSED — schemas/neutral-model/fodt/ (7 entities, 26 mappings, 19 rules); FODT_NEUTRAL_MODEL_VALIDATION PASS 4/4; Gate 5 approved |
| Oracle harness | CREATED run035, HARDENED run036 — tools/oracle/ (6 files: oracle_common.py + 5 tools); FORMAT_FACTORY_SOFFICE env var; --soffice-path CLI |
| Acquisition pack | acquisition-packs/fods/ — 12+ files (run035+run036: gate5-human-review-packet, gate6 planning, blocker report, installation checklist) |
| Spec downloaded | YES — ODF 1.3 Part 3 PDF downloaded run021 (24.27 MB); SHA-256 independently re-verified run022: MATCH |
| Samples acquired | YES — 4 synthetic FODS samples (Apache-2.0, project-owned), run026. Validated: 4/4 PASS |
| Prototype created | YES — prototypes/by-format/fods/fods_parser.py (run029); 4/4 PASS; TC-0018 PASS |
| Product source created | No |
| Commits made | (see Section 33) — run046: f659307. |
| Active taskcards | TC-0040 not_started (FODS Gate 9 product mapping); TC-0042 not_started (FODT Gate 6 oracle execution); TC-0043 not_started (FODT Gate 6 DEC-034) |
| Closed/completed taskcards | TC-0018 CLOSED; TC-0024 CLOSED; TC-0023/TC-0025/TC-0026/TC-0027/TC-0032/TC-0033/TC-0034/TC-0035 COMPLETED; TC-0036 COMPLETED (FODS Gate 8 security); TC-0037 COMPLETED (FODT Gate 5 neutral model); TC-0038 COMPLETED (FODS Gate 8 DEC-034 20/20); TC-0039 COMPLETED (FODT Gate 5 DEC-034); TC-0041 COMPLETED (FODT Gate 6 oracle planning) |
| Deferred taskcards | TC-0015 not_started (spec retrieval eval); TC-0016 not_started (vector index pilot); TC-0020 not_started (Spec Workbench core) |
| Last evidence bundle | run048: BUNDLE_VALIDATION PASS (run048-combined-sprint.zip; 448 entries); run049 bundle: built at sprint end |
| Next required action | (1) FODS Gate 11: DEC-033 resolution + explicit TC-0047 prompt. (2) FODT Gate 9: explicit TC-0048 prompt. (3) FUL-001 schema approval + FUL-002/003 compilation (run049). |

---

## Section 7 — Evidence Bundle Inspection Rule

**This rule is absolute and applies before every next prompt.**

Before issuing any next prompt (Phase 1 or otherwise):
1. The latest evidence bundle must be uploaded by the human to an inspection environment.
2. The bundle must be extracted and its contents listed.
3. The bundle contents must be challenged against the agent's summary.
4. At minimum: verify file count, check for forbidden paths, read key files, verify registry is empty, verify no product code exists.
5. If the bundle does not match the summary, log the discrepancy as a gap and issue a healing prompt — not a Phase 1 prompt.
6. No "trust the summary" shortcuts. Evidence rules. Summary is a hypothesis.

**The latest evidence bundle (run014 or most recent) must be inspected before any next prompt is issued.**

---

## Section 8 — Phase Model

### Phase 0: Foundation
**Purpose:** Create governance, policies, directory structure, taskcards, registries, and templates. No format-specific content.
**Allowed:** All 41 foundation files. Local artifacts (.local/).
**Forbidden:** Acquisition packs for specific formats. Samples. Schemas. Prototypes. Product source. CI workflows. Commercial folder. Security/legal reports.
**Completion criteria:** All 45 files exist (41 original + 3 added in run008 + 1 added in run010: TC-0008). Registry empty. Forbidden paths absent. Bundle clean. Human accepts.

### Phase 1A: Pilot Candidate Scoring and Gate 1 Review Preparation
**Purpose:** Score FODS using the scoring model, confirm legal category, create a registry entry with `scored_pending_human_approval` status, and request human Gate 1 approval.
**Allowed:** Scoring artifacts. Registry entry (candidate/scored_pending status only). TC-0001 scoring evidence. `tools/llm/` client code (TC-0005). Project commands (TC-0004). TC-0002, TC-0003 infrastructure work.
**Forbidden:** `acquisition-packs/fods/` — creation is forbidden until human Gate 1 approval is explicitly recorded. Samples. Full spec analysis. Prototypes. Product source. Commercial folder.
**Gate:** Gate 1 (Candidate Accepted) — requires human approval. Agent produces scoring evidence. Human records approval.
**Not allowed until:** Phase 0 accepted by human.

### Phase 1B: Post-Gate-1 Transition (after human Gate 1 approval recorded)
**Purpose:** Record Gate 1 passage in registry, update master plan, prepare for Phase 2.
**Allowed:** Update registry `gate_1.status` to `passed` (confirm human's recorded approval). Update TC-0001 completion record. Prepare Phase 2 taskcard.
**Forbidden:** `acquisition-packs/fods/` — still forbidden until Phase 2 is authorized by an explicit execution prompt. Samples. Prototypes. Product source. Commercial folder.
**Requires:** Human has set `gate_1.status: passed`, `approved_by`, and `approved_date` in `registry/format-registry.yaml` in the current session.

### Phase 2: FODS Evidence and Legal Pack (Gates 2–3)
**Purpose:** Gather spec evidence, acquire sample corpus, complete legal review.
**Allowed:** `acquisition-packs/fods/` — created here after Gate 1 human approval and an explicit Phase 2 execution prompt. `samples/by-format/fods/`. Legal notes. Spec evidence.
**Forbidden:** Parser prototype. Neutral model. Product source.
**Gates:** Gate 2 (Evidence Complete), Gate 3 (Sample Corpus Complete).

### Phase 3: FODS Prototype and Mapping (Gates 4–9)
**Purpose:** Build parser prototype, define neutral model, run oracle comparison, fuzz testing, security review, product mapping.
**Allowed:** `prototypes/by-format/fods/`. `schemas/neutral-model/`. `tests/fixtures/`, `tests/oracle/`, `tests/fuzz/`. `reports/security/`, `reports/legal/`.
**Forbidden:** Product source code. CI workflows. Commercial folder.
**Gates:** Gates 4–9.

### Phase 4+: Product Implementation (Gates 10–11)
**Purpose:** Build Python FOSS product and (if approved) .NET commercial product.
**Allowed:** `src/python/{format}/` after Gate 9 + Python implementation taskcards + explicit Phase 4 Python implementation execution prompt. `src/net/{format}/` after Gate 9 + .NET implementation taskcards + explicit Phase 4 .NET implementation execution prompt. `.github/workflows/`. .NET commercial-tier source within `src/net/{format}/` after Gate 10 + DD3 + commercial implementation taskcards + explicit commercial implementation execution prompt. Gate 11 = commercial release readiness (not creation authorization).
**Not the target layout:** `src/python/open-source/`, `src/dotnet/open-source/`, `src/dotnet/commercial/` are NOT the target directory structure. These obsolete path assumptions are replaced by the format-first layout above.
**Gates:** Gate 10 (OSS Readiness), Gate 11 (Commercial Readiness).

---

## Section 9 — Phase 0 Required Files

All 45 files must exist (41 original + 3 added run008 + 1 added run010). They are expected to exist — not yet formally accepted. Formal acceptance requires human bundle review.

| # | File | Status |
|---|---|---|
| 1 | `.gitignore` | Expected: exists |
| 2 | `.env.example` | Expected: exists |
| 3 | `README.md` | Expected: exists |
| 4 | `AGENTS.md` | Expected: exists |
| 5 | `GOVERNANCE.md` | Expected: exists |
| 6 | `ROADMAP.md` | Expected: exists |
| 7 | `.claude/settings.json` | Expected: exists |
| 8 | `.claude/commands/_readme.md` | Expected: exists |
| 9 | `docs/architecture.md` | Expected: exists |
| 10 | `docs/product-tracks.md` | Expected: exists |
| 11 | `docs/acquisition-workflow.md` | Expected: exists |
| 12 | `docs/gates.md` | Expected: exists |
| 13 | `docs/security.md` | Expected: exists |
| 14 | `docs/legal-and-licensing.md` | Expected: exists |
| 15 | `docs/release-control.md` | Expected: exists |
| 16 | `docs/llm-endpoint-strategy.md` | Expected: exists |
| 17 | `plans/master-plan.md` | Expected: exists (this file) |
| 18 | `taskcards/_template.md` | Expected: exists |
| 19 | `taskcards/TC-0001-pilot-selection.md` | Expected: exists |
| 20 | `taskcards/TC-0002-schema-language.md` | Expected: exists |
| 21 | `taskcards/TC-0003-sdk-baseline.md` | Expected: exists |
| 22 | `taskcards/TC-0004-commands-skills.md` | Expected: exists |
| 23 | `taskcards/TC-0005-llm-endpoint-impl.md` | Expected: exists |
| 24 | `taskcards/TC-0006-release-manifest.md` | Expected: exists |
| 25 | `taskcards/TC-0007-specification-cache.md` | Expected: exists |
| 26 | `docs/specification-cache.md` | Expected: exists |
| 27 | `tools/spec-cache/_readme.md` | Expected: exists |
| 28 | `registry/format-registry.yaml` | Expected: exists |
| 29 | `registry/scoring/_scoring-model.md` | Expected: exists |
| 30 | `acquisition-packs/_template/pack.yaml` | Expected: exists |
| 31 | `acquisition-packs/_template/spec-evidence.md` | Expected: exists |
| 32 | `acquisition-packs/_template/legal-notes.md` | Expected: exists |
| 33 | `acquisition-packs/_template/sample-sources.md` | Expected: exists |
| 34 | `acquisition-packs/_template/parser-notes.md` | Expected: exists |
| 35 | `samples/_policy.md` | Expected: exists |
| 36 | `samples/_provenance.yaml` | Expected: exists |
| 37 | `schemas/_readme.md` | Expected: exists |
| 38 | `prototypes/_readme.md` | Expected: exists |
| 39 | `src/python/_readme.md` | Expected: exists |
| 40 | `src/dotnet/_readme.md` | Expected: exists |
| 41 | `tests/_readme.md` | Expected: exists |
| 42 | `tools/_readme.md` | Expected: exists |
| 43 | `reports/_readme.md` | Expected: exists |
| 44 | `tools/llm/endpoints.yaml` | Expected: exists |
| 45 | `taskcards/TC-0008-memory-sync-command.md` | Expected: exists (added run010) |

---

## Section 10 — Forbidden Paths Before Later Gates

The following paths must NOT exist until their respective gates are approved by a human:

| Path | Allowed From |
|---|---|
| `acquisition-packs/fods/` | Phase 2 only — after human Gate 1 approval AND explicit Phase 2 execution prompt |
| `samples/by-format/` | Gate 3 (Phase 2) |
| `schemas/neutral-model/` | Gate 5 (Phase 3) |
| `prototypes/by-format/` | Gate 4 (Phase 3) |
| `src/python/{format}/` | Phase 4 only — after Gates 1-9 complete, Gate 9 human approval recorded, Python implementation taskcards exist, and explicit Phase 4 Python implementation execution prompt |
| `src/net/{format}/` | Phase 4 only — after Gates 1-9 complete, Gate 9 human approval recorded, .NET implementation taskcards exist, and explicit Phase 4 .NET implementation execution prompt |
| `.NET commercial-tier source in src/net/{format}/` | Commercial implementation only — after Gate 10 passed, DD3 resolved, commercial implementation taskcards exist, and explicit commercial implementation execution prompt |
| `.github/workflows/` | Phase 4 — after product implementation begins and explicit Phase 4 CI/setup execution prompt |
| `src/python/open-source/` | OBSOLETE TARGET PATH — not the intended layout. Do not create. Use `src/python/{format}/` instead. |
| `src/dotnet/open-source/` | OBSOLETE TARGET PATH — not the intended layout. Do not create. |
| `src/dotnet/commercial/` | OBSOLETE TARGET PATH — not the intended layout. Do not create. |
| `tests/fixtures/` | Gate 7 (Phase 3) |
| `tests/oracle/` | Gate 6 (Phase 3) |
| `tests/fuzz/` | Gate 7 (Phase 3) |
| `reports/security/` | Gate 8 (Phase 3) |
| `reports/legal/` | Gate 2 (Phase 2) |

Agents must verify these paths do not exist before declaring phase compliance. The presence of any forbidden path is a compliance failure.

---

## Section 11 — Agent Operations Layer

### Primary Executor
Claude Code (VS Code) is the primary agent executor for all project phases.

### Secondary Executor
Codex (GitHub Copilot / OpenAI API) is an optional secondary executor. It may be used for code review, schema cross-check, or .NET prototype review when explicitly instructed. Codex output must be tagged `generated_by: codex`. Codex may not approve gates or commit.

### Agent Required Actions (Before Any Task)
1. Read `AGENTS.md` and verify the current allowed phase.
2. Read `plans/master-plan.md` and note current phase, allowed actions, forbidden actions.
3. Check `.local/artifact-index.yaml` for existing artifacts before creating new ones.
4. Identify the active taskcard and its acceptance criteria.

### Agent Required Actions (During Task)
5. Obey phase rules. Never perform Phase N+1 work during Phase N.
6. Reuse valid existing artifacts (reuse-before-regenerate rule).
7. Log every gap immediately — do not proceed over an unlogged gap.
8. Update `.local/artifact-index.yaml` for every artifact created or modified.
9. Write run record to `.local/llm-logs/` in JSONL format.

### Agent Required Actions (After Task)
10. Self-challenge: answer all required questions before marking work complete.
11. Produce evidence bundle (in execution mode). Print absolute path as final line.
12. Update `plans/master-plan.md` for phase transitions and gate results.
13. Never approve gates. State: "Gate X criteria met. Awaiting human approval."
14. Never commit unless the human explicitly says to commit.

---

## Section 12 — Plan Mode vs Execution Mode

| Action | Plan Mode | Execution Mode |
|---|---|---|
| Create, edit, delete repo files | FORBIDDEN | Allowed per phase rules |
| Create evidence bundles | FORBIDDEN | Required at phase/gate completion |
| Print intended bundle path | Required (intended only) | Print actual absolute path |
| Score formats | FORBIDDEN | Allowed Phase 1+ |
| Create acquisition packs | FORBIDDEN | Allowed after Gate 1 |
| Approve gates | FORBIDDEN | FORBIDDEN (human only) |
| Update plans/master-plan.md | FORBIDDEN | Required at gate transitions |
| Run bash commands or scripts | FORBIDDEN | Allowed per phase rules |
| Create local artifacts (.local/) | FORBIDDEN | Allowed |
| Access .env or secrets | FORBIDDEN | Never — use env var names only |
| Commit to git | FORBIDDEN | FORBIDDEN unless human asks |
| Push to remote | FORBIDDEN | FORBIDDEN unless human asks |

In plan mode: output the plan, intended bundle path, and file manifest only. Zero file writes.

---

## Section 13 — Commands and Skills Governance

### Location
Project-level commands live at `.claude/commands/`. Each command is a Markdown file. The filename becomes the slash command name. Commands are committed and versioned.

### Current State
Phase 0 contains only `.claude/commands/_readme.md`. No functional commands exist yet.

### Planned Commands (Phase 1 via TC-0004)

| Command | Purpose | Phase Available |
|---|---|---|
| `/score-format` | Apply scoring model to a format candidate | Phase 1 |
| `/create-taskcard` | Create a new taskcard from the template | Phase 1 |
| `/check-gate` | Verify gate criteria before human approval is requested | Phase 1 |
| `/create-acquisition-pack` | Initialize an acquisition pack from template | Phase 1 |
| `/reproduce-master-plan` | Generate current-state summary from repo artifacts | Phase 1 |
| `/build-evidence-bundle` | Build and validate an evidence bundle for the current phase | Phase 1 |
| `/check-release-boundary` | Verify that no commercial artifacts are in OSS release scope | Phase 3+ |

### Versioning and Logging
Every command file includes a front-matter block with `version`, `last-updated`, `phase-available`, `gate-required`. Version is incremented when behavior changes. When an agent uses a command, it records `commands_used: ["/command-name"]` in its run record.

### Non-Bypass Rule
When a project command exists for a task, the agent must use it rather than re-implementing the task ad hoc. If no command exists and one should, the agent logs a gap and does the task manually this one time only.

---

## Section 14 — LLM Endpoint and Model Strategy

### Supported Endpoint Classes

| Class | Description | Config |
|---|---|---|
| Claude native | Claude Code / Anthropic API — primary executor | `auth_env: ANTHROPIC_API_KEY` |
| Codex | OpenAI / GitHub Copilot — optional secondary | `auth_env: OPENAI_API_KEY` (disabled by default) |
| llm.professionalize.com | Remote specialized endpoint | `auth_env: PROFESSIONALIZE_API_KEY` |
| Local discoverable | Ollama, LM Studio at localhost | No auth required |

### Key Rules
- Endpoint configuration lives in `tools/llm/endpoints.yaml` (committed, no secrets).
- Secrets live in `.env` (gitignored, never committed). `.env.example` shows variable names only.
- No real LLM API calls in Phase 0. Phase 0 is documentation and governance only.
- Endpoint client implementation is TC-0005 scope, Phase 1.
- Local discovery probes `localhost:11434` (Ollama) and `localhost:1234` (LM Studio). Results cached in `.local/discovered-models.yaml`.
- Fallback: if preferred endpoint unavailable, try next by priority. If none available, log `ENDPOINT_UNAVAILABLE` and stop.
- Prompts and responses are local-only (`.local/llm-cache/`). Never committed.

### Model Selection by Task Type

| Task Type | Preferred | Fallback |
|---|---|---|
| Spec analysis, evidence drafting | Claude (large) | llm.professionalize.com |
| Prototype code review | Claude or Codex | Claude |
| Oracle comparison analysis | Claude | Local model |
| Scoring calculation | Claude | Local model |
| Batch sample analysis | Local model | llm.professionalize.com |
| Privacy-sensitive tasks | Local model only | None |

---

## Section 15 — Persistent Artifact Model

### Artifact Storage by Type

| Artifact Type | Format | Committed | Local-Only |
|---|---|---|---|
| Plans, governance, docs | Markdown | Yes | No |
| Registry, config | YAML | Yes | No |
| Taskcards | Markdown | Yes | No |
| Acquisition pack evidence | Markdown/YAML | Yes | No |
| Samples (text/binary) | As-is (+ LFS for large) | Yes | No |
| Schemas, prototypes | YAML/JSON/Python/C# | Yes | No |
| Oracle outputs | JSON/YAML | Yes | No |
| Release manifests | YAML | Yes | No |
| Product source | Python/C# | Yes | No |
| Specification cache files | PDF/HTML/XML | No | Yes |
| LLM run records | JSONL | No | Yes |
| LLM prompt/response cache | JSONL | No | Yes |
| Discovered model list | YAML | No | Yes |
| Artifact index | YAML | No | Yes |
| Evidence bundles | ZIP | No | Yes |
| Generated summaries | Markdown | No | Yes |
| `.env` secrets | `.env` | Never | Yes |

### .local/ Directory (Gitignored, Never Committed)
```
.local/
  artifact-index.yaml      # Index of all known artifacts
  llm-logs/                # Agent run records (JSONL)
  llm-cache/               # Prompt/response cache (JSONL)
  discovered-models.yaml   # Local LLM model discovery cache
  evidence-bundles/        # Phase evidence ZIPs awaiting human upload
  spec-cache/              # Downloaded specification files (local-only, never committed)
                           # See docs/specification-cache.md and tools/spec-cache/_readme.md
```

`.local/` can be rebuilt from committed state if lost (fresh clone). Rebuild procedure is documented in `docs/architecture.md`.

---

## Section 16 — Reuse, Cache, and Idempotency Strategy

### Reuse Decision Table

| Condition | Action |
|---|---|
| Artifact exists, source hash matches | Reuse — log `ARTIFACT_REUSED` in run record |
| Artifact exists, source changed | Refresh — update artifact, update source_hash |
| Artifact marked stale | Regenerate from current inputs |
| Artifact missing | Generate fresh |
| Artifact exists, provenance unclear | Flag for human review — do not use |

### Rules
1. Before creating any artifact, check `.local/artifact-index.yaml`.
2. Before creating a taskcard, check `taskcards/` for an existing one with the same format-id and gate.
3. Before acquiring a sample, check `samples/_provenance.yaml` for the same source URL.
4. Before adding a registry entry, check for an existing entry with the same format-id.
5. Before generating a security/legal report, check `reports/` for an existing current report.
6. Monthly refresh: re-check all spec source URLs and sample source URLs. Mark stale. Create refresh taskcards. Do NOT regenerate automatically.

---

## Section 17 — Open-Source Release Control

### Visibility Classes

| Class | Meaning | Publishable |
|---|---|---|
| `public` | Safe for OSS release. Intentionally public. | Yes |
| `internal` | Working documents, plans. Not external. | No |
| `commercial` | Commercial-tier artifacts. Never in OSS release. | Commercial only |
| `evidence-only` | Acquisition evidence. Informs product, not released. | No |
| `generated` | Machine-generated content. Requires human review before publish. | Conditional |
| `blocked` | Legally restricted, PII, or prohibited. | Never |

### Default Classification Rules

| Artifact Type | Default Visibility |
|---|---|
| Plans, governance, architecture | `internal` |
| Registry (after Gate 9) | `public` |
| Acquisition pack evidence | `evidence-only` |
| Samples (confirmed open license) | `public` |
| Samples (uncertain license) | `blocked` until confirmed |
| Schemas (after Gate 10) | `public` |
| Product source (`src/python/{format}/` — FOSS) | `public` after Gate 10 |
| Product source (`src/net/{format}/` — .NET FOSS tiers, if released) | `public` after Gate 10 (DEC-033 deferred) |
| Product source (`src/net/{format}/` — commercial tiers) | `commercial` |
| LLM prompts/responses | `generated` (may be `blocked` if containing spec text) |
| Security/legal reports | `internal` (may be `public` after redaction) |
| Release manifests | `public` |
| `.env` secrets | `blocked` — never committed |

**Default rule:** When uncertain, classify as `internal`. Never default to `public`.

### Open-Source Eligibility
A file is open-source eligible if: `visibility: public`, `publish_allowed: true`, `open_source_allowed: true`, `release_blockers` is empty, and license is Apache-2.0 or MIT compatible.

### Commercial Exclusion
Commercial artifacts (`visibility: commercial`) are excluded from OSS releases by: physical separation within `src/net/{format}/` (commercial tiers isolated), release manifest exclusion, and CI boundary check (Phase 4+). The exact commercial isolation mechanism within the format-first layout is defined at Phase 4 time (DEC-033 deferred).

### Release Manifest Generation
TC-0006 (Phase 3+) builds the release manifest generator. Until then, manifests are created manually. Every release requires human review of the manifest before publish.

---

## Section 18 — Artifact Visibility Schema

Every artifact in `acquisition-packs/`, `samples/`, `reports/`, `schemas/`, and `src/` must carry front matter conforming to this schema. Phase 0 governance files use the hybrid classification policy below.

```yaml
artifact_id: string          # Unique ID, e.g. "fods-spec-evidence-v1"
artifact_type: string        # plan|registry|taskcard|acquisition-pack|sample|schema|
                             # prototype|report-security|report-legal|release-manifest|
                             # source-python|source-dotnet-oss|source-dotnet-commercial|
                             # llm-prompt|llm-response|run-record|tool-script
path: string                 # Relative path from repo root
format_id: string|null       # e.g. "fods", null for non-format artifacts
product_family: string|null  # cells|words|slides|imaging|diagram|archive|null
visibility: string           # public|internal|commercial|evidence-only|generated|blocked
publish_allowed: boolean
license: string|null         # SPDX identifier e.g. "Apache-2.0"
provenance_required: boolean
provenance_status: string    # confirmed|unconfirmed|missing|not-applicable
source_hash: string|null     # sha256:<hash> of primary source
generated_by: string|null    # human|claude|codex|tool:<name>|null
generated_at: string|null    # ISO-8601 datetime
reusable: boolean
refresh_policy:
  trigger: string            # source-changed|spec-version-changed|tool-version-changed|manual|age
  max_age_days: integer|null
stale: boolean
open_source_allowed: boolean
commercial_allowed: boolean
release_blockers: list       # empty means no blockers
notes: string|null
```

### Phase 0 Hybrid Classification Policy

Phase 0 governance files (`.gitignore`, `.env.example`, `AGENTS.md`, `GOVERNANCE.md`, README, ROADMAP, settings files, YAML configs, etc.) are classified via `.local/artifact-index.yaml` rather than inline YAML front matter. This is the **hybrid policy** — approved in run002, documented in `docs/release-control.md` and `AGENTS.md` Section F.

**Rationale:** Config files (`.gitignore`, YAML endpoint files, JSON settings) cannot carry Markdown front matter without breaking file syntax. Standard governance documents (AGENTS.md, GOVERNANCE.md) do not conventionally carry YAML front matter headers. `.local/artifact-index.yaml` provides equivalent classification for all 41 Phase 0 files.

**Phase 1+ rule:** All acquisition artifacts (acquisition packs, samples, schemas, prototypes, product source, reports) must carry inline front matter directly in the file. The hybrid policy applies only to Phase 0 governance files.

---

## Section 19 — Acquisition Workflow

The 9-stage acquisition workflow is defined fully in `docs/acquisition-workflow.md`. Summary:

| Stage | Description | Gate |
|---|---|---|
| 1 | Candidate scoring and pilot selection | Gate 1: Candidate Accepted |
| 2 | Spec and legal evidence gathering | Gate 2: Evidence Complete |
| 3 | Sample corpus acquisition | Gate 3: Sample Corpus Complete |
| 4 | Parser prototype development | Gate 4: Parser Prototype Complete |
| 5 | Neutral model design | Gate 5: Neutral Model Complete |
| 6 | Oracle comparison analysis | Gate 6: Oracle Comparison Complete |
| 7 | Fuzz and malformed-file testing | Gate 7: Fuzz Testing Complete |
| 8 | Security review | Gate 8: Security Review Complete |
| 9 | Product mapping | Gate 9: Product Mapping Complete |

Before Stage 1, agents must check whether the format is already in the registry (idempotency check).
At Stage 2, `spec-evidence.md` must carry front matter conforming to the visibility schema.
At Stage 3, all sample front matter must have confirmed visibility classification and `provenance_status: confirmed`.

**Reuse-before-regenerate applies at every stage.** Check existing artifacts before running any LLM or tool.

---

## Section 20 — Gate Model

All 11 gates require human approval. No agent may self-approve.

| Gate | Name | Phase | Required Artifacts | Authority |
|---|---|---|---|---|
| 1 | Candidate Accepted | 1 | Scoring sheet, pilot rationale, TC-0001 complete | Project lead |
| 2 | Evidence Complete | 2 | `spec-evidence.md`, `legal-notes.md`, spec URL confirmed | Project lead |
| 3 | Sample Corpus Complete | 2 | `sample-sources.md`, provenance confirmed, samples acquired | Project lead |
| 4 | Parser Prototype Complete | 3 | `parser-notes.md`, prototype reads all sample files | Project lead |
| 5 | Neutral Model Complete | 3 | `schemas/neutral-model/<format>.yaml`, design rationale | Project lead |
| 6 | Oracle Comparison Complete | 3 | Oracle comparison report, discrepancies logged | Project lead |
| 7 | Fuzz Testing Complete | 3 | Fuzz results (10K+ iterations), all crashes analyzed | Security reviewer |
| 8 | Security Review Complete | 3 | Security report with sign-off, all threat categories addressed | Security reviewer |
| 9 | Product Mapping Complete | 3 | Product mapping report, tier assignments confirmed | Project lead |
| 10 | Open-Source Readiness | 4 | Release manifest reviewed, boundary check passed | Project lead |
| 11 | Commercial Readiness | 4 | Commercial review, legal review, DD3 resolved | Commercial lead |

**Gate rules:**
- Gates are sequential. Gate N cannot be approved before Gate N-1.
- WIP limits apply (see Section 24).
- Human approval records: approver name, date, and notes in `registry/format-registry.yaml`.
- Master plan must be updated at every gate transition.
- A gate "meets criteria" notification from an agent is not approval. Human reviews and decides.

---

## Section 21 — Legal Category Model

| Category | Description | Action |
|---|---|---|
| 1 — Open Standard RF | OASIS, W3C, IETF RF standards with published specs | Fast-path: proceed |
| 2 — Permissive OSS Implementation | OSS with permissive license; spec from code | Normal path |
| 3 — Published Proprietary Spec (Parser Permitted) | Spec published, parsing explicitly permitted | Normal path with DD2 |
| 4 — Ambiguous Public Documentation | Partial docs, no explicit permission | Requires legal review before Gate 2 |
| 5 — Reverse-Engineered Binary (No Permission) | No spec, no permission; must reverse-engineer | Auto-reject |
| 6 — Blocked | PII, DRM, patent risk unresolved, or otherwise prohibited | Auto-reject |

**Pre-approved formats (Category 1, fast-path):** ODF family (FODS, ODS, ODT, ODP), OOXML (XLSX, DOCX, PPTX), SVG, CSV, JSON, HTML.
**FODS:** Category 1, OASIS ODF 1.3, fast-path eligible.

---

## Section 22 — Oracle Model

- The **specification is the authority**. When a spec says X, X is correct.
- Reference tools (LibreOffice, Excel, etc.) are comparison aids — not truth.
- LibreOffice may be used for ODF/FODS oracle comparison but is not the absolute truth. LibreOffice may have bugs or extensions.
- When a reference tool output disagrees with the spec, the spec wins unless there is explicit evidence that the spec is errata.
- All discrepancies between oracle output and spec must be logged in the oracle comparison report with analysis: spec bug, tool bug, or ambiguity.
- Oracle comparisons are reproducible: tool version, input files, and command are recorded in the comparison report.

---

## Section 23 — Pilot Recommendation

**First pilot: FODS** (Flat OpenDocument Spreadsheet)
- Standard: OASIS ODF 1.3
- Legal category: 1 (Open Standard RF)
- Format family: Cells (spreadsheet)
- Rationale: flat XML (no zip), complete public spec, large existing OSS ecosystem, simple fast-path legal, good gateway to full ODF family.
- Gate 1 scoring completed in run015 (score: 93/100, Accept band, claude-sonnet-4-6).
- Gate 1 independently verified in run016 (all claims PASS, no fabrication).
- Gate 1 approved by Babar Raza on 2026-05-04 (run017). TC-0001 is closed.
- acquisition-packs/fods/ skeleton created run017 (5 files). Updated run019 with Gate 2 evidence draft.
- TC-0009 evidence draft completed run019: spec-evidence.md (primary source, XML structure, security analysis), legal-notes.md (fast-path checklist 4/7 confirmed). Gate 2 status: evidence_draft_pending_independent_verification.
- Spec NOT downloaded (T3 not authorized in run019). All spec claims are [SUPPORTED_BY_RECORDED_URL] or [PLAUSIBLE_PENDING_VERIFICATION].
- TC-0007 spec-cache tooling implemented run019: spec_index.py (library), acquire_spec.py (dry-run default), refresh_check.py (staleness scan).
- Gate 2 awaits: independent verification sprint (DEC-034), project lead fast-path confirmation (3 items), human sign-off.

**Second likely candidate: Gnumeric .gnumeric**
- Open-source, XML-based, category 1 or 2.
- Shares Python tooling interest.
- To be evaluated after FODS Gate 3+ completes.

---

## Section 24 — WIP Limits

WIP limits prevent spreading acquisition effort too thin. Enforced by project lead at phase transitions.

| Stage Band | Gates | WIP Limit |
|---|---|---|
| Early stages (spec/samples) | Gates 1–3 | 3 formats |
| Middle stages (prototype/model/oracle) | Gates 4–6 | 2 formats |
| Late stages (fuzz/security/mapping) | Gates 7–9 | 1 format |
| Product stages | Gates 10–11 | 1 format |

A format counts toward WIP from the moment it enters Gate 1 until it exits Gate 11 or is rejected.

---

## Section 25 — Active Taskcards

| TC ID | Title | Phase | Status | Depends On |
|---|---|---|---|---|
| TC-0001 | Pilot Selection (FODS Gate 1) | 1 | **completed** — Gate 1 approved by Babar Raza (2026-05-04, run017) | Phase 0 acceptance |
| TC-0002 | Schema Language Selection | 1 | not_started | Phase 0 acceptance |
| TC-0003 | SDK Baseline Confirmation | 1 | not_started | Phase 0 acceptance |
| TC-0004 | Commands and Skills Design | 1 | not_started | Phase 0 acceptance |
| TC-0005 | LLM Endpoint Client Implementation | 1 | not_started | Phase 0 acceptance |
| TC-0006 | Release Manifest Generator | 3+ | not_started | Gate 9 |
| TC-0007 | Specification Cache Tooling | 1 | **completed_independently_verified_run020** — spec_index.py schema fixed (run020), acquire_spec.py warning removed (run020), refresh_check.py encoding fixed (run020) | Phase 0 acceptance |
| TC-0008 | Memory Sync Command | 1+ | not_started — planned capability only | Phase 0 acceptance |
| TC-0009 | FODS Phase 2 Spec and Legal Evidence | 2 | **completed** — Gate 2 PASSED (Babar Raza, 2026-05-05, run023). TC-0009 closed. | Gate 1 passed |
| TC-0010 | FODS Gate 3 Sample Corpus Planning | 3 | **planning_ready** — Gate 2 passed (run023); corpus plan verified + spec refs updated (run025); awaiting Gate 3 execution prompt | Gate 2 passed |
| TC-0011 | FODS Gate 3 Independent Verification Sprint | 3 | **closed** — superseded by run027 verification | TC-0013 completion |
| TC-0012 | Specification Normalization Layer | 2+ | **Phase 2 done + Navigation Layer complete** — full extraction (run025), Nav Layer (run026): 884 sections, 940 chunks | Gate 2 passed |
| TC-0013 | FODS Gate 3 Sample Corpus Execution | 3 | **COMPLETED** — Gate 3 PASSED (Babar Raza 2026-05-05, run028) | Gate 3 approval |
| TC-0014 | FODS Gate 4 Parser Prototype Planning | 4 | **completed** — planning package used in run029; TC-0017 executed | Gate 3 PASSED |
| TC-0017 | FODS Gate 4 Parser Prototype Execution | 4 | **completed** — fods_parser.py created run029; 4/4 PASS; TC-0018 PASS run030 | TC-0018 DEC-034 |
| TC-0018 | FODS Gate 4 Prototype Verification | 4 | **verification_passed_pending_human_review** — DEC-034 PASS run030; 4/4 re-verified | Gate 4 human approval |
| TC-0019 | FODS Gate 5 Neutral Model Planning | 5 | **not_started** — blocked by Gate 4 human approval + explicit Gate 5 prompt | Gate 4 PASSED |
| TC-0020 | Spec Workbench Core (all formats) | 3+ | **not_started** — generic tooling created run030; future multi-format validation needed | none |
| TC-0021 | FODS Workbench Quality Review | 3 | **not_started** — v1 seeded run030; quality review after Gate 4 approval | Gate 4 PASSED |

All taskcards are in `taskcards/` as Markdown files. Current phase is Phase 3 (Gate 4 verified pending human approval). TC-0013 COMPLETED. TC-0014 completed. TC-0017 completed. TC-0018 verification_passed_pending_human_review. TC-0020/TC-0021 not_started (created run030).

---

## Section 26 — Decision Register

| ID | Decision | Status | Notes |
|---|---|---|---|
| DEC-001 | "File format hacking" definition | Decided | Legal parsers/converters. Not bypassing security. |
| DEC-002 | Product-neutral acquisition layer | Decided | Format knowledge acquired once, shared across tracks. |
| DEC-003 | Python FOSS product | Decided | Apache-2.0 or MIT. Tier 0–4 ceiling. Format-first layout: `src/python/{format}/`. |
| DEC-004 | .NET product layout | Decided (run011) | Format-first layout: `src/net/{format}/`. .NET workspace covers commercial/full-feature path by default. .NET FOSS packaging deferred — see DEC-033. Old paths `src/dotnet/open-source/` and `src/dotnet/commercial/` are obsolete and must not be created. |
| DEC-005 | .NET commercial tiers | Decided | Tier 5–6 commercial source within `src/net/{format}/`. Commercial source creation authorized after Gate 10 passed + DD3 resolved + commercial taskcards + explicit commercial implementation prompt. Gate 11 is commercial release readiness. |
| DEC-006 | Python commercial product | Deferred | Indefinitely deferred. Not in current roadmap. |
| DEC-007 | Feature tier model (Tiers 0–6) | Decided | See Section 4. |
| DEC-008 | Python 3.11+ | Decided | Python 3.11 minimum. |
| DEC-009 | net8.0 / net10.0 (not net9.0) | Decided | net9.0 reaches EOL May 2026. |
| DEC-010 | Commercial source deferred | Decided (updated run011) | Commercial-tier source within `src/net/{format}/` not created until Gate 10 passed + DD3 resolved + commercial implementation taskcards + explicit commercial implementation prompt. Gate 11 is release readiness, not creation authorization. Old path `src/dotnet/commercial/` is obsolete. |
| DEC-011 | Monorepo, extraction-ready | Decided | Single repo. OSS/commercial separated so OSS can be mirrored. |
| DEC-012 | `plans/master-plan.md` single authority | Decided | See Section 5. |
| DEC-013 | Claude (VS Code) primary executor | Decided | See Section 11. |
| DEC-014 | Codex optional secondary | Decided | Not activated until explicitly instructed. |
| DEC-015 | Endpoint support: Claude + local + professionalize + Codex | Decided | See Section 14. |
| DEC-016 | Everything useful persists on disk | Decided | See Section 15. |
| DEC-017 | `.local/` is local-only, never committed | Decided | Gitignored. |
| DEC-018 | Visibility classification required for every artifact | Decided | From Phase 1 forward. Phase 0 uses hybrid policy. |
| DEC-019 | Phase 0 hybrid classification policy | Decided | run002. Phase 0 files classified via artifact-index.yaml. |
| DEC-020 | SQLite deferred | Deferred | YAML artifact index until >~500 entries or query need. |
| DEC-021 | Commands in Phase 1, directory in Phase 0 | Decided | TC-0004 implements commands in Phase 1. |
| DEC-022 | LLM endpoint implementation in Phase 1 | Decided | TC-0005. No real API calls in Phase 0. |
| DEC-023 | Release manifest generator in Phase 3+ | Decided | TC-0006. |
| DEC-024 | FODS as first pilot | Decided | See Section 23. |
| DEC-025 | Bundle inspection required before next prompt | Decided | Absolute rule — see Section 7. |
| DEC-026 | Gate 9 authorizes implementation planning; explicit Phase 4 prompt authorizes product source | Decided (updated run011) | Gate 9 human approval + implementation taskcards + explicit Phase 4 implementation execution prompt together authorize creation of `src/python/{format}/` and `src/net/{format}/`. Gate 10 is OSS release readiness, not start-of-implementation authorization. Old paths `src/python/open-source/` and `src/dotnet/open-source/` are obsolete. |
| DEC-027 | Gate 10 + DD3 + explicit commercial prompt authorize commercial tiers; Gate 11 is commercial release readiness | Decided | Commercial-tier source within `src/net/{format}/` requires: Gate 10 passed + DD3 resolved + commercial implementation taskcards + explicit commercial implementation execution prompt. Gate 11 is commercial release readiness, not start-of-commercial-implementation authorization. |
| DEC-031 | Python track is the FOSS product path | Decided (run011) | `src/python/{format}/` is the Python FOSS product workspace per format. Feature ceiling: Tier 0-4. License: Apache-2.0 or MIT. One directory per format (e.g. `src/python/fods/`). No `src/python/open-source/` — that path is obsolete. |
| DEC-032 | .NET track is the commercial/full-feature path | Decided (run011) | `src/net/{format}/` is the .NET product workspace per format. Covers commercial/full-feature product path by default. Tier ceiling: 0-6 (commercial). One directory per format (e.g. `src/net/fods/`). No `src/dotnet/open-source/` or `src/dotnet/commercial/` — those paths are obsolete. |
| DEC-033 | .NET FOSS packaging strategy deferred | Deferred (run011) | Whether `src/net/{format}/` includes a separate FOSS-tier packaging model (parallel to Python FOSS) is not yet decided. The .NET workspace covers the full commercial path. If a .NET FOSS package is desired, the master plan must explicitly authorize and describe the separation mechanism before any source folder is created. This decision must be made before the first .NET release at Gate 10. |
| DEC-034 | Agent-requested human review requires independent agent verification first | Decided (run016) | Any agent-produced request for human gate approval, phase acceptance, scoring evidence approval, commit acceptance, or release readiness must first pass an independent agent verification sprint in a separate execution session. The human must not be asked to approve until independent verification is completed and recorded. Exceptions require explicit human waiver in the current session prompt. See AGENTS.md Section V. |
| DEC-028 | `/memory` is persistent project context, not operational authority | Decided | run010. `/memory` provides historical context, decision rationale, and phase evolution. It does not supersede `plans/master-plan.md`, `AGENTS.md`, or `GOVERNANCE.md`. Contradictions between `/memory` and master plan must be logged as gaps and resolved through human governance. |
| DEC-029 | `AGENTS.md` must require memory reads for relevant tasks | Decided | run010. Agents must read minimal required memory files before complex planning, phase transitions, governance changes, and long-running resumed tasks. Task-type-specific additional files are listed in AGENTS.md Section U4. |
| DEC-030 | Memory updates or memory-update taskcards required after major project evolution | Decided | run010. After phase acceptance, gate transition, major decision, major gap, significant healing run, architecture amendment, spec-cache policy change, release control change, or governance change — agent must update `/memory` in scope or create a taskcard. Deferred for this run via TC-0008. |

---

## Section 27 — Gap Register

### Current Blockers

| ID | Gap | Owner | Severity | Blocks |
|---|---|---|---|---|
| ~~G-021~~ | ~~Spec download blocked~~ | — | — | **RESOLVED run021** — ODF 1.3 Part 3 PDF downloaded (24.27 MB, sha256:92cfe64...b066); spec-index.yaml VALID/CURRENT; claims upgraded to SUPPORTED_BY_CACHED_SOURCE |

**Resolution (run021):** T3 authorization confirmed in run021 execution prompt. settings.json deny rule for python *acquire_spec* removed. ODF 1.3 Part 3 PDF downloaded from official OASIS source (https://docs.oasis-open.org/office/OpenDocument/v1.3/os/part3-schema/OpenDocument-v1.3-os-part3-schema.pdf). Spec cached at .local/spec-cache/fods/1.3/. G-021 is resolved.

### Resolved Phase Blockers

| ID | Gap | Resolution | Resolved By |
|---|---|---|---|
| G-001 | Evidence bundle must be inspected before next step | Human-authorized Phase 0 acceptance in run015 prompt; all 36 checks verified | run015, 2026-05-04 |
| G-002 | Phase 0 acceptance not formally recorded | Phase 0 declared accepted; recorded in master-plan v2.11 and memory files | run015, 2026-05-04 |

### Future Gaps (Phase 1+)

| ID | Gap | Owner | Severity | Blocks |
|---|---|---|---|---|
| G-003 | Command and skill file format not finalized | Project lead | Medium | Phase 1 TC-0004 |
| G-004 | LLM endpoint discovery not implemented | Developer | High | Phase 1 TC-0005 |
| G-005 | Model selection policy file not implemented | Developer | Medium | Phase 1 TC-0005 |
| G-006 | Artifact index bootstrap not fully automated | Developer | High | Phase 1 TC-0005 |
| G-007 | Visibility validation tooling not implemented | Developer | High | Phase 2 Gate 3 |
| G-008 | Release manifest generator not built | Developer | Low | Phase 3 Gate 10 |
| G-009 | Reuse/cache invalidation tooling not implemented | Developer | Medium | Phase 1+ |
| G-010 | Prompt/response retention policy needs refinement | Project lead | Medium | Phase 1 |
| G-011 | `/reproduce-master-plan` command not implemented | Developer | Low | Phase 1 TC-0004 |
| G-012 | Neutral schema language not finalized | Developer | High | Phase 1 TC-0002 |
| G-013 | SDK baseline not verified against installed tools | Developer | Medium | Phase 1 TC-0003 |
| G-014 | Commercial repo isolation mechanism deferred | Developer | Medium | Gate 11 |
| G-015 | Test framework not selected | Developer | Medium | Phase 3 |
| G-016 | Version and release cadence not defined | Project lead | Low | Phase 4 |
| G-017 | `docs/architecture.md` folder tree does not include `/memory` folder — minor omission after run010 | Developer | Low | Cosmetic; does not block any gate |
| G-018 | `/sync-memory` command not yet implemented — deferred to Phase 1+ via TC-0008 | Developer | Low | Phase 1+ memory sync automation |
| G-020 | .NET FOSS packaging decision not yet made — deferred as DEC-033 | Project lead | Medium | Must be resolved before Gate 10; does not block Phase 1 |
| G-NORM-001 | ~~PDF extraction library not installed~~ **RESOLVED run025** — pdfminer.six 20260107 installed; full extraction completed: text.txt 2,160,370 chars, pages.jsonl 782 pages, citations.yaml 194+35 refs. | Developer | ~~Medium~~ CLOSED | Resolved run025. |

---

## Section 28 — Healing Gap Register

| ID | Gap | Status | Resolved By |
|---|---|---|---|
| G-HEAL-001 | Bundle missing 10 required audit files | RESOLVED | run002 — staging audit files created |
| G-HEAL-002 | Malformed `ocal/` path in run001 bundle | RESOLVED | run002 — clean `repo/` + `bundle-metadata/` layout |
| G-HEAL-003 | Phase 0 files lacked visibility classification | RESOLVED | run002 — hybrid policy documented in release-control.md + AGENTS.md |
| G-HEAL-004 | `.claude/settings.json` too broad (Phase 1+ paths allowed) | RESOLVED | run002 — Phase 0 conservative mode applied |

| G-HEAL-005 | Phase 1 boundary ambiguity — master-plan.md allowed `acquisition-packs/fods/` in Phase 1 before Gate 1 human approval | RESOLVED | run005 — Phase 1A/1B split; acquisition pack explicitly forbidden in Phase 1 |
| G-HEAL-006 | Scoring model contained a FODS pre-scoring numeric estimate (a preliminary 5-factor model score in the accept band); needed neutralization before Phase 1 | RESOLVED | run005 — Complete rewrite to 7-factor 100-point format-neutral model; FODS pre-scoring removed |

| G-HEAL-007 | Section 10 forbidden paths table still listed `acquisition-packs/fods/` as allowed from `Gate 1 (Phase 1)` — contradicts Phase 1A/1B rules fixed in run005 | RESOLVED | run006 — Section 10 corrected: `acquisition-packs/fods/` now says "Phase 2 only — after human Gate 1 approval AND explicit Phase 2 execution prompt" |
| G-HEAL-008 | Section 23 pilot recommendation still contained a numeric pre-score estimate — residual numeric value present despite run005 claiming full removal | RESOLVED | run006 — Section 23 corrected: numeric pre-score removed; replaced with: "Formal Gate 1 scoring has not yet been performed. TC-0001 will compute the formal score in Phase 1A. No pre-score is authoritative." |

| G-HEAL-009 | Product implementation gate semantics ambiguous — `src/dotnet/commercial/` was blocked until "Gate 11 + DD3" across multiple files (AGENTS.md G4, GOVERNANCE.md 6.1, product-tracks.md Track 3, master-plan.md Section 1 Rule 12, Section 10, Decision Register DEC-005/DEC-010), but Gate 11 is release readiness, not creation authorization; also OSS source rows in Section 10 lacked explicit Phase 4 prompt requirement; Gate 9/10/11 semantics (implementation vs. readiness) were inconsistent across plans, workflow, and gates docs | RESOLVED | run007 — Corrected model applied across 6 files: OSS source requires Gate 9 + implementation taskcards + explicit Phase 4 prompt; commercial source requires Gate 10 + DD3 + commercial taskcards + explicit commercial prompt; Gate 10 = OSS release readiness; Gate 11 = commercial release readiness |

| G-HEAL-010 | Healing-history records for G-HEAL-006 and G-HEAL-008 contained quoted pre-score numeric values and a false grep verification claim. G-HEAL-006 description quoted the original numeric score inline. G-HEAL-008 description quoted the numeric pre-score inline. G-HEAL-008 verification condition stated "Confirmed by grep: no pattern in repo" — factually false because the healing records themselves contained those quoted values. | RESOLVED | run008 — Records rewritten to describe the issue neutrally without quoting the original numeric values. Verification condition corrected: no live content outside historical documentation records contains these patterns; historical records now describe the issue without quoting the score. |

| G-HEAL-011 | TC-0007 overreached by requiring FODS/ODF 1.3 specification acquisition as part of the generic spec-cache tooling implementation. TC-0007 was scoped as generic infrastructure but its acceptance criteria, steps, artifacts, and "in scope" section all required downloading the FODS/ODF 1.3 spec to `.local/spec-cache/fods/1.3/` as a proof of concept. This is Phase 1+ format-specific work that requires a separate explicit authorization prompt, not part of generic tooling. | RESOLVED | run009 — TC-0007 rewritten: scope now states generic tooling only; FODS download requirement removed from acceptance criteria, steps, and artifacts; dry-run/synthetic test substituted as proof of concept; explicit "deferred" section added; "Explicitly deferred" section states that real spec acquisition requires a separate prompt. |

| G-HEAL-012 | Spec-cache policy wording in `docs/specification-cache.md` and AGENTS.md Section S allowed automatic acquisition or re-acquisition without explicit authorization. Specifically: (1) spec-cache.md said "Any agent that finds the cache empty or stale re-acquires the spec from the canonical source URL" — unconditional automatic re-acquisition; (2) spec-cache.md Stage 2 rule said "If the cache is empty, acquire the spec first" — no authorization gate; (3) AGENTS.md S1 said "If not, acquire it using acquire_spec.py or download it manually" — no authorization required; (4) Refresh Policy Rules 2 and 3 said "the entry is re-acquired" automatically on staleness; (5) acquisition-workflow.md Stage 2 lacked a spec-cache authorization gate. | RESOLVED | run009 — spec-cache.md Authorization Model section added (6 required conditions for any download); automatic re-acquisition language replaced with stop-log-gap language; Refresh Policy rewritten to say staleness detection does not authorize re-download; AGENTS.md Section S rewritten with S3 (authorization required), S3-gap rule (stop-log-gap-create-taskcard), S9 (remote LLM restriction), S10 (no automatic re-download); acquisition-workflow.md Stage 1 and Stage 2 updated with spec-cache authorization language; docs/legal-and-licensing.md updated with four permissions section. |

| G-HEAL-013 | `.claude/settings.json` Phase 0 conservative mode lacked explicit deny rules for: (1) spec-cache implementation scripts (acquire_spec.py, refresh_check.py, spec_index.py) — Phase 1 only, not Phase 0; (2) network download commands (curl, wget, Invoke-WebRequest, iwr, python *acquire_spec*) — not authorized in Phase 0 or without explicit authorization. | RESOLVED | run009 — settings.json deny list extended: Write(tools/spec-cache/acquire_spec.py), Write(tools/spec-cache/refresh_check.py), Write(tools/spec-cache/spec_index.py), Bash(curl *), Bash(wget *), Bash(Invoke-WebRequest *), Bash(iwr *), Bash(python *acquire_spec*) added; phase_note and notes updated; limitation documented: powershell pattern approximated via separate entries; AGENTS.md Section S and docs/specification-cache.md carry the governing policy for network restrictions. |

| G-HEAL-014 | AGENTS.md had duplicate Section Q label and mislabeled internal rule IDs. Security Rules section was labeled "Q" but used P1-P4 for its internal rules (conflicting with the already-correct Section P which also used P1-P4). Acquisition Workflow Rules section was also labeled "Q" (duplicate top-level letter). This made AGENTS.md structurally ambiguous and untrustworthy for agents parsing section references. | RESOLVED | run010 — Security Rules section kept as Q with internal IDs corrected to Q1-Q4. Acquisition Workflow Rules moved to Section R (R1-R4). "What This Document Does Not Cover" moved to Section S. Specification Cache Rules moved to Section T (T1-T10, with T3/T3-gap/T9/T10 adjusted). Memory Usage and Maintenance added as Section U. |

| G-HEAL-015 | Product source layout in governance docs used obsolete paths `src/python/open-source/`, `src/dotnet/open-source/`, `src/dotnet/commercial/` instead of the intended format-first layout `src/python/{format}/`, `src/net/{format}/`. The old paths were present in plans/master-plan.md, docs/architecture.md, docs/product-tracks.md, AGENTS.md, GOVERNANCE.md, docs/release-control.md, docs/gates.md, docs/security.md, docs/acquisition-workflow.md, src/dotnet/_readme.md, src/python/_readme.md, and taskcards. Memory files correctly described the expected layout but the master plan had not been updated. | RESOLVED | run011 — All governance and architecture files updated with format-first layout. Old paths marked obsolete. DEC-031, DEC-032, DEC-033 added. G-020 logged for .NET FOSS packaging decision. |

| G-HEAL-016 | Agent review items (Gate 1 scoring, Phase 0 acceptance) were presented for human approval without independent verification sprint. No governance rule existed requiring pre-review verification. | RESOLVED | run016 — DEC-034 added (independent verification before human review). AGENTS.md Section V added (V1-V5). GOVERNANCE.md Section 15 added (15.1-15.5). Memory files updated. |

| G-HEAL-017 | Gate 1 approval was pending (all pre-conditions met in run016) but no commit had been made to record it. Registry still showed scored_pending_human_approval. | RESOLVED | run017 — Gate 1 approved by Babar Raza (2026-05-04). Registry gate_1.status: passed. TC-0001 closed. acquisition-packs/fods/ skeleton created. TC-0009 created. Commit c79f2d1 made. |

| G-HEAL-018 | Section 23 (Pilot Recommendation) still contained stale language "Formal Gate 1 scoring has not yet been performed. TC-0001 will compute the formal score in Phase 1A. No pre-score is authoritative." and "No FODS-specific work before Gate 1." — written in Phase 0 and never updated after Gate 1 passage. | RESOLVED | run018 — Section 23 updated with Gate 1 completion record. |

| G-HEAL-019 | Section 25 (Active Taskcards) still showed TC-0001 as "Pending — awaits Phase 0 acceptance" and all other TCs as "Pending". TC-0009 was missing from the table. The final line still said "Current status is Phase 0 pending". | RESOLVED | run018 — Section 25 updated: TC-0001 completed, TC-0009 added (not_started, active), all others not_started. |

| G-HEAL-020 | Section 27 Current Blockers still said "Next blocker: Gate 1 human approval for FODS" — Gate 1 was passed in run017. | RESOLVED | run018 — Section 27 Current Blockers updated to reflect Gate 1 passed; next action is Phase 2 execution prompt. |

| G-HEAL-021 | master-plan.md footer still said "version 2.7 — 2026-05-03" — written in run010 when the plan was v2.7 and never updated by subsequent runs despite the header advancing to v2.13. | RESOLVED | run018 — footer updated to v2.14 — 2026-05-04. |

| G-HEAL-022 | README.md Project Status section still said "Current phase: Phase 0 — Foundation" and "No format-specific content exists yet." — written in Phase 0 and never updated. | RESOLVED | run018 — README.md updated to Phase 2 status. |

| G-HEAL-023 | ROADMAP.md Phase 0 section still said "Status: In progress." and "Phase 0: Foundation (Current)" — written in Phase 0 and never updated. Phase 1 exit condition incorrectly required "endpoint client implemented" alongside Gate 1 passage; endpoint client is infrastructure work not required for Gate 1. | RESOLVED | run018 — ROADMAP.md Phase 0 status updated to Complete; Phase 1 exit condition corrected; Phase 2 marked Current. |

| G-HEAL-024 | .claude/settings.json still said phase: "0" and "PHASE 0 CONSERVATIVE MODE" and had acquisition-packs/fods/** in the deny list — all stale since Phase 2 began and run017 authorized acquisition pack work. | RESOLVED | run018 — settings.json updated to Phase 2 conservative mode. acquisition-packs/fods/** moved to allow list. Dangerous paths remain denied. |

| G-HEAL-025 | Section 33 Commit Policy still said "Include only Phase 0 foundation files" for the next commit — stale; multiple commits have been made since Phase 0. | RESOLVED | run018 — Section 33 updated to reflect current commit history. |

All twenty-five healing gaps confirmed resolved. Verification conditions:
- G-HEAL-001: run002 bundle contains all 11 bundle-metadata files. Confirmed by validation script.
- G-HEAL-002: run002 bundle has no `ocal/` entries. Confirmed by validation script.
- G-HEAL-003: `docs/release-control.md` has "Hybrid Classification Policy" section. `AGENTS.md` has Section F (F1–F7).
- G-HEAL-004: `.claude/settings.json` has `phase: "0"`, `phase_note`, and explicit deny list for Phase 1+ paths.
- G-HEAL-005: plans/master-plan.md Phase 1A now explicitly forbids `acquisition-packs/fods/`. Phase 1B also forbids it. Phase 2 is the authorized creation point.
- G-HEAL-006: `registry/scoring/_scoring-model.md` is now 7-factor 100-point format-neutral. No FODS pre-scoring present. TC-0001 pre-scoring reference removed.
- G-HEAL-007: plans/master-plan.md Section 10 now says "Phase 2 only — after human Gate 1 approval AND explicit Phase 2 execution prompt" for `acquisition-packs/fods/`. Confirmed by grep: no "Gate 1 (Phase 1)" pattern in repo (excluding .git/ and .local/).
- G-HEAL-008: plans/master-plan.md Section 23 no longer contains a numeric pre-score or "Estimated score" text. No live content outside historical documentation records contains these patterns. Historical records describe the issue neutrally without quoting the original numeric score (corrected in run008, G-HEAL-010).
- G-HEAL-009: Product implementation gate semantics corrected across 6 files. Section 10 OSS rows clarified. Section 10 commercial row corrected (Gate 11 → Gate 10 + DD3 + prompt). Section 1 Rules 11 and 12 updated. AGENTS.md G4/G5 updated. GOVERNANCE.md 6.1/6.5 updated. docs/gates.md Gate 9/10/11 clarified. docs/acquisition-workflow.md Stage 10/11 renamed and annotated. docs/product-tracks.md Track 3 corrected. DEC-005, DEC-010, DEC-026, DEC-027 added/updated.
- G-HEAL-010: Healing records G-HEAL-006 and G-HEAL-008 rewritten to describe pre-score issue neutrally. Verification condition corrected. No live content outside historical documentation contains numeric pre-score patterns. docs/architecture.md folder-tree commercial annotation corrected from "[Gate 11 + DD3 resolved only]" to correct authorization model (run007 missed this inline comment).
- G-HEAL-011: TC-0007 now states "generic tooling only" in objective and notes. Acceptance criteria no longer require FODS spec acquisition. Steps now use dry-run synthetic test. "Explicitly deferred" section added. Grep confirms no file says TC-0007 must download FODS/ODF.
- G-HEAL-012: docs/specification-cache.md Authorization Model section added. Automatic re-acquisition language removed. AGENTS.md Section S has S3 (authorization required), S3-gap rule, S9 (remote LLM), S10 (no auto re-download). acquisition-workflow.md Stage 2 has spec-cache authorization gate. docs/legal-and-licensing.md has four permissions section. Grep confirms no file says "acquire the spec first" or "re-acquires the spec" as unconditional rules.
- G-HEAL-013: settings.json deny list has Write(tools/spec-cache/acquire_spec.py), Write(tools/spec-cache/refresh_check.py), Write(tools/spec-cache/spec_index.py), Bash(curl *), Bash(wget *), Bash(Invoke-WebRequest *), Bash(iwr *), Bash(python *acquire_spec*). JSON remains valid. Limitation (powershell pattern approximated) documented in notes.
- G-HEAL-014: AGENTS.md Section Q duplicate resolved. Security Rules internal IDs are now Q1-Q4. Acquisition Workflow Rules is Section R (R1-R4). "What This Document Does Not Cover" is Section S. Specification Cache Rules is Section T (T1-T10). Memory Usage and Maintenance is Section U (U1-U9). Self-challenge extended to 14 questions. No duplicate top-level section letters remain. GOVERNANCE.md Section 1.2 updated with memory authority rule. TC-0008 created.

---

## Section 29 — Risk Register

| ID | Risk | Severity | Phase | Mitigation |
|---|---|---|---|---|
| R-001 | Agent drift — performs Phase N+1 work during Phase N | High | All | AGENTS.md rules, phase rules in master plan, self-challenge |
| R-002 | Overstated agent completion — agent says done, bundle says incomplete | High | All | Bundle inspection rule (Section 7). Evidence rules, summary is hypothesis. |
| R-003 | Stale master plan — plan diverges from repo state | High | All | Update requirement at every gate transition. `last_updated` header. |
| R-004 | Incomplete bundles — bundle missing files or containing wrong structure | High | All | Bundle validation script. Required bundle-metadata files list. |
| R-005 | Raw `.local/` leakage into bundle | High | All | Bundle creation script excludes `.local/`. Validation checks. |
| R-006 | Secrets in committed files | Critical | All | `.gitignore` includes `.env`. Pre-commit scan. secrets-scan audit file. |
| R-007 | LLM prompt/response leaks commercial or copyrighted content | High | Phase 1+ | Prompts/responses local-only. Never committed. |
| R-008 | Visibility inconsistency — same artifact type classified differently across sessions | Medium | Phase 1+ | Default classification rules table (Section 17). `/check-gate` validation. |
| R-009 | Stale artifact reused without detection | High | Phase 1+ | Source hash in artifact front matter. Staleness flag. Reuse-before-regenerate checks staleness. |
| R-010 | Premature product code — source written before Gate 9 | High | Phase 3 | Forbidden paths list. Phase rules. `.claude/settings.json` deny list. |
| R-011 | Commercial artifact leaks into OSS release | Critical | Phase 4+ | CI boundary check. Release manifest review. Commercial folder deferred. |
| R-012 | Overbuilding Phase 0 — Phase 0 expands into Phase 1+ | Medium | Phase 0 | Phase 0 forbidden list. Self-challenge question 1. |
| R-013 | Endpoint rabbit hole — LLM endpoint section grows into full API client | Medium | Phase 1 | TC-0005 is one taskcard. Strategy doc does not grow beyond purpose. |
| R-014 | Too many storage mechanisms — YAML + JSONL + SQLite all introduced early | Medium | Phase 0 | SQLite deferred (DEC-020). JSONL for run logs. YAML for committed structured data. |
| R-015 | Oracle treated as truth — reference tool output accepted without spec cross-check | High | Phase 3 | Oracle model (Section 22). Spec is authority rule. |
| R-016 | Legal rubber stamp — Gate 2 approved without real legal review | High | Phase 2 | Gate 2 criteria require documented legal category confirmation. |
| R-017 | Sample provenance gaps — samples acquired without confirmed license | High | Phase 2 | `samples/_provenance.yaml` required. Gate 3 checks provenance. |
| R-018 | Commands directory becomes a mess | Low | Phase 1+ | Command registry YAML (TC-0004 scope). Unused commands removed. |
| R-019 | Agent over-trusts stale `/memory` files — treats outdated memory as current project state | High | All | AGENTS.md Section U1 states memory is context only. U5 requires gap logging for contradictions. Self-challenge questions 12-13. |
| R-020 | `/memory` diverges from master plan due to missing maintenance — agents read stale rationale | Medium | All | AGENTS.md Section U6 requires memory updates or taskcards after trigger events. TC-0008 planned for automation. |
| R-021 | Secrets, raw LLM prompts, or copyrighted spec text accidentally stored in `/memory` | High | All | AGENTS.md Section U7 explicitly prohibits this. GOVERNANCE.md Section 1.2a mirrors the rule for humans. Memory files are not committed secrets-free by policy. |

---

## Section 30 — Evidence Bundle Rules

### Required Bundle Contents

Every execution-mode bundle must contain:
```
repo/
  <all files created or modified during the executed phase>
bundle-metadata/
  master-plan-snapshot.md        (copy of plans/master-plan.md at bundle time)
  phase0-file-list.txt           (list of all Phase 0 files with EXIST/MISSING status)
  forbidden-path-check.txt       (all forbidden Phase 1+ paths — ABSENT/PRESENT status)
  agents-md-check.txt            (AGENTS.md rule coverage check)
  governance-md-check.txt        (GOVERNANCE.md rule coverage check)
  yaml-validation-notes.txt      (YAML/JSON syntax validation results)
  secrets-scan-notes.txt         (secrets scan — API key patterns, .env presence)
  phase0-completion-report.md    (gap summary, fix summary, validation table)
  self-challenge.md              (all self-challenge questions answered)
  gap-log-update.md              (gap register changes this run)
  artifact-index-snapshot.yaml   (copy of .local/artifact-index.yaml at bundle time)
  git-status.txt                 (git status output confirming no commit)
```

Phase-specific bundles may include additional audit files as needed (e.g., `master-plan-section-check.txt` for run003).

### Prohibited Bundle Contents

Bundles must NEVER contain:
- `.git/` directory or any git objects
- `.env` file (secrets)
- Raw `.local/` directory contents
- `ocal/` (malformed path artifact)
- LLM prompts or responses (local-only, privacy-sensitive)
- Any artifact with `visibility: blocked`
- Any file not produced by or directly related to the executed phase

### Final Path Rule
The absolute Windows path to the ZIP is printed as the **final line** of the agent's response:
```
EVIDENCE_BUNDLE: C:\<absolute path>\<bundle-name>.zip
```
No other text after this line.

---

## Section 31 — Phase 0 Review Checklist

To be completed by human reviewer inspecting the evidence bundle:

- [ ] All 45 required files exist (see Section 9 — 41 original + 3 added in run008 + 1 added in run010: TC-0008)
- [ ] `registry/format-registry.yaml` contains no format entries (empty skeleton only)
- [ ] All forbidden Phase 1+ paths absent (see Section 10)
- [ ] `.gitignore` includes `.local/` and `.env` patterns
- [ ] No `.env` file present in repo
- [ ] No secrets or API keys in any committed file
- [ ] All YAML/JSON files parse without errors
- [ ] `AGENTS.md` contains all required sections (21 sections A-U, including Section F hybrid policy, Section T spec-cache rules, Section U memory rules)
- [ ] `GOVERNANCE.md` contains all required rules
- [ ] `plans/master-plan.md` is complete and canonical (this document)
- [ ] Bundle structure: `repo/` + `bundle-metadata/` only, no forbidden paths
- [ ] No git commit has been made
- [ ] `docs/release-control.md` contains Hybrid Classification Policy section
- [ ] `.claude/settings.json` is Phase 0 conservative mode (phase: "0", deny list present)
- [ ] `docs/specification-cache.md` exists and defines spec-cache policy with authorization model
- [ ] `tools/spec-cache/_readme.md` exists with authorization rules
- [ ] `taskcards/TC-0007-specification-cache.md` exists and requires generic tooling only (no FODS download)
- [ ] `.local/spec-cache/` is NOT present in repo (local-only; covered by `.local/` gitignore pattern)
- [ ] No file in repo says TC-0007 must download FODS/ODF spec
- [ ] No file in repo says missing spec cache automatically authorizes download
- [ ] `.claude/settings.json` deny list includes spec-cache scripts and network download commands
- [ ] `AGENTS.md` has no duplicate top-level section letters (A through U, each unique)
- [ ] `AGENTS.md` Section Q Security Rules uses Q1-Q4 (not P1-P4)
- [ ] `AGENTS.md` Section U (Memory Usage and Maintenance) exists
- [ ] `AGENTS.md` self-challenge has 14 questions (questions 11-14 cover memory)
- [ ] `GOVERNANCE.md` Section 1.2 states `/memory` is context, not authority
- [ ] `taskcards/TC-0008-memory-sync-command.md` exists with status "Not started"
- [ ] `/memory` folder exists at repo root with at least README.md and 00-index.md
- [ ] No secrets, raw LLM prompts, or copyrighted spec text in `/memory`
- [ ] `plans/master-plan.md` Section 10 uses `src/python/{format}/` and `src/net/{format}/` — not old `src/dotnet/` paths
- [ ] `docs/architecture.md` folder tree uses format-first `src/python/{format}/` and `src/net/{format}/` layout
- [ ] `docs/product-tracks.md` replaces old Track 1/2/3 with format-first layout
- [ ] `AGENTS.md` G4, G5, N rules reference new format-first paths
- [ ] `GOVERNANCE.md` Sections 6.1 and 6.5 reference new format-first paths
- [ ] No committed file claims `src/python/open-source/`, `src/dotnet/open-source/`, or `src/dotnet/commercial/` is the target architecture (any remaining mentions must be labeled OBSOLETE or historical)
- [ ] DEC-031, DEC-032, DEC-033 present in Decision Register

If all items pass: Human may declare Phase 0 accepted and issue Phase 1 prompt.
If any item fails: Log the failure as a new healing gap and issue a targeted healing prompt.

---

## Section 32 — Current Next Action

1. **Completed (run015):** Phase 0 accepted (all 36 checks passed). Phase 0 baseline commit made. Phase 1A: FODS scored 93/100 (Accept band). Registry entry created (gate_1: scored_pending_human_approval). TC-0001 updated. Evidence bundle created.
2. **Completed (run016):** Independent verification sprint. All run015 claims verified. DEC-034 added. AGENTS.md Section V + question 15. GOVERNANCE.md Section 15. Evidence bundle produced.
3. **Completed (run017):** Gate 1 approved by Babar Raza (2026-05-04). Registry gate_1.status set to passed. TC-0001 closed. acquisition-packs/fods/ skeleton created (5 files). TC-0009 created (Phase 2 taskcard, not_started). run016+run017 changes committed. Evidence bundle produced. master-plan.md v2.13.
4. **Completed (run018):** State reconciliation. Stale Sections 23, 25, 27, 28, 33, footer healed. README.md and ROADMAP.md Phase 0/2 status updated. `.claude/settings.json` advanced to Phase 2 conservative mode. G-HEAL-018 through G-HEAL-025 resolved. No Gate 2 evidence work performed. No commit made. master-plan.md v2.14.
5. **Completed (run019):** Combined sprint. run018 state independently verified (27 checks PASS). run018 committed (0c97256 "chore: reconcile Phase 2 project state"). settings.json TC-0007 scripts moved from deny to allow. TC-0007 implemented (spec_index.py, acquire_spec.py, refresh_check.py; smoke tests pass; status: completed_pending_independent_verification). TC-0009 Gate 2 evidence draft completed (spec-evidence.md, legal-notes.md; 4/7 fast-path checklist items confirmed; gate_2 status: evidence_draft_pending_independent_verification). Committed run019 (589c1af). master-plan.md v2.15.
6. **Completed (run020):** Independent verification + schema reconciliation + spec acquisition sprint. 5 issues found and fixed in TC-0007 tooling: (a) spec_index.py REQUIRED_FIELDS restructured; (b) acquire_spec.py spurious warning removed; (c) refresh_check.py Windows encoding bug fixed; (d) docs/specification-cache.md schema/lifecycle updated; (e) settings.json phase_note corrected. Spec download attempted but --allow-network denied; pre-download spec-index.yaml metadata entry created. Evidence updated (5/8 fast-path). G-021 logged. Committed tooling fixes (1e69121). Evidence leftovers committed (e8ab83f) in continuation session. master-plan.md v2.16.
7. **Completed (run021):** Combined sprint: repo hygiene + settings.json fix + spec acquisition + Gate 2 evidence upgrade. (a) __pycache__ removed from working tree; (b) settings.json deny rule for python *acquire_spec* removed — T3 authorization confirmed in run021 prompt; (c) ODF 1.3 Part 3 PDF downloaded from OASIS official source (24,270,588 bytes, sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066); spec-index.yaml validates VALID/CURRENT; (d) spec-evidence.md primary claims upgraded to SUPPORTED_BY_CACHED_SOURCE; (e) legal-notes.md fast-path checklist updated 6/8; (f) TC-0007 status updated to completed_independently_verified_run020; (g) all governance artifacts updated. Gap G-021 resolved. Committed 138effd. master-plan.md v2.17.
8. **Completed (run022):** Independent verification sprint for run021 evidence (per DEC-034). (a) SHA-256 of cached FODS spec independently re-verified: MATCH (sha256:92cfe64...b066); (b) spec_index.py VALID/CURRENT confirmed; refresh_check.py 0 stale entries; (c) spec-cache tooling dry-run mode verified (no network by default); (d) Gate 2 evidence claims reviewed: primary source SUPPORTED_BY_CACHED_SOURCE confirmed; structural claims correctly labeled PLAUSIBLE_PENDING_VERIFICATION; (e) stale state fixed (G-HEAL-028 through G-HEAL-036); (f) Gate 2 status upgraded to evidence_cached_pending_human_review; (g) TC-0010 future planning taskcard created (not_started); (h) master-plan.md v2.18. Committed 32cdb1c.
9. **Completed (run023):** Human Gate 2 approval recorded. (a) run022 state verified (32cdb1c, clean tree, no forbidden paths, Gate 2 approved_by null confirmed); (b) stale status leftovers fixed (pack.yaml header/notes, TC-0009 artifact table, master-plan latest-commit); (c) registry gate_2.status → passed; approved_by: Babar Raza; approved_date: 2026-05-05; patent search waived by project lead; (d) acquisition pack Gate 2 status → passed; (e) spec-evidence.md + legal-notes.md sign-off sections updated; (f) TC-0009 closed; (g) TC-0010 activated (planning_ready); (h) TC-0011 created (not_started — future Gate 3 planning verification); (i) README.md + ROADMAP.md updated; (j) master-plan.md v2.19. No samples acquired. No push.
10. **Completed (run024):** Independent verification of run023 + stale state fixes + Specification Normalization Layer. (a) run023 state independently verified (c9d8d8e; 5 stale issues found and fixed: pack.yaml notes/next_action, settings.json phase/description/allow-list, sample-sources.md Gate 2 status); (b) Specification Normalization Layer created: docs/specification-normalization.md (15 sections), tools/spec-normalize/ (4 files: _readme.md, normalize_pdf.py, build_citation_map.py, validate_normalized_spec.py); (c) governance integration: AGENTS.md Section W (10 rules), GOVERNANCE.md Section 16 (6 rules), docs/gates.md Gate 3/4 normalization notes, docs/specification-cache.md Normalization Layer section; (d) TC-0012 created (in_progress); (e) TC-0010 updated (normalization dependency + planning steps expanded); (f) Local normalization dry-run: SHA-256 MATCH confirmed (92cfe64...b066), source-manifest.yaml written, normalization-plan.md + extraction-report.md produced, G-NORM-001 logged (pdfminer.six not installed); (g) Gate 3 planning: sample-sources.md updated with corpus plan (4 sample types, blocked rules, synthetic strategy, 3 candidate sources, provenance procedure); (h) master-plan.md v2.20.
11. **Completed (run025):** Independent verification of run024 + full FODS spec normalization + TC-0013. (a) run024 state verified (01f7bbe; valid uncommitted master-plan.md hash update confirmed); (b) pdfminer.six 20260107 installed (--user); (c) normalize_pdf.py run on FODS spec: full extraction SUCCESS — text.txt 2,160,370 chars, pages.jsonl 782 pages; (d) build_citation_map.py run: citations.yaml 194 section refs + 35 external refs; (e) validate_normalized_spec.py: 7 PASS, 1 WARN, 0 FAIL; (f) G-NORM-001 RESOLVED; (g) requirements.txt added to tools/spec-normalize/; (h) TC-0012 updated (Phase 2 complete, G-NORM-001 resolved); (i) sample-sources.md updated with verified spec section refs; (j) TC-0013 created (FODS Gate 3 Sample Corpus Execution, not_started); (k) master-plan.md v2.21.
12. **Completed (run026):** Spec Navigation Layer + Gate 3 corpus execution + TC-0014. (a) run025 state independently verified (f17bb12; valid uncommitted master-plan.md hash update confirmed); (b) 4 navigation tools created: build_section_index.py (884 sections, 705 pages mapped), build_chunk_index.py (940 chunks, 423,290 words), query_normalized_spec.py (multi-mode query), export_sample_requirements.py; (c) sample-requirements.yaml (4 samples), parser-requirements-draft.yaml (10 requirements) produced; (d) 4 synthetic FODS samples created: minimal-spreadsheet.fods, multi-sheet-basic.fods, typed-values-basic.fods, formula-basic.fods — all Apache-2.0 project-owned; (e) tools/samples/create_fods_samples.py + validate_fods_samples.py created; (f) Validation: 4/4 PASS; (g) samples/_provenance.yaml: 4 confirmed entries; (h) registry gate_3 → sample_corpus_created_pending_independent_verification; (i) TC-0013 updated (in_progress); (j) TC-0014 created (Gate 4 planning, not_started); (k) docs/specification-normalization.md updated with Navigation Layer section; (l) master-plan.md v2.22. Commit pending.
13. **Completed (run030):** TC-0018 DEC-034 verification + stale fixes + Spec Workbench v1. (a) validate_against_samples.py re-run: 4/4 PASS confirmed independently; (b) fods_parser.py imports verified: stdlib only, no network; (c) forbidden paths verified absent; (d) settings.json contradiction fixed (prototypes/fods deny→allow); (e) Spec Workbench v1 built (local-only): verified-facts.yaml (10 facts), parser/sample/model requirement packs (205/205 validation PASS), task packets (gate3: 59 lines, gate4: 120 lines, gate5-draft: 44 lines), coverage matrices; (f) 5 new tools created (build_spec_workbench.py, build_requirement_pack.py, validate_requirement_pack.py, export_task_packet.py) + docs/spec-consumption-workbench.md; (g) TC-0020 (Spec Workbench core) and TC-0021 (FODS quality review) created; (h) parser planning files updated with workbench refs and PASS statuses; (i) registry gate_4 → prototype_verified_pending_human_review; master-plan.md v2.26.
14. **Completed (run034):** run033 independent verification + evidence hardening + TC-0024 DEC-034 + Gate 5 review packet + Gate 6 planning + TC-0026/TC-0027. (a) run033 verified (35/35 checks PASS, working tree clean); (b) evidence bundle system hardened: builder+validator updated with git cleanliness check, contract-in-bundle, manifest generation, min metadata enforcement; negative test PASS (thin bundles correctly rejected); (c) TC-0024 DEC-034 executed: validate_neutral_model.py independently re-run (4/4 PASS, 87 checks, 0 errors); model.yaml 6 entities verified; model.schema.json valid; field-map.yaml 19 mappings verified; coverage-matrix.yaml 30 features verified; validation-rules.yaml 21 rules verified; no forbidden paths; no self-approval; (d) Gate 5 human-review packet created (gate5-human-review-packet.md); (e) Registry gate_5 → neutral_model_verified_pending_human_review; (f) Gate 6 planning: gate6-oracle-plan.md, oracle-scope.md, oracle-risk-register.md (planning only); (g) TC-0026 (Gate 6 execution, not_started), TC-0027 (Gate 6 verification, not_started) created; (h) master-plan.md v2.30.
15. **Completed (run035):** run034 independent verification (PASS) + Gate 5 PASSED + TC-0024/TC-0023/TC-0025 CLOSED + Gate 6 oracle harness created + oracle_blocked_missing_tool. (a) run034 verified (34/34 checks PASS); (b) Gate 5 approved by Babar Raza (2026-05-06); registry gate_5 → passed; (c) TC-0024 CLOSED; TC-0023 COMPLETED; TC-0025 COMPLETED; (d) stale fixes: master-plan header, memory/09, TC-0024 checkboxes; (e) oracle harness created: tools/oracle/ (5 files: preflight_oracle.py, run_fods_oracle.py, compare_fods_oracle.py, summarize_oracle_results.py, README.md); (f) oracle preflight run: FAIL (soffice/libreoffice not found); (g) gate6-oracle-blocker-report.md created; registry gate_6 → oracle_blocked_missing_tool; TC-0026 → blocked_missing_oracle_tool; (h) evidence bundle validator+builder fixes (run_required_repo_files normalization); master-plan.md v2.31.
16. **Completed (run036):** run035 independent verification PASS + oracle harness hardening + stale path fixes + blocker report hardened + installation checklist. (a) run035 verified: all 5 commits present (179e6db + 625fca1 + 2fb4e35 + 1e14079 + 1be6c0a), validate_neutral_model.py 4/4 PASS re-confirmed, forbidden paths absent, no Gate 5/6 self-approval, Gate 5 PASSED status confirmed; (b) evidence validator hardened: git-status-final.txt OR git-status.txt accepted (either is sufficient), missing git status now FAIL not WARN; (c) oracle_common.py created (shared constants, find_soffice(), check_samples(), print_discovery_summary()); (d) preflight/run/compare/summarize all rewritten to import from oracle_common; (e) FORMAT_FACTORY_SOFFICE env var added to all discovery; (f) --soffice-path CLI arg added to preflight + run tools; (g) oracle preflight re-run with oracle_common harness: FAIL (same result, 10 candidates tried, FORMAT_FACTORY_SOFFICE not set); (h) stale path refs fixed in TC-0026/TC-0027/gate6-oracle-plan.md/oracle-scope.md (`.local/oracle-outputs/fods/` → `.local/oracle/fods/`; `reports/fods-oracle.md` → `acquisition-packs/fods/gate6-oracle-comparison-report.md`); (i) oracle-installation-checklist.md created; (j) gate6-oracle-blocker-report.md hardened with run036 diagnostics; (k) tools/oracle/README.md updated with canonical path model and discovery priority; master-plan.md v2.32.
17. **Completed (run037):** run036 independent verification PASS + stale state fixed + oracle provider abstraction + --check-no-pending validator + negative tests + oracle preflight re-run 3. (a) run036 verified: all 3 commits present (8acd48d + 82281e6 + 3216dcf), forbidden paths absent, no self-approval, oracle_common.py and installation checklist confirmed; (b) stale state fixed: master-plan header 82281e6→3216dcf, memory/09 latest-commit updated; (c) validator --check-no-pending flag added (scans metadata files for PENDING markers); 4 negative tests PASS (thin bundle FAIL ✓, PENDING marker FAIL ✓, PASS without flag ✓, clean bundle PASS ✓); (d) oracle provider abstraction: tools/oracle/provider_registry.yaml (LibreOffice entry + FODS assignment), tools/oracle/validate_oracle_environment.py (reads registry, discovers providers), docs/oracle-provider-strategy.md (architecture + governance rules); (e) acquisition-packs/fods/oracle-provider-options.md created (LibreOffice APPROVED, 4 alternatives evaluated); (f) oracle preflight re-run (3rd): FAIL — 8 candidates tried, LibreOffice not installed; (g) blocker report updated with run037 findings and improvements table; (h) master-plan.md v2.33. Commits: de29c97 + f964eba + a35b089. No Gate 6 approval. No product source. No embeddings.
18. **Completed (run038):** run037 independent verification PASS + stale commit fixed (f964eba→a35b089) + TC-0026 blocker wording fixed + oracle preflight re-run (4th): FAIL + oracle harness self-test added (self_test_oracle_harness.py — HARNESS_SELF_TEST_ONLY) + operator handoff doc (oracle-operator-handoff.md) + next-format candidate shortlist (TC-0028, registry/candidates/odf-flat-family-shortlist.yaml — candidate-only, no Gate 1 approval) + registry/memory/docs updated; master-plan.md v2.34. No Gate 6 approval. No product source. No embeddings.
19. **Completed (run039):** run038 independent verification PASS (all 4 commits confirmed: 1e1d504+e0fc07c+998412c+bc2bdf8; BUNDLE_VALIDATION: PASS) + stale commit fixed (998412c→bc2bdf8) + consistency enforcement tool added (tools/evidence/check_current_state_consistency.py — 4 negative tests PASS) + oracle preflight re-run (5th): FAIL + harness self-test confirmed PASS 4/4 + candidate shortlist independently verified (10/10 checks PASS) + FODT Gate 1 scoring package created (registry/candidates/fodt-gate1-scoring-package.yaml — 88/100, candidate-only, no Gate 1 approval) + TC-0029 created + ODF reuse strategy doc created (docs/odf-flat-family-reuse-strategy.md) + TC-0028 → in_progress + registry/memory/ROADMAP/README/settings.json updated; master-plan.md v2.35. No Gate 6 approval. No product source. No embeddings.
20. **Completed (run040):** run039 independently verified PASS (44 checks PASS; all 5 run039 commits confirmed: 48f6a0d+8cd2ed2+075edca+d052510+54a27dc; BUNDLE_VALIDATION: PASS) + stale commit fixed (d052510→54a27dc, memory/09 updated) + CURRENT_STATE_CONSISTENCY: PASS + clean-git loophole closed: require_clean_git: false now fails on dirty git unless emergency_blocker_bundle: true; base-run.yaml updated (require_clean_git: true, emergency_blocker_bundle: false); 2 new negative tests (6/6 total PASS) + consistency checker strengthened (10 checks: master-plan header commit, Section 33 commit, memory/09 commit, registry gate_6 approved_by null, registry gate_6 approved_date null, no official fodt registry entry, fodt-gate1-scoring-package gate_1_approved false, no acquisition-packs/fodt/, pack.yaml gate_6 not approved) + oracle preflight re-run (6th): FAIL (6 consecutive FAIL confirmed) + TC-0029 DEC-034 PASS: 7/7 scoring factors independently verified, 88/100 confirmed, Accept band confirmed + FODT Gate 1 human-review packet created (acquisition-packs/_candidate-shortlists/fodt-gate1-human-review-packet.md) + TC-0029 → verification_passed_pending_human_review + README/ROADMAP/registry/oracle-provider-strategy.md/gate6-oracle-blocker-report.md/settings.json updated; master-plan.md v2.36. No Gate 6 approval. No FODT Gate 1 approval. No product source. No embeddings.
21. **Completed (run041):** run040 independently verified PASS (45 checks PASS; all run040 commits confirmed; BUNDLE_VALIDATION: PASS) + self-referential commit-hash model REPLACED: docs/current-state-and-evidence-authority.md (NEW) + check_current_state_consistency.py redesigned (PENDING-marker checks, FODT consistency, gate_6 null checks — no hash matching) + validate_evidence_bundle.py extended (repo current-state PENDING scan) + build_evidence_bundle.py: auto-generates git-log.txt+git-status-final.txt + base-run.yaml v1.1 (current_state_authority: bundle-metadata; git metadata required) + 7/7 consistency tests PASS + Section 33 renamed "Run Commit Ledger and Evidence Authority" + master-plan/memory-09 PENDING markers removed + FODT Gate 1 APPROVED: Babar Raza, 2026-05-07, 88/100, Accept band + registry FODT entry created (gate_1: passed) + acquisition-packs/fodt/ skeleton (6 files: pack.yaml, spec-evidence.md, legal-notes.md, sample-sources.md, parser-notes.md, gate2-planning.md) + TC-0030 created (FODT Gate 2 planning) + TC-0029 COMPLETED + TC-0028 COMPLETED + oracle preflight re-run (7th): FAIL (7 consecutive: run035–run041); master-plan.md v2.37. No Gate 6 approval. No FODT Gate 2+. No FODT samples/parser/schema. No product source. No embeddings.
22. **Completed (run042):** run041 independently verified PASS (47 checks PASS; BUNDLE_VALIDATION: PASS; 5-metadata regression confirmed) + evidence-contract repair: base-run.yaml v1.2 (min_metadata_count→30; normal_pass_min_metadata:30) + validate_evidence_bundle.py hardened: matches_forbidden exact-match fix (.env.example no longer blocked by .env pattern); NORMAL_PASS_METADATA_DEPTH check added; 8/8 negative tests PASS + fodt-gate1-scoring-package.yaml CANDIDATE-ONLY header replaced with GATE 1 APPROVED record + master-plan skeleton "(5 files)"→"(6 files)" fixed + master-plan last_completed_run: run040→run041 fixed + TC-0030 FODT Gate 2 executed: spec-evidence.md→SUPPORTED_BY_CACHED_SOURCE; legal-notes.md→FAST_PATH_DECLARED (8/8 fast-path items, patent waived); pack.yaml gate_2→evidence_cached_pending_independent_verification; registry gate_2 updated; gate2-human-review-packet.md created + TC-0031 created (DEC-034 pending) + oracle preflight re-run (8th): FAIL (8 consecutive: run035–run042); master-plan.md v2.38. No Gate 6 approval. No FODT Gate 2 approval. No FODT samples/parser/schema. No product source. No embeddings.
23. **Completed (run043):** FODT Gate 2 DEC-034 PASS (TC-0031; SHA-256 re-verified MATCH; 8/8 fast-path items confirmed) + FODT Gate 2 APPROVED (Babar Raza, 2026-05-08) + FODT Gate 3 executed (4 FODT samples, TC-0032 DEC-034 PASS 27/27, Gate 3 approved) + FODS Gate 6 oracle executed (LibreOffice installed run043; ORACLE_RUN PASS 4/4; TC-0026 COMPLETED) + Gate 6 status → oracle_comparison_complete; master-plan v2.39.
24. **Completed (run044):** FODS Gate 6 DEC-034 (TC-0027 PASS 24/24; ORACLE_COMPARE PASS 3/4 WARN 1/4) + Gate 6 APPROVED (Babar Raza, 2026-05-08) + FODT Gate 4 prototype created (fodt_parser.py, TC-0035 DEC-034 PASS 20/20) + Gate 4 APPROVED (Babar Raza, 2026-05-08); master-plan v2.40.
25. **Completed (run045):** FODS Gate 7 fuzz executed (18 malformed fixtures, GATE7_FUZZ_TEST PASS 18/18 CRASH 0/18) + TC-0033 DEC-034 PASS + Gate 7 APPROVED (Babar Raza, 2026-05-08) + FODS Gate 8 planning (gate8-security-plan.md, TC-0036) + FODT Gate 5 planning (TC-0037); master-plan v2.41.
26. **Completed (run046):** FODS Gate 8 security review executed (reports/security/fods.md; 8 threat categories; GATE8_SECURITY_REVIEW: PASS) + TC-0038 DEC-034 PASS 20/20 + Gate 8 APPROVED (Babar Raza, 2026-05-08) + FODT Gate 5 neutral model created (schemas/neutral-model/fodt/ — 7 entities, 26 mappings, 19 rules; FODT_NEUTRAL_MODEL_VALIDATION PASS 4/4 109 checks) + TC-0039 DEC-034 PASS + Gate 5 APPROVED (Babar Raza, 2026-05-08) + FODS Gate 9 planning (TC-0040, gate9-product-mapping-plan.md, tier-map-draft.yaml) + FODT Gate 6 oracle planning (TC-0041/TC-0042/TC-0043; gate6-oracle-plan.md, oracle-scope.md, oracle-risk-register.md); master-plan v2.42. No Gate 9 approval. No FODT Gate 6 execution. No product source. No embeddings.

27. **Completed (run047):** Evidence metadata floor RESTORED 4→30 (run046 regression repaired) + RUN_CONTRACT_MINIMUM_NOT_BELOW_BASE check added to validator + 11 negative tests (was 10) + base-run.yaml v1.3 + FODS Gate 9 APPROVED (Babar Raza, 2026-05-08): tier-map.yaml v1.0 (first_oss_release_tiers [0,1,2]) + gate9-human-review-packet.md + TC-0040 COMPLETED + DEC-034 inline 20/20 + FODT Gate 6 APPROVED (Babar Raza, 2026-05-08): run_fodt_oracle.py + compare_fodt_oracle.py + FODT_ORACLE_RUN PASS 4/4 + FODT_ORACLE_COMPARE PASS + TC-0042/TC-0043 COMPLETED + DEC-034 inline 10/10 + gate6-oracle-comparison-report.md + gate6-human-review-packet.md + FODS Gate 10 planning (TC-0044, gate10-product-planning.md) + FODT Gate 7 planning (TC-0045, gate7-fuzz-plan.md); master-plan v2.43. No product source. No Gate 10 approval. No FODT Gate 7 approval.
28. **Next required action (run047):** (1) FODS Gate 10: issue explicit TC-0044 execution prompt for product planning. (2) FODT Gate 7: issue explicit TC-0045 fuzz testing execution prompt. Both require separate explicit execution prompts; no self-approval. Commit: 629cc32.

**Gate 2 for FODS: PASSED — approved by Babar Raza (2026-05-05). Patent search waived by project lead.**
**Gate 3 for FODS: PASSED — approved by Babar Raza (2026-05-05, run028). 4 Apache-2.0 synthetic samples, 4/4 PASS, SHA-256 verified run027. Spec Navigation Layer: 884 sections, 940 chunks. TC-0013 COMPLETED.**
**Gate 4 for FODS: PASSED — approved by Babar Raza (2026-05-06, run033 prompt). Prototype at prototypes/by-format/fods/fods_parser.py. TC-0018 DEC-034 PASS.**
**Gate 5 for FODS: PASSED — approved by Babar Raza (2026-05-06, run035 prompt). Neutral model at schemas/neutral-model/fods/ — 6 entities, 19 field mappings, 4/4 samples PASS (87 checks, 0 errors). TC-0024 DEC-034 PASS run034. TC-0024 CLOSED.**
**Gate 6 for FODS: oracle_blocked_missing_tool — LibreOffice not installed (8 consecutive preflight FAIL: run035/036/037/038/039/040/041/042). Oracle harness hardened run036 (oracle_common.py, FORMAT_FACTORY_SOFFICE, canonical paths, installation checklist). Provider abstraction added run037. Harness self-test PASS run038 (HARNESS_SELF_TEST_ONLY 4/4). Operator handoff run038. Consistency enforcement tool added run039, redesigned run041 (stable run-state model). TC-0026 blocked. Gate 6 NOT approved.**
**Gate 1 for FODT: PASSED — approved by Babar Raza (2026-05-07, run041). Score 88/100, Accept band. Registry entry created. acquisition-packs/fodt/ skeleton (6 files) created. TC-0028 COMPLETED. TC-0029 COMPLETED.**
**Gate 2 for FODT: evidence_cached_pending_independent_verification — TC-0030 executed run042 (2026-05-08). 8/8 fast-path items confirmed. SHA-256 MATCH (3rd verification). Patent search waived (same as FODS Gate 2 waiver, Babar Raza, 2026-05-05). TC-0031 DEC-034 independent verification not_started. Gate 2 NOT approved.**

### Run History

| Run | Date | Action | Result |
|---|---|---|---|
| run001 | 2026-05-03 | Phase 0 foundation execution | All 41 files created |
| run002 | 2026-05-03 | Healing pass | 4 compliance gaps resolved (settings, release-control, AGENTS.md, bundle structure) |
| run003 | 2026-05-03 | Master-plan canonicalization | plans/master-plan.md rewritten v1.1→v2.0 (34 sections) |
| run004 | 2026-05-03 | Governance sync | 40 files reviewed; 4 contradictions resolved; 5 files updated |
| run005 | 2026-05-03 | Final consistency healing | Phase 1 boundary fixed; scoring model hardened; 2 healing gaps resolved |
| run006 | 2026-05-03 | Final cleanup (missed contradictions) | Section 10 acquisition-pack boundary corrected; Section 23 numeric pre-score removed; grep verification; 2 healing gaps resolved (G-HEAL-007, G-HEAL-008) |
| run007 | 2026-05-03 | Product implementation gate semantics reconciliation | OSS source authorization (Gate 9 + explicit Phase 4 prompt); commercial source authorization corrected (Gate 10 + DD3 + prompt, not Gate 11); Gate 10/11 as release readiness; 6 files updated; G-HEAL-009 resolved |
| run008 | 2026-05-03 | Specification-cache amendment + residual pre-score cleanup | 3 new files (docs/specification-cache.md, tools/spec-cache/_readme.md, TC-0007); G-HEAL-010 resolved (pre-score language in G-HEAL-006/008 records corrected); architecture.md commercial annotation fixed; AGENTS.md Section S added; phase count updated to 44 |
| run009 | 2026-05-03 | Spec-cache governance cleanup and bundle repair | TC-0007 FODS download overreach corrected; spec-cache authorization model added; AGENTS.md Section S extended (S3/S3-gap/S9/S10); settings.json deny rules added; 8 files updated; G-HEAL-011/012/013 resolved |
| run010 | 2026-05-03 | Memory integration and AGENTS.md governance cleanup | AGENTS.md Section Q duplicate fixed; Sections R/S/T renamed; Section U (Memory Usage) added; self-challenge extended to 14 questions; GOVERNANCE.md memory authority rule added; TC-0008 created; master-plan.md v2.7; G-HEAL-014 resolved; 3 files updated; 1 file created |
| run011 | 2026-05-04 | Product source layout reconciliation and agentic workflow foundation | Format-first layout (`src/python/{format}/`, `src/net/{format}/`) propagated to all governance and architecture docs; old paths marked obsolete; DEC-031/DEC-032/DEC-033 added; G-HEAL-015 resolved; G-020 logged; 13+ files updated; master-plan.md v2.8 |
| run012 | 2026-05-04 | Memory stream sync — run009/run010 state and source-layout expectation | 9 /memory files updated; stale pending-propagation notes added; run stream model documented; spec-cache authorization from run009 captured; AGENTS.md Section U from run010 captured; no governance files modified |
| run013 | 2026-05-04 | Source-layout verification and memory reconciliation | Confirmed run011 propagation complete; stale pending-propagation notes removed from /memory files; docs/release-control.md and docs/llm-endpoint-strategy.md updated; repeatable agentic workflow section added; master-plan.md v2.9 |
| run014 | 2026-05-04 | Phase 0 closure-readiness sprint — full governance audit | All 45 Phase 0 files audited; stale "run003 bundle" reference in Section 7 fixed; Section 8 and Section 31 file count corrected (44→45); 28 search patterns verified (1 FIXED, rest PASS); memory files updated; master-plan.md v2.10 |
| run015 | 2026-05-04 | Combined sprint: Phase 0 acceptance + baseline commit + Phase 1A FODS scoring | Phase 0 accepted (all 36 checks PASS); G-001/G-002 closed; Phase 0 baseline commit made; FODS scored 93/100 (Accept band); registry entry created (gate_1: scored_pending_human_approval); TC-0001 updated; master-plan.md v2.11 |
| run016 | 2026-05-04 | Independent verification sprint for run015 Phase 0 acceptance, commit c9d02da, FODS Gate 1 scoring, and governance rule addition | Phase 0 acceptance independently verified (all 36 checks PASS). Commit c9d02da verified (61 files, no forbidden paths, no secrets). FODS scoring independently verified (93/100 math confirmed, 7-factor weights correct, status correctly scored_pending_human_approval, no self-approval). Source claims reviewed (all PLAUSIBLE or SUPPORTED; none OVERSTATED or FABRICATED). New governance rule added (DEC-034): agent-requested human review requires independent agent verification sprint first. AGENTS.md Section V added. GOVERNANCE.md Section 15 added. Memory files updated. master-plan.md v2.12 |
| run017 | 2026-05-04 | Gate 1 approval and Phase 2 setup | Gate 1 approved by Babar Raza (2026-05-04). Registry gate_1.status set to passed. TC-0001 closed. acquisition-packs/fods/ skeleton created (5 files: pack.yaml, spec-evidence.md, legal-notes.md, sample-sources.md, parser-notes.md). TC-0009 created (Phase 2, not_started). run016+run017 changes committed. Evidence bundle produced (full-width). master-plan.md v2.13 |
| run018 | 2026-05-04 | State reconciliation — stale docs and settings healed | Verified actual repo state. Registered G-HEAL-018 through G-HEAL-025. Fixed Section 23, 25, 27, 28, 33, footer. Fixed README.md, ROADMAP.md. Updated settings.json to Phase 2 conservative mode. No Gate 2 work. No commit made. master-plan.md v2.14 |
| run019 | 2026-05-04 | Combined sprint: run018 commit + TC-0007 tooling + TC-0009 Gate 2 evidence draft | Independently verified run018 (27 checks PASS). Committed run018 (0c97256). Moved TC-0007 scripts from settings.json deny→allow. Implemented TC-0007 (spec_index.py 354 lines, acquire_spec.py, refresh_check.py; smoke tests pass). Completed TC-0009 Gate 2 evidence draft (spec-evidence.md, legal-notes.md; fast-path 4/7 confirmed; gate_2: evidence_draft_pending_independent_verification). Updated pack.yaml, registry gate_2 status, TC-0009 taskcard. Committed run019 (589c1af). master-plan.md v2.15 |
| run020 | 2026-05-04 | Independent verification + schema reconciliation + spec acquisition attempt | Independently verified run019 (5 issues found): spec_index.py REQUIRED_FIELDS restructured; acquire_spec.py spurious warning removed; refresh_check.py Windows encoding bug fixed; docs/specification-cache.md schema/lifecycle updated; settings.json phase_note corrected. Spec download attempted — --allow-network denied; pre-download spec-index.yaml metadata entry created. spec-evidence.md + legal-notes.md updated (5/8 fast-path confirmed). G-021 logged. Committed tooling fixes (1e69121). Evidence leftovers committed (e8ab83f) in continuation session. master-plan.md v2.16 |
| run021 | 2026-05-04 | Combined: hygiene + settings.json fix + spec acquisition + Gate 2 evidence upgrade | Verified run020 (e8ab83f committed all leftovers; clean working tree). __pycache__ removed. settings.json deny for python *acquire_spec* removed (T3 authorized in run021 prompt). ODF 1.3 Part 3 PDF downloaded (24.27 MB, sha256:92cfe64...b066). spec-index.yaml VALID/CURRENT. spec-evidence.md primary claims → SUPPORTED_BY_CACHED_SOURCE. legal-notes.md 6/8 checklist. TC-0007 → completed_independently_verified_run020. G-021 resolved. Committed 138effd. master-plan.md v2.17 |
| run022 | 2026-05-05 | Independent verification sprint (DEC-034) for run021 evidence + stale-state fixes | Independently verified run021 commit 138effd (SHA-256 re-verified: MATCH; spec-cache VALID/CURRENT; tooling dry-run confirmed; evidence claims reviewed). Stale state fixed: master-plan latest-commit, Section 33, Section 6, TC-0009 independent-verification checkbox, pack.yaml stages, registry next_allowed_action. Gate 2 status upgraded: evidence_cached_pending_independent_verification → evidence_cached_pending_human_review. TC-0010 future planning taskcard created (not_started). G-HEAL-028 through G-HEAL-036 registered. Master-plan v2.18. Committed 32cdb1c. |
| run023 | 2026-05-05 | Human Gate 2 approval recording + Gate 3 planning transition | Verified run022 state (32cdb1c, clean tree). Fixed stale status leftovers (pack.yaml header/notes, TC-0009 artifact table). Recorded Gate 2 approval: Babar Raza, 2026-05-05, OASIS RF Category 1, fast-path, patent search waived. TC-0009 closed. TC-0010 activated (planning_ready). TC-0011 created (not_started — future Gate 3 verification). README.md + ROADMAP.md updated. Master-plan v2.19. No samples acquired. No push. |
| run024 | 2026-05-05 | Independent verification of run023 + stale fixes + Specification Normalization Layer + Gate 3 planning | Verified run023 (5 stale issues fixed: pack.yaml, settings.json, sample-sources.md). Created: docs/specification-normalization.md, tools/spec-normalize/ (4 files). Governance integration: AGENTS.md W, GOVERNANCE.md 16, gates.md, specification-cache.md. TC-0012 created. TC-0010 updated. Local normalization dry-run: SHA-256 MATCH, source-manifest.yaml written, G-NORM-001 logged. sample-sources.md corpus plan drafted. Master-plan v2.20. |
| run025 | 2026-05-05 | Independent verification of run024 + full FODS spec normalization + TC-0013 creation | Verified run024 (01f7bbe; valid uncommitted leftover confirmed). pdfminer.six 20260107 installed. Full extraction: text.txt 2,160,370 chars, pages.jsonl 782 pages. Citations: 194 section refs, 35 external refs. Validation: 7 PASS, 1 WARN, 0 FAIL. G-NORM-001 RESOLVED. requirements.txt added. TC-0012 Phase 2 complete. TC-0013 created (not_started). sample-sources.md spec refs verified. Master-plan v2.21. |
| run026 | 2026-05-05 | Spec Navigation Layer + Gate 3 corpus execution + TC-0014 | Verified run025 (f17bb12; valid uncommitted leftover confirmed). Built 4 navigation tools: build_section_index.py (884 sections, 705 pages), build_chunk_index.py (940 chunks), query_normalized_spec.py, export_sample_requirements.py. Produced: sample-requirements.yaml (4 samples), parser-requirements-draft.yaml (10 reqs). Created 4 FODS samples (Apache-2.0): minimal-spreadsheet.fods, multi-sheet-basic.fods, typed-values-basic.fods, formula-basic.fods. Validation: 4/4 PASS. create_fods_samples.py + validate_fods_samples.py created. Provenance: 4 confirmed entries. Registry gate_3 updated. TC-0013 → in_progress. TC-0014 created (not_started). spec-normalization.md updated. Master-plan v2.22. Committed 8871777. |
| run027 | 2026-05-05 | Independent verification of run026 + stale fixes + Hybrid Spec Retrieval Strategy | Verified run026 (8871777; trivial master-plan leftover confirmed). Independent verification (DEC-034) PASS: 21 checks PASS, 6 stale issues found and fixed. Stale fixes: master-plan header (f17bb12→8871777), settings.json notes[0] (Phase 2→3), TC-0013 prerequisites (lines 67-68 checked), TC-0013 planned-sample-names labeled, sample-sources.md (full update: status, filenames, checklist, history), parser-notes.md gate status. SHA-256 hashes added to provenance.yaml. Validation re-run: 4/4 PASS. Nav layer smoke-tested: §3.1.2 query ✓, core-req query ✓, section rebuild 705pp ✓. Gate 3 status: sample_corpus_created_pending_independent_verification → sample_corpus_verified_pending_human_review. Hybrid Spec Retrieval Strategy: docs/spec-retrieval-strategy.md (10 sections, Tier 1+2+3 design). TC-0015 created (evaluation, not_started). TC-0016 created (vector index pilot, not_started). AGENTS.md Section X added. settings.json updated. Master-plan v2.23. Committed 09ee31f. |
| run028 | 2026-05-05 | Gate 3 approval + Gate 4 planning package + memory updates | Verified run027 (09ee31f; working tree clean). Recorded Gate 3 approval: Babar Raza, 2026-05-05. Updated registry gate_3 → passed. next_allowed_action → gate4_parser_prototype_planning. Stale fixes: master-plan header (8871777→09ee31f), settings.json notes[0] (run027 commit pending→Gate 3 PASSED), pack.yaml header/notes/next_action, README.md (Gate 3 PASSED, Gate 4 next), ROADMAP.md (Gate 3 PASSED). TC-0011 closed (superseded by run027 verification). TC-0013 completed (Gate 3 approval recorded). TC-0014 activated (planning_ready). TC-0015+TC-0016 updated (cloud-DB/no-mixing/stale-hash restrictions added). Created parser planning package: parser-requirements.md, parser-scope.md, parser-test-plan.md. Created TC-0017 (Gate 4 prototype execution, not_started) and TC-0018 (Gate 4 prototype verification DEC-034, not_started). Memory files updated: 03 (Hybrid Retrieval architecture section), 05 (D-046–D-049), 09 (complete rewrite to run028 current state), 10 (run027+run028 update entries). External MEMORY.md updated. Master-plan v2.24. Committed 5c93b88. |
| run029 | 2026-05-05 | run028 independent verification + stale-state fixes + TC-0017 Gate 4 prototype execution | Verified run028 (5c93b88; working tree clean). All 33 verification checks PASS. Stale fixes: master-plan header (09ee31f→5c93b88), settings.json description→Gate4 execution mode, prototypes/by-format/fods/** moved to allow list, notes[0] updated. parser-notes.md Gate 3 status fixed. TC-0017 executed: prototype created at prototypes/by-format/fods/fods_parser.py (Python stdlib only, ElementTree). Validation: PT-001 PASS (8/8), PT-002 PASS (6/6), PT-003 PASS (8/8), PT-004 PASS (8/8) = 4/4 overall PASS. Test plan discrepancies documented: PT-001 text "Hello" vs predicted "Hello, World!"; PT-002 sheets "Data"/"Summary" vs predicted "Sheet1"/"Sheet2"; PT-003 no date cell vs predicted date cell. All discrepancies in prototype-notes.md + parser-notes.md. Registry gate_4 → prototype_created_pending_independent_verification. next_allowed_action → gate4_independent_verification_tc0018. TC-0017 → prototype_created_pending_independent_verification (acceptance criteria updated). TC-0018 → ready_for_execution. TC-0019 created (Gate 5 neutral model planning, not_started). Created: prototypes/by-format/fods/fods_parser.py, README.md, validate_against_samples.py, prototype-notes.md. Updated: parser-notes.md, parser-test-plan acceptance criteria context. Memory files updated: 05 (D-050), 09 (current state rewrite), 10 (run029 entry). External MEMORY.md updated. Master-plan v2.25. Committed d8187e0. No product source. No schema. No push. Gate 4 NOT approved. |
| run030 | 2026-05-06 | run029 independent verification (TC-0018) + stale fixes + Spec Workbench v1 + parser planning updates | Verified run029. TC-0018 DEC-034 PASS. Spec Workbench v1 created (local-only, 205/205 PASS). 5 new tools + docs/spec-consumption-workbench.md. TC-0020/TC-0021 created. Registry gate_4 → prototype_verified_pending_human_review. Master-plan v2.26. Committed 9382e66 + 4ca85ad. |
| run031 | 2026-05-06 | run030 independent verification + stale fixes + Evidence Bundle Contract system + TC-0021 workbench quality review + Gate 4 human-review packet | Verified run030 (4ca85ad; working tree clean, 30/30 checks PASS). Stale fixes: master-plan commit refs (ea20cde→4ca85ad), memory/09 commit refs, settings.json vector index allow→evidence allow. Evidence Bundle Contract system: tools/evidence/ (builder, validator, contracts, collectors). TC-0022 created (completed_pending_independent_verification). TC-0021 quality review PASS (205/205 validation, all packs verified). TC-0018 rerun: 4/4 PASS. Gate 4 human-review packet created (acquisition-packs/fods/gate4-human-review-packet.md). TC-0019 → ready_for_execution_after_gate4_approval. TC-0023 created (not_started). AGENTS.md Section Y + GOVERNANCE.md Section 18 (evidence bundle policy). No Gate 4 approval. No product source. No schema. No embeddings. Master-plan v2.27. |
| run032 | 2026-05-06 | run031 independent verification (DEC-034) + stale fixes + reusable evidence contracts + Gate 5 planning prep | Verified run031 (31/31 checks PASS). Stale fixes: master-plan line 9 commit ref (4ca85ad→17bceff), TC-0021 header status, TC-0022 → completed_verified, gate4-human-review-packet TC-0021 status. Evidence contract system independently verified: dry-run FAIL correct, run031 bundle PASS. TC-0021 workbench quality independently verified: 205/205 PASS reproduced. TC-0018 prototype rerun: 4/4 PASS. Gate 4 review packet audit: all fields correct, gate_4_approved=false confirmed. Created 4 reusable evidence contracts (gate-approval, gate-execution, independent-verification, spec-workbench). Gate 5 planning checklist created. TC-0019 current state updated (run032). Registry gate_4 notes extended with run032 verification. No Gate 4 approval. No product source. No schema. No embeddings. Master-plan v2.28. |
| run033 | 2026-05-06 | run032 independent verification + Gate 4 approval recording + TC-0018 closure + Gate 5 neutral model execution (TC-0023) + TC-0024/TC-0025 creation | Verified run032 (31/31 checks PASS). Gate 4 approved by Babar Raza (2026-05-06, run033 prompt). TC-0018 closed. Settings.json updated for Gate 5 (schemas/neutral-model/fods/** moved to allow). Gate 5 neutral model v1 created: schemas/neutral-model/fods/ (7 files: README.md, model.yaml, model.schema.json, field-map.yaml, coverage-matrix.yaml, validation-rules.yaml). tools/model/validate_neutral_model.py created. 6 entities: Workbook, Sheet, Row, Cell, Formula, Warning. 19 field mappings (14 direct, 1 rename, 1 expand, 3 derived). 30 coverage features (13 covered, 2 partial, 10 deferred, 5 out-of-scope). 21 validation rules (18 error, 3 warning). Validation: 4/4 samples PASS (87 total checks, 0 errors). acquisition-packs/fods/neutral-model-notes.md created. TC-0023 → neutral_model_created_pending_independent_verification. TC-0024 created (Gate 5 DEC-034 verification, ready_for_execution). TC-0025 created (Gate 6 oracle planning, not_started). TC-0019 superseded_by_tc0023. Registry gate_5 → neutral_model_created_pending_independent_verification. No Gate 5 approval. No product source. No embeddings. Master-plan v2.29. |
| run034 | 2026-05-06 | run033 independent verification + evidence hardening + TC-0024 DEC-034 verification + Gate 5 review packet + Gate 6 planning + TC-0026/TC-0027 | Verified run033 (35/35 checks PASS, working tree clean). Evidence bundle system hardened: builder and validator updated with git cleanliness check, contract-in-bundle enforcement, manifest generation, min metadata count enforcement; negative test PASS (thin bundles correctly rejected). TC-0024 DEC-034 executed: validate_neutral_model.py independently re-run against all 4 samples (4/4 PASS, 87 checks, 82 PASS, 5 WARN, 0 ERROR). model.yaml 6 entities verified. model.schema.json valid JSON Schema. field-map.yaml 19 mappings verified. coverage-matrix.yaml 30 features verified. validation-rules.yaml 21 rules verified. No forbidden paths. No Gate 5 self-approval. Registry gate_5 → neutral_model_verified_pending_human_review. Gate 5 human-review packet created (gate5-human-review-packet.md). Gate 6 planning: gate6-oracle-plan.md, oracle-scope.md, oracle-risk-register.md (planning only, NO execution). TC-0026 (Gate 6 execution, not_started), TC-0027 (Gate 6 verification, not_started) created. No Gate 5 approval. No Gate 6 execution. No product source. No embeddings. Master-plan v2.30. Commits: 2176266 + 074386a (builder fix) + f59fc46 (Section 33). |
| run035 | 2026-05-07 | run034 independent verification + Gate 5 approval + TC-0024 closure + Gate 6 oracle preflight + oracle harness creation (TC-0026 blocked) | Verified run034 (34/34 checks PASS): all 3 commits exist (2176266, 074386a, f59fc46); validate_neutral_model.py 4/4 PASS re-confirmed; run034 evidence bundle validates; no forbidden paths; no Gate 5 self-approval. Commit discrepancy: human summary mentioned f59fc46 not in bundle git-log — RESOLVED: bundle was built between 2176266 and 074386a; f59fc46 was post-bundle commit; all commits present in checkout. Stale-state fixes: master-plan header (ea20cde→f59fc46, pending→clean; version 2.30→2.31), memory/09, TC-0024 checkboxes unchecked→checked. Gate 5 PASSED by Babar Raza (2026-05-06, human-authorized run035 prompt); registry gate_5 → passed; approved_by: Babar Raza; approved_date: 2026-05-06. TC-0024 CLOSED; TC-0023 COMPLETED; TC-0025 COMPLETED (planning reviewed). Oracle preflight (Section G): soffice/libreoffice not found — BLOCKED. Oracle harness created: tools/oracle/ (5 files: README.md, preflight_oracle.py, run_fods_oracle.py, compare_fods_oracle.py, summarize_oracle_results.py). gate6-oracle-blocker-report.md created. Registry gate_6 → oracle_blocked_missing_tool. TC-0026 → blocked_missing_oracle_tool. TC-0027 → not_started. TC-0028 NOT created (no oracle comparison produced). No Gate 6 approval. No product source. No embeddings. Master-plan v2.31. |
| run036 | 2026-05-07 | run035 independent verification PASS + oracle harness hardening (oracle_common.py, FORMAT_FACTORY_SOFFICE) + stale path fixes + blocker report hardened + installation checklist + evidence validator fix | Verified run035 (5 commits: 179e6db, 625fca1, 2fb4e35, 1e14079, 1be6c0a; Gate 5 PASSED confirmed; validate_neutral_model.py 4/4 PASS re-confirmed; forbidden paths absent; no self-approval). Evidence validator hardened: git-status-final.txt OR git-status.txt both accepted; missing git status → FAIL (was WARN). oracle_common.py created: shared constants (SAMPLES_DIR, ORACLE_LOCAL_DIR, RAW_EXPORTS_DIR, PER_SAMPLE_DIR, all report paths), LIBREOFFICE_CANDIDATES list, find_soffice() with priority order, check_samples(), print_discovery_summary(). All 4 oracle scripts rewritten to import from oracle_common. FORMAT_FACTORY_SOFFICE env var checked in discovery. --soffice-path CLI arg added (preflight + run). Oracle preflight re-run: FAIL (10 candidates tried, all MISS, FORMAT_FACTORY_SOFFICE not set). Stale path refs fixed in TC-0026/TC-0027/gate6-oracle-plan.md/oracle-scope.md (`.local/oracle-outputs/fods/` → `.local/oracle/fods/`; `reports/fods-oracle.md` → `acquisition-packs/fods/gate6-oracle-comparison-report.md`). oracle-installation-checklist.md created. gate6-oracle-blocker-report.md hardened with run036 diagnostics and improvements table. tools/oracle/README.md updated (canonical path model, discovery priority, run036 status). No Gate 6 approval. No product source. No embeddings. Master-plan v2.32. |
| run037 | 2026-05-07 | run036 independent verification PASS + stale state fixed + oracle provider abstraction + --check-no-pending validator + 4 negative tests + oracle preflight re-run 3 | Verified run036 (3 commits: 8acd48d+82281e6+3216dcf). Stale fixed: master-plan header 82281e6→3216dcf, memory/09 commit. Validator --check-no-pending flag added; 4 negative tests PASS. tools/oracle/provider_registry.yaml + validate_oracle_environment.py + docs/oracle-provider-strategy.md + oracle-provider-options.md created. Oracle preflight re-run (3rd): FAIL. blocker report updated. No Gate 6 approval. No product source. No embeddings. Master-plan v2.33. Commits: de29c97+f964eba+a35b089. |
| run038 | 2026-05-07 | run037 independent verification PASS + stale commit fixed + harness self-test (PASS 4/4, HARNESS_SELF_TEST_ONLY) + operator handoff + candidate shortlist (TC-0028, no Gate 1 approval) + oracle preflight re-run 4 | Verified run037 (3 commits confirmed). Stale fixed: f964eba→a35b089, memory/09. self_test_oracle_harness.py created (HARNESS_SELF_TEST_ONLY; PASS 4/4). oracle-operator-handoff.md + oracle-harness-self-test-report.md created. odf-flat-family-shortlist.yaml created (FODT; gate_1_approved: false). TC-0028 created. Oracle preflight re-run (4th): FAIL. TC-0026 blocker wording corrected. No Gate 6 approval. No product source. No embeddings. Master-plan v2.34. Commits: 1e1d504+e0fc07c+998412c+bc2bdf8. |
| run039 | 2026-05-07 | run038 independent verification PASS + stale commit fixed + consistency enforcement tool + FODT Gate 1 scoring package (candidate-only) + ODF reuse strategy + oracle preflight re-run 5 | Verified run038 (4 commits; BUNDLE_VALIDATION: PASS). Stale fixed: 998412c→bc2bdf8, memory/09. check_current_state_consistency.py created; 4 negative tests PASS. fodt-gate1-scoring-package.yaml created (88/100; gate_1_approved: false). TC-0029 created. odf-flat-family-reuse-strategy.md created. Oracle preflight re-run (5th): FAIL. TC-0028 → in_progress. No Gate 6 approval. No product source. No embeddings. Master-plan v2.35. Commits: 48f6a0d+8cd2ed2+075edca+d052510+54a27dc. |
| run040 | 2026-05-07 | run039 independent verification PASS (44 checks) + stale commit fixed + clean-git loophole closed + consistency checker strengthened (10 checks) + TC-0029 DEC-034 PASS (7/7, 88/100) + FODT Gate 1 human-review packet + oracle preflight re-run 6 | Verified run039 (5 commits; 44 checks PASS). Stale fixed: master-plan d052510→54a27dc, memory/09. Clean-git loophole closed (dirty git always fails unless emergency_blocker_bundle: true). base-run.yaml updated. 2 new negative tests (6/6). Consistency checker → 10 checks. Oracle preflight re-run (6th): FAIL (6 consecutive). TC-0029 DEC-034 PASS (7/7 verified, 88/100). fodt-gate1-human-review-packet.md created. TC-0029 → verification_passed_pending_human_review. README/ROADMAP/registry/settings.json/docs/blocker-report updated. Master-plan v2.36. |
| run041 | 2026-05-07 | run040 independent verification PASS + stable run-state authority model + FODT Gate 1 APPROVED (Babar Raza) + FODT acquisition skeleton + TC-0030 + oracle preflight re-run 7 | Verified run040 PASS. Self-referential commit-hash model REPLACED: docs/current-state-and-evidence-authority.md created; check_current_state_consistency.py redesigned (PENDING-marker + FODT consistency checks, no hash matching); validate_evidence_bundle.py extended (repo current-state PENDING scan); build_evidence_bundle.py auto-generates git metadata; base-run.yaml v1.1; 7/7 tests PASS. Section 33 renamed to "Run Commit Ledger". FODT Gate 1 APPROVED (Babar Raza, 2026-05-07, 88/100): registry FODT entry; acquisition-packs/fodt/ (6 files); TC-0030; TC-0029+TC-0028 COMPLETED. Oracle preflight (7th): FAIL (7 consecutive). Master-plan v2.37. |
| run042 | 2026-05-08 | run041 independent verification PASS (47 checks) + evidence-contract repair (base-run.yaml v1.2) + validate_evidence_bundle.py .env.example fix + FODT Gate 2 evidence executed (TC-0030) + TC-0031 created + oracle preflight re-run 8 | Verified run041 (47 checks PASS; 5-metadata regression confirmed). base-run.yaml v1.2: min_metadata_count→30, normal_pass_min_metadata:30. validate_evidence_bundle.py: matches_forbidden exact-match fix (.env.example no longer blocked by .env pattern); NORMAL_PASS_METADATA_DEPTH check added; 8/8 negative tests PASS. fodt-gate1-scoring-package.yaml CANDIDATE-ONLY header → GATE 1 APPROVED record. master-plan skeleton "(5 files)"→"(6 files)" fixed; last_completed_run: run040→run041 fixed. TC-0030 FODT Gate 2 executed: spec-evidence.md→SUPPORTED_BY_CACHED_SOURCE; legal-notes.md→FAST_PATH_DECLARED (8/8 items, patent waived); pack.yaml gate_2→evidence_cached_pending_independent_verification; registry gate_2 updated; gate2-human-review-packet.md created. TC-0031 created (DEC-034, not_started). Oracle preflight (8th): FAIL (8 consecutive: run035–run042). Master-plan v2.38. |

---

## Section 33 — Run Commit Ledger and Evidence Authority

**Current-state authority (run041+):** Committed repo files record run state and gate state only.
The exact final Git HEAD for each run is authoritative in `bundle-metadata/git-log.txt` and
`bundle-metadata/git-status-final.txt` in the run's evidence bundle.
See `docs/current-state-and-evidence-authority.md`.

**last_completed_run:** run051 (exact final HEAD in bundle-metadata/git-log.txt)
**run051 commit set:** d18e73e + 559c672 + b960609 + 199cff3
**run050 commit set:** cc6d00c + 9da927d + 3a7c2b0 + c23588a + 3a14a05 + e5fcde7 + 134e3e9 + 7671e42 + dfb172f + 07fc026
**run049 commit set:** 2b0d448 + 8fd26fa + 3964298 + f487d5e + 743fa38 + ba6aad2 + 740514f + 594f1a2 + 1c75d7e + 365ff9a + 8552d1c
**run044 commit set:** 0e732c3
**run043 commit set (informational):** bc92729
**run042 commit set:** b6e4316 + e31dc66 + fd098c9 + 079ba6d
**run041 commit set (informational):** f16ddf0
**run040 commit set (informational):** b3cfdd7 + 2ca4b78 + d4e6390 + a60826a + f451804 + 1bdafb5 + a4f79e0 + 931ef34 + 411180a
**run039 commit set:** 48f6a0d + 8cd2ed2 + 075edca + d052510 + 54a27dc
**run038 commit set:** 1e1d504 + e0fc07c + 998412c + bc2bdf8
**run037 commit set:** de29c97 + f964eba + a35b089
**run036 commit set:** 8acd48d + 82281e6 + 3216dcf
**run035 commit set:** 179e6db + 625fca1 + 2fb4e35 + 1e14079 + 1be6c0a
**run034 commit set:** 2176266 + 074386a + f59fc46

**Committed so far:**
- c9d02da (run015): Phase 0 foundation + Phase 1A FODS scoring
- c79f2d1 (run017): Gate 1 approval, acquisition-packs/fods/ skeleton, TC-0009, AGENTS.md Section V, GOVERNANCE.md Section 15, memory updates
- 0c97256 (run018 via run019): State reconciliation — README.md, ROADMAP.md, settings.json Phase 2, master-plan v2.14
- 589c1af (run019): Gate 2 evidence draft + TC-0007 implementation + settings.json allow list update
- 1e69121 (run020): spec_index.py schema fix, acquire_spec.py warning fix, refresh_check.py encoding fix, docs/specification-cache.md update, settings.json phase_note fix
- e8ab83f (run020 continuation): pack.yaml spec_cache section, spec-evidence.md, legal-notes.md, registry gate_2 notes, TC-0009, master-plan v2.16, memory 06/08/09
- 138effd (run021): settings.json deny removed, spec-evidence.md SUPPORTED_BY_CACHED_SOURCE upgrade, legal-notes.md 6/8, pack.yaml spec_cache downloaded, registry gate_2 status, TC-0007+TC-0009 updated, master-plan v2.17, memory 06/09
- 32cdb1c (run022): independent verification of run021 evidence, stale state fixed (G-HEAL-028–036), gate_2.status → evidence_cached_pending_human_review, TC-0010 created, master-plan v2.18, memory 06/09, registry/pack.yaml/settings.json updated
- c9d8d8e (run023): Gate 2 approved (Babar Raza 2026-05-05), patent search waived, TC-0009 closed, TC-0010 planning_ready, TC-0011 created, README+ROADMAP updated, memory 06/09 updated, master-plan v2.19
- 01f7bbe (run024): Specification Normalization Layer + AGENTS.md W + GOVERNANCE.md 16 + TC-0012 + docs + normalization dry-run
- f17bb12 (run025): Full FODS spec normalization (G-NORM-001 resolved), requirements.txt, TC-0013 created, sample-sources.md updated, master-plan v2.21
- 8871777 (run026): Spec Navigation Layer (4 tools) + Gate 3 corpus (4 FODS samples, 4/4 PASS) + TC-0014 + settings.json Phase 3 + master-plan v2.22

**Committed (09ee31f, run027):**
- plans/master-plan.md v2.23, AGENTS.md Section X, docs/spec-retrieval-strategy.md (NEW), TC-0015 (NEW), TC-0016 (NEW), settings.json, samples/_provenance.yaml (SHA-256 hashes), registry gate_3 status, TC-0013 (updated), sample-sources.md, parser-notes.md

**Committed (5c93b88, run028):**
- plans/master-plan.md v2.24, registry gate_3 passed, acquisition-packs/fods/pack.yaml, parser-requirements.md (NEW), parser-scope.md (NEW), parser-test-plan.md (NEW), TC-0011 closed, TC-0013 completed, TC-0014 planning_ready, TC-0015/TC-0016 restrictions, TC-0017 (NEW), TC-0018 (NEW), README.md, ROADMAP.md, settings.json, memory/03/05/09/10

**Committed (d8187e0, run029):**
- prototypes/by-format/fods/fods_parser.py (NEW), prototypes/by-format/fods/README.md (NEW), prototypes/by-format/fods/validate_against_samples.py (NEW), prototypes/by-format/fods/prototype-notes.md (NEW), taskcards/TC-0019 (NEW), plans/master-plan.md v2.25, registry/format-registry.yaml gate_4 updated, acquisition-packs/fods/parser-notes.md, acquisition-packs/fods/pack.yaml gate_4 section, .claude/settings.json, taskcards/TC-0017/TC-0018 updated, README.md, ROADMAP.md, memory/05/09/10

**Committed (ea20cde, run029):**
- plans/master-plan.md (TC table rows updated, master-plan.md Section 33 latest commit d8187e0 recorded), taskcards/TC-0014 (current state updated)

**Committed (9382e66, run030):**
- docs/spec-consumption-workbench.md (NEW)
- tools/spec-normalize/build_spec_workbench.py (NEW)
- tools/spec-normalize/build_requirement_pack.py (NEW)
- tools/spec-normalize/validate_requirement_pack.py (NEW)
- tools/spec-normalize/export_task_packet.py (NEW)
- taskcards/TC-0020-spec-workbench-core.md (NEW)
- taskcards/TC-0021-fods-workbench-quality-review.md (NEW)
- .claude/settings.json (settings.json contradiction fixed: prototypes/fods moved to allow)
- registry/format-registry.yaml (gate_4 → prototype_verified_pending_human_review; next_allowed_action → gate4_human_approval)
- taskcards/TC-0017 (status → completed)
- taskcards/TC-0018 (status → verification_passed_pending_human_review; acceptance criteria all checked)
- taskcards/TC-0019 (blocker updated: TC-0018 no longer blocking)
- acquisition-packs/fods/parser-requirements.md (workbench cross-reference added)
- acquisition-packs/fods/parser-scope.md (status updated; revision history)
- acquisition-packs/fods/parser-test-plan.md (all statuses updated to PASS; discrepancies corrected)
- acquisition-packs/fods/parser-notes.md (Gate 4 status → verified; workbench section added; gate sign-off updated)
- plans/master-plan.md v2.26 (Section 6 updated; Section 33 current; run030 history entry added)
- memory/09 (latest commit, uncommitted, run030)
**Committed (4ca85ad, run030 post-commit):**
- plans/master-plan.md Section 33 latest commit record, taskcards/TC-0014 current state

**Committed (40f4ae5, run031):**
- tools/evidence/** (Evidence Bundle Contract system: builder, validator, contracts, collectors)
- TC-0022, TC-0023 created; TC-0021 quality_review_passed; TC-0019 ready_for_execution_after_gate4_approval
- Gate 4 human-review packet (acquisition-packs/fods/gate4-human-review-packet.md)
- AGENTS.md Section Y, GOVERNANCE.md Section 18
- Stale state fixes (master-plan, memory/09, settings.json)
- README.md, ROADMAP.md, registry/format-registry.yaml updated
- (.local/ artifacts NOT committed — normalized/, spec cache, workbench, run records, evidence bundles)

**Committed (ea141fb, run032):**
- tools/evidence/contracts/ (4 new reusable contracts: gate-approval, gate-execution, independent-verification, spec-workbench)
- acquisition-packs/fods/gate5-planning-checklist.md (NEW), gate4-human-review-packet.md (TC-0021 status updated)
- taskcards/TC-0021 (run032 revision history), TC-0022 (completed_verified), TC-0019 (current state updated)
- registry/format-registry.yaml (gate_4 notes extended with run032 verification)
- plans/master-plan.md v2.28, memory/09 updated

**Committed (28881e3, run033):**
- schemas/neutral-model/fods/ (6 NEW files: README.md, model.yaml, model.schema.json, field-map.yaml, coverage-matrix.yaml, validation-rules.yaml)
- tools/model/validate_neutral_model.py (NEW)
- acquisition-packs/fods/neutral-model-notes.md (NEW)
- taskcards/TC-0024 (NEW), TC-0025 (NEW)
- registry/format-registry.yaml (gate_4 passed, gate_5 neutral_model_created_pending_independent_verification)
- acquisition-packs/fods/pack.yaml (gate_4 passed, gate_5 status)
- taskcards/TC-0018 (closed), TC-0019 (superseded), TC-0023 (executed)
- .claude/settings.json (Gate 5 execution mode)
- README.md, ROADMAP.md, plans/master-plan.md v2.29, memory/09
- acquisition-packs/fods/gate4-human-review-packet.md (Gate 4 passed status)

**Committed (2176266, run034):**
- tools/evidence/validate_evidence_bundle.py (HARDENED: git cleanliness check, contract-in-bundle, manifest validation, min metadata enforcement)
- tools/evidence/build_evidence_bundle.py (HARDENED: git status check, manifest generation, contract-in-bundle, forbidden path matching)
- acquisition-packs/fods/gate5-human-review-packet.md (NEW)
- acquisition-packs/fods/gate6-oracle-plan.md (NEW)
- acquisition-packs/fods/oracle-scope.md (NEW)
- acquisition-packs/fods/oracle-risk-register.md (NEW)
- taskcards/TC-0024 (verification_passed_pending_human_review — DEC-034 PASS)
- taskcards/TC-0026 (NEW — Gate 6 execution, not_started)
- taskcards/TC-0027 (NEW — Gate 6 verification, not_started)
- registry/format-registry.yaml (gate_5 → neutral_model_verified_pending_human_review; tc0024_verification added)
- acquisition-packs/fods/pack.yaml (gate_5 status updated; gate_4_approved true; notes updated)
- .claude/settings.json (Gate 5 VERIFIED status)
- README.md, ROADMAP.md, plans/master-plan.md v2.30
- memory/09-current-state-before-phase1.md
- tools/evidence/contracts/run034-*.yaml (evidence contract)

**Committed (074386a, run034 builder fix):**
- tools/evidence/build_evidence_bundle.py (fix: manifest pre-check accounts for auto-generated manifest)

**Committed (f59fc46, run034 post-commit):**
- plans/master-plan.md Section 33 latest commit updated to 074386a

**Committed (179e6db, run035):**
- tools/oracle/ (5 NEW files: README.md, preflight_oracle.py, run_fods_oracle.py, compare_fods_oracle.py, summarize_oracle_results.py)
- acquisition-packs/fods/gate6-oracle-blocker-report.md (NEW)
- acquisition-packs/fods/gate5-human-review-packet.md (Gate 5 PASSED updated)
- acquisition-packs/fods/pack.yaml (gate_5 → passed; gate_6 oracle_blocked)
- taskcards/TC-0023 (status → completed)
- taskcards/TC-0024 (all checkboxes checked; status → closed)
- taskcards/TC-0025 (status → completed; current state updated)
- taskcards/TC-0026 (status → blocked_missing_oracle_tool; preconditions updated)
- registry/format-registry.yaml (gate_5 → passed approved_by Babar Raza; gate_6 → oracle_blocked_missing_tool)
- .claude/settings.json (Gate 6 conservative mode)
- README.md, ROADMAP.md, plans/master-plan.md v2.31, memory/09
- tools/evidence/contracts/run035-gate5-approval-gate6-oracle.yaml (evidence contract)

**Committed (625fca1, run035 post-commit):**
- plans/master-plan.md Section 33 updated with run035 commit hash 179e6db

**Committed (2fb4e35, run035 builder fix):**
- tools/evidence/build_evidence_bundle.py (fix: normalize required_repo_files list-of-dicts)

**Committed (1e14079, run035 validator fix):**
- tools/evidence/validate_evidence_bundle.py (fix: normalize required_repo_files list-of-dicts)

**Committed (8acd48d, run036):**
- tools/oracle/oracle_common.py (NEW — shared constants, LibreOffice discovery, path model)
- tools/oracle/preflight_oracle.py (REWRITTEN — uses oracle_common, --soffice-path, --verbose, FORMAT_FACTORY_SOFFICE)
- tools/oracle/run_fods_oracle.py (REWRITTEN — uses oracle_common, --soffice-path)
- tools/oracle/compare_fods_oracle.py (REWRITTEN — uses oracle_common, removed duplicates)
- tools/oracle/summarize_oracle_results.py (REWRITTEN — uses oracle_common canonical paths)
- tools/oracle/README.md (UPDATED — canonical path model, discovery priority, run036 status)
- tools/evidence/validate_evidence_bundle.py (HARDENED — git-status-final.txt OR git-status.txt; FAIL not WARN when missing)
- acquisition-packs/fods/gate6-oracle-blocker-report.md (HARDENED — run036 diagnostics, improvements table)
- acquisition-packs/fods/oracle-installation-checklist.md (NEW — step-by-step operator install guide)
- acquisition-packs/fods/gate6-oracle-plan.md (UPDATED — stale path refs fixed)
- acquisition-packs/fods/oracle-scope.md (UPDATED — stale path refs fixed)
- taskcards/TC-0026-fods-gate6-oracle-execution.md (UPDATED — canonical path model section)
- taskcards/TC-0027-fods-gate6-oracle-verification.md (UPDATED — stale path refs fixed)
- tools/evidence/contracts/run036-gate6-oracle-harness-hardening.yaml (NEW)
- plans/master-plan.md v2.32
- registry/format-registry.yaml gate_6 notes updated
- README.md, ROADMAP.md, .claude/settings.json, memory/09 updated

**Committed (82281e6, run036 post-commit):**
- plans/master-plan.md Section 33 latest commit updated to 8acd48d; memory/09 updated

**Committed (3216dcf, run036 Section 33):**
- plans/master-plan.md Section 33 latest commit updated to 82281e6

**Committed (de29c97, run037):**
- tools/oracle/provider_registry.yaml (NEW), tools/oracle/validate_oracle_environment.py (NEW),
  docs/oracle-provider-strategy.md (NEW), acquisition-packs/fods/oracle-provider-options.md (NEW),
  tools/evidence/validate_evidence_bundle.py (--check-no-pending flag added),
  tests/evidence/test_negative_bundle_validation.py (NEW — 4 negative tests),
  tools/evidence/contracts/run037-oracle-provider-readiness-or-gate6-execution.yaml (NEW),
  plans/master-plan.md v2.33, registry/format-registry.yaml gate_6 updated,
  acquisition-packs/fods/gate6-oracle-blocker-report.md updated,
  README.md, ROADMAP.md, .claude/settings.json, memory/09 updated

**Committed (f964eba, run037 post-commit):**
- plans/master-plan.md Section 33 latest commit updated to de29c97

**Committed (a35b089, run037 Section 33 final):**
- plans/master-plan.md Section 33 latest commit corrected to f964eba→a35b089

**Committed (1e1d504, run038):**
- tools/oracle/self_test_oracle_harness.py (NEW — HARNESS_SELF_TEST_ONLY; PASS 4/4)
- acquisition-packs/fods/oracle-operator-handoff.md (NEW — precise install/verify/execute)
- acquisition-packs/fods/oracle-harness-self-test-report.md (NEW — HARNESS_SELF_TEST_ONLY PASS)
- registry/candidates/odf-flat-family-shortlist.yaml (NEW — FODT recommended; gate_1_approved: false)
- acquisition-packs/_candidate-shortlists/odf-flat-family-next-candidates.md (NEW — CANDIDATE-ONLY)
- taskcards/TC-0028-next-format-candidate-shortlist.md (NEW — not_started)
- tools/evidence/contracts/run038-oracle-readiness-and-next-format-shortlist.yaml (NEW)
- plans/master-plan.md v2.34, registry/format-registry.yaml gate_6 updated,
  taskcards/TC-0026 blocker wording corrected,
  acquisition-packs/fods/gate6-oracle-blocker-report.md updated (run038 column added),
  acquisition-packs/fods/pack.yaml updated, docs/oracle-provider-strategy.md Section 6 updated,
  README.md, ROADMAP.md, .claude/settings.json, memory/09 updated

**Committed (e0fc07c, run038 post-commit):**
- plans/master-plan.md Section 33 latest commit updated to 1e1d504

**Committed (998412c, run038 Section 33 correction):**
- plans/master-plan.md Section 33 latest commit updated to e0fc07c

**Committed (bc2bdf8, run038 Section 33 final):**
- plans/master-plan.md Section 33 latest commit corrected to 998412c→bc2bdf8

**Committed (48f6a0d, run039):**
- tools/evidence/check_current_state_consistency.py (NEW — validates "Latest commit" in master-plan matches actual git HEAD + 2 other checks; CURRENT_STATE_CONSISTENCY: PASS)
- tests/evidence/test_current_state_consistency.py (NEW — 4 negative tests; all PASS)
- registry/candidates/fodt-gate1-scoring-package.yaml (NEW — FODT Gate 1 7-factor scoring: 88/100, Accept band, candidate-only; gate_1_approved: false)
- taskcards/TC-0029-fodt-gate1-scoring-preparation.md (NEW — not_started; FODT Gate 1 independent verification sprint)
- docs/odf-flat-family-reuse-strategy.md (NEW — ODF flat family pipeline reuse strategy, FODS→FODT ~40-50% effort)
- acquisition-packs/fods/gate6-oracle-blocker-report.md (UPDATED — run039 preflight re-run 5 recorded; improvements table)
- registry/format-registry.yaml gate_6 (UPDATED — run039 re-run recorded as 5th consecutive FAIL)
- README.md, ROADMAP.md, .claude/settings.json, memory/09 updated
- plans/master-plan.md v2.35

**Committed (8cd2ed2, run039 post-commit):**
- plans/master-plan.md Section 33 latest commit updated to 48f6a0d

**Committed (075edca, run039 stale fix):**
- plans/master-plan.md Section 33 stale commit reference corrected (bc2bdf8 re-confirmed as run038 final)

**Committed (d052510, run039 Section 33):**
- plans/master-plan.md Section 33 latest commit updated to 075edca

**Committed (54a27dc, run039 final Section 33):**
- plans/master-plan.md Section 33 latest commit corrected to d052510→54a27dc (run039 actual final)

**Committed (b3cfdd7, run040):**
- tools/evidence/validate_evidence_bundle.py (HARDENED — clean-git loophole closed: dirty git fails even with require_clean_git: false; emergency_blocker_bundle: true added as escape hatch)
- tools/evidence/build_evidence_bundle.py (HARDENED — same loophole fix: dirty git always fails unless emergency_blocker_bundle: true)
- tools/evidence/contracts/base-run.yaml (UPDATED — require_clean_git: true + emergency_blocker_bundle: false added as base defaults)
- tools/evidence/check_current_state_consistency.py (STRENGTHENED — 10 invariants: master-plan commits, memory/09 commit, registry gate_6 not approved, FODT candidate-only, pack.yaml gate_6)
- tests/evidence/test_negative_bundle_validation.py (UPDATED — 2 new negative tests: dirty-git-fails-with-require_clean_git_false, dirty-git-passes-with-emergency_blocker_bundle_true; 6/6 total PASS)
- acquisition-packs/_candidate-shortlists/fodt-gate1-human-review-packet.md (NEW — FODT Gate 1 human-review packet; 7/7 factors verified, 88/100 confirmed, WIP check, decision instructions)
- taskcards/TC-0029-fodt-gate1-scoring-preparation.md (UPDATED — status verification_passed_pending_human_review; DEC-034 PASS run040; review packet linked)
- acquisition-packs/fods/gate6-oracle-blocker-report.md (UPDATED — run040 preflight re-run 6; improvements table; 6 consecutive FAIL)
- registry/format-registry.yaml gate_6 (UPDATED — run040 re-run 6; clean-git loophole closed; consistency checker 10 checks; FODT Gate 1 DEC-034 verified)
- docs/oracle-provider-strategy.md (UPDATED — Section 6 updated: 6 consecutive FAIL; run040 loophole fix noted)
- README.md, ROADMAP.md, .claude/settings.json, memory/09, memory/MEMORY.md updated
- tools/evidence/contracts/run040-*.yaml (NEW — evidence contract)
- plans/master-plan.md v2.36

**Committed (f16ddf0, run041):**
- docs/current-state-and-evidence-authority.md (NEW — run-state authority policy)
- tools/evidence/check_current_state_consistency.py (REDESIGNED — PENDING-marker model; no hash matching; 7/7 tests PASS)
- tools/evidence/validate_evidence_bundle.py (EXTENDED — repo current-state PENDING scan)
- tools/evidence/build_evidence_bundle.py (ENHANCED — auto-generates git-log.txt + git-status-final.txt)
- tools/evidence/contracts/base-run.yaml v1.1 (current_state_authority: bundle-metadata; git metadata required)
- tools/evidence/contracts/run041-fodt-gate1-approval-and-state-authority.yaml (NEW)
- AGENTS.md Section Z (Run-State Authority Model)
- GOVERNANCE.md Section 19 (Run-State Authority and Current-State Consistency)
- registry/format-registry.yaml (FODT gate_1 passed; gate_1_approved_by Babar Raza; official entry)
- registry/candidates/fodt-gate1-scoring-package.yaml (gate_1_approved: true; approval metadata)
- acquisition-packs/fodt/ (6 NEW files: pack.yaml, spec-evidence.md, legal-notes.md, sample-sources.md, parser-notes.md, gate2-planning.md)
- acquisition-packs/_candidate-shortlists/fodt-gate1-human-review-packet.md (Gate 1 APPROVED updated)
- taskcards/TC-0030 (NEW — FODT Gate 2 spec/legal evidence)
- taskcards/TC-0029 (COMPLETED), TC-0028 (COMPLETED)
- acquisition-packs/fods/gate6-oracle-blocker-report.md (run041 preflight re-run 7 recorded)
- .claude/settings.json (acquisition-packs/fodt/** added to allow; run041 status)
- ROADMAP.md, README.md, memory/09, memory/MEMORY.md updated
- plans/master-plan.md v2.37

**Committed (2d5548a, run041 post-commit):**
- plans/master-plan.md Section 33 updated; memory/09 run041 state recorded

**Committed (b6e4316, run042):**
- tools/evidence/validate_evidence_bundle.py (HARDENED — matches_forbidden exact-match fix; NORMAL_PASS_METADATA_DEPTH check)
- tools/evidence/contracts/base-run.yaml v1.2 (min_metadata_count→30; normal_pass_min_metadata:30)
- tests/evidence/test_negative_bundle_validation.py (UPDATED — 2 new tests; 8/8 PASS)
- registry/candidates/fodt-gate1-scoring-package.yaml (CANDIDATE-ONLY header replaced with GATE 1 APPROVED record)
- acquisition-packs/fodt/spec-evidence.md (→ SUPPORTED_BY_CACHED_SOURCE; SHA-256 MATCH 3rd verify)
- acquisition-packs/fodt/legal-notes.md (→ FAST_PATH_DECLARED; 8/8 fast-path items; patent waived)
- acquisition-packs/fodt/pack.yaml (gate_2 → evidence_cached_pending_independent_verification)
- acquisition-packs/fodt/gate2-human-review-packet.md (NEW)
- registry/format-registry.yaml (FODT gate_2 status updated)
- taskcards/TC-0030 (status → evidence_executed_pending_dec034_verification; acceptance criteria updated)
- taskcards/TC-0031 (NEW — DEC-034 independent verification; not_started)
- plans/master-plan.md v2.38; memory/09, ROADMAP.md, README.md updated

**Committed (run043 — bc92729):**
- tools/oracle/oracle_common.py (FIXED — soffice.com added before soffice.exe in LIBREOFFICE_CANDIDATES; env var .com variant auto-try on Windows)
- tools/oracle/run_fods_oracle.py (FIXED — --infilter=OpenDocument Spreadsheet Flat XML; --convert-to csv:Text - txt - csv (StarCalc))
- tools/oracle/compare_fods_oracle.py (FIXED — parser subprocess CLI call corrected)
- acquisition-packs/fods/gate6-oracle-comparison-report.md (NEW — 3/4 PASS, 1/4 WARN, multi-sheet CSV limit)
- acquisition-packs/fods/gate6-oracle-blocker-report.md (UPDATED — BLOCKER RESOLVED; run043 improvements documented)
- taskcards/TC-0026 (→ COMPLETED — oracle comparison executed run043)
- taskcards/TC-0031 (→ COMPLETED — 20/20 PASS; DEC-034 satisfied)
- taskcards/TC-0030 (→ CLOSED — Gate 2 APPROVED)
- taskcards/TC-0032 (NEW — FODT Gate 3 DEC-034 verification; not_started)
- acquisition-packs/fodt/pack.yaml (gate_2 → passed; Babar Raza, 2026-05-08)
- acquisition-packs/fodt/gate2-human-review-packet.md (→ APPROVED)
- registry/format-registry.yaml (FODT gate_2 → passed; gate_3 → sample_corpus_created; FODS gate_6 → oracle_comparison_created; next_allowed_action updated)
- samples/by-format/fodt/ (NEW — 4 FODT samples: minimal-document.fodt, headings-and-paragraphs.fodt, list-basic.fodt, table-basic.fodt; FODT_SAMPLE_VALIDATION: PASS 4/4)
- tools/samples/validate_fodt_samples.py (NEW — FODT Gate 3 sample validation tool)
- samples/_provenance.yaml (UPDATED — 4 FODT entries, all provenance_status: confirmed)
- plans/master-plan.md v2.39; memory/09, ROADMAP.md, settings.json updated

**Committed (run044 — 0e732c3):**
- tools/evidence/build_evidence_bundle.py (FIXED — 2 bugs: metadata count off-by-one; matches_forbidden false-positives .env.example/.gitignore)
- acquisition-packs/fods/pack.yaml (UPDATED — gate_6 header + oracle_tool section; run043/run044 notes)
- acquisition-packs/fods/gate6-oracle-comparison-report.md (UPDATED — Gate 6 PASSED status)
- acquisition-packs/fods/gate6-human-review-packet.md (NEW — TC-0027 DEC-034 PASS 24/24 gate review packet)
- acquisition-packs/fods/gate7-malformed-fuzz-plan.md (NEW — Gate 7 planning: 18 malformed inputs, 4 categories)
- acquisition-packs/fods/gate7-risk-scope.md (NEW — Gate 7 risk and scope analysis)
- acquisition-packs/fodt/pack.yaml (UPDATED — gate_3 → passed; Gate 3 approved header)
- acquisition-packs/fodt/sample-sources.md (UPDATED — GATE_3_PASSED status; corpus table)
- acquisition-packs/fodt/gate3-human-review-packet.md (NEW — TC-0032 DEC-034 PASS 27/27 gate review packet)
- acquisition-packs/fodt/gate4-parser-prototype-plan.md (NEW — Gate 4 planning)
- acquisition-packs/fodt/parser-requirements.md (NEW — FR-001..FR-007)
- acquisition-packs/fodt/parser-scope.md (NEW — scope definition)
- acquisition-packs/fodt/parser-test-plan.md (NEW — PT-001..PT-004)
- acquisition-packs/fodt/parser-notes.md (UPDATED — PLANNING_READY status)
- taskcards/TC-0026 (UPDATED — COMPLETED stale text replaced)
- taskcards/TC-0027 (UPDATED — COMPLETED 24/24)
- taskcards/TC-0032 (UPDATED — COMPLETED 27/27)
- taskcards/TC-0033 (NEW — FODS Gate 7 malformed/fuzz; not_started)
- taskcards/TC-0034 (NEW — FODT Gate 4 parser prototype; not_started)
- taskcards/TC-0035 (NEW — FODT Gate 4 DEC-034 verification; not_started)
- registry/format-registry.yaml (FODS gate_6 → passed; gate_7 → planning_ready; FODT gate_3 → passed; gate_4 → planning_ready; next_allowed_action updated)
- plans/master-plan.md v2.40; memory/09, ROADMAP.md, README.md, settings.json updated
- tools/evidence/contracts/run044-*.yaml (NEW — run044 evidence contract)

**Committed (run045 — 72f6590):**
- acquisition-packs/fods/gate7-malformed-fuzz-report.md (NEW — GATE7_FUZZ_TEST PASS 18/18 CRASH 0/18)
- acquisition-packs/fods/gate8-security-plan.md (NEW — Gate 8 security planning)
- acquisition-packs/fodt/gate4-human-review-packet.md (NEW — DEC-034 PASS 20/20)
- acquisition-packs/fodt/gate5-neutral-model-plan.md (NEW — Gate 5 neutral model planning)
- prototypes/by-format/fodt/fodt_parser.py (NEW — FODT Gate 4 parser prototype)
- prototypes/by-format/fodt/validate_against_samples.py (NEW — FODT_PROTOTYPE_VALIDATION PASS 4/4)
- prototypes/by-format/fodt/README.md (NEW), prototypes/by-format/fodt/prototype-notes.md (NEW)
- tests/fixtures/fods/malformed/ (NEW — 18 malformed FODS fixtures across 4 categories)
- tools/fuzz/run_gate7_fuzz_test.py (NEW — Gate 7 fuzz test harness)
- taskcards/TC-0033 (UPDATED — COMPLETED GATE7_FUZZ_TEST PASS 18/18)
- taskcards/TC-0034 (UPDATED — COMPLETED FODT_PROTOTYPE_VALIDATION PASS 4/4)
- taskcards/TC-0035 (UPDATED — COMPLETED DEC-034 PASS 20/20)
- taskcards/TC-0036 (NEW — FODS Gate 8 security review; not_started)
- taskcards/TC-0037 (NEW — FODT Gate 5 neutral model; not_started)
- registry/format-registry.yaml (FODS gate_7 → passed; gate_8 → planning_ready; FODT gate_4 → passed; gate_5 → planning_ready)
- acquisition-packs/fods/pack.yaml (gate_7/gate_8 added; notes updated)
- acquisition-packs/fodt/pack.yaml (gate_4 → passed; gate_5 → planning_ready; notes updated)
- tools/evidence/contracts/run045-combined-sprint.yaml (NEW — run045 evidence contract)
- plans/master-plan.md v2.41; memory/09, settings.json updated
- (run045 exact final HEAD in bundle-metadata/git-log.txt)

**Committed (run048):**
- tools/evidence/validate_evidence_bundle.py (HARDENED — REQUIRED_METADATA_DEPTH check; REQUIRED_METADATA_DEPTH_MINIMUM_NAMED=10)
- tools/evidence/contracts/base-run.yaml v1.4 (UPDATED — run048 note; REQUIRED_METADATA_DEPTH)
- tools/evidence/contracts/run047-combined-sprint.yaml (PATCHED — test_contract:true; legacy bypass)
- tools/evidence/contracts/run048-combined-sprint.yaml (NEW — run048 evidence contract)
- tests/evidence/test_negative_bundle_validation.py (UPDATED — 2 new tests; 13/13 PASS)
- acquisition-packs/fods/gate10-oss-scope.md (NEW — Tiers 0-2, 12 features)
- acquisition-packs/fods/gate10-packaging-plan.md (NEW — format-factory-fods v0.1.0)
- acquisition-packs/fods/gate10-product-source-readiness-report.md (NEW — TC-6/TC-1 addressed)
- acquisition-packs/fods/gate10-human-review-packet.md (NEW — Gate 10 APPROVED)
- tests/fixtures/fodt/malformed/ (NEW — 18 malformed FODT fixtures, 4 categories)
- tools/fuzz/run_fodt_gate7_fuzz_test.py (NEW — FODT Gate 7 fuzz runner)
- acquisition-packs/fodt/gate7-fuzz-report.md (NEW — FODT_GATE7_FUZZ_TEST PASS 18/18)
- reports/security/fodt.md (NEW — Gate 8 GATE8_SECURITY_REVIEW PASS; TC-7 partial)
- taskcards/TC-0046-fodt-gate8-security-review.md (NEW — COMPLETED)
- taskcards/TC-0047-fods-gate11-commercial-planning.md (NEW — not_started; blocked DEC-033)
- taskcards/TC-0048-fodt-gate9-product-mapping.md (NEW — not_started)
- taskcards/TC-0044 (UPDATED — COMPLETED; 4th deliverable added)
- taskcards/TC-0045 (UPDATED — COMPLETED)
- registry/format-registry.yaml (FODS gate_10 → passed; FODT gate_7/8 → passed; gate_9 → planning_ready)
- acquisition-packs/fods/pack.yaml (gate_10 → passed; Babar Raza 2026-05-08)
- acquisition-packs/fodt/pack.yaml (gate_7/8 → passed; gate_9 → planning_ready)
- README.md, ROADMAP.md, .claude/settings.json, memory/09 updated
- plans/master-plan.md v2.44
- (run048 exact final HEAD in bundle-metadata/git-log.txt)

**Commit policy:** Commits are made only when the human explicitly requests a commit (or the execution prompt authorizes it). An agent must never commit on its own initiative.

---

## Section 34 — Standing Instruction to Future Agents

Every agent reading this document must follow these rules without exception:

1. **Read this master plan and AGENTS.md first.** Do not begin any task without understanding the current phase, allowed actions, and forbidden actions.
2. **Obey phase boundaries.** Phase N work is forbidden during Phase N-1. No exceptions.
3. **Inspect evidence.** The bundle contents are the truth. Agent summaries are hypotheses. If you are resuming from a summary, verify it against the actual files.
4. **Log every gap.** If you encounter an unknown, an ambiguity, a missing artifact, or a deviation from plan — log it in Section 27 before proceeding. Silent gaps are governance violations.
5. **Do not self-approve gates.** State: "Gate X criteria met. Awaiting human approval." Never mark a gate passed.
6. **Do not commit.** Unless the human explicitly says "commit now," do not run `git commit` or `git push`.
7. **Produce bundles in execution mode.** Every execution run must produce an evidence bundle and print its absolute path as the final line.
8. **Update this master plan** at every gate transition, phase change, and significant decision. The master plan is only valuable if it is current.
9. **Reuse before regenerating.** Check `.local/artifact-index.yaml` before creating any artifact.
10. **Self-challenge before completing.** Answer all required self-challenge questions. If you cannot answer satisfactorily, log the gap and do not mark the work complete.
11. **Read relevant `/memory` files before complex tasks.** See `AGENTS.md` Section U for the required file list by task type. Treat memory as context, not authority.

---

## Section 35 — Memory Layer

### Purpose

The `/memory` folder provides persistent context across agent sessions. It contains historical rationale, phase evolution, decision background, bundle-review lessons, and standing operating rules from the ChatGPT conversation that shaped the project before Phase 1.

### Authority Hierarchy

| Priority | Source |
|----------|--------|
| 1 | `plans/master-plan.md` (this document) |
| 2 | `AGENTS.md` and `GOVERNANCE.md` |
| 3 | Current repo files and taskcards |
| 4 | Evidence bundles |
| 5 | `/memory` context files |

### Required Memory Files

Minimum read before any general task:
- `memory/README.md`
- `memory/00-index.md`
- `memory/02-standing-operating-rules.md`
- `memory/09-current-state-before-phase1.md`

Task-type-specific additions: see `AGENTS.md` Section U4.

### Memory Contradiction Rule

If `/memory` conflicts with this master plan or any governance file: log a gap in Section 27, do not silently defer to memory, treat this document as authority until the human resolves the contradiction.

### Memory Maintenance Triggers

Update `/memory` (or create a taskcard to update it) after:
- phase acceptance
- gate transition
- major decision
- major gap discovery
- significant healing run
- architecture amendment
- spec-cache policy change
- release control change
- governance change

### Memory Content Restrictions

Do not store in `/memory`: secrets, API keys, credentials, raw LLM prompts, raw LLM responses, or copyrighted specification excerpts.

### Future: /sync-memory Command

TC-0008 defines a planned `/sync-memory` command for Phase 1 or later. It will compare `/memory` against this master plan, detect contradictions, and produce a `memory-sync-report.md`. It is not yet implemented.

---

---

## Section 36 — Secondary Sprint Roadmap: Full2Foss-Inspired System Strengthening

### Relationship to MAIN SPRINT

This section records a SECONDARY sprint roadmap that is strictly subordinate to the MAIN
SPRINT (FODS Gate 7, FODT Gate 4, and subsequent gates). The MAIN SPRINT remains the only
active delivery path. All secondary sprints are optional, cannot interfere with MAIN SPRINT
progress, and cannot change any active gate status or registry entry.

### Origin

The original secondary plan was produced in plan mode (iridescent-coalescing-stearns.md)
during run044 planning. ExitPlanMode was rejected before execution. The plan-mode document
contained 15 defects (D-01 through D-15) catalogued in plans/secondary/full2foss-inspired-
plan-repair-review.md. The plan-repair sprint (S-F2F-00) corrected all defects and produced:
- plans/secondary/full2foss-inspired-plan-repair-review.md (defect catalogue)
- plans/secondary/full2foss-inspired-system-strengthening-plan-v2.md (corrected plan)
- taskcards/S-F2F-00 through S-F2F-08 (9 proposed taskcards)

### Authorization Status

- S-F2F-00 (plan repair): CLOSED_VERIFIED — S-F2F-00B closure sprint 2026-05-08; commit 881e333; evidence independently verified PASS
- S-F2F-01 (playbook schema + policy): CLOSED_VERIFIED — executed 2026-05-08; independently verified S-F2F-01B 2026-05-08; schemas/playbook/ + docs/playbook-layer.md created; no replay tools, no apply mode, no acquisition-pack playbooks
- S-F2F-02 (playbook validation tool): CLOSED_VERIFIED — executed 2026-05-08; schema gap repaired in S-F2F-02B (not_for_execution added to schema); 42/42 tests PASS; both jsonschema and structural engines; docs example passes full JSON Schema; no MAIN SPRINT deviation
- S-F2F-03 (dry-run replay + review queue): CLOSED_VERIFIED — executed 2026-05-09; 3 tools (replay/diff/export); 96 tests PASS; no apply mode; no repo mutations from dry-run; no MAIN SPRINT deviation
- S-F2F-04 through S-F2F-08: proposed_pending_human_approval — NOT authorized

No gate statuses were changed by S-F2F-00 through S-F2F-03. S-F2F-03 created read-only
dry-run tools only (no apply mode, no file mutations). All S-F2F taskcards from S-F2F-04
onward require separate explicit human authorization before execution.

### Secondary Phase Map

| Phase | Taskcard | Scope | Prerequisites |
|-------|----------|-------|---------------|
| S0 | S-F2F-00 | Plan repair (COMPLETE) | None |
| S1 | S-F2F-01 | Playbook schema + policy doc only | CLOSED_VERIFIED (2026-05-08) |
| S2 | S-F2F-02 | Playbook validation tool (read-only) | CLOSED_VERIFIED (S-F2F-02B, 2026-05-08) — 42 PASS, 1 skip |
| S3 | S-F2F-03 | Dry-run replay + review queue export | CLOSED_VERIFIED (2026-05-09) — 96 PASS, 1 skip |
| S4 | S-F2F-04 | Golden dry-run tests | S-F2F-03 complete |
| S5 | S-F2F-05 | ODF-flat family playbook docs | S-F2F-01 complete (parallel to S2-S4) |
| S6 | S-F2F-06 | Apply-mode risk review (doc only) | S-F2F-04 complete |
| P1 | S-F2F-07 | Product dependency closure design | FODS Gate 8 PASSED + human approval |
| P2 | S-F2F-08 | Product skeleton/stub design (doc only) | S-F2F-07 complete + Gate 10 progress |

### Product Dependency Closure and Skeleton Work

Product dependency closure (P1) and product skeleton/stub design (P2) are deferred until:
- Product-track gates (Gate 10+) explicitly authorize source work
- FODS Gate 8 PASSED (hard prerequisite for P1)
- Separate explicit human authorization for each P-phase sprint

No product source files (src/python/, src/net/), no product schemas, and no product tools
will be created until the appropriate gate sequence is satisfied.

### Next Possible Secondary Action

S-F2F-03 is CLOSED_VERIFIED (executed 2026-05-09; 3 dry-run tools; 96 tests PASS;
no apply mode; replay writes nothing to repo). The next possible secondary actions are:
- S-F2F-04 (Golden Dry-Run Tests) or S-F2F-05 (ODF-Flat Family Playbook)
  — each requires a separate explicit human authorization prompt naming the taskcard.

This section is informational only. Execution of any S-F2F sprint beyond S-F2F-03 requires
human authorization conditions above to be met.

### Evidence Bundle for Plan-Repair Sprint

.local/evidence-bundles/secondary-full2foss-plan-repair-YYYYMMDD-HHMMSS.zip

---

---

## Section 37 — Format Understanding Layer, LLM Strategy, and Architecture Backlog

**Added:** memory sprint 2026-05-08
**Status:** Backlog only. No items in this section are authorized for immediate execution.

### 37.1 Format Understanding Layer (Backlog)

Format knowledge is currently scattered across 12–20+ acquisition pack files per format.
Before Phase 4 product source begins, a compiled Format Understanding Layer should exist for each format.
See `docs/format-understanding-layer.md` for the full plan.

**Per-format target files:**
- `acquisition-packs/{format}/format-profile.yaml` — format classification, spec reference
- `acquisition-packs/{format}/verified-facts.yaml` — spec-cited deterministic facts
- `acquisition-packs/{format}/implementation-requirements.yaml` — product-facing requirements
- `acquisition-packs/{format}/parser-strategy.yaml` — parser design decisions
- `acquisition-packs/{format}/security-surface.yaml` — compiled security findings
- `acquisition-packs/{format}/product-readiness.yaml` — compiled readiness from Gate 9/10

**Backlog taskcards:** FUL-001, FUL-002, FUL-003, FUL-004, FUL-005

### 37.2 Controlled LLM and Embedding Strategy (Backlog)

Controlled use of `llm.professionalize.com` model families is authorized for future governed work.
- Model families: GPT OSS, Qwen Next, embedding models
- LLMs may propose facts, summaries, requirements, code drafts — NOT authority
- Embeddings/vector DB are controlled retrieval — NOT truth authority
- Embeddings should use verified-facts-first content strategy
- No secrets committed; no raw transcripts in bundles

See `docs/llm-and-embedding-strategy.md` for full policy.

**Backlog taskcards:** LLM-001, LLM-002, EMB-001, EMB-002, EMB-003

### 37.3 XML-first Focus; Non-XML Adaptability Backlog

Current pipeline validated for XML-type formats (text_xml). Non-XML adaptability is explicit backlog.
Architecture must avoid hardcoding XML-only assumptions.

Physical representation categories defined: text_xml, zip_container, binary_records, compound_document, delimited_text, json_like, hybrid_container.

See `docs/format-representation-model.md` for adaptation ranges and pipeline reuse analysis.

**Backlog taskcards:** REP-001, REP-002, REP-003, REP-004, REP-005

### 37.4 Non-Aspose Format Candidate Registry (Backlog)

A visible registry of formats underserved by Aspose is planned at `registry/non-aspose-format-candidates.yaml`.
Candidates must be verified before claiming Aspose non-overlap.

See `docs/non-aspose-format-candidate-registry-plan.md`.

**Backlog taskcards:** NAC-001, NAC-002, NAC-003, NAC-004

### 37.5 Discovered Gap Backlog Capture Rule

All agents and human contributors must capture discovered gaps in durable repo artifacts (roadmap, backlog, taskcard, memory, gap register) — not only in chat or evidence bundles. See AGENTS.md Section AB and GOVERNANCE.md Section 21.

**Governance taskcard:** GOV-001

### 37.6 Infrastructure Milestones Added

| Milestone | Phase | Taskcard |
|---|---|---|
| Format Understanding Layer design | Before Phase 4+ source | FUL-001 |
| FODS compiled understanding package | After FUL-001; FODS Gate 9 PASSED | FUL-002 |
| FODT compiled understanding package | After FUL-001; FODT Gate 9 PASSED | FUL-003 |
| Product source consumes FUL | After FUL-002 or FUL-003; Phase 4 prompt | FUL-004 |
| LLM model discovery preflight | After LLM-001 authorized | LLM-001 |
| Embedding/retrieval architecture design | After LLM-001 + FUL-001 | EMB-001 |
| Format representation profile schema | After FUL-001 | REP-001 |
| Non-XML adaptability architecture | After REP-001; non-XML format identified | REP-003 |
| Non-Aspose candidate registry | Human authorization | NAC-001 |
| Discovered-gap governance rule | Next governance update sprint | GOV-001 |

---

*End of plans/master-plan.md — version 2.47 — 2026-05-09*
*This document is the single operational authority for format-factory. All other documents are subordinate to it for operational decisions.*

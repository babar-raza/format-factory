# Roadmap

**Document type:** Governance — Phase 0 Foundation
**Last reviewed:** 2026-05-07 (run041)
**Note:** This roadmap describes planned phases and milestones. It is a planning document, not a commitment. Actual progress is tracked in `plans/master-plan.md`.

---

## Phase Model

The project proceeds through five phases. Each phase has a clear entry condition and exit condition. Work in a later phase requires all earlier phases to be complete for the relevant format.

| Phase | Name | Entry Condition | Exit Condition |
|---|---|---|---|
| 0 | Foundation | Repository created | All 41 foundation files exist, human-reviewed |
| 1 | Gate 1 — FODS Scoring | Phase 0 complete | FODS passes Gate 1 (human approval recorded in registry) |
| 2 | Gates 2-3 — FODS Evidence and Samples | Gate 1 passed | FODS passes Gate 3 |
| 3 | Gates 4-9 — FODS Prototype through Security | Gate 3 passed | FODS passes Gate 9 |
| 4+ | Gates 10-11 — FODS Product and Release | Gate 9 passed | FODS product shipped in at least one track |

---

## Phase 0: Foundation (Complete)

**Goal:** Establish governance, policy, folder structure, and templates before any format-specific work begins.

**Deliverables:**
- All governance documents (`AGENTS.md`, `GOVERNANCE.md`, `ROADMAP.md`, `README.md`)
- All policy documents in `docs/` (architecture, product tracks, acquisition workflow, gates, security, legal, release control, LLM endpoint strategy)
- Registry skeleton (`registry/format-registry.yaml` — no format entries)
- Scoring model (`registry/scoring/_scoring-model.md`)
- Acquisition pack template (`acquisition-packs/_template/`)
- Sample policy and empty provenance skeleton (`samples/`)
- Taskcards for next phase work (TC-0001 through TC-0006)
- Configuration files (`.gitignore`, `.env.example`, `.claude/settings.json`, `tools/llm/endpoints.yaml`)
- Directory orientation `_readme.md` files for all top-level directories
- Living master plan (`plans/master-plan.md`)

**Not in Phase 0:**
- FODS registry entry
- Any acquisition pack (beyond template)
- Any sample files
- Any prototype code
- Any product source code
- LLM endpoint client code
- Project command files (beyond `_readme.md`)
- CI workflows

**Status:** Complete — accepted 2026-05-04 (run015). All 45 foundation files exist and human-reviewed.

---

## Phase 1: Gate 1 — FODS Scoring (Complete)

**Goal:** Score FODS against the scoring model, pass Gate 1, and implement the infrastructure needed for LLM-assisted evidence work.

**Deliverables:**
- FODS registry entry in `registry/format-registry.yaml` with Gate 1 passage recorded
- LLM endpoint client code in `tools/llm/` (TC-0005)
- `tools/llm/model-selection.yaml`
- Local artifact index bootstrap (`.local/artifact-index.yaml`)
- Project commands in `.claude/commands/` (TC-0004): `/score-format`, `/create-acquisition-pack`, `/check-gate`, `/create-taskcard`

**Entry condition:** Phase 0 complete and human-reviewed.

**Exit condition:** Gate 1 passed for FODS (human approval recorded in registry).

**Status:** Complete — Gate 1 passed 2026-05-04, approved by Babar Raza. FODS score: 93/100, Accept band. run015/run016/run017.

---

## Phase 2: Gates 2-3 — FODS Evidence and Samples

**Goal:** Complete legal review, spec analysis, and sample acquisition for FODS.

**Deliverables:**
- `acquisition-packs/fods/spec-evidence.md` (Gate 2) ✓
- `acquisition-packs/fods/legal-notes.md` with fast-path approval (Gate 2) ✓
- `samples/by-format/fods/` with minimum 4 samples (Gate 3) — pending
- Provenance entries for all FODS samples (Gate 3) — pending

**Entry condition:** Gate 1 passed for FODS.

**Exit condition:** Gate 3 passed for FODS (human approval recorded in registry).

**Gate 2 status:** PASSED — approved by Babar Raza (2026-05-05). Spec acquired and verified. Legal fast-path confirmed (OASIS Category 1, royalty-free). Patent search waived by project lead.

**Gate 3 status:** PASSED — approved by Babar Raza (2026-05-05, run028). 4 Apache-2.0 synthetic samples validated 4/4 PASS (run026). DEC-034 independently verified (run027). Spec Navigation Layer complete: 884 sections, 940 chunks.

---

## Phase 3: Gates 4-9 — FODS Prototype through Security Review

**Goal:** Build a working FODS parser, validate it against the oracle, fuzz it, and complete security review.

**Deliverables:**
- `prototypes/by-format/fods/` with Python prototype parser (Gate 4)
- `schemas/neutral-model/cells/` with neutral-model schema (Gate 5)
- Oracle comparison report for FODS (Gate 6)
- Fuzz seeds in `tests/fuzz/fods/` (Gate 7)
- Security report in `reports/security/fods.md` with sign-off (Gate 8)
- FODS tier map and delivery plan in acquisition pack (Gate 9)

**Entry condition:** Gate 3 passed for FODS.

**Gate 4 status:** PASSED — approved by Babar Raza (2026-05-06, run033). Prototype at `prototypes/by-format/fods/fods_parser.py` — Python stdlib only. Validation: PT-001 through PT-004 PASS (4/4). TC-0018 DEC-034 PASS (run030+run032).

**Gate 5 status:** PASSED — approved by Babar Raza (2026-05-06, run035). Neutral model v1: 6 entities, 19 field mappings, 30 coverage features, 21 validation rules. Validation 4/4 PASS (87 checks, 0 errors). TC-0024 CLOSED. TC-0023 COMPLETED.

**Gate 6 status:** oracle_blocked_missing_tool (run035; re-confirmed run036 + run037 + run038 + run039 + run040 + run041 — 7 consecutive FAIL). LibreOffice not installed on dev machine. Oracle harness hardened run036: oracle_common.py, FORMAT_FACTORY_SOFFICE, --soffice-path, canonical paths, installation checklist. Provider abstraction added run037: provider_registry.yaml, validate_oracle_environment.py, oracle-provider-strategy.md, oracle-provider-options.md. Harness self-test confirmed PASS run039 (HARNESS_SELF_TEST_ONLY 4/4). Operator handoff added run038: oracle-operator-handoff.md. TC-0026 blocker wording corrected run038. Consistency enforcement tool added (run039) and strengthened (run040 — 10 checks). Clean-git loophole closed run040 (emergency_blocker_bundle). Stable run-state authority model introduced run041 (replaces self-referential commit-hash model). Next: install LibreOffice per oracle-operator-handoff.md, then execute TC-0026 with explicit prompt. Gate 6 NOT approved. FODT Gate 1 APPROVED (Babar Raza, 2026-05-07, run041) — 88/100, Accept band; official registry entry and acquisition-packs/fodt/ skeleton created.

**Exit condition:** Gate 9 passed for FODS (human approval recorded in registry).

---

## Phase 4+: Gates 10-11 — FODS Product and Release

**Goal:** Ship FODS support in at least one open-source product track.

**Deliverables:**
- Production Python FOSS source in `src/python/fods/` and/or .NET product source in `src/net/fods/` (Gate 10, format-first layout)
- Passing test suite (Gate 10)
- Release manifest with human sign-off (Gate 10)
- Open-source release of Python FOSS tier (Gate 10)
- .NET FOSS packaging strategy resolved (DEC-033, required before Gate 10 .NET release)
- Commercial-tier source within `src/net/fods/` (Gate 11, deferred until DD3 resolved)

**Entry condition:** Gate 9 passed for FODS.

**Exit condition:** FODS ships in at least one open-source product track.

---

## Beyond FODS: Subsequent Formats

After FODS, subsequent formats are scored and acquired in priority order as determined by the scoring model. Next-format candidate shortlist created run038, independently verified run039. **FODT Gate 1 APPROVED** (Babar Raza, 2026-05-07, run041): 88/100, Accept band, Category 1 RF — official registry entry created; acquisition-packs/fodt/ skeleton created (6 files); TC-0030 created (not_started). ODF reuse strategy documented at `docs/odf-flat-family-reuse-strategy.md`. FODP, FODG, FODB remain in candidate pool. Shortlist at `registry/candidates/odf-flat-family-shortlist.yaml`; scoring package at `registry/candidates/fodt-gate1-scoring-package.yaml`. Next for FODT: Gate 2 spec/legal evidence (TC-0030). Formats in other families (Words, Slides, Imaging) are considered after the Cells family has at least two formats in product.

The format registry (`registry/format-registry.yaml`) is the authoritative record of which formats are in-flight, deferred, or rejected.

---

## WIP Limits

To prevent work in progress from spreading across too many formats simultaneously:

- Maximum 1 format in Gates 7-9 (security-intensive) at a time.
- Maximum 2 formats in Gates 4-6 (prototype-intensive) at a time.
- Maximum 3 formats in Gates 1-3 (evidence-intensive) at a time.
- No limit on formats scored but not yet accepted (scoring is lightweight).

WIP limit violations require project lead approval to proceed.

---

## Infrastructure Milestones

Alongside format acquisition, several infrastructure milestones are tracked:

| Milestone | Phase | Taskcard |
|---|---|---|
| LLM endpoint client implemented | Phase 1 | TC-0005 |
| Project commands implemented | Phase 1 | TC-0004 |
| Artifact index bootstrap | Phase 1 | TC-0005 |
| Release manifest generator | Phase 3+ | TC-0006 |
| CI boundary check | Phase 4+ | (future taskcard) |
| SQLite artifact index | Phase 3+ if needed | Decision DEC-020 |

---

## Relationship to Other Documents

- `plans/master-plan.md` — current operational state (actual progress, not plan)
- `docs/gates.md` — gate pass criteria
- `docs/acquisition-workflow.md` — stage-by-stage workflow
- `registry/format-registry.yaml` — which formats are active and at which gate
- `taskcards/` — work units for current and upcoming phases

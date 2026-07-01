# Roadmap

**Document type:** Governance / Planning
**Last reviewed:** 2026-05-16 (R18 ZST Gate 4 prototype COMPLETE; FODP/FODG/Gnumeric/ABW Gate 1 APPROVED; 8 formats in registry)
**Note:** This roadmap describes planned phases and milestones. It is a planning document, not the operational authority. Actual progress is tracked in `plans/master-plan.md` and `registry/format-registry.yaml`.

---

## Project Goal

format-factory is intended to become a repeatable system for studying file formats and turning that knowledge into safe, legal, tested software tools.

The long-term plan is:

1. Select promising file formats through scoring and legal classification.
2. Gather official evidence, samples, and provenance.
3. Build prototypes, neutral models, tests, security reviews, and product mappings.
4. Compile reusable format understanding for product work.
5. Build open-source Python libraries first.
6. Prepare .NET and commercial tracks only after the required decisions and gates.
7. Repeat the process for more formats without restarting from scratch.

---

## Phase Model

The project proceeds through five phases. Each phase has a clear entry condition and exit condition. Work in a later phase requires all earlier required gates to be complete for the relevant format.

| Phase | Name | Entry Condition | Exit Condition |
|---|---|---|---|
| 0 | Foundation | Repository created | Foundation files exist and are human-reviewed |
| 1 | Gate 1 Scoring | Phase 0 complete | Format passes Gate 1 |
| 2 | Gates 2-3 Evidence and Samples | Gate 1 passed | Format passes Gate 3 |
| 3 | Gates 4-9 Prototype through Product Mapping | Gate 3 passed | Format passes Gate 9 |
| 4+ | Gates 10-11 Product and Release | Gate 9 passed and explicit source authorization | Product ships in at least one approved track |

---

## Phase 0: Foundation

**Goal:** Establish governance, policy, folder structure, templates, and the master plan before format-specific work begins.

**Status:** Complete. Accepted 2026-05-04 in run015.

Key deliverables:

- Governance documents: `AGENTS.md`, `GOVERNANCE.md`, `ROADMAP.md`, `README.md`
- Policy documents in `docs/`
- Registry skeleton and scoring model
- Acquisition pack template
- Sample policy and provenance skeleton
- Taskcards for initial work
- Directory orientation files
- Living master plan

---

## Phase 1: Gate 1 Scoring

**Goal:** Score candidate formats against the scoring model and select formats that are legally and technically suitable.

**FODS status:** Complete. Gate 1 passed 2026-05-04, approved by Babar Raza. FODS score: 93/100.

**FODT status:** Complete. Gate 1 passed 2026-05-07, approved by Babar Raza. FODT score: 88/100.

---

## Phase 2: Gates 2-3 Evidence and Samples

**Goal:** Complete legal review, specification evidence, and sample corpus creation.

**FODS status:** Complete.

- Gate 2 passed 2026-05-05.
- Gate 3 passed 2026-05-05.
- 4 Apache-2.0 synthetic FODS samples validated 4/4 PASS.
- Spec Navigation Layer completed.

**FODT status:** Complete.

- Gate 2 passed 2026-05-08.
- Gate 3 passed 2026-05-08.
- 4 Apache-2.0 synthetic FODT samples validated 4/4 PASS.

---

## Phase 3: Gates 4-9 Prototype Through Product Mapping

**Goal:** Build prototypes, define neutral models, compare against reference outputs, fuzz, review security, and map product features.

**FODS status:** Complete.

- Gate 4 prototype passed.
- Gate 5 neutral model passed.
- Gate 6 oracle comparison passed.
- Gate 7 fuzz testing passed.
- Gate 8 security review passed.
- Gate 9 product mapping passed.

**FODT status:** Complete through Gate 9 (same as FODS).

- Gate 4 prototype passed.
- Gate 5 neutral model passed.
- Gate 6 oracle comparison passed.
- Gate 7 fuzz testing passed.
- Gate 8 security review passed.
- Gate 9 product mapping passed.

---

## Phase 4+: Product and Release

**Goal:** Turn approved format knowledge into product source and release-ready packages.

**FODS status:**

- Gate 10 passed in run048 (approved by Babar Raza 2026-05-08).
- Python source created under `src/python/fods/` in run051 (TC-0050 completed).
- Gate 11 is `commercial_readiness_in_progress` (C4-C6 vertical slice demonstrated; NOT approved).
- .NET C4-C6 vertical slice created in `src/net/fods/`; DEC-033 resolved Option B.
- commercial_product_ready: false. Requires C7+ capability and explicit human approval.

**FODT status:**

- Gate 10 passed (approved by Babar Raza 2026-05-11; TC-0052 completed).
- Python source created under `src/python/fodt/`; 115/115 tests passing.
- Gate 11 is `commercial_readiness_in_progress` (C4-C6 vertical slice demonstrated; NOT approved).
- .NET C4-C6 vertical slice created in `src/net/fodt/`; DEC-033 resolved Option B.
- commercial_product_ready: false. Requires C7+ capability and explicit human approval.

---

## ZST — Zstandard

ZST is the third format in the acquisition pipeline. Gate 1 scored 8.95/10 (ACQUISITION_READY).

**ZST status:**

- Gate 1 PASSED (delegated, R13B, 2026-05-15). Score: 8.95/10. IETF RFC 8878.
- Gate 2 PASSED (delegated, R14, 2026-05-15). RFC 8878 + RFC 9659 cached. 20 tests PASS.
- **Gate 3 PASSED (delegated, R16, 2026-05-15).** 11-file corpus (8 valid + 3 invalid). 57 corpus tests PASS. DEC-034 IV PASS.
- **Gate 4: planning_complete (R17, 2026-05-16).** parser-notes.md created. Frame format, parsing strategy, validation plan documented. DEC-034 IV PASS (10/10). Gate 4 full pass (prototype + human review) deferred to R18+.
- Gate 4 prototype: R18 taskcard created (ZST-R18-GATE5-REQUIREMENTS-READINESS.md). Pending execution prompt.

---

## Beyond FODS And FODT

FODS and FODT are the first two XML-style pilots. They prove the acquisition pipeline across two product families: Cells and Words.

Next likely ODF flat XML candidates remain in the candidate pool:

- FODP, flat OpenDocument Presentation
- FODG, flat OpenDocument Graphics
- FODB, flat OpenDocument Database (deferred — Aspose support unclear)

Non-ODF candidates from R11 planning bundle (R17 Gate 1 packets ready):
- Gnumeric (.gnumeric) — R11 score 8.75, ACQUISITION_READY; Gate 1 scoring packet created (R17)
- ABW (.abw) — R11 score 8.75, ACQUISITION_READY; Gate 1 scoring packet created (R17)

Other candidates:
- ORA (.ora) — OpenRaster; estimated 6.5-7.0; Aspose audit required; Gate 1 packet created (R17)
- dnumber/.numbers — Apple Numbers; AUTOMATIC_REJECT (Category 5 — no public spec)

Batch sprint taskcards created in R17:
- FODP-FODG-GATE1-BATCH.md — ODF batch; pending Conway R9 + execution prompt
- ORA-GNUMERIC-ABW-GATE1-SCORING-IV.md — scoring IV; pending Aspose audits + execution prompt

The next format should be selected through the same scoring, evidence, gate, and human-approval process. No format inherits gate approval from FODS or FODT.

---

## WIP Limits

To prevent work in progress from spreading across too many formats simultaneously:

- Maximum 1 format in Gates 7-9 at a time.
- Maximum 2 formats in Gates 4-6 at a time.
- Maximum 3 formats in Gates 1-3 at a time.
- No limit on formats scored but not yet accepted.

WIP limit violations require project lead approval.

---

## Infrastructure Milestones

| Milestone | Status |
|---|---|
| Evidence bundle builder and validator | Active |
| Oracle harness | Active |
| Fuzz testing harnesses | Active for FODS/FODT |
| Current-state consistency checker | Active |
| Format Understanding Layer schemas | Complete |
| FODS compiled understanding package | Complete |
| FODT compiled understanding package | Complete |
| Playbook validation tool | Active, read-only |
| Dry-run replay tools | Active, no apply mode |
| LLM operational rollout | Plan hardened (2026-05-18); implementation Phase 1 pending authorization |
| Embedding/retrieval architecture | Plan hardened (2026-05-18); implementation Phase 3 pending authorization |
| AI platform control plane | Plan hardened (2026-05-18); Phase 1 pending authorization |
| Agent Metrics telemetry integration | Plan hardened (2026-05-18); Phase 1 spool, Phase 5 full |
| Non-XML adaptability architecture | Backlog |
| Non-Aspose candidate registry | Backlog |
| .NET C4-C6 vertical slice | Created for FODS + FODT; Gate 11 NOT approved; commercial_product_ready: false |

---

## Architecture Backlog

### Format Understanding Layer

Format knowledge accumulated through gates 1-9 is compiled into per-format understanding artifacts:

- `format-profile.yaml`
- `verified-facts.yaml`
- `implementation-requirements.yaml`
- `parser-strategy.yaml`
- `security-surface.yaml`
- `product-readiness.yaml`

FUL-001, FUL-002, and FUL-003 are complete for the current FODS/FODT track. FUL-004 and FUL-005 remain follow-up work.

### AI/LLM/Embedding Platform Layer

A generic, segregated, production-grade AI platform layer is planned. All AI usage (agentic, synthesis, embeddings) flows through one governed substrate with contracts, role-based model routing, validators, telemetry (Agent Metrics), and evidence integration. Plan hardened 2026-05-18; implementation not yet authorized. See `docs/ai/ai-platform-operating-model.md` and `plans/master-plan.md` Section 39.

LLMs assist but do not approve gates, define legal status, or replace citations. Embeddings are retrieval tools, not truth. Spec normalization is mandatory input for AI consumption. AI test generation is mandatory with full artifact lifecycle.

### XML-First Focus And Non-XML Adaptability

The pipeline is validated for XML-type formats. Non-XML formats such as ZIP containers, binary records, and compound documents are backlog only. The architecture should avoid XML-only assumptions, but implementation requires explicit authorization.

### Three-Pilot Proof Direction

The near-term proof goal is three XML-style format pilots with different feature profiles. FODS and FODT are the first two pilots. A third pilot should be selected only after evidence review and explicit authorization.

---

## Relationship To Other Documents

- `plans/master-plan.md`: current operational state and decisions
- `registry/format-registry.yaml`: authoritative gate status per format
- `docs/gates.md`: gate pass criteria
- `docs/python-foss/acquisition-workflow.md`: stage-by-stage workflow
- `taskcards/`: work units for current and upcoming phases

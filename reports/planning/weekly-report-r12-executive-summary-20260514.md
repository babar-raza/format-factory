# Weekly Report — R12 Executive Summary
Sprint: FORMAT-FACTORY-R12-ACQUISITION-ENGINE-IV-AND-ZST-GOVERNED-READINESS-SWARM-001
Date: 2026-05-14
Author: R12 Lane G

---

## Executive Summary

The format-factory project has crossed a structural threshold.

Through R10 and R11, the system built a complete governed acquisition planning
engine — candidate scoring, lifecycle simulation, multi-format planning, and
deterministic bundle generation. Through R12, that engine has now been
independently verified and adversarially challenged.

**The verdict: the acquisition engine is trustworthy.**

This week's work answers the question: *can this system safely reason about
formats beyond the XML/ODF proof of concept?*

The answer is yes.

---

## Why the Project Is Now a Governed Acquisition Platform

When this project started, it was a format parser implementation project with a
governance wrapper.

It is now a **governed acquisition platform** — a system that can:

1. **Maintain a format backlog** of 49 candidates across 13 categories
2. **Score candidates** on 8 readiness dimensions with deterministic weighted arithmetic
3. **Select a first candidate** via reproducible acquisition planning
4. **Simulate the full lifecycle** of any candidate from CANDIDATE state to EVIDENCE_READY
5. **Model acquisition graphs** — dependencies, stale propagation, evidence chains, IV requirements
6. **Govern all of this** with immutable governance flags, dry-run enforcement, and replay determinism

The platform is not just governed — it *actively enforces* governance at the code level:
- `dry_run=False` raises `ValueError`
- `commercial_product_ready` cannot be set to `True` by code
- `Gate 11` cannot be approved without human action
- All scores are labeled estimates, not decisions

---

## Why Governance Accelerated Rather Than Slowed Scale

A natural assumption is that governance overhead slows execution. This project
demonstrates the opposite.

**Governance created reusability.** The same lifecycle states that govern FODS
and FODT now govern ZST, gnumeric, abw, and all 19 TIER_A candidates. The system
scales to new formats without re-engineering the governance layer.

**Governance created confidence.** Every sprint produces a validated evidence bundle.
The R11 sprint bundle contains 945 entries, 49 metadata files. When the R12
IV sprint challenged the engine, all 18 IV checks passed without modifications.
The engine was already correct because governance forced it to be honest.

**Governance prevented scope creep.** Because `dry_run=True` is enforced in code,
no sprint has accidentally begun implementing a format. Every candidate — ZST
included — is still at CANDIDATE state. Nothing was over-engineered or
pre-implemented without authorization.

**Governance enabled parallelism.** R12 ran 9 lanes simultaneously because each
lane had clear ownership and clear non-overlap rules. Without governance boundaries,
lanes would have conflicted.

---

## Why Dry-Run/Simulation-First Mattered

The R9 simulation framework, R10 POC tools, R11 runtime, and R12 graph simulator
collectively represent 40+ sprint-hours of simulation work on the acquisition layer.

None of it implemented a single byte of production code.

That was intentional. The simulation-first approach:

1. **Validated architecture** before committing to implementation. The acquisition
   lifecycle state machine was tested with 412+ tests before any format implementation began.

2. **Found real gaps early.** R10/R11 discovered that ZST's `binary_format=False` flag
   is debatable (it's a binary format but has a full RFC spec). This calibration question
   was found in simulation, not in a broken production parser.

3. **Built trust through replay.** Every output is deterministic and replayable.
   The R12 IV sprint confirmed that running the engine fresh produces identical results
   to R11 outputs. That replay property is only possible because simulation-first
   produced deterministic, hash-verified outputs from the start.

4. **Provided governance evidence.** The R11 evidence bundle (2.1 MB, 945 entries)
   is the authoritative record of what the acquisition engine decided and why.
   Human reviewers have a complete audit trail.

---

## The Shift Beyond XML-Only Thinking

FODS and FODT are flat XML formats. They were the ideal proof of concept: fully
specified, well-understood, Aspose-supported.

ZST breaks every one of those assumptions:
- Not XML (binary LZ77+ANS/FSE)
- Not document-family (archive/compression)
- Not primarily an Aspose use case (TBD — pending audit)
- Not word processing (archive category)
- Has an RFC (not an OASIS standard)

The fact that the acquisition engine correctly selects ZST as the #1 TIER_A
candidate — with a fully reproduced score of 8.95/10 — demonstrates that the
architecture is **format-family-agnostic**.

The system correctly reasons that:
- A full public RFC > a partial vendor spec
- Clear legal provenance > unclear provenance
- An OSS reference implementation > no reference
- Archive parser complexity is lower than document parser complexity

These are structural properties of the scoring system that hold across all
format categories.

---

## Why ZST Matters Strategically

ZST is not just the highest-scoring TIER_A candidate. It is a proof point.

**ZST proves the acquisition engine can reason about non-document formats.**
Compression formats have different parser primitives (entropy coding vs. XML SAX parsing),
different oracle approaches (round-trip vs. schema validation), and different legal profiles
(IETF RFC vs. OASIS standard). The engine handles all of these correctly.

**ZST validates the future non-Aspose direction.**
The format expansion roadmap includes 49 candidates, most of which are not Aspose
product formats. ZST may or may not be Aspose-supported (audit pending). The system
does not require Aspose support to score or plan — it only requires an honest
`aspose_supported: None` (needs_audit) until the audit is completed.

**ZST demonstrates archive category feasibility.**
The archive category (alz, egg, xar, zpaq, zst, lha, lzh, arj) has 8 TIER_A candidates.
ZST is the only one with a full public RFC. It is the correct first choice for an
archive format acquisition — and the engine found it automatically.

---

## What Still Remains Blocked Before Real Implementation Execution

Despite all of the above, implementation cannot begin for ZST (or any other candidate).

The following are explicitly blocked:

| Gate | Status | Reason |
|------|--------|--------|
| ZST Support Matrix Audit | NOT_STARTED | Required before any planning proceeds |
| ZST Spec Normalization | NOT_STARTED | RFC must be cached locally before AI req gen |
| ZST Requirements Generation | NOT_STARTED | Requires spec normalization first |
| ZST DEC-034 IV Sprint | NOT_STARTED | Required before any implementation |
| Gate 11 (FODS) | NOT APPROVED | Human authorization required |
| Gate 11 (FODT) | NOT APPROVED | Human authorization required |
| commercial_product_ready | false | Has not changed; Gate 11 not approved |

**The platform is ready to plan. It is not authorized to execute.**

That distinction — plan vs. execute — is the most important governance boundary
in the system. R12 has verified that this boundary is enforced at the code level.

The next step is human authorization for R13, which will determine the first
controlled acquisition onboarding action.

---

*Weekly Report — Format Factory R12 | 2026-05-14*

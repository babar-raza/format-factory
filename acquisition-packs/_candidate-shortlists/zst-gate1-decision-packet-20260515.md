# ZST Gate 1 Decision Packet
Prepared by: FORMAT-FACTORY-R13A-R12-CLOSURE-AND-ZST-GATE1-PACKET-SWARM-001
Lane: G (ZST Gate 1 Decision Packet)
Date: 2026-05-15
Attention: Babar Raza (human approver)

---

## NOTICE

**THIS IS A DECISION PACKET — NOT AN APPROVAL.**

Gate 1 has NOT been approved. ZST acquisition has NOT started.
No spec retrieval has been performed. No implementation has begun.
This packet exists to give Babar Raza the information needed to decide whether to proceed.

---

## A. Format Identity

| Field | Value |
|-------|-------|
| Format ID | zst |
| Format Name | Zstandard Compressed File |
| Extension | .zst |
| MIME Type | application/zstd |
| Category | archive |
| Product Family | Archive |
| Format Introduced | 2015 (Facebook/Meta) |
| RFC | RFC 8878 (2021-02-01; obsoletes RFC 8478) |

---

## B. Current Lifecycle State

| Field | Value |
|-------|-------|
| Lifecycle state | CANDIDATE |
| Gate 1 | NOT STARTED |
| Gate 1 approval | REQUIRED from Babar Raza |
| Spec retrieval | NOT AUTHORIZED |
| Acquisition status | NOT STARTED |
| commercial_product_ready | false |

---

## C. Score and Score Decomposition

**Score: 8.95 / 10 — Band: ACQUISITION_READY (threshold: >=7.01)**

Source: R11 acquisition_planning_runtime.py + R12 Lane A/B independent verification.

| Dimension | Weight | Score | Contribution | Notes |
|-----------|--------|-------|--------------|-------|
| spec_availability | 0.20 | 10 | 2.00 | IETF RFC 8878, fully public |
| spec_completeness | 0.15 | 9 | 1.35 | Complete bitstream spec |
| complexity | 0.10 | 7 | 0.70 | Archive category; moderate |
| sample_availability | 0.10 | 8 | 0.80 | Samples constructible from any file |
| legal_clarity | 0.15 | 9 | 1.35 | IETF public domain; BSD+patent grant |
| parser_feasibility | 0.15 | 10 | 1.50 | OSS reference impl available |
| oracle_feasibility | 0.05 | 7 | 0.35 | Round-trip oracle feasible |
| requirements_gen_readiness | 0.10 | 9 | 0.90 | Full public spec + legal clarity |
| **TOTAL** | **1.00** | | **8.95** | |

---

## D. Why ZST Was Selected First

ZST ranked #1 in the R11 acquisition planning bundle with score 8.95, ahead of:
- gnumeric: 8.75
- abw: 8.75
- zpaq: 8.70
- qoi: 8.60

Reasons for ZST's #1 rank:
1. **Highest spec quality in the Tier A archive class:** IETF RFC 8878 is an authoritative
   standards-body publication, not a community wiki or vendor doc.
2. **Clear legal path:** BSD+patent grant (Zstandard reference impl) + IETF royalty-free
   publication policy. No known IP encumbrance.
3. **Archive category is strategically valuable:** Container/compression formats are required
   for handling other formats (e.g. .tar.zst, packages).
4. **Widely adopted:** Linux kernel, npm, rpm, Arch Linux, Facebook infrastructure — broad
   ecosystem = good sample availability + strong implementation track record.
5. **Round-trip oracle feasible:** compress → decompress → compare SHA256 is a deterministic
   and automatable oracle with no dependency on external reference images.

---

## E. Risk Classification

| Risk Dimension | Assessment | Notes |
|---|---|---|
| Legal risk | LOW | IETF RFC; Zstandard BSD+patent grant. Formal confirmation pending Gate 2 legal review. |
| Spec risk | LOW | Single authoritative RFC; no fragmentation |
| Technical complexity | MEDIUM | LZ77+ANS (FSE) + Huffman; more complex than FODS/FODT but well-documented |
| Aspose support | UNKNOWN | Support matrix audit NOT yet performed |
| Sample availability | LOW | Constructible from any content; open samples available |
| Oracle feasibility | LOW | Round-trip oracle is standard for compression formats |
| Reverse engineering required | NO | Full public RFC; no RE needed |

**Overall acquisition risk classification: LOW-MEDIUM (legal LOW, technical MEDIUM)**
**Note:** `unsupported_by_aspose` remains `needs_audit` until real audit is performed.

---

## F. Legal / Spec-Readiness Summary (from local reports only)

Source: R12 Lane B (zst-governed-candidate-audit-20260514.md) and R12 zst-score-decomposition.

**RFC 8878** was verified to exist as a published IETF Proposed Standard (2021-02-01).
It covers: magic number (0xFD2FB528), frame format, block types (raw/RLE/compressed),
LZ77+ANS (FSE), Huffman coding for literals, checksum, dictionary support.

**Spec quality classification:** RFC_STANDARD (highest tier in format-onboarding schema)

**Legal provenance classification:** PUBLIC_SPEC (per format-onboarding schema)

**WARNING:** These assessments are based on R12 analysis without formal RFC retrieval.
Gate 2 requires formal spec retrieval, legal notes, and human confirmation.

---

## G. Support-Matrix Audit Requirements

The following steps are required in a real support-matrix audit (R13B):

1. Check Aspose.ZIP documentation for ZST support (authorized internet access required)
2. Confirm RFC 8878 royalty-free terms (IETF policy check)
3. Confirm Zstandard BSD+patent grant is compatible with project use
4. Identify available Python binding licenses (python-zstandard / zstandard on PyPI)
5. Identify open-license .zst sample files

Until these steps are completed: `aspose_supported = None`; `unsupported_by_aspose = needs_audit`

---

## H. Explicit Statements

- **No real acquisition has started.** ZST is a candidate only.
- **RFC 8878 has NOT been retrieved, cached, or embedded in this sprint.**
- **No ZST requirements have been generated.**
- **No ZST implementation code has been written.**
- **No ZST Gate 1 has been approved.**
- **Gate 11 for FODS and FODT has NOT been approved.** These are separate tracks.
- **commercial_product_ready remains false.**

---

## I. Approval Choices for Babar Raza

Please choose one of the following:

### Option 1: APPROVE_ZST_GATE1_SIMULATION_TO_REAL_AUDIT
Proceed with R13B: real support-matrix audit (authorized internet access), RFC 8878
retrieval preparation, and formal Gate 1 approval recording.
**Effect:** R13B sprint authorized; ZST Gate 1 moves from NOT_STARTED to IN_PROGRESS.

### Option 2: DEFER_ZST
Keep ZST as CANDIDATE. Do not proceed with Gate 1 at this time.
**Effect:** ZST remains in backlog. No sprint authorized.

### Option 3: SELECT_SECOND_CHOICE_GNUMERIC
Proceed with Gnumeric (.gnumeric, score 8.75) instead of ZST.
**Effect:** R13B targets Gnumeric support-matrix audit instead.

### Option 4: SELECT_SECOND_CHOICE_ABW
Proceed with AbiWord (.abw, score 8.75) instead of ZST.
**Effect:** R13B targets ABW support-matrix audit instead.

### Option 5: REQUEST_MORE_INVESTIGATION
Return more information before deciding. Specify what additional investigation is needed.
**Effect:** Sprint produces additional targeted investigation as specified.

---

## J. Next Sprint Prompt (use ONLY if Babar approves Option 1)

The following prompt is the exact ready-to-send R13B prompt to use ONLY after Babar Raza
explicitly approves ZST Gate 1 (Option 1 above). Do NOT use this prompt unless approval
is confirmed in the current session.

---
```
EXECUTION MODE
Sprint: FORMAT-FACTORY-R13B-ZST-REAL-SUPPORT-MATRIX-AUDIT-AND-GATE1-APPROVAL-RECORDING-SWARM-001
Date: 2026-05-15 (or later)

Authorization: Babar Raza approved ZST Gate 1 simulation-to-real-audit in the R13A decision packet.

Objectives:
1. Perform real support-matrix audit for ZST:
   - Check Aspose.ZIP documentation for ZST support (AUTHORIZED internet access)
   - Record aspose_supported status with evidence
   - Confirm RFC 8878 royalty-free terms
   - Confirm Zstandard BSD+patent grant compatibility
   - Confirm python-zstandard license
2. Record Gate 1 approval in registry/format-registry.yaml for ZST
   (human has approved; record the approval with today's date and Babar Raza as approver)
3. Create acquisition-packs/zst/pack.yaml from template
4. Create acquisition-packs/zst/spec-evidence.md with RFC 8878 evidence
5. Create acquisition-packs/zst/legal-notes.md with legal classification
6. Update plans/master-plan.md with ZST Gate 1 approved status
7. Run full test suite and produce evidence bundle

Non-goals:
- Do NOT begin Gate 2 spec retrieval/caching
- Do NOT generate ZST requirements
- Do NOT implement ZST
- Do NOT modify src/net/ or src/python/
- Do NOT approve Gate 2 or any subsequent gate

Evidence bundle required. BUNDLE_VALIDATION: PASS required before reporting complete.
```
---

---

## K. Packet Metadata

| Field | Value |
|-------|-------|
| Prepared by | FORMAT-FACTORY-R13A-R12-CLOSURE-AND-ZST-GATE1-PACKET-SWARM-001 Lane G |
| Packet version | 1.0 |
| Based on | R11 planning bundle + R12 Lane A/B audit |
| Local reports cited | zst-governed-candidate-audit-20260514.md; r12-zst-score-decomposition.md |
| Internet sources cited | NONE — simulation only |
| Gate 1 approved | NO |
| Approval required from | Babar Raza |

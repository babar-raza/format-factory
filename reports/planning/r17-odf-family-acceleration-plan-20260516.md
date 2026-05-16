# R17 Gate 7: OpenDocument Family Acceleration Plan
Sprint: FORMAT-FACTORY-R17-R16-CLOSURE-VERIFY-ZST-GATE4-PLANNING-AND-MULTI-FORMAT-GATE1-SWARM-001
Date: 2026-05-16
Gate: 7 — OpenDocument Acceleration Plan

## 1. FODS Current State

- Gates 1-10: PASSED
- Gate 11: commercial_readiness_in_progress — NOT APPROVED
- Python: src/python/fods/ exists (Tier 0-3 implemented)
- .NET: src/net/fods/ exists (C4-C6 vertical slice, FodsDocument with Load/Save/Edit)
- Gate 11 sub-gates: G11-A through G11-G, all NOT_STARTED or PROPOSED
- commercial_product_ready: false
- Gate 11 blocker: C7+ capability + all sub-gate evidence + human approval by Babar Raza

## 2. FODT Current State

- Gates 1-10: PASSED
- Gate 11: commercial_readiness_in_progress — NOT APPROVED
- Python: src/python/fodt/ exists
- .NET: src/net/fodt/ exists (C4-C6 vertical slice, FodtDocument with Load/Save/Edit)
- Gate 11 sub-gates: all NOT_STARTED or PROPOSED
- commercial_product_ready: false
- Gate 11 blocker: same as FODS

## 3. FODP Recommended Path

### Identity
FODP (.fodp) is the flat XML variant of ODP (OpenDocument Presentation).
Same OASIS ODF 1.3 spec, same legal category (1), same RF licensing.

### Recommended Path
1. Batch Gate 1 with FODG (same spec, same legal, same Aspose family)
2. Reuse existing OASIS ODF 1.3 spec cache from FODS/FODT sprint (no new download needed)
3. Reuse legal-notes.md framework from FODS/FODT (same OASIS RF basis)
4. Fast-path Gate 2 eligible (same legal basis already approved)
5. Gate 3 corpus: OASIS provides ODP sample files; flat XML conversion straightforward
6. Gate 4 prototype: reuse FODS XML parsing skeleton; new schema domain (presentations)

### Prerequisite
- Conway R9 proof stable (FODS/FODT Gate 11 work foundation must be solid)
- Aspose.Slides support audit for .fodp
- DEC-034 IV of Gate 1 scoring

### Estimated Sprint: R19+ (parallel to ZST Gate 5 or after)

## 4. FODG Recommended Path

### Identity
FODG (.fodg) is the flat XML variant of ODG (OpenDocument Drawing).
Same spec, same legal basis as FODP.

### Recommended Path
- Batch with FODP (same sprint)
- Reuse all FODP infrastructure
- Aspose.Diagram or Aspose.Imaging support audit needed

### Notes
- Narrower commercial use case (diagrams vs presentations)
- Can be deprioritized within the batch if sprint capacity is limited

## 5. FODB Status

- FODB (.fodb) = flat XML variant of ODB (OpenDocument Database)
- Status: DEFER
- Reason: Database schema is less standardized; Aspose support unclear
- Action: Do not include in FODP/FODG batch until Aspose audit confirms support

## 6. Running FODP/FODG Without Blocking ZST

Lane separation:
- ZST Lane: Gate 4 prototype → Gate 5 requirements → Gate 6 oracle (R18+)
- ODF Lane: FODP/FODG Gate 1 → Gate 2 fast-path → Gate 3 corpus (R19+)
- These lanes are independent — no blocking relationship

WIP limit per master-plan Section 38: max 2 formats in Gates 4-6 simultaneously.
With ZST in Gate 4, one additional slot is available.
FODP/FODG can run in Gate 1-3 simultaneously with ZST Gate 4-6 (Gate 1-3 ≠ Gates 4-6).

## 7. Keeping FODS/FODT Gate 11 Separate

Gate 11 (commercial_readiness) is a separate lane from format acquisition:
- FODS/FODT Gate 11 lane: Conway R9 → C7+ capability → sub-gate evidence → human approval
- New format acquisition lane: ZST + FODP/FODG + Gnumeric/ABW
- These must NOT be mixed in the same sprint unless explicitly authorized
- This sprint (R17) does NOT touch FODS/FODT Gate 11

## 8. Proposed Next Sprint Split

### Lane A: ZST Gate 5 Readiness (R18)
Sprint: FORMAT-FACTORY-R18-ZST-GATE5-REQUIREMENTS-READINESS-SWARM
Scope:
- Create prototypes/by-format/zst/ (Gate 4 prototype)
- parser-requirements.yaml in spec-cache or G-NORM-004 waiver
- ZST Gate 4 prototype + Gate 4 human approval
- ZST Gate 5 neutral model scoping (codec format: N/A or minimal model)
- generated-requirements/zst/ authorization (if Gate 5 proceeds)

Prerequisites: R17 parser-notes.md complete (DONE in this sprint)
Authorization: Requires R18 execution prompt from Babar Raza

### Lane B: FODP/FODG Gate 1 Batch Approval (R19)
Sprint: FORMAT-FACTORY-R19-FODP-FODG-GATE1-BATCH-SWARM
Scope:
- Run Gate 1 scoring for FODP and FODG
- Aspose.Slides / Aspose.Diagram support audit
- DEC-034 IV of scoring
- Gate 1 approval (if human delegates)

Prerequisites: Conway R9 stable; Aspose audits complete
Authorization: Requires R19 execution prompt

### Lane C: ORA + Gnumeric/ABW Gate 1 Scoring IV (R19 parallel or R20)
Sprint: FORMAT-FACTORY-R19-ORA-GNUMERIC-ABW-GATE1-SCORING-IV-SWARM
Scope:
- Run Gate 1 scoring for Gnumeric and ABW
- Aspose audit for each
- DEC-034 IV of scoring
- ORA spec completeness review
- Gate 1 approval if human delegates

Prerequisites: Aspose audits; spec research
Authorization: Requires execution prompt

## 9. Gate 11 Separation Guarantee

No R17+ work touches:
- FODS Gate 11 sub-gates (G11-A through G11-G) — LOCKED
- FODT Gate 11 sub-gates — LOCKED
- commercial_product_ready flag for FODS or FODT — LOCKED
- src/net/fods or src/net/fodt above C4-C6 slice — LOCKED
- src/python/fods or src/python/fodt above existing Tier — LOCKED

Gate 11 remains: NOT APPROVED for both FODS and FODT.

GATE_7_ODF_ACCELERATION_PLAN: COMPLETE

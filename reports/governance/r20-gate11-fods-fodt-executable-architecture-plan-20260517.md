# R20 Gate 11: FODS/FODT Executable Architecture Plan

**Date:** 2026-05-17
**Sprint:** FORMAT-FACTORY-R20-PRODUCTIZATION-TRAIN-ZST-FODP-FODG-GNUMERIC-ABW-SOURCE-AND-GATE11-ARCHITECTURE-SWARM-001
**Status:** PLANNING ONLY — no Gate 11 approval, no source execution
**commercial_product_ready:** false

---

## Current State Summary

| Format | Gates 1-10 | Gate 11 Status | .NET Source | commercial_product_ready |
|--------|------------|----------------|-------------|--------------------------|
| FODS   | ALL PASSED | in_progress (NOT APPROVED) | C4-C6 vertical slice | false |
| FODT   | ALL PASSED | in_progress (NOT APPROVED) | C4-C6 vertical slice | false |

**G11-D DEMONSTRATED:** COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001 (FODS 42/42, FODT 43/43 tests pass). Edit-and-save vertical slice complete.
**G11-E through G11-G:** NOT STARTED. Require explicit human authorization before execution.

---

## Gate 11 Sub-Gate Architecture

### G11-A: Architecture Review
**Status:** PROPOSED
**Owner:** Human (Babar Raza)
**What:** Review and approve the overall Gate 11 commercial architecture before any further implementation.
**Inputs:** `docs/commercial-dotnet-architecture.md`, `docs/commercial-product-capability-model.md`, C4-C6 vertical slice results.
**Output:** Architecture approval memo or taskcard marked COMPLETED.
**Blocker:** Human approval required — cannot be delegated to AI.

### G11-B: Commercial Licensing Confirmation
**Status:** PROPOSED
**What:** Confirm commercial license terms for FODS/FODT product distribution.
**Inputs:** ODF 1.3 OASIS RF Category 1 license (already cleared at Gate 1). .NET runtime licensing (MIT).
**Output:** `acquisition-packs/fods/gate11-commercial-licensing.md` + FODT equivalent.
**Note:** This is low-risk for ODF formats (OASIS RF). Can proceed once G11-A is approved.

### G11-C: NuGet Package Definition
**Status:** PROPOSED
**What:** Define NuGet package IDs, version scheme, and dependency policy.
**Proposed package IDs:**
- `FormatFactory.Fods` (or `Aspose.FormatFactory.Fods`)
- `FormatFactory.Fodt`
**Version:** `0.1.0-alpha.1` for first commercial preview.
**Output:** `acquisition-packs/fods/gate11-nuget-package-plan.md` + FODT equivalent.
**Blocker:** G11-A approval, commercial product naming decision by Babar Raza.

### G11-D: Edit-and-Save Vertical Slice (DEMONSTRATED)
**Status:** DEMONSTRATED (COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001)
**Evidence:** FODS 42/42 PASS, FODT 43/43 PASS (C4-C6 capability).
**Source location:** `src/net/fods/`, `src/net/fodt/`
**Capability level:** C4 (structured extraction) + C5 (properties editing) + C6 (save/round-trip).
**Next capability target:** C7+ (format conversion/export).

### G11-E: Conversion and Export Capability (C7+)
**Status:** NOT STARTED
**What:** Implement PDF, HTML, or PNG export from FODS/FODT (C7 = format conversion).
**Technical approach:**
- FODS → PDF: Leverage LibreOffice headless or a .NET PDF library
- FODT → DOCX: Transform ODF to OOXML (or use a document model bridge)
**Effort estimate:** Large — not suitable for a single sprint without explicit scoping.
**Blocker:** Explicit human authorization required (execution prompt). G11-A must be approved first.
**Does NOT authorize:** This plan document does NOT authorize G11-E execution.

### G11-F: Package Readiness and CI/CD
**Status:** NOT STARTED
**What:** NuGet pack, CI/CD pipeline, release signing.
**Inputs:** Completed C7+ implementation, NuGet package definition (G11-C).
**Output:** `FormatFactory.Fods.nupkg`, `FormatFactory.Fodt.nupkg`.
**Blocker:** G11-E must be at least at C7 capability. CI/CD pipeline design pending.

### G11-G: Human Gate 11 Approval
**Status:** NOT STARTED
**Owner:** Babar Raza (human only — cannot be AI-delegated)
**What:** Final human review and approval of all Gate 11 sub-gates.
**DEC-034 requirement:** Independent verification sprint required before human review.
**Output:** `commercial_product_ready: true` — set only after this approval.

---

## Critical Path

```
G11-A (human approval)
  → G11-B (licensing) + G11-C (package plan)
    → G11-E (C7+ conversion) [requires new execution prompt]
      → G11-F (CI/CD + packaging)
        → DEC-034 IV sprint
          → G11-G (human approval)
            → commercial_product_ready: true
```

---

## Current Blockers

1. **G11-A: No human approval yet.** Architecture review has not been formally scheduled.
2. **G11-E: No execution prompt.** C7+ export requires a dedicated sprint with explicit user authorization.
3. **commercial_product_ready: false** will remain false until G11-G is approved.

---

## What This Plan Does NOT Authorize

- No .NET source changes in this sprint (no src/net/ mutations)
- No Gate 11 sub-gate approvals
- No commercial_product_ready=true claims
- No NuGet packaging
- No CI/CD pipeline creation

---

## Next Steps for Human

To advance Gate 11, Babar Raza must:

1. Review and approve G11-A (architecture) — issue an explicit execution prompt
2. After G11-A: authorize G11-B + G11-C in the same or a follow-up prompt
3. After G11-C: issue a **G11-E execution prompt** to start C7+ conversion capability (new sprint)
4. After G11-E: DEC-034 IV sprint required before G11-G review

**Ready-to-send prompt for G11-A approval:**
> "I approve the Gate 11 architecture for FODS and FODT as described in r20-gate11-fods-fodt-executable-architecture-plan-20260517.md. Please execute G11-B (commercial licensing confirmation) and G11-C (NuGet package plan) for both formats. Do NOT execute G11-E or write any new .NET source."

---

*This report is PLANNING ONLY. No sub-gates are approved by this document. commercial_product_ready: false.*

# R13A-R14 Forward Roadmap
Sprint: FORMAT-FACTORY-R13A-R12-CLOSURE-AND-ZST-GATE1-PACKET-SWARM-001
Lane: H (Forward Roadmap)
Date: 2026-05-15

## Overview

Two parallel tracks continue from this sprint:
1. **ZST acquisition track** — contingent on Babar Raza approving ZST Gate 1
2. **FODS/FODT commercial Gate 11 track** — independent of ZST; blocked by G11-E authorization

These tracks are independent. Progress in one does NOT authorize or unblock the other.

---

## ZST Acquisition Track (CONDITIONAL — requires Babar Raza approval)

### R13B: ZST Real Support-Matrix Audit and Gate 1 Approval Recording
**Trigger:** Babar Raza selects Option 1 in the ZST Gate 1 decision packet
**Authorization state:** AWAITING_HUMAN_APPROVAL (not authorized as of 2026-05-15)

Deliverables:
- Real Aspose.ZIP documentation review (authorized internet access)
- RFC 8878 royalty-free terms confirmation
- Zstandard BSD+patent grant compatibility analysis
- python-zstandard license verification
- acquisition-packs/zst/pack.yaml created
- acquisition-packs/zst/spec-evidence.md and legal-notes.md created
- registry/format-registry.yaml: ZST Gate 1 recorded as approved (with Babar Raza as approver)
- plans/master-plan.md updated with ZST Gate 1 status

Constraints:
- Do NOT begin Gate 2 spec retrieval/caching in R13B
- Do NOT generate ZST requirements
- Do NOT implement ZST

### R14: ZST Spec Retrieval, Cache, and Legal Proof
**Trigger:** R13B complete; Gate 1 formally recorded in registry
**Deliverables:**
- RFC 8878 retrieved and cached locally under spec-cache/zst/
- SHA-256 hash recorded
- Legal notes complete (Gate 2 legal review)
- Sample sources identified and documented

### R15: ZST Spec Normalization
**Trigger:** R14 complete; Gate 2 approved by human
**Deliverables:**
- RFC 8878 normalized into structured format
- spec_normalization_status → NORMALIZED
- Requirements generation pipeline ready

### R16: ZST AI-Assisted Requirements Generation
**Trigger:** R15 complete; human authorization for AI requirements generation
**Deliverables:**
- AI-generated ZST implementation requirements
- Schema-validated against format-onboarding schema
- Staged for verifier review

### R17: Verifier Review
**Trigger:** R16 complete; requirements generated
**Deliverables:**
- Human verifier (Babar Raza or designated) reviews AI-generated requirements
- Requirements marked as VERIFIER_REVIEWED
- Ready for DEC-034 IV

### R18: DEC-034 Independent Verification
**Trigger:** R17 complete; requirements verifier-reviewed
**Deliverables:**
- Separate agent session IV sprint
- IV confirms requirements against spec evidence
- IV verdict: PASS or FAIL

### R19: Implementation Simulation
**Trigger:** R18 PASS; human authorizes simulation
**Deliverables:**
- Implementation simulation dry run
- No product source written
- Simulation report produced

### R20+: Implementation Authorization and Execution
**Trigger:** R19 complete; human explicitly authorizes implementation
**Deliverables:**
- src/python/zst/ created (Python FOSS track)
- src/net/zst/ created (if .NET commercial track authorized separately)
- Gate 10 evidence prepared

---

## FODS/FODT Commercial Gate 11 Track (INDEPENDENT — not affected by ZST)

Current state: Gate 11 commercial_readiness_in_progress, C4-C6 vertical slice demonstrated.
commercial_product_ready: false. Gate 11 NOT approved.

### G11-E: Conversion/Export
**Trigger:** Explicit human authorization (separate prompt required)
**Deliverables:**
- PDF/HTML/PNG export capability for FODS/FODT
- C7+ capability level achieved
- Evidence bundle produced

### G11-F: Package Readiness
**Trigger:** G11-E complete and human authorized
**Deliverables:**
- NuGet package dry-run
- CLI interface
- Documentation

### G11-G: Human Approval
**Trigger:** G11-F complete; DEC-034 IV complete
**Deliverables:**
- Gate 11 human approval by Babar Raza
- commercial_product_ready → true (only after this step)
- Release authorized

---

## Separation Guarantee

The following operations are BLOCKED until explicitly authorized:
- ZST Gate 1 recording: blocked until Babar approves R13B prompt
- G11-E work: blocked until explicit conversion/export prompt
- commercial_product_ready: false until Gate 11 human approval
- Any ZST implementation: blocked until R20+ authorization

---

## Candidate Queue (if ZST is deferred or after ZST completes)

| Rank | Format | Score | Notes |
|------|--------|-------|-------|
| 1 | ZST (.zst) | 8.95 | Selected first |
| 2 | Gnumeric (.gnumeric) | 8.75 | Second choice if ZST deferred |
| 3 | ABW (.abw) | 8.75 | Third choice |
| 4 | ZPAQ (.zpaq) | 8.70 | Fourth choice |
| 5 | QOI (.qoi) | 8.60 | Fifth choice |

Source: R11 acquisition planning bundle (r11-candidate-ranking-20260514.md)

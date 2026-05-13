# Gate 11 Commercial Rebaseline
# Sprint: COMMERCIAL-PRODUCT-DIRECTION-RESET-SWARM-001
# Lane D — Gate and Roadmap Rebaseline
# Date: 2026-05-13

## 1. Purpose

Fix the project planning so agents stop treating current Tier 0 parser source as
commercial readiness. Document what Gate 11 actually requires.

---

## 2. Current Gate 11 Language Analysis

### Current recorded state (as of commit c7ee7ab)
- FODS Gate 11: `commercial_readiness_in_progress`
- FODT Gate 11: `commercial_readiness_in_progress`
- DEC-033: RESOLVED as Option B (.NET Commercial Only)
- Gate 11 APPROVED: NO — explicitly deferred

### What "commercial_readiness_in_progress" currently means
The prior sprint implemented Tier 0 .NET parsers and labeled them as a starting point
for Gate 11. The label `commercial_readiness_in_progress` is accurate — but it risks
being interpreted by future agents as "progress toward approval."

The **key ambiguity** that this rebaseline resolves:

> Gate 11 previously could have been interpreted as requiring only:
> - `.NET implementation exists` (any tier)
> - Package dry-run passes
> - DEC-033 decision recorded
>
> This rebaseline makes explicit that Gate 11 requires:
> - Full load-edit-save-convert capability (C7 minimum)
> - Sub-gate approval sequence (G11-A through G11-G)
> - NOT just Tier 0 parser existence

---

## 3. Gate 11 Sub-Gates

The following sub-gates are proposed to replace the single Gate 11 approval:

### G11-A: Commercial Architecture Approved
**Criteria:**
- docs/commercial-product-capability-model.md accepted by human
- docs/commercial-dotnet-architecture.md accepted by human
- Sub-gate design accepted
**Status:** PROPOSED — requires human approval of this plan

### G11-B: Full Object Model Implemented (C4-C5)
**Criteria:**
- FodsDocument/FodtDocument with full typed entity graph
- Load(path) returns navigable DOM
- All 4 sample fixtures load successfully
- Oracle comparison against Python neutral model passes
**Status:** NOT_STARTED

### G11-C: No-Edit Roundtrip (C3+C7 partial)
**Criteria:**
- Load → Save → Reload → identical semantic content
- All 4 sample fixtures pass roundtrip
- LibreOffice oracle: loaded saved file matches original
**Status:** NOT_STARTED

### G11-D: Edit-and-Save Vertical Slice (C6-C7)
**Criteria:**
- FODS: edit cell value, save, reload, verify
- FODT: edit paragraph text, save, reload, verify
- Edited file validates structurally
**Status:** NOT_STARTED

### G11-E: Conversion/Export Vertical Slice (C9)
**Criteria:**
- HTML export produces structurally valid HTML
- PDF export produces readable PDF
- Family conversion: FODS→ODS or FODT→ODT
**Status:** NOT_STARTED

### G11-F: Package/Release Readiness
**Criteria:**
- NuGet package builds cleanly
- Package includes README, license, API documentation
- Package passes dry-run install and usage test
- Commercial license finalized (DEC-030/031 decisions)
**Status:** NOT_STARTED (blocked by G11-B through G11-E)

### G11-G: Commercial Human Approval
**Criteria:**
- Human reviews G11-A through G11-F evidence
- Human explicitly approves Gate 11
- Commit records approval with human identity
**Status:** NOT_STARTED

---

## 4. State Corrections Required

### In registry/format-registry.yaml
Add fields:
- `commercial_capability_level: C2` (for both FODS and FODT .NET)
- `gate11_sub_gate_status` map with all G11-A through G11-G as NOT_STARTED
- Note that `commercial_readiness_in_progress` refers to sub-gate planning, not product completion

### In plans/master-plan.md
Add to Rule 12 (or Section 11):
- Gate 11 minimum capability requirement: C7
- Sub-gate summary
- Current .NET source is C2 (Tier 0 extractor)

### In taskcards/
- GATE11-COMMERCIAL-REBASELINE.md (created this sprint)
- Link to each G11-A through G11-G sub-gate taskcard (future)

---

## 5. What This Sprint Does NOT Do

- Does NOT approve any gate
- Does NOT implement product code
- Does NOT change DEC-033 Option B
- Does NOT create .NET FOSS source
- Does NOT change Python source behavior

---

## 6. Lane D Verdict

```
LANE_D_VERDICT: LANE_D_PASS_WITH_PROPOSED_SUBGATES_ONLY
gate11_rebaselined: true
subgates_proposed: G11-A through G11-G
gate11_approved: false
dec033_preserved: true
registry_update_required: true (coordinator integrates)
master_plan_update_required: true (coordinator integrates)
```

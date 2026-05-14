---
document_type: strategic_roadmap
sprint: FORMAT-FACTORY-ROADMAP-MEMORY-SYNC-001
title: "Format Factory — Format Expansion Roadmap"
date: "2026-05-14"
visibility: internal
publish_allowed: false
authority: plans/master-plan.md Section 38
---

# Format Factory — Format Expansion Roadmap

**Sprint:** FORMAT-FACTORY-ROADMAP-MEMORY-SYNC-001
**Date:** 2026-05-14
**Authority:** plans/master-plan.md Section 38

---

## Section 1 — Strategic Position

Format Factory is the **top-priority project**. Speed is required — but never by skipping:
- Evidence review and bundle validation
- Governance and authority-chain checks
- Taskcards and gate discipline (11 gates, human approval required at each)
- Tests, source inspection, and independent verification (DEC-034)
- No-stash/reset/restore/clean safety
- No push/publish safety
- No commercial-readiness overclaim

The preferred execution style is **broader controlled swarm**:
- More agents, more parallel lanes, bigger sprints
- Dependency-aware execution, coordinator integration
- Exact-path staging, lane ownership
- No uncontrolled overlap, no skipped gates

Human/orchestrator review is delegated to the agent except for non-delegable actions:
push, publish, package release, external credential use, Gate 11 approval, commercial_product_ready = true.

---

## Section 2 — Immediate Plan (XML-Based Proof First)

**Status:** IN PROGRESS — FODS/FODT active proof formats.

The XML-based proof system must be completed cleanly before expanding to new formats.

### 2.1 XML Proof Completion Steps

1. Finish Conway orchestration infrastructure (Phases R1–R9):
   - R1: Schema and tooling hardening (6/6 schemas, full test suite)
   - R2: Format context resolver (FODS/FODT → REQUIREMENTS_AUTHORITATIVE)
   - R3: Lane library (R-lanes + I-lanes + C-lanes)
   - R4: Prompt generator + quality gate (10 criteria)
   - R5: Evidence contract template
   - R6: Commands (9 `.claude/commands/` skill files)
   - R7: Full test suite + FODS/FODT dry-runs
   - R8: Independent verification of skill system (separate session)
   - R9: First new format rollout

2. Keep FODS/FODT as current proof formats — do not add new formats until proof is stable.

3. Generated requirements remain authoritative only after verifier review + DEC-034 IV.

4. Do not move to autonomous implementation execution until planning/dry-run orchestration is proven.

### 2.2 Current FODS/FODT Status

| Format | Gates | Gate 11 | .NET Capability | commercial_product_ready |
|--------|-------|---------|-----------------|--------------------------|
| FODS   | 1-10 ALL PASSED | in_progress (NOT APPROVED) | C4-C6-vertical-slice | false |
| FODT   | 1-10 ALL PASSED | in_progress (NOT APPROVED) | C4-C6-vertical-slice | false |

Gate 11 requires C7+ capability (load-edit-save minimum), all sub-gate evidence, and human approval.

---

## Section 3 — Short-Term Plan (After XML Proof Stable)

**Status:** PENDING — blocked on Conway R9 completion.

After the XML-based proof system is stable and the Conway orchestration infrastructure is proven:

1. Expand to additional XML/package-based or public-spec formats.
2. Prefer formats with:
   - Public specifications (publicly available, no NDA required)
   - Public structural knowledge (open documentation, public reverse-engineering records)
   - Open test material (open-license sample files)
   - Reverse-engineering-safe documentation (community-published format docs)
3. Build repeatable skills/playbooks so new formats require minimal custom engineering.
4. Support both:
   - Deterministic/manual-repeatable process through skills (Claude Code skills)
   - Governed autonomous process using llm.professionalize.com models (under AI policy)
5. AI is acceleration layer, not authority.
6. Every format must pass all 11 gates with human approval.

### 3.1 Near-Term Expansion Candidates (Tier A)

These formats have the strongest fit for the current system after XML proof stabilizes.
All marked `unsupported_by_aspose: needs_audit` — audit required before acquisition planning.

| Format | Category | Public Spec | Notes |
|--------|----------|-------------|-------|
| .hwpx | Word processing | Partial public | Hancom Hangul XML/package |
| .hwp | Word processing | Limited | Hancom Hangul binary — requires careful audit |
| .hwt | Word processing | Partial public | Hancom Hangul template |
| .alz | Archive | No public spec | ALZip — reverse-engineering documented |
| .egg | Archive | Partial | ESTsoft EGG — partial documentation |
| .numbers | Spreadsheet | No public spec | Apple Numbers (iWork) |
| .key | Presentation | No public spec | Apple Keynote (iWork) |
| .pages | Word processing | No public spec | Apple Pages (iWork) |
| .gnumeric | Spreadsheet | Full public (XML) | GNOME Gnumeric — open source |
| .abw | Word processing | Full public (XML) | AbiWord — open source |
| .xar | Archive | Partial | XAR archive format |
| .lha / .lzh | Archive | Partial | LHA/LZH — documented |
| .arj | Archive | Partial | ARJ — documented |
| .zpaq | Archive | Full public | ZPAQ — public spec |
| .zst | Compression | Full public | Zstandard — RFC |
| .qoi | Image | Full public | Quite OK Image — minimal spec |
| .ora | Image | Full public (XML ZIP) | OpenRaster — LGPL spec |
| .xcf | Image | Full public | GIMP native — documented |

---

## Section 4 — Long-Term Plan (Beyond XML-Family)

**Status:** BACKLOG — not authorized for immediate execution.

Once XML-based formats are proven, enhance the system for any format family where specifications
or sufficient public technical information are available, regardless of original source or vendor ecosystem.

**The system must not be limited to formats currently supported by Aspose.**

Strategic future backlog includes:
- Formats not currently supported by Aspose
- Minor/underserved formats
- Publicly specified formats
- Proprietary-but-documented formats
- Formats with public reverse-engineering documentation
- Archive/package formats
- Binary document formats
- CAD/3D/GIS/media/project/email/page-layout formats where public technical material exists

---

## Section 5 — Medium-Term Expansion Candidates (Tier B)

Useful after archive/package and XML-package workflows mature.
All marked `unsupported_by_aspose: needs_audit`.

| Format | Category | Notes |
|--------|----------|-------|
| .indd / .idml | Page layout | InDesign (via IDML — XML-based) |
| .qxp / .qxd | Page layout | QuarkXPress |
| .sla | Page layout | Scribus (XML-based, FOSS) |
| .wpd | Word processing | WordPerfect |
| .123 / .wk1 / .wk3 / .wk4 | Spreadsheet | Lotus 1-2-3 family |
| .qpw | Spreadsheet | Quattro Pro |
| .skp | CAD | SketchUp |
| .3dm | CAD | Rhino |
| .fcstd | CAD | FreeCAD (XML ZIP, FOSS) |
| .mbtiles | GIS | MBTiles (SQLite-based) |
| .pmtiles | GIS | PMTiles (cloud-optimized, public spec) |
| .osm | GIS | OpenStreetMap XML (full public spec) |
| .pbf | GIS | Protobuf binary |

---

## Section 6 — Long-Term Advanced Targets (Tier C)

Advanced or commercial-only targets requiring specific expertise.
All marked `unsupported_by_aspose: needs_audit`.

- Vendor CAD binaries: SolidWorks (.sldprt/.sldasm), CATIA (.catpart/.catproduct), Inventor (.ipt/.iam)
- BIM formats: Revit (.rvt/.rfa), IFC (.ifcxml)
- Camera RAW: .cr3, .raf, .orf, .rw2, .pef, .srw, .x3f, .erf, .mrw, .mos, .fff
- Proprietary DTP: InDesign binary, QuarkXPress binary
- Game/3D: .gltf/.glb, .usd/.usda/.usdc/.usdz, .fbx, .dae
- Email PIM: .nsf, .olm
- Game assets and voxel: .vox, .pmx, .pmd

---

## Section 7 — Complete Non-Aspose Candidate Backlog

See `memory/26-format-expansion-roadmap-and-non-aspose-backlog-20260514.md` for the full
category-by-category listing (13 categories, ~200+ candidates).

See `taskcards/NON-ASPOSE-FORMAT-BACKLOG.md` for the governance taskcard.

**CRITICAL:** Every candidate is `unsupported_by_aspose: needs_audit` until verified against
current Aspose support matrices.

---

## Section 8 — Governance Rules for Format Expansion

1. **No new format before Conway R9 complete.** The orchestration infrastructure must be proven first.
2. **Every format must pass all 11 gates** with human approval at each gate.
3. **Support-matrix audit required** before any acquisition planning begins.
4. **Public-spec availability must be recorded** before implementation begins.
5. **Proprietary or reverse-engineered formats must be classified** legally before proceeding.
6. **AI assists, not decides.** AI can assist with discovery, classification, requirements extraction,
   planning, and implementation drafting. Authority comes from specs, evidence, validation, verifier
   review, DEC-034 IV, taskcards, and delegated gate decisions.
7. **Speed is required, but not at the expense of governance, correctness, evidence, or safety.**
8. **Every new format must use the repeatable skill system** (after Conway R9).
9. **Generated requirements must be schema-validated, verifier-reviewed, and DEC-034 IV'd** before
   implementation consumes them.
10. **No gate self-approval.** All 11 gates require human approval (Babar Raza or delegated).

---

## Section 9 — Format Expansion Process for Each New Format

For each new format added to the system:

1. **Support-matrix audit** — verify current Aspose support; classify overlap/gap
2. **Specification/source audit** — identify public spec, documentation, or reverse-engineering sources
3. **Legal/provenance classification** — Apache-2.0/MIT samples? Spec license? Reverse-engineering safe?
4. **Local spec normalization** — download and cache spec locally (per AGENTS.md Section T)
5. **Generated requirements** — AI synthesis from local sources, then schema validation + verifier review + DEC-034 IV
6. **Implementation planning** — taskcards, sprint design, lane assignment
7. **Evidence bundle validation** — BUNDLE_VALIDATION: PASS before each gate
8. **Tests PASS** — all automated tests pass at each tier
9. **Gate approvals** — human approval at each of the 11 gates
10. **Commercial readiness** — Gate 11 requires C7+ capability and human approval

---

## Section 10 — Dependency on Conway Infrastructure

Format expansion (Phase R9+) depends on the complete Conway orchestration system:

```
Conway R0 (COMPLETE)
  └── R1 (schemas) → R2 (context resolver) → R3 (lane library)
        → R4 (prompt generator + quality gate) → R5 (evidence contract template)
              → R6 (commands) → R7 (dry-runs FODS + FODT) → R8 (IV of skill system)
                    └── R9: FIRST NEW FORMAT — expansion begins here
```

Do not authorize new format work until Conway R8 IV is complete.

---

## Related Files

| File | Purpose |
|------|---------|
| plans/master-plan.md Section 38 | Master plan format expansion section |
| memory/26-format-expansion-roadmap-and-non-aspose-backlog-20260514.md | Memory file (this session) |
| docs/format-expansion-roadmap.yaml | Machine-readable version of this doc |
| taskcards/FORMAT-EXPANSION-ROADMAP.md | Format expansion roadmap governance taskcard |
| taskcards/NON-ASPOSE-FORMAT-BACKLOG.md | Non-Aspose candidate backlog taskcard |
| taskcards/PUBLIC-SPEC-FORMAT-EXPANSION.md | Public-spec expansion taskcard |
| taskcards/NAC-001-non-aspose-format-candidate-registry.md | Existing NAC-001 taskcard |
| taskcards/REP-003-non-xml-adaptability-backlog.md | Existing REP-003 taskcard |
| reports/planning/format-expansion-roadmap-memory-sync-20260514.md | Planning report |
| registry/format-registry.yaml | Current format gate status |
